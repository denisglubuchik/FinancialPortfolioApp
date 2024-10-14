from back.portfolio_service.repositories.base import SQLAlchemyRepository
from back.portfolio_service.models.users import Users


class UsersRepository(SQLAlchemyRepository):
    model = Users
