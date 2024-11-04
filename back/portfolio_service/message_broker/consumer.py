from faststream.rabbit import RabbitRouter

from back.portfolio_service.database import async_session_maker
from back.portfolio_service.repositories.users import UsersRepository

rabbit_router = RabbitRouter()


@rabbit_router.subscriber("user_created")
async def handle_new_user(message):
    user_id = message["user_id"]
    username = message["username"]
    async with async_session_maker() as session:
        await UsersRepository(session).add({"id": user_id, "username": username})
        await session.commit()


@rabbit_router.subscriber("user_updated")
async def handle_update_user(message):
    user_id = message["user_id"]
    username = message["username"]
    async with async_session_maker() as session:
        await UsersRepository(session).update(id=user_id, data={"username": username})
        await session.commit()


@rabbit_router.subscriber("user_deleted")
async def handle_delete_user(message):
    user_id = message["user_id"]
    async with async_session_maker() as session:
        await UsersRepository(session).delete(id=user_id)
        await session.commit()
