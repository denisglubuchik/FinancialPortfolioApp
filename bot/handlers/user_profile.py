from aiogram import Router
from aiogram.enums import ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Cancel
from aiogram_dialog.widgets.text import Const, Format

from bot.services.users import get_user_by_tg, change_email
from bot.utils.others import is_valid_email

router = Router(name="profile")

class ProfileStates(StatesGroup):
    main = State()
    change_email = State()
    waiting_for_email = State()


async def profile_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    profile = await get_user_by_tg(dialog_manager.event.from_user.id)
    dialog_manager.dialog_data["backend_user_id"] = profile["id"]

    profile_description = (f"{profile['username']}\n"
                           f"{profile['email']}\n")

    return {
        "user_profile": profile_description,
    }


async def on_change_email(message: Message, mi: MessageInput, dm: DialogManager):
    #проверка валидности email
    email = message.text
    if not is_valid_email(email):
        await message.answer(text="email не валиден")
        return
    #запрос на бек
    result_message = await change_email(message.from_user.id, email)
    await message.answer(text=result_message)
    await dm.switch_to(ProfileStates.main)


dialog = Dialog(
    Window(
        Format("{user_profile}"),
        SwitchTo(Const("Изменить email"), id="change_email", state=ProfileStates.change_email),
        Cancel(Const('Назад')),
        getter=profile_getter,
        state=ProfileStates.main
    ),
    Window(
        Const("Введите новый email"),
        MessageInput(on_change_email, content_types=ContentType.TEXT),
        state=ProfileStates.change_email
    )
)
