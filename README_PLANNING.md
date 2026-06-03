# ECNAILPCOM — Indian Business Compliance SaaS
## Pre-Build Planning Documentation Index

This directory contains the complete pre-build architecture, domain analysis, data model,
and clarification framework produced before any implementation begins.

**All documents in `docs/` must be read before any code is written.**
Read Part A (01–10) first. Then Part B (11–22). Then answer doc 22 clarification questions.

---

## PART A — Compliance Intelligence Foundation (FROZEN BASELINE)

> Part A is accepted and frozen. Do not re-argue core structure unless Part B creates a direct conflict.

| File | Purpose |
|------|---------|
| [docs/01_PRODUCT_VISION_AND_ARCHITECTURE.md](docs/01_PRODUCT_VISION_AND_ARCHITECTURE.md) | Product restatement, 8 system layers, design philosophy |
| [docs/02_COMPLIANCE_DOMAINS.md](docs/02_COMPLIANCE_DOMAINS.md) | All 15 compliance domains: laws, rules, due dates, penalties |
| [docs/03_SOURCE_STRATEGY.md](docs/03_SOURCE_STRATEGY.md) | Source hierarchy, conflict resolution, metadata model |
| [docs/04_DATA_MODEL.md](docs/04_DATA_MODEL.md) | Complete database schema for compliance library |
| [docs/05_DUE_DATE_ENGINE.md](docs/05_DUE_DATE_ENGINE.md) | 8 due date rule types, FY logic, notification overrides |
| [docs/06_HEATMAP_SEVERITY_MODEL.md](docs/06_HEATMAP_SEVERITY_MODEL.md) | Severity scoring model (0–100), bands, color codes |
| [docs/07_QUESTIONNAIRE_DESIGN.md](docs/07_QUESTIONNAIRE_DESIGN.md) | 8 questionnaire domains, field-to-compliance mapping |
| [docs/08_APPLICABILITY_MODEL.md](docs/08_APPLICABILITY_MODEL.md) | Applicability status taxonomy, rule expression JSON format |
| [docs/09_MVP_VS_LATER.md](docs/09_MVP_VS_LATER.md) | Compliance library MVP (~85–110 records) vs Phase 2 |
| [docs/10_CLARIFICATION_QUESTIONS.md](docs/10_CLARIFICATION_QUESTIONS.md) | Legal research items B1–B10 (unresolved, primary sources only) |

## PART A SUPPLEMENT — Legal Research and Compliance Gaps

| File | Purpose |
|------|---------|
| [docs/23_LEGAL_RESEARCH_B1_B10.md](docs/23_LEGAL_RESEARCH_B1_B10.md) | Primary-source resolution of B1–B10 items; what's ready to populate vs. still blocked |
| [docs/24_ADDITIONAL_COMPLIANCE_GAPS.md](docs/24_ADDITIONAL_COMPLIANCE_GAPS.md) | New compliance items surfaced during legal research (43B(h), 206AB, 194Q, small company fix) |

## PART B — SaaS Product and API Architecture

