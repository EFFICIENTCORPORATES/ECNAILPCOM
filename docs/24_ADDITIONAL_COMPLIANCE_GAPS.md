# Document 24 — Additional Compliance Gaps
## Items Not Covered in B1–B10 But Identified During Legal Research

**SCOPE:** This document records compliance items and legal provisions that were not in the original B1–B10 list but were discovered during the B1–B10 analysis in doc 23. These are real legal obligations that affect the compliance engine's accuracy. Each is assessed for MVP vs. Phase 2 placement.

**FORMAT PER ITEM:** Same as doc 23.

---

## GAP-1 — Section 43B(h): Tax Disallowance for Delayed MSME Payments

### What is already resolved

**Source:** Finance Act, 2023 inserted a new clause (h) in **Section 43B of the Income Tax Act, 1961**, effective from Assessment Year 2024-25 (Financial Year 2023-24 onwards).

**The provision:** Any sum payable by an assessee to a micro or small enterprise registered under the MSMED Act 2006 that is not paid within the time limit prescribed under **Section 15 of the MSMED Act** shall be allowed as a deduction only in the year of actual payment — not in the year of accrual.

**Section 15 of MSMED Act, 2006** prescribes:
- Where a written agreement exists: payment must be made within the period agreed upon, but not exceeding 45 days from the day of acceptance.
- Where no written agreement exists: payment must be made within 15 days from the day of acceptance.

**Consequence:** If a business buys goods/services from an MSME supplier and pays after 45 days (or 15 days if no agreement), the purchase expense is **disallowed** in the current year under Income Tax. It will be deductible only in the year of actual payment.

**Why this is a critical gap in the current architecture:**

The current Part A compliance library records MSME Form I (the MCA reporting obligation) but does not record Section 43B(h) (the income tax consequence of the same delayed payment). These are two separate legal obligations arising from the same underlying fact — and they reinforce each other. A business owner who understands only the MCA Form I obligation but not the 43B(h) tax disallowance is insufficiently informed.

### What remains unresolved

Whether any CBDT circular has clarified the interaction between Section 43B(h) and the matching principle (e.g., whether accrual basis taxpayers must specifically track MSME payment timing). The provision is relatively new and professional interpretation continues.

### Why it matters to the compliance engine

This creates a new compliance indicator that should trigger for:
- Entity types: ALL (including proprietorships, partnerships, LLPs, and companies)
- Trigger: Business makes purchases from MSME-registered suppliers
- Risk: Income tax disallowance of purchase expenses if payment exceeds 45 days

**Relationship to MSME Form I:** MSME Form I applies only to companies. Section 43B(h) applies to ALL assessees. This makes Section 43B(h) broader in scope.

### Primary source

Section 43B(h) of the Income Tax Act, 1961 as inserted by Finance Act, 2023. Available from incometax.gov.in or the Finance Act 2023 Gazette publication.

### Critical blocker or deferred

**NOT A BLOCKER for MVP if treated as an INDICATOR.** Should be added as a new compliance master record:
- `compliance_code: IT_MSME_PAYMENT_43B_H_INDICATOR`
- `obligation_type: INDICATOR`
- `domain: INCOME_TAX`
- `description: "Payments to MSME suppliers delayed beyond 45 days are not deductible in the year of accrual (Section 43B(h), IT Act 1961). Expense is deductible only in the year of actual payment."`
- `applicability_rule: makes_purchases_from_msme = true OR is_trading_or_manufacturing = true` (conservative flag)

### Recommended next decision

Add `IT_MSME_PAYMENT_43B_H_INDICATOR` to MVP library. Source from Finance Act 2023. Flag for all businesses with trading or manufacturing activity. Connect it conceptually (in the UI description) to the MSME Form I obligation for companies.

---

## GAP-2 — Section 206AB/206CCA: Higher TDS/TCS for ITR Non-Filers

### What is already resolved

**Source:** Finance Act 2021 inserted:
- **Section 206AB of the Income Tax Act, 1961** — Higher TDS rate for "Specified Persons" (persons who have not filed ITR for 2 preceding FYs and whose total TDS/TCS exceeded ₹50,000 in each of those years).
- **Section 206CCA** — Higher TCS rate for the same "Specified Persons."

**Effective from:** July 1, 2021.

**The higher rate:** Twice the normal TDS rate OR 5%, whichever is higher.

**Compliance obligation for TDS deductors:** Before making a payment on which TDS applies, the deductor MUST check whether the payee is a "Specified Person" under Section 206AB. CBDT provides a utility/portal (Compliance Check for Sections 206AB and 206CCA — available on the income tax portal) for this purpose.

**Who this affects:** Any business making payments subject to TDS must check each payee's ITR filing status before applying the rate. This is an ongoing obligation, not a one-time check.

### What remains unresolved

