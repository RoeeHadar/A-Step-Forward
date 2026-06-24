# ADR-003: Clerk Dev Instance (No Custom Domain)
Status: Accepted
Date: 2026-06-24

## Context
- Auth needs to be secure, fast to implement, and support OAuth + email/passkey flows.
- Clerk is the chosen auth provider (excellent Next.js integration, RBAC, parental controls).
- A Clerk production instance requires a verified custom domain.
- The custom domain `astepforward.app` is not yet configured (DNS setup pending).
- Clerk dev instances work on any domain including Vercel preview URLs.

## Decision
- Use Clerk dev instance keys (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starting with `pk_test_`)
- Dev instance is fully functional for development, testing, and early user demos
- Production instance creation is deferred until the custom domain is configured

## Consequences
- Positive: Auth works immediately on the Vercel deployment without custom domain setup.
- Trade-off: Dev instance keys must be rotated before public production launch.
- Trade-off: Clerk dev instances show a banner in the Clerk dashboard indicating dev mode.
- Action required before launch: Configure `astepforward.app` DNS, create Clerk production instance, rotate all Clerk keys.
