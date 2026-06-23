# Clerk JWT (production)
# Set CLERK_JWKS_URL to enable Bearer-token auth; omit it for local dev headers.
CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json
CLERK_ISSUER=https://<your-clerk-domain>
CLERK_AUDIENCE=

# Local dev (when CLERK_JWKS_URL is empty)
# curl -H "X-Learner-Id: learner-1" http://localhost:8000/v1/learners/me
