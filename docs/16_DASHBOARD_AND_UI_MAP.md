# Document 16 — Dashboard and UI Map
## All Product Pages, Screens, and Their Specifications

**AUDIENCE:** Frontend implementors and UX designers.
**IMPORTANT:** This document describes what each screen does and what it must contain. Visual design decisions (colors, component library, layout details) are separate concerns. Implement information architecture first.

---

## SECTION 1: PUBLIC PAGES (No Login Required)

---

### P1 — Homepage `/`

**Purpose:** Introduce the product, establish trust, drive signup.

**Essential sections:**
1. **Hero:** One-line value proposition + "See a demo" CTA + "Sign up free" CTA
   - Value prop: "Know every compliance due date for your Indian business — backed by primary legal sources."
2. **How it works:** 3-step visual (Answer questions → Get assessment → Track deadlines)
3. **What's covered:** Compliance domain tiles — GST, Income Tax, TDS, MCA/LLP, EPF/ESI, Labour Laws, Shops/Establishments
4. **Trust signal:** "Every item linked to its primary legal source — Acts, Rules, and CBIC/MCA notifications"
5. **For whom:** Three tiles — Business Owner, CA/Consultant, Developer/API
6. **Pricing summary:** Free vs paid comparison (2–3 plan columns)
7. **Developer section:** Code snippet showing a sample API call + response
8. **Footer:** Links to Docs, Pricing, Privacy, Terms, API Reference

**Launch-critical:** Everything above.
**Deferred:** Testimonials, case studies, blog section.

---

### P2 — Pricing Page `/pricing`

**Purpose:** Explain plans and drive upgrade decisions.

**Content:**
- Plan comparison table (Free / Starter / Pro — exact names TBD)
- Feature matrix per plan
- FAQ section: "What counts as a request?", "Can I use the API on the free plan?", "What happens when I hit the limit?"
- CTA: "Start Free" on Free plan; "Contact Us" on Enterprise

**Free Plan display must include:**
- 100 evaluations/day
- UI + API access included
- Up to 3 business profiles
- JSON + CSV export
- Share links (up to 10)
- Source-backed compliance library

**Launch-critical:** Must be live before launch. Placeholder pricing acceptable if billing not yet integrated.

---

### P3 — Demo Page `/demo`

**Purpose:** Show real value without requiring signup.

**Content:**
1. Tagline: "See your compliance profile in 30 seconds"
2. Mini-questionnaire form (6 fields only):
   - Entity type
   - Principal state
   - GST registered? + scheme
   - Annual turnover band
   - Employee count band
3. "Generate Sample Assessment" button (triggers POST /v1/public/demo/evaluate)
4. Result display: Shows 8–10 applicable compliance items with actual due dates and severity colors
5. Disclaimer: "Showing a partial result for illustration. Sign up for your full profile."
6. CTA: "Get your complete compliance profile →" → /signup

**Abuse protection:** IP rate limit 5/day. hCaptcha if triggered.
**Launch-critical:** Must work at launch.

---

### P4 — Signup Page `/signup`

**Essential fields:**
- Full name
- Email
- Password (with show/hide toggle)
- Role selection: "I'm a..." (Business Owner / CA or Consultant / Developer / Other)
- hCaptcha widget
- "Create Free Account" button
- Link to login
- Link to Terms and Privacy

---

### P5 — Login Page `/login`

- Email + password
- "Forgot password?" link
- Rate limit: 10 failed attempts → 15 min lockout + captcha
- Link to signup

---

### P6 — Documentation Hub `/docs`

See [doc 19](19_DEVELOPER_EXPERIENCE_AND_DOCS.md) for full spec.

**Must be public, no login required.**
Sidebar navigation with sections: Overview, Authentication, Rate Limits, API Reference, Examples, Error Codes.

---

### P7 — Legal Pages (Placeholder)

`/privacy` — Privacy Policy (required before launch)
`/terms` — Terms of Service (required before launch)
`/cookies` — Cookie Policy

