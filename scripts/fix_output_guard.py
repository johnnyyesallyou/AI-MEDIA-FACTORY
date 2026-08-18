import pathlib

p = pathlib.Path('./engines/writing/output_guard.py')
s = p.read_text(encoding='utf-8')

# Добавляем min_length параметр и проверку в начало clean()
old_clean = '''    def clean(self, text: str) -> str:

        if not text:
            return ""


        result = text.strip()'''

new_clean = '''    def clean(self, text: str, min_length: int = 50) -> str:
        """
        Очищает результат LLM от служебных элементов.
        
        Если после очистки текст короче min_length символов — возвращает пустую строку,
        чтобы WritingJob пометил пост как needs_revision (вместо сохранения пустого драфта).
        """

        if not text:
            return ""


        result = text.strip()
        
        # Ранняя проверка: если исходник слишком короткий — не тратим время
        if len(result) < min_length:
            logger.warning(f"OutputGuard: text too short before cleaning ({len(result)} < {min_length})")
            return ""'''

if old_clean in s:
    s = s.replace(old_clean, new_clean)
    
    # В конце clean() добавляем финальную проверку длины
    old_return = '''        # Чистим пустые строки
        result = re.sub(
            r"\\n{3,}",
            "\\n\\n",
            result
        )


        return result.strip()'''
    
    new_return = '''        # Чистим пустые строки
        result = re.sub(
            r"\\n{3,}",
            "\\n\\n",
            result
        )

        result = result.strip()
        
        # Финальная проверка: если после очистки слишком короткий — возвращаем пустую строку
        if len(result) < min_length:
            logger.warning(f"OutputGuard: text too short after cleaning ({len(result)} < {min_length})")
            return ""

        return result'''
    
    s = s.replace(old_return, new_return)
    p.write_text(s, encoding='utf-8')
    print('OK: OutputGuard теперь возвращает пустую строку при тексте < 50 символов')
else:
    print('ERROR: паттерн не найден')