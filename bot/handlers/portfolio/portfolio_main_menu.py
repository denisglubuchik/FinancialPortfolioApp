#todo добавить вывод активов с текущими ценами и изменениями цены за сутки

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Button, Row, FirstPage, PrevPage, CurrentPage, NextPage, LastPage
from aiogram_dialog.widgets.text import Format, Const, List

from bot.handlers.portfolio.portfolio_assets import dialog as portfolio_assets_dialog, PortfolioAssetsStates
from bot.handlers.portfolio.transactions import dialog as transactions_dialog, TransactionsStates
from bot.services.portfolios import get_portfolio_assets

LEX = {
    'back': 'Назад'
}

router = Router(name="portfolio")


class PortfolioMenu(StatesGroup):
    main = State()


async def on_portfolio_assets_click(callback: CallbackQuery, button: Button, dm: DialogManager):
    await dm.start(state=PortfolioAssetsStates.main, data={"portfolio_assets": dm.dialog_data["portfolio_assets"]})


async def on_transactions_click(callback: CallbackQuery, button: Button, dm: DialogManager):
    await dm.start(state=TransactionsStates.select_asset)


async def portfolio_assets_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    back_user_id = dialog_manager.middleware_data["backend_user_id"]
    back_portfolio = dialog_manager.middleware_data["backend_portfolio"]
    portfolio_assets = await get_portfolio_assets(back_user_id, back_portfolio["id"])
    dialog_manager.dialog_data["portfolio_assets"] = portfolio_assets

    portfolio_details = (
            f"💰 <b>Текущая стоимость портфеля:</b> {back_portfolio['current_value']:,.2f}".replace(",", " ") + "$\n"
            f"📈 <b>Сумма вложений:</b> {back_portfolio['total_invested']:,.2f}".replace(",", " ") + "$\n"
    )

    if not portfolio_assets:
        return {
            'is_empty': True,
            'portfolio_details': portfolio_details,
            'portfolio_assets': ["Портфель пуст 🫥"],
        }

    asset_lines = []
    for asset in portfolio_assets:
        change_icon = "📉" if float(asset["usd_24h_change"]) < 0 else "📈"
        asset_lines.append(
            f"{change_icon} <b>{asset['symbol']}</b> — {asset['quantity']} шт.\n"
            f"💸 Цена: {asset['current_price']}$\n"
            f"📊 Изменение за 24ч: {asset['usd_24h_change']:.2f}%\n"
        )

    return {
        'is_empty': False,
        'portfolio_details': portfolio_details,
        'portfolio_assets': asset_lines,
        'pagination': len(portfolio_assets) > 5,
    }

dialog = Dialog(
    Window(
        Format("{portfolio_details}"),
        Const("Ваши активы:"),
        List(
            Format('{item}'),
            id="l_portfolio_assets",
            items="portfolio_assets",
            page_size=5,
        ),
        Row(
        FirstPage(scroll='l_portfolio_assets', text=Format("<< {target_page1}")),
            PrevPage(scroll='l_portfolio_assets', text=Format("<")),
            CurrentPage(scroll='l_portfolio_assets', text=Format("{current_page1}")),
            NextPage(scroll='l_portfolio_assets', text=Format(">")),
            LastPage(scroll='l_portfolio_assets', text=Format("{target_page1} >>")),
            when="pagination"
        ),
        Button(Const("Перейти к активам"), id="to_portfolio_assets", on_click=on_portfolio_assets_click, when=~F.is_empty),
        Button(Const("Добавить транзакцию"), id="add_transactions", on_click=on_transactions_click),
        Cancel(Const('Закрыть')),
        state=PortfolioMenu.main,
        getter=portfolio_assets_getter
    )
)


router.include_routers(
    dialog,
    portfolio_assets_dialog,
    transactions_dialog,
)
