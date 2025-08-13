# MMAmania

A dark, modern iOS app for UFC events, fights, predictions and debates.

## v1 Scope
- iOS only, Auth0 auth (map `auth0_sub` 1:1)
- Daily scraping, patch-only updates, 12h post-event freshness
- Infinite scroll events (50 at a time), event details
- Predictions lock at card start, ELO/points (Main=40, Co=30, Main-card=25, Prelims=20; Draw/NC=0)
- All‑time leaderboard
- Feed (link/embed), Debates (audio≤10 + text), dark theme

## Architecture
- Scraper (Python) → Supabase (Postgres)
- Backend (FastAPI): Auth verify, predictions writes/locking, ELO worker, admin
- App (Flutter iOS): reads via Supabase REST; realtime later

## Data Model
- events(id, name, slug, date, venue, location, status)
- fights(id, event_id, fight_order, is_main_event, is_co_main_event, is_title_fight,
  weight_class, winner_name, loser_name, method, round, time, status)
- users(id, auth0_sub, handle, avatar)
- predictions(id, user_id, fight_id, pick_name, locked_at)
- user_scores(user_id, elo, points, wins, losses, pushes)
- media_posts(...), debates(...)

## Scraper
- List page → canonical date; Event page → fights
- Fight order by table; idempotent patch; skip blanks
- Cron daily + post‑event; on‑demand refresh endpoint

## APIs
- GET /rest/v1/events?order=date.desc&limit=50&offset=…
- GET /rest/v1/fights?event_id=eq.<id>&order=fight_order.asc
- Search strict: fighter/title whole‑word
- POST /api/predictions { user_id, fight_id, pick_name }
- GET /api/leaderboard

## Predictions & ELO
- Lock at card start; weights above; update on fight completion

## iOS
- Dark gradient UI, Past/Upcoming, details, predictions, leaderboard, feed, debates

## Dev
- .env: SUPABASE_URL, SUPABASE_SERVICE_KEY, AUTH0_DOMAIN, AUTH0_AUDIENCE
- Scraper: `python3 scripts/robust_wikipedia_scraper.py --workers 4`
- iOS: `flutter run`

## Milestones
- M1: Scraper + Cards + Predictions + Leaderboard
- M2: Realtime + Notifications groundwork + Admin refresh
- M3: Feed + Debates
- M4: Analytics + LLM
