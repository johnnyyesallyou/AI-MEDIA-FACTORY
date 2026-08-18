import pathlib

p = pathlib.Path("/app/backend/automation/jobs/manga_publish_job.py")
c = p.read_text(encoding="utf-8")

# Добавляем лог после query
old_query_block = """            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.asset_id != None,
                (ContentORM.source_url.like("%remanga.org%") | ContentORM.source_url.like("%mangadex.org%"))
            ).limit(limit * 2).all()

            if not items:
                return {"status": "ok", "published": 0, "message": "No items"}"""

new_query_block = """            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.asset_id != None,
                (ContentORM.source_url.like("%remanga.org%") | ContentORM.source_url.like("%mangadex.org%"))
            ).limit(limit * 2).all()

            self.logger.info(f"Query returned {len(items)} items")
            
            if not items:
                self.logger.warning("No items matching filter (status=research, asset_id!=None, source contains remanga/mangadex)")
                return {"status": "ok", "published": 0, "message": "No items"}"""

if old_query_block in c:
    c = c.replace(old_query_block, new_query_block)
    print("✅ Added query logging")
else:
    print("❌ Block not found")

p.write_text(c, encoding="utf-8")
import ast
ast.parse(c)
print("✅ Syntax OK")