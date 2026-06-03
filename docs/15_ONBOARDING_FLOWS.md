# Document 15 — Onboarding Flows
## User Journeys, Friction Analysis, and Onboarding Checklist Design

---

## 1. DESIGN PRINCIPLES

**Principle O1: Time-to-first-value must be under 5 minutes.**
A new user must reach a real compliance output (not a sample/placeholder) within 5 minutes of signup.

**Principle O2: The onboarding forks by role at the earliest moment.**
At signup, the `self_identified_role` field determines which onboarding path the user follows. A "Developer" gets the API key and quickstart immediately. A "Business Owner" gets guided through creating a project.

**Principle O3: Show real value early, ask questions progressively.**
Don't require 100% questionnaire completion before showing ANY output. Show partial results at 40% completion with clear prompts to complete the profile.

**Principle O4: Never hide the usage counter.**
The usage counter (X/100 today) is visible from first login in the top navigation bar. No surprises when the limit is hit.

**Principle O5: Every onboarding step is a DB record.**
The `onboarding_progress` table tracks each step. This enables: email nudges (Phase 2), product analytics, and restoring the UI state when user returns.

---

## 2. USER TYPES AND THEIR ONBOARDING FORKS

| Self-Identified Role at Signup | Primary Onboarding Path |
|-------------------------------|------------------------|
| BUSINESS_OWNER | Business path — guided to create project and run evaluation |
| CA_CONSULTANT | Business path (same as owner for MVP; CA-specific UI in Phase 2) |
| DEVELOPER | Developer path — API key visible first; quickstart code shown |
| OTHER | Business path (default) |

---

## 3. JOURNEY 1 — ANONYMOUS VISITOR TO SIGNUP

```
Landing Page
  → reads value proposition
  → optionally clicks "Try Demo"
    → fills 6-field demo form
    → sees truncated compliance output for sample business
    → sees "Sign up to get full results for your business"
  → clicks "Get Started Free"
  → Signup Page
    → email + password + full name + role selection
    → hCaptcha
    → clicks "Create Account"
  → Email sent: "Verify your email"
  → [Optional: allow unverified access for 24 hours before gating certain features]
```

**Friction point:** Email verification. Decision required: gate evaluation behind email verify or allow first evaluation before verify?
**Recommendation:** Allow one evaluation before email verification is required. This ensures the user sees value before hitting an auth wall.

---

## 4. JOURNEY 2A — NEW BUSINESS USER POST-SIGNUP

**Step 1: Welcome Screen + Path Selection**
```
"Welcome to ECNAILPCOM, Rajan!"
[ ] I want to check compliance for my business → [Get Started]
[ ] I want to use the API → [See API Quickstart]
```

**Step 2: Auto-create workspace**
(Happens in background. User never sees a "create workspace" form in Day 1.)
Workspace name: "{full_name}'s Workspace" — editable later in settings.

**Step 3: Create First Project (simplified)**
```
"Let's set up your first business profile"

Business Name: [Acme Technologies Pvt Ltd        ]
Entity Type:   [Private Limited Company      ▼   ]
Primary State: [Maharashtra                  ▼   ]

[Continue →]
```

Only 3 fields for the first screen. The rest of the questionnaire is shown step by step.

**Step 4: Core Questionnaire — Minimum Required**
```
Page 2: Tax & Registration
  - Are you registered for GST? [Yes/No]
  - If yes: GST Scheme [Regular / Composition]
  - Annual Turnover [Band selector]

Page 3: Employment
  - Number of employees [0 / 1-9 / 10-19 / 20-49 / 50+]
  - Do you pay salaries? [Yes/No]

Page 4: Activity
  - Primary activity [Service/Trading/Manufacturing/Mixed]
  - Do you have a food business? [Yes/No]
  - Do you import or export? [Yes/No]
```

At this point (~40% completion), the system can run a meaningful evaluation.

**Step 5: "Your profile is ready for a first assessment"**
```
Profile: 42% complete (you can add more details later)

[Generate My Compliance Profile →]

This will use 1 of your 100 daily evaluations.
```

**Step 6: First Evaluation Result**
```
Compliance Profile: Acme Technologies Pvt Ltd
FY2025-26 | Private Limited Company | Maharashtra

43 compliance items identified
  ⚠ 3 overdue items
  🔴 2 items due this week
  ✅ 2 items just completed

[View Full Compliance List] [View Calendar] [View Risk Map]
```

**Step 7: Onboarding Checklist Sidebar**
```
Getting Started — 3/8 steps complete
[✓] Create account
[✓] Create business profile
[✓] Generate first assessment
[ ] Review upcoming due dates →
[ ] View risk heat map →
[ ] Copy your API key →
[ ] Make your first API call →
[ ] Export your first report →
```

