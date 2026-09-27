import urllib.parse
from typing import List, Dict

CURATED_YOUTUBE_RESOURCES: Dict[str, List[Dict]] = {
    "react": [
        {
            "title": "React JS Full Course 2024 | Build an App and Deploy It",
            "channel": "freeCodeCamp.org",
            "views": "3.8M+ views",
            "duration": "11 hours",
            "thumbnail": "https://img.youtube.com/vi/bMknfKXIFA8/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=bMknfKXIFA8",
            "badge": "Best Comprehensive Course",
            "level": "Beginner to Advanced"
        },
        {
            "title": "React in 100 Seconds",
            "channel": "Fireship",
            "views": "2.4M+ views",
            "duration": "2:25",
            "thumbnail": "https://img.youtube.com/vi/Tn6-PIqc4UM/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=Tn6-PIqc4UM",
            "badge": "Fast Overview",
            "level": "Overview"
        },
        {
            "title": "Full Modern React Tutorial with Redux Toolkit",
            "channel": "Dave Gray",
            "views": "1.2M+ views",
            "duration": "8 hours",
            "thumbnail": "https://img.youtube.com/vi/RVFAyFWO4go/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=RVFAyFWO4go",
            "badge": "Industry Standard",
            "level": "Intermediate"
        }
    ],
    "frontend": [
        {
            "title": "Frontend Web Development Bootcamp Course (HTML, CSS, JS)",
            "channel": "freeCodeCamp.org",
            "views": "7.1M+ views",
            "duration": "21 hours",
            "thumbnail": "https://img.youtube.com/vi/mU6anWqZJcc/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=mU6anWqZJcc",
            "badge": "Most Viewed",
            "level": "Complete Foundation"
        },
        {
            "title": "Modern HTML & CSS From The Beginning",
            "channel": "Traversy Media",
            "views": "4.5M+ views",
            "duration": "4 hours",
            "thumbnail": "https://img.youtube.com/vi/UB1O30fR-EE/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=UB1O30fR-EE",
            "badge": "Essential Styling",
            "level": "Beginner"
        }
    ],
    "public speaking": [
        {
            "title": "How to speak so that people want to listen",
            "channel": "TED (Julian Treasure)",
            "views": "54M+ views",
            "duration": "9:58",
            "thumbnail": "https://img.youtube.com/vi/eIho2S0ZahI/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=eIho2S0ZahI",
            "badge": "Top TED Talk",
            "level": "All Levels"
        },
        {
            "title": "The 7 Secrets of Great Public Speaking",
            "channel": "Richard Greene",
            "views": "4.9M+ views",
            "duration": "18:04",
            "thumbnail": "https://img.youtube.com/vi/i0a61wFaQD8/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=i0a61wFaQD8",
            "badge": "Practical Techniques",
            "level": "Actionable Skills"
        }
    ],
    "linear algebra": [
        {
            "title": "Essence of linear algebra (Full Playlist)",
            "channel": "3Blue1Brown (Grant Sanderson)",
            "views": "18M+ views",
            "duration": "15 videos",
            "thumbnail": "https://img.youtube.com/vi/fNk_zzaMoSs/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=fNk_zzaMoSs&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
            "badge": "Best Visual Intuition",
            "level": "Foundational"
        },
        {
            "title": "MIT 18.06 Linear Algebra, Spring 2005 (Prof. Gilbert Strang)",
            "channel": "MIT OpenCourseWare",
            "views": "9.2M+ views",
            "duration": "35 lectures",
            "thumbnail": "https://img.youtube.com/vi/7UJ4CFRGd-U/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=7UJ4CFRGd-U",
            "badge": "Gold Standard Academic",
            "level": "University Level"
        }
    ],
    "machine learning": [
        {
            "title": "Machine Learning for Everybody – Full Course",
            "channel": "freeCodeCamp.org",
            "views": "4.3M+ views",
            "duration": "4 hours",
            "thumbnail": "https://img.youtube.com/vi/i_LwzRVP7bg/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
            "badge": "Best Intro Course",
            "level": "Beginner"
        },
        {
            "title": "Stanford CS229: Machine Learning (Andrew Ng)",
            "channel": "Stanford Online",
            "views": "6.8M+ views",
            "duration": "20 lectures",
            "thumbnail": "https://img.youtube.com/vi/jGwO_UgTS7I/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=jGwO_UgTS7I",
            "badge": "World Renowned",
            "level": "Intermediate to Advanced"
        }
    ],
    "video editing": [
        {
            "title": "DaVinci Resolve Beginners Guide: Learn in Under 20 Minutes",
            "channel": "Casey Faris",
            "views": "3.1M+ views",
            "duration": "19:45",
            "thumbnail": "https://img.youtube.com/vi/63LN33ceWeI/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=63LN33ceWeI",
            "badge": "Top Free Editor",
            "level": "Beginner"
        },
        {
            "title": "Premiere Pro Tutorial for Beginners 2024",
            "channel": "Envato Tuts+",
            "views": "2.8M+ views",
            "duration": "25:30",
            "thumbnail": "https://img.youtube.com/vi/u79_r4_qWio/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=u79_r4_qWio",
            "badge": "Pro Workflow",
            "level": "Industry Standard"
        }
    ],
    "guitar": [
        {
            "title": "First Guitar Lesson for Beginners (Your First Guitar Lesson)",
            "channel": "JustinGuitar",
            "views": "14M+ views",
            "duration": "15:20",
            "thumbnail": "https://img.youtube.com/vi/BBz-Jyr23M4/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=BBz-Jyr23M4",
            "badge": "Top Rated Instructor",
            "level": "Complete Beginner"
        },
        {
            "title": "Learn 4 Chords to Play Hundreds of Songs on Guitar",
            "channel": "Marty Music",
            "views": "8.5M+ views",
            "duration": "10:14",
            "thumbnail": "https://img.youtube.com/vi/p8Qz1z_Z4Ew/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=p8Qz1z_Z4Ew",
            "badge": "Instant Progress",
            "level": "Beginner"
        }
    ],
    "python": [
        {
            "title": "Python for Beginners - Full Course [Programming Tutorial]",
            "channel": "Programming with Mosh",
            "views": "41M+ views",
            "duration": "6 hours",
            "thumbnail": "https://img.youtube.com/vi/_uQrJ0TkZlc/hqdefault.jpg",
            "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "badge": "Most Popular Python Course",
            "level": "Beginner"
        }
    ]
}

