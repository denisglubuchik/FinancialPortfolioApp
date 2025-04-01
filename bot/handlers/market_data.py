#todo вывод курсов интересующих валют, брать значения из редиса, список валют получать через реббит и кешировать или через редис
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window


class MarketDataStates(StatesGroup):
    main = State()

dialog = Dialog(
    Window(
        state=MarketDataStates.main
    )
)