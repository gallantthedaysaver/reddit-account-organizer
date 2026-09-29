# Reddit Account Organizer v0.1.0

Self-hosted Docker prototype for reviewing Reddit subscriptions and Custom Feeds.

## Important Reddit API note
Reddit currently requires registered OAuth access for Data API clients and may require approval for a use case. This project does not scrape Reddit. If Reddit does not grant your app access to a particular account-data endpoint, that feature will report unavailable rather than bypassing Reddit's controls.

## Setup
1. Obtain/register approved Reddit Data API/OAuth credentials for this use case.
2. Copy `.env.example` to `.env`.
3. Fill in `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and a descriptive `REDDIT_USER_AGENT`.
4. Leave `READ_ONLY=true` initially.
5. From this directory run: `docker compose up -d --build`
6. Open `http://localhost:8787`.
7. Connect Reddit and first use **Backup subscriptions CSV**.

The redirect URI configured with Reddit must exactly match `http://localhost:8787/oauth/callback` unless you change it in `.env`.

## Current prototype features
- OAuth login
- Fetch subscribed communities (when authorised by Reddit)
- Member count / NSFW flag
- Activity analysis: newest post, days since newest post, posts among the latest 100 in the last 7/30 days
- Custom Feed discovery via the legacy OAuth multireddit route, with graceful failure if unavailable
- CSV subscription backup
- Docker health endpoint at `/health`
- Destructive unsubscribe endpoint implemented but blocked by default with `READ_ONLY=true`

## Next milestones
- Background job/progress UI so large accounts do not block one request
- SQLite caching and timestamped backups before every change
- Sortable columns and richer cleanup filters
- Custom Feed membership matrix
- Confirmation UI for unsubscribe/removal actions
- Restore/import tools
- Tests and public-release docs (LICENSE, SECURITY.md, CONTRIBUTING.md)
