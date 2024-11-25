from fastapi import HTTPException


class AuthException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidTokenException(AuthException):
    status_code = 401

    def __init__(self, e):
        self.detail = f"invalid token {e}"


class InvalidTokenTypeException(AuthException):
    status_code = 401

    def __init__(self, current_token_type, token_type):
        self.detail = f"invalid token type {current_token_type!r} expected {token_type!r}"
