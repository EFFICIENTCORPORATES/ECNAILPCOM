# C14 — Population Priority Framework
## Framework for Sequencing the Library Population Work

---

## 1. Objective

Define the criteria and method for deciding which compliance rules to populate first, how to sequence domains and individual rules within domains, and how to make defensible trade-offs when time or research capacity is constrained.

The population priority framework is a decision-making tool, not a fixed queue. As legal research progresses, as user research reveals high-demand areas, or as critical blockers are cleared, priorities may shift. This framework provides the principles for making those shifts in a documented, coherent way.

---

## 2. Why It Matters to the Compliance Engine

A compliance library is only as useful as the depth of what it covers. A library that covers 100% of GST obligations but 0% of EPF obligations does not serve manufacturing businesses well. A library that covers annual obligations but misses monthly obligations leaves calendar views mostly empty.

Equally, a library that tries to cover every domain at once at 20% depth is less useful than one that covers key domains at 90% depth. The priority framework prevents both failure modes by directing effort toward the rules that produce the most compliance value per unit of population effort.

---

## 3. Design Principles

**P1 — User prevalence first.** Rules that apply to the broadest user base are prioritized over niche rules. GSTR-3B applies to every GST-registered business; MSME Form I applies only to companies with MSME suppliers. GSTR-3B is prioritized higher.

**P2 — Risk consequence second.** Where two rules have similar user prevalence, the one with higher severity (prosecution risk, larger penalties, registration cancellation) is prioritized. A missed obligation with CRITICAL consequences must be in the library before a missed obligation with LOW consequences.

**P3 — Source readiness third.** Rules with confirmed, ready-to-retrieve primary sources are prioritized over rules where the research is still blocked. Populating in order of readiness maximizes throughput.

**P4 — Calendar completeness.** The compliance calendar must have meaningful coverage for every month. Rules must be selected to ensure that every month in the financial year has at least one APPLICABLE item for the most common business profiles.

**P5 — Dependency ordering.** If Rule A depends on Rule B (e.g., GSTR-9 depends on GSTR-3B being in the library for its cascade logic to work), Rule B must be populated before Rule A.

---

## 4. Priority Scoring Model

Each candidate rule receives a priority score from 0 to 100 computed from four factors:

---

### Factor 1: User Base Breadth (max 40 points)

"What percentage of the target user base does this rule affect?"

| Coverage | Points |
|----------|--------|
| Applies to all businesses (e.g., GST returns, ITR) | 35–40 |
| Applies to most businesses (e.g., TDS for salary payers) | 25–34 |
| Applies to companies and LLPs only (e.g., AOC-4, MGT-7) | 15–24 |
| Applies to a specific subset (e.g., ≥20 employees only) | 8–14 |
| Applies to a narrow niche (e.g., food businesses only for FSSAI) | 3–7 |
| Applies to a very specific edge case | 0–2 |

---

### Factor 2: Consequence Severity (max 30 points)

"How serious is non-compliance with this rule?"

Based on the `base_severity_score` ranges from C6:

| Severity Band | Points |
|--------------|--------|
| CRITICAL (score 80–100) | 25–30 |
| SEVERE (score 60–79) | 18–24 |
| HIGH (score 40–59) | 11–17 |
| MODERATE (score 20–39) | 5–10 |
| LOW (score 0–19) | 0–4 |

---

### Factor 3: Source Readiness (max 20 points)

"How ready is this rule for population without blocking research?"

| Source Status | Points |
|--------------|--------|
| Primary source confirmed, ready to encode | 18–20 |
| Primary source identified, minor retrieval work needed | 12–17 |
| Primary source known but requires research (notifications, amendments) | 6–11 |
| Partially blocked (e.g., one component missing) | 3–5 |
| Blocked (primary source not retrievable, statute/portal divergence unresolved) | 0–2 |

---

### Factor 4: Calendar Distribution Value (max 10 points)

"Does including this rule improve coverage of under-represented months or frequencies?"

| Situation | Points |
|-----------|--------|
| Fills a month or frequency with no coverage currently | 8–10 |
| Improves coverage of an already-represented month | 4–7 |
| Adds to a month/frequency already well-covered | 0–3 |

