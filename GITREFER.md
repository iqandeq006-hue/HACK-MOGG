# Skill Exchange Platform — Research Compilation

Research on GitHub repos and open source reference architectures for a peer-to-peer skill exchange platform (students teach what they know, learn what they want, matched with peers).

Judging criteria to keep in mind: **implementation, scalability, and how well the matching problem is actually solved.**

---

## Relevant GitHub Repos (Skill Exchange / Peer-to-Peer Learning)

### 1. [KLP13/skill-exchange-platform](https://github.com/KLP13/skill-exchange-platform)
Credit-based model: one hour of teaching earns a credit, spendable to learn from someone else — no money changes hands. Includes video sessions and a community forum.

### 2. [Kaviya-Ramesh-2007/campus-skill-exchange](https://github.com/Kaviya-Ramesh-2007/campus-skill-exchange)
Only a foundation/scaffold exists so far (app shells, DB migrations, CI, no product features yet), but the layout is worth studying: NestJS API + Next.js web monorepo with Prisma migrations, shared config/contracts packages, and an accessible design-system package. A clean starting skeleton for structuring a monorepo.

### 3. [shruti1760/Skill-Swap-Marketplace-Fe-](https://github.com/shruti1760/Skill-Swap-Marketplace-Fe-)
Frontend for a barter-based marketplace. Works like a directory of student skills, profiles double as a portfolio/resume, and includes an "intelligent" skill-match recommender.

### 4. [ravindra-y/Skill-Exchange-Platform](https://github.com/ravindra-y/Skill-Exchange-Platform)
The strongest technical reference in this list. Live messaging and video sessions with a collaborative whiteboard:
- WebRTC for direct peer-to-peer video/audio.
- Socket.io used purely as the signaling server (exchanging offers/answers/ICE candidates before the direct connection is established).
- Matching is explicitly **deterministic** — exact skill-string matches in the database, no fuzzy/semantic matching.
- Per-user undo/redo history on the whiteboard without disrupting the other peer's work.

### 5. [Manans6114/skill-loop (SkillLoop)](https://github.com/Manans6114/skill-loop)
Clean separation of concerns:
- Backend: FastAPI + Python, SQLAlchemy models, Pydantic schemas, Auth0 integration.
- Frontend: React + TypeScript + Vite, with an auth context and custom API hooks.
- Credit system: earn by teaching, spend by learning.

### 6. [pravin-python/Student-Skill-Swap](https://github.com/pravin-python/Student-Skill-Swap)
Django-based. More of a detailed product spec than finished code, but a good source of feature ideas:
- Skill-swap requests between students.
- Session history log (completed teaching/learning sessions).
- A matching algorithm for connections.
- Badges for completing sessions, teaching diverse skills, high ratings.
- Skill-tree / learning-path suggestions that break a skill into smaller topics.

