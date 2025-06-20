from fastapi import HTTPException


class PortfolioException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class PortfolioAssetDoesntExistCannotSellException(PortfolioException):
    status_code = 404
    detail = "Asset doesn't exist, you cannot sell it"


class TransactionDoesntExistsException(PortfolioException):
    status_code = 404
    detail = "Transaction doesn't exist"

class TransactionCannotConductException(PortfolioException):
    status_code = 409
    detail = "Can not conduct transaction"


class PortfolioAlreadyExistException(PortfolioException):
    status_code = 409
    detail = "Portfolio already exist"


class PortfolioDoesntExistException(PortfolioException):
    status_code = 404
    detail = "Portfolio doesn't exist"


class PortfolioAssetDoesntExistException(PortfolioException):
    status_code = 404
    detail = "Portfolio asset doesn't exist"


class AssetDoesntExistException(PortfolioException):
    status_code = 404
    detail = "Asset doesn't exist"


class AssetAlreadyExistException(PortfolioException):
    status_code = 409
    detail = "Asset already exist"


class UserDoesntExistException(PortfolioException):
    status_code = 404
    detail = "User doesn't exist"


class UserDoesntOwnPortfolioException(PortfolioException):
    status_code = 403
    detail = "User doesn't own this portfolio"


class UserDoesntOwnTransactionException(PortfolioException):
    status_code = 403
    detail = "User doesn't own this transaction"
