import pathlib

p = pathlib.Path("/app/engines/analytics_engine.py")
c = p.read_text(encoding="utf-8")

# Добавляем expunge перед commit чтобы объект был usable после db.close()
old = '''            db.add(metric)
            db.commit()
            self.logger.info(f"Recorded metric for {content_id}: views={views}")
            return metric'''

new = '''            db.add(metric)
            db.commit()
            db.refresh(metric)
            db.expunge(metric)  # detach от сессии, но с загруженными атрибутами
            self.logger.info(f"Recorded metric for {content_id}: views={views}")
            return metric'''

if old in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ Added db.expunge(metric) to prevent DetachedInstanceError")
else:
    print("❌ Marker not found")