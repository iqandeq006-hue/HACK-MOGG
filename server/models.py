import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, LargeBinary, Text, Table
from sqlalchemy.orm import relationship
from database import Base

class ListingType(str, enum.Enum):
    TEACH = "TEACH"
    LEARN = "LEARN"

class SessionType(str, enum.Enum):
    CREDIT_EXCHANGE = "CREDIT_EXCHANGE"
    DIRECT_TRADE = "DIRECT_TRADE"

class SessionStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    COMPLETED = "COMPLETED"
    CREDIT_RELEASED = "CREDIT_RELEASED"
    DECLINED = "DECLINED"

class TransactionType(str, enum.Enum):
    INITIAL_GRANT = "INITIAL_GRANT"
    DAILY_REWARD = "DAILY_REWARD"
    ESCROW_HOLD = "ESCROW_HOLD"
    ESCROW_RELEASE = "ESCROW_RELEASE"
    EARNED_TEACHING = "EARNED_TEACHING"
    COURSE_CERTIFICATION = "COURSE_CERTIFICATION"
    REFUND_ESCROW = "REFUND_ESCROW"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True, default="")
    linkedin_url = Column(String, nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    listings = relationship("SkillListing", back_populates="user", cascade="all, delete-orphan")
    credit_account = relationship("CreditAccount", back_populates="user", uselist=False, cascade="all, delete-orphan")
    certifications = relationship("DomainCertification", back_populates="user", cascade="all, delete-orphan")

class DomainCertification(Base):
    __tablename__ = "domain_certifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain = Column(String, nullable=False, index=True)  # tech, soft, survival, creative, languages, business
    course_title = Column(String, nullable=False)
    score = Column(Integer, default=100)
    certified_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="certifications")

class CreditAccount(Base):
    __tablename__ = "credit_accounts"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    balance = Column(Integer, default=3, nullable=False)           # Available coins
    escrow_balance = Column(Integer, default=0, nullable=False)    # Locked during accepted sessions
    last_daily_claim = Column(DateTime, nullable=True)             # Daily free coin tracking

    user = relationship("User", back_populates="credit_account")

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(String, nullable=False) # TransactionType value
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SkillListing(Base):
    __tablename__ = "skill_listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(ListingType), nullable=False)
    skill_text = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True)
    domain = Column(String, nullable=True, default="tech")        # tech, soft, survival, creative, languages, business
    fee_text = Column(String, nullable=True, default="⚡ 1 Credit / Session")  # Display text for pricing
    description = Column(Text, nullable=True, default="")         # Detailed skill description
    embedding = Column(LargeBinary, nullable=True)  # Serialized numpy vector
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="listings")

class PeerSession(Base):
    __tablename__ = "peer_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_type = Column(Enum(SessionType), default=SessionType.CREDIT_EXCHANGE, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    learner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teach_skill_text = Column(String, nullable=False)
    trade_skill_text = Column(String, nullable=True) # Used if DIRECT_TRADE: what learner teaches teacher in return
    status = Column(Enum(SessionStatus), default=SessionStatus.REQUESTED, nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    google_meet_url = Column(String, nullable=True)
    calendar_link = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", foreign_keys=[teacher_id])
    learner = relationship("User", foreign_keys=[learner_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("peer_sessions.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("PeerSession", back_populates="messages")
    sender = relationship("User")

# ─────────────────────────────────────────────────────────
# Multi-Peer Study Rooms & Group Chat
# ─────────────────────────────────────────────────────────
group_room_members = Table(
    "group_room_members",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("group_rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("joined_at", DateTime, default=datetime.utcnow)
)

class GroupRoom(Base):
    __tablename__ = "group_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", foreign_keys=[creator_id])
    members = relationship("User", secondary=group_room_members, backref="group_rooms")
    messages = relationship("GroupMessage", back_populates="room", cascade="all, delete-orphan")

class GroupMessage(Base):
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("group_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("GroupRoom", back_populates="messages")
    sender = relationship("User")
