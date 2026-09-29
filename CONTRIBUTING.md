# Contributing

Reddit Account Organizer is currently an early prototype. Contributions are welcome once the core Reddit API access path has been validated.

## Development

1. Fork or clone the repository.
2. Copy `.env.example` to `.env` and configure your own approved Reddit OAuth credentials.
3. Keep `READ_ONLY=true` while developing unless you are intentionally testing an account-changing operation.
4. Run with `docker compose up -d --build`.
5. Do not commit `.env`, OAuth tokens, credentials, exports, or other user-specific Reddit data.

## Design principles

- Use authorized Reddit APIs; do not add web-scraping workarounds for unavailable account data.
- Respect Reddit rate limits and cache responsibly.
- Keep account-changing operations separate from analysis and require explicit confirmation.
- Preserve the self-hosted Docker deployment.
- Treat subscriptions and Custom Feed membership as separate account states.

Before a wider public release, contribution workflow, tests, formatting, and issue templates will be expanded.
