from back.portfolio_service.schemas.users import SUserCreate
from back.portfolio_service.utils.uow import IUnitOfWork


class UsersService:
    async def get_user(self, uow: IUnitOfWork, **kwargs):
        async with uow:
            user = await uow.users.get_one(**kwargs)
            return user

    async def add_user(self, uow: IUnitOfWork, user: SUserCreate):
        async with uow:
            user_id = await uow.users.add(user.model_dump())
            await uow.commit()
            return user_id