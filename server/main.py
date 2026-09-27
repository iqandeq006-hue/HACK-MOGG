import os
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import (
    User, SkillListing, ListingType, CreditAccount,
    PeerSession, SessionStatus, SessionType, CreditTransaction, ChatMessage,
    GroupRoom, GroupMessage, DomainCertification, TransactionType
)
import matching
import ledger
import resources
import ai_service
import scheduler
import web_search_integration
from seed import seed_database

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MOGG SkillSwap API",
    description="Peer-to-peer student skill exchange with semantic AI matching, time-credit ledger & Google Meet integration",
    version="2.0.0"
)

# Enable CORS for external frontends / local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount client directory for web UI & static assets
CLIENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))
if os.path.exists(CLIENT_DIR):
    app.mount("/static", StaticFiles(directory=CLIENT_DIR), name="static")
    app.mount("/client", StaticFiles(directory=CLIENT_DIR), name="client")

@app.get("/", response_class=FileResponse)
def serve_index():
    index_file = os.path.join(CLIENT_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "MOGG SkillSwap API is running. Visit /docs for Swagger UI."}

# ----------------- Pydantic Schemas -----------------

class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    bio: Optional[str] = ""
    linkedin_url: Optional[str] = None

class LoginRequest(BaseModel):
    name: str
    email: str

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None

class CourseCompleteRequest(BaseModel):
    user_id: int
    domain: str
    course_title: str
    score: int = 100

class ListingCreate(BaseModel):
    user_id: int
    type: ListingType
    skill_text: str
    category: Optional[str] = "General"
    domain: Optional[str] = "tech"
    fee_text: Optional[str] = "⚡ 1 Credit / Session"
    description: Optional[str] = ""

class SessionCreate(BaseModel):
    session_type: SessionType = SessionType.CREDIT_EXCHANGE
    teacher_id: int
    learner_id: int
    teach_skill_text: str
    trade_skill_text: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    notes: Optional[str] = None

class SessionAction(BaseModel):
    user_id: int

class AiQuery(BaseModel):
    query: str
    skill_context: Optional[str] = None
    chat_history: Optional[List[dict]] = None

class MessageCreate(BaseModel):
    sender_id: int
    text: str

class BioUpdate(BaseModel):
    bio: str

class GroupCreate(BaseModel):
    name: str
    topic: Optional[str] = ""
    creator_id: int
    member_ids: Optional[List[int]] = []

class GroupInvite(BaseModel):
    user_id: int

class GroupMessageCreate(BaseModel):
    sender_id: int
    text: str

# ----------------- Auth / Login Endpoint -----------------

