import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from back.notification_service.message_broker.rabbitmq import rabbit_broker
from back.notification_service.api import notification_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    try:
        await rabbit_broker.start()
        logger.info("✅ RabbitMQ broker started in notification service")
    except Exception as e:
        logger.error(f"❌ Failed to start RabbitMQ broker: {e}")
        
    yield  # Приложение работает здесь
    
    # SHUTDOWN
    try:
        await rabbit_broker.stop()
        logger.info("✅ RabbitMQ broker stopped in notification service")
    except Exception as e:
        logger.warning(f"⚠️ RabbitMQ broker shutdown error: {e}")


# Create combined app
notification_app = FastAPI(
    title="Notification Service",
    description="Combined FastAPI + FastStream notification service",
    lifespan=lifespan
)

# Include the notification API routes
notification_app.include_router(notification_router)
