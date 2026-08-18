import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from core.models.content_orm import ContentORM


class ContentRepository:
    def __init__(self, db: Session):
        self.db = db


    def create(self, **fields) -> ContentORM:
        item = ContentORM(
            id=str(uuid.uuid4()),
            **fields
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item


    def get(self, content_id: str) -> Optional[ContentORM]:
        return (
            self.db
            .query(ContentORM)
            .filter(ContentORM.id == content_id)
            .first()
        )


    def list_all(
        self,
        status: Optional[str] = None,
        channel_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ContentORM]:

        query = self.db.query(ContentORM)

        if status:
            query = query.filter(ContentORM.status == status)

        if channel_id:
            query = query.filter(ContentORM.channel_id == channel_id)

        return (
            query
            .order_by(ContentORM.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


    def count(
        self,
        status: Optional[str] = None,
        channel_id: Optional[str] = None
    ) -> int:

        query = self.db.query(ContentORM)

        if status:
            query = query.filter(ContentORM.status == status)

        if channel_id:
            query = query.filter(ContentORM.channel_id == channel_id)

        return query.count()


    def exists(
        self,
        channel_id: Optional[str] = None,
        source_url: Optional[str] = None,
        headline: Optional[str] = None,
    ) -> bool:

        query = self.db.query(ContentORM)

        if channel_id is not None:
            query = query.filter(ContentORM.channel_id == channel_id)

        if source_url:
            query = query.filter(ContentORM.source_url == source_url)

        if headline:
            query = query.filter(ContentORM.headline == headline)

        return query.first() is not None


    def update_status(
        self,
        content_id: str,
        status: str
    ) -> Optional[ContentORM]:

        item = self.get(content_id)

        if not item:
            return None

        item.status = status
        item.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(item)

        return item


    def update_publish_result(
        self,
        content_id: str,
        message_id: str
    ) -> Optional[ContentORM]:

        item = self.get(content_id)

        if not item:
            return None

        item.status = "published"
        item.telegram_message_id = str(message_id)
        item.published_at = datetime.utcnow()
        item.publish_error = None
        item.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(item)

        return item


    def update_publish_error(
        self,
        content_id: str,
        error: str
    ) -> Optional[ContentORM]:

        item = self.get(content_id)

        if not item:
            return None

        item.status = "failed"
        item.publish_error = error
        item.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(item)

        return item
