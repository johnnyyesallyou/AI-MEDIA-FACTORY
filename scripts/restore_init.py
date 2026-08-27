import pathlib

p = pathlib.Path("/app/engines/telegraph/publisher.py")
c = p.read_text(encoding="utf-8")

# Сломанный __init__ (без access_token)
broken_init = '''    def __init__(self, access_token: Optional[str] = None):
        """
        Инициализация TelegraphPublisher.

        Args:
            access_token: Telegraph API access token (из .env или createAccount)
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    def upload_images_to_telegraph'''

# Правильный __init__ с access_token
correct_init = '''    def __init__(self, access_token: Optional[str] = None):
        """
        Инициализация TelegraphPublisher.

        Args:
            access_token: Telegraph API access token (из .env или createAccount)
        """
        self.access_token = access_token
        if not self.access_token:
            self.access_token = os.getenv("TELEGRAPH_ACCESS_TOKEN")
        self.logger = logging.getLogger(self.__class__.__name__)

    def upload_images_to_telegraph'''

if broken_init in c:
    c = c.replace(broken_init, correct_init, 1)
    p.write_text(c, encoding="utf-8")
    print("[OK] __init__ восстановлен с self.access_token")
else:
    print("[!] Сломанный __init__ не найден")
    # Пробуем найти что есть
    if "self.access_token = access_token" in c:
        print("[i] access_token уже установлен")
    else:
        print("[!] access_token нигде не устанавливается!")