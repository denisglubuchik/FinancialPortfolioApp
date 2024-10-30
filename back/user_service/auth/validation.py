from fastapi import Depends,  Form
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from back.user_service.db.dao import UsersDAO
from back.user_service.auth.helpers import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, JWTPayload
from back.user_service.auth import utils as auth_utils
from back.user_service.schemas.users import SUser
from back.user_service.exceptions import InvalidTokenException, InvalidTokenTypeException, UserNotFoundException, \
    InvalidPasswordException, InvalidUsernameException

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
)


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> JWTPayload:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise InvalidTokenException(e)
    return JWTPayload(**payload)


async def validate_token_type(
    payload: JWTPayload,
    token_type: str,
) -> bool:
    current_token_type = payload.token_type
    if current_token_type == token_type:
        return True
    raise InvalidTokenTypeException(current_token_type, token_type)


async def get_user_by_token_sub(payload: JWTPayload) -> SUser:
    username: str | None = payload.sub
    if user := await UsersDAO.find_one_or_none(username=username):
        return SUser.model_validate(user)
    raise UserNotFoundException()


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        payload: JWTPayload = Depends(get_current_token_payload),
    ):
        await validate_token_type(payload, self.token_type)
        return await get_user_by_token_sub(payload)


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
) -> SUser:
    if not (user := await UsersDAO.find_one_or_none(username=username)):
        raise InvalidUsernameException()

    user = SUser.model_validate(user)

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        raise InvalidPasswordException()

    return user
