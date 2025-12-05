from pydantic import BaseModel, field_validator, Field, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional

class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class SkillCategory(str, Enum):
    programming = "programming"
    music = "music"
    sports = "sports"
    languages = "languages"
    art = "art"
    science = "science"
    cooking = "cooking"
    other = "other"


class SkillBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Назва навички")
    description: str = Field(..., min_length=10, max_length=500, description="Детальний опис навички")
    category: SkillCategory
    level: SkillLevel

    @field_validator('title', 'description', mode='before')
    @classmethod
    def strip_title(cls, v: str):
        if v:
            return v.strip()
        else:
            raise ValueError('invalid data')
        

class SkillCreate(SkillBase):
    can_teach: bool
    want_learn: bool

class SkillResponse(SkillBase):
    id: int
    can_teach: bool
    want_learn: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SkillUpdate(BaseModel):
    title: Optional[str] = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    category: Optional[SkillCategory] = None
    level: Optional[SkillLevel] = None
    can_teach: Optional[bool] = None
    want_learn: Optional[bool] = None


class UserBase(BaseModel):
    username: str = Field(max_length=50, unique=True)
    email: EmailStr = Field(..., max_length=100)
    full_name: str = Field(max_length=100)

class UserCreate(UserBase):
    is_active: bool = Field(default=True)
    password: str 

class UserResponse(UserBase):
    id: Optional[int] = Field(..., ge=1)
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str