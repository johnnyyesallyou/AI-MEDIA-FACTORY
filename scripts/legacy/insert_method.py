import pathlib

p = pathlib.Path("/app/engines/source_adapters/remanga_adapter.py")
content = p.read_text(encoding="utf-8")

# ????????? ???? ?? ??? ?????
if "fetch_first_chapter_preview" in content:
    print("Method already exists, skipping")
    exit(0)

new_method = '''
    def fetch_first_chapter_preview(self, slug: str, limit: int = 5) -> Optional[List[str]]:
        """
        Sprint 18: ???????? ?????? N ??????? ?????? ????? ??? ??????.

        Args:
            slug: slug ?????? (???????? 'descendants-of-the-hero')
            limit: ?????????? ??????? (?? ????????? 5)

        Returns:
            List of page URLs (? Referer ??? ???????) ??? None ???? ?? ???????
        """
        try:
            # 1. ???????? first_chapter ID ?? title info
            response = requests.get(
                f"https://remanga.org/api/titles/{slug}/",
                headers=self.HEADERS,
                timeout=self.timeout
            )
            response.raise_for_status()

            title_content = response.json().get("content", {})
            first_chapter = title_content.get("first_chapter")

            if not first_chapter:
                self.logger.warning(f"No first_chapter for {slug}")
                return None

            chapter_id = first_chapter.get("id") if isinstance(first_chapter, dict) else first_chapter
            self.logger.info(f"First chapter ID for {slug}: {chapter_id}")

            # 2. ???????? ???????? ?????? ?????
            ch_response = requests.get(
                f"https://remanga.org/api/titles/chapters/{chapter_id}/",
                headers=self.HEADERS,
                timeout=self.timeout
            )
            ch_response.raise_for_status()

            ch_data = ch_response.json().get("content", {})
            pages = ch_data.get("pages", [])

            # 3. ????????? URL ?????? N ??????? (pages - ?????? ??????? [[{...}], [{...}]])
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

# ??????? ????? ReMangaAdapter ? ????????? ????? ????? ????????? ????????
# ?????????: ???? ????????? "    def " ? ????????? ????? ???
lines = content.splitlines(keepends=True)

last_method_idx = None
for i, line in enumerate(lines):
    if line.startswith("    def "):
        last_method_idx = i

if last_method_idx is None:
    print("ERROR: no methods found in class")
    exit(1)

print(f"Last method at line {last_method_idx}: {lines[last_method_idx].strip()[:60]}")

# ????????? ????? ????? ????? ?????????
lines.insert(last_method_idx, new_method)

# ??????????
new_content = "".join(lines)
p.write_text(new_content, encoding="utf-8")

# ?????????
check_content = p.read_text(encoding="utf-8")
if "fetch_first_chapter_preview" in check_content:
    print("? Method successfully inserted")
    
    # ????????? ?????????
    import ast
    try:
        ast.parse(check_content)
        print("? Syntax OK")
    except SyntaxError as e:
        print(f"? Syntax error: {e}")
else:
    print("? Method not found after insertion")
