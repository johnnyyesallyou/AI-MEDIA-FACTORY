import sys
sys.path.insert(0, '/app')
import requests
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()
try:
    content = db.query(ContentORM).filter(
        ContentORM.image_url.isnot(None),
        ContentORM.image_url != ''
    ).first()
    
    print(f'URL: {content.image_url}')
    
    # Тестируем скачивание напрямую
    print('\\nПытаемся скачать...')
    response = requests.get(content.image_url, timeout=120, stream=True)
    
    print(f'Status: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    print(f'Content-Length header: {response.headers.get("content-length", "N/A")}')
    print(f'Content-Type: {response.headers.get("content-type", "N/A")}')
    
    # Читаем содержимое
    content_bytes = response.content
    print(f'\\nРазмер данных: {len(content_bytes)} bytes')
    
    if len(content_bytes) > 0:
        print(f'Первые 100 bytes: {content_bytes[:100]}')
    else:
        print('❌ Получили пустой ответ!')
finally:
    db.close()