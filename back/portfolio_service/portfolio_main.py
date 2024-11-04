from fastapi import FastAPI

from back.portfolio_service.message_broker.rabbitmq import rabbit_broker
from back.portfolio_service.routers.users import router as users_router
from back.portfolio_service.routers.portfolio import router as portfolio_router
from back.portfolio_service.routers.assets import router as assets_router
from back.portfolio_service.routers.transactions import router as transactions_router
from back.portfolio_service.routers.portfolio_assets import router as portfolio_assets_router

# from back.config import PortfolioSettings

portfolio_app = FastAPI()

portfolio_app.include_router(users_router)
portfolio_app.include_router(portfolio_router)
portfolio_app.include_router(assets_router)
portfolio_app.include_router(transactions_router)
portfolio_app.include_router(portfolio_assets_router)

# portfolio_settings = PortfolioSettings()


@portfolio_app.on_event("startup")
async def start_rabbit():
    try:
        await rabbit_broker.start()
    except Exception as e:
        print(e)


@portfolio_app.on_event("shutdown")
async def stop_rabbit():
    await rabbit_broker.stop()
