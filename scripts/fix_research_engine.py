import pathlib

engine_file = pathlib.Path('./engines/research/engine.py')
s = engine_file.read_text(encoding='utf-8')
changes = []

# 1. Фиксим сигнатуру run() — добавляем параметр channel
if 'def run(self) -> dict:' in s:
    s = s.replace('def run(self) -> dict:', 'def run(self, channel=None) -> dict:', 1)
    changes.append("добавлен параметр channel в run()")

# 2. Фиксим initialize() — принимает channel и использует channel.sources
if 'def initialize(self):' in s:
    s = s.replace('def initialize(self):', 'def initialize(self, channel=None):', 1)
    changes.append("добавлен параметр channel в initialize()")

# 3. Заменяем блок initialize — вместо RSS_SOURCES используем channel.sources
old_init_block = '''        logger.info(f"Инициализация Research Engine с {len(RSS_SOURCES)} источниками")
        for source_config in RSS_SOURCES:
            self.sources.append(RSSSource(source_config))
        self._initialized = True'''

new_init_block = '''        # Sprint 8.4.1 fix: используем channel.sources если передан
        if channel and getattr(channel, "sources", None):
            sources_to_use = channel.sources
            logger.info(f"Инициализация Research Engine с {len(sources_to_use)} источниками из канала")
        else:
            # Fallback на hardcoded RSS_SOURCES для обратной совместимости
            sources_to_use = RSS_SOURCES
            logger.info(f"Инициализация Research Engine с {len(sources_to_use)} hardcoded источниками (fallback)")
        
        for source_config in sources_to_use:
            try:
                self.sources.append(RSSSource(source_config))
            except Exception as e:
                logger.warning(f"Failed to init source {source_config.get('name', 'unknown')}: {e}")
        self._initialized = True'''

if old_init_block in s:
    s = s.replace(old_init_block, new_init_block, 1)
    changes.append("initialize() теперь использует channel.sources вместо RSS_SOURCES")
else:
    print("⚠️ Не найден точный блок initialize — показываю текущее состояние")
    lines = s.split('\n')
    for i, line in enumerate(lines[20:40], start=21):
        print(f"   {i}: {line}")

# 4. Фиксим run() — передаём channel в initialize
if '            self.initialize()' in s:
    s = s.replace('            self.initialize()', '            self.initialize(channel=channel)', 1)
    changes.append("run() передаёт channel в initialize()")
elif '        if not self._initialized:\n            self.initialize()' in s:
    s = s.replace(
        '        if not self._initialized:\n            self.initialize()',
        '        if not self._initialized:\n            self.initialize(channel=channel)',
        1
    )
    changes.append("run() передаёт channel в initialize() (альтернативный паттерн)")

if changes:
    engine_file.write_text(s, encoding='utf-8')
    print(f"✅ Применено {len(changes)} фиксов:")
    for c in changes:
        print(f"   - {c}")
else:
    print("⚠️ Изменения не применены")