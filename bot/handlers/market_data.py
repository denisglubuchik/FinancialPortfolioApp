#todo вывод курсов интересующих валют, брать значения из редиса, список валют получать через реббит и кешировать или через редис
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, Cancel, Back, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from datetime import datetime

from bot.services.market_data import get_popular_cryptocurrencies, get_multiple_crypto_prices, get_crypto_price

router = Router(name="market_data")

class MarketDataStates(StatesGroup):
    main = State()
    detail = State()

async def get_crypto_data(dialog_manager: DialogManager, **kwargs):
    """Получаем данные о криптовалютах"""
    crypto_list = await get_popular_cryptocurrencies()
    crypto_data = await get_multiple_crypto_prices(crypto_list)
    
    # Подготавливаем данные для отображения
    crypto_items = []
    for crypto, data in crypto_data.items():
        price = data.get("current_price")
        change = data.get("usd_24h_change")
        
        if price and change:
            # Форматируем цену с двумя знаками после запятой
            try:
                price_float = float(price)
                price_formatted = f"{price_float:.2f}"
            except (ValueError, TypeError):
                price_formatted = price
                
            # Форматируем изменение цены с двумя знаками после запятой
            try:
                change_float = float(change)
                change_formatted = f"{change_float:.2f}"
                emoji = "🔴" if change_float < 0 else "🟢"
            except (ValueError, TypeError):
                change_formatted = change
                emoji = "⚪"
                
            display_text = f"{crypto}: ${price_formatted} ({emoji} {change_formatted}%)"
        else:
            display_text = f"{crypto}: данные недоступны"
            
        crypto_items.append((crypto, display_text))
    
    return {
        "crypto_data": crypto_data,
        "crypto_items": crypto_items,
        "selected_crypto": dialog_manager.dialog_data.get("selected_crypto", "")
    }

async def get_crypto_detail(dialog_manager: DialogManager, **kwargs):
    """Получаем подробные данные о выбранной криптовалюте"""
    selected = dialog_manager.dialog_data.get("selected_crypto", "")
    
    crypto_data = await get_crypto_price(selected)
    
    # Форматируем цену с двумя знаками после запятой
    price = crypto_data.get("current_price", "данные отсутствуют")
    try:
        price_float = float(price)
        price_formatted = f"{price_float:.2f}"
    except (ValueError, TypeError):
        price_formatted = price
        
    # Форматируем изменение с двумя знаками после запятой
    change = crypto_data.get("usd_24h_change", "данные отсутствуют")
    try:
        change_float = float(change)
        change_formatted = f"{change_float:.2f}"
        change_emoji = "🔴" if change_float < 0 else "🟢"
    except (ValueError, TypeError):
        change_formatted = change
        change_emoji = ""
    
    # Форматируем дату последнего обновления
    last_updated = crypto_data.get("last_updated", "данные отсутствуют")
    try:
        if "T" in last_updated:
            # Преобразуем ISO формат в более читаемый
            dt = datetime.fromisoformat(last_updated)
            last_updated_formatted = dt.strftime("%d.%m.%Y %H:%M:%S")
        else:
            last_updated_formatted = last_updated
    except (ValueError, TypeError):
        last_updated_formatted = last_updated
    
    return {
        "name": selected,
        "price": price_formatted,
        "change_24h": change_formatted,
        "change_emoji": change_emoji,
        "last_updated": last_updated_formatted
    }

async def on_crypto_selected(callback: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    """Обработчик выбора криптовалюты"""
    manager.dialog_data["selected_crypto"] = item_id
    await manager.switch_to(MarketDataStates.detail)

def crypto_price_formatter(price, change):
    """Форматирует вывод цены и изменения"""
    if not price or not change:
        return "данные недоступны"
    
    change_float = float(change)
    emoji = "🔴" if change_float < 0 else "🟢"
    
    return f"${price} ({emoji} {change}%)"

dialog = Dialog(
    Window(
        Const("🪙 Курсы криптовалют"),
        Const("Выберите криптовалюту из списка:"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="crypto_select",
                item_id_getter=lambda x: x[0],
                items="crypto_items",
                on_click=on_crypto_selected
            ),
            id="sg_portfolio_assets",
            width=1,
            height=5,
            hide_on_single_page=True
        ),
        
        Cancel(Const("⬅️ Назад")),
        state=MarketDataStates.main,
        getter=get_crypto_data
    ),
    Window(
        Format("🪙 Информация о {name}"),
        Format("💰 Текущая цена: ${price}"),
        Format("📈 Изменение за 24ч: {change_emoji} {change_24h}%"),
        Format("🕒 Последнее обновление: {last_updated}"),
        Back(Const("⬅️ Назад к списку")),
        Cancel(Const("❌ Закрыть")),
        state=MarketDataStates.detail,
        getter=get_crypto_detail
    )
)

# Регистрируем диалог в роутере
router.include_router(dialog)