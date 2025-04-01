from aiogram import Router, Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


def get_handlers_router() -> Router:
    from . import start, menu

    router = Router()
    router.include_routers(
        menu.router,
        start.router,
    )

    return router


async def setup_commands_menu(bot: Bot):
    commands = [
        # BotCommand(command='rewrite', description="Рерайт текста"),
        # BotCommand(command='summary', description="Саммари текста"),
        # BotCommand(command='survey', description="Пройти анкету"),
        # BotCommand(command='help', description="Помощь"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def delete_commands_menu(bot: Bot):
    await bot.delete_my_commands(BotCommandScopeDefault())