### 7. GitHub topic pages (browse directly — dozens of smaller repos)
- [github.com/topics/skill-exchange](https://github.com/topics/skill-exchange)
- [github.com/topics/skill-sharing](https://github.com/topics/skill-sharing)

Stacks seen across these: MERN, Flutter/Dart, Spring Boot, .NET, Firebase + Next.js. Several advertise AI-based or fuzzy matching and token-economy / gamification layers.

---

## Reference Product Architectures

These are closer to production-grade than the student hackathon projects above, and more useful for architecture decisions.

### [openmentor-io/openmentor](https://github.com/openmentor-io/openmentor)
Real mentor-matching platform (mentees find a mentor, send a request, meet 1:1 — no payments, no lock-in). Documented architecture:
- **Web**: Next.js 16 + TypeScript + Tailwind — a thin client; every data operation goes through the API.
- **API**: Go + PostgreSQL — REST API, mentor catalog, magic-link auth for mentors/moderators, request lifecycle.
- **Worker**: a separate background process (same Go codebase, different binary) handling side effects — transactional email via AWS SES, daily reminder/deactivation cron jobs. Isolated crash domain, its own DB pool, triggered via authenticated internal HTTP calls.
- **Infra**: single VM, Docker Compose + Traefik, Postgres in a container with nightly backups to S3, observability via Grafana Alloy → Grafana Cloud.

Good reference for **"how much infrastructure do we actually need"** — deliberately not microservices-heavy, and cleanly separates request-path work from async side effects.

### [mantisdarling/Mantis (MANTIS)](https://github.com/mantisdarling/Mantis)
More ambitious mentorship marketplace. The part most relevant to a matching problem:
- **API**: NestJS 11 + Express 5 + Prisma 7 + PostgreSQL 15.
- **Web**: Next.js 15 + React 19 + Stripe (escrow payments, manual capture).
- **Recommender**: a *separate* FastAPI + scikit-learn Python service — matching/recommendation logic is isolated from the core API rather than baked in.
- Real-time messaging via Socket.io + Redis adapter.
- Expert search combines skill/rating filters with AI matching.

The key architectural idea worth borrowing: **treat the matching engine as its own swappable service.** You can start with simple rule-based matching and later swap in embeddings/ML without touching the core API.

### Timebanking software (older, non-startup lineage of the same problem)
Time Banks USA and platforms like Cyclos / the Community Exchange System have run this exact model for two decades — historically on Drupal-based stacks — using an exchangeable time-credit system: one hour volunteered for someone earns one credit, redeemable for a service from *anyone* in the network (not just the original counterparty). Conceptually this is the closest real-world analog to "credits for teaching, spend to learn." Worth studying for the edge cases it has already had to solve: double-booking, no-shows, credit hoarding/inflation, and network-wide (not just 1:1) redemption.

---

## Takeaway for Implementation Priorities

Given the judging criteria (implementation, scalability, problem-solving depth):

- **Deterministic skill-string matching** (like repo #4) is fastest to implement but weakest on "problem actually solved" — it won't match "I know React" with "I want to learn frontend development."
- **Separating the matching/recommender logic into its own service** (MANTIS's pattern) is the single most valuable architectural idea to borrow — it lets the matching approach evolve (rule-based → fuzzy → embeddings) without re-architecting the core API.
- **Isolating async side effects into a worker process** (openmentor's pattern) keeps the request path fast and is simple enough to implement in a hackathon timeframe.
- **Timebanking's network-wide credit model** (rather than strict 1:1 barter) solves a real matching bottleneck: A teaches B, but B doesn't have anything A wants — a network-wide credit ledger avoids requiring a direct reciprocal match.

---

## Follow-up: Deep Dive on User-Cloned Reference Repos

A follow-up round cloned and analyzed a further shortlist of repos directly (see `REFER.md`). Notes below add analysis on top of that shortlist — two of the three key repos could not be independently re-verified via search (likely too new/small to be indexed yet), so those two are assessed from their own repo descriptions; TimeOverflow was independently verified.

### ShyanCS/SkillxSwap — primary architecture reference
The modular split (`matching`, `skill`, `session`, `availability`, `wallet`, `review`, `messaging`) is the right shape for this problem: it treats matching, scheduling, and credit accounting as separate bounded contexts instead of one monolithic "User" model with fifteen fields bolted on. 19 Flyway migrations is a good sign — the schema evolved incrementally with real migration discipline rather than being hand-written once and never touched. The `wallet` module is worth reading first if it can be run locally, since credit accounting is where these projects usually cut corners (see TimeOverflow notes below on why that's hard to get right).

### kr1shnnna/skill-swap — best matching-algorithm reference
A separate Python microservice doing `sentence-transformers` + cosine similarity for teach/learn matching is meaningfully better than keyword/string matching (e.g. the deterministic exact-string matching seen in `ravindra-y/Skill-Exchange-Platform` earlier in this doc). Concretely: someone who lists "I can teach React" gets correctly matched against "I want to learn frontend development" — a string match never fires on that pair. Tradeoffs: added cost/latency (an embedding call per profile) and a classic failure mode of near-miss over-matching (adjacent-but-different skills scoring too high). Worth demoing a similarity threshold plus a couple of deliberately-excluded near-miss examples to show precision was considered, not just recall.

### coopdevs/timeoverflow — verified, strongest ledger reference
Independently confirmed: Ruby on Rails, AGPL-3.0 licensed, started 2012, still actively maintained, ~165 stars / 74 forks. Multi-tenant by design — one installation can host several independent time banks, with three privilege tiers (superadmin across banks, admin per-bank, member). Split into two blocks: an admin/management system (member rolls, service listings, manual accounting — built so a bank whose members mostly aren't online can still run on paper + an office) and a social network / online banking layer for members who want to self-serve.

This is the strongest reference for **many-to-many settlement**: A teaches B, B teaches C, C teaches A — a network-wide credit ledger, not a strict 1:1 barter, is what resolves this. None of the `wallet`-branded modules in the cloned student repos document debt limits or settlement rules across more than two parties, which is usually a sign the project never got far enough to hit that problem. TimeOverflow already has to solve it because real time banks run into it daily.

### Priority ranking for implementation
1. **Architecture skeleton** → SkillxSwap's module boundaries.
2. **Matching approach** → kr1shnnna's embedding-based microservice, kept as its own service (same separation pattern as MANTIS's recommender, above) — swappable later, doesn't block the main API.
3. **Ledger correctness** → borrow TimeOverflow's tiered access model (superadmin/admin/member) and its explicit design for less tech-savvy users, rather than copying any from-scratch student `wallet` module.