---

### Priority Score Calculation

```
Priority Score = Factor1 + Factor2 + Factor3 + Factor4
                                    (max 100 points)
```

Rules with scores ≥ 70 are TIER 1 (populate first).
Rules with scores 40–69 are TIER 2 (populate in Phase 1 expansion).
Rules with scores < 40 are TIER 3 (defer to Phase 2).

---

## 5. MVP Priority List by Domain

The following table shows illustrative priority assessments for the most commonly expected compliance rules across domains. These are indicative, not final — actual scoring requires confirming source readiness at the time of population.

---

### GST Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| GSTR-3B Monthly (Regular) | Very High | HIGH | Ready (B1: monthly confirmed) | Monthly | ~88 | TIER 1 |
| GSTR-1 Monthly | Very High | HIGH | Ready | Monthly | ~85 | TIER 1 |
| GSTR-3B QRMP Quarterly | High | HIGH | Partially blocked (B1: state groups need Notif 84/2020-CT) | Quarterly | ~70 | TIER 1 |
| GSTR-9 Annual Return | High | MODERATE | Ready (B3: base rule confirmed) | Annual | ~72 | TIER 1 |
| GSTR-9C Reconciliation | Medium | HIGH | Ready (B4: ₹5Cr threshold confirmed) | Annual | ~68 | TIER 2 |
| GSTR-4 Composition Annual | Medium | MODERATE | Ready | Annual | ~55 | TIER 2 |
| CMP-08 Composition Quarterly | Medium | MODERATE | Ready | Quarterly | ~55 | TIER 2 |
| E-Invoicing Indicator | Medium | HIGH | Partially blocked (B2: threshold needs verification) | Continuous | ~60 | TIER 2 |
| GSTR-1 Quarterly (QRMP) | Medium | HIGH | Ready | Quarterly | ~65 | TIER 2 |

---

### Income Tax Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| Advance Tax Q1 (June 15) | High | SEVERE | Ready | Q1 | ~82 | TIER 1 |
| Advance Tax Q2 (Sept 15) | High | SEVERE | Ready | Q2 | ~82 | TIER 1 |
| Advance Tax Q3 (Dec 15) | High | SEVERE | Ready | Q3 | ~82 | TIER 1 |
| Advance Tax Q4 (Mar 15) | High | SEVERE | Ready | Q4 | ~82 | TIER 1 |
| ITR (non-audit; July 31) | Very High | SEVERE | Ready | Annual | ~88 | TIER 1 |
| ITR (audit; Oct 31) | Medium | SEVERE | Ready | Annual | ~75 | TIER 1 |
| Tax Audit Report (Sept 30) | Medium | HIGH | Ready | Annual | ~70 | TIER 1 |
| Section 43B(h) Indicator | Medium | HIGH | Ready (GAP-1: Finance Act 2023) | Continuous | ~65 | TIER 2 |
| Section 206AB Indicator | Medium | HIGH | Ready (GAP-2: Finance Act 2021) | Continuous | ~60 | TIER 2 |

---

### TDS Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| TDS Deposit Monthly (non-govt) | High | CRITICAL | Ready | Monthly | ~90 | TIER 1 |
| TDS Return Quarterly (Form 26Q) | High | HIGH | Ready | Quarterly | ~78 | TIER 1 |
| TDS Return Quarterly (Form 24Q — salary) | Medium | HIGH | Ready | Quarterly | ~72 | TIER 1 |
| Form 16 Issuance (May 31) | High | HIGH | Ready | Annual | ~75 | TIER 1 |
| Form 16A Issuance | Medium | MODERATE | Ready | Quarterly | ~60 | TIER 2 |

---

