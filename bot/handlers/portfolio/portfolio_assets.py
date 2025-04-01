#todo диалог с активами, вывод транзакций
import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo, ScrollingGroup, Select, Button
from aiogram_dialog.widgets.text import Format, Const
from aiogram.fsm.state import StatesGroup, State

from bot.handlers.portfolio.transactions import TransactionsStates


class PortfolioAssetsStates(StatesGroup):
    main = State()
    portfolio_asset_details = State()


async def portfolio_assets_getter(dialog_manager: DialogManager, **kwargs) -> dict:

    # portfolio_assets: list[tuple[tuple[int, int], str]] # list[tuple[tuple[portfolio_asset_id, asset_id], portfolio_asset]]
    portfolio_assets = dialog_manager.start_data['portfolio_assets']
    return {
        'portfolio_assets': [(asset['id'], asset['symbol']) for asset in portfolio_assets]
    }


async def portfolio_asset_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    selected_portfolio_asset = dialog_manager.dialog_data['selected_portfolio_asset']
    portfolio_assets = dialog_manager.start_data['portfolio_assets']

    portfolio_asset = next(asset for asset in portfolio_assets if asset["id"] == int(selected_portfolio_asset))
    dialog_manager.dialog_data['selected_asset_id'] = portfolio_asset['asset_id']
    # todo получить транзы по конкретному активу портфеля
    return {
        'portfolio_asset': f"<b>{portfolio_asset['symbol']}</b> — {portfolio_asset['quantity']} шт.\n"
        f"💸 Цена: {portfolio_asset['current_price']}$\n",
        "transactions": "",
    }

async def on_portfolio_asset_selected(callback: CallbackQuery, select: Select, dm: DialogManager, item_id: int):
    dm.dialog_data['selected_portfolio_asset'] = item_id
    await dm.switch_to(PortfolioAssetsStates.portfolio_asset_details)


async def on_add_transaction(callback: CallbackQuery, button: Button, dm: DialogManager):
    await dm.start(
        state=TransactionsStates.select_transaction_type,
        data={"selected_asset_id": dm.dialog_data['selected_asset_id']}
    )


dialog = Dialog(
    Window(
        Const("Ваши активы"),
        ScrollingGroup(
            Select(
                Format('{item[1]}'),
                id="s_portfolio_asset",
                item_id_getter=operator.itemgetter(0),
                items="portfolio_assets",
                on_click=on_portfolio_asset_selected
            ),
            id="sg_portfolio_assets",
            width=1,
            height=5,
            hide_on_single_page=True
        ),
        Cancel(Const("Назад")),
        getter=portfolio_assets_getter,
        state=PortfolioAssetsStates.main
    ),
    Window(
        Format("{portfolio_asset}"),
        Button(Const("Добавить транзакцию"), id="add_transactions", on_click=on_add_transaction),
        SwitchTo(Const("Назад"), id="back", state=PortfolioAssetsStates.main),
        getter=portfolio_asset_getter,
        state=PortfolioAssetsStates.portfolio_asset_details
    )
)
