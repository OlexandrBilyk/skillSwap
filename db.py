from sqlmodel import create_engine, Session, SQLModel, Field, Relationship
import os
from pydantic import EmailStr
from models import SkillCategory, SkillLevel
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
import bcrypt

load_dotenv()

DB_URL = os.getenv('DB_URL')

engine = create_engine(DB_URL)


class UserSkillLink(SQLModel, table=True):
    user_id: Optional[int] = Field(foreign_key='user.id', primary_key=True, default=None)
    skill_id: Optional[int] = Field(foreign_key='skill.id', primary_key=True, default=None)


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    username: str = Field(max_length=50, unique=True)
    password: str = Field()
    email: EmailStr = Field(max_length=100)
    full_name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)

    skills: List["Skill"] = Relationship(back_populates="users", link_model=UserSkillLink)

    sent_exchanges: List["Exchange"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.sender_id]"}
    )
    received_exchanges: List["Exchange"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.receiver_id]"}
    )

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    category: SkillCategory = Field()
    level: SkillLevel = Field()
    can_teach: bool = Field(default=False)
    want_learn: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    users: List["User"] = Relationship(back_populates="skills", link_model=UserSkillLink)

    exchanges: List["Exchange"] = Relationship(back_populates="skill")


class Exchange(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)

    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    skill_id: int = Field(foreign_key="skill.id")

    message: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    sender: User = Relationship(
        back_populates="sent_exchanges",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.sender_id]"}
    )
    receiver: User = Relationship(
        back_populates="received_exchanges",
        sa_relationship_kwargs={"foreign_keys": "[Exchange.receiver_id]"}
    )

    skill: Skill = Relationship(back_populates="exchanges")


def get_db():
    with Session(engine) as session:
        yield session
