from bot.core.loader import market_redis as redis
from bot.services.portfolios import get_assets

async def get_crypto_price(crypto_asset: str) -> dict:
    """
    Получение цены криптовалюты из Redis

    Args:
        crypto_asset: Идентификатор криптовалюты (например, bitcoin, ethereum)

    Returns:
        dict: Словарь с данными о криптовалюте (цена, изменение за 24 часа, время обновления)
    """
    key = f"market_data:{crypto_asset}"
    crypto_info = await redis.hgetall(key)
    
    if not crypto_info:
        return {"error": f"Данные для {crypto_asset} не найдены"}
    
    return {k.decode(): v.decode() for k, v in crypto_info.items()}


async def get_multiple_crypto_prices(crypto_assets: list[str]) -> dict:
    """
    Получение цен нескольких криптовалют из Redis

    Args:
        crypto_assets: Список идентификаторов криптовалют

    Returns:
        dict: Словарь с данными о криптовалютах
    """
    result = {}
    
    for asset in crypto_assets:
        result[asset] = await get_crypto_price(asset)
    
    return result


async def get_popular_cryptocurrencies() -> list[str]:
    """
    Получение списка популярных криптовалют 
    
    Returns:
        list: Список идентификаторов популярных криптовалют
    """
    assets = await get_assets()
    # В реальном приложении можно получать этот список из Redis или конфига
    return [asset["name"] for asset in assets]