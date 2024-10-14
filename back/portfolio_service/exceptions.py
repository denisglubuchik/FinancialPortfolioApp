from fastapi import HTTPException


class PortfolioException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class PortfolioAssetDoesntExistCannotSellException(PortfolioException):
    status_code = 404
    detail = "Asset doesn't exist, you cannot sell it"