### MCA Company Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| AOC-4 (Financial Statements) | Companies | HIGH | Ready | AGM-based | ~70 | TIER 1 |
| MGT-7 (Annual Return) | Companies | HIGH | Ready | AGM-based | ~70 | TIER 1 |
| MGT-7A (Small Company AR) | Small companies/OPC | HIGH | Ready (GAP-3: threshold confirmed) | AGM-based | ~68 | TIER 1 |
| DIR-3 KYC (Sept 30) | All directors | HIGH | Ready (B10: confirmed) | Annual | ~75 | TIER 1 |
| DPT-3 (June 30) | All companies | MODERATE | Ready (B9: confirmed) | Annual | ~72 | TIER 1 |
| ADT-1 (Auditor Appointment) | Companies | MODERATE | Ready | Event-based | ~60 | TIER 2 |
| DIR-12 (Director Change) | Companies | MODERATE | Ready | Event-based | ~58 | TIER 2 |
| MSME Form I (Oct 31, Apr 30) | Companies (conditional) | MODERATE | Ready (B8: confirmed) | Half-yearly | ~62 | TIER 2 |

---

### MCA LLP Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| Form 11 Annual Return (May 30) | LLPs | MODERATE | Ready | Annual | ~65 | TIER 2 |
| Form 8 Statement of Accounts (Oct 30) | LLPs | MODERATE | Ready | Annual | ~65 | TIER 2 |

---

### EPF Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| EPF ECR Deposit Monthly (15th) | Employers ≥20 | HIGH | Ready | Monthly | ~78 | TIER 1 |
| EPF Registration (one-time) | New employers ≥20 | HIGH | Ready | One-time | ~72 | TIER 1 |

---

### ESI Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| ESI Contribution Deposit Monthly (15th) | Employers ≥10 | HIGH | Ready | Monthly | ~75 | TIER 1 |
| ESI Return Half-Yearly | Employers ≥10 | MODERATE | Blocked (B5: statute/portal divergence) | Half-yearly | ~40 | TIER 2 (blocked) |
| ESI Registration (one-time) | New employers ≥10 | HIGH | Ready | One-time | ~70 | TIER 1 |

---

### Labour Law Domain

| Rule | User Base | Severity | Source Ready | Calendar | Est. Score | Tier |
|------|-----------|----------|-------------|----------|-----------|------|
| Bonus Payment Annual (Nov 30) | Employers ≥20 | HIGH | Ready (B7: confirmed) | Annual | ~72 | TIER 1 |
| Gratuity Funding/Provision | Employers ≥10 | HIGH | Ready | Continuous | ~60 | TIER 2 |
| Minimum Wages Compliance | All employers | HIGH | Partially blocked (state-specific rates) | Continuous | ~55 | TIER 2 |

---

## 6. MVP Target Library: Tier 1 Population List

Based on the scoring above, the following rules are recommended for MVP (Tier 1) library population, covering the most prevalent business profiles and highest-risk obligations:

**Priority order is: TDS → GST Monthly → Income Tax → EPF/ESI → MCA Company → Labour → LLP**

| Priority | Domain | Rule Code | Due Date Reference |
|----------|--------|-----------|--------------------|
| 1 | TDS | `TDS_DEPOSIT_MONTHLY_NON_GOVT` | 7th of following month |
| 2 | GST | `GST_GSTR3B_MONTHLY_REGULAR` | 20th of following month |
| 3 | GST | `GST_GSTR1_MONTHLY` | 11th of following month |
| 4 | ADVANCE_TAX | `IT_ADVANCE_TAX_Q1`, `Q2`, `Q3`, `Q4` | June 15, Sep 15, Dec 15, Mar 15 |
| 5 | INCOME_TAX | `IT_ITR_NONAUTDIT_ANNUAL` | July 31 (AY) |
| 6 | INCOME_TAX | `IT_ITR_AUDIT_ANNUAL` | October 31 (AY) |
| 7 | TDS | `TDS_RETURN_QUARTERLY_26Q` | Last day of month after quarter end |
| 8 | TDS | `TDS_RETURN_QUARTERLY_24Q` | Last day of month after quarter end |
| 9 | TDS | `TDS_FORM16_ANNUAL` | May 31 |
| 10 | EPF | `EPF_ECR_DEPOSIT_MONTHLY` | 15th of following month |
| 11 | ESI | `ESI_CONTRIBUTION_DEPOSIT_MONTHLY` | 15th of following month |
| 12 | INCOME_TAX | `IT_TAX_AUDIT_ANNUAL` | September 30 (AY) |
| 13 | GST | `GST_GSTR9_ANNUAL` | December 31 |
| 14 | MCA_COMPANY | `MCA_DIR3_KYC_ANNUAL` | September 30 |
| 15 | MCA_COMPANY | `MCA_DPT3_ANNUAL` | June 30 |
| 16 | MCA_COMPANY | `MCA_AOC4_ANNUAL` | Within 30 days of AGM |
| 17 | MCA_COMPANY | `MCA_MGT7_ANNUAL` | Within 60 days of AGM |
| 18 | MCA_COMPANY | `MCA_MGT7A_ANNUAL` | Within 60 days of AGM |
| 19 | LABOUR_BONUS | `LABOUR_BONUS_PAYMENT_ANNUAL` | November 30 |
| 20 | EPF | `EPF_REGISTRATION_MANDATORY` | One-time / threshold trigger |

