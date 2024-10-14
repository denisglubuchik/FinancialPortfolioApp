from fastapi import FastAPI

from back.config import UserSettings

user_app = FastAPI()

user_settings = UserSettings()
