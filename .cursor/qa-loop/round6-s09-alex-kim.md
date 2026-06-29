# S09 — Alex Kim QA Simulation Report
## Round 6 · "A Step Forward" Student Simulator

**Simulated:** 2026-06-29  
**Persona:** Alex Kim, University 1st Year CS, Korean background, international high school in Israel, English-only, Calculus 1 final exam in 8 weeks, weak in epsilon-delta limits / sequences-series convergence / Riemann integrals.

---

## Full JSON Report

```json
{
  "student_id": "S09_alex_kim",
  "rubric_scores": {
    "learning_improvement_progress": {
      "score": 7,
      "weight": 0.20,
      "weighted": 1.40,
      "notes": "Dashboard next-lesson logic works, mastery engine feeds quiz results, adaptive difficulty present. Gaps: no Calc1-specific exam countdown, missing seq/series lesson breaks the learning plan."
    },
    "material_coverage_calc1": {
      "score": 4,
      "weight": 0.20,
      "weighted": 0.80,
      "notes": "limits.json and derivatives_intro.json exist and are high quality. BUT: (a) limits.json tagged high_school/5pt with no calc1 body_by_level block; (b) uni_sequences_series has NO authored lesson file; (c) epsilon-delta appears only briefly in a pitfall sidebar; (d) no university-depth Riemann sums treatment."
    },
    "language_fit_english_only": {
      "score": 6,
      "weight": 0.15,
      "weighted": 0.90,
      "notes": "App is fully bilingual and renders 100% English once preference is set. Critical issue: default language is Hebrew (useLanguagePreference default='he') so first load is confusing. Tutor agent persona also defaults to HE, requiring Alex to chat in English before the agent matches his language."
    },
    "retention_memory_tab": {
      "score": 7,
      "weight": 0.10,
      "weighted": 0.70,
      "notes": "Memory page fully bilingual EN. Searchable, editable, deletable with audit trail. Memory is written by agents during sessions. No static issues found."
    },
    "accessibility": {
      "score": 7,
      "weight": 0.10,
      "weighted": 0.70,
      "notes": "aria-labels on sliders, quiz buttons use aria-pressed, KaTeX renders math as semantic HTML. Minor: quiz difficulty badge shows raw 'easy/medium/hard' (acceptable for EN user). No skip-nav or focus-trap management detected."
    },
    "uniqueness_ai_vs_textbook": {
      "score": 8,
      "weight": 0.10,
      "weighted": 0.80,
      "notes": "Multi-agent system (Tutor/Coach/Mentor/Reviewer), Socratic pacing, agent_hints misconception injection, mastery-based quiz, memory persistence across sessions. Genuinely differentiated from a textbook or ChatGPT."
    },
    "exam_success_likelihood": {
      "score": 4,
      "weight": 0.15,
      "weighted": 0.60,
      "notes": "Alex's three declared weak areas are poorly supported: epsilon-delta has no dedicated content at university level, uni_sequences_series has no lesson, Riemann integrals lesson exists but not at university depth. No notation-difference guidance (Israeli vs US style). No past-exam Calc1 practice papers."
    }
  },
  "final_weighted_score": 5.90,
  "checkpoints": [
    {
      "label": "Day 1",
      "narrative": "I land on the site after my professor mentioned it in the first lecture. The page is in Hebrew. I can read a bit but it's not comfortable for a 60-minute study session. I find the EN/עב toggle in the header and flip to English — the entire page reflows instantly. Nice. I go through onboarding: I select 'University — Calculus 1' from the goals list (it's right there, no 'Other' workaround needed), set grade level to 'University — 1st year', set the final exam date 8 weeks out. The self-assessment step shows me 6 Calc 1 concepts as sliders: limits, derivatives_intro, derivatives_rules, derivatives_applications, integrals_intro, definite_integrals. I rate myself 3/10 on limits and 2/10 on derivatives, honest about where I am. I'm directed to the diagnostic — the flow feels clean and purposeful. First impression: this is more structured than random YouTube videos. Slight annoyance: I had to toggle the language myself on arrival. Why doesn't it detect my browser locale?",
      "ux_score": 7,
      "stress_level": 3,
      "knowledge_scores": {
        "limits": 3,
        "derivatives_intro": 4,
        "derivatives_rules": 3,
        "integrals_intro": 3,
        "definite_integrals": 3,
        "uni_sequences_series": 2
      },
      "green_lights": [
        "'University — Calculus 1' goal exists as a first-class option in onboarding",
        "Goal date / exam date fields work perfectly — 8-week timeline set",
        "Language toggle in header immediately affects the whole onboarding page",
        "Self-assessment shows Calc1-specific concepts (limits, derivatives) not irrelevant high-school topics",
        "Smooth 4-step onboarding flow, no dead ends"
      ],
      "red_flags": [
        "Default language is Hebrew on first load — international student sees Hebrew before finding the toggle",
        "No browser locale detection (navigator.language) — Korean/English browser users still get Hebrew default",
        "No 'notation style' question in onboarding (Israeli vs US/AP Calc notation differences not captured)"
      ],
      "would_continue": true
    },
    {
      "label": "Week 1",
      "narrative": "I've set up my account and I'm exploring. The dashboard in English looks clean. I navigate to Lessons and see a 'University — Calculus 1' section. I open the Limits lesson first — it's well written. The intro walks through the classic (x²-1)/(x-1) factoring example, there are worked examples with conjugates, and the summary is tight. Math renders beautifully with KaTeX. I want to go deeper on epsilon-delta though — that's the part my professor actually tests. I search in the lesson but can't find a dedicated epsilon-delta section. There's a brief formal definition (∀ε>0, ∃δ>0...) buried inside the 'common pitfalls' sidebar body, but it's not explained or practiced. That's frustrating — my biggest gap and it's just a footnote. I then try the Tutor chat. The first message the Tutor sends is in Hebrew. I type 'Hello, can we work in English?' and the Tutor immediately switches. After that the conversation is great — Socratic, asks me what I already know, gives me a worked limit example. I also try the quiz builder. I set it to 10 minutes, mixed questions, select 'Limits' and 'Derivatives' topics. The quiz generates in about 8 seconds, all in English, with nice KaTeX rendering. Score: 5/10, but I get instant explanations for each wrong answer. Useful.",
      "ux_score": 7,
      "stress_level": 5,
      "knowledge_scores": {
        "limits": 4,
        "derivatives_intro": 5,
        "derivatives_rules": 4,
        "integrals_intro": 3,
        "definite_integrals": 3,
        "uni_sequences_series": 2
      },
      "green_lights": [
        "Limits lesson is well-authored with good examples (conjugate trick, one-sided limits, infinity)",
        "KaTeX renders math correctly and LTR even in English mode",
        "Quiz builder works fully in English, topic selection clear",
        "Quiz generates fast and feeds mastery scores back to the system",
        "Tutor agent responds in English after first message clarification",
        "Per-question explanations after quiz submission are genuinely helpful"
      ],
      "red_flags": [
        "Tutor agent first response is in Hebrew (default) despite app being set to English — confusing and forces the user to explicitly request English",
        "No dedicated epsilon-delta section in Limits lesson — formal definition only appears briefly in a 'pitfall' sidebar, not as a teachable section with practice",
        "Limits lesson has no 'calc1' level body_by_level block — it serves university students the same content as 5pt high-school track",
        "Lesson page has hardcoded 'Back to lessons' string (minor for EN users but reveals i18n incompleteness)",
        "lesson.est_minutes displayed as '{n} min · math' — 'min' and subject name 'math' are not localized"
      ],
      "would_continue": true
    },
    {
      "label": "Week 3",
      "narrative": "I'm now regularly using the Tutor (evenings, ~55 min sessions). It's genuinely helpful for derivatives — the agent gives me Socratic prompts, catches my recurring mistake of confusing f(a) with f'(a) exactly as predicted by the lesson's misconception detector. That surprised me positively. I'm working through the learning plan. But when I try to study Sequences and Series — my professor just covered ratio test and comparison test, which I'm completely lost on — I search the Lessons page and find... nothing for university sequences/series. The concept 'Sequences & Series (University)' exists in the quiz topic picker but there's no authored lesson behind it. I generate a quiz on it and get questions, but when I get things wrong I don't know where to go to learn the material. I ask the Tutor 'Can you teach me about series convergence?' and get a solid verbal explanation via chat, but without a structured lesson to back it up the learning is fragile. I check the memory page to see what the system remembers about me — it shows a few notes from my sessions: 'struggles with limit definition notation', 'prefers worked examples over theory first'. That's accurate and reassuring.",
      "ux_score": 6,
      "stress_level": 7,
      "knowledge_scores": {
        "limits": 5,
        "derivatives_intro": 6,
        "derivatives_rules": 5,
        "integrals_intro": 4,
        "definite_integrals": 4,
        "uni_sequences_series": 2
      },
      "green_lights": [
        "Tutor correctly detects and corrects f(a) vs f'(a) misconception (agent_hints system working)",
        "Socratic dialogue keeps sessions engaging across 55-min sessions",
        "Memory page shows accurate, English-language notes about Alex's learning patterns",
        "Memory entries are editable and deletable — trust and transparency respected",
        "Quiz can be generated for uni_sequences_series topic even without a lesson"
      ],
      "red_flags": [
        "CRITICAL: uni_sequences_series has no authored lesson file — the concept exists in the KG and quiz but the 'Lessons' tab returns nothing, creating a dead end for Alex's primary weak area",
        "Without a lesson, wrong quiz answers have nowhere to send Alex for remediation",
        "Tutor can explain convergence via chat but this is fragile and doesn't build mastery systematically",
        "No 'Exam prep' or 'Past paper practice' mode — 5 weeks to go and no exam-mode drill"
      ],
      "would_continue": true
    },
    {
      "label": "Week 6",
      "narrative": "I'm in the final push. I now use the Coach agent for timed drills — it's fast and efficient. I do 20-minute sprint sessions with the quiz builder every other night. The weakest-concept picking works well — it keeps sending me limits and integrals questions I keep getting wrong. I look at the Progress tab: I can see my mastery scores going up for derivatives (now at 0.72 equivalent) but limits is stuck around 0.45. I try once more to find epsilon-delta practice — the only thing I can find is the brief definition in the Limits pitfall section. My professor just gave us a problem set with 6 epsilon-delta proofs. I use the Tutor to work through them conversationally — the agent handles the ∀ε∃δ notation correctly and catches when I write the wrong direction of the implication. But there's no structured practice quiz or lesson for this. Also, I try to search for 'Riemann sums' in the quiz builder — I see 'Definite Integrals' as a topic, generate a quiz. The questions are mostly about computing definite integrals with FTC, not about constructing Riemann sums or proving that a function is Riemann-integrable. My exam will definitely have a Riemann sum problem. Stress is rising.",
      "ux_score": 6,
      "stress_level": 8,
      "knowledge_scores": {
        "limits": 5,
        "derivatives_intro": 7,
        "derivatives_rules": 6,
        "integrals_intro": 6,
        "definite_integrals": 5,
        "uni_sequences_series": 3
      },
      "green_lights": [
        "Coach agent works well for timed drill sessions",
        "Quiz weakest-concept selection is accurate — keeps routing me to my gaps",
        "Progress page shows per-concept mastery over time in English",
        "Tutor handles formal epsilon-delta notation correctly in chat (∀ε∃δ, correct implication direction)",
        "Agent memory correctly notes my struggle with limits after 6 weeks — personalization is real"
      ],
      "red_flags": [
        "CRITICAL: Still no epsilon-delta lesson or practice set after 6 weeks — must rely on unstructured Tutor chat",
        "Definite Integrals quiz focuses on FTC computation, not Riemann sum construction — exam-relevant gap",
        "No 'Exam mode' — no timed past-paper simulation or mock exam for university Calc1",
        "No notification/reminder system as exam approaches (8-week countdown entered at onboarding but nothing uses it in the UI)",
        "University Calc1 learner gets the same Limits lesson as a high-school 5pt student — no depth differentiation"
      ],
      "would_continue": true
    },
    {
      "label": "Week 8",
      "narrative": "Exam is tomorrow. I've been using the platform for 2 months. For derivatives and basic limits I feel genuinely more confident — the combination of Socratic Tutor, quick Coach drills, and adaptive quizzes has been more effective than my textbook. The memory system keeps the context fresh; I don't have to re-explain my background in every session. But I'm going into the exam with two unresolved gaps: (1) epsilon-delta proofs — I had to supplement with Khan Academy and StackExchange because this platform never gave me structured practice; (2) series convergence (ratio test, comparison test, divergence test) — I learned these entirely from the Tutor chatting, not from any lesson. The quiz questions for sequences were decent but I had nowhere to go when I got them wrong. Overall: this platform is excellent for derivatives and 'standard' limits, and the AI agents are far better tutors than any textbook. But as a university Calc1 student I hit two hard walls — missing content — that a high-school 5pt student wouldn't hit. If those gaps were filled I'd give this an 9/10. As it stands: 6/10.",
      "ux_score": 6,
      "stress_level": 9,
      "knowledge_scores": {
        "limits": 6,
        "derivatives_intro": 8,
        "derivatives_rules": 7,
        "integrals_intro": 7,
        "definite_integrals": 6,
        "uni_sequences_series": 4
      },
      "green_lights": [
        "Derivatives mastery genuinely improved from ~3 to ~8 over 8 weeks",
        "Socratic Tutor + adaptive quiz combination is genuinely superior to textbook study",
        "Memory personalization persists correctly across all 8 weeks — no cold-start after day 3",
        "Agent correctly handles university-level math notation in chat (Leibniz, Lagrange, ∀ε∃δ)",
        "English-only experience is seamless once language is set — no Hebrew leakage after day 1"
      ],
      "red_flags": [
        "CRITICAL: Still no epsilon-delta lesson after 8 weeks — had to use external resources",
        "CRITICAL: uni_sequences_series still has no lesson — convergence tests not systematically covered",
        "University Calc1 depth is effectively the same as 5pt high school — no notation-difference guidance",
        "No past-paper / mock-exam mode for university courses",
        "App was in Hebrew on first load — bad first impression for international student"
      ],
      "would_continue": true
    }
  ],
  "issues": [
    {
      "id": "ISSUE-S09-001",
      "category": "missing_feature",
      "severity": "critical",
      "description": "uni_sequences_series concept has no authored lesson JSON file. The concept exists in the KG, appears in the Calc1 goal track, is available in the quiz builder, but clicking into Lessons returns nothing. Alex's declared weak area (series convergence, ratio test, comparison test) has zero structured content.",
      "root_cause": "scripts/seed_data/lessons/uni_sequences_series.json does not exist. The concept ID is registered in onboarding CONCEPTS_BY_GOAL.calculus1 and in curriculum-categories but no lesson was authored.",
      "suggested_fix": "Author a university-level sequences and series lesson (uni_sequences_series.json) covering: definition of sequence convergence, squeeze theorem for sequences, series definition, divergence test, comparison test, ratio test, alternating series test, power series radius of convergence. Add body_by_level.calc1 block. Tag math_track: ['calc1'].",
      "affects_students": ["university"]
    },
    {
      "id": "ISSUE-S09-002",
      "category": "content",
      "severity": "critical",
      "description": "No epsilon-delta lesson or dedicated practice section exists at any level. The formal ε-δ definition appears once, briefly, inside the 'pitfall' sidebar of limits.json body_by_level.5pt — it is not a teachable section, has no practice questions, and is tagged for high-school 5pt not for university.",
      "root_cause": "limits.json is designed for Bagrut 5pt (high school). No separate university-level limits content was authored. The concept 'epsilon_delta_limits' does not even exist as a skill_atom in limits.json's agent_hints.",
      "suggested_fix": "Add a body_by_level.calc1 section to limits.json with a full epsilon-delta treatment: motivation, formal definition, worked proof that lim(x→2)(3x+1)=7, practice problems in the epsilon-delta style. Alternatively author a new concept 'epsilon_delta_proofs' as a university sub-lesson. Add skill_atoms: epsilon_delta_definition, epsilon_delta_proof_linear, epsilon_delta_proof_quadratic.",
      "affects_students": ["university"]
    },
    {
      "id": "ISSUE-S09-003",
      "category": "ux",
      "severity": "high",
      "description": "Default language on first load is Hebrew (useLanguagePreference default='he'; readInitial() falls through to 'he' if no localStorage/cookie). International students with English-only browsers land on a fully Hebrew page and must discover the toggle manually.",
      "root_cause": "use-language-preference.ts line 44: useLanguagePreference(defaultLang: Lang = 'he'). readInitial() only checks navigator.language as a last fallback when it starts with 'en'. All other cases fall through to the passed defaultLang. The I18nProvider likely passes no explicit default, inheriting 'he'.",
      "suggested_fix": "Change readInitial() to check navigator.language FIRST (before localStorage), falling back to 'he' only when the browser language is not detectable or starts with 'he'. Alternatively, change defaultLang to 'he' only when no signal is available and the browser language is Hebrew.",
      "affects_students": ["university", "5pt", "4pt", "3pt", "physics"]
    },
    {
      "id": "ISSUE-S09-004",
      "category": "content",
      "severity": "high",
      "description": "All Calc1 lessons (limits, derivatives, integrals) are tagged level='high_school' and math_track=['4pt' or '5pt']. No lesson has a body_by_level.calc1 block. University students receive identical content depth as Bagrut 5pt students, missing key university-specific content: proof by epsilon-delta, formal series convergence, Riemann sum construction, L'Hôpital's rule at full rigour.",
      "root_cause": "Lessons were authored for the Israeli high school Bagrut curriculum. University track (calc1) was added later to onboarding and KG but no lesson body_by_level depth was added for it.",
      "suggested_fix": "For each lesson in the calc1 track (limits, continuity, derivatives_intro, derivatives_rules, integrals_intro, definite_integrals, integrals_techniques), add a body_by_level.calc1 section with university-appropriate depth: formal proofs, rigorous notation, and exam-style questions. Also add body_by_level.calc1 questions in the questions array.",
      "affects_students": ["university"]
    },
    {
      "id": "ISSUE-S09-005",
      "category": "bilingual",
      "severity": "high",
      "description": "Tutor agent first response is in Hebrew by default, even when the entire UI is set to English. The agent persona states 'Match the learner's language (HE default)' — meaning it requires the learner to type in English first before the agent infers the preferred language. English-only learners (Alex) face a confusing first message in a foreign script.",
      "root_cause": "The Tutor prompt in agent-prompts.ts says 'Match the learner's language (HE default)'. Language preference (stored in localStorage/cookie) is not injected into the system prompt — the agent has no signal about Alex's UI language preference on turn 1.",
      "suggested_fix": "Inject the learner's language preference into the system prompt (alongside profile, mastery, etc.) in apps/web/src/app/api/chat/route.ts. Something like: 'Learner language preference: en. Respond in English by default.' This is a one-line change in the context builder.",
      "affects_students": ["university", "5pt"]
    },
    {
      "id": "ISSUE-S09-006",
      "category": "content",
      "severity": "high",
      "description": "Definite Integrals quiz/lesson covers FTC-based computation but does not address Riemann sum construction (left/right/midpoint sums, upper/lower sums, limit of Riemann sums). University Calc1 exams consistently test this; the platform would leave Alex unprepared.",
      "root_cause": "definite_integrals.json was authored with high-school Bagrut content focus (FTC, area computation). Riemann sum construction as a formal limit is university-level content that was not included.",
      "suggested_fix": "Add a body_by_level.calc1 section to definite_integrals.json covering: definition of Riemann sums (left, right, midpoint, upper, lower), the limit definition ∫f(x)dx = lim(n→∞) Σf(xᵢ*)Δx, worked examples with explicit sum notation, questions testing Riemann sum construction.",
      "affects_students": ["university"]
    },
    {
      "id": "ISSUE-S09-007",
      "category": "missing_feature",
      "severity": "medium",
      "description": "No notation-difference guidance anywhere in the platform. Israeli university textbooks use different notation from US/AP Calculus (e.g., different integral notation styles, derivative notation mixing). Alex's onboarding background note mentions this but the platform has no agent hint, curriculum note, or onboarding question to capture and address it.",
      "root_cause": "The platform was designed primarily for Israeli students. International students studying in Israeli universities with different notation backgrounds are not yet a design consideration.",
      "suggested_fix": "Add a notation-awareness note to the Tutor and QA Explainer system prompts for calc1 track learners. In the agent baseline, inject a 'notation note' when the learner's profile indicates international background or calc1 track. Example: 'This learner may be unfamiliar with Leibniz vs Lagrange notation — briefly note both when introducing a new derivative concept.'",
      "affects_students": ["university"]
    },
    {
      "id": "ISSUE-S09-008",
      "category": "missing_feature",
      "severity": "medium",
      "description": "No exam-mode or mock-exam feature. The onboarding collects the exam date (Alex's was set to 8 weeks out) but this information is never surfaced again as a countdown, an urgency signal, or a 'mock exam' trigger. Alex has to manually manage his exam preparation without platform-level exam awareness.",
      "root_cause": "The next_test_date and final_goal_date fields are stored in the learner profile (submitted via /api/onboarding/submit) but the dashboard and learning plan do not display a countdown or adaptive urgency mode.",
      "suggested_fix": "Display a 'Exam in N days' countdown on the dashboard. When N < 14, surface a 'Exam prep mode' CTA that shifts the quiz builder default to 'mixed, exam-length (45 min), hardest topics'. This is a dashboard UI + learning_plan.next() signal change.",
      "affects_students": ["university", "5pt", "4pt", "3pt", "physics"]
    },
    {
      "id": "ISSUE-S09-009",
      "category": "content",
      "severity": "medium",
      "description": "Several body_by_level sections in lesson JSON files have truncated Hebrew body content. Observed in derivatives_intro.json (body_he_md lines ending mid-sentence), limits.json (pitfall body_he_md is entirely in English despite the he field). These do not affect Alex (English-only) but would break Hebrew university students.",
      "root_cause": "AI-generated body_by_level content was not fully validated. Some body_he_md fields appear to have been truncated at generation time.",
      "suggested_fix": "Run a validation script that checks all body_he_md fields in body_by_level sections for truncation (e.g., body ends without a sentence terminator or is identical to the English body). Flag for re-generation or manual completion.",
      "affects_students": ["university", "5pt"]
    },
    {
      "id": "ISSUE-S09-010",
      "category": "ux",
      "severity": "low",
      "description": "The lesson page (`l/[lessonId]/page.tsx` line 67) has a hardcoded 'Back to lessons' link that is not run through i18n. Also the lesson metadata line shows '{n} min · {subject}' where 'min' and the subject name are not localized.",
      "root_cause": "The lesson page server component was not fully wired to i18n messages (it uses a different locale resolution path from the client components that use useI18n()).",
      "suggested_fix": "Move the lesson page strings into the i18n messages.ts file under messages.lessons.backToLessons and messages.lessons.minutesLabel. Pass them as props to a wrapper or use a thin client component to access useI18n().",
      "affects_students": ["university", "5pt", "4pt", "3pt", "physics"]
    }
  ],
  "final_satisfaction": 6,
  "final_knowledge_gain": "fair",
  "summary": "Alex Kim achieves solid improvement in derivatives and basic limits (the platform's strongest content areas) but hits hard walls on his two primary exam weaknesses: epsilon-delta proofs have no dedicated content at university depth, and the sequences/series convergence concept has no authored lesson at all. The AI agent experience (Socratic Tutor, adaptive Coach, memory persistence) is genuinely differentiated and better than a textbook, but the university-specific content depth is currently identical to the high-school 5pt track. To serve university Calc1 students adequately, the platform needs: (1) uni_sequences_series.json authored, (2) body_by_level.calc1 blocks added to all Calc1 lessons, (3) learner language preference injected into the agent system prompt so the first turn is not in Hebrew."
}
```

