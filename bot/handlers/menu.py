from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const

from bot.handlers.portfolio.portfolio_main_menu import router as portfolio_router, PortfolioMenu
from bot.handlers.user_profile import dialog as user_profile_dialog, ProfileStates
from bot.handlers.market_data import MarketDataStates
from bot.middlewares.portfolio import PortfolioMiddleware
from bot.middlewares.users import UsersMiddleware

router = Router(name="menu")
router.message.middleware(UsersMiddleware())
router.callback_query.middleware(UsersMiddleware())
router.message.middleware(PortfolioMiddleware())
router.callback_query.middleware(PortfolioMiddleware())

class MenuStates(StatesGroup):
    main = State()


async def on_portfolio_click(callback: CallbackQuery, button: Button, dm: DialogManager):
    await dm.start(state=PortfolioMenu.main)


async def on_profile_click(callback: CallbackQuery, button: Button, dm: DialogManager):
    await dm.start(state=ProfileStates.main)


async def on_market_data_click(callback: CallbackQuery, button: Button, dm: DialogManager):
    await dm.start(state=MarketDataStates.main)


dialog = Dialog(
    Window(
        Const("Меню"),
        Button(Const("Портфель"), id="to_portfolio", on_click=on_portfolio_click),
        Button(Const("Профиль"), id="to_user_profile", on_click=on_profile_click),
        Button(Const("Курсы валют"), id="to_assets_prices", on_click=on_market_data_click),
        Cancel(Const('Закрыть')),
        state=MenuStates.main,
    )
)

router.include_routers(
    dialog,
    portfolio_router,
    user_profile_dialog,
)

@router.message(Command("menu"))
async def on_menu_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=MenuStates.main, mode=StartMode.RESET_STACK)