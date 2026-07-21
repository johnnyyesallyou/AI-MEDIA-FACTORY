# AI-MEDIA-FACTORY

Платформа для автоматизированного создания и управления медиа-контентом с использованием искусственного интеллекта.

## 🚀 Быстрый старт

\\\ash
# Установка зависимостей
pip install -r requirements.txt

# Запуск через Docker
docker-compose up -d

# Запуск backend
cd backend
uvicorn app.main:app --reload
\\\

##  Технологический стек

- **Backend**: FastAPI, Python 3.10
- **Базы данных**: PostgreSQL 16, Redis 7, Qdrant (векторная БД)
- **Хранилище**: MinIO (S3-compatible)
- **AI интеграции**: OpenAI, Stable Diffusion, и другие

## ️ Архитектура

- \core/\ - ядро системы, бизнес-логика, DI, оркестратор
- \engines/\ - специализированные движки (research, image, writing, telegram)
- \ackend/\ - API слой на FastAPI
- \infrastructure/docker/\ - Docker конфигурации

## 📝 License

MIT