---

## Weighted Score Summary

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Learning improvement / progress | 20% | 7/10 | 1.40 |
| Material coverage — Calc1 topics | 20% | 4/10 | 0.80 |
| Language fit — English only | 15% | 6/10 | 0.90 |
| Retention — memory tab | 10% | 7/10 | 0.70 |
| Accessibility | 10% | 7/10 | 0.70 |
| Uniqueness — AI vs textbook | 10% | 8/10 | 0.80 |
| Exam success likelihood | 15% | 4/10 | 0.60 |
| **TOTAL** | **100%** | | **5.90 / 10** |

**Verdict: FAIL** (threshold: 8.5). Alex would partially benefit from the platform but would need to supplement with external resources for his most exam-critical weak areas.

---

## Top 3 Improvement Recommendations (Priority Order)

### P1 — Author `uni_sequences_series.json` lesson [CRITICAL, ~4 days work]
This is Alex's declared weak area and currently a dead end. The concept exists in the KG and quiz engine but has no lesson. A full university-level lesson covering sequence convergence, series convergence tests (divergence, comparison, ratio, alternating series), and power series would close the biggest single gap for all university track learners.

### P2 — Add `body_by_level.calc1` blocks to existing Calc1 lessons [CRITICAL, ~3 days work]
`limits.json`, `derivatives_intro.json`, `definite_integrals.json`, and `integrals_intro.json` all serve university students the same content as high-school 5pt students. Adding `body_by_level.calc1` sections with epsilon-delta proofs, rigorous Riemann sum treatment, and university-exam-style questions would differentiate the experience meaningfully.

### P3 — Inject learner language preference into agent system prompt [HIGH, ~1 hour work]
One line in `apps/web/src/app/api/chat/route.ts`: read the locale from the learner's profile or the request cookie and inject `"Learner language preference: en. Respond in English by default."` into the context block before the agent persona. This prevents the jarring Hebrew first-response for English-only users and removes the need to manually instruct the agent on every new session.
