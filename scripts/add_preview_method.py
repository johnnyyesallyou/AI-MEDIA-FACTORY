import pathlib

p = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
content = p.read_text(encoding="utf-8")

new_method = '''

    def fetch_first_chapter_preview(self, slug: str, limit: int = 5) -> Optional[List[str]]:
        """
        Sprint 18: ???????? ?????? N ??????? ?????? ????? ??? ??????.
        
        Returns:
            List of page URLs (? Referer ??? ???????) ??? None ???? ?? ???????
        """
        try:
            # 1. ???????? first_chapter ID ?? title info
            title_info = self.get_title_info(slug)
            if not title_info:
                return None
            
            # ???????? ?????? ?????????? ? ??????
            response = requests.get(
                f"https://remanga.org/api/titles/{slug}/",
                headers=self.HEADERS,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            content = response.json().get("content", {})
            first_chapter = content.get("first_chapter")
            
            if not first_chapter:
                self.logger.warning(f"No first_chapter for {slug}")
                return None
            
            chapter_id = first_chapter.get("id") if isinstance(first_chapter, dict) else first_chapter
            
            # 2. ???????? ???????? ?????? ?????
            ch_response = requests.get(
                f"https://remanga.org/api/titles/chapters/{chapter_id}/",
                headers=self.HEADERS,
                timeout=self.timeout
            )
            ch_response.raise_for_status()
            
            ch_data = ch_response.json().get("content", {})
            pages = ch_data.get("pages", [])
            
            # 3. ????????? URL ?????? N ???????
            page_urls = []
            for page_item in pages[:limit]:
                if isinstance(page_item, list) and page_item:
                    page_obj = page_item[0]
                    if isinstance(page_obj, dict):
                        url = page_obj.get("link")
                        if url:
                            page_urls.append(url)
                elif isinstance(page_item, dict):
                    url = page_item.get("link")
                    if url:
                        page_urls.append(url)
            
            self.logger.info(f"Fetched {len(page_urls)} preview pages for {slug}")
            return page_urls
        
        except Exception as e:
            self.logger.error(f"Failed to fetch preview for {slug}: {e}")
            return None
'''

# ??????? ????????? ?????? ????? ????? ????????????? (???? def test_connection)
marker = "    def test_connection"
if marker in content:
    content = content.replace(marker, new_method + "\n" + marker)
    p.write_text(content, encoding="utf-8")
    print("? fetch_first_chapter_preview added to ReMangaAdapter")
else:
    print("? Marker not found")
