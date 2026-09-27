from database import engine, SessionLocal, Base
from models import (
    User, SkillListing, ListingType, CreditAccount, CreditTransaction,
    TransactionType, PeerSession, SessionType, SessionStatus, ChatMessage,
    GroupRoom, GroupMessage, DomainCertification
)
from matching import embed_text, vector_to_bytes

# ─────────────────────────────────────────────────────────
# 15 MOGG Community Users — ported from MOGG-main frontend
# Each has 6 TEACH skills + 1 LEARN goal across 6 domains:
# tech, creative, soft, survival, languages, business
# ─────────────────────────────────────────────────────────
SEED_USERS = [
    {
        "name": "Alex Rivera",
        "email": "alex@mogg.io",
        "credits": 5,
        "bio": "Senior product designer passionate about clean interfaces, brand strategy, and frontend development.",
        "teach": [
            ("UI/UX Design & Figma Systems", "creative", "Free Peer Exchange", "Wireframing, auto-layout, design tokens, and interactive prototyping in Figma."),
            ("Fullstack Web App with React & Vite", "tech", "⚡ 1 Credit / Session", "Modern React hooks, component design, state management, and deployment."),
            ("Motion Graphics & After Effects", "creative", "Free Peer Exchange", "Keyframe animation, UI motion design, and vector logo animation."),
            ("Brand Strategy & Visual Positioning", "business", "⚡ 1 Credit / Session", "Create compelling brand identities, color theory, and logo systems."),
            ("Conversational Spanish Basics", "languages", "Free Peer Exchange", "Practical daily Spanish conversation and travel vocabulary."),
            ("Mindful Leadership & Team Motivation", "soft", "Free Peer Exchange", "Fostering psychological safety and active motivation within creative product teams."),
        ],
        "learn": [
            ("AI Prompt Engineering & Agents", "tech", "Free Peer Exchange", "Want to learn autonomous agent loops and tool calling in Python."),
        ]
    },
    {
        "name": "Sofia Chen",
        "email": "sofia@mogg.io",
        "credits": 4,
        "bio": "AI researcher & developer. Happy to teach Python coding, data analytics, and Mandarin!",
        "teach": [
            ("Python for Data Science & ML", "tech", "Free Peer Exchange", "Pandas data cleaning, NumPy array manipulation, and Scikit-Learn models."),
            ("AI Prompt Engineering & Agents", "tech", "⚡ 1 Credit / Session", "Autonomous AI agents, tool calling loops, and structured LLM prompt architecture."),
            ("SQL & PostgreSQL Database Tuning", "tech", "Free Peer Exchange", "Relational queries, index optimization, complex joins, and schema design."),
            ("Business Analytics & Dashboards", "business", "⚡ 1 Credit / Session", "Turn raw datasets into executive KPI dashboards and analytical reports."),
            ("Mandarin Chinese Pinyin & Dialogue", "languages", "Free Peer Exchange", "Pronunciation, tone practice, and essential conversational Mandarin."),
            ("Data-Driven Decision Making", "soft", "Free Peer Exchange", "Structuring analytical arguments and removing cognitive bias in business choices."),
        ],
        "learn": [
            ("UI/UX Design & Figma Systems", "creative", "Free Peer Exchange", "Eager to learn user interface design principles to polish my AI web apps."),
        ]
    },
    {
        "name": "Marcus Vance",
        "email": "marcus@mogg.io",
        "credits": 6,
        "bio": "Indie musician & outdoor survival enthusiast. Trading guitar lessons, survival skills, and audio production!",
        "teach": [
            ("Guitar Basics & Music Theory", "creative", "⚡ 1 Credit / Session", "Acoustic and electric guitar fundamentals, chord progressions, and fingerpicking."),
            ("Emergency Shelter & Firemaking", "survival", "Free Peer Exchange", "Outdoor survival: friction fire starting, tarp shelters, and wilderness knot tying."),
            ("Audio Production & Ableton Mixing", "creative", "⚡ 1 Credit / Session", "Beat making, vocal tuning, EQ equalization, and track mastering."),
            ("Wilderness First Aid & CPR", "survival", "Free Peer Exchange", "Field trauma triage, wound management, CPR techniques, and emergency response."),
            ("Creative Songwriting & Composition", "creative", "⚡ 1 Credit / Session", "Lyric writing, melodic structure, verse-chorus arrangement, and key changes."),
            ("Creative Problem Solving Under Pressure", "soft", "Free Peer Exchange", "Improv techniques and calm mental pivoting when high-stakes projects derail."),
        ],
        "learn": [
            ("High-Stakes Negotiation & Persuasion", "soft", "Free Peer Exchange", "Looking to improve contract negotiation skills for record deals."),
        ]
    },
    {
        "name": "Elena Rostova",
        "email": "elena@mogg.io",
        "credits": 3,
        "bio": "Polyglot and communications coach eager to trade language fluency and speaking skills for coding.",
        "teach": [
            ("Conversational Spanish & Russian", "languages", "Free Peer Exchange", "Immersive vocabulary, pronunciation refinement, and conversational fluency drills."),
            ("Executive Public Speaking & Pitching", "soft", "⚡ 1 Credit / Session", "Overcome presentation anxiety, refine posture, and deliver memorable keynote speeches."),
            ("Persuasive Business Writing", "soft", "Free Peer Exchange", "Craft compelling emails, proposals, speeches, and persuasive copy."),
            ("Cross-Cultural Communication", "soft", "⚡ 1 Credit / Session", "Navigate global team dynamics, cultural nuances, and international etiquette."),
            ("French Basics & Daily Dialogue", "languages", "Free Peer Exchange", "French phonetics, greeting etiquette, travel phrases, and sentence building."),
            ("Vocal Control & Voice Acting", "creative", "Free Peer Exchange", "Vocal warmups, pitch resonance, tone modulation, and voiceover fundamentals."),
        ],
        "learn": [
            ("Fullstack Web App with React & Vite", "tech", "Free Peer Exchange", "Eager to learn web development to build my coaching platform."),
        ]
    },
    {
        "name": "David Kim",
        "email": "david@mogg.io",
        "credits": 5,
        "bio": "Cloud Security Engineer & outdoor survivalist. Teaching DevOps, cybersecurity, and Korean!",
        "teach": [
            ("Cybersecurity & Network Defense", "tech", "⚡ 1 Credit / Session", "Packet analysis, Wireshark, penetration testing basics, and firewall configuration."),
            ("Docker & Kubernetes Containerization", "tech", "Free Peer Exchange", "Dockerfile creation, container orchestration, microservices deployment, and Helm."),
            ("Cloud Architecture & AWS DevOps", "tech", "⚡ 1 Credit / Session", "AWS EC2, S3, Lambda serverless, Terraform infrastructure, and CI/CD pipelines."),
            ("Urban Navigation & Emergency Prep", "survival", "Free Peer Exchange", "Bug-out bag assembly, off-grid power banks, GPS mapping, and urban emergency strategy."),
            ("Korean Language & Hangul Basics", "languages", "Free Peer Exchange", "Read Hangul characters, basic phrases, and conversational Korean."),
            ("Cybersecurity Compliance & Auditing", "business", "⚡ 1 Credit / Session", "SOC2 frameworks, vulnerability disclosures, risk assessment, and security policy."),
        ],
        "learn": [
            ("Executive Public Speaking & Pitching", "soft", "Free Peer Exchange", "Want to improve technical presentation skills for tech conferences."),
        ]
    },
    {
        "name": "Priya Patel",
        "email": "priya@mogg.io",
        "credits": 4,
        "bio": "Venture consultant & executive coach. Offering business growth strategy, negotiation, and soft skills.",
        "teach": [
            ("High-Stakes Negotiation & Persuasion", "soft", "Free Peer Exchange", "Win-win negotiation frameworks, anchoring tactics, and objection handling."),
            ("Startup Pitch Deck Creation", "business", "⚡ 1 Credit / Session", "Structure pitch decks, financial projections, and investor Q&A preparation."),
            ("Digital Marketing & Growth Hacking", "business", "Free Peer Exchange", "Customer acquisition, PPC ads, funnel optimization, and viral campaign tactics."),
            ("Conflict Resolution & Team Coaching", "soft", "⚡ 1 Credit / Session", "De-escalating workplace friction, active mediation, and team trust building."),
            ("Emotional Intelligence & EQ Coaching", "soft", "Free Peer Exchange", "Self-regulation, empathy exercises, and stress management in high-pressure roles."),
            ("Hindi Conversational Fluency", "languages", "Free Peer Exchange", "Daily conversation, business etiquette, and cultural expressions in Hindi."),
        ],
        "learn": [
            ("Python for Data Science & ML", "tech", "Free Peer Exchange", "Looking to learn data analysis to back up marketing strategies."),
        ]
    },
    {
        "name": "Lucas Meyer",
        "email": "lucas@mogg.io",
        "credits": 6,
        "bio": "3D artist & photographer based in Berlin. Teaching Blender, digital illustration, and German!",
        "teach": [
            ("3D Modeling & Rendering in Blender", "creative", "⚡ 1 Credit / Session", "3D mesh modeling, texturing, lighting setups, and realistic Cycles rendering."),
            ("Digital Photography & Composition", "creative", "Free Peer Exchange", "Manual DSLR controls, exposure triangle, portrait lighting, and Lightroom editing."),
            ("Digital Illustration & Painting", "creative", "⚡ 1 Credit / Session", "Procreate and Photoshop brush techniques, color harmony, and character design."),
            ("Graphic Design & Typography", "creative", "Free Peer Exchange", "Poster design, font pairings, vector graphics, and print production."),
            ("German Conversation & Grammar", "languages", "Free Peer Exchange", "Conversational German, case system explanations, and daily vocabulary."),
            ("Web3 & Decentralized Apps", "tech", "⚡ 1 Credit / Session", "Smart contract basics, Ethereum wallet integration, and decentralized storage."),
        ],
        "learn": [
            ("Off-Grid Solar & Battery Setup", "survival", "Free Peer Exchange", "Want to learn basic electrical setups for camper van conversion."),
        ]
    },
    {
        "name": "Maya Lin",
        "email": "maya@mogg.io",
        "credits": 5,
        "bio": "Off-grid living specialist & engineer. Teaching solar energy, water filtration, and homesteading.",
        "teach": [
            ("Off-Grid Solar & Battery Setup", "survival", "Free Peer Exchange", "Solar panel wiring, charge controllers, inverter sizing, and lithium battery banks."),
            ("Bushcraft Water Purification", "survival", "⚡ 1 Credit / Session", "Sand filters, boiling, UV treatment, and natural water source testing."),
            ("Map & Compass Wilderness Orienteering", "survival", "Free Peer Exchange", "Topographic map navigation, declination adjustment, and triangulation."),
            ("Essential Outdoor Knot Tying", "survival", "Free Peer Exchange", "Mastering the bowline, trucker's hitch, taut-line, and lashings for shelters."),
            ("Basic Homesteading & Food Preservation", "survival", "⚡ 1 Credit / Session", "Canning, dehydration, fermenting vegetables, and urban garden planning."),
            ("Calm Mindset in Extreme Environments", "soft", "Free Peer Exchange", "Psychological resilience, breathwork, and panic reduction in survival scenarios."),
        ],
        "learn": [
            ("Digital Marketing & Growth Hacking", "business", "Free Peer Exchange", "Want to promote my sustainable homesteading workshops online."),
        ]
    },
    {
        "name": "Sarah Jenkins",
        "email": "sarah@mogg.io",
        "credits": 4,
        "bio": "E-commerce strategist & certified Scrum Master. Teaching SEO, Shopify, and personal finance.",
        "teach": [
            ("E-commerce Store Setup & Shopify", "business", "Free Peer Exchange", "Store creation, payment gateways, product catalog, and dropshipping logistics."),
            ("SEO Optimization & Content Strategy", "business", "⚡ 1 Credit / Session", "Keyword research, technical SEO audits, backlink strategy, and organic growth."),
            ("Agile Project Management & Scrum", "business", "Free Peer Exchange", "Sprint planning, Jira boards, standups, and retrospective facilitation."),
            ("Personal Finance & Budgeting", "business", "⚡ 1 Credit / Session", "Debt reduction strategies, index fund investing, and personal financial tracking."),
            ("Time Management & Deep Work", "soft", "Free Peer Exchange", "Pomodoro techniques, Notion workspace setup, and eliminating digital distractions."),
            ("Business English Masterclass", "languages", "Free Peer Exchange", "Professional vocabulary, corporate emailing, presentation tone, and idioms."),
        ],
        "learn": [
            ("Italian Language & Culture", "languages", "Free Peer Exchange", "Preparing for a summer trip to Italy and want basic conversational skills."),
        ]
    },
    {
        "name": "Carlos Mendez",
        "email": "carlos@mogg.io",
        "credits": 5,
        "bio": "Fullstack Mobile Architect. Teaching Flutter, Node.js APIs, Git workflows, and Italian!",
        "teach": [
            ("Mobile App Dev with Flutter & Dart", "tech", "⚡ 1 Credit / Session", "Cross-platform mobile apps, widget state management, and Firebase integration."),
            ("Backend API Engineering with Node.js", "tech", "Free Peer Exchange", "RESTful endpoints, Express framework, JWT authentication, and MongoDB."),
            ("Git & GitHub Team Collaboration", "tech", "Free Peer Exchange", "Branching strategies, pull requests, merge conflict resolution, and rebase."),
            ("Conversational Italian & Phrases", "languages", "Free Peer Exchange", "Italian pronunciation, common idioms, travel conversation, and culture."),
            ("Critical Thinking & Logic Frameworks", "soft", "⚡ 1 Credit / Session", "Mental models, cognitive bias identification, and structured problem solving."),
            ("Primitive Foraging & Plant ID", "survival", "Free Peer Exchange", "Identifying edible wild flora, toxic plants, and seasonal harvesting."),
        ],
        "learn": [
            ("Cybersecurity & Network Defense", "tech", "Free Peer Exchange", "Want to learn secure coding and vulnerability auditing for mobile apps."),
        ]
    },
    {
        "name": "Nina Patel",
        "email": "nina@mogg.io",
        "credits": 5,
        "bio": "Data Engineer & linguistics enthusiast. Teaching Airflow, Japanese basics, and HAM radio!",
        "teach": [
            ("Modern Data Pipelines & Airflow", "tech", "⚡ 1 Credit / Session", "ETL pipeline orchestration, Apache Airflow DAGs, and data warehousing."),
            ("Japanese Hiragana & Basic Dialogue", "languages", "Free Peer Exchange", "Hiragana writing, pronunciation, travel phrases, and cultural etiquette."),
            ("Active Listening & Empathetic Communication", "soft", "Free Peer Exchange", "Mastering deep listening, emotional validation, and feedback delivery."),
            ("Calligraphy & Lettering Art", "creative", "Free Peer Exchange", "Brush pen techniques, letter spacing, flourish design, and ink work."),
            ("Emergency Radio Communications & HAM", "survival", "⚡ 1 Credit / Session", "HAM radio basics, emergency frequencies, signal propagation, and antennas."),
            ("Financial Modeling & Unit Economics", "business", "Free Peer Exchange", "LTV/CAC calculation, financial forecasting, and cash flow projections."),
        ],
        "learn": [
            ("Digital Photography & Composition", "creative", "Free Peer Exchange", "Looking to capture better outdoor calligraphy work."),
        ]
    },
    {
        "name": "Liam O'Connor",
        "email": "liam@mogg.io",
        "credits": 4,
        "bio": "Wilderness guide & woodcrafter. Teaching cold weather survival, leather craft, and Gaelic!",
        "teach": [
            ("Cold Weather Survival & Snow Shelters", "survival", "Free Peer Exchange", "Building quinzees, hypothermia prevention, and sub-zero gear prep."),
            ("Traditional Woodworking & Hand Tools", "survival", "⚡ 1 Credit / Session", "Chisel joinery, hand plane tuning, timber selection, and carving."),
            ("Leather Crafting & Custom Goods", "creative", "Free Peer Exchange", "Pattern cutting, saddle stitching, edge burnishing, and leather dye."),
            ("Gaelic & Irish Culture Basics", "languages", "Free Peer Exchange", "Introductory Irish language phrases, folklore, and pronunciation."),
            ("Resilience & Mental Toughness Training", "soft", "⚡ 1 Credit / Session", "Mindset tactics for endurance, stoic mental framing, and obstacle handling."),
            ("Sustainable Craft Business Operations", "business", "Free Peer Exchange", "Pricing handmade goods, artisan craft fairs, and sustainable sourcing."),
        ],
        "learn": [
            ("E-commerce Store Setup & Shopify", "business", "Free Peer Exchange", "Eager to start an online store for handmade leather products."),
        ]
    },
    {
        "name": "Vikram Singh",
        "email": "vikram@mogg.io",
        "credits": 6,
        "bio": "VP of Engineering & outdoorsman. Teaching microservices, product strategy, and video editing.",
        "teach": [
            ("Microservices & Distributed Systems", "tech", "⚡ 1 Credit / Session", "gRPC, Kafka event streaming, distributed caching, and resilient APIs."),
            ("Tech Leadership & Engineering Management", "soft", "Free Peer Exchange", "1-on-1 coaching, career ladder progression, and technical delegation."),
            ("Product Strategy & Roadmap Planning", "business", "⚡ 1 Credit / Session", "Prioritization frameworks (RICE, Kano), PRDs, and feature validation."),
            ("Punjabi Language & Cultural Etiquette", "languages", "Free Peer Exchange", "Gurmukhi alphabet overview, spoken conversational Punjabi, and culture."),
            ("Video Editing with Premiere Pro", "creative", "Free Peer Exchange", "Timeline editing, color grading, audio leveling, and YouTube export."),
            ("Wilderness Tracking & Animal Signs", "survival", "⚡ 1 Credit / Session", "Footprint analysis, gait identification, environmental sign reading."),
        ],
        "learn": [
            ("Off-Grid Solar & Battery Setup", "survival", "Free Peer Exchange", "Want to learn off-grid solar setups for cabin builds."),
        ]
    },
    {
        "name": "Aisha Khan",
        "email": "aisha@mogg.io",
        "credits": 5,
        "bio": "Fashion designer & PR strategist. Teaching garment pattern making, Arabic, and PR strategy.",
        "teach": [
            ("Fashion Design & Pattern Making", "creative", "⚡ 1 Credit / Session", "Garment sketching, fabric selection, draping, and sewing techniques."),
            ("Arabic Calligraphy & Conversational Basics", "languages", "Free Peer Exchange", "Naskh script stroke order, common phrases, and dialect variations."),
            ("Social Media Brand Monetization", "business", "Free Peer Exchange", "Influencer marketing contracts, brand deals, and audience growth."),
            ("Public Relations & Media Relations", "soft", "⚡ 1 Credit / Session", "Writing press releases, journalist outreach, and crisis communications."),
            ("WordPress & No-Code Web Builders", "tech", "Free Peer Exchange", "Elementor layout building, plugin selection, domain setup, and SEO."),
            ("Emergency Preparedness for Families", "survival", "Free Peer Exchange", "Family evacuation planning, food storage rotation, and emergency kits."),
        ],
        "learn": [
            ("3D Modeling & Rendering in Blender", "creative", "Free Peer Exchange", "Eager to learn 3D garment rendering in Blender."),
        ]
    },
    {
        "name": "Tom Wilson",
        "email": "tom@mogg.io",
        "credits": 4,
        "bio": "Sales director & sea kayaking instructor. Teaching enterprise sales, Linux scripting, and Portuguese!",
        "teach": [
            ("Sea Kayaking & Open Water Safety", "survival", "⚡ 1 Credit / Session", "Paddle strokes, self-rescue rolls, tide reading, and sea navigation."),
            ("Corporate Sales & Pipeline Management", "business", "Free Peer Exchange", "B2B cold outreach, qualifying leads (BANT), and closing enterprise deals."),
            ("Team Building & Group Facilitation", "soft", "⚡ 1 Credit / Session", "Running effective workshops, icebreakers, and alignment retrospectives."),
            ("Portuguese Conversational Skills", "languages", "Free Peer Exchange", "Brazilian Portuguese dialogue, pronunciation, and travel expressions."),
            ("Acoustic Audio Recording", "creative", "Free Peer Exchange", "Microphone placement, room acoustics treatment, and vocal recording."),
            ("Linux Command Line & Bash Scripting", "tech", "Free Peer Exchange", "Shell syntax, file permission management, grep/sed, and automated cron jobs."),
        ],
        "learn": [
            ("Python for Data Science & ML", "tech", "Free Peer Exchange", "Goal to learn Python scripting for sales data processing."),
        ]
    },
]

