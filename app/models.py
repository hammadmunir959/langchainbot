from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlmodel import SQLModel, Field as SQLField, Relationship

class User(SQLModel, table=True):
    id: int = SQLField(primary_key=True)
    username: str = SQLField(unique=True)
    sessions: List["UserSession"] = Relationship(back_populates="user")

class UserSession(SQLModel, table=True):
    id: int = SQLField(primary_key=True)
    session_id: UUID = SQLField(default_factory=uuid4, unique=True)
    user_id: int = SQLField(foreign_key="user.id")
    user: User = Relationship(back_populates="sessions")

class ChatRequest(BaseModel):
    username: str = Field(..., pattern="^[a-zA-Z0-9]+$")
    message: str = Field(..., min_length=2)
    session_id: Optional[UUID] = None
    location: Optional[str] = "Unknown"
