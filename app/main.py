from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, SQLModel
from .models import ChatRequest, UserSession
from .engine import stream_response, get_history
from .config import engine, get_session, validate_session, verify_api_key

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/chat", 
    dependencies=[Depends(verify_api_key)]
    )
def chat(
    request: ChatRequest, 
    sid: str = Depends(validate_session)
    ):
    
    """Secured chat endpoint."""
    
    return StreamingResponse(
        stream_response(
            request.message, 
            sid, 
            request.username, 
            request.location
            ), 
        media_type="text/plain",
        headers={"X-Session-ID": sid}
    )

@app.get("/sessions/{session_id}",
    dependencies=[Depends(verify_api_key)]
    )
def get_session_history(
    session_id: str, 
    db: Session = Depends(get_session)
    ):
    
    """Returns all history messages for a specific session."""

    try:
        s_id = UUID(session_id)
    except ValueError:
        raise HTTPException(400, "Invalid session ID format")

    session = db.exec(select(UserSession).where(UserSession.session_id == s_id)).first()
    
    if not session:
        raise HTTPException(404, "Session not found")

    # 2. Retrieve history
    messages = get_history(session_id)
    
    return {
        "session_id": session_id,
        "messages": messages
    }
