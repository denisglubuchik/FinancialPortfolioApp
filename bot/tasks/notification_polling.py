import asyncio
import logging

from bot.services.notifications import process_pending_notifications

logger = logging.getLogger(__name__)


class NotificationPollingTask:
    """Background task manager for notification polling"""
    
    def __init__(self, polling_interval_minutes: int = 15):
        self.polling_interval_minutes = polling_interval_minutes
        self.task = None
        self.is_running = False
    
    async def _polling_loop(self):
        """Main polling loop"""
        logger.info(f"Starting notification polling task (interval: {self.polling_interval_minutes}min)...")
        self.is_running = True
        
        while self.is_running:
            try:
                stats = await process_pending_notifications()
                if stats["fetched"] > 0:
                    logger.info(f"Notification polling stats: {stats}")
                else:
                    logger.debug("No pending notifications found")
            except Exception as e:
                logger.error(f"Error in notification polling task: {e}")
            
            # Wait for next poll cycle
            await asyncio.sleep(self.polling_interval_minutes * 60)
    
    def start(self):
        """Start the background polling task"""
        if self.task is not None:
            logger.warning("Notification polling task is already running")
            return
        
        self.task = asyncio.create_task(self._polling_loop())
        logger.info("Notification polling task started")
    
    async def stop(self):
        """Stop the background polling task"""
        if self.task is None:
            return
        
        logger.info("Stopping notification polling task...")
        self.is_running = False
        self.task.cancel()
        
        try:
            await self.task
        except asyncio.CancelledError:
            logger.info("Notification polling task cancelled successfully")
        finally:
            self.task = None
    
    @property
    def running(self) -> bool:
        """Check if the task is currently running"""
        return self.task is not None and not self.task.done()


notification_polling = NotificationPollingTask() 