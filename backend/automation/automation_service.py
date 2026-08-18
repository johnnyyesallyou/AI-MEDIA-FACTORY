"""Automation Service - Sprint 35.

Background daemon для автоматического запуска jobs.

Usage:
    python -m backend.automation.automation_service start
    python -m backend.automation.automation_service stop
"""
import sys
import time
import signal
import logging
import argparse

from core.channel_manager import ChannelManager
from core.monitoring import setup_structured_logging


logger = logging.getLogger(__name__)


class AutomationService:
    """Background daemon для automation."""
    
    def __init__(self):
        self.manager = ChannelManager()
        self.running = False
    
    def start(self):
        """Запускает daemon."""
        setup_structured_logging(level="INFO")
        
        logger.info("Automation Service starting...")
        
        # Загружаем все connected channels
        from core.database import SessionLocal
        from core.models.channel_orm import ChannelORM
        
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).filter(ChannelORM.is_connected == True).all()
            for ch in channels:
                self.manager.enable_automation(ch.id, interval_minutes=30)
                logger.info(f"Enabled automation for {ch.name}")
        finally:
            db.close()
        
        # Запускаем scheduler
        self.manager.start_scheduler()
        logger.info("Automation Service started")
        
        self.running = True
        
        # Main loop
        while self.running:
            time.sleep(1)
    
    def stop(self):
        """Останавливает daemon."""
        logger.info("Automation Service stopping...")
        self.running = False
        self.manager.stop_scheduler()
        logger.info("Automation Service stopped")


def main():
    parser = argparse.ArgumentParser(description="Automation Service")
    parser.add_argument("command", choices=["start", "stop"], help="Command")
    args = parser.parse_args()
    
    service = AutomationService()
    
    # Signal handlers
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, stopping...")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.command == "start":
        service.start()
    elif args.command == "stop":
        # TODO: send SIGTERM to running daemon
        print("Stop not implemented yet (use Ctrl+C)")


if __name__ == "__main__":
    main()