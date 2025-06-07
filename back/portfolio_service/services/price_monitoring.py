import logging
import asyncio
from typing import Dict, List, Optional, Set
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from back.portfolio_service.database import async_session_maker
from back.portfolio_service.models.portfolio_assets import PortfolioAssets
from back.portfolio_service.models.assets import Assets
from back.portfolio_service.repositories.portfolio_assets import PortfolioAssetsRepository
from back.portfolio_service.message_broker.rabbitmq import rabbit_broker
from back.portfolio_service.redis import redis_client

logger = logging.getLogger(__name__)


class PriceMonitoringService:
    """Сервис мониторинга цен с отправкой уведомлений"""
    
    def __init__(self, price_change_threshold: float = 5.0):
        """
        Args:
            price_change_threshold: Порог изменения цены в процентах для создания уведомления
        """
        self.price_change_threshold = price_change_threshold
        self._alert_cooldown_key_prefix = "price_alert_sent:"  # Префикс для cooldown в Redis
        self._alert_cooldown_hours = 6  # Отправлять уведомления максимум раз в 6 часов
        
    async def check_price_changes(self) -> None:
        """Проверяет изменения цен для всех активов в портфелях"""
        try:
            logger.info("🔍 Starting price monitoring check...")
            
            # Получаем все уникальные активы из портфелей
            unique_assets = await self._get_unique_portfolio_assets()
            
            if not unique_assets:
                logger.info("No assets found in portfolios for monitoring")
                return
                
            logger.info(f"Found {len(unique_assets)} unique assets to monitor")
            
            # Проверяем каждый актив
            for asset in unique_assets:
                await self._check_asset_price_change(asset)
                
            logger.info("✅ Price monitoring check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in price monitoring: {e}")
            
    async def _get_unique_portfolio_assets(self) -> List[Assets]:
        """Получает все уникальные активы из портфелей пользователей"""
        async with async_session_maker() as session:
            # Получаем все активы, которые есть в портфелях пользователей
            query = (
                select(Assets)
                .join(PortfolioAssets, Assets.id == PortfolioAssets.asset_id)
                .filter(PortfolioAssets.quantity > 0)  # Только активы с положительным количеством
                .distinct()
            )
            result = await session.execute(query)
            return result.scalars().all()
            
    async def _check_asset_price_change(self, asset: Assets) -> None:
        """Проверяет изменение цены конкретного актива"""
        try:
            # Получаем данные о цене из Redis (market_data service хранит по name: bitcoin, ethereum, solana)
            market_data = await self._get_market_data_from_redis(asset.name)
                
            if not market_data:
                logger.warning(f"No market data found for asset {asset.name} (symbol: {asset.symbol})")
                return
                
            current_price = float(market_data.get("current_price", 0))
            price_change_24h = float(market_data.get("usd_24h_change", 0))
            
            if current_price == 0:
                logger.warning(f"Invalid price data for asset {asset.name}")
                return
                
            logger.debug(f"{asset.name} ({asset.symbol}): price=${current_price:.2f}, 24h change={price_change_24h:+.2f}%")
            
            # Проверяем превышает ли изменение порог
            if abs(price_change_24h) >= self.price_change_threshold:
                # Проверяем не отправляли ли уже уведомления недавно
                if await self._should_send_alert(asset.name):
                    await self._send_price_alerts(asset, current_price, price_change_24h)
                    await self._mark_alert_sent(asset.name)
                else:
                    logger.debug(f"Skipping alert for {asset.name} - already sent within cooldown period")
            
        except Exception as e:
            logger.error(f"Error checking price for {asset.name} ({asset.symbol}): {e}")
            
    async def _send_price_alerts(
        self, 
        asset: Assets, 
        current_price: float, 
        change_percent: float
    ) -> None:
        """Отправляет уведомления пользователям, у которых есть этот актив"""
        try:
            # Получаем всех пользователей, у которых есть этот актив
            users_with_asset = await self._get_users_with_asset(asset.name)
            
            if not users_with_asset:
                return
                
            direction = "📈" if change_percent > 0 else "📉"
            sign = "+" if change_percent > 0 else ""
            
            # Создаем уведомление для каждого пользователя
            for user_id in users_with_asset:
                notification_data = {
                    "user_id": user_id,
                    "asset_name": asset.name,
                    "asset_symbol": asset.symbol,
                    "change_percent": round(change_percent, 2),
                    "current_price": current_price,
                    "direction": direction,
                    "sign": sign
                }
                
                # Отправляем уведомление через RabbitMQ
                await rabbit_broker.publish(
                    notification_data,
                    "price_change_alert"
                )
                
            logger.info(f"📢 Sent price alerts for {asset.symbol} to {len(users_with_asset)} users "
                       f"({change_percent:+.1f}%)")
                       
        except Exception as e:
            logger.error(f"Error sending price alerts for {asset.symbol}: {e}")
            
    async def _get_users_with_asset(self, asset_name: str) -> List[int]:
        """Получает список пользователей, у которых есть определенный актив"""
        async with async_session_maker() as session:
            repository = PortfolioAssetsRepository(session)
            # Используем готовый метод который делает правильный JOIN
            user_ids = await repository.get_users_with_asset(asset_name)
            return user_ids
            
    async def _get_market_data_from_redis(self, asset_symbol: str) -> Optional[Dict[str, str]]:
        """Получает market data для актива из Redis (сохраненные market_data_service)"""
        try:
            # Используем готовый метод get_asset из Redis клиента
            market_data = await redis_client.get_asset(asset_symbol)
            
            if not market_data:
                return None
                
            return market_data
                
        except Exception as e:
            logger.error(f"Error getting market data for {asset_symbol} from Redis: {e}")
            return None
            
    async def _should_send_alert(self, asset_name: str) -> bool:
        """Проверяет можно ли отправить уведомление (не отправляли ли недавно)"""
        try:
            cooldown_key = f"{self._alert_cooldown_key_prefix}{asset_name}"
            
            # Проверяем есть ли ключ в Redis напрямую
            if hasattr(redis_client, 'redis') and redis_client.redis:
                last_sent = await redis_client.redis.get(cooldown_key)
                return last_sent is None  # Если ключа нет - можно отправлять
            else:
                logger.warning("Redis client not properly initialized for cooldown check")
                return True
            
        except Exception as e:
            logger.error(f"Error checking alert cooldown for {asset_name}: {e}")
            return True  # В случае ошибки разрешаем отправку
            
    async def _mark_alert_sent(self, asset_name: str) -> None:
        """Отмечает что уведомление было отправлено (устанавливает cooldown)"""
        try:
            cooldown_key = f"{self._alert_cooldown_key_prefix}{asset_name}"
            # Сохраняем отметку на время cooldown (в секундах)
            cooldown_seconds = self._alert_cooldown_hours * 60 * 60
            
            # Используем напрямую redis клиент для setex
            if hasattr(redis_client, 'redis') and redis_client.redis:
                await redis_client.redis.setex(cooldown_key, cooldown_seconds, "sent")
                logger.debug(f"Set cooldown for {asset_name} for {self._alert_cooldown_hours} hour(s)")
            else:
                logger.warning(f"Redis client not properly initialized for cooldown marking")
                
        except Exception as e:
            logger.error(f"Error marking alert sent for {asset_name}: {e}")