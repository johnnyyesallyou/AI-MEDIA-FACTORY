# Task — Sprint 65: Smart Channel Intelligence (Foundation)

## Цель
Создать универсальную архитектуру Wizard для любых тематик.
Не LLM-классификация (это 65.2+), а правильная data model.

## Что делаем в 65.1
- [ ] ChannelIntent dataclass (domain/topic/audience/frequency)
- [ ] ChannelStrategy dataclass (profile_key/sources/formatter/media)
- [ ] CapabilityDefinition (source/formatter/media capabilities)
- [ ] Profile Registry: 5-7 новых профилей
- [ ] CapabilityMatcher (детерминированный подбор)
- [ ] DeterministicTopicClassifier (keywords fallback)
- [ ] E2E: "Новости автомобилей" → ChannelStrategy
- [ ] Commit

## НЕ делаем
- ❌ LLM-классификацию (это 65.2)
- ❌ UI обновления (это 65.6)
- ❌ Integration с PostGenerationService (это 65.5)

## Следующий: Sprint 66 (Hardening)
Параллельно ведём список технического долга:
- pytest: 1 failed, Pydantic V2 warnings, pytest-asyncio warnings
- CI pipeline (GitHub Actions)
- Logging standard
- Error tracking