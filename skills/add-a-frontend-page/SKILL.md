---
name: add-a-frontend-page
description: How to add a Next.js 15 page in apps/web using App Router, RSC, Tailwind v4 + shadcn/ui, TanStack Query, Zod, and Vercel AI SDK. Read BEFORE adding or modifying any route in apps/web/.
---

# Add a Frontend Page

## When to use
Adding a route under `apps/web/src/app/...` or a feature component under `apps/web/src/components/...`.

## Steps

1. **Decide RSC vs Client**. Default to RSC. Add `"use client"` only if you need state, effects, or browser APIs.
2. **Create the route**:
   ```
   apps/web/src/app/<segment>/page.tsx
   apps/web/src/app/<segment>/loading.tsx
   apps/web/src/app/<segment>/error.tsx
   ```
3. **Data fetching**:
   - RSC reads: call the API via `fetch` with `cache: 'no-store'` for personalized data, `revalidate` otherwise.
   - Client reads: TanStack Query.
   - Validate every response with Zod from `packages/schemas/ts/`.
4. **Mutations**:
   - Server actions for form submissions.
   - Streaming agent calls via Vercel AI SDK (`useChat`).
5. **Styling**:
   - Tailwind v4 + shadcn/ui primitives. Use the `shadcn` MCP to scaffold.
   - Respect dark mode, reduced-motion, and the design tokens in `apps/web/src/lib/design-tokens.ts`.
6. **Accessibility**:
   - Semantic HTML; labels on inputs; focus states; aria-*.
   - Test keyboard navigation; lint with `eslint-plugin-jsx-a11y`.
7. **Auth / RBAC**:
   - Wrap pages in the auth boundary (Clerk).
   - Server actions verify role via the `getAuth()` helper.
8. **Tests**:
   - Vitest for components.
   - Playwright E2E for the user flow.

## Patterns to copy
- Streaming chat → `apps/web/src/app/(app)/app/chat/[agent]/page.tsx`.
- Server action mutation → `apps/web/src/app/(app)/app/memory/actions.ts`.
- Dashboard page → `apps/web/src/app/(app)/app/progress/page.tsx`.

## Pitfalls
- No `any`. No `console.log` in shipped code (use `logger`).
- Don't fetch inside a loop in RSC; batch.
- Don't add a global state store for something a few props can do.
- Don't import server-only modules into a client component (mark with `import 'server-only'`).

## ESLint errors fail the build — check before pushing

Next.js runs ESLint as part of `next build`. Any ESLint **error** (not just warning)
causes the build to exit with code 1 on Vercel. The most common ones to watch for:

- `@typescript-eslint/no-unused-vars` — remove any destructured variables that are never read
- `jsx-a11y/*` — every interactive element needs an accessible name/label
- `@next/next/no-html-link-for-pages` — use `<Link>` from `next/link`, not `<a>`

**Always run `npx next lint --dir src` before pushing** to catch these locally.

## ESM-only packages — MUST add to `transpilePackages`

Several popular packages ship as **pure ESM** and will cause a Vercel build failure
("require() of ES Module") unless explicitly listed in `apps/web/next.config.mjs`
under `transpilePackages`. **Always add a new ESM-only package to that list.**

Known ESM-only packages used in this project (already in `transpilePackages`):
- `react-markdown` v9+
- `remark-gfm` v4+, `remark-math` v6+
- `rehype-katex` v7+, `rehype-highlight` v7+
- `unified`, `bail`, `is-plain-obj`, `trough`, `vfile`, `vfile-message`
- `unist-util-stringify-position`, `mdast-util-*`, `micromark`, `micromark-*`

To check if a package is ESM-only: look for `"type": "module"` in its `package.json`
or the absence of a `main` field paired with an `exports` map that has no `require`
entry. When in doubt, add it to `transpilePackages`.