These must exist as pages but detailed legal text can be drafted by a professional after tech architecture is defined.

---

## SECTION 2: LOGGED-IN PRODUCT PAGES

---

### A1 — Dashboard Home `/dashboard`

**Purpose:** First screen after login. Shows the user's compliance landscape at a glance.

**Essential widgets:**

1. **Workspace Summary Bar** (top)
   - Workspace name | Current plan | Usage counter: X/100 today | Upgrade link

2. **Project Quick-Switch** (if multiple projects)
   - Dropdown or tab row: [Acme Tech ▼] | [+ New Project]

3. **For selected project — Summary Cards (4 cards):**
   - `Overdue` — count in red, click → compliance list filtered by OVERDUE
   - `Due This Week` — count in amber, click → calendar filtered to next 7 days
   - `Due This Month` — count in blue
   - `Completed This Month` — count in green

4. **Critical Actions Banner** (if overdue items exist)
   - "⚠ 3 items are overdue. Earliest: GSTR-3B May 2026 (3 days late). [View All Overdue →]"

5. **Upcoming Due Dates Widget** — next 7 items with domain, title, date, severity chip

6. **Risk Heat Map Mini Widget** — compressed 2×3 grid showing severity by domain (clickable → full heat map)

7. **Onboarding Checklist** (collapsed sidebar panel, until dismissed)

8. **Profile Completeness** — "Your profile is 65% complete. Adding employee count and bank details may reveal more compliances. [Complete Profile →]"

**What the landing page after login should show:**
- If user has no projects: show "Create your first project" centered CTA
- If user has projects: show dashboard for most recently edited project
- If user just completed signup: show onboarding welcome screen (first time only)

---

### A2 — Projects List `/projects`

**Purpose:** Manage all business profiles in the workspace.

**Content:**
- Grid or list of project cards
- Each card: project_name, entity_type, overdue count badge, last evaluated date, quick action buttons (View / Edit / Archive)
- Search/filter bar
- "New Project" button (top right)
- Sort: Last evaluated / Alphabetical / Most overdue

---

### A3 — Create Project Wizard `/projects/new`

**Purpose:** Guide user through minimal profile creation.

**Steps (wizard):**
1. Basic identity (name, entity type, state) — 3 fields
2. Tax profile (GST status, scheme, turnover band) — 3 fields
3. Employment (employee count band, salary payments) — 2 fields
4. Activity (type, food, export) — 3 fields
5. Review + Generate

Each step shows: "This information helps us identify which laws apply to your business."

After step 5: Auto-trigger evaluation (costs 1 quota unit). Show usage confirmation: "This will use 1 evaluation (X remaining today)."

---

### A4 — Project Questionnaire Editor `/projects/:id/questionnaire`

**Purpose:** Full questionnaire editing after initial setup.

**Layout:**
- Left sidebar: domain navigation (A, B, C, D, E, F, G, H sections from doc 07)
- Main panel: questions for selected domain
- Right panel: completeness indicator + summary of derived flags

**Behavior:**
- Auto-save on field change (PATCH /questionnaire/answers debounced 2 seconds)
- Show "Profile changed — re-evaluate to see updated compliance list" banner when answers change
- Validation inline (e.g., GST scheme options only shown when GST registered = Yes)

**Re-evaluation CTA:**
When answers have changed since last evaluation:
- Yellow banner: "⚠ Profile updated. Your compliance results may have changed."
- Button: [Re-evaluate Now] (costs 1 quota)

---

### A5 — Project Results Overview `/projects/:id`

**Purpose:** Quick snapshot of a project's compliance state.

**Content:**
1. Project header: Legal name, entity type, state, last evaluated timestamp + library version
2. Financial year label: "Assessment: FY2025-26 | As of: June 3, 2026"
3. Summary cards (same as dashboard but project-specific)
4. Quick actions: [Edit Profile] [View Full List] [View Calendar] [View Heat Map] [Export] [Share]
5. Top 5 critical items (by combined severity)
6. Missing information warnings (if profile is incomplete in important ways)

