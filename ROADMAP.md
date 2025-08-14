# MMAmania Roadmap

This document is the single source of truth for what we are building, how we are building it, and why. It is intentionally detailed and technical so engineering can execute without ambiguity.

---

## 0. Product Charter

- Purpose: Be the most engaging place for UFC fans to follow cards, pick winners, debate, and consume MMA content.
- v1 Platform: iOS (Flutter). Android/Web later.
- Ethos: Dark, modern, fast, fun. Low-friction predictions. High-signal debates.

---

## 1. Locked Decisions

- UFC-only v1
- Auth: Auth0; map `auth0_sub` 1:1 to `users`
- Scraping: daily + post‑event finalization (≤12h). Patch-only.
- Pagination: ~50 events at a time, load more on scroll
- Predictions: lock at card start; weights {Main=40, Co‑main=30, Main‑card=25, Prelims=20}; Draw/NC=0
- Leaderboards: all‑time only
- Feed: multi-source, link/embed only; no re-hosting
- Debates: audio (≤10 speakers, mod controls, optional record) + text threads
- LLM: Q&A + summaries + explanations (freemium later)
- Theme: dark + gradients + subtle animations
- Budget: <$200/mo until scale

---

## 2. System Architecture (Detailed)

- Client (Flutter iOS)
  - Reads via Supabase REST; writes predictions via Backend; admin refresh via Backend.
  - Realtime subscriptions (M2) for leaderboard/prediction deltas.
- Backend (FastAPI)
  - Auth0 JWT verify (RS256). Maps `sub`→`users.auth0_sub`. Creates user row if missing.
  - Endpoints: predictions (write/lock), search proxy (optional), admin scrape trigger, leaderboards.
  - ELO worker trigger on fight finalization.
- Scraper (Python)
  - Daily cron + on-demand; bounded concurrency; patch-only idempotent upserts.
  - Canonical dates from List-of-events; fight details from event pages.
- Data (Supabase/Postgres)
  - Tables: `events`, `fights`, `users`, `predictions`, `user_scores`, `media_posts`, `debates`, `debate_participants`, `debate_messages`.
  - Indexes for date ordering and trigram name search.
- Notifications (M2+)
  - APNs via FCM; topic per event for reminders; user-level toggles.
- Media ingestion
  - Scripts hit public APIs/RSS/scrapes lightly; link/embed only; tag content.

---

## 3. Data Model (DDL, Indexes, RLS)

- DDL and indexes are defined to support: fast event paging by date, exact fight ordering, strict uniqueness, and whole-word search.
- RLS: read-mostly; predictions writable only by owner; service role for scraper/admin.

Key uniqueness and indexes:
- `unique(events.slug)`
- `unique(fights.event_id, fights.fight_order)`
- `idx_events_date_desc` for pagination
- trigram GIN on `events.name` and `fights(winner+loser)`

RLS policy examples:
- `events`: select all; no public writes
- `fights`: select all; no public writes
- `predictions`: user can insert/update where `auth.uid() = user_id` and lock not passed

---

## 4. Scraper (Algorithms & Selectors)

Table detection:
- A table is a fight table if its headers include any of {weight, method, round, time} (case-insensitive).

Winner/Loser parsing:
- Primary regex: `(?i)^\s*(?P<winner>[^\n]+?)\s+def\.?\s+(?P<loser>[^\n]+?)\s*$`.
- Fallback: `(?i)^\s*(?P<a>[^\n]+?)\s+vs\.?\s+(?P<b>[^\n]+?)\s*$` (status remains scheduled).
- Normalize: strip references `[a]`, scorecards `(29–28, ...)`, punctuation spacing.

Global ordering:
- Iterate tables in DOM order; maintain `global_fight_order`.
- Assign `is_main_event = (fight_order==1)`, `is_co_main_event=(fight_order==2)`.
- Skip rows with empty names; do not increment order.

Idempotent upsert:
- Key: `(event_id, fight_order)`.
- Compute `row_hash` across names, weight_class, method, round, time, status, flags.
- If unchanged, skip; else `update ... set updated_at=now()` or insert.

Cadence:
- Daily: reprocess upcoming + last 8 weeks.
- Finalization: run within 12h post scheduled end.
- On-demand: `/api/admin/scrape/event/{id_or_slug}` queue job.

Backoff:
- Exponential with jitter for 429/5xx; global hourly request budget.

Diagnostics:
- Log per event: tables, fights parsed, upserts/skips; warnings on empty names/missing def.

