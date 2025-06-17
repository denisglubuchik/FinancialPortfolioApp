from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

price_monitoring_router = APIRouter(
    prefix="/price-monitoring",
    tags=["Price Monitoring"]
)


@price_monitoring_router.get("/status")
async def get_monitoring_status() -> Dict[str, Any]:
    """Получить статус мониторинга цен"""
    try:
        from back.portfolio_service.portfolio_main import price_scheduler
        
        if price_scheduler is None:
            return {
                "status": "not_initialized",
                "message": "Price monitoring scheduler is not initialized"
            }
            
        status = price_scheduler.get_status()
        return {
            "status": "active" if status["is_running"] else "stopped",
            "details": status
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get monitoring status")


@price_monitoring_router.post("/manual-check")
async def trigger_manual_check() -> Dict[str, str]:
    """Ручной запуск проверки цен"""
    try:
        from back.portfolio_service.portfolio_main import price_scheduler
        
        if price_scheduler is None:
            raise HTTPException(status_code=503, detail="Price monitoring scheduler is not initialized")
            
        if not price_scheduler.is_running:
            raise HTTPException(status_code=503, detail="Price monitoring scheduler is not running")
            
        await price_scheduler.trigger_manual_check()
        
        return {
            "status": "success",
            "message": "Manual price check triggered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual check: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger manual check")


@price_monitoring_router.post("/start")
async def start_monitoring() -> Dict[str, str]:
    """Запустить мониторинг цен"""
    try:
        from back.portfolio_service.portfolio_main import price_scheduler
        
        if price_scheduler is None:
            raise HTTPException(status_code=503, detail="Price monitoring scheduler is not initialized")
            
        if price_scheduler.is_running:
            return {
                "status": "already_running",
                "message": "Price monitoring is already running"
            }
            
        if await price_scheduler.start():
            return {
                "status": "success", 
                "message": "Price monitoring started successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start price monitoring")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to start monitoring")


@price_monitoring_router.post("/stop")
async def stop_monitoring() -> Dict[str, str]:
    """Остановить мониторинг цен"""
    try:
        from back.portfolio_service.portfolio_main import price_scheduler
        
        if price_scheduler is None:
            raise HTTPException(status_code=503, detail="Price monitoring scheduler is not initialized")
            
        if not price_scheduler.is_running:
            return {
                "status": "already_stopped",
                "message": "Price monitoring is already stopped"
            }
            
        if await price_scheduler.stop():
            return {
                "status": "success",
                "message": "Price monitoring stopped successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to stop price monitoring")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop monitoring") 