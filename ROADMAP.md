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

## 2. System Architecture

- Flutter iOS app → Supabase REST/Realtime (reads), Backend (writes)
- FastAPI backend: Auth0 JWT verification, predictions, ELO worker, admin scraping
- Scraper (Python): daily cron + on‑demand; patch-only idempotent updates
- DB: Supabase/Postgres (events, fights, predictions, user_scores, media_posts, debates)
- Realtime: Supabase for leaderboards/picks (M2)
- Notifications: FCM/APNs (post‑v1)
- Media ingestion: scripts pulling YouTube/X/TikTok/podcast links → `media_posts`
- Audio infra: free-first; adapter for managed providers later

---

## 3. Data Model

### 3.1 Tables

- events(id uuid pk, name text, slug text unique, date timestamptz, venue text, location text, status text, created_at, updated_at)
- fights(id uuid pk, event_id uuid fk, fight_order int, is_main_event bool, is_co_main_event bool, is_title_fight bool, weight_class text, winner_name text, loser_name text, method text, round int, time text, status text, updated_at)
  - unique(event_id, fight_order)
- users(id uuid pk, auth0_sub text unique, handle text, avatar text, created_at)
- predictions(id uuid pk, user_id fk, fight_id fk, pick_name text, locked_at ts, created_at; unique(user_id,fight_id))
- user_scores(user_id fk, elo int default 1000, points int, wins int, losses int, pushes int, updated_at)
- media_posts(id, source, url, title, published_at, tags text[], engagement, created_at)
- debates(id, title, is_audio, room_state, host_user_id, created_at)
- debate_participants(id, debate_id, user_id, role, joined_at, left_at)
- debate_messages(id, debate_id, user_id, message, created_at, pinned bool default false)

### 3.2 Slugs

`ufc-<number>-<main-winner-surname>-<main-loser-surname>` (lowercase, hyphen). Example: `ufc-317-topuria-oliveira`.

---

## 4. Scraper

### 4.1 Sources
- List-of-UFC-events → canonical `date` and event links
- Event page → fights table (8-column), winner/loser/method/round/time

### 4.2 Rules
- Order fights by table row → `fight_order`
- `is_main_event = fight_order == 1`; `is_co_main_event = fight_order == 2`
- Skip rows with empty fighter names
- Patch-only updates: upsert per fight diff; protect unique(event_id, fight_order)

### 4.3 Cadence & Ops
- Daily cron + a finalization run within 12 hours after the event completes
- On-demand refresh endpoint for a single event (admin token)
- Concurrency: 4–6; exponential backoff for 429/5xx; request budget
- Logging: per-event summary (# fights parsed, # updated, warnings)

---

## 5. Backend API (FastAPI)

### 5.1 Auth
- Verify Auth0 RS256 JWT; create user row on first login using `auth0_sub`; attach `user_id` to requests

### 5.2 Predictions
- POST /api/predictions { user_id, fight_id, pick_name }
  - Reject if now >= event card start
  - Upsert predictions (enforce unique(user_id,fight_id))
- GET /api/leaderboard — top N by points desc, elo desc

### 5.3 Admin
- POST /api/admin/scrape/event/:id — on-demand refresh
- POST /api/admin/recompute/elo — replay ELO if needed

---

## 6. Supabase REST Reads (App)

- GET /rest/v1/events?select=*&order=date.desc&limit=50&offset=…
- GET /rest/v1/fights?event_id=eq.<event_id>&order=fight_order.asc
- Search (strict):
  - Step 1: /fights?select=event_id,winner_name,loser_name&or=(winner_name.ilike.%q%,loser_name.ilike.%q%)
  - Filter to whole‑word matches client‑side → event_ids
  - Step 2: /events?select=*&or=(id.eq.id1,id.eq.id2,...)&order=date.desc

---

## 7. Predictions & ELO

### 7.1 Locking
- Predictions disabled at event card start time

### 7.2 Scoring
- K: Main=40, Co‑main=30, Main‑card=25, Prelims=20; Draw/NC=0
- Points: mirror K initially (tunable later)

### 7.3 Worker
- Trigger on fight completion → update `user_scores` (elo, points, wins/losses)
- Emit realtime updates (M2)

---

## 8. iOS App (Flutter)

### 8.1 Screens
- Fight Cards: Past/Upcoming (infinite scroll), search, dark tiles
- Event Details: gradient header, stat tiles, ordered fights, predictions form
- Leaderboard: all‑time ranking
- Feed: embeds + comments
- Debates: list rooms, join audio, text threads, mod controls

### 8.2 UX
- Dark palette (UFC red + slate + emerald accents) with gradients/shimmer
- Emoji-enhanced chips (`🔜 UPCOMING`, `✅ COMPLETED`, `🥇 WINNER`)

---

## 9. Feed & Debates

### 9.1 Feed
- Ingestors: YouTube/X/TikTok/Podcasts → `media_posts`
- Store: url, title, published_at, tags; embed-only rendering

### 9.2 Debates
- Audio rooms (≤10 speakers), host/mod mute, optional record
- Text threads (per event/fight), pinned messages; light moderation
- Audio infra adapter: free-first; upgrade to managed when needed

---

## 10. Notifications (M2+)

- FCM/APNs for pick reminders & results summaries
- Local notifications fallback

---

## 11. DevOps

- Envs: `.env` now; secret manager later
- CI: lint/test/build; formatters enforced
- Deploy: backend (Render/Fly), scraper cron (Cloud Run/Cron), Supabase DB
- Monitoring: Sentry (client/server), uptime pings, scraper logs
- Budget: <$200/month until scale

---

## 12. Local Dev Runbooks

### 12.1 Env
```
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
AUTH0_DOMAIN=...
AUTH0_AUDIENCE=...
```

### 12.2 Scraper
```
python3 scripts/wipe_tables_uuid.py            # careful!
python3 scripts/robust_wikipedia_scraper.py --workers 4 --start-from 0
```

### 12.3 App
```
flutter run
```

---

## 13. Milestones

### M1 (2–3 weeks): Scraper + Cards + Predictions
- Harden scraper (canonical dates, patch-only, backoff)
- Admin on‑demand refresh
- Event slugs + deep link routes
- iOS Past/Upcoming, event details, predictions
- Backend predictions write + lock
- ELO worker; all‑time leaderboard API + screen

### M2 (1–2 weeks): Realtime + Notifications groundwork
- Supabase Realtime for predictions/leaderboard
- Local reminders; push plan
- Admin refresh UI per event

### M3 (3–4 weeks): Feed + Debates
- Feed ingestors (YouTube/X/TikTok/Podcasts) → `media_posts`
- Feed list + embeds + comments
- Debate audio rooms + text threads + mod controls + record option

### M4 (3–6 weeks): Analytics + LLM
- Heuristics (strength-of-schedule, finishing rates)
- Feature store for ML; batch models; insights badges
- LLM Q&A, summaries, explanations; freemium hooks

---

## 14. Risk & Mitigation
- Source HTML drift → parser guards + hash-based change detection
- Legal: embed-only; terms link in settings
- Cost creep: request budgets; ingest caps; disable non-critical jobs if quota
- Quality: idempotent upserts; uniqueness constraints; backfills for known bugs

---

## 15. Future Work
- Android/Web clients
- Advanced odds integrations + sentiment overlays
- Rich ML models (style matchups, transition graphs)
- Tournament/brackets; parlay/propositions (future)
- Community moderation tooling

---

This roadmap is authoritative. Changes should be made via PRs to `ROADMAP.md` with rationale and impact analysis.