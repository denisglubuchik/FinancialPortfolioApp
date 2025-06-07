from contextlib import asynccontextmanager
from fastapi import FastAPI

from back.notification_service.message_broker.rabbitmq import rabbit_broker
from back.notification_service.api import notification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    try:
        await rabbit_broker.start()
        print("✅ RabbitMQ broker started in notification service")
    except Exception as e:
        print(f"❌ Failed to start RabbitMQ broker: {e}")
        
    yield  # Приложение работает здесь
    
    # SHUTDOWN
    try:
        await rabbit_broker.stop()
        print("✅ RabbitMQ broker stopped in notification service")
    except Exception as e:
        print(f"⚠️ RabbitMQ broker shutdown error: {e}")


# Create combined app
notification_app = FastAPI(
    title="Notification Service",
    description="Combined FastAPI + FastStream notification service",
    lifespan=lifespan
)

# Include the notification API routes
notification_app.include_router(notification_router)
