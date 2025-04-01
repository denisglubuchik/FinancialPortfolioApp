from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from bot.services.users import get_user_by_tg


class UsersMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Any:
        backend_portfolio_id = data.get("backend_portfolio_id")
        if not backend_portfolio_id:
            user = await get_user_by_tg(event.from_user.id)
            data["backend_user_id"] = user["id"]
        return await handler(event, data)
