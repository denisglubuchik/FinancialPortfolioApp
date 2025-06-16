from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.services.users import add_new_user

router = Router(name="start")

LEX = {
    "hello": """🎯 **Добро пожаловать в FinancialPortfolio Bot!**

Этот бот поможет вам:
📈 Отслеживать ваш инвестиционный портфель
💰 Анализировать доходность активов
📊 Получать актуальные данные о рынке
🔔 Настраивать уведомления о важных изменениях

Для начала работы используйте команду /help, чтобы узнать все доступные функции.""",
    
    "help": """📋 **Доступные команды:**

🏠 **Основные команды:**
• /start - Запустить бота
• /menu - Открыть главное меню
• /help - Показать это сообщение

📱 **Главное меню содержит:**

📊 **Портфель** - Управление вашим инвестиционным портфелем:
   • Просмотр текущих активов и их стоимости
   • Добавление новых транзакций (покупка/продажа)
   • Детальная информация по каждому активу

👤 **Профиль** - Управление вашим аккаунтом:
   • Просмотр информации профиля
   • Изменение email адреса
   • Подтверждение email (верификация)

🪙 **Курсы валют** - Актуальная информация о криптовалютах:
   • Текущие цены популярных криптовалют
   • Изменения за 24 часа
   • Детальная информация по каждой валюте

💡 **Как пользоваться:**
1. Используйте /menu для открытия главного меню
2. Выберите нужный раздел кнопками
3. Следуйте инструкциям в диалогах
"""
}

@router.message(CommandStart())
async def on_start_command(message: Message):
    await message.answer(LEX["hello"], parse_mode="Markdown")
    await add_new_user(message.from_user.id, message.from_user.username)


@router.message(Command("help"))
async def on_help_command(message: Message):
    await message.answer(text=LEX["help"], parse_mode="Markdown")
