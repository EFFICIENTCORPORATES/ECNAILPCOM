# CLAUDE.md — Project Orientation for AI Agents
## ECNAILPCOM — Indian Business Compliance Intelligence SaaS

Read this file first, before touching any code or document in this repository.

---

## 1. What This Project Is

**ECNAILPCOM** is a pre-build-phase SaaS product that helps Indian businesses understand which compliance obligations apply to them, when deadlines fall, and what the penalties for missing them are.

It is NOT a reminder app. Every compliance item in the system must be traceable to a primary legal/regulatory source (statute, rule, notification, circular). The system computes actual calendar due dates from encoded rules, not from guessed labels.

**Three user modes at launch:**
1. **Self-serve business owner** — fills a questionnaire, gets a classified compliance profile with due dates and severity scores
2. **Developer / API consumer** — submits business profile via REST API, gets structured JSON compliance output
3. **CA / Consultant** — manages multiple client businesses in one workspace (data model ready; dedicated UI deferred to Phase 2)

---

## 2. Two Workstreams in This Repo

### Workstream A — The SaaS Product (main product, not yet implemented)
Architecture fully designed across 24 documents in `docs/`. No application code exists yet. See Section 5 below for what to read.

### Workstream B — Training Data Scraper (implemented, in `scraper/`)
A Playwright-based scraper that downloads Supreme Court of India judgments from `verdictfinder.sci.gov.in` as PDFs. These will form a legal AI training dataset. The scraper mimics human behaviour (Gaussian delays, curved mouse movement, persistent browser profile). See Section 7 below.

---

## 3. Repository Structure

```
ECNAILPCOM/
├── CLAUDE.md                   ← you are here
├── README_PLANNING.md          ← index of all docs; read this second
│
├── docs/                       ← all 24 architecture/spec documents
│   ├── 01–10  (Part A)         ← compliance engine foundation — FROZEN
│   ├── 11–22  (Part B)         ← SaaS product and API architecture
│   ├── 23–24  (Part A Suppl.)  ← legal research and compliance gaps
│   └── C1–C7  (Part C)         ← canonical schema and encoding standards
│
├── schema/                     ← JSON Schemas for compliance data structures
│   ├── compliance_master.schema.json
│   ├── due_date_rule.schema.json
│   ├── applicability_rule.schema.json
│   ├── api_error.schema.json
│   └── api_compliance_output.schema.json
│
├── scraper/                    ← Supreme Court judgment scraper (Python + Playwright)
│   ├── main.py                 ← entry point
│   ├── human.py                ← human behaviour simulation
│   ├── config.py               ← URLs, timing, fingerprint pool, paths
│   └── requirements.txt
│
└── trainingdata/
    ├── source_sites            ← target URLs for scraper
    └── scraped/                ← created on first scraper run
        ├── pdfs/               ← downloaded case PDFs
        └── logs/               ← scrape logs + JSON metadata per case
```

---

## 4. Product Architecture — 8 Layers

The compliance engine is divided into eight logical layers. Each layer has a dedicated document.

| Layer | Name | What it does | Key Doc |
|-------|------|-------------|---------|
| 1 | User Input | Adaptive business questionnaire | doc 07 |
| 2 | Entity Classification | Translates raw inputs into compliance-relevant flags | doc 01, 08 |
| 3 | Applicability Engine | Evaluates each compliance rule against the business profile | doc 08 |
| 4 | Compliance Library | Master knowledge base — sourced, versioned, structured | doc 04 |
| 5 | Due Date Computation | Computes actual calendar dates from encoded rule formulas | doc 05 |
| 6 | Penalty / Severity | Assigns 0–100 severity score; feeds the heat map | doc 06 |
| 7 | Source Tracking | Full legal citation, supersession history, conflict tracking | doc 03 |
| 8 | UI / API Consumption | Checklist, calendar, dashboard, heat map, REST API | doc 13, 16 |

---

## 5. What to Read Before Working on the Product

**Mandatory reading order (do not skip steps):**

1. `README_PLANNING.md` — master index, confirmed decisions, open decisions
2. `docs/01` — product vision, 8 system layers, design philosophy
3. `docs/02` — all 15 compliance domains with laws, rules, due dates, penalties
4. `docs/04` — complete database schema
5. `docs/05` — due date rule types and FY logic
6. `docs/08` — applicability rule expressions and confidence taxonomy
7. `docs/09` — MVP scope (~85–110 library records) vs Phase 2/3
8. `docs/11` — SaaS product architecture, Part B extensions, disclaimer design
9. `docs/22` — **open decisions** that MUST be answered before implementation begins
10. `schema/` — JSON Schema files for all data structures

**Part C (docs C1–C7)** contains canonical encoding standards — read before populating compliance library records.

---

## 6. Current Project Status

