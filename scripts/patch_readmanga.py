import pathlib

p = pathlib.Path("/app/engines/source_adapters/readmanga_adapter.py")
c = p.read_text(encoding="utf-8")

# Добавляем метод get_title_info после fetch_latest_chapters
method = '''

    def get_title_info(self, slug: str) -> Optional[dict]:
        """
        Загружает информацию о тайтле из ReadManga.
        
        Args:
            slug: ReadManga slug (числовой ID или транслит)
        
        Returns:
            dict с title, description, genres, cover_url
        """
        try:
            url = f"{self.BASE_URL}/{slug}"
            r = requests.get(url, headers=self.HEADERS, timeout=self.timeout)
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Извлекаем title (обычно в h1 или .title)
            title_elem = soup.find("h1") or soup.find(class_=lambda c: c and "title" in " ".join(c).lower())
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Извлекаем description (обычно в .description или .summary)
            desc_elem = soup.find(class_=lambda c: c and any(kw in " ".join(c).lower() for kw in ["description", "summary", "about"]))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Извлекаем genres (обычно в .genres или .tags)
            genres_elem = soup.find_all(class_=lambda c: c and any(kw in " ".join(c).lower() for kw in ["genre", "tag", "category"]))
            genres = [g.get_text(strip=True) for g in genres_elem if g.get_text(strip=True)]
            
            # Извлекаем cover (обычно img с классом cover или в .cover-image)
            cover_elem = soup.find("img", class_=lambda c: c and "cover" in " ".join(c).lower())
            if not cover_elem:
                cover_elem = soup.find(class_=lambda c: c and "cover" in " ".join(c).lower())
                if cover_elem:
                    cover_elem = cover_elem.find("img")
            
            cover_url = None
            if cover_elem:
                cover_url = cover_elem.get("data-src") or cover_elem.get("src")
            
            return {
                "title": title,
                "description": description,
                "genres": genres,
                "cover_url": cover_url,
            }
        except Exception as e:
            self.logger.warning(f"ReadManga get_title_info failed for {slug}: {e}")
            return None
'''

# Вставляем метод перед последним class или в конец файла
if "def get_title_info" not in c:
    # Находим последнюю строку класса
    lines = c.split('\n')
    insert_pos = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() and not lines[i].startswith(' '):
            insert_pos = i
            break
    
    lines.insert(insert_pos, method)
    c = '\n'.join(lines)
    p.write_text(c, encoding="utf-8")
    print("✅ ReadMangaAdapter.get_title_info() added")
else:
    print("ℹ️ Method already exists")