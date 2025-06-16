from aiogram import Router, Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


def get_handlers_router() -> Router:
    from . import start, menu
    from .market_data import router as market_data_router

    router = Router()

    router.include_routers(
        menu.router,
        start.router,
    )

    router.include_router(market_data_router)

    return router


async def setup_commands_menu(bot: Bot):
    commands = [
        BotCommand(command='menu', description="Главное меню"),
        BotCommand(command='help', description="Помощь"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def delete_commands_menu(bot: Bot):
    await bot.delete_my_commands(BotCommandScopeDefault())