| Area | Status |
|------|--------|
| Part A compliance architecture (docs 01–10) | COMPLETE, FROZEN |
| Part B SaaS product architecture (docs 11–22) | COMPLETE |
| Legal research B1–B10 (doc 23) | 5 resolved, 3 partial, 2 with known divergence |
| Additional compliance gaps (doc 24) | Identified; 43B(h), 206AB, 194Q, small company fix |
| JSON Schemas | COMPLETE |
| Open decisions (doc 22) | NOT YET ANSWERED — blocks implementation |
| Compliance library population | NOT STARTED |
| Tech stack selection | NOT DECIDED |
| Application code | NOT WRITTEN |
| Training data scraper | IMPLEMENTED (scraper/) |

**Most blocking open decisions (from doc 22):**
- Q11: Product name — required before any content is written
- Q12: Tech stack — required before implementation begins
- I1: Confirm `compliance_period_instance` replaces `business_compliance_output`
- I2: How many FY periods to pre-generate per evaluation run

---

## 7. Key Design Principles — Never Violate These

1. **Source-first.** Every compliance record starts from a primary legal source. No guessing.
2. **Computable due dates.** Every recurring compliance has an encoded rule formula. "Monthly" is not sufficient.
3. **Applicability has confidence.** Nothing is binary — use the taxonomy: APPLICABLE / LIKELY_APPLICABLE / CHECK_THRESHOLD / STATE_SPECIFIC / EVENT_TRIGGERED / NOT_APPLICABLE.
4. **Penalties are structured.** Store as fields, not prose. The severity engine reads them.
5. **Library is separate from business instances.** `compliance_master` is static knowledge. `compliance_period_instance` is derived output per business per period.
6. **Notification overrides are first-class.** Indian compliance has frequent government-notification extensions. Store as versioned overrides, never edit the base rule.
7. **Disclaimer on every output.** Text is in `system_config`, not hardcoded. See doc 11 section 7.

---

## 8. Training Data Scraper (Workstream B)

**Purpose:** Download all Supreme Court of India judgments from `verdictfinder.sci.gov.in` as PDFs for legal AI training data. The site shows ~30 lakh (3 million) results.

**Stack:** Python 3.10+ · Playwright · Chromium (headless off)

**Key behaviour:**
- Opens a persistent browser profile (`scraper/browser_profile/`) — cookies, cache, and history accumulate across runs making it look like a returning human visitor
- Fingerprint (user-agent + viewport) is chosen once on first run and locked in `browser_profile/fingerprint.json`
- Pauses for the user to manually solve the CAPTCHA on the homepage
- Uses Gaussian-distributed random delays, curved mouse movement with wobble, per-keystroke typing delays, and random scroll to mimic human reading
- Optional Tor routing via `--tor` flag (requires Tor Browser running on SOCKS5 :9050)

**Setup (run once):**
```bash
cd scraper
pip install -r requirements.txt
playwright install chromium
```

**Run:**
```bash
python main.py              # scrape 1 test case
python main.py --count 5    # scrape first 5 cases
python main.py --tor        # route through Tor
```

**Output:**
- PDFs → `trainingdata/scraped/pdfs/`
- JSON metadata per case → `trainingdata/scraped/logs/`
- Scrape log → `trainingdata/scraped/logs/scrape_YYYYMMDD_HHMMSS.log`
- Debug HTML (on selector failure) → `trainingdata/scraped/logs/`

**If PDF buttons are not found:** The scraper saves a `debug_page.html` — inspect it to determine the correct CSS selectors and update `find_pdf_buttons()` in `scraper/main.py`.

---

## 9. Confirmed Product Decisions

| Decision | Answer |
|----------|--------|
| Legal liability posture | Informational only + disclaimer + source provenance. No accuracy SLA. |
| Day 1 primary user | Self-serve business owner. Backend professional-grade. |
| Compliance tracker | YES — `tracking_status`, `completed_on`, `completed_by`, `completion_notes` per period instance |
| Library maintenance | Git-tracked files → DB import. No direct DB edits ever. |
| CA portfolio UI | NOT Day 1. Data model ready. Up to 3 projects on free plan. |
| Database | PostgreSQL (confirmed in doc 04) |
| `business_compliance_output` | REPLACED by `compliance_period_instance` (doc 11, Extension B1) |

---

## 10. Indian Financial Year Reference

| Concept | Definition |
|---------|-----------|
| Financial Year (FY) | April 1 – March 31 |
| FY label format | FY2025-26 |
| Assessment Year (AY) | FY + 1 (for income tax) |
| AY label format | AY2026-27 (corresponds to FY2025-26 income) |
| Q1 | April 1 – June 30 |
| Q2 | July 1 – September 30 |
| Q3 | October 1 – December 31 |
| Q4 | January 1 – March 31 |
| MCA AGM deadline | September 30 (for March FY companies) |

All due date computation must be grounded in this calendar. The engine derives current FY, quarter, AY, and days remaining from the system date at evaluation time.

---

*This file is the entry point for any agent or developer working in this repository.*
*For detailed architecture, follow the reading order in Section 5.*
