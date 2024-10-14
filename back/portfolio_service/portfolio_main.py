from fastapi import FastAPI

from back.portfolio_service.routers.portfolio import router as portfolio_router
from back.portfolio_service.routers.assets import router as assets_router
from back.portfolio_service.routers.transactions import router as transactions_router
from back.portfolio_service.routers.portfolio_assets import router as portfolio_assets_router

# from back.config import PortfolioSettings

portfolio_app = FastAPI()

portfolio_app.include_router(portfolio_router)
portfolio_app.include_router(assets_router)
portfolio_app.include_router(transactions_router)
portfolio_app.include_router(portfolio_assets_router)

# portfolio_settings = PortfolioSettings()
