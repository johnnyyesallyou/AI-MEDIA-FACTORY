import pathlib

p = pathlib.Path('./engines/writing/models.py')
s = p.read_text(encoding='utf-8')

if 'class ContentDraft' not in s:
    content_draft = '''

class ContentDraft(BaseModel):
    """
    Строгий контракт ответа WritingEngine.
    Возвращается из engine.generate() вместо dict.
    
    Подготовка к WritingEngine v2: единый интерфейс Draft для всех Publisher.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    brief_id: str
    title: str = ""
    body: str
    hashtags: List[str] = Field(default_factory=list)
    estimated_read_time: int = 45
    quality_score: int = 0
    model_used: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    platform: str = "telegram"
'''
    s = s + content_draft
    p.write_text(s, encoding='utf-8')
    print('OK: ContentDraft добавлен в models.py')
else:
    print('INFO: ContentDraft уже есть')