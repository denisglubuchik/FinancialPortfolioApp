from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from back.portfolio_service.services.price_monitoring import PriceMonitoringService

logger = logging.getLogger(__name__)


class PriceMonitoringScheduler:
    """APScheduler для мониторинга цен каждые 15 минут"""
    
    def __init__(
        self, 
        price_change_threshold: float = 5.0,
        check_interval_minutes: int = 15
    ):
        """
        Args:
            price_change_threshold: Порог изменения цены в процентах для уведомления
            check_interval_minutes: Интервал проверки в минутах (по умолчанию 15)
        """
        self.scheduler = AsyncIOScheduler()
        self.price_monitoring_service = PriceMonitoringService(price_change_threshold)
        self.check_interval_minutes = check_interval_minutes
        self.is_running = False
        
        # Настраиваем слушатели событий
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED)
        
    async def start(self) -> bool:
        """Запускает планировщик"""
        try:
            if self.is_running:
                logger.warning("Price monitoring scheduler is already running")
                return True
                
            # Добавляем задачу мониторинга цен
            self.scheduler.add_job(
                self.price_monitoring_service.check_price_changes,
                trigger=IntervalTrigger(minutes=self.check_interval_minutes),
                id='price_monitoring_job',
                name='Price Monitoring Job',
                max_instances=1,  # Только одна задача одновременно
                coalesce=True,    # Объединяем пропущенные запуски
                misfire_grace_time=300,  # Допустимая задержка в секундах
                next_run_time=datetime.now() + timedelta(seconds=10)
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"✅ Price monitoring scheduler started successfully")
            logger.info(f"⏰ Price monitoring will run every {self.check_interval_minutes} minutes")
            logger.info(f"📊 Price change threshold: {self.price_monitoring_service.price_change_threshold}%")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start price monitoring scheduler: {e}")
            return False
            
    async def stop(self) -> bool:
        """Останавливает планировщик"""
        try:
            if not self.is_running:
                logger.info("Price monitoring scheduler is not running")
                return True
                
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            
            logger.info("✅ Price monitoring scheduler stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping price monitoring scheduler: {e}")
            return False
            
    def _job_error_listener(self, event):
        """Обработчик ошибок заданий"""
        logger.error(f"❌ Price monitoring job failed: {event.exception}")
        
    def _job_executed_listener(self, event):
        """Обработчик успешного выполнения заданий"""
        logger.debug(f"✅ Price monitoring job executed successfully")
        
    async def trigger_manual_check(self) -> None:
        """Ручной запуск проверки цен"""
        try:
            logger.info("🔧 Manual price monitoring check triggered")
            await self.price_monitoring_service.check_price_changes()
            
        except Exception as e:
            logger.error(f"❌ Manual price check failed: {e}")
            
    def get_status(self) -> dict:
        """Возвращает статус планировщика"""
        return {
            "is_running": self.is_running,
            "interval_minutes": self.check_interval_minutes,
            "price_threshold": self.price_monitoring_service.price_change_threshold,
            "jobs_count": len(self.scheduler.get_jobs()) if self.is_running else 0
        } 