---

## 5. JOURNEY 2B — NEW DEVELOPER USER POST-SIGNUP

**Step 1: Same welcome screen but Developer path selected**

**Step 2: API Quickstart Screen**
```
"Your workspace is ready. Here's how to start."

Your API Key (shown once — copy it now):
┌─────────────────────────────────────────────────────────────┐
│  pk_live_a3f8c2d1e4b7a9f0c1d2e3f4a5b6c7d8   [Copy] [👁]  │
└─────────────────────────────────────────────────────────────┘

⚠ This key is shown once. Store it securely.

Quick Start — Create your first compliance profile:

  curl -X POST https://api.ecnailpcom.in/v1/projects \
    -H "X-API-Key: pk_live_..." \
    -H "Content-Type: application/json" \
    -d '{"project_name": "My Business", "entity_type": "PRIVATE_LIMITED"}'

[Read Full API Docs] [Try in Playground] [Continue to Dashboard →]
```

**Step 3: Dashboard with API-focused shortcuts**
- Usage counter prominently displayed
- Link to API Reference
- "Make your first evaluation" card with sample code

---

## 6. JOURNEY 3 — RETURNING USER (BUSINESS)

```
Login → Dashboard
  Shows:
  - Projects list with status badges
  - Global upcoming dues across all projects (if multiple)
  - Usage counter (today: X/100)
  
User selects a project:
  - Sees "2 items overdue" banner
  - Clicks into compliance list
  - Filters by OVERDUE
  - Marks one item as COMPLETED
  - Navigates to calendar
  - Checks next week's due dates
  - Exports PDF-style report
  - Shares report link with CA via email
```

---

## 7. JOURNEY 4 — RETURNING DEVELOPER (API-FIRST)

```
Login → Dashboard
  → API Keys section
  → Sees key usage (X calls today, Y calls this month)
  → Goes to docs
  → Makes API call from external system
  [API system does]:
    PATCH /v1/projects/:id/questionnaire/answers   (update turnover)
    POST  /v1/projects/:id/evaluation              (trigger re-eval, costs 1 quota)
    GET   /v1/projects/:id/compliance?status=OVERDUE&domain=GST  (read overdue GST items)
```

---

## 8. ONBOARDING CHECKLIST — DB-BACKED STEPS

| Step ID | Label | Trigger |
|---------|-------|---------|
| account_created | Create account | Auto-complete on signup |
| first_project | Create your first business profile | Project created |
| questionnaire_core | Complete core business details | Completeness ≥ 70% |
| first_evaluation | Generate first compliance assessment | First evaluation completes |
| viewed_due_dates | Review upcoming due dates | User navigates to /due-dates page |
| viewed_heat_map | View risk heat map | User navigates to /heat-map page |
| api_key_copied | Copy your API key | User clicks Copy on API key page |
| first_api_call | Make your first API call | api_keys.last_used_at populated |
| first_export | Export your first report | First export completed |

Steps `account_created`, `first_project`, `first_evaluation` are required. Others are optional enrichment.

**When to dismiss:** User can dismiss the checklist at any time. It remains available in a collapsed form in sidebar. Re-open anytime via "Getting Started" link.

---

## 9. SAMPLE PROJECT PRELOADING

**Decision:** Should a sample pre-filled project be shown to new users?

**Recommendation:** Yes, but as an OPTIONAL template, not the default. Show on the dashboard a card: "Want to see a sample output first? Load a demo project →". This opens a READ-ONLY project with a pre-filled Private Limited Company in Maharashtra with sample data. The user can then create their own project.

**Why not auto-load:** Users often find pre-filled data confusing ("is this my data or sample data?"). It's cleaner to let them create their own from scratch with an optional sample view.

---

## 10. FRICTION POINTS AND MITIGATIONS

| Friction Point | Risk | Mitigation |
|---------------|------|-----------|
| Email verification required before value | User drops off | Allow one evaluation before requiring verify |
| Long questionnaire before results | User gives up | Show results at 40% completion |
| "What counts as a request?" confusion | User miscounts and hits limit | Show counter always; FAQ tooltip on counter |
| API key shown once, user forgets to copy | User frustrated, must regenerate | Show warning prominently; allow download of key as .txt (one time) |
| Overdue items on first load are alarming | User panics | Contextual explanation: "These are estimated based on your profile. Mark as done if filed." |
| "Who is this for?" unclear | Wrong user lands | Role selection at signup + different onboarding paths |
