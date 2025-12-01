from sqlmodel import create_engine, Session, DateTime, SQLModel, Field, Relationship
import os
from pydantic import EmailStr
from models import SkillCategory, SkillLevel
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional

load_dotenv()

DB_URL = os.getenv('DB_URL')

engine = create_engine(DB_URL)
class UserSkillLink(SQLModel, table=True):
    user_id: Optional[int] = Field(foreign_key='user.id', primary_key=True,  default=None)
    skill_id: Optional[int] = Field(foreign_key='skill.id', primary_key=True,  default=None)

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True,  default=None)
    username: str = Field(max_length=50, unique=True)
    email: EmailStr = Field(max_length=100)
    full_name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)

    skills: List['Skill'] = Relationship(back_populates='users', link_model=UserSkillLink)


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str = Field( min_length=3, max_length=100)
    description: str = Field( min_length=10, max_length=500)
    category: SkillCategory = Field()
    level: SkillLevel = Field()
    can_teach: bool = Field(default=False)
    want_learn: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    users: List['User'] = Relationship(back_populates='skills', link_model=UserSkillLink)


class Exchange(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True,  default=None)
    sender_id: int = Field(foreign_key='user.id')
    receiver_id: int = Field(foreign_key='user.id') 
    skill_id: int = Field(foreign_key='skill.id')
    message: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

def get_db():
    with Session(engine) as session:
        yield session