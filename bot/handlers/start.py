from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.services.users import add_new_user

router = Router(name="start")

LEX = {
    "hello": "Привет это бот для трекинга твоего финансового портфеля",
    "help": ""
}

@router.message(CommandStart())
async def on_start_command(message: Message):
    await message.answer(LEX["hello"])
    await add_new_user(message.from_user.id, message.from_user.username)


@router.message(Command("help"))
async def on_help_command(message: Message):
    await message.answer(text=LEX["help"])
