"""
Repositories для Channel Templates и Profiles.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from core.models.channel_template_orm import ChannelTemplateORM
from core.models.channel_profile_orm import ChannelProfileORM
from core.models.channel_orm import ChannelORM

import uuid
from datetime import datetime


class ChannelProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, platform: Optional[str] = None, is_active: Optional[bool] = None) -> List[ChannelProfileORM]:
        query = self.db.query(ChannelProfileORM)
        if platform is not None:
            query = query.filter(ChannelProfileORM.platform == platform)
        if is_active is not None:
            query = query.filter(ChannelProfileORM.is_active == is_active)
        return query.order_by(ChannelProfileORM.name).all()

    def get_by_id(self, profile_id: str) -> Optional[ChannelProfileORM]:
        return self.db.query(ChannelProfileORM).filter(ChannelProfileORM.id == profile_id).first()

    def get_by_name(self, name: str) -> Optional[ChannelProfileORM]:
        return self.db.query(ChannelProfileORM).filter(ChannelProfileORM.name == name).first()

    def create(self, **kwargs) -> ChannelProfileORM:
        profile = ChannelProfileORM(
            id=str(uuid.uuid4()),
            **kwargs
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile_id: str, **kwargs) -> Optional[ChannelProfileORM]:
        profile = self.get_by_id(profile_id)
        if not profile:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile_id: str) -> bool:
        profile = self.get_by_id(profile_id)
        if not profile:
            return False
        self.db.delete(profile)
        self.db.commit()
        return True


class ChannelTemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, category: Optional[str] = None, is_active: Optional[bool] = None) -> List[ChannelTemplateORM]:
        query = self.db.query(ChannelTemplateORM)
        if category is not None:
            query = query.filter(ChannelTemplateORM.category == category)
        if is_active is not None:
            query = query.filter(ChannelTemplateORM.is_active == is_active)
        return query.order_by(ChannelTemplateORM.name).all()

    def get_by_id(self, template_id: str) -> Optional[ChannelTemplateORM]:
        return self.db.query(ChannelTemplateORM).filter(ChannelTemplateORM.id == template_id).first()

    def get_by_name(self, name: str) -> Optional[ChannelTemplateORM]:
        return self.db.query(ChannelTemplateORM).filter(ChannelTemplateORM.name == name).first()

    def create(self, **kwargs) -> ChannelTemplateORM:
        # Конвертируем Pydantic-модели в dict для JSON полей
        if 'sources' in kwargs and kwargs['sources']:
            kwargs['sources'] = [s.dict() if hasattr(s, 'dict') else s for s in kwargs['sources']]
        if 'retry_policy' in kwargs and kwargs['retry_policy']:
            rp = kwargs['retry_policy']
            kwargs['retry_policy'] = rp.dict() if hasattr(rp, 'dict') else rp
        
        template = ChannelTemplateORM(
            id=str(uuid.uuid4()),
            **kwargs
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template_id: str, **kwargs) -> Optional[ChannelTemplateORM]:
        template = self.get_by_id(template_id)
        if not template:
            return None
        for key, value in kwargs.items():
            if value is not None:
                if key == 'sources' and value:
                    value = [s.dict() if hasattr(s, 'dict') else s for s in value]
                elif key == 'retry_policy' and value:
                    value = value.dict() if hasattr(value, 'dict') else value
                setattr(template, key, value)
        template.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template_id: str) -> bool:
        template = self.get_by_id(template_id)
        if not template:
            return False
        # Проверяем, не используется ли template в каналах
        used = self.db.query(ChannelORM).filter(ChannelORM.template_id == template_id).count()
        if used > 0:
            return False
        self.db.delete(template)
        self.db.commit()
        return True