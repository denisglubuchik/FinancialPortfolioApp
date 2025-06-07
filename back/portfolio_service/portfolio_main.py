import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from back.portfolio_service.message_broker.rabbitmq import rabbit_broker
from back.portfolio_service.routers import all_routers
from back.portfolio_service.utils.uow import UnitOfWork
from back.portfolio_service.redis import redis_client
from back.portfolio_service.schedulers.price_scheduler import PriceMonitoringScheduler
from back.portfolio_service.services.portfolio import PortfolioService


logger = logging.getLogger(__name__)

# Глобальный планировщик мониторинга цен
price_scheduler: PriceMonitoringScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    global price_scheduler
    
    try:
        # Запуск RabbitMQ
        await rabbit_broker.start()
        logger.info("✅ RabbitMQ broker started")
        
        # Подключение к Redis
        await redis_client.connect()
        logger.info("✅ Redis client connected")
        
        # Запуск планировщика мониторинга цен
        price_scheduler = PriceMonitoringScheduler(
            price_change_threshold=5.0,  # 5% порог изменения цены
            check_interval_minutes=15    # Проверка каждые 15 минут
        )
        
        if await price_scheduler.start():
            logger.info("✅ Price monitoring scheduler started successfully")
        else:
            logger.error("❌ Failed to start price monitoring scheduler")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
        
    yield  # Приложение работает здесь
    
    # SHUTDOWN
    logger.info("🔄 Portfolio service shutdown initiated...")
    
    # Остановка планировщика мониторинга цен
    if price_scheduler:
        if await price_scheduler.stop():
            logger.info("✅ Price monitoring scheduler stopped successfully")
        else:
            logger.warning("⚠️ Price monitoring scheduler shutdown had issues")
    
    # Остановка RabbitMQ и Redis
    try:
        await rabbit_broker.stop()
        logger.info("✅ RabbitMQ broker stopped")
    except Exception as e:
        logger.warning(f"⚠️ RabbitMQ broker shutdown error: {e}")
    
    try:
        await redis_client.close()
        logger.info("✅ Redis client disconnected")
    except Exception as e:
        logger.warning(f"⚠️ Redis client shutdown error: {e}")
    
    logger.info("✅ Portfolio service shutdown complete")


portfolio_app = FastAPI(lifespan=lifespan)

for router in all_routers:
    portfolio_app.include_router(router)



@portfolio_app.middleware("http")
async def update_portfolio_value_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)

    response = await call_next(request)

    user_id = request.headers.get("X-User-ID")

    if user_id:
        try:
            user_id = int(user_id)
            portfolio_id = await PortfolioService().get_portfolio(UnitOfWork(), user_id=user_id)
            if portfolio_id:
                await PortfolioService().update_portfolio_value(UnitOfWork(), portfolio_id.id)
        except ValueError:
            logger.warning(f"Некорректный user_id: {user_id}")

    return response



