import pathlib

p = pathlib.Path('./core/models/content_orm.py')
s = p.read_text(encoding='utf-8')

# Добавляем импорт JSON и Boolean (если нет)
if 'from sqlalchemy import' in s and 'JSON' not in s:
    s = s.replace(
        'from sqlalchemy import Column, String, Integer, DateTime, Text',
        'from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean'
    )
    print('OK: добавил JSON, Boolean в import')

# Добавляем 3 поля перед created_at
fields = '''
    # === WritingEngine v2 fields ===
    validation_issues = Column(
        JSON,
        nullable=True,
        default=list
    )

    fact_check_passed = Column(
        Boolean,
        nullable=True,
        default=True
    )

    model_used = Column(
        String(100),
        nullable=True,
        default=""
    )

'''

if 'validation_issues' not in s and 'created_at = Column' in s:
    s = s.replace(
        '    created_at = Column(',
        fields + '    created_at = Column('
    )
    p.write_text(s, encoding='utf-8')
    print('OK: добавил validation_issues, fact_check_passed, model_used в ContentORM')
elif 'validation_issues' in s:
    print('INFO: поля уже есть в ORM')
else:
    print('WARN: не удалось найти точку вставки')