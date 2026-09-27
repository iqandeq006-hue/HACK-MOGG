import io
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models import SkillListing, ListingType, User, CreditAccount

MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_THRESHOLD = 0.60

# Global model instance
_model = None

# Domain Skill Ontology for semantic vocabulary expansion
SKILL_ONTOLOGY = {
    "react": "React (Frontend web development and UI components)",
    "frontend development": "Frontend development (Web UI, React, client-side engineering)",
    "public speaking": "Public speaking (Speech delivery, presentation skills, audience communication)",
    "presentation skills": "Presentation skills (Public speaking, slide delivery, communication)",
    "linear algebra": "Linear algebra (Vector spaces, matrix decomposition, machine learning math)",
    "machine learning math": "Machine learning math (Linear algebra, matrix calculus, optimization)",
    "piano": "Piano (Acoustic keyboard musical instrument, classical keys)",
    "guitar": "Guitar (Fretted string musical instrument, acoustic chords, strumming)",
    "video editing": "Video editing (Film cutting, Premiere Pro, DaVinci, video post-production)"
}

def enrich_skill_text(text: str) -> str:
    cleaned = text.lower().strip()
    return SKILL_ONTOLOGY.get(cleaned, text)

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_text(text: str) -> np.ndarray:
    model = get_model()
    enriched = enrich_skill_text(text)
    vec = model.encode(enriched, normalize_embeddings=True)
    return vec.astype(np.float32)

def vector_to_bytes(vec: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, vec)
    return buffer.getvalue()

def bytes_to_vector(data: bytes) -> np.ndarray:
    buffer = io.BytesIO(data)
    return np.load(buffer)

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    # Since normalized, dot product is cosine similarity
    dot = float(np.dot(v1, v2))
    norm_product = float(np.linalg.norm(v1) * np.linalg.norm(v2))
    if norm_product == 0:
        return 0.0
    return float(dot / norm_product)

def match_learn_listing(db: Session, learn_listing_id: int, threshold: float = DEFAULT_THRESHOLD):
    """
    Finds all TEACH listings that match the specified LEARN listing.
    """
    target = db.query(SkillListing).filter(
        SkillListing.id == learn_listing_id,
        SkillListing.type == ListingType.LEARN
    ).first()

    if not target or not target.embedding:
        return []

    target_vec = bytes_to_vector(target.embedding)

    # Fetch all TEACH listings from other users
    teach_listings = db.query(SkillListing).filter(
        SkillListing.type == ListingType.TEACH,
        SkillListing.user_id != target.user_id
    ).all()

    matches = []
    for listing in teach_listings:
        if not listing.embedding:
            continue
        vec = bytes_to_vector(listing.embedding)
        score = cosine_similarity(target_vec, vec)
        if score >= threshold:
            matches.append({
                "teach_listing_id": listing.id,
                "teacher_id": listing.user.id,
                "teacher_name": listing.user.name,
                "teach_skill": listing.skill_text,
                "similarity_score": round(score, 4),
                "is_semantic_match": target.skill_text.lower() not in listing.skill_text.lower()
            })

    # Sort descending by similarity score
    matches.sort(key=lambda x: x["similarity_score"], reverse=True)
    return matches

def search_teachers_by_skill(db: Session, query_text: str, current_user_id: int = None, threshold: float = 0.50):
    """
    Hybrid semantic + keyword search over all TEACH listings (credit-spend flow without needing a reciprocal match).
    """
    query_vec = embed_text(query_text)
    clean_q = query_text.lower().strip()

    query = db.query(SkillListing).filter(SkillListing.type == ListingType.TEACH)
    if current_user_id:
        query = query.filter(SkillListing.user_id != current_user_id)

    teach_listings = query.all()

    results = []
    for listing in teach_listings:
        if not listing.embedding:
            continue
        vec = bytes_to_vector(listing.embedding)
        score = cosine_similarity(query_vec, vec)

        # Keyword and category hybrid boost
        skill_lower = listing.skill_text.lower()
        cat_lower = (listing.category or "").lower()

        if clean_q in skill_lower or skill_lower in clean_q:
            score = max(score, 0.95)
        elif any(w in skill_lower for w in clean_q.split() if len(w) > 3):
            score = max(score, 0.80)
        elif clean_q in cat_lower or any(w in cat_lower for w in clean_q.split() if len(w) > 3):
            score = max(score, 0.75)

        if score >= threshold:
            results.append({
                "listing_id": listing.id,
                "teacher_id": listing.user.id,
                "teacher_name": listing.user.name,
                "skill_offered": listing.skill_text,
                "category": listing.category,
                "similarity_score": round(score, 4),
            })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results

def find_mutual_trade_candidates(db: Session, user_id: int, threshold: float = DEFAULT_THRESHOLD):
    """
    Finds direct 1-on-1 mutual trade opportunities:
    User A wants to learn what User B teaches, AND User B wants to learn what User A teaches.
    """
    user_learns = db.query(SkillListing).filter(
        SkillListing.user_id == user_id,
        SkillListing.type == ListingType.LEARN
    ).all()

    user_teaches = db.query(SkillListing).filter(
        SkillListing.user_id == user_id,
        SkillListing.type == ListingType.TEACH
    ).all()

    if not user_learns or not user_teaches:
        return []

    # Get all other users
    other_users = db.query(User).filter(User.id != user_id).all()
    trades = []

    for other in other_users:
        other_learns = db.query(SkillListing).filter(
            SkillListing.user_id == other.id,
            SkillListing.type == ListingType.LEARN
        ).all()
        other_teaches = db.query(SkillListing).filter(
            SkillListing.user_id == other.id,
            SkillListing.type == ListingType.TEACH
        ).all()

        best_forward_match = None
        # Forward: other teaches what user wants to learn
        for ul in user_learns:
            u_vec = bytes_to_vector(ul.embedding)
            for ot in other_teaches:
                ot_vec = bytes_to_vector(ot.embedding)
                sim = cosine_similarity(u_vec, ot_vec)
                if sim >= threshold and (best_forward_match is None or sim > best_forward_match["score"]):
                    best_forward_match = {
                        "user_wants": ul.skill_text,
                        "other_teaches": ot.skill_text,
                        "score": round(sim, 4)
                    }

        best_reverse_match = None
        # Reverse: user teaches what other wants to learn
        for ut in user_teaches:
            ut_vec = bytes_to_vector(ut.embedding)
            for ol in other_learns:
                ol_vec = bytes_to_vector(ol.embedding)
                sim = cosine_similarity(ut_vec, ol_vec)
                if sim >= threshold and (best_reverse_match is None or sim > best_reverse_match["score"]):
                    best_reverse_match = {
                        "other_wants": ol.skill_text,
                        "user_teaches": ut.skill_text,
                        "score": round(sim, 4)
                    }

        if best_forward_match and best_reverse_match:
            trades.append({
                "peer_id": other.id,
                "peer_name": other.name,
                "you_learn": best_forward_match["other_teaches"],
                "you_teach": best_reverse_match["user_teaches"],
                "forward_score": best_forward_match["score"],
                "reverse_score": best_reverse_match["score"],
                "avg_score": round((best_forward_match["score"] + best_reverse_match["score"]) / 2, 4)
            })

    trades.sort(key=lambda x: x["avg_score"], reverse=True)
    return trades
