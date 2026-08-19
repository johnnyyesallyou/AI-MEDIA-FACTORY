from .automation_models import AutomationSettings
from .automation_policies import DEFAULT_SETTINGS, validate_settings
from .manager import automation_manager


class AutomationService:

    def __init__(self):
        self.settings = DEFAULT_SETTINGS
        self.manager = automation_manager


    def get_settings(self) -> AutomationSettings:
        return self.settings


    def update_settings(self, settings: AutomationSettings):
        self.settings = validate_settings(settings)
        return self.settings


    def start(self):
        self.settings.enabled = True
        return {
            "status": "started",
            "enabled": True
        }


    def stop(self):
        self.settings.enabled = False
        return {
            "status": "stopped",
            "enabled": False
        }


    async def run_now(self):

        return await self.manager.run_all_channels()



automation_service = AutomationService()