---

### A6 — Compliance List View `/projects/:id/compliance`

**Purpose:** The full, searchable, filterable list of compliance items.

**Filters (sidebar or top bar):**
- Status: Overdue / Due Soon / Upcoming / Completed / All
- Domain: GST / Income Tax / TDS / MCA / EPF / ESI / Shops & Establishments / All
- Frequency: Monthly / Quarterly / Annual / Event-Based
- Severity: Critical / Severe / High / Moderate / Low
- Applicability: Applicable / Likely Applicable / Check Threshold / Event Triggered
- Search: free text

**Sort options:** Due Date (ASC default), Severity (DESC), Domain

**List item display:**
```
[🔴] GSTR-3B Monthly Return Filing
     Domain: GST · Period: May 2026 · Due: Jun 20, 2026
     Status: OVERDUE (3 days) · Severity: HIGH
     [Mark Done] [View Details] [View Source]
     Tracking: PENDING
```

**Bulk actions:** Mark selected as done.

**MVP filter minimum:** Status + Domain + Severity. Others can be Phase 2.

---

### A7 — Due Date Calendar/Timeline `/projects/:id/calendar`

**Purpose:** Time-based view of upcoming and overdue compliance obligations.

**View options:**
1. **List/Timeline View (MVP — required):** Month-grouped list showing all due dates
2. **Calendar Grid View (Phase 2):** Traditional calendar grid

**Timeline view structure:**
```
─── JUNE 2026 ───────────────────────────────
⚠ OVERDUE (from previous periods)
  🔴 GSTR-3B May 2026 — Due Jun 20 — 3 days late
  🔴 EPF May 2026 — Due Jun 15 — 18 days late

DUE THIS WEEK
  🟠 GSTR-1 May 2026 — Due Jun 11 — in 8 days

UPCOMING THIS MONTH
  🔵 TDS Deposit May 2026 — Due Jun 7 — in 4 days
  🔵 EPF Jun 2026 — Due Jul 15 (next month)

─── JULY 2026 ───────────────────────────────
  GSTR-3B Jun 2026 — Due Jul 20
  ...
```

**Per item:** Domain chip, title, period, due date, days remaining/overdue, severity color, [Mark Done] button.

**Filter bar:** Domain filter. Severity filter. Status filter (Show/hide completed).

**Financial year toggle:** View FY2025-26 / FY2026-27 (show only if compliance extends to next FY).

---

### A8 — Heat Map / Risk View `/projects/:id/heat-map`

**Purpose:** Visual severity matrix to identify highest-risk obligations immediately.

**Layout — Grid Heat Map:**

Columns: Compliance Domains (GST, IT/TDS, MCA/LLP, EPF/ESI, Labour, Establishments)
Rows: Urgency tiers (Critical Overdue, Severely Overdue, High Overdue, Due This Week, Due This Month, Upcoming)

Each cell: Color-coded count badge. Empty cells are grey.

Click a cell → slide-in panel showing the specific compliance items in that cell.

**Below grid: Top 10 Most Critical Items** (severity sorted, with penalty summary)

**Color guide legend:** Always shown so users understand what the colors mean.

---

### A9 — Compliance Detail + Source View `/projects/:id/compliance/:instanceId`

**Purpose:** Full detail for a single compliance item. The most important trust-building screen.

**Content:**
1. **Title and Classification:**
   - Full title, domain, frequency, period
   - Applicability status with confidence
   - "Why this applies": bullet list from `why_it_applies` field

2. **Due Date Details:**
   - Period: May 2026
   - Due date: June 20, 2026
   - Status: Overdue by 3 days / Due in X days
   - Base rule: "20th of month following period end (GSTR-3B staggered — Maharashtra in Group A)"
   - Override active: Yes/No + if yes, notification reference

3. **Severity and Consequences:**
   - Severity band: HIGH (score: 65/100)
   - Late fee: ₹50/day (max ₹10,000) — CGST Act Sec 47(1)
   - Interest: 18% p.a. on outstanding liability — CGST Act Sec 50
   - "What happens if missed" — plain language summary