This 20-rule core library covers monthly obligations across GST and TDS, quarterly advance tax, key annual income tax filings, MCA annual filings, and the most prevalent labour law obligation.

---

## 7. Tier 2 Expansion Priorities (Post-MVP)

After the Tier 1 library is complete and verified, Tier 2 population expands coverage to:

1. GST QRMP quarterly variants (after B1 research is completed)
2. GST GSTR-9C annual reconciliation
3. GST composition scheme obligations (CMP-08, GSTR-4)
4. TDS Form 16A issuance
5. MCA event-based filings (DIR-12, PAS-3, CHG-1, ADT-1)
6. LLP annual filings (Form 8, Form 11)
7. MSME Form I half-yearly
8. ESI half-yearly return (after B5 research resolves the divergence)
9. INDICATOR records (43B(h), 206AB, e-invoicing)
10. Gratuity, Minimum Wages, Contract Labour indicators

---

## 8. Tier 3 Defer List

The following areas are explicitly deferred to Phase 2 and must not be populated for MVP:

1. Professional Tax (state-by-state slabs not yet researched; B6 resolution pending)
2. Shops & Establishments (state-specific; varies significantly)
3. Factories Act compliance (sector-specific; human review required)
4. FSSAI obligations (sector-specific)
5. FEMA/FDI compliance (HUMAN_REVIEW_REQUIRED by design)
6. TCS under Section 206C(1H) (deferred in doc 09)
7. Section 194Q TDS on goods purchase (indicator only for MVP)
8. State-specific labour laws beyond Payment of Bonus
9. Environment/pollution compliance
10. Import-Export Code and DGFT obligations (human review required)

---

## 9. Priority Review Cadence

The population priority list must be reviewed at three milestones:

**Before beginning population:** Confirm source readiness for all Tier 1 rules. Identify any that are blocked and either unblock or swap with a ready alternative.

**At 50% completion:** Review Tier 2 list for any items that should be elevated to Tier 1 based on user feedback or new research findings.

**At MVP launch:** Confirm the Tier 2 roadmap is realistic for the post-launch quarter. Identify any rules where legal changes (new notifications, Finance Act) require updating rules already in Tier 1.

---

## 10. What Should Be Deferred

**Automated priority scoring** (computing priority scores dynamically from the library's current state) is a Phase 2 library management feature. For MVP, the priority framework is applied manually by the Library Owner.

**User-demand-driven reprioritization** (surfacing rules requested by users that are not yet in the library) requires a feedback mechanism in the product. This is a Phase 2 product feature that will inform Phase 2 library population decisions.

---

## 11. Recommended Conclusion

A library of 20 carefully verified Tier 1 rules delivers more compliance value than a library of 60 partially verified rules. Depth and accuracy in core obligations — the ones that affect every GST-registered, TDS-liable, company-incorporated, or salary-paying business — are the foundation on which the product's credibility rests.

The priority framework ensures that every unit of effort spent on population goes to the rules with the highest impact. Rules that are blocked by research gaps are not forced through; they wait until the gap is resolved. Rules in Tier 3 are not abandoned — they are explicitly deferred with a documented rationale, so the roadmap is honest about what is and is not covered.