# Pre-seeded trade requests for demo purposes
SEED_REQUESTS = [
    # Alex bought Python from Sofia
    {"from": "alex@mogg.io", "to": "sofia@mogg.io", "skill": "Python for Data Science & ML", "status": "ACCEPTED"},
    # Alex completed guitar with Marcus
    {"from": "alex@mogg.io", "to": "marcus@mogg.io", "skill": "Guitar Basics & Music Theory", "status": "CREDIT_RELEASED"},
    # David wants to learn from Alex — pending
    {"from": "david@mogg.io", "to": "alex@mogg.io", "skill": "UI/UX Design & Figma Systems", "status": "REQUESTED"},
    # Priya learned After Effects from Alex
    {"from": "priya@mogg.io", "to": "alex@mogg.io", "skill": "Motion Graphics & After Effects", "status": "ACCEPTED"},
]

SEED_MESSAGES = {
    0: [  # session index 0 (Alex ↔ Sofia)
        ("alex@mogg.io", "Hi Sofia! Excited to start learning Python for Data Science from you!"),
        ("sofia@mogg.io", "Hey Alex! Happy to help. Let's schedule a 1-on-1 call to set up Jupyter Notebooks."),
    ],
    1: [  # session index 1 (Alex ↔ Marcus)
        ("alex@mogg.io", "Hey Marcus, thanks for the amazing acoustic guitar fingerpicking lesson!"),
        ("marcus@mogg.io", "Anytime Alex! Practice those chord transitions and let me know when you want to learn songwriting."),
    ],
    3: [  # session index 3 (Priya ↔ Alex)
        ("priya@mogg.io", "Hi Alex, I accepted your After Effects motion graphics session!"),
        ("alex@mogg.io", "Awesome Priya! I will share my Figma UI motion templates with you."),
    ],
}

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[Seed] Seeding MOGG Community Data (15 users, 90+ TEACH, 15 LEARN)...")

    users_map = {}  # email → User instance

    for u_data in SEED_USERS:
        linkedin = u_data.get("linkedin_url", f"https://www.linkedin.com/in/{u_data['name'].lower().replace(' ', '-')}")
        u = User(
            name=u_data["name"],
            email=u_data["email"],
            avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={u_data['name']}",
            bio=u_data.get("bio", ""),
            linkedin_url=linkedin
        )
        db.add(u)
        db.flush()
        users_map[u_data["email"]] = u

        # Create Credit Account with specified balance
        acc = CreditAccount(user_id=u.id, balance=u_data.get("credits", 3), escrow_balance=0)
        db.add(acc)

        tx = CreditTransaction(
            user_id=u.id,
            amount=u_data.get("credits", 3),
            type=TransactionType.INITIAL_GRANT.value,
            description=f"Welcome bonus: {u_data.get('credits', 3)} free MG Coins granted."
        )
        db.add(tx)

        # Seed Domain Certifications for all their teaching domains so they pass verification
        seeded_domains = set()
        for _, d_name, _, _ in u_data["teach"]:
            d_clean = d_name.lower().strip()
            if d_clean not in seeded_domains:
                cert = DomainCertification(
                    user_id=u.id,
                    domain=d_clean,
                    course_title=f"Verified {d_clean.title()} Instructor Certification",
                    score=100
                )
                db.add(cert)
                seeded_domains.add(d_clean)

        # TEACH listings
        for skill_text, domain, fee_text, description in u_data["teach"]:
            vec = embed_text(skill_text)
            listing = SkillListing(
                user_id=u.id,
                type=ListingType.TEACH,
                skill_text=skill_text,
                category=domain.title(),
                domain=domain,
                fee_text=fee_text,
                description=description,
                embedding=vector_to_bytes(vec)
            )
            db.add(listing)

        # LEARN listings
        for skill_text, domain, fee_text, description in u_data["learn"]:
            vec = embed_text(skill_text)
            listing = SkillListing(
                user_id=u.id,
                type=ListingType.LEARN,
                skill_text=skill_text,
                category=domain.title(),
                domain=domain,
                fee_text=fee_text,
                description=description,
                embedding=vector_to_bytes(vec)
            )
            db.add(listing)

    db.flush()

    # Seed trade requests / sessions
    session_objs = []
    for req in SEED_REQUESTS:
        teacher_user = users_map.get(req["to"])
        learner_user = users_map.get(req["from"])
        if not teacher_user or not learner_user:
            continue

        status_map = {
            "REQUESTED": SessionStatus.REQUESTED,
            "ACCEPTED": SessionStatus.ACCEPTED,
            "CREDIT_RELEASED": SessionStatus.CREDIT_RELEASED,
            "DECLINED": SessionStatus.DECLINED,
        }

        s = PeerSession(
            session_type=SessionType.CREDIT_EXCHANGE,
            teacher_id=teacher_user.id,
            learner_id=learner_user.id,
            teach_skill_text=req["skill"],
            status=status_map.get(req["status"], SessionStatus.REQUESTED),
        )
        db.add(s)
        db.flush()
        session_objs.append(s)

    # Seed messages for sessions
    for session_idx, messages in SEED_MESSAGES.items():
        if session_idx < len(session_objs):
            session_obj = session_objs[session_idx]
            for sender_email, text in messages:
                sender = users_map.get(sender_email)
                if sender:
                    msg = ChatMessage(
                        session_id=session_obj.id,
                        sender_id=sender.id,
                        text=text,
                    )
                    db.add(msg)

    # ─────────────────────────────────────────────────────────
    # Seed Multi-Peer Study Rooms & Group Conversations
    # ─────────────────────────────────────────────────────────
    group_configs = [
        {
            "name": "🚀 AI Engineers & Prompt Crafters",
            "topic": "Autonomous Agents, LangChain, Tool Calling, and Local LLMs",
            "creator": "sofia@mogg.io",
            "members": ["sofia@mogg.io", "alex@mogg.io", "david@mogg.io", "vikram@mogg.io"],
            "messages": [
                ("sofia@mogg.io", "Welcome everyone! What autonomous agent projects are you working on this week?"),
                ("alex@mogg.io", "I'm designing a Figma UI that lets non-technical users define agent goals and tool permissions visually."),
                ("david@mogg.io", "Make sure you sandbox agent tool execution so network requests and bash execution remain strictly isolated!"),
                ("vikram@mogg.io", "Agreed on sandboxing. We should schedule a 30-min group sync on Google Meet this Thursday to review architecture.")
            ]
        },
        {
            "name": "🏕️ Wilderness & Emergency Prep Squad",
            "topic": "Off-Grid Survival, Bushcraft Knots, Solar Storage & Trauma Triage",
            "creator": "marcus@mogg.io",
            "members": ["marcus@mogg.io", "maya@mogg.io", "liam@mogg.io", "alex@mogg.io"],
            "messages": [
                ("marcus@mogg.io", "Hey squad! What's everyone's go-to friction fire method in high humidity or damp conditions?"),
                ("liam@mogg.io", "Bow drill with cedar spindle on a dry cedar hearthboard! Plus a fatwood shavings tinder bundle."),
                ("maya@mogg.io", "And remember to keep battery banks inside insulated pockets overnight so the cold doesn't drain their charge.")
            ]
        },
        {
            "name": "🎨 Creative Design & Motion Mastermind",
            "topic": "Figma Design Systems, After Effects Keyframing & 3D Renders",
            "creator": "alex@mogg.io",
            "members": ["alex@mogg.io", "lucas@mogg.io", "priya@mogg.io", "elena@mogg.io"],
            "messages": [
                ("alex@mogg.io", "Welcome to our creative circle! Feel free to drop work-in-progress renders and design tokens here."),
                ("lucas@mogg.io", "Just finished a Blender glass caustics simulation, happy to share shader and lighting node tips."),
                ("priya@mogg.io", "3D product renders combined with strong typography elevate conversion rates by over 40% in our portfolio startups!")
            ]
        }
    ]

    for gc in group_configs:
        creator_user = users_map.get(gc["creator"])
        if not creator_user:
            continue
        room = GroupRoom(
            name=gc["name"],
            topic=gc["topic"],
            creator_id=creator_user.id
        )
        for mem_email in gc["members"]:
            mem = users_map.get(mem_email)
            if mem and mem not in room.members:
                room.members.append(mem)
        db.add(room)
        db.flush()

        for sender_email, text in gc["messages"]:
            sender_u = users_map.get(sender_email)
            if sender_u:
                gmsg = GroupMessage(
                    room_id=room.id,
                    sender_id=sender_u.id,
                    text=text
                )
                db.add(gmsg)

    db.commit()

    total_teach = sum(len(u["teach"]) for u in SEED_USERS)
    total_learn = sum(len(u["learn"]) for u in SEED_USERS)
    print(f"[Seed] Seed completed successfully with {len(SEED_USERS)} users, {total_teach} TEACH listings, {total_learn} LEARN listings, {len(SEED_REQUESTS)} sessions, and {sum(len(m) for m in SEED_MESSAGES.values())} chat messages!")
    db.close()


if __name__ == "__main__":
    seed_database()
