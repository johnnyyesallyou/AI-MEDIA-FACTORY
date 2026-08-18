class TelegramEngineError(Exception):
    """Base Telegram engine error."""
    pass


class TelegramPublishError(TelegramEngineError):
    """Telegram message publishing failed."""
    pass