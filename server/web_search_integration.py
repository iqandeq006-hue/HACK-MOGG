import re
import json
import urllib.parse
from typing import List, Dict, Optional
import httpx

from resources import get_best_youtube_videos_for_skill

YOUTUBE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def search_youtube_live(query: str, limit: int = 6) -> List[Dict]:
    """
    Performs live search on YouTube, extracting video titles, channels, view counts,
    thumbnails, and URLs directly from YouTube search results without requiring an API key.
    """
    encoded = urllib.parse.quote(query.strip())
    url = f"https://www.youtube.com/results?search_query={encoded}"

    results = []
    try:
        with httpx.Client(timeout=8.0, headers=YOUTUBE_HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                # Extract ytInitialData json payload
                match = re.search(r'var ytInitialData = ({.*?});</script>', resp.text)
                if match:
                    data = json.loads(match.group(1))
                    sections = data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", [])
                    for sec in sections:
                        items = sec.get("itemSectionRenderer", {}).get("contents", [])
                        for item in items:
                            if "videoRenderer" in item:
                                vr = item["videoRenderer"]
                                vid_id = vr.get("videoId")
                                title = vr.get("title", {}).get("runs", [{}])[0].get("text", "Tutorial Video")
                                channel = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "Educational Channel")
                                views = vr.get("viewCountText", {}).get("simpleText", "High View Count")
                                length = vr.get("lengthText", {}).get("simpleText", "Video")

                                results.append({
                                    "title": title,
                                    "channel": channel,
                                    "views": views,
                                    "duration": length,
                                    "thumbnail": f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
                                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                                    "badge": "Live YouTube Search",
                                    "level": "Self-paced"
                                })
                                if len(results) >= limit:
                                    break
                        if len(results) >= limit:
                            break
    except Exception as e:
        print(f"[YouTube Live Search Error] {e}")

    # If live search returned fewer results than limit, supplement with curated resources
    if len(results) < limit:
        curated = get_best_youtube_videos_for_skill(query)
        # Avoid duplicate URLs
        existing_urls = {r["url"] for r in results}
        for c in curated:
            if c["url"] not in existing_urls:
                results.append(c)
                existing_urls.add(c["url"])
            if len(results) >= limit:
                break

    return results

def search_web_articles_and_docs(query: str, limit: int = 5) -> List[Dict]:
    """
    Searches web documentation, cheat sheets, and articles for learning resources.
    Tries local SearXNG instance (from WEB/config.toml) first, falling back to curated
    and direct reference links.
    """
    clean_q = query.strip()
    encoded = urllib.parse.quote(clean_q)

    # 1. Try SearXNG instance (if running locally as per WEB/searxng)
    try:
        searx_url = f"http://localhost:8888/search?q={encoded}&format=json"
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(searx_url)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("results", [])[:limit]
                results = []
                for it in items:
                    results.append({
                        "title": it.get("title", clean_q.title()),
                        "url": it.get("url", ""),
                        "snippet": it.get("content", ""),
                        "source": it.get("engine", "Web Search")
                    })
                if results:
                    return results
    except Exception:
        pass

    # 2. Intelligent verified documentation & cheatsheet generator
    # For common programming and technical skills, provide authoritative docs
    q_lower = clean_q.lower()
    docs = []

    if "react" in q_lower:
        docs.extend([
            {
                "title": "React Official Documentation & Interactive Guide",
                "url": "https://react.dev/learn",
                "snippet": "Learn React from first principles with interactive sandboxes, hooks reference, and state management guides.",
                "source": "react.dev"
            },
            {
                "title": "React TypeScript Cheatsheet for Professional Engineers",
                "url": "https://react-typescript-cheatsheet.netlify.app/",
                "snippet": "Comprehensive reference for typing React components, hooks, synthetic events, and custom context.",
                "source": "react-typescript-cheatsheet"
            }
        ])

    if "python" in q_lower:
        docs.extend([
            {
                "title": "Official Python 3 Documentation & Tutorial",
                "url": "https://docs.python.org/3/tutorial/",
                "snippet": "The definitive tutorial covering data structures, modules, classes, and standard libraries.",
                "source": "python.org"
            }
        ])

    if "linear algebra" in q_lower or "math" in q_lower:
        docs.extend([
            {
                "title": "Linear Algebra Done Right — Concepts & Reference Notes",
                "url": "https://linear.axler.net/",
                "snippet": "Focuses on linear operators on vector spaces rather than dry matrix manipulation.",
                "source": "linear.axler.net"
            }
        ])

    # Universal search fallbacks
    docs.append({
        "title": f"{clean_q.title()} Complete Roadmap & Study Guide",
        "url": f"https://roadmap.sh/search?q={encoded}",
        "snippet": f"Visual, step-by-step developer roadmap and skill milestones for mastering {clean_q}.",
        "source": "roadmap.sh"
    })
    docs.append({
        "title": f"DevDocs Reference: {clean_q.title()} API & Quick Guide",
        "url": f"https://devdocs.io/#q={encoded}",
        "snippet": f"Fast, searchable, mobile-friendly documentation and cheat sheet index for {clean_q}.",
        "source": "devdocs.io"
    })

    return docs[:limit]

def get_skill_learning_hub(skill: str) -> Dict:
    """
    Unified learning resource hub combining live YouTube search and web articles.
    """
    youtube_videos = search_youtube_live(skill, limit=5)
    web_articles = search_web_articles_and_docs(skill, limit=4)

    return {
        "skill": skill,
        "youtube_videos": youtube_videos,
        "web_articles": web_articles,
        "total_resources": len(youtube_videos) + len(web_articles)
    }
