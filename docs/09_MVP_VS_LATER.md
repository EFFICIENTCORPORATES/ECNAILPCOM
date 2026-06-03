# Document 09 — MVP vs. Later Phases
## Compliance Domain Coverage: Phase-by-Phase Rollout Plan

---

## 1. MVP DEFINITION CRITERIA

A compliance domain belongs in MVP if:
1. It applies to a large majority of Indian businesses (not niche)
2. The consequences of missing it are significant (penalty, legal risk, business impact)
3. The due date rules can be reliably encoded without excessive state-specificity
4. Primary legal sources are available and well-established
5. It is asked about / confused about by typical SME business owners

A domain is deferred if:
1. It is highly sector-specific and applies to < 15% of the target business population
2. The legal framework is so state-specific that encoding it would require 28+ state-specific rules per item
3. The rules change so frequently that the maintenance burden is disproportionate at launch
4. The consequences of a slightly wrong answer are high (FEMA, foreign exchange: get wrong → legal liability)

---

## 2. MVP — PHASE 1 COMPLIANCE DOMAINS

These must be in the product at launch. The compliance library must be populated,
sources verified, due dates encoded, and penalties structured before launch.

### GST Domain (MVP — Complete)
- [ ] GST registration threshold check and applicability indicator
- [ ] Mandatory registration triggers (interstate, e-commerce, etc.)
- [ ] GSTR-1 monthly (11th rule)
- [ ] GSTR-1 quarterly QRMP (13th rule)
- [ ] GSTR-3B monthly with state-staggered due dates
- [ ] GSTR-3B quarterly QRMP
- [ ] CMP-08 quarterly (Composition)
- [ ] GSTR-4 annual (Composition)
- [ ] GSTR-9 annual (Regular, all taxpayers)
- [ ] GSTR-9C annual reconciliation (turnover > ₹5 Cr)
- [ ] E-invoicing applicability indicator
- [ ] E-way bill applicability indicator
- [ ] Late fee / interest penalty structure (Sec 47 + Sec 50)

### Income Tax Domain (MVP — Complete)
- [ ] ITR filing due dates by entity type
- [ ] Tax audit applicability indicator (Sec 44AB)
- [ ] Tax audit report due date (Form 3CA/CB + 3CD)
- [ ] Advance tax 4 installments with due dates
- [ ] Books of account maintenance indicator (Sec 44AA)
- [ ] Presumptive taxation applicability indicator (Sec 44AD / 44ADA) — indicator only
- [ ] Penalty for late ITR filing (Sec 234F)
- [ ] Interest for advance tax shortfall (Sec 234B/234C) — indicator only

### TDS Domain (MVP — Core Sections)
- [ ] TAN requirement indicator
- [ ] TDS on salary (Sec 192) — deposit and return cycles
- [ ] TDS on contractor (Sec 194C) — deposit and return cycles
- [ ] TDS on professional fees (Sec 194J) — deposit and return cycles
- [ ] TDS on rent (Sec 194I) — deposit and return cycles
- [ ] TDS monthly deposit due date rule (7th / 30th April for March)
- [ ] TDS quarterly return due dates (Q1–Q4)
- [ ] Form 16 / 16A certificate due dates
- [ ] Penalty for TDS default (Sec 234E, 276B, 40(a)(ia) disallowance) — structured

### MCA / Companies Act Domain (MVP — Core Annual)
- [ ] Company AGM indicator and deadline (Sep 30)
- [ ] AOC-4 filing (30 days from AGM)
- [ ] MGT-7 / MGT-7A filing (60 days from AGM)
- [ ] ADT-1 auditor appointment (15 days from AGM)
- [ ] DIR-3 KYC (September 30 annual)
- [ ] DPT-3 (June 30 annual) — for companies accepting deposits/loans
- [ ] MSME Form I (half-yearly: Oct 31 / Apr 30) — for companies with MSME suppliers
- [ ] Board meeting frequency indicator (min 4/year, max 120-day gap)
- [ ] Event-based filings as EVENT_TRIGGERED with offset rule:
  - DIR-12 (director change)
  - PAS-3 (share allotment)
  - CHG-1 (charge creation)
  - INC-22 (registered office change — same city)

### LLP Domain (MVP — Complete)
- [ ] Form 8 (October 30)
- [ ] Form 11 (May 30)
- [ ] LLP audit threshold indicator (₹40L turnover / ₹25L contribution)
- [ ] Event-based partner change (Form 4) — EVENT_TRIGGERED
- [ ] Event-based registered office change (Form 15) — EVENT_TRIGGERED

### EPF Domain (MVP — Complete)
- [ ] EPF registration threshold indicator (20 employees)
- [ ] Monthly ECR deposit (15th rule)
- [ ] Interest and damages for default — structured

### ESI Domain (MVP — Complete)
- [ ] ESI registration threshold indicator (10 employees, salary ≤ ₹21,000)
- [ ] Monthly ESI deposit (15th rule)
- [ ] Half-yearly ESI return cycle

### Shops and Establishments (MVP — Top 5 States)
Model S&E compliance for the 5 most commercially active states:
- [ ] Maharashtra
- [ ] Karnataka
- [ ] Delhi
- [ ] Tamil Nadu
- [ ] Telangana

For remaining states: flag as STATE_SPECIFIC → "Check your state S&E Act."

### Books and Records (MVP — Indicators)
- [ ] Books of account maintenance indicator (IT Act + Companies Act + LLP Act)
- [ ] Invoice retention period indicator (GST: 72 months)
- [ ] Payroll records indicator (where applicable)