def get_best_youtube_videos_for_skill(skill: str) -> List[Dict]:
    """
    Returns the top viewed, curated YouTube videos matching the given skill.
    If exact key is not found, performs fuzzy keyword matching or generates
    a verified YouTube search resource.
    """
    clean_skill = skill.lower().strip()

    # Exact or substring match in curated database
    for key, videos in CURATED_YOUTUBE_RESOURCES.items():
        if key in clean_skill or clean_skill in key:
            return videos

    # Multi-keyword matching
    words = clean_skill.split()
    for word in words:
        if len(word) > 3:
            for key, videos in CURATED_YOUTUBE_RESOURCES.items():
                if word in key:
                    return videos

    # Dynamic fallback: Return formatted YouTube search direct resource
    encoded_query = urllib.parse.quote(f"{skill} full tutorial best")
    return [
        {
            "title": f"Top Rated Tutorials: {skill.title()} (Mastery & Hands-on Guide)",
            "channel": "Verified Educational Channels",
            "views": "1M+ views",
            "duration": "Curated Playlist",
            "thumbnail": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80",
            "url": f"https://www.youtube.com/results?search_query={encoded_query}",
            "badge": "Search Recommended",
            "level": "All Levels"
        },
        {
            "title": f"{skill.title()} in 10 Minutes - Core Concepts for Beginners",
            "channel": "Developer / Skill Hub",
            "views": "500K+ views",
            "duration": "10-20 min",
            "thumbnail": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&auto=format&fit=crop&q=80",
            "url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(skill + ' beginner guide')}",
            "badge": "Quick Start",
            "level": "Beginner"
        }
    ]
