import logging
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

logger = logging.getLogger(__name__)

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
    logger.info(f"Authentication attempt for username: {credentials.username}")
    
    if not (user := await UsersDAO.find_one_or_none(username=credentials.username)):
        logger.warning(f"Authentication failed: username not found: {credentials.username}")
        raise InvalidUsernameException()

    if not auth_utils.validate_password(
        password=credentials.password,
        hashed_password=user.hashed_password,
    ):
        logger.warning(f"Authentication failed: invalid password for username: {credentials.username}")
        raise InvalidPasswordException()
    
    logger.info(f"Authentication successful for user_id: {user.id}, username: {credentials.username}")
    return user


@router.get("/user")
async def get_user_by_username(username: str) -> SUser:
    if not (user := await UsersDAO.find_one_or_none(username=username)):
        logger.warning(f"User not found by username: {username}")
        raise UserNotFoundException()
    
    return user


@router.get("/user/by_tg/{tg_id}")
async def get_user_by_tg(tg_id: int) -> SUser:
    if not (user := await UsersDAO.find_one_or_none(tg_id=tg_id)):
        logger.warning(f"User not found by telegram_id: {tg_id}")
        raise UserNotFoundException()
    
    return user


@router.post("/register", response_model=SUser)
async def user_register(
    new_user: SUserCreate,
):
    logger.info(f"User registration attempt: username={new_user.username}, email={new_user.email}")
    
    user = await UsersDAO.find_one_or_none(username=new_user.username)
    if user:
        logger.warning(f"Registration failed: user already exists with username: {new_user.username}")
        raise UserAlreadyExistsException()
    
    try:
        new_user = new_user.model_dump()
        new_user["hashed_password"] = auth_utils.hash_password(new_user["hashed_password"])
        user: Users = await UsersDAO.insert(**new_user)
        
        await rabbit_producer.new_user(user.id, user.username, user.email, None)
        
        logger.info(f"User registered successfully: user_id={user.id}, username={user.username}")
        return user
    except Exception as e:
        logger.error(f"User registration failed for username {new_user.username}: {e}")
        raise


@router.post("/telegram_login", response_model=SUser)
async def telegram_login(
    tg_id: int,
    username: str
):
    logger.info(f"Telegram login attempt: telegram_id={tg_id}, username={username}")
    
    user = await UsersDAO.find_one_or_none(tg_id=tg_id)
    if user:
        logger.warning(f"Telegram login failed: user already exists with telegram_id: {tg_id}")
        raise UserAlreadyExistsException()
    
    try:
        user: Users = await UsersDAO.insert(tg_id=tg_id, username=username, email="", hashed_password="")
        await rabbit_producer.new_user(user.id, user.username, user.email, tg_id)
        
        logger.info(f"Telegram user created successfully: user_id={user.id}, telegram_id={tg_id}")
        return user
    except Exception as e:
        logger.error(f"Telegram login failed for telegram_id {tg_id}: {e}")
        raise


@router.put("/email",
            response_model=SUser,
            response_model_exclude_none=True,
)
async def user_update(tg_id: int, new_email: str):
    logger.info(f"Email update attempt for telegram_id: {tg_id}, new_email: {new_email}")
    
    user = await UsersDAO.find_one_or_none(tg_id=tg_id)
    if new_email == user.email:
        logger.warning(f"Email update failed: same email provided for user_id: {user.id}")
        raise UserWasntChangedException()

    try:
        updated_user: SUser = await UsersDAO.update(user.id, email=new_email)
        await rabbit_producer.update_user(user.id, updated_user.username, updated_user.email)
        
        logger.info(f"Email updated successfully: user_id={user.id}, new_email={new_email}")
        return updated_user
    except Exception as e:
        logger.error(f"Email update failed for user_id {user.id}: {e}")
        raise