### Audit Indicators (MVP — As Indicators)
- [ ] Statutory audit applicability (companies: always; LLPs: if threshold crossed)
- [ ] Tax audit applicability (turnover-based)
- [ ] GST reconciliation (GSTR-9C) applicability indicator

---

## 3. PHASE 2 — POST-LAUNCH (3–6 MONTHS)

### Additional TDS Sections
- TCS (Tax Collected at Source) — Sec 206C, 206CQ
- TDS on purchase of goods (Sec 194Q)
- TDS on dividend, interest from securities, other sections
- Complete TDS section coverage

### Labour Laws (Phase 2)
- [ ] Minimum Wages compliance indicator (record keeping, display)
- [ ] Payment of Wages Act indicator
- [ ] Bonus Act compliance (payment by November 30) — with threshold
- [ ] Gratuity Act indicator (threshold + payment obligation)
- [ ] Maternity Benefit Act indicator
- [ ] Contract Labour Act registration indicator

### Professional Tax (Phase 2 — Expanded)
- [ ] All major PT states modeled (currently only Maharashtra in MVP detail)
- [ ] PT applicability, rates, payment cycles per state

### Shops and Establishments (Phase 2 — Expanded)
- [ ] Remaining major states added

### FSSAI (Phase 2)
- [ ] Registration category determination
- [ ] Renewal cycle
- [ ] Penalty for operating without license

### MSME / Udyam (Phase 2)
- [ ] Udyam registration recommendation
- [ ] MSME Form I filing (for purchasing businesses)

### Import/Export (Phase 2 — Basic)
- [ ] IEC requirement indicator
- [ ] LUT/bond filing indicator
- [ ] Basic DGFT/Customs awareness flags

### Advance Tax — Presumptive Taxpayers (Phase 2)
- [ ] Sec 44AD presumptive taxation scenario: single installment by March 15
- [ ] Comparison: regular vs. presumptive tax treatment

### Company Event-Based Filings (Phase 2 — Extended)
- [ ] BEN-2 (beneficial ownership)
- [ ] INC-23 + INC-22 (registered office other city)
- [ ] SH-7 (authorized capital increase)
- [ ] CHG-4 (charge satisfaction)
- [ ] Company name change
- [ ] Share buyback forms

---

## 4. PHASE 3 — DEFERRED / FUTURE MODULES

### FEMA / FDI Compliance
- Highly complex; changes frequently; requires professional consultation
- Flag only: if foreign ownership/investment detected → HUMAN_REVIEW_REQUIRED

### Factories Act (Full State Coverage)
- State-specific factory rules and forms
- Currently: indicator only + human review flag

### Environment / Pollution Control Board
- Project-based; state-specific; inspection-driven
- Currently: indicator only + human review flag

### Customs / Import Export Detailed
- Customs duty classification, bonds, DGFT compliance
- Complex and document-intensive

### Transfer Pricing
- For companies with international related-party transactions
- Requires TP study, Form 3CEB

### Section 8 / NGO / Trust Compliance
- Different tax regime (Sec 11/12), different reporting requirements
- Separate module needed

### Employee Stock Options (ESOP)
- Complex company-level compliance; triggered only for companies with ESOP schemes

### Insolvency / IBBI Related
- Not applicable to going-concern businesses

### SEBI / Listed Company Compliance
- Out of scope for SME-focused product

### State-Level Specific Taxes
- Entry tax, entertainment tax, electricity duty (state-specific)
- Low relevance for digital/service businesses

---

## 5. MVP COMPLIANCE ITEM COUNT (ESTIMATE)

| Domain | Estimated Records |
|--------|------------------|
| GST | 15–20 |
| Income Tax | 10–12 |
| TDS (core sections) | 18–22 |
| MCA / Companies Act | 12–15 |
| LLP | 6–8 |
| EPF | 4–5 |
| ESI | 3–4 |
| Shops & Establishments (5 states) | 10–15 |
| Books/Records/Audit Indicators | 6–8 |
| **Total MVP records** | **~85–110** |

Each record is a `compliance_master` row with full source links, due date rule, and penalty record.

This is the minimum viable compliance library for the product to be genuinely useful.

---

## 6. MVP ENTITY TYPE PRIORITIZATION

Not all entity types need equal depth at launch. Priority order:

| Priority | Entity Types | Reason |
|----------|-------------|--------|
| 1 | Private Limited Company | Largest segment with formal compliance obligations |
| 2 | LLP | Growing segment; moderate compliance complexity |
| 3 | Sole Proprietorship | Very large in count; GST/IT primary concerns |
| 4 | OPC | Similar to Pvt Ltd with some simplifications |
| 5 | Partnership Firm | Less common for newer businesses; basic compliance |
| 6 | Public Limited Company | More complex; flag human review for advanced items |

---

## 7. MVP DATA QUALITY STANDARD

Before any compliance record goes live in the product:

- [ ] Primary statutory source identified and verified active
- [ ] Notification/rule reference accurate and current
- [ ] Due date rule encoded and test-computed for at least 3 periods
- [ ] Penalty structure sourced from the same statutory provision
- [ ] Source URL verified as active and pointing to original text
- [ ] Applicability rule expression tested against at least 3 sample business profiles
- [ ] Last verified date set to within 30 days of launch
- [ ] review_due_by date set (90 days from verification)

No compliance record should go live with `confidence_level = LOW` on its primary source.