| File | Purpose |
|------|---------|
| [docs/11_SAAS_PRODUCT_ARCHITECTURE.md](docs/11_SAAS_PRODUCT_ARCHITECTURE.md) | SaaS product goal, module map, Part A/B compatibility, library versioning |
| [docs/12_TENANT_USER_WORKSPACE_MODEL.md](docs/12_TENANT_USER_WORKSPACE_MODEL.md) | Full DB schema for users, workspaces, projects, keys, audit log |
| [docs/13_API_PRODUCT_DESIGN.md](docs/13_API_PRODUCT_DESIGN.md) | Complete REST API: all endpoint families, request/response contracts |
| [docs/14_AUTHENTICATION_AND_SECURITY.md](docs/14_AUTHENTICATION_AND_SECURITY.md) | Auth design, API key lifecycle, tenant isolation, security headers |
| [docs/15_ONBOARDING_FLOWS.md](docs/15_ONBOARDING_FLOWS.md) | All user journeys, onboarding checklist, friction analysis |
| [docs/16_DASHBOARD_AND_UI_MAP.md](docs/16_DASHBOARD_AND_UI_MAP.md) | All product pages: public, logged-in, docs — what each must contain |
| [docs/17_USAGE_METERING_AND_PLANS.md](docs/17_USAGE_METERING_AND_PLANS.md) | What counts as quota, Redis counter design, over-limit behavior |
| [docs/18_EXPORT_SHARING_REPORTING.md](docs/18_EXPORT_SHARING_REPORTING.md) | JSON/CSV/Print exports, share link token design, snapshot architecture |
| [docs/19_DEVELOPER_EXPERIENCE_AND_DOCS.md](docs/19_DEVELOPER_EXPERIENCE_AND_DOCS.md) | Docs structure, quickstart guide, OpenAPI spec, playground design |
| [docs/20_OBSERVABILITY_AND_OPS.md](docs/20_OBSERVABILITY_AND_OPS.md) | Structured logging, metrics, activation funnel, library update ops |
| [docs/21_SAAS_MVP_VS_LATER.md](docs/21_SAAS_MVP_VS_LATER.md) | Complete MVP checklist, v1 hardening, Phase 2/3 plan |
| [docs/22_SAAS_CLARIFICATION_QUESTIONS.md](docs/22_SAAS_CLARIFICATION_QUESTIONS.md) | **⚠ OPEN DECISIONS** — Must answer before implementation begins |

## Schema Files

| File | Purpose |
|------|---------|
| [schema/compliance_master.schema.json](schema/compliance_master.schema.json) | JSON Schema for compliance master record |
| [schema/due_date_rule.schema.json](schema/due_date_rule.schema.json) | JSON Schema for due date rule encoding |
| [schema/applicability_rule.schema.json](schema/applicability_rule.schema.json) | JSON Schema for applicability rule expressions |
| [schema/api_error.schema.json](schema/api_error.schema.json) | Standardized API error response format |
| [schema/api_compliance_output.schema.json](schema/api_compliance_output.schema.json) | Compliance period instance shape as returned by API |

---

## Confirmed Decisions (from user)

| Decision | Answer |
|----------|--------|
| Legal liability posture | Informational only + disclaimer + source provenance. No accuracy SLA. |
| Day 1 target user | Self-serve business owner. Backend professional-grade. |
| Compliance tracker | YES. Status + completed_on + notes + completed_by. Evidence upload deferred. |
| Library maintenance | Git-tracked files → DB import. No direct DB edits. |
| CA portfolio UI | NOT Day 1. Data model ready. Individual multi-project allowed (up to 3 free). |

## Open Decisions (from doc 22)

See [docs/22_SAAS_CLARIFICATION_QUESTIONS.md](docs/22_SAAS_CLARIFICATION_QUESTIONS.md) for the full list.

**Most blocking items:**
- Q11: Product name (required for all content)
- Q12: Tech stack (required for implementation)
- I1: Confirm `compliance_period_instance` replaces Part A `business_compliance_output`
- Q2: Does UI evaluation count toward quota? (recommended: YES)
- Q6: Full source in API responses? (recommended: YES, inline)

---

## Project Status

- [x] Part A: Compliance foundation architecture — COMPLETE, FROZEN
- [x] Part B: SaaS product and API architecture — COMPLETE
- [x] B1–B10 legal research — ANALYZED in doc 23 (5 resolved, 3 partially resolved, 2 with known divergence)
- [x] Additional compliance gaps identified — doc 24 (43B(h), 206AB, 194Q, small company threshold fix)
- [ ] B1 state staggering: Notification 84/2020-CT text must be retrieved from cbic.gov.in
- [ ] B2 e-invoicing threshold: Current notification (post-Aug 2025) must be verified
- [ ] B5 ESI return: Current Rule 26 text + ESIC portal requirement must be checked
- [ ] GAP-3 small company fix: MGT-7/7A applicability rules must use ₹4Cr/₹40Cr thresholds
- [ ] Clarification questions in doc 22 answered
- [ ] Compliance library population started
- [ ] Tech stack selected
- [ ] Implementation started

---

*Part A produced by Claude (claude-sonnet-4-6) on 2026-06-03.*
*Part B produced by Claude (claude-sonnet-4-6) on 2026-06-03.*
*No code has been written. This is architecture and product specification only.*
*Implementation team: Read all docs before writing code. Ask questions via doc 22 process.*