---

## 5. Backend API (Contracts)

Auth:
- RS256 verify; map/create user; attach `user_id`.

Events:
- GET `/api/events?limit=50&cursor=<iso8601>&dir=desc` → `[Event]` ordered by date.
- GET `/api/events/{id_or_slug}` → `{...event, fights:[Fight ordered asc]}`.
- GET `/api/search/events?q=...` → whole-word match (title or fighter names), `date desc`.

Predictions:
- POST `/api/predictions` `{ fight_id, pick_name }` → 401/403 on unauth/locked; upsert by `(user_id,fight_id)`.
- GET `/api/leaderboard?limit=100` → `[ { user_id, handle, elo, points, wins, losses } ]`.

Admin:
- POST `/api/admin/scrape/event/{id_or_slug}` → 202, job queued.
- POST `/api/admin/recompute/elo` → 202.

Debates:
- POST `/api/debates` `{ title, is_audio }`.
- POST `/api/debates/{id}/join` `{ role }`.
- POST `/api/debates/{id}/message` `{ message }`.
- POST `/api/debates/{id}/pin` `{ message_id }` (host/mod).

Feed:
- GET `/api/feed?limit=50&cursor=<iso8601>` → `[MediaPost]`.

Errors: 400, 401, 403, 404, 409, 429, 5xx.

---

## 6. Supabase REST Reads (App Wiring)

- Events: `/rest/v1/events?select=*&order=date.desc&limit=50&offset=...`.
- Fights: `/rest/v1/fights?event_id=eq.<id>&order=fight_order.asc`.
- Search: first query fights superset via `ilike`, enforce `\bquery\b` client-side, then fetch events by IDs; sort `date desc`.
- Client filters: upcoming vs past based on device time; invalid dates → sentinel old date to sort bottom.

---

## 7. Predictions & ELO (Math and Flow)

Locking:
- Lock predictions at event card start time (first scheduled fight). Backend enforces 403.

ELO:
- Expected: `E = 1 / (1 + 10^((elo_opponent - elo_self)/400))`.
- Update: `elo' = elo + K * (result - E)`; K by position: {40,30,25,20}.
- Result: 1 (correct pick), 0 (incorrect), 0 (draw/NC) v1.

Points:
- Mirror K per position initially; adjustable later.

Worker:
- On scraper mark `completed`: gather predictions, compute deltas, upsert `user_scores`, increment wins/losses/pushes; emit realtime (M2).

Anti-cheat:
- Unique `(user_id,fight_id)`; lock cutoffs; optional audit trail M2.

---

## 8. iOS App (Flutter)

Architecture:
- Services: `SupabaseService` (REST), `BackendService` (JWT to backend), `SimpleDatabaseService` wrapper.
- State: Provider; debounced search; defensive sorts only where unavoidable.

Screens:
- Home: Past/Upcoming tabs, infinite scroll, search bar (≥3 chars, whole-word), dark cards.
- Event Details: gradient header; ordered fights; prediction selector; lock state.
- Leaderboard: all-time list with ranks; avatars.
- Feed: embeds; comments (basic).
- Debates: rooms list; join audio; text thread.

Theme:
- Palette: background `#0B0F14`, surface `#121820`, primary `#D71E28`, accent `#10B981`.
- Motion: 150–250ms transitions; shimmer loaders; subtle elevation.
- Accessibility: ≥4.5:1 contrast; scalable fonts.

---

## 9. Realtime & Notifications (M2+)

- Realtime: subscribe to prediction counts and leaderboard changes by `event_id`.
- Notifications: pick reminders (X hours pre-start), results summaries, leaderboard milestones. APNs via FCM.

---

## 10. Media Feed

- Ingest: YouTube/X/TikTok/Podcasts; store `media_posts(source,url,title,published_at,tags,engagement)`.
- Render: embed/webview only; no downloads.
- Moderation: minimal flags; hide on report (M2).

---

## 11. Debates (Audio/Text)

- Roles: host, mod, speaker, listener; ≤10 speakers; mod mute; optional record.
- Text: persistent messages per room; pinned; upvotes (M2).
- Provider: free-first; adapter to LiveKit/Agora if needed.

---

## 12. LLM (Post-v1)

- RAG over our DB + scraped content; guardrails and quotas.
- Use cases: Q&A, debate summaries, pick explanations.

---

## 13. Ops: SLOs, Monitoring, Runbooks

