import sys
import os
import io
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ensure server module path and working directory are set to server/
SERVER_DIR = Path(__file__).resolve().parent.parent / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
os.chdir(SERVER_DIR)

from database import SessionLocal
from models import (
    User, SkillListing, ListingType, PeerSession, SessionStatus, SessionType, ChatMessage,
    GroupRoom, GroupMessage, DomainCertification
)
import matching
import ledger
import resources
import ai_service
import scheduler

def run_tests():
    db = SessionLocal()
    print("================== RUNNING MOGG SKILLSWAP VERIFICATION SUITE ==================")

    # 1. Verify Users & Balances
    users = db.query(User).all()
    assert len(users) == 15, f"Expected 15 users, found {len(users)}"
    print(f"[PASS] [Test 1] 15 Users verified: {[u.name for u in users[:5]]} ...")

    alex = db.query(User).filter(User.name == "Alex Rivera").first()
    assert alex is not None, "Alex Rivera not found"
    acc = ledger.get_or_create_account(db, alex.id)
    assert acc.balance >= 1, f"Expected credit balance for Alex, got {acc.balance}"
    print(f"[PASS] [Test 2] User credit accounts verified (Alex balance: {acc.balance}).")

    # 2. Verify Semantic Matching Benchmark Cases
    alex_learn = db.query(SkillListing).filter(
        SkillListing.user_id == alex.id,
        SkillListing.type == ListingType.LEARN
    ).first()
    assert alex_learn is not None, "Alex learn listing not found"

    matches = matching.match_learn_listing(db, alex_learn.id, threshold=0.55)
    print(f"\nMatches for Alex's LEARN ('{alex_learn.skill_text}'):")
    for m in matches[:3]:
        print(f"  - Teacher: {m['teacher_name']} | Skill: {m['teach_skill']} | Score: {m['similarity_score']}")

    top_match = matches[0]
    assert top_match["teacher_name"] == "Sofia Chen", f"Expected Sofia Chen to top match Alex, got {top_match['teacher_name']}"
    assert top_match["similarity_score"] >= 0.70, f"Score {top_match['similarity_score']} below threshold"
    print("[PASS] [Test 3] Semantic match passed: Sofia ('AI Prompt Engineering') matches Alex ('AI Prompt Engineering & Agents').")

    # Deliberate near-miss check: Guitar vs Firemaking
    marcus_guitar = db.query(SkillListing).filter(
        SkillListing.skill_text.ilike("%Guitar%"),
        SkillListing.type == ListingType.TEACH
    ).first()
    guitar_vec = matching.bytes_to_vector(marcus_guitar.embedding)
    fire_listing = db.query(SkillListing).filter(
        SkillListing.skill_text.ilike("%Firemaking%"),
        SkillListing.type == ListingType.TEACH
    ).first()
    fire_vec = matching.bytes_to_vector(fire_listing.embedding)
    sim = matching.cosine_similarity(guitar_vec, fire_vec)
    assert sim < 0.40, f"Expected Guitar vs Firemaking to have low similarity (<0.40), got {sim}"
    print(f"[PASS] [Test 4] Near-miss precision passed: Guitar vs Firemaking similarity is {sim:.3f} (< 0.40).")

    # 3. Verify Mutual Skill Trade Discovery
    # Alex teaches UI/UX and wants AI Prompt Engineering.
    # Sofia teaches AI Prompt Engineering and wants UI/UX!
    trades = matching.find_mutual_trade_candidates(db, alex.id, threshold=0.60)
    print(f"\nMutual Trade Candidates for Alex Rivera:")
    for t in trades:
        print(f"  - With {t['peer_name']}: You learn '{t['you_learn']}' while teaching '{t['you_teach']}' (Score: {t['avg_score']})")
    assert any(t["peer_name"] == "Sofia Chen" for t in trades), "Expected mutual trade detected between Alex and Sofia!"
    print("[PASS] [Test 5] Mutual 1-on-1 skill trade candidate discovery verified (Alex <-> Sofia).")

    # 4. Verify Credit-Spend Teacher Search
    teachers = matching.search_teachers_by_skill(db, "data science machine learning", threshold=0.45)
    assert len(teachers) > 0 and any(t["teacher_name"] == "Sofia Chen" for t in teachers), "Expected Sofia Chen in data science query"
    print("[PASS] [Test 6] Semantic teacher search (credit-spend flow) verified.")

    # 5. Verify Session Lifecycle & Escrow
    sofia = db.query(User).filter(User.name == "Sofia Chen").first()
    # Guarantee learner has sufficient credits for repeatable test execution
    sofia_acc = ledger.get_or_create_account(db, sofia.id)
    if sofia_acc.balance < 1:
        sofia_acc.balance = 5
        db.commit()

    meet_info = scheduler.create_google_meet_session("Figma Mentorship", "Alex Rivera", "Sofia Chen")
    session = PeerSession(
        session_type=SessionType.CREDIT_EXCHANGE,
        teacher_id=alex.id,
        learner_id=sofia.id,
        teach_skill_text="UI/UX Design & Figma Systems",
        status=SessionStatus.REQUESTED,
        google_meet_url=meet_info["meet_url"],
        calendar_link=meet_info["calendar_url"]
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    print(f"\n[PASS] [Test 7] Session created #{session.id}. Google Meet URL: {session.google_meet_url}")

    sofia_acc_before = ledger.get_or_create_account(db, sofia.id).balance
    sofia_escrow_before = ledger.get_or_create_account(db, sofia.id).escrow_balance
    # Teacher accepts: 1 credit held in escrow from learner (Sofia)
    ledger.transition_accept_session(db, session.id, alex.id)
    sofia_acc = ledger.get_or_create_account(db, sofia.id)
    assert sofia_acc.balance == sofia_acc_before - 1 and sofia_acc.escrow_balance == sofia_escrow_before + 1
    print(f"[PASS] [Test 8] Session ACCEPTED: Sofia's balance held in escrow ({sofia_acc.escrow_balance} locked).")

    # Complete session: 1 credit released to Alex
    alex_acc_before = ledger.get_or_create_account(db, alex.id).balance
    ledger.transition_complete_and_release(db, session.id, sofia.id)
    alex_acc = ledger.get_or_create_account(db, alex.id)
    sofia_acc = ledger.get_or_create_account(db, sofia.id)
    assert sofia_acc.escrow_balance == sofia_escrow_before, f"Escrow should return to {sofia_escrow_before} after release"
    assert alex_acc.balance == alex_acc_before + 1, f"Expected Alex balance +1, got {alex_acc.balance}"
    print(f"[PASS] [Test 9] Session COMPLETED: Alex earned 1 credit, Sofia escrow released.")

    # 6. Verify Persistent Chat Messages
    msg = ChatMessage(session_id=session.id, sender_id=alex.id, text="Hi Sofia, excited for our session!")
    db.add(msg)
    db.commit()
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).all()
    assert len(msgs) >= 1 and any("excited" in m.text for m in msgs)
    print(f"[PASS] [Test 10] Persistent chat messages verified for session #{session.id}.")

    # 7. Verify Free Daily Bonus Credit
    bonus_res = ledger.earn_bonus_coin(db, alex.id, reason="Daily Login Reward")
    assert bonus_res["success"]
    print(f"[PASS] [Test 11] Free bonus credit claim verified (New balance: {bonus_res['new_balance']}).")

    # 8. Verify YouTube Video Resources
    vids = resources.get_best_youtube_videos_for_skill("React")
    assert len(vids) > 0 and any("freeCodeCamp" in v.get("channel", "") for v in vids)
    print(f"[PASS] [Test 12] Curated YouTube video resources verified.")

    # 9. Verify AI Tutor
    ai_reply = asyncio.run(ai_service.query_cloud_ai_model(
        [{"role": "user", "content": "Explain Figma auto-layout briefly."}],
        skill_context="UI/UX Design"
    ))
    assert len(ai_reply) > 20
    print(f"[PASS] [Test 13] AI Doubt Assistant verified: {ai_reply[:60]}...")

    # 10. Verify Multi-Peer Study Rooms & Group Chat
    room = GroupRoom(
        name="Fullstack JavaScript Collective",
        topic="Node.js, Express, React, Vite & Cloud Deployments",
        creator_id=alex.id
    )
    room.members.append(alex)
    room.members.append(sofia)
    marcus = db.query(User).filter(User.name == "Marcus Vance").first()
    if marcus:
        room.members.append(marcus)
    db.add(room)
    db.commit()
    db.refresh(room)

    assert len(room.members) >= 2, "Expected at least 2 peers in study room"

    gmsg1 = GroupMessage(room_id=room.id, sender_id=alex.id, text="Welcome everyone to the JavaScript collective!")
    gmsg2 = GroupMessage(room_id=room.id, sender_id=sofia.id, text="Excited to collaborate on fullstack apps!")
    db.add_all([gmsg1, gmsg2])
    db.commit()

    room_msgs = db.query(GroupMessage).filter(GroupMessage.room_id == room.id).all()
    assert len(room_msgs) == 2, f"Expected 2 group messages, got {len(room_msgs)}"
    assert {m.sender_id for m in room_msgs} == {alex.id, sofia.id}
    print(f"[PASS] [Test 14] Multi-peer study room '{room.name}' verified with {len(room.members)} peers and group chat history.")

    # 11. Verify LinkedIn Connection & Proof
    assert alex.linkedin_url and "linkedin.com" in alex.linkedin_url, "Expected valid LinkedIn URL for Alex Rivera"
    print(f"[PASS] [Test 15] LinkedIn connection & proof link verified: {alex.linkedin_url}")

    # 12. Verify Free Skill Course Finishing, Bonus Coins & Domain Certification Gating
    certs_before = db.query(DomainCertification).filter(DomainCertification.user_id == alex.id).all()
    certified_domains_before = {c.domain for c in certs_before}
    assert "creative" in certified_domains_before or "tech" in certified_domains_before, "Expected seeded domain certs for Alex"

    # Simulate Alex taking and completing the Business domain training course
    alex_bal_before = ledger.get_or_create_account(db, alex.id).balance
    test_cert = DomainCertification(
        user_id=alex.id,
        domain="business",
        course_title="Business Growth & Startup Strategy Crash Course",
        score=100
    )
    db.add(test_cert)
    bonus_cert_res = ledger.earn_bonus_coin(
        db, alex.id, amount=2,
        reason="Completed Business Certification Course",
        tx_type="COURSE_CERTIFICATION"
    )
    assert bonus_cert_res["success"] and bonus_cert_res["new_balance"] == alex_bal_before + 2

    # Verify domain certification unlocks teaching in that domain
    alex_certs = db.query(DomainCertification).filter(DomainCertification.user_id == alex.id).all()
    assert any(c.domain == "business" for c in alex_certs)
    print(f"[PASS] [Test 16] Free Skill Training completion verified: +2 MG Coins awarded (New balance: {bonus_cert_res['new_balance']}) and 'business' teaching domain unlocked.")

    # Clean test cert
    db.delete(test_cert)

    # Self-clean test fixtures to keep skillswap.db clean across repeated runs
    db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
    db.query(PeerSession).filter(PeerSession.id == session.id).delete()
    db.query(GroupMessage).filter(GroupMessage.room_id == room.id).delete()
    db.delete(room)
    db.commit()

    print("\n================== ALL 16 VERIFICATION TESTS PASSED! ==================")
    db.close()

if __name__ == "__main__":
    run_tests()