@app.post("/api/auth/login")
def login_or_register(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    name = payload.name.strip()
    if not email or not name:
        raise HTTPException(status_code=400, detail="Name and email are required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={name}",
            bio="",
            linkedin_url=f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        ledger.get_or_create_account(db, user.id)
        is_new = True
    else:
        user.name = name
        db.commit()
        db.refresh(user)
        is_new = False

    acc = ledger.get_or_create_account(db, user.id)
    teach_listings = [
        {"id": l.id, "skill_text": l.skill_text, "category": l.category, "domain": l.domain,
         "fee_text": l.fee_text, "description": l.description}
        for l in user.listings if l.type == ListingType.TEACH
    ]
    learn_listings = [
        {"id": l.id, "skill_text": l.skill_text, "category": l.category, "domain": l.domain,
         "fee_text": l.fee_text, "description": l.description}
        for l in user.listings if l.type == ListingType.LEARN
    ]
    cert_list = [c.domain for c in user.certifications]
    return {
        "id": user.id, "name": user.name, "email": user.email,
        "avatar_url": user.avatar_url, "bio": user.bio,
        "linkedin_url": user.linkedin_url or "",
        "balance": acc.balance, "escrow_balance": acc.escrow_balance,
        "teach_listings": teach_listings, "learn_listings": learn_listings,
        "certifications": cert_list,
        "is_new": is_new
    }

# ----------------- User & Wallet Endpoints -----------------

@app.get("/api/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    results = []
    for u in users:
        acc = ledger.get_or_create_account(db, u.id)
        teach_count = sum(1 for l in u.listings if l.type == ListingType.TEACH)
        learn_count = sum(1 for l in u.listings if l.type == ListingType.LEARN)
        results.append({
            "id": u.id, "name": u.name, "email": u.email,
            "avatar_url": u.avatar_url, "bio": u.bio,
            "linkedin_url": u.linkedin_url or "",
            "balance": acc.balance, "escrow_balance": acc.escrow_balance,
            "teach_count": teach_count, "learn_count": learn_count,
            "certifications": [c.domain for c in u.certifications]
        })
    return results

@app.get("/api/users/{user_id}")
def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    acc = ledger.get_or_create_account(db, u.id)
    teach_listings = [
        {"id": l.id, "skill_text": l.skill_text, "category": l.category,
         "domain": l.domain, "fee_text": l.fee_text, "description": l.description}
        for l in u.listings if l.type == ListingType.TEACH
    ]
    learn_listings = [
        {"id": l.id, "skill_text": l.skill_text, "category": l.category,
         "domain": l.domain, "fee_text": l.fee_text, "description": l.description}
        for l in u.listings if l.type == ListingType.LEARN
    ]
    return {
        "id": u.id, "name": u.name, "email": u.email,
        "avatar_url": u.avatar_url, "bio": u.bio,
        "linkedin_url": u.linkedin_url or "",
        "balance": acc.balance, "escrow_balance": acc.escrow_balance,
        "teach_listings": teach_listings, "learn_listings": learn_listings,
        "certifications": [c.domain for c in u.certifications]
    }

@app.post("/api/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    linkedin = payload.linkedin_url or f"https://www.linkedin.com/in/{payload.name.lower().replace(' ', '-')}"
    u = User(
        name=payload.name,
        email=payload.email,
        avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={payload.name}",
        bio=payload.bio or "",
        linkedin_url=linkedin
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    # Grant welcome credits
    ledger.get_or_create_account(db, u.id)
    return {"id": u.id, "name": u.name, "email": u.email, "linkedin_url": u.linkedin_url}

@app.put("/api/users/{user_id}/bio")
def update_user_bio(user_id: int, payload: BioUpdate, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.bio = payload.bio
    db.commit()
    return {"id": u.id, "name": u.name, "bio": u.bio, "linkedin_url": u.linkedin_url or ""}

@app.put("/api/users/{user_id}/profile")
def update_user_profile(user_id: int, payload: ProfileUpdate, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.bio is not None:
        u.bio = payload.bio
    if payload.linkedin_url is not None:
        u.linkedin_url = payload.linkedin_url.strip()
    db.commit()
    return {
        "id": u.id,
        "name": u.name,
        "bio": u.bio,
        "linkedin_url": u.linkedin_url or ""
    }

@app.post("/api/users/{user_id}/claim-daily")
def claim_daily_coin(user_id: int, db: Session = Depends(get_db)):
    res = ledger.claim_daily_free_coin(db, user_id)
    return res

@app.post("/api/users/{user_id}/earn-bonus")
def earn_bonus(user_id: int, reason: str = "Completed Challenge", db: Session = Depends(get_db)):
    res = ledger.earn_bonus_coin(db, user_id, reason=reason)
    return res

@app.get("/api/users/{user_id}/ledger")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    txs = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == user_id
    ).order_by(CreditTransaction.created_at.desc()).all()
    return [
        {
            "id": t.id, "amount": t.amount, "type": t.type,
            "description": t.description, "created_at": t.created_at.isoformat()
        }
        for t in txs
    ]

# ----------------- Skill Listings Endpoints -----------------

@app.get("/api/listings")
def list_listings(user_id: Optional[int] = None, type: Optional[ListingType] = None, db: Session = Depends(get_db)):
    q = db.query(SkillListing)
    if user_id:
        q = q.filter(SkillListing.user_id == user_id)
    if type:
        q = q.filter(SkillListing.type == type)
    listings = q.all()
    return [
        {
            "id": l.id, "user_id": l.user_id, "user_name": l.user.name,
            "type": l.type.value, "skill_text": l.skill_text,
            "category": l.category, "domain": l.domain,
            "fee_text": l.fee_text, "description": l.description,
            "created_at": l.created_at.isoformat()
        }
        for l in listings
    ]

@app.post("/api/listings", status_code=status.HTTP_201_CREATED)
def create_listing(payload: ListingCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Domain certification check: Must pass free training course in this domain to post TEACH skills
    if payload.type == ListingType.TEACH:
        target_domain = (payload.domain or "tech").lower().strip()
        has_cert = db.query(DomainCertification).filter(
            DomainCertification.user_id == payload.user_id,
            DomainCertification.domain == target_domain
        ).first()
        if not has_cert:
            raise HTTPException(
                status_code=403,
                detail=f"Domain certification required! You must complete the free training course & quiz in '{target_domain.title()}' to unlock teaching in this domain."
            )

    # Generate vector embedding for semantic matching
    vec = matching.embed_text(payload.skill_text)
    listing = SkillListing(
        user_id=payload.user_id,
        type=payload.type,
        skill_text=payload.skill_text,
        category=payload.category,
        domain=payload.domain,
        fee_text=payload.fee_text,
        description=payload.description,
        embedding=matching.vector_to_bytes(vec)
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return {
        "id": listing.id, "user_id": listing.user_id,
        "type": listing.type.value, "skill_text": listing.skill_text,
        "category": listing.category, "domain": listing.domain,
        "fee_text": listing.fee_text, "description": listing.description
    }

# ----------------- Course Completion & Domain Certifications -----------------

@app.post("/api/courses/complete")
def complete_course_certification(payload: CourseCompleteRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    target_domain = payload.domain.lower().strip()
    existing_cert = db.query(DomainCertification).filter(
        DomainCertification.user_id == user.id,
        DomainCertification.domain == target_domain
    ).first()

    coins_rewarded = 0
    if not existing_cert:
        cert = DomainCertification(
            user_id=user.id,
            domain=target_domain,
            course_title=payload.course_title,
            score=payload.score
        )
        db.add(cert)
        bonus_res = ledger.earn_bonus_coin(
            db, user.id, amount=2,
            reason=f"Completed {target_domain.title()} Certification Course",
            tx_type=TransactionType.COURSE_CERTIFICATION.value
        )
        coins_rewarded = 2
        new_balance = bonus_res["new_balance"]
    else:
        acc = ledger.get_or_create_account(db, user.id)
        new_balance = acc.balance

    return {
        "success": True,
        "domain": target_domain,
        "bonus_earned": coins_rewarded,
        "new_balance": new_balance,
        "message": f"Congratulations! You completed the {target_domain.title()} course, earned {coins_rewarded} MG Coins, and unlocked teaching!"
    }

@app.get("/api/users/{user_id}/certifications")
def get_user_certifications(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    certs = db.query(DomainCertification).filter(DomainCertification.user_id == user_id).all()
    return [
        {
            "domain": c.domain,
            "course_title": c.course_title,
            "score": c.score,
            "certified_at": c.certified_at.isoformat()
        }
        for c in certs
    ]

@app.delete("/api/listings/{listing_id}")
def delete_listing(listing_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    listing = db.query(SkillListing).filter(
        SkillListing.id == listing_id, SkillListing.user_id == user_id
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or not owned by user")
    db.delete(listing)
    db.commit()
    return {"status": "deleted", "id": listing_id}

# ----------------- Community Marketplace -----------------

@app.get("/api/community/skills")
def get_community_skills(domain: Optional[str] = None, db: Session = Depends(get_db)):
    """Aggregated marketplace: all TEACH listings with seller info for the MOGG frontend."""
    q = db.query(SkillListing).filter(SkillListing.type == ListingType.TEACH)
    if domain and domain != "all":
        q = q.filter(SkillListing.domain == domain)
    listings = q.all()

    results = []
    for l in listings:
        results.append({
            "id": l.id,
            "skill_text": l.skill_text,
            "category": l.category,
            "domain": l.domain or "tech",
            "fee_text": l.fee_text or "⚡ 1 Credit / Session",
            "description": l.description or "",
            "seller_id": l.user.id,
            "seller_name": l.user.name,
            "seller_email": l.user.email,
            "seller_bio": l.user.bio or "",
            "seller_avatar": l.user.avatar_url,
            "seller_linkedin": l.user.linkedin_url or ""
        })
    return {"count": len(results), "listings": results}

# ----------------- Semantic Matching Endpoints -----------------

@app.get("/api/matches/{learn_listing_id}")
def get_matches_for_listing(learn_listing_id: int, threshold: float = 0.60, db: Session = Depends(get_db)):
    """
    Computes cosine similarity between this LEARN listing and all active TEACH listings.
    """
    matches = matching.match_learn_listing(db, learn_listing_id, threshold=threshold)
    return {
        "learn_listing_id": learn_listing_id,
        "threshold_applied": threshold,
        "match_count": len(matches),
        "matches": matches
    }

@app.get("/api/matches/mutual-trades/{user_id}")
def get_mutual_trades_for_user(user_id: int, threshold: float = 0.60, db: Session = Depends(get_db)):
    """
    Finds direct 1-on-1 equal skill trade candidates:
    Where user teaches what peer learns AND peer teaches what user learns!
    """
    trades = matching.find_mutual_trade_candidates(db, user_id, threshold=threshold)
    return {
        "user_id": user_id,
        "mutual_trade_count": len(trades),
        "trades": trades
    }

@app.get("/api/teachers")
def search_teachers(skill: str, user_id: Optional[int] = None, threshold: float = 0.55, db: Session = Depends(get_db)):
    """
    Semantic search over all teachers for users wishing to spend a credit without a reciprocal match.
    """
    results = matching.search_teachers_by_skill(db, skill, current_user_id=user_id, threshold=threshold)
    return {
        "search_query": skill,
        "threshold": threshold,
        "count": len(results),
        "teachers": results
    }

# ----------------- Session & Meeting Endpoints -----------------

@app.post("/api/sessions", status_code=status.HTTP_201_CREATED)
def request_session(payload: SessionCreate, db: Session = Depends(get_db)):
    teacher = db.query(User).filter(User.id == payload.teacher_id).first()
    learner = db.query(User).filter(User.id == payload.learner_id).first()
    if not teacher or not learner:
        raise HTTPException(status_code=404, detail="Teacher or Learner not found")

    if payload.session_type == SessionType.CREDIT_EXCHANGE:
        learner_acc = ledger.get_or_create_account(db, learner.id)
        if learner_acc.balance < 1:
            raise HTTPException(status_code=400, detail="Insufficient credits. Earn free coins or claim daily reward first!")

    # Auto-generate Google Meet link & Calendar invite
    meet_info = scheduler.create_google_meet_session(
        topic=payload.teach_skill_text,
        teacher_name=teacher.name,
        learner_name=learner.name,
        start_time=payload.scheduled_time
    )

    session_obj = PeerSession(
        session_type=payload.session_type,
        teacher_id=payload.teacher_id,
        learner_id=payload.learner_id,
        teach_skill_text=payload.teach_skill_text,
        trade_skill_text=payload.trade_skill_text,
        status=SessionStatus.REQUESTED,
        scheduled_time=payload.scheduled_time or datetime.utcnow(),
        google_meet_url=meet_info["meet_url"],
        calendar_link=meet_info["calendar_url"],
        notes=payload.notes
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    return {
        "id": session_obj.id,
        "session_type": session_obj.session_type.value,
        "teacher_id": teacher.id,
        "teacher": teacher.name,
        "learner_id": learner.id,
        "learner": learner.name,
        "teach_skill": session_obj.teach_skill_text,
        "trade_skill": session_obj.trade_skill_text,
        "status": session_obj.status.value,
        "google_meet_url": session_obj.google_meet_url,
        "calendar_link": session_obj.calendar_link,
        "created_at": session_obj.created_at.isoformat()
    }

@app.get("/api/sessions")
def list_sessions(user_id: Optional[int] = None, status: Optional[SessionStatus] = None, db: Session = Depends(get_db)):
    q = db.query(PeerSession)
    if user_id:
        q = q.filter((PeerSession.teacher_id == user_id) | (PeerSession.learner_id == user_id))
    if status:
        q = q.filter(PeerSession.status == status)
    sessions = q.order_by(PeerSession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "session_type": s.session_type.value,
            "teacher_id": s.teacher_id,
            "teacher_name": s.teacher.name,
            "learner_id": s.learner_id,
            "learner_name": s.learner.name,
            "teach_skill": s.teach_skill_text,
            "trade_skill": s.trade_skill_text,
            "status": s.status.value,
            "google_meet_url": s.google_meet_url,
            "calendar_link": s.calendar_link,
            "scheduled_time": s.scheduled_time.isoformat() if s.scheduled_time else None,
            "created_at": s.created_at.isoformat()
        }
        for s in sessions
    ]

@app.post("/api/sessions/{session_id}/accept")
def accept_session(session_id: int, action: SessionAction, db: Session = Depends(get_db)):
    try:
        s = ledger.transition_accept_session(db, session_id, action.user_id)
        return {
            "id": s.id,
            "status": s.status.value,
            "message": "Session accepted. 1 credit held in escrow." if s.session_type == SessionType.CREDIT_EXCHANGE else "Mutual trade accepted! Join your peer on Google Meet."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sessions/{session_id}/complete")
def complete_session(session_id: int, action: SessionAction, db: Session = Depends(get_db)):
    try:
        s = ledger.transition_complete_and_release(db, session_id, action.user_id)
        return {
            "id": s.id,
            "status": s.status.value,
            "message": "Session completed! Credit released to teacher." if s.session_type == SessionType.CREDIT_EXCHANGE else "Mutual skill trade completed successfully!"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sessions/{session_id}/decline")
def decline_session(session_id: int, action: SessionAction, db: Session = Depends(get_db)):
    try:
        s = ledger.transition_decline_or_cancel(db, session_id, action.user_id)
        return {"id": s.id, "status": s.status.value, "message": "Session declined/cancelled."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----------------- Chat / Messages Endpoints -----------------

@app.get("/api/messages/{session_id}")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    session = db.query(PeerSession).filter(PeerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": m.sender.name,
            "text": m.text,
            "created_at": m.created_at.isoformat()
        }
        for m in msgs
    ]

@app.post("/api/messages/{session_id}", status_code=status.HTTP_201_CREATED)
def send_message(session_id: int, payload: MessageCreate, db: Session = Depends(get_db)):
    session = db.query(PeerSession).filter(PeerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    sender = db.query(User).filter(User.id == payload.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    msg = ChatMessage(
        session_id=session_id,
        sender_id=payload.sender_id,
        text=payload.text
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "sender_name": sender.name,
        "text": msg.text,
        "created_at": msg.created_at.isoformat()
    }

@app.get("/api/messages/private/conversations/{user_id}")
def get_private_conversations(user_id: int, db: Session = Depends(get_db)):
    """
    Returns all 1-on-1 private peer conversations for the user across their skill exchanges.
    """
    user_sessions = db.query(PeerSession).filter(
        (PeerSession.teacher_id == user_id) | (PeerSession.learner_id == user_id)
    ).order_by(PeerSession.created_at.desc()).all()

    convos = []
    for s in user_sessions:
        is_teacher = s.teacher_id == user_id
        peer = s.learner if is_teacher else s.teacher
        if not peer:
            continue
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.session_id == s.id
        ).order_by(ChatMessage.created_at.desc()).first()

        convos.append({
            "session_id": s.id,
            "session_status": s.status.value,
            "skill_text": s.teach_skill_text,
            "peer_id": peer.id,
            "peer_name": peer.name,
            "peer_avatar": peer.avatar_url,
            "peer_linkedin": peer.linkedin_url or "",
            "role": "Teacher" if is_teacher else "Learner",
            "last_message": {
                "text": last_msg.text,
                "created_at": last_msg.created_at.isoformat(),
                "sender_id": last_msg.sender_id
            } if last_msg else None,
            "google_meet_url": s.google_meet_url
        })
    return {"conversations": convos, "total": len(convos)}

# ----------------- Group Study Rooms & Multi-Peer Chat -----------------

@app.get("/api/groups")
def list_group_rooms(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List all study group rooms with member counts, topic, and creator details."""
    rooms = db.query(GroupRoom).order_by(GroupRoom.created_at.desc()).all()
    result = []
    for r in rooms:
        member_ids = [m.id for m in r.members]
        is_member = bool(user_id and (user_id in member_ids or user_id == r.creator_id))
        last_msg = (
            db.query(GroupMessage)
            .filter(GroupMessage.room_id == r.id)
            .order_by(GroupMessage.created_at.desc())
            .first()
        )
        result.append({
            "id": r.id,
            "name": r.name,
            "topic": r.topic or "",
            "creator_id": r.creator_id,
            "creator_name": r.creator.name if r.creator else "Unknown",
            "member_count": len(r.members),
            "is_member": is_member,
            "members": [
                {
                    "id": m.id,
                    "name": m.name,
                    "email": m.email,
                    "avatar_url": m.avatar_url or f"https://api.dicebear.com/7.x/bottts/svg?seed={m.name}",
                    "bio": m.bio or ""
                }
                for m in r.members
            ],
            "last_message": {
                "sender_id": last_msg.sender_id,
                "sender_name": last_msg.sender.name if last_msg.sender else "Unknown",
                "text": last_msg.text,
                "created_at": last_msg.created_at.isoformat()
            } if last_msg else None,
            "created_at": r.created_at.isoformat()
        })
    return {"rooms": result, "total": len(result)}

@app.post("/api/groups", status_code=status.HTTP_201_CREATED)
def create_group_room(payload: GroupCreate, db: Session = Depends(get_db)):
    """Create a new multi-peer study room and invite initial members."""
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Group name is required")
    creator = db.query(User).filter(User.id == payload.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator user not found")

    room = GroupRoom(
        name=name,
        topic=payload.topic.strip() if payload.topic else "",
        creator_id=creator.id
    )
    # Creator is automatically a member
    room.members.append(creator)

    # Add any invited members
    if payload.member_ids:
        for mid in payload.member_ids:
            if mid != creator.id:
                member_user = db.query(User).filter(User.id == mid).first()
                if member_user and member_user not in room.members:
                    room.members.append(member_user)

    db.add(room)
    db.commit()
    db.refresh(room)

    # Add a system welcome message
    welcome = GroupMessage(
        room_id=room.id,
        sender_id=creator.id,
        text=f"Welcome to {room.name}! Let's learn and share skills together."
    )
    db.add(welcome)
    db.commit()

    return {
        "id": room.id,
        "name": room.name,
        "topic": room.topic,
        "creator_id": room.creator_id,
        "creator_name": creator.name,
        "member_count": len(room.members),
        "created_at": room.created_at.isoformat()
    }

@app.get("/api/groups/{room_id}")
def get_group_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(GroupRoom).filter(GroupRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Group room not found")
    return {
        "id": room.id,
        "name": room.name,
        "topic": room.topic or "",
        "creator_id": room.creator_id,
        "creator_name": room.creator.name if room.creator else "Unknown",
        "member_count": len(room.members),
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "avatar_url": m.avatar_url or f"https://api.dicebear.com/7.x/bottts/svg?seed={m.name}",
                "bio": m.bio or ""
            }
            for m in room.members
        ],
        "created_at": room.created_at.isoformat()
    }

@app.post("/api/groups/{room_id}/join")
def join_group_room(room_id: int, payload: GroupInvite, db: Session = Depends(get_db)):
    room = db.query(GroupRoom).filter(GroupRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Group room not found")
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in room.members:
        room.members.append(user)
        # Notify room
        sys_msg = GroupMessage(
            room_id=room.id,
            sender_id=user.id,
            text=f"{user.name} joined the study group."
        )
        db.add(sys_msg)
        db.commit()
    return {"success": True, "member_count": len(room.members)}

@app.post("/api/groups/{room_id}/invite")
def invite_to_group_room(room_id: int, payload: GroupInvite, db: Session = Depends(get_db)):
    room = db.query(GroupRoom).filter(GroupRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Group room not found")
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in room.members:
        room.members.append(user)
        invite_msg = GroupMessage(
            room_id=room.id,
            sender_id=user.id,
            text=f"{user.name} was added to the study group."
        )
        db.add(invite_msg)
        db.commit()
    return {"success": True, "member_count": len(room.members)}

@app.get("/api/groups/{room_id}/messages")
def get_group_messages(room_id: int, db: Session = Depends(get_db)):
    room = db.query(GroupRoom).filter(GroupRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Group room not found")
    messages = (
        db.query(GroupMessage)
        .filter(GroupMessage.room_id == room_id)
        .order_by(GroupMessage.created_at.asc())
        .all()
    )
    return {
        "room_id": room_id,
        "count": len(messages),
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "sender_name": m.sender.name if m.sender else "Unknown",
                "sender_avatar": m.sender.avatar_url if m.sender else None,
                "text": m.text,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }

@app.post("/api/groups/{room_id}/messages", status_code=status.HTTP_201_CREATED)
def send_group_message(room_id: int, payload: GroupMessageCreate, db: Session = Depends(get_db)):
    room = db.query(GroupRoom).filter(GroupRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Group room not found")
    sender = db.query(User).filter(User.id == payload.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    # If sender isn't in room yet, auto-add
    if sender not in room.members:
        room.members.append(sender)

    msg = GroupMessage(
        room_id=room_id,
        sender_id=sender.id,
        text=payload.text.strip()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "sender_name": sender.name,
        "sender_avatar": sender.avatar_url,
        "text": msg.text,
        "created_at": msg.created_at.isoformat()
    }

# ----------------- Learning Resources (YouTube) -----------------

@app.get("/api/resources/youtube")
def get_youtube_videos(skill: str):
    videos = resources.get_best_youtube_videos_for_skill(skill)
    return {
        "skill": skill,
        "recommended_videos": videos
    }

@app.get("/api/resources/youtube-live")
def get_youtube_live_videos(query: str, limit: int = 5):
    """
    Live YouTube search extracting real titles, channel names, view counts,
    thumbnails, and URLs.
    """
    videos = web_search_integration.search_youtube_live(query, limit=limit)
    return {
        "query": query,
        "count": len(videos),
        "videos": videos
    }

@app.get("/api/resources/web-search")
def get_web_articles(query: str, limit: int = 5):
    """
    Live Web search for skill documentation, cheatsheets, and roadmaps.
    """
    articles = web_search_integration.search_web_articles_and_docs(query, limit=limit)
    return {
        "query": query,
        "count": len(articles),
        "articles": articles
    }

@app.get("/api/resources/hub")
def get_comprehensive_hub(skill: str):
    """
    Unified learning resource hub combining curated courses, live YouTube search,
    and authoritative web documentation.
    """
    hub = web_search_integration.get_skill_learning_hub(skill)
    return hub

# ----------------- Open-Source AI Doubts & Chatbot -----------------

@app.post("/api/ai/ask")
async def ask_ai_tutor(payload: AiQuery):
    messages = []
    if payload.chat_history:
        messages.extend(payload.chat_history)
    messages.append({"role": "user", "content": payload.query})

    reply = await ai_service.query_cloud_ai_model(messages, skill_context=payload.skill_context)
    return {
        "reply": reply,
        "skill_context": payload.skill_context
    }

# ----------------- Health & Seed -----------------

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "MOGG SkillSwap API", "time": datetime.utcnow().isoformat()}

@app.post("/api/seed/reset")
def reset_seed():
    seed_database()
    return {"status": "success", "message": "Seeded benchmark data successfully"}

# ----------------- Client SPA Catch-all Route -----------------
@app.get("/{full_path:path}")
def serve_client_assets(full_path: str):
    file_path = os.path.join(CLIENT_DIR, full_path)
    if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_file = os.path.join(CLIENT_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "MOGG SkillSwap API is running. Visit /docs for Swagger UI."}