SLOs:
- Freshness: 99% events updated ≤12h after end.
- p95 latency: reads ≤400ms; writes ≤600ms.
- App crash rate <1%.

Monitoring:
- Sentry (app/backend); uptime pings; structured logs with correlation IDs.

Runbooks:
- Missing fights: trigger on-demand; inspect logs; adjust selectors.
- Wrong order: verify DB `fight_order`; remove client resorting; fix global order.
- Bad dates: backfill from list page; never default to `now()`.
- Supabase errors: check unique constraints and RLS.
- Predictions lock: validate card start calculation and server checks.

---

## 14. Security & Compliance

- Auth0 RS256 verify; strict RLS; minimal write surfaces.
- Rate limits on write endpoints; basic profanity filtering.
- Legal: embed-only; terms link in settings.

---

## 15. CI/CD & Environments

- CI: lint/tests for Python & Flutter; formatters.
- Branch: `main` prod; feature branches via PR.
- Deploy: backend (Render/Fly), scraper cron (Cloud Run/Cron), Supabase SQL migrations via PR.
- Secrets: `.env` local; provider secrets in managed env store (M2).

---

## 16. Milestones (Phased)

M1 (2–3 weeks): Scraper + iOS cards + Predictions
- Harden scraper (dates, upserts, backoff), admin refresh, iOS list/detail, predictions with lock, ELO worker + leaderboard API + basic UI.

M2 (1–2 weeks): Realtime + Notifications groundwork
- Realtime channels; local reminders; APNs prep; admin refresh UI.

M3 (3–4 weeks): Feed + Debates
- Media ingestion + feed UI; debates audio + text + mod controls.

M4 (3–6 weeks): Analytics + LLM
- Heuristics; feature store; insights UI; LLM Q&A and summaries; freemium.

---

## 17. API Examples

Get events (page):
```bash
curl "$SUPABASE_URL/rest/v1/events?select=*&order=date.desc&limit=50" \
 -H "apikey: $SUPABASE_ANON_KEY" -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

Get fights for event:
```bash
curl "$SUPABASE_URL/rest/v1/fights?event_id=eq.$EVENT_ID&order=fight_order.asc" \
 -H "apikey: $SUPABASE_ANON_KEY" -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

Search superset then filter whole-word client-side:
```bash
curl "$SUPABASE_URL/rest/v1/fights?select=event_id,winner_name,loser_name&winner_name=ilike.*khabib*&loser_name=ilike.*khabib*" \
 -H "apikey: $SUPABASE_ANON_KEY" -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

---

## 18. Performance Budgets & Risks

- First paint ≤2.5s; detail ≤1.0s; scraper daily run ≤20m, on-demand ≤60s.
- Risks: HTML drift, duplication, API costs, legal complaints → mitigations documented above.

---
## 16. Milestones (Detailed Implementation Plan)

## 16. Next Steps - Feature Implementation

Based on your priority order, here's what we need to build:

### **Phase 1: Content & Community (Week 1-2)**

**📺 Enhanced Feed Aggregation**
- Add `media_posts` table
- YouTube/Twitter/TikTok/Podcast API integration
- New feed screen with embeds

**🎙️ Live Debates (Audio + Text)**
- Add `debate_rooms` and `debate_messages` tables
- LiveKit for audio rooms (≤10 speakers, mod controls)
- Supabase Realtime for text threads

### **Phase 2: Intelligence & Analytics (Week 3-4)**

**📊 Real Data-Driven ML Analytics**
- UFC Stats API integration
- Fighter metrics and matchup analysis
- Chart widgets in fight cards

**🧠 LLM Functionalities**
- OpenAI API for Q&A and summaries
- Use existing data as context
- Chat interface in app

### **Phase 3: Enhanced Scrapers & Fight System (Week 5-6)**

**🕷️ Enhanced Daily Scrapers**
- Add daily cron to existing scraper
- Scrape upcoming UFC schedule
- Auto-update event status (scheduled → completed)
- Architecture for future fight cards

**🏆 ELO + Fight Picking System**
- Add `predictions` and `user_scores` tables to Supabase
- Add prediction buttons to existing fight cards
- Create leaderboard screen
- Simple ELO calculation when fights complete

### **Phase 4: Advanced Betting Integration (Week 7-8)**

**🔍 NLP + Odds + Parlays**
- Sportsbook API integration
- Sentiment analysis on social mentions
- Parlay prediction logic
- Legal compliance features

**Ready to start with Phase 1?** We can begin with feed aggregation and debate rooms.

