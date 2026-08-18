from datetime import datetime


def normalize_publish_time(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "09:00"
    if len(value) == 5 and value[2] == ":":
        return value
    return "09:00"


def get_publish_slots(times: list[str]) -> list[str]:
    return [normalize_publish_time(item) for item in times if item]


def should_run_now(now: datetime | None = None) -> bool:
    now = now or datetime.utcnow()
    return now.minute % 60 == 0
