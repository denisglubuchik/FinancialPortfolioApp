from fastapi import FastAPI

from back.config import UserSettings
from back.user_service.routers import router

user_app = FastAPI()

user_app.include_router(router)

user_settings = UserSettings()


@user_app.on_event("startup")
async def start_rabbit():
    from back.user_service.message_broker.rabbitmq import rabbit_broker
    await rabbit_broker.start()


@user_app.on_event("shutdown")
async def stop_rabbit():
    from back.user_service.message_broker.rabbitmq import rabbit_broker
    await rabbit_broker.stop()