# SkillSwap — Reference Links

Problem Statement: *How can you build a platform that enables students to exchange skills by finding peers who can teach what they want to learn and allowing them to offer their own skills as mentors?*

## Cloned & Analyzed (most relevant, ranked)

1. **[ShyanCS/SkillxSwap](https://github.com/ShyanCS/SkillxSwap)** — Spring Boot 4 + PostgreSQL + React. Most production-grade: modular backend (`matching`, `skill`, `session`, `availability`, `wallet`, `review`, `messaging`), 19 Flyway migrations, Docker Compose prod setup, tests. **Primary architecture reference.**
2. **[kr1shnnna/skill-swap](https://github.com/kr1shnnna/skill-swap)** — MERN + a separate Python AI microservice using `sentence-transformers` for semantic teach/learn matching (cosine similarity on embeddings, not just keyword match). **Best matching-algorithm reference.**
3. **[XoXoHarsh/SkillSwap](https://github.com/XoXoHarsh/SkillSwap)** — MERN, Google OAuth2 + JWT, real screenshots (discover, chat, schedule-call, rating pages). Good UX reference.
4. **[srishtighoshh/SkillSwap](https://github.com/srishtighoshh/SkillSwap)** — Java, layered (model/dao/service/util), includes ER diagrams and a project report doc.
5. **[eshivani07/Skillswap](https://github.com/eshivani07/Skillswap)** — React + Firebase/Firestore, AI matchmaking + "SkillCoin" barter concept. Lighter weight, UI-reference only.

## Other repos found (not cloned)

- [vibha2047-core/SkillSwap](https://github.com/vibha2047-core/SkillSwap)
- [Abarna-1808/SkillSwap](https://github.com/Abarna-1808/SkillSwap)
- [Tanusri-Dummu/Skill-Swap](https://github.com/Tanusri-Dummu/Skill-Swap)
- [shabanas-git/SkillSwap](https://github.com/shabanas-git/SkillSwap)
- [Wellitsabhi/Skillswap](https://github.com/Wellitsabhi/Skillswap)
- [GitHub Topic: skill-exchange](https://github.com/topics/skill-exchange)

## Open-source production reference (non-student, ledger architecture)

- **[coopdevs/timeoverflow](https://github.com/coopdevs/timeoverflow)** — Rails-based time-banking system, public-domain licensed, actually used by real time banks. Best reference for correct credit/ledger accounting.
- [coopdevs/TimeOverflow-1](https://github.com/coopdevs/TimeOverflow-1) — companion data-exploration repo.
- [ashura-01/time-bank](https://github.com/ashura-01/time-bank) — MERN time-credit ledger with dispute resolution.
- [gtamborero/time-flow](https://github.com/gtamborero/time-flow)

## Real-world closed-source products (for UX/feature benchmarking)

- [Simbi](https://simbi.com/) — barter marketplace, Simbi credits, YC-backed
- [TimeRepublik](https://www.timerepublik.com/) — time-based peer skill exchange
- [hOurworld / Time and Talents](https://www.hourworld.org/_TimeAndTalents.htm) — free time-banking software for community time banks
- [Timebanks.org](https://timebanks.org/) — foundational time-banking platform

## Academic reference

- [SkillSwap: A Peer-to-Peer Skill Exchange Platform for Community-Driven Learning (PDF)](https://ijcope.org/wp-content/uploads/2026/05/SkillSwap-A-Peer-to-Peer-Skill-Exchange-Platform-for-Community-Driven-Learning.pdf) — full paper covering architecture, JWT auth, swap-request system, rating mechanism, grounded in Cahn's time-banking theory.
