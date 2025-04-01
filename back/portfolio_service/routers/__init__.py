from back.portfolio_service.routers.users import router as users_router
from back.portfolio_service.routers.portfolio import router as portfolio_router
from back.portfolio_service.routers.assets import router as assets_router
from back.portfolio_service.routers.transactions import router as transactions_router
from back.portfolio_service.routers.portfolio_assets import router as portfolio_assets_router


all_routers = [
    users_router,
    portfolio_router,
    assets_router,
    transactions_router,
    portfolio_assets_router
]