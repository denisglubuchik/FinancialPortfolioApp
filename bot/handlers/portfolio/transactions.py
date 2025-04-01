# todo добавление транзакции в портфолио
import operator

from aiogram.enums import ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, SwitchTo, Button
from aiogram_dialog.widgets.text import Const, Format

from bot.services.portfolios import get_assets, add_transaction


class TransactionsStates(StatesGroup):
    select_asset = State()
    select_transaction_type = State()
    add_quantity = State()
    add_price = State()
    confirm = State()


async def assets_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    # получить ассеты
    assets = await get_assets()
    return {
        'assets': [(asset["id"], asset["symbol"]) for asset in assets]
    }


async def on_asset_selected(callback: CallbackQuery, select: Select, dm: DialogManager, item_id: str):
    dm.dialog_data['selected_asset_id'] = item_id
    await dm.switch_to(TransactionsStates.select_transaction_type)


async def on_transaction_type_selected(callback: CallbackQuery, select: Select, dm: DialogManager, item_id: str):
    dm.dialog_data['transaction_type'] = item_id
    await dm.switch_to(TransactionsStates.add_quantity)


async def on_add_quantity(message: Message, mi: MessageInput, dm: DialogManager):
    #проверка числа
    dm.dialog_data['quantity'] = message.text
    await dm.switch_to(TransactionsStates.add_price)


async def on_add_price(message: Message, mi: MessageInput, dm: DialogManager):
    # проверка числа
    dm.dialog_data['price'] = message.text
    await dm.switch_to(TransactionsStates.confirm)


async def confirm_transaction_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    assets = await get_assets()
    selected_asset_id = dialog_manager.dialog_data.get('selected_asset_id', None)
    if not selected_asset_id:
        selected_asset_id = dialog_manager.start_data["selected_asset_id"]

    asset = next(asset for asset in assets if asset["id"] == int(selected_asset_id))

    transaction_type = "Покупка" if dialog_manager.dialog_data['transaction_type'] == "buy" else "Продажа"

    return {
        'transaction': f"Актив: {asset['symbol']}\n"
                       f"Тип транзакции: {transaction_type}\n"
                       f"Количество: {dialog_manager.dialog_data['quantity']}\n"
                       f"Цена: {dialog_manager.dialog_data['price']}",
    }


async def on_confirm_transaction(callback: CallbackQuery, button: Button, dm: DialogManager):
    back_user_id = dm.middleware_data["backend_user_id"]
    back_portfolio_id = dm.middleware_data["backend_portfolio"]["id"]

    selected_asset_id = dm.dialog_data.get('selected_asset_id', None)
    if not selected_asset_id:
        selected_asset_id = dm.start_data["selected_asset_id"]

    transaction_type = dm.dialog_data['transaction_type']
    quantity = dm.dialog_data['quantity']
    price = dm.dialog_data['price']

    try:
        transaction_message = await add_transaction(back_user_id, back_portfolio_id,
                                            selected_asset_id, transaction_type,
                                            quantity, price)

        await callback.message.answer(transaction_message)

        from bot.handlers.portfolio.portfolio_main_menu import PortfolioMenu
        await dm.start(PortfolioMenu.main, mode=StartMode.RESET_STACK)

    except Exception:
        await callback.message.answer("Что-то пошло не так")

    # добавить транзакцию


dialog = Dialog(
    Window(
        Const("Выберите актив"),
        ScrollingGroup(
            Select(
                Format('{item[1]}'),
                id="s_asset",
                item_id_getter=operator.itemgetter(0),
                items="assets",
                on_click=on_asset_selected
            ),
            id="sg_assets",
            width=1,
            height=5,
            hide_on_single_page=True
        ),
        Cancel(Const("Назад")),
        getter=assets_getter,
        state=TransactionsStates.select_asset
    ),
    Window(
        Const("Выберите тип транзакции"),
        Select(
            Format('{item[1]}'),
            id="s_transaction_type",
            item_id_getter=operator.itemgetter(0),
            items=[("buy","Покупка"), ("sell","Продажа")],
            on_click=on_transaction_type_selected
        ),
        SwitchTo(Const("Назад"), id="back", state=TransactionsStates.select_asset),
        state=TransactionsStates.select_transaction_type
    ),
    Window(
        Const("Введите количество"),
        MessageInput(on_add_quantity, content_types=ContentType.TEXT),
        SwitchTo(Const("Назад"), id="back", state=TransactionsStates.select_transaction_type),
        state=TransactionsStates.add_quantity
    ),
    Window(
        Const("Введите цену за единицу"),
        MessageInput(on_add_price, content_types=ContentType.TEXT),
        SwitchTo(Const("Назад"), id="back", state=TransactionsStates.add_quantity),
        state=TransactionsStates.add_price
    ),
    Window(
        Const("Подтвердите транзакцию"),
        Format("{transaction}"),
        Button(Const("Подтверждаю"), id="confirm_transaction", on_click=on_confirm_transaction),
        Cancel(Const("Отмена")),
        getter=confirm_transaction_getter,
        state=TransactionsStates.confirm
    )
)
