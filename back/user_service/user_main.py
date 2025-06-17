import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from back.logging import setup_logging_base_config
from back.user_service.message_broker.rabbitmq import rabbit_broker
from back.user_service.routers import router


setup_logging_base_config()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await rabbit_broker.start()
        logger.info("RabbitMQ broker started in user service")
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ broker in user service: {e}")
        
    yield

    try:
        await rabbit_broker.stop()
        logger.info("RabbitMQ broker stopped in user service")
    except Exception as e:
        logger.warning(f"RabbitMQ broker shutdown error in user service: {e}")


user_app = FastAPI(lifespan=lifespan)

user_app.include_router(router)
