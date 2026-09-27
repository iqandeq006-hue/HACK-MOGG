import os
import httpx
from typing import List, Dict, Optional

# Supported providers: Groq, OpenRouter, Together, HuggingFace Inference
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter" if OPENROUTER_API_KEY else ("groq" if GROQ_API_KEY else "local"))

SYSTEM_PROMPT = """You are SkillBot, an expert AI Peer Learning Mentor and Skill Exchange Assistant for the SkillSwap platform.
Your mission is to:
1. Clarify doubts in any technical, creative, or academic subject (programming, math, speech, music, design, etc.).
2. Break down complex concepts into step-by-step, intuitive explanations.
3. Suggest learning roadmaps and practice exercises students can prepare before peer tutoring sessions.
4. Help students formulate what they want to teach or learn to get better peer matches.
Keep your answers engaging, encouraging, clear, and actionable. Use markdown formatting with bullet points and code blocks where helpful.
"""

async def query_cloud_ai_model(messages: List[Dict[str, str]], skill_context: Optional[str] = None) -> str:
    """
    Connects to an open-source cloud AI model (Llama-3, Mistral, DeepSeek) via Groq or OpenRouter.
    Falls back gracefully to the built-in intelligent peer-tutor engine if no API key is provided.
    """
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if skill_context:
        api_messages.append({
            "role": "system",
            "content": f"The student is currently inquiring in the context of the skill: '{skill_context}'."
        })
    api_messages.extend(messages)

    # 1. Try Groq (Ultra-fast open-source Llama 3 / Mixtral inference)
    if GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": api_messages,
                        "temperature": 0.7,
                        "max_tokens": 1024
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Groq AI Error] {e}")

    # 2. Try OpenRouter (Connects to DeepSeek, Llama 3, Mistral, Qwen)
    if OPENROUTER_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "HTTP-Referer": "https://skillswap.edu",
                        "X-Title": "SkillSwap AI"
                    },
                    json={
                        "model": "meta-llama/llama-3.3-70b-instruct:free",
                        "messages": api_messages,
                        "temperature": 0.7,
                        "max_tokens": 1024
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[OpenRouter AI Error] {e}")

    # 3. Intelligent Built-in Peer Learning Tutor (Zero-dependency fallback)
    last_user_msg = messages[-1]["content"] if messages else ""
    return generate_local_tutor_response(last_user_msg, skill_context)

def generate_local_tutor_response(user_query: str, skill_context: Optional[str] = None) -> str:
    """
    Intelligent built-in AI tutor response generator for offline and demo environments.
    """
    q = user_query.lower()
    ctx = (skill_context or "").lower()

    if "react" in q or "react" in ctx:
        return (
            "### ⚛️ Master React: Concept & Practice\n\n"
            "**Core mental model:** React is fundamentally a function of state: `UI = f(State)`.\n\n"
            "**Key areas to review before your peer session:**\n"
            "- **Components & Props:** Pure functions that accept inputs and return JSX elements.\n"
            "- **`useState`:** Triggers a re-render whenever state updates. Remember state updates are asynchronous.\n"
            "- **`useEffect`:** Handles side effects (data fetching, DOM subscriptions). Be careful with dependency arrays.\n"
            "- **Component Composition:** Break larger UIs into reusable children rather than prop-drilling.\n\n"
            "💡 **Exercise for your peer:** Try building a simple counter with an undo/redo stack, or fetch GitHub user profiles using `useEffect`!"
        )

    if "linear algebra" in q or "math" in q or "linear algebra" in ctx:
        return (
            "### 📐 Linear Algebra: Intuition & Application\n\n"
            "**Key mental model:** Think of matrices not as tables of numbers, but as **geometric transformations of coordinate space**.\n\n"
            "- **Eigenvalues & Eigenvectors:** Vectors that do not change direction during a transformation; they only get scaled by $\\lambda$.\n"
            "- **Dot Product:** Measures directional alignment and projection ($A \\cdot B = ||A|| \\, ||B|| \\cos \\theta$).\n"
            "- **Matrix Multiplication:** Composition of multiple geometric transformations applied sequentially.\n\n"
            "🎯 **Peer Practice Idea:** Plot 2D vectors $(1, 0)$ and $(0, 1)$, then apply a shear or rotation matrix together to visualize the determinant as the scaling of area!"
        )

    if "speaking" in q or "presentation" in q:
        return (
            "### 🎤 Public Speaking & Presentation Mastery\n\n"
            "**The 3 pillars of an impactful presentation:**\n"
            "1. **Content Structure (What you say):** Use the *Hook $\\to$ Conflict $\\to$ Resolution* narrative arc. Limit slides to 1 main idea.\n"
            "2. **Vocal Delivery (How you sound):** Master the intentional pause. Silence builds anticipation and allows your peer to process key points.\n"
            "3. **Physical Presence (How you look):** Open posture, steady eye contact, and purposeful hand gestures above the waist.\n\n"
            "⏱️ **Quick Session Drill:** Do a 2-minute impromptu pitch on a topic given by your peer, focusing on eliminating filler words ('um', 'like', 'you know')."
        )

    return (
        f"### 💡 SkillSwap Peer Tutor: Guidance\n\n"
        f"Great question regarding **{skill_context.title() if skill_context else 'your learning goal'}**!\n\n"
        f"Here is a recommended approach for your upcoming peer session:\n\n"
        f"1. **Clarify the Core Objective:** Define exactly what you want to achieve in the next 45 minutes (e.g., build 1 feature, understand 1 proof, or practice 1 technique).\n"
        f"2. **Active Recall & Feynman Technique:** Explain the concept in simple terms back to your peer without checking your notes.\n"
        f"3. **Hands-On Application:** Ensure at least 60% of the session is spent live-coding, solving problems, or doing roleplay exercises.\n\n"
        f"*Feel free to ask me for specific code snippets, study checklists, or interview practice questions!*"
    )
