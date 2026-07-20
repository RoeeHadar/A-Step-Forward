# Pre-flight checklist — before inviting the cohort

Use **one dry-run learner** + **one dry-run educator** (can be pilot lead). Fix every **P0** before day 1.

Environment: production. Locale: Hebrew.

## Learner core path

- [ ] Sign-in / sign-up works  
- [ ] `/identity` → learner + username  
- [ ] Onboarding completes → lands on `/app` with a plan  
- [ ] Open at least one lesson; math renders (no red KaTeX boxes)  
- [ ] Start weekly quiz or mock (items load; submit does not 500)  
- [ ] Notifications / friend request send does not error  
- [ ] Teacher invite can be accepted  
- [ ] `/app/chat/tutor` — 3 turns stream OK  

## Educator core path

- [ ] `/identity` → educator  
- [ ] `/educator` loads roster  
- [ ] Send teacher invite; see linked student after accept  
- [ ] Open `/educator/students/[id]` — overview shows goal/hours/week  
- [ ] Plan tab: change hours + reason → save → student notified  
- [ ] Tests tab: list attempts if any; grade/feedback save OR document empty-state OK  

## Seed smoke (optional but recommended)

- [ ] `seed-pilot-demo --variant building` on dry-run learner → readiness mock-gated ~70%  
- [ ] Flip to `at-risk` → behind-pace badge  
- [ ] Reset dry-run accounts after smoke  

## Gate

| Result | Action |
|--------|--------|
| Any core-path blocker | **Do not** invite cohort until fixed |
| Polish / content nits | Proceed — cohort will score them |

Signed off by: __________ Date: __________
