from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.debate import DebateRoom, DebateMessage
from ..schemas.debate import (
    DebateRoom as DebateRoomSchema,
    DebateRoomCreate,
    DebateRoomUpdate,
    DebateRoomWithDetails,
    DebateMessage as DebateMessageSchema,
    DebateMessageCreate,
    DebateMessageWithUser
)

router = APIRouter()


@router.get("/", response_model=List[DebateRoomSchema])
async def get_debate_rooms(
    status_filter: str = Query("Active", description="Filter by status: Active, Ended, Cancelled"),
    limit: int = Query(20, le=50),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of debate rooms"""
    query = db.query(DebateRoom)
    
    if status_filter != "all":
        query = query.filter(DebateRoom.status == status_filter)
    
    debate_rooms = query.order_by(DebateRoom.created_at.desc()).offset(skip).limit(limit).all()
    return debate_rooms


@router.post("/", response_model=DebateRoomSchema)
async def create_debate_room(
    debate_data: DebateRoomCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new debate room"""
    db_debate = DebateRoom(
        created_by=current_user.id,
        **debate_data.dict()
    )
    
    # Add creator as first participant
    db_debate.participants = [str(current_user.id)]
    db_debate.current_participants = 1
    
    db.add(db_debate)
    db.commit()
    db.refresh(db_debate)
    return db_debate


@router.get("/{debate_id}", response_model=DebateRoomWithDetails)
async def get_debate_room(debate_id: str, db: Session = Depends(get_db)):
    """Get specific debate room with details"""
    debate = db.query(DebateRoom).filter(DebateRoom.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate room not found")
    return debate


@router.put("/{debate_id}", response_model=DebateRoomSchema)
async def update_debate_room(
    debate_id: str,
    debate_data: DebateRoomUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update debate room (creator only)"""
    debate = db.query(DebateRoom).filter(DebateRoom.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate room not found")
    
    if debate.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only creator can update debate room")
    
    for field, value in debate_data.dict(exclude_unset=True).items():
        setattr(debate, field, value)
    
    db.commit()
    db.refresh(debate)
    return debate


@router.post("/{debate_id}/join")
async def join_debate_room(
    debate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a debate room"""
    debate = db.query(DebateRoom).filter(DebateRoom.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate room not found")
    
    if debate.status != "Active":
        raise HTTPException(status_code=400, detail="Debate room is not active")
    
    if str(current_user.id) in debate.participants:
        raise HTTPException(status_code=400, detail="Already joined this debate")
    
    if debate.current_participants >= debate.max_participants:
        raise HTTPException(status_code=400, detail="Debate room is full")
    
    # Add user to participants
    debate.participants.append(str(current_user.id))
    debate.current_participants += 1
    
    db.commit()
    db.refresh(debate)
    
    return {"message": "Successfully joined debate room", "debate_id": debate_id}


@router.post("/{debate_id}/leave")
async def leave_debate_room(
    debate_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Leave a debate room"""
    debate = db.query(DebateRoom).filter(DebateRoom.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate room not found")
    
    if str(current_user.id) not in debate.participants:
        raise HTTPException(status_code=400, detail="Not a participant in this debate")
    
    # Remove user from participants
    debate.participants.remove(str(current_user.id))
    debate.current_participants -= 1
    
    db.commit()
    db.refresh(debate)
    
    return {"message": "Successfully left debate room", "debate_id": debate_id}


@router.get("/{debate_id}/messages", response_model=List[DebateMessageWithUser])
async def get_debate_messages(
    debate_id: str,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get messages from a debate room"""
    messages = db.query(DebateMessage).filter(
        DebateMessage.debate_room_id == debate_id
    ).order_by(DebateMessage.created_at.asc()).offset(skip).limit(limit).all()
    
    return messages


@router.post("/{debate_id}/messages", response_model=DebateMessageSchema)
async def create_debate_message(
    debate_id: str,
    message_data: DebateMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new message in a debate room"""
    # Check if debate room exists and is active
    debate = db.query(DebateRoom).filter(DebateRoom.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate room not found")
    
    if debate.status != "Active":
        raise HTTPException(status_code=400, detail="Debate room is not active")
    
    # Check if user is a participant
    if str(current_user.id) not in debate.participants:
        raise HTTPException(status_code=400, detail="Must be a participant to send messages")
    
    # Create message
    db_message = DebateMessage(
        debate_room_id=debate_id,
        user_id=current_user.id,
        **message_data.dict()
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.post("/{debate_id}/end")
async def end_debate(
    debate_id: str,
    winner_user_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """End a debate and declare winner (creator only)"""
    debate = db.query(DebateRoom).filter(DebateRoom.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate room not found")
    
    if debate.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only creator can end debate")
    
    if debate.status != "Active":
        raise HTTPException(status_code=400, detail="Debate is already ended")
    
    # Update debate status
    debate.status = "Ended"
    if winner_user_id:
        debate.winner_user_id = winner_user_id
    
    db.commit()
    db.refresh(debate)
    
    return {"message": "Debate ended successfully", "debate_id": debate_id, "winner": winner_user_id}


@router.post("/{debate_id}/messages/{message_id}/vote")
async def vote_on_message(
    debate_id: str,
    message_id: str,
    vote_type: str = Query(..., description="Vote type: upvote or downvote"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Vote on a debate message"""
    message = db.query(DebateMessage).filter(
        DebateMessage.id == message_id,
        DebateMessage.debate_room_id == debate_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Update vote count
    if vote_type == "upvote":
        message.upvotes += 1
    elif vote_type == "downvote":
        message.downvotes += 1
    else:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    db.commit()
    db.refresh(message)
    
    return {"message": "Vote recorded", "message_id": message_id, "vote_type": vote_type} 