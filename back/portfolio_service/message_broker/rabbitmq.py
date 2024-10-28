from faststream.rabbit import RabbitBroker

from back.config import RabbitMQSettings
from back.portfolio_service.database import async_session_maker
from back.portfolio_service.repositories.users import UsersRepository

rabbit_broker = RabbitBroker(RabbitMQSettings().RABBITMQ_MQ)


@rabbit_broker.subscriber("user_created")
async def handle_new_user(message):
    user_id = message["user_id"]
    username = message["username"]
    async with async_session_maker() as session:
        await UsersRepository(session).add({"id": user_id, "username": username})
        await session.commit()


@rabbit_broker.subscriber("user_deleted")
async def handle_delete_user(message):
    user_id = message["user_id"]
    async with async_session_maker() as session:
        await UsersRepository(session).delete(id=user_id)
        await session.commit()
