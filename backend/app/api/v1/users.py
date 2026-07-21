from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/users", tags=["users"])

# === МОДЕЛИ ===

class UserRole(str, Enum):
    ADMINISTRATOR = "administrator"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    password: str = Field(min_length=8, description="В реальности пароль хэшируется (bcrypt/argon2)")

# === ЗАГЛУШКА БД ===
_users_db = [
    User(id="1", email="admin@amf.local", full_name="Главный Администратор", role=UserRole.ADMINISTRATOR)
]

# === ENDPOINTS ===

@router.get("/me", response_model=User)
async def get_current_user(authorization: Optional[str] = Header(None)):
    '''Получить текущего авторизованного пользователя.'''
    # В реальности здесь будет декодирование JWT токена из заголовка Authorization
    return _users_db[0]

@router.get("/", response_model=List[User])
async def list_users():
    '''Получить список всех пользователей системы.'''
    return _users_db

@router.post("/", response_model=User, status_code=201)
async def create_user(request: UserCreateRequest):
    '''Добавить нового пользователя в команду.'''
    new_user = User(
        id=str(uuid4()),
        email=request.email,
        full_name=request.full_name,
        role=request.role
    )
    _users_db.append(new_user)
    return new_user

@router.put("/{user_id}/role")
async def update_user_role(user_id: str, new_role: UserRole):
    '''Изменить роль пользователя.'''
    for user in _users_db:
        if user.id == user_id:
            user.role = new_role
            return {"message": "Role updated", "user": user}
    raise HTTPException(status_code=404, detail="User not found")
