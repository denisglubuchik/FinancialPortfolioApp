from fastapi import HTTPException


class UserException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(UserException):
    status_code = 409
    detail = "user already exists"


class UserNotFoundException(UserException):
    status_code = 404
    detail = "user not found"


class UserWasntChangedException(UserException):
    status_code = 400
    detail = "you change nothing, so user wasn't changed"


class InvalidTokenException(UserException):
    status_code = 401

    def __init__(self, e):
        self.detail = f"invalid token {e}"


class InvalidTokenTypeException(UserException):
    status_code = 401

    def __init__(self, current_token_type, token_type):
        self.detail = f"invalid token type {current_token_type!r} expected {token_type!r}"


class InvalidUsernameException(UserException):
    status_code = 401
    detail = "invalid username"


class InvalidPasswordException(UserException):
    status_code = 401
    detail = "invalid password"