@router.put("/",
            response_model=SUser,
            response_model_exclude_none=True,
)
async def user_update(updated_user: SUserUpdate, current_user: SUser):
    logger.info(f"User profile update attempt: user_id={current_user.id}")
    
    if current_user.username == updated_user.username and current_user.email == updated_user.email:
        logger.warning(f"User update failed: no changes provided for user_id: {current_user.id}")
        raise UserWasntChangedException()

    try:
        updated_user: SUser = await UsersDAO.update(current_user.id, **updated_user.model_dump(exclude_defaults=True))
        await rabbit_producer.update_user(current_user.id, updated_user.username, updated_user.email)
        
        logger.info(f"User profile updated successfully: user_id={current_user.id}")
        return updated_user
    except Exception as e:
        logger.error(f"User profile update failed for user_id {current_user.id}: {e}")
        raise


@router.put("/password")
async def user_update_password(current_password: str = Body(), new_password: str = Body(), user: SUser = Body()):
    logger.info(f"Password change attempt for user_id: {user.id}")
    
    if not auth_utils.validate_password(current_password, user.hashed_password):
        logger.warning(f"Password change failed: invalid current password for user_id: {user.id}")
        raise InvalidPasswordException()

    try:
        new_password = auth_utils.hash_password(new_password)
        await UsersDAO.update_password(user.id, new_password)
        await rabbit_producer.password_changed(user.id)
        
        logger.info(f"Password changed successfully for user_id: {user.id}")
        return {"message": "password has been changed"}
    except Exception as e:
        logger.error(f"Password change failed for user_id {user.id}: {e}")
        raise


@router.delete("/")
async def user_delete(user_id: str):
    logger.info(f"User deletion attempt: user_id={user_id}")
    
    try:
        await UsersDAO.delete(int(user_id))
        await rabbit_producer.delete_user(user_id)
        
        logger.info(f"User deleted successfully: user_id={user_id}")
        return {"message": "user deleted"}
    except Exception as e:
        logger.error(f"User deletion failed for user_id {user_id}: {e}")
        raise


def generate_verification_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


@router.get("/verification_code")
async def request_verification_code(user_id: int):  
    logger.info(f"Verification code request for user_id: {user_id}")
    
    user = await UsersDAO.find_one_or_none(id=user_id)
    if not user:
        logger.warning(f"Verification code request failed: user not found: {user_id}")
        raise UserNotFoundException()
    
    if not user.email:
        logger.warning(f"Verification code request failed: no email for user_id: {user_id}")
        raise ValueError("User has no email address")
    
    code = generate_verification_code()
    
    try:
        if current_token := await VerificationTokensDAO.find_one_or_none(user_id=user_id, is_used=False):
            await VerificationTokensDAO.delete(current_token.id)
            logger.debug(f"Removed existing verification token for user_id: {user_id}")
            
        await VerificationTokensDAO.insert(user_id=user_id, verification_token=code,
                                           is_used=False, expires_at=(datetime.utcnow() + timedelta(minutes=10)))
        
        await rabbit_producer.email_verification(user_id, code)
        
        logger.info(f"Verification code sent successfully to user_id: {user_id}")
        return {"message": "verification code sent"}
        
    except Exception as e:
        logger.error(f"Verification code request failed for user_id {user_id}: {e}")
        raise


@router.post("/verification_code")
async def verify_email(user_id: int = Body(), code: str = Body()):
    logger.info(f"Email verification attempt for user_id: {user_id}")
    
    token = await VerificationTokensDAO.find_one_or_none(user_id=user_id, is_used=False)
    if not token:
        logger.warning(f"Email verification failed: no valid token for user_id: {user_id}")
        raise VerificationTokenNotFoundException()
    
    if token.verification_token != code:
        logger.warning(f"Email verification failed: invalid code for user_id: {user_id}")
        raise InvalidVerificationTokenException()
    
    try:
        await VerificationTokensDAO.update(token.id, is_used=True)
        await UsersDAO.update(user_id, is_verified=True)
        
        logger.info(f"Email verified successfully for user_id: {user_id}")
        return {"message": "email verified"}
        
    except Exception as e:
        logger.error(f"Email verification failed for user_id {user_id}: {e}")
        raise