Whether CBDT has issued any further guidance on the frequency and method of the compliance check (is one check per FY per payee sufficient, or does it need to be done before each payment?). The statute does not prescribe frequency of checking — it creates liability for the deductor if they use the wrong rate.

### Why it matters to the compliance engine

This is a **process obligation** for TDS deductors — a check they must perform, not a filing per se. It does not have a single due date. It is better modeled as:
- `obligation_type: INDICATOR`
- `domain: TDS`
- `description: "Businesses deducting TDS must verify each payee's ITR filing status before applying TDS rates. If payee is a 'Specified Person' under Sec 206AB, double rate applies."`
- No due date (continuous obligation)

**This is not currently in the Part A architecture.** It should be added as an indicator compliance record.

### Primary source

Section 206AB and Section 206CCA, Income Tax Act, 1961 (inserted by Finance Act 2021). Effective July 1, 2021.

### Critical blocker or deferred

**NON-BLOCKING for MVP.** Add as an INDICATOR record in the library. The record helps users understand they have a process obligation for TDS but does not have a computed due date.

### Recommended next decision

Add `IT_TDS_206AB_CHECK_INDICATOR` as an INDICATOR-type compliance item. Applicable to all businesses with TAN that make TDS-applicable payments. Source: Section 206AB, IT Act 1961.

---

## GAP-3 — Small Company Definition Update: Companies Act Amendment

### What is already resolved

The definition of "small company" under Section 2(85) of the Companies Act, 2013 has been amended twice in recent years:

**Amendment 1 (Companies Amendment Act 2021, effective 01.04.2021):**
- Paid-up capital ≤ ₹2 Cr AND turnover ≤ ₹20 Cr
(Previously, the threshold was ₹50 lakh paid-up capital OR ₹2 Cr turnover — note: old rule was OR, new rule is AND)

**Amendment 2 (Companies (Amendment) Act 2022, via notification effective 2022):**
- Paid-up capital ≤ ₹4 Cr AND turnover ≤ ₹40 Cr
(Source: MCA Notification S.O. 1178(E) dated 15.03.2022)

**Why this matters critically:** The small company status determines:
1. **MGT-7 vs. MGT-7A:** Small companies and OPCs file **MGT-7A** (simplified); all other companies file **MGT-7**.
2. **Audit requirements:** Small companies have certain relaxations.
3. **Board meeting requirements:** Small companies can hold board meetings with reduced notice.

The Part A compliance architecture (docs 02, 04) references MGT-7A for small companies and OPCs, which is correct. But the **applicability rule threshold** for "small company" must use the current ₹4 Cr paid-up capital AND ₹40 Cr turnover thresholds from the 2022 amendment, not older thresholds.

### What remains unresolved

Whether any further amendment to the small company definition has been issued between August 2025 and June 2026. The 2022 thresholds are the most recent known to the author.

### Primary source

Section 2(85), Companies Act, 2013 as amended. Current amendment: MCA Notification S.O. 1178(E) dated 15.03.2022.

### Critical blocker or deferred

**CRITICAL BLOCKER** for the MGT-7 vs. MGT-7A applicability rule. The wrong threshold causes incorrect form identification — a company using MGT-7A when it should use MGT-7 (or vice versa) is a compliance error.

**Correction to current architecture:** The `applicability_rule` for `MCA_MGT7A_ANNUAL` must use:
- `paid_up_capital <= 4,00,00,000 (₹4 Cr)` AND `annual_turnover <= 40,00,00,000 (₹40 Cr)` for small company classification
- AND entity_type = OPC (OPCs always file MGT-7A regardless of turnover)

### Recommended next decision

1. Update applicability rules for `MCA_MGT7_ANNUAL` and `MCA_MGT7A_ANNUAL` to use the ₹4 Cr / ₹40 Cr thresholds.
2. Source: Section 2(85) CA 2013 + MCA Notification S.O. 1178(E) dated 15.03.2022.
3. Verify from mca.gov.in whether any further amendment has been issued post-August 2025.

---

## GAP-4 — Section 194Q: TDS on Purchase of Goods (Not in Part A)

### What is already resolved

**Source:** Section 194Q of the Income Tax Act, 1961, inserted by Finance Act 2021 with effect from July 1, 2021.

**Provision (in substance):** Any buyer of goods (other than certain exempt categories) who is responsible for paying to a resident seller and whose total sales/turnover/gross receipts in the immediately preceding FY exceed **₹10 Cr** must deduct TDS at **0.1%** on any payment to any seller for goods worth **more than ₹50 lakh in the FY.**

**This is significant because:**
1. It applies to the BUYER, not just to professional/service payments.
2. The threshold triggers at ₹10 Cr buyer turnover — meaning mid-to-large businesses become TDS deductors on goods purchases.
3. It overlaps with TCS under Section 206C(1H) but a clarification exists: if the buyer is liable to deduct under 194Q, the seller is NOT required to collect under 206C(1H) for the same transaction.

