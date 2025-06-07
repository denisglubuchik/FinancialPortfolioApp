from contextlib import asynccontextmanager
from fastapi import FastAPI

from back.user_service.message_broker.rabbitmq import rabbit_broker
from back.config import UserSettings
from back.user_service.routers import router

user_settings = UserSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    try:
        await rabbit_broker.start()
    except Exception as e:
        print(e)
        
    yield  # Приложение работает здесь
    
    # SHUTDOWN
    await rabbit_broker.stop()


user_app = FastAPI(lifespan=lifespan)

user_app.include_router(router)
