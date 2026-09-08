"""Platform renderers for Publication contract. Sprint 72.3."""
from .telegram_renderer import TelegramRenderer, TelegramRenderResult
from .vk_renderer import VKRenderer, VKRenderResult

__all__ = [
    "TelegramRenderer",
    "TelegramRenderResult",
    "VKRenderer",
    "VKRenderResult",
]