# Security policy

This repository must remain safe to publish.

Do not open a public issue containing a credential or private data. Revoke the
credential first, remove it from Git history, then use GitHub's private
security-advisory channel for any remaining report.

## Never commit

- API keys, tokens, cookies, private keys, or OAuth state;
- `.env` files, auth files, or machine-local settings;
- transcripts, memories, browser profiles, or caches;
- private knowledge-base content;
- absolute personal home paths.

## Supply-chain policy

Third-party skills must have an explicit redistribution license, a full commit
pin, preserved attribution, and a manual review of scripts and dependencies.
Upstream changes are never merged automatically.
