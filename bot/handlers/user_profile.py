from aiogram import Router
from aiogram.enums import ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Cancel, Button, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.services.users import get_user_by_tg, change_email, request_verification_code, verify_email_code
from bot.utils.others import is_valid_email

router = Router(name="profile")

class ProfileStates(StatesGroup):
    main = State()
    change_email = State()
    waiting_for_email = State()
    email_verification = State()
    waiting_for_verification_code = State()


async def profile_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    profile = await get_user_by_tg(dialog_manager.event.from_user.id)
    dialog_manager.dialog_data["backend_user_id"] = profile["id"]

    # Проверяем статус верификации
    is_verified = profile.get("is_verified", False)
    verification_status = "✅ Подтвержден" if is_verified else "❌ Не подтвержден"
    
    profile_description = (f"👤 Пользователь: {profile['username']}\n"
                           f"📧 Email: {profile['email'] or 'Не указан'}\n"
                           f"🔐 Статус email: {verification_status}")

    # Определяем текст кнопки в зависимости от наличия email
    has_email = bool(profile.get("email"))
    email_button_text = "Изменить email" if has_email else "Добавить email"

    return {
        "user_profile": profile_description,
        "has_email": has_email,
        "is_verified": is_verified,
        "email_button_text": email_button_text,
        "can_verify": has_email and not is_verified,  # Можно верифицировать только если есть email и он не подтвержден
    }


async def on_change_email(message: Message, mi: MessageInput, dm: DialogManager):
    """Обработчик изменения email"""
    email = message.text
    if not is_valid_email(email):
        await message.answer(text="Email не валиден")
        return
    
    # Запрос на изменение email
    result_message = await change_email(message.from_user.id, email)
    await message.answer(text=result_message)
    
    # Если email изменен успешно, переходим к верификации
    if "изменен" in result_message.lower():
        await dm.switch_to(ProfileStates.email_verification)
    else:
        await dm.switch_to(ProfileStates.main)


async def on_request_verification_code(callback, button, dm: DialogManager):
    """Обработчик запроса кода верификации"""
    tg_id = dm.event.from_user.id
    result = await request_verification_code(tg_id)
    await callback.message.answer(result)
    await dm.switch_to(ProfileStates.waiting_for_verification_code)


async def on_verify_code(message: Message, mi: MessageInput, dm: DialogManager):
    """Обработчик верификации кода"""
    code = message.text.strip()
    
    # Проверяем, что код состоит из 6 цифр
    if not code.isdigit() or len(code) != 6:
        await message.answer("Код должен состоять из 6 цифр")
        return
    
    tg_id = message.from_user.id
    result = await verify_email_code(tg_id, code)
    
    # Проверяем результат верификации
    if "invalid verification token" in result.lower() or "ошибка" in result.lower():
        await message.answer("❌ Неверный код верификации. Попробуйте еще раз или запросите новый код.")
        return  # Остаемся в том же состоянии для повторного ввода
    
    await message.answer(result)
    
    # Возвращаемся в главное меню профиля только при успешной верификации
    await dm.switch_to(ProfileStates.main)


dialog = Dialog(
    Window(
        Format("{user_profile}"),
        Row(
            SwitchTo(Format("{email_button_text}"), id="change_email", state=ProfileStates.change_email),
            Button(
                Const("Подтвердить email"), 
                id="verify_email", 
                on_click=on_request_verification_code,
                when="can_verify"
            ),
        ),
        Cancel(Const('Назад')),
        getter=profile_getter,
        state=ProfileStates.main
    ),
    Window(
        Const("Введите новый email"),
        MessageInput(on_change_email, content_types=ContentType.TEXT),
        Cancel(Const('Отмена')),
        state=ProfileStates.change_email
    ),
    Window(
        Const("📧 Подтверждение email"),
        Const("Для подтверждения email нажмите кнопку ниже.\nКод будет отправлен на указанный email адрес."),
        Button(Const("Отправить код"), id="send_code", on_click=on_request_verification_code),
        Cancel(Const('Отмена')),
        state=ProfileStates.email_verification
    ),
    Window(
        Const("🔐 Введите код верификации"),
        Const("Введите 6-значный код, который был отправлен на ваш email:"),
        MessageInput(on_verify_code, content_types=ContentType.TEXT),
        Row(
            Button(Const("Запросить новый код"), id="request_new_code", on_click=on_request_verification_code),
            Cancel(Const('Отмена')),
        ),
        state=ProfileStates.waiting_for_verification_code
    )
)