### What remains unresolved

The interaction between Section 194Q and transactions with unregistered MSME sellers, export payments, and certain exempt categories needs careful handling. These are edge cases the compliance engine should flag as `requires_human_review` rather than attempting to resolve.

### Why it matters to the compliance engine

Section 194Q was NOT included in the Part A TDS coverage (doc 02). The Part A TDS table covers common sections (192, 194C, 194I, 194J, 194A, 194H, 194B) but omits 194Q. This creates a gap for trading or manufacturing businesses with turnover > ₹10 Cr.

The compliance engine should add `TDS_194Q_GOODS_PURCHASE` as a separate TDS obligation with:
- Applicability: entity makes goods purchases + annual_turnover > ₹10 Cr
- TDS rate: 0.1% on purchase value exceeding ₹50 lakh from single seller in FY
- Deposit due date: Same as other TDS deposits (7th of following month; April 30 for March deductions)
- Return: Covered in the quarterly TDS return (same Form 26Q as other non-salary TDS)

### Primary source

Section 194Q, Income Tax Act, 1961 (Finance Act 2021). CBDT Circular No. 13/2021 dated 30.06.2021 provides clarifications on the interaction between 194Q and 206C(1H).

### Critical blocker or deferred

**NON-BLOCKING for MVP if restricted to flagging.** Add as an INDICATOR for trading/manufacturing businesses with turnover > ₹10 Cr for MVP. Full TDS deposit/return tracking can be Phase 2.

---

## GAP-5 — Section 206C(1H): TCS on Sale of Goods (Not in Part A)

### What is already resolved

**Source:** Section 206C(1H) of the Income Tax Act, 1961, inserted by Finance Act 2020 with effect from October 1, 2020.

**Provision:** Every seller of goods whose total sales/turnover in the immediately preceding FY exceeds **₹10 Cr** must collect tax at source (TCS) at **0.1%** on the amount received from a buyer in excess of **₹50 lakh in the FY**, for any goods sold.

**Note:** This does NOT apply where the buyer is required to deduct TDS under Section 194Q on the same transaction (to avoid double taxation).

### Why it matters to the compliance engine

This creates a TCS obligation for large sellers of goods (trading, manufacturing with turnover > ₹10 Cr) that is currently absent from the Part A architecture. The obligation mirrors the TDS deposit and return filing cycle.

### Primary source

Section 206C(1H), Income Tax Act, 1961 (Finance Act 2020). Effective October 1, 2020.

### Critical blocker or deferred

**DEFERRED — NON-BLOCKING for MVP.** Part A doc 09 explicitly deferred TCS to Phase 2. This is consistent. Flag for Phase 2.

---

## GAP-6 — DIR-3 KYC Due Date Correction (Part A Doc 05 Table)

### What is resolved

This is a minor correction to the due date encoding in Part A doc 05.

The doc 05 OFFSET_FROM_FY_END table listed DIR-3 KYC as "~183 days from FY end = September 30."

The more precise encoding is: `FIXED_ANNUAL` rule type with `fixed_day: 30`, `fixed_month: 9`, `fixed_in_year_context: CURRENT_FY_END_YEAR`.

The "current FY end year" for DIR-3 KYC for the March 31, 2026 compliance date is: September 30, **2026** (not 2027 like an AY-based item). This is within the same calendar year as the FY end date, not in the next year.

This is a precision correction that does not change the output date (September 30) but ensures the computation logic is correctly coded for future FY transitions.

### Primary source

Rule 12A, Companies (Appointment and Qualification of Directors) Rules, 2014 — confirmed in B10 above.

### Critical blocker or deferred

**MINOR CORRECTION — NOT A BLOCKER.** The output date is the same (September 30). Only the internal computation logic path changes.

---

## ADDITIONAL GAPS SUMMARY

| Gap | Description | MVP or Phase 2 | Blocker? |
|-----|------------|---------------|---------|
| GAP-1 | Section 43B(h): MSME payment tax disallowance | MVP — add as INDICATOR | No |
| GAP-2 | Section 206AB/206CCA: Higher TDS for ITR non-filers | MVP — add as INDICATOR | No |
| GAP-3 | Small company definition: ₹4Cr/₹40Cr thresholds | MVP — CRITICAL fix to applicability rule | YES for MGT-7/7A distinction |
| GAP-4 | Section 194Q: TDS on purchase of goods | Phase 2 (for full tracking); MVP indicator for >₹10Cr trading | No |
| GAP-5 | Section 206C(1H): TCS on sale of goods | Phase 2 (already deferred in doc 09) | No |
| GAP-6 | DIR-3 KYC due date encoding correction | Minor correction — non-blocking | No |
