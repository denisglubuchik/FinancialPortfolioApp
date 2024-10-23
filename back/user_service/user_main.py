from fastapi import FastAPI

from back.config import UserSettings
from back.user_service.routers import router

user_app = FastAPI()

user_app.include_router(router)

user_settings = UserSettings()
