from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from starlette import status

from back.user_service.message_broker import rabbitmq

from back.user_service.dao import UsersDAO
from back.user_service.models import Users
from back.user_service.schemas.users import SUserCreate, SUserUpdate
from back.user_service.auth import utils as auth_utils
from back.user_service.auth.helpers import create_access_token, create_refresh_token
from back.user_service.auth.validation import (
    get_current_auth_user_for_refresh,
    validate_auth_user,
    get_current_auth_user,
)
from back.user_service.schemas.users import SUser

http_bearer = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(http_bearer)],
)


@router.get("/users/me/", response_model=SUser)
async def auth_user_check_self_info(
    user: SUser = Depends(get_current_auth_user),
):
    return user


@router.post("/register/", response_model=SUser)
async def user_register(
    new_user: SUserCreate,
):
    user = await UsersDAO.find_one_or_none(username=new_user.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user already exists",
        )
    new_user = new_user.model_dump()
    new_user["hashed_password"] = auth_utils.hash_password(new_user["hashed_password"])
    user: Users = await UsersDAO.insert(**new_user)
    await rabbitmq.new_user(user.id, user.username)
    return user


@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(
    user: SUser = Depends(validate_auth_user),
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh/",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh_jwt(
    user: SUser = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    return TokenInfo(
        access_token=access_token,
    )


class UpdatedUserAndToken(BaseModel):
    updated_user: SUser
    token: TokenInfo


@router.put("/users", response_model=SUser | UpdatedUserAndToken)
async def user_update(updated_user: SUserUpdate, current_user: SUser = Depends(get_current_auth_user)):
    updated_user = await UsersDAO.update(current_user.id, **updated_user.model_dump())
    if current_user.username != updated_user.username:
        await rabbitmq.update_user(current_user.id, updated_user.username)
        access_token = create_access_token(updated_user)
        return UpdatedUserAndToken(updated_user=updated_user,
                                   token=TokenInfo(access_token=access_token))
    return updated_user


@router.delete("/users")
async def user_delete(user: SUser = Depends(get_current_auth_user)):
    await UsersDAO.delete(user.id)
    await rabbitmq.delete_user(user.id)
    return {"message": "user deleted"}
