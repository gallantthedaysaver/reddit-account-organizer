# Security Policy

## Reporting a vulnerability

Please do not post credentials, OAuth tokens, private Reddit account data, or other secrets in a public issue.

For now, security issues can be reported to the repository owner through GitHub. A private vulnerability-reporting channel may be added before a broader public release.

## Secrets

Reddit client secrets, Flask secret keys, OAuth tokens, and local user data must not be committed to the repository. Use the local `.env` file described in `.env.example`. `.env` and `data/` are excluded by `.gitignore`.

## Destructive actions

The application defaults to `READ_ONLY=true`. Any future unsubscribe or Custom Feed modification UI should require explicit user selection and confirmation, and should create a timestamped backup before changing account state.
