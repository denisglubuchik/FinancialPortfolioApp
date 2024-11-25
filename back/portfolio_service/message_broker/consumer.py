from faststream.rabbit import RabbitRouter, RabbitExchange, ExchangeType

from back.portfolio_service.database import async_session_maker
from back.portfolio_service.repositories.users import UsersRepository

rabbit_router = RabbitRouter()


user_exchange = RabbitExchange("user_exchange", type=ExchangeType.DIRECT)


@rabbit_router.subscriber("portfolio_user_created", user_exchange)
async def handle_new_user(message):
    user_id = message["user_id"]
    username = message["username"]
    async with async_session_maker() as session:
        await UsersRepository(session).add({"id": user_id, "username": username})
        await session.commit()


@rabbit_router.subscriber("portfolio_user_updated", user_exchange)
async def handle_update_user(message):
    user_id = message["user_id"]
    username = message["username"]
    async with async_session_maker() as session:
        await UsersRepository(session).update(id=user_id, data={"username": username})
        await session.commit()


@rabbit_router.subscriber("portfolio_user_deleted", user_exchange)
async def handle_delete_user(message):
    user_id = message["user_id"]
    async with async_session_maker() as session:
        await UsersRepository(session).delete(int(user_id))
        await session.commit()
