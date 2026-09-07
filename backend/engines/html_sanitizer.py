"""Sprint 69.20: HTML Sanitizer — очистка текста от неподдерживаемых HTML-тегов для Telegram."""
import re
import html
from typing import Optional


# Telegram HTML parse_mode поддерживает ТОЛЬКО эти теги:
# <b>, <strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>,
# <span class="tg-spoiler">, <tg-spoiler>, <a href="">, <code>, <pre>
ALLOWED_TAGS = {
    "b", "strong", "i", "em", "u", "ins", "s", "strike", "del",
    "span", "tg-spoiler", "a", "code", "pre"
}


def sanitize_for_telegram(text: str, max_length: int = 4000) -> str:
    """
    Очищает текст от HTML-тегов, не поддерживаемых Telegram.
    
    - Удаляет все теги кроме разрешённых
    - Сохраняет содержимое тегов
    - Декодирует HTML entities (&amp; → &)
    - Обрезает до max_length символов
    
    Args:
        text: исходный текст с HTML
        max_length: максимальная длина (Telegram limit = 4096, берём 4000 с запасом)
    
    Returns:
        Очищенный текст
    """
    if not text:
        return ""
    
    # Декодируем HTML entities
    text = html.unescape(text)
    
    # Удаляем все HTML-теги (сохраняя содержимое)
    # Паттерн: <tag>content</tag> → content
    # Также удаляем self-closing теги: <br/>, <img/>
    text = re.sub(r'<[^>]+>', '', text)
    
    # Нормализуем пробелы (убираем множественные)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Обрезаем до max_length
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    # Экранируем символы которые Telegram может интерпретировать как HTML
    # НО только те что реально опасны в HTML контексте
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    
    return text


def sanitize_keep_links(text: str, max_length: int = 4000) -> str:
    """
    Альтернативная версия: сохраняет <a href> ссылки.
    
    - Сохраняет <a href="url">text</a> как есть
    - Удаляет все остальные теги
    """
    if not text:
        return ""
    
    text = html.unescape(text)
    
    # Извлекаем ссылки
    links = {}
    link_pattern = r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>'
    
    def replace_link(match):
        url = match.group(1)
        link_text = match.group(2)
        placeholder = f"__LINK_{len(links)}__"
        links[placeholder] = f'<a href="{url}">{link_text}</a>'
        return placeholder
    
    text = re.sub(link_pattern, replace_link, text, flags=re.IGNORECASE)
    
    # Удаляем остальные теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Восстанавливаем ссылки
    for placeholder, link_html in links.items():
        text = text.replace(placeholder, link_html)
    
    # Нормализуем пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Обрезаем (но аккуратно с ссылками)
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text