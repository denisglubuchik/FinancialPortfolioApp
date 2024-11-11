import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from back.user_service.message_broker.producer import rabbit_producer

from back.user_service.db.dao import UsersDAO, VerificationTokensDAO
from back.user_service.db.models import Users
from back.user_service.schemas.users import SUserCreate, SUserUpdate
from back.user_service.auth import utils as auth_utils
from back.user_service.auth.helpers import create_access_token, create_refresh_token
from back.user_service.auth.validation import (
    get_current_auth_user_for_refresh,
    validate_auth_user,
    get_current_auth_user,
)
from back.user_service.schemas.users import SUser
from back.user_service.exceptions import UserAlreadyExistsException, UserWasntChangedException

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
        raise UserAlreadyExistsException()
    new_user = new_user.model_dump()
    new_user["hashed_password"] = auth_utils.hash_password(new_user["hashed_password"])
    user: Users = await UsersDAO.insert(**new_user)
    await rabbit_producer.new_user(user.id, user.username, user.email)
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


@router.put("/users",
            response_model=SUser | UpdatedUserAndToken,
            response_model_exclude_none=True,
)
async def user_update(updated_user: SUserUpdate, current_user: SUser = Depends(get_current_auth_user)):
    if current_user.username == updated_user.username and current_user.email == updated_user.email:
        raise UserWasntChangedException()

    updated_user: SUser = await UsersDAO.update(current_user.id, **updated_user.model_dump(exclude_defaults=True))
    await rabbit_producer.update_user(current_user.id, updated_user.username, updated_user.email)

    # if user changes username, we need to update access token
    if current_user.username != updated_user.username:
        access_token = create_access_token(updated_user)
        return UpdatedUserAndToken(updated_user=updated_user,
                                   token=TokenInfo(access_token=access_token))
    return updated_user


@router.delete("/users")
async def user_delete(user: SUser = Depends(get_current_auth_user)):
    await UsersDAO.delete(user.id)
    await rabbit_producer.delete_user(user.id)
    return {"message": "user deleted"}


def generate_verification_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


@router.get("/verification_code")
async def request_verification_code(user: SUser = Depends(get_current_auth_user)):
    code = generate_verification_code()
    try:
        await VerificationTokensDAO.insert(user_id=user.id, verification_token=code,
                                           is_used=False, expires_at=(datetime.utcnow() + timedelta(minutes=10)))
    except Exception as e:
        raise e
    await rabbit_producer.email_verification(user.id, user.email, code)
    return {"message": "verification code sent"}


@router.post("/verification_code")
async def verify_email():
    pass
