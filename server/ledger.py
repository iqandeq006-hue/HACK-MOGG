from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import (
    CreditAccount, CreditTransaction, PeerSession,
    SessionStatus, SessionType, TransactionType
)

INITIAL_BALANCE = 3
DAILY_REWARD_COINS = 1

def get_or_create_account(db: Session, user_id: int) -> CreditAccount:
    account = db.query(CreditAccount).filter(CreditAccount.user_id == user_id).first()
    if not account:
        account = CreditAccount(user_id=user_id, balance=INITIAL_BALANCE, escrow_balance=0)
        db.add(account)
        db.flush()
        # Record initial grant
        tx = CreditTransaction(
            user_id=user_id,
            amount=INITIAL_BALANCE,
            type=TransactionType.INITIAL_GRANT.value,
            description="Welcome bonus: 3 free skill credits granted."
        )
        db.add(tx)
        db.commit()
        db.refresh(account)
    return account

def claim_daily_free_coin(db: Session, user_id: int):
    """
    Grants 1 free daily coin to the user.
    """
    account = get_or_create_account(db, user_id)
    now = datetime.utcnow()

    # Allow claim if never claimed or claimed more than 20 hours ago
    if account.last_daily_claim and (now - account.last_daily_claim) < timedelta(hours=20):
        remaining = timedelta(hours=20) - (now - account.last_daily_claim)
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return {
            "success": False,
            "message": f"Daily reward already claimed. Next claim available in {hours}h {minutes}m.",
            "balance": account.balance
        }

    account.balance += DAILY_REWARD_COINS
    account.last_daily_claim = now

    tx = CreditTransaction(
        user_id=user_id,
        amount=DAILY_REWARD_COINS,
        type=TransactionType.DAILY_REWARD.value,
        description="Daily login reward: +1 free skill credit."
    )
    db.add(tx)
    db.commit()
    db.refresh(account)

    return {
        "success": True,
        "message": "Claimed 1 free skill credit! Keep learning.",
        "new_balance": account.balance
    }

def earn_bonus_coin(db: Session, user_id: int, amount: int = 1, reason: str = "Learning Milestone", tx_type: str = None):
    """
    Allows earning additional free coins for practice, feedback, or completing courses.
    """
    account = get_or_create_account(db, user_id)
    account.balance += amount
    tx = CreditTransaction(
        user_id=user_id,
        amount=amount,
        type=tx_type or TransactionType.COURSE_CERTIFICATION.value,
        description=f"Bonus credit earned: {reason}"
    )
    db.add(tx)
    db.commit()
    db.refresh(account)
    return {"success": True, "new_balance": account.balance}

def transition_accept_session(db: Session, session_id: int, user_id: int):
    """
    Teacher accepts a requested session.
    If CREDIT_EXCHANGE: Deduct 1 credit from learner, lock into escrow.
    If DIRECT_TRADE: No credit change, both peers agree to mutual skill exchange.
    """
    peer_session = db.query(PeerSession).filter(PeerSession.id == session_id).first()
    if not peer_session:
        raise ValueError("Session not found")
    if peer_session.teacher_id != user_id:
        raise ValueError("Only the designated teacher can accept this session")
    if peer_session.status != SessionStatus.REQUESTED:
        raise ValueError(f"Cannot accept session currently in state {peer_session.status}")

    if peer_session.session_type == SessionType.CREDIT_EXCHANGE:
        learner_acc = get_or_create_account(db, peer_session.learner_id)
        if learner_acc.balance < 1:
            raise ValueError("Learner has insufficient skill credits (balance < 1)")

        # Deduct 1 from balance, add 1 to escrow
        learner_acc.balance -= 1
        learner_acc.escrow_balance += 1

        tx = CreditTransaction(
            user_id=peer_session.learner_id,
            amount=-1,
            type=TransactionType.ESCROW_HOLD.value,
            description=f"Escrow lock for session #{peer_session.id} with {peer_session.teacher.name}"
        )
        db.add(tx)

    peer_session.status = SessionStatus.ACCEPTED
    db.commit()
    db.refresh(peer_session)
    return peer_session

def transition_complete_and_release(db: Session, session_id: int, user_id: int):
    """
    Marks session completed and releases credit to teacher (if credit exchange).
    """
    peer_session = db.query(PeerSession).filter(PeerSession.id == session_id).first()
    if not peer_session:
        raise ValueError("Session not found")
    if user_id not in (peer_session.teacher_id, peer_session.learner_id):
        raise ValueError("Only participants can mark session complete")
    if peer_session.status != SessionStatus.ACCEPTED:
        raise ValueError(f"Session must be ACCEPTED before completing (current: {peer_session.status})")

    if peer_session.session_type == SessionType.CREDIT_EXCHANGE:
        learner_acc = get_or_create_account(db, peer_session.learner_id)
        teacher_acc = get_or_create_account(db, peer_session.teacher_id)

        # Release escrow
        learner_acc.escrow_balance = max(0, learner_acc.escrow_balance - 1)
        teacher_acc.balance += 1

        tx1 = CreditTransaction(
            user_id=peer_session.learner_id,
            amount=0,
            type=TransactionType.ESCROW_RELEASE.value,
            description=f"Escrow released for completed session #{peer_session.id}"
        )
        tx2 = CreditTransaction(
            user_id=peer_session.teacher_id,
            amount=1,
            type=TransactionType.EARNED_TEACHING.value,
            description=f"Earned 1 skill credit for teaching '{peer_session.teach_skill_text}' to {peer_session.learner.name}"
        )
        db.add_all([tx1, tx2])

    peer_session.status = SessionStatus.CREDIT_RELEASED
    db.commit()
    db.refresh(peer_session)
    return peer_session

def transition_decline_or_cancel(db: Session, session_id: int, user_id: int):
    """
    Cancels or declines a session. If already in escrow, refund learner.
    """
    peer_session = db.query(PeerSession).filter(PeerSession.id == session_id).first()
    if not peer_session:
        raise ValueError("Session not found")
    if user_id not in (peer_session.teacher_id, peer_session.learner_id):
        raise ValueError("Unauthorized")

    if peer_session.status == SessionStatus.ACCEPTED and peer_session.session_type == SessionType.CREDIT_EXCHANGE:
        learner_acc = get_or_create_account(db, peer_session.learner_id)
        learner_acc.escrow_balance = max(0, learner_acc.escrow_balance - 1)
        learner_acc.balance += 1

        tx = CreditTransaction(
            user_id=peer_session.learner_id,
            amount=1,
            type=TransactionType.REFUND_ESCROW.value,
            description=f"Refunded 1 credit from cancelled session #{peer_session.id}"
        )
        db.add(tx)

    peer_session.status = SessionStatus.DECLINED
    db.commit()
    db.refresh(peer_session)
    return peer_session
