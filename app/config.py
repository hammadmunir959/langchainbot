import os
import uuid

from uuid import UUID
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlmodel import create_engine, Session, select
from langchain_community.chat_message_histories import SQLChatMessageHistory
from .models import ChatRequest, User, UserSession

load_dotenv()

# --- INFRASTRUCTURE ---
DB_URL = "sqlite:///database.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

# --- SECURITY ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(
    api_key: str = Security(api_key_header)):
    if os.getenv("API_KEY_ENABLED", "False").lower() == "true":
        if api_key != os.getenv("API_KEY"):
            raise HTTPException(
                status_code=403, 
                detail="Invalid or Missing API Key"
                )
    return api_key


def get_session():
    with Session(engine) as session:
        yield session

def get_session_history(session_id: str):
    return SQLChatMessageHistory(
        session_id=session_id, 
        connection=engine
        )

def validate_session(request: ChatRequest, db: Session = Depends(get_session)):
    """Resolves user, ensures user exists, and records the session."""

    # 1. Get or Create User
    user = db.exec(select(User).where(User.username == request.username)).first()
    if not user:
        user = User(username=request.username)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 2. Get or Generate Session ID

    if request.session_id == None:
        s_id= uuid.uuid4()
    else:
        s_id= request.session_id

    
    # 3. Check/Create UserSession
    if not db.exec(select(UserSession).where(UserSession.session_id == s_id)).first():
        db.add(UserSession(session_id=s_id, user_id=user.id))
        db.commit()

    return str(s_id)
