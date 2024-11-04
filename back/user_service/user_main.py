from fastapi import FastAPI

from back.user_service.message_broker.rabbitmq import rabbit_broker
from back.config import UserSettings
from back.user_service.routers import router

user_app = FastAPI()

user_app.include_router(router)

user_settings = UserSettings()


@user_app.on_event("startup")
async def start_rabbit():
    try:
        await rabbit_broker.start()
    except Exception as e:
        print(e)


@user_app.on_event("shutdown")
async def stop_rabbit():
    await rabbit_broker.stop()
