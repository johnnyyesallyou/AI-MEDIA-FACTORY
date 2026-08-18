import pathlib

p = pathlib.Path('./engines/writing/prompt_builder.py')
s = p.read_text(encoding='utf-8')

# Патч 1: передаём brief во все _build_* методы
# build() — передаём brief как параметр
old_build_calls = '''    def build(self, brief: ContentBrief) -> str:
        """Собирает финальный промпт для LLM."""
        parts = [
            self._build_system(),
            self._build_style(),
            self._build_platform_rules(),
            self._build_topic(brief),
            self._build_facts(brief),
            self._build_goal(brief),
            self._build_format_rules(),
            self._build_final_instruction()
        ]
        return "\\n\\n".join(parts)'''

new_build_calls = '''    def build(self, brief: ContentBrief) -> str:
        """Собирает финальный промпт для LLM."""
        parts = [
            self._build_system(),
            self._build_style(),
            self._build_platform_rules(),
            self._build_topic(brief),
            self._build_facts(brief),
            self._build_goal(brief),
            self._build_format_rules(brief),
            self._build_final_instruction()
        ]
        return "\\n\\n".join(parts)'''

if old_build_calls in s:
    s = s.replace(old_build_calls, new_build_calls)
    print('OK: build() теперь передаёт brief в _build_format_rules')
else:
    print('WARN: build() pattern not found')

# Патч 2: меняем сигнатуру _build_format_rules
old_format_sig = '''    def _build_format_rules(self) -> str:
        """Запреты и ограничения."""
        forbidden = getattr(brief, 'forbidden_words', []) or []'''

new_format_sig = '''    def _build_format_rules(self, brief: ContentBrief) -> str:
        """Запреты и ограничения."""
        forbidden = getattr(brief, 'forbidden_words', []) or []'''

if old_format_sig in s:
    s = s.replace(old_format_sig, new_format_sig)
    print('OK: _build_format_rules принимает brief как параметр')
else:
    print('ERROR: _build_format_rules pattern not found')

p.write_text(s, encoding='utf-8')