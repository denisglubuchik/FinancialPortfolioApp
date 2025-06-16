import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Body
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from back.user_service.message_broker.producer import rabbit_producer

from back.user_service.db.dao import UsersDAO, VerificationTokensDAO
from back.user_service.db.models import Users
from back.user_service.schemas.users import SUserCreate, SUserUpdate
from back.user_service.auth import utils as auth_utils
from back.user_service.schemas.users import SUser
from back.user_service.exceptions import UserAlreadyExistsException, UserWasntChangedException, \
    VerificationTokenNotFoundException, InvalidVerificationTokenException, InvalidPasswordException, \
    InvalidUsernameException, UserNotFoundException

http_bearer = HTTPBearer(auto_error=False)


class Credentials(BaseModel):
    username: str
    password: str


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/verify_credentials")
async def verify_credentials(credentials: Credentials) -> SUser:
    if not (user := await UsersDAO.find_one_or_none(username=credentials.username)):
        raise InvalidUsernameException()

    if not auth_utils.validate_password(
        password=credentials.password,
        hashed_password=user.hashed_password,
    ):
        raise InvalidPasswordException()
    return user


@router.get("/user")
async def get_user_by_username(username: str) -> SUser:
    if not (user := await UsersDAO.find_one_or_none(username=username)):
        raise UserNotFoundException()
    return user


@router.get("/user/by_tg/{tg_id}")
async def get_user_by_tg(tg_id: int) -> SUser:
    if not (user := await UsersDAO.find_one_or_none(tg_id=tg_id)):
        raise UserNotFoundException()
    return user


@router.post("/register", response_model=SUser)
async def user_register(
    new_user: SUserCreate,
):
    user = await UsersDAO.find_one_or_none(username=new_user.username)
    if user:
        raise UserAlreadyExistsException()
    new_user = new_user.model_dump()
    new_user["hashed_password"] = auth_utils.hash_password(new_user["hashed_password"])
    user: Users = await UsersDAO.insert(**new_user)
    await rabbit_producer.new_user(user.id, user.username, user.email, None)
    return user


@router.post("/telegram_login", response_model=SUser)
async def telegram_login(
    tg_id: int,
    username: str
):
    user = await UsersDAO.find_one_or_none(tg_id=tg_id)
    if user:
        raise UserAlreadyExistsException()
    user: Users = await UsersDAO.insert(tg_id=tg_id, username=username, email="", hashed_password="")
    await rabbit_producer.new_user(user.id, user.username, user.email, tg_id)
    return user


@router.put("/email",
            response_model=SUser,
            response_model_exclude_none=True,
)
async def user_update(tg_id: int, new_email: str):
    user = await UsersDAO.find_one_or_none(tg_id=tg_id)
    if new_email == user.email:
        raise UserWasntChangedException()

    updated_user: SUser = await UsersDAO.update(user.id, email=new_email)
    await rabbit_producer.update_user(user.id, updated_user.username, updated_user.email)
    return updated_user


@router.put("/",
            response_model=SUser,
            response_model_exclude_none=True,
)
async def user_update(updated_user: SUserUpdate, current_user: SUser):
    if current_user.username == updated_user.username and current_user.email == updated_user.email:
        raise UserWasntChangedException()

    updated_user: SUser = await UsersDAO.update(current_user.id, **updated_user.model_dump(exclude_defaults=True))
    await rabbit_producer.update_user(current_user.id, updated_user.username, updated_user.email)
    return updated_user


@router.put("/password")
async def user_update_password(current_password: str = Body(), new_password: str = Body(), user: SUser = Body()):
    if not auth_utils.validate_password(current_password, user.hashed_password):
        raise InvalidPasswordException()

    new_password = auth_utils.hash_password(new_password)
    await UsersDAO.update_password(user.id, new_password)

    await rabbit_producer.password_changed(user.id)
    return {"message": "password has been changed"}


@router.delete("/")
async def user_delete(user_id: str):
    await UsersDAO.delete(int(user_id))
    await rabbit_producer.delete_user(user_id)
    return {"message": "user deleted"}


def generate_verification_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


# TODO добавить проверку на то что пользователь верифицирован
@router.get("/verification_code")
async def request_verification_code(user_id: int):  
    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        raise UserNotFoundException()
    
    if not user.email:
        raise ValueError("User has no email address")
    
    code = generate_verification_code()
    
    try:
        if current_token := await VerificationTokensDAO.find_one_or_none(user_id=user_id, is_used=False):
            await VerificationTokensDAO.delete(current_token.id)
            
        await VerificationTokensDAO.insert(user_id=user_id, verification_token=code,
                                           is_used=False, expires_at=(datetime.utcnow() + timedelta(minutes=10)))
        
    except Exception as e:
        raise e
    
    await rabbit_producer.email_verification(user_id, code)
    
    return {"message": "verification code sent"}


@router.post("/verification_code")
async def verify_email(user_id: int = Body(), code: str = Body()):
    
    token = await VerificationTokensDAO.find_one_or_none(user_id=user_id, is_used=False)
    if not token:
        raise VerificationTokenNotFoundException()
    
    if token.verification_token != code:
        raise InvalidVerificationTokenException()
        
    await VerificationTokensDAO.update(token.id, is_used=True)
    await UsersDAO.update(user_id, is_verified=True)
    
    return {"message": "email verified"}
