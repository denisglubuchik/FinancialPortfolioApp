import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from back.logging import setup_logging_base_config
from back.notification_service.message_broker.rabbitmq import rabbit_broker
from back.notification_service.api import notification_router


setup_logging_base_config()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await rabbit_broker.start()
        logger.info("RabbitMQ broker started in notification service")
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ broker in notification service: {e}")
        
    yield

    try:
        await rabbit_broker.stop()
        logger.info("RabbitMQ broker stopped in notification service")
    except Exception as e:
        logger.warning(f"RabbitMQ broker shutdown error in notification service: {e}")


notification_app = FastAPI(
    title="Notification Service",
    description="Combined FastAPI + FastStream notification service",
    lifespan=lifespan
)

notification_app.include_router(notification_router)
