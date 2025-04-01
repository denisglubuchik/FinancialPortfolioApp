from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from bot.services.portfolios import get_portfolio


class PortfolioMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Any:
        portfolio = await get_portfolio(event.from_user.id)
        data["backend_portfolio"] = portfolio
        return await handler(event, data)