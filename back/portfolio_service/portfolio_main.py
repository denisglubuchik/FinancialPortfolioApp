import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from back.logging import setup_logging_base_config
from back.portfolio_service.message_broker.rabbitmq import rabbit_broker
from back.portfolio_service.routers import all_routers
from back.portfolio_service.utils.uow import UnitOfWork
from back.portfolio_service.redis import redis_client
from back.portfolio_service.schedulers.price_scheduler import PriceMonitoringScheduler
from back.portfolio_service.services.portfolio import PortfolioService


setup_logging_base_config()
logger = logging.getLogger(__name__)

price_scheduler: PriceMonitoringScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global price_scheduler
    
    try:
        await rabbit_broker.start()
        logger.info("RabbitMQ broker started in portfolio service")

        await redis_client.connect()
        logger.info("Redis client connected in portfolio service")

        price_scheduler = PriceMonitoringScheduler(
            price_change_threshold=5.0,
            check_interval_minutes=15
        )
        
        if await price_scheduler.start():
            logger.info("Price monitoring scheduler started successfully")
        else:
            logger.error("Failed to start price monitoring scheduler")
        
    except Exception as e:
        logger.error(f"Startup error in portfolio service: {e}")
        raise
        
    yield

    logger.info("Portfolio service shutdown initiated")

    if price_scheduler:
        await price_scheduler.stop()

    try:
        await rabbit_broker.stop()
        await redis_client.close()
        logger.info("Portfolio service shutdown complete")
    except Exception as e:
        logger.warning(f"Portfolio service shutdown error: {e}")


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
            logger.warning(f"Invalid user_id: {user_id}")

    return response