4. **Source Attribution (the trust section):**
   - Primary obligation: Section 39, CGST Act, 2017
   - Rule: Rule 61(1), CGST Rules, 2017
   - Notification: [if any active override] "Extended to Jun 25 per Notification XX/2026-CT"
   - Official link: [gst.gov.in →] (clickable, opens in new tab)
   - Last verified: May 15, 2026 | Confidence: HIGH

5. **Tracking:**
   - Status: PENDING / COMPLETED / SKIPPED
   - [Mark as Completed] button → modal asking for completion date and optional notes

6. **Dependencies:**
   - "Note: This return should align with GSTR-1 filed for the same period."

---

### A10 — Exports Page `/projects/:id/exports`

**Content:**
- Export button bar: [Export JSON] [Export CSV] [Export Report (Print)]
- Export history table: timestamp, type, library version, download link (expires 24h)
- "Exports use 1 evaluation unit each. X remaining today."

---

### A11 — Share Links Page `/projects/:id/share`

**Content:**
- Active share links list: label, token preview, created date, expiry, access count, [Revoke] button
- "Create Share Link" form:
  - Label (optional)
  - Include business legal name? [Toggle — default OFF]
  - Include PAN/GSTIN? [Toggle — default OFF and disabled by warning]
  - Expiry: 7 days / 30 days / 90 days / Never
- After creation: Share URL shown with copy button + warning "Store this URL — the token is not recoverable"

---

### A12 — API Keys Page `/settings/api-keys`

**Content:**
- Key list: label, key_preview, created date, last used date, usage count, status badge, [Revoke] [Rotate] buttons
- "Create New Key" form: label field + [Create Key] button
- After creation: One-time full key display with copy button + "⚠ Store this key now — it won't be shown again"
- Plan limit indicator: "2 of 3 keys used (Free plan)"

---

### A13 — Usage Page `/settings/usage`

**Content:**
- Today's quota: progress bar (X of 100 used)
- Reset time: "Resets at midnight UTC"
- Breakdown: Evaluations (X), Exports (Y)
- This month: daily usage chart (last 30 days)
- Plan info + Upgrade CTA if on Free plan

---

### A14 — Settings `/settings`

**Tabs:**
- Profile: name, email, timezone, password change
- Workspace: workspace name, plan info
- API Keys: same as A12
- Usage: same as A13
- Danger Zone: Archive workspace / Delete account (with confirmation flow)

---

## SECTION 3: DOCS PAGES (Public)

See [doc 19](19_DEVELOPER_EXPERIENCE_AND_DOCS.md) for full spec.

Key pages: `/docs/overview`, `/docs/authentication`, `/docs/rate-limits`, `/docs/reference`, `/docs/examples`, `/docs/errors`, `/docs/versioning`

---

## SECTION 4: LAUNCH-CRITICAL vs. DEFERRED

| Screen | Launch-Critical |
|--------|----------------|
| Homepage, Pricing, Demo, Signup, Login | ✓ |
| Privacy, Terms (placeholder text OK) | ✓ |
| Dashboard, Projects list, Create project wizard | ✓ |
| Questionnaire editor | ✓ |
| Compliance list with filters (Domain + Status + Severity) | ✓ |
| Timeline/due date view (list view only) | ✓ |
| Heat map (grid view) | ✓ |
| Compliance detail + source view | ✓ |
| Exports (JSON + CSV + Print) | ✓ |
| Share links | ✓ |
| API keys page | ✓ |
| Usage page | ✓ |
| Settings (profile + workspace) | ✓ |
| Docs (auth + rate limits + endpoint ref + examples) | ✓ |
| Calendar grid view | Phase 2 |
| Collaboration/member invite UI | Phase 2 |
| Bulk compliance operations | Phase 2 |
| Revision history/diff views | Phase 2 |
| Admin/ops internal dashboard | Phase 2 |
