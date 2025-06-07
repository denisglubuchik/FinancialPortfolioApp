from fastapi import FastAPI

from back.gateway.routers.api import router as api_router
from back.gateway.routers.new_tg import router as tg_router
from back.gateway.routers.notifications import router as notifications_router

api_gateway = FastAPI()
api_gateway.include_router(api_router)
api_gateway.include_router(tg_router)
api_gateway.include_router(notifications_router)
