from .automation_models import AutomationSettings

DEFAULT_SETTINGS = AutomationSettings()


def validate_settings(settings: AutomationSettings) -> AutomationSettings:
    if settings.research_interval not in {"5m", "15m", "30m", "60m", "120m"}:
        settings.research_interval = "60m"
    if not settings.publish_times:
        settings.publish_times = ["09:00", "13:00", "18:00"]
    return settings
