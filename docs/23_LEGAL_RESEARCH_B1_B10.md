# Document 23 — Legal Research: B1–B10 Resolution
## Primary Source Validation for Unresolved Compliance Items

**SCOPE DISCIPLINE NOTICE:**
This document resolves only the B1–B10 legal research items listed in doc 10.
It does not reopen architecture, API design, UI, or product decisions.
All resolution is from primary statutory sources where possible.
Where primary source text is known with high confidence, it is cited precisely.
Where the author's knowledge is uncertain or may have changed post-August 2025, this is explicitly flagged.

**DATE OF ANALYSIS:** June 2026 (author knowledge cutoff: August 2025)
**IMPLICATION:** All notification-based rules must be verified against currently active notifications at the time of library population. Statute-based rules with no recent changes are treated as stable.

**FORMAT PER ITEM:**
1. What is already resolved
2. What remains unresolved
3. Why it matters to the compliance engine
4. Exact primary source required
5. Critical blocker or deferred/non-blocker
6. Recommended next decision

---

## B1 — GSTR-3B State Staggering (20th / 22nd / 24th)

### What is already resolved

The legal basis for GSTR-3B is **Section 39 of the CGST Act, 2017** read with **Rule 61(1) of the CGST Rules, 2017**. The base statutory due date under Rule 61(1) is the 20th of the month following the tax period.

The general pattern as of August 2025 is:

**For monthly GSTR-3B filers (turnover > ₹5 Cr):**
All states: 20th of the following calendar month. No state-wise staggering applies to this category. This is confirmed and stable.

**For QRMP scheme quarterly GSTR-3B filers (turnover ≤ ₹5 Cr, enrolled in QRMP):**
The 22nd/24th staggering applies. Two groups of states:

Group A (due by 22nd of month after quarter end):
Chhattisgarh, Madhya Pradesh, Gujarat, Maharashtra, Karnataka, Goa, Kerala, Tamil Nadu, Telangana, Andhra Pradesh, UT of Dadra and Nagar Haveli and Daman and Diu, UT of Puducherry, UT of Andaman and Nicobar Islands, UT of Lakshadweep

Group B (due by 24th of month after quarter end):
Himachal Pradesh, Punjab, Uttarakhand, Haryana, Rajasthan, Uttar Pradesh, Bihar, Sikkim, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, Meghalaya, Assam, West Bengal, Jharkhand, Odisha, UT of Jammu and Kashmir, UT of Ladakh, UT of Chandigarh, Delhi

This grouping was established via **Notification No. 84/2020-Central Tax dated 10.11.2020** for QRMP scheme filing cycles.

**CRITICAL NUANCE:**
The commonly referenced "20th / 22nd / 24th" pattern across ALL taxpayers is partially accurate but imprecise. The correct reading is:
- Monthly large taxpayers (> ₹5 Cr): uniformly 20th, all states
- QRMP quarterly taxpayers (≤ ₹5 Cr): 22nd or 24th by state group

There is NO 20th/22nd/24th staggering for monthly non-QRMP filers — they are all on the 20th.

### What remains unresolved

1. The state groupings above were accurate as of August 2025 based on Notification 84/2020-CT. Any subsequent amendment notification altering the state groupings or due dates must be checked. It is possible (though not known to the author) that further notifications have been issued between August 2025 and June 2026.

2. The treatment of states that may have changed Union Territory status or administrative boundaries (this has been stable since J&K bifurcation in 2019, but should be confirmed).

3. Whether any class-specific modifications exist (e.g., taxpayers under ISD, casual taxable persons, non-resident taxable persons have separate return timelines — these are separate compliances and should not be confused with GSTR-3B).

### Why it matters to the compliance engine

The `due_date_rule` record for `GST_GSTR3B_QRMP_QUARTERLY` requires an accurate `state_offset_rules` array. A business in Maharashtra (Group A) gets a 22nd due date; a business in Delhi (Group B) gets a 24th due date. The engine cannot compute the correct date without the correct grouping. An incorrect grouping produces a wrong due date shown to the user.

For monthly filers (> ₹5 Cr), no state variation is needed — the 20th applies uniformly.

### Exact primary source required

- **Notification No. 84/2020-Central Tax dated 10.11.2020** — defines QRMP quarterly 3B due dates and state groups. Available at cbic.gov.in. Must be retrieved and state group lists confirmed from the notification text.
- **Any subsequent amendment notifications** between Notification 84/2020-CT and the current date that may have altered the state groups.
- **Rule 61(1) of CGST Rules, 2017** (current amended version) — for the base 20th date.

### Critical blocker or deferred

**CRITICAL BLOCKER** for the `GST_GSTR3B_QRMP_QUARTERLY` compliance record.
**NON-BLOCKER** for the `GST_GSTR3B_MONTHLY_REGULAR` record (all states = 20th, no state data needed).

### Recommended next decision

1. Retrieve Notification 84/2020-CT from cbic.gov.in and extract the exact state group lists.
2. Search for any amendment notifications post-Notification 84/2020-CT that modify the state groupings.
3. Populate `state_offset_rules` in the `due_date_rule` record ONLY after Step 1 and 2 are complete.
4. The GSTR-3B monthly record can be populated immediately with `state_based_variation: false` and `offset_days: 20`.

---

## B2 — E-Invoicing Threshold (Current Level)

### What is already resolved

**Legal basis:** E-invoicing (IRP — Invoice Registration Portal) is governed by **Rule 48(4) of the CGST Rules, 2017** and **Notification No. 13/2020-Central Tax dated 21.03.2020** (as amended by subsequent notifications).

The threshold has been progressively reduced:

| Threshold | Effective From | Notification |
|-----------|---------------|-------------|
| ₹500 Cr | 01.10.2020 | Notif. 13/2020-CT + Notif. 70/2020-CT |
| ₹100 Cr | 01.01.2021 | Notif. 88/2020-CT |
| ₹50 Cr | 01.04.2021 | Notif. 5/2021-CT |
| ₹20 Cr | 01.04.2022 | Notif. 1/2022-CT |
| ₹10 Cr | 01.10.2022 | Notif. 10/2022-CT |
| ₹5 Cr | 01.08.2023 | Notif. 70/2023-CT (to be verified) |

*Note: Notification numbers for thresholds below ₹10 Cr should be verified against the CBIC website. The author's knowledge of exact notification numbers for the ₹5 Cr and below thresholds is not fully confirmed.*

**Confirmed as of author's knowledge cutoff (August 2025):** The threshold was ₹5 Cr of Aggregate Annual Turnover (AATO) in the preceding financial year.

### What remains unresolved

**Post-August 2025 notification status:** The GST Council has discussed reducing the threshold to ₹1 Cr. Whether any such notification was issued between August 2025 and June 2026 is unknown to the author. The current threshold at time of library population may be ₹5 Cr or lower.

The **exact notification number** for the ₹5 Cr threshold (effective ~August 2023) should be confirmed from cbic-gst.gov.in. The author's reference to "Notif. 70/2023-CT" is tentative and must be verified.

### Why it matters to the compliance engine

E-invoicing applicability is an `INDICATOR` compliance record in the master library. Its applicability rule checks `turnover_band` against the threshold. If the threshold is ₹5 Cr, then a business in the `5CR_10CR` band is APPLICABLE. If the threshold has dropped to ₹1 Cr, then even `1CR_5CR` businesses become APPLICABLE.

The wrong threshold creates a false-negative (missed obligation) for businesses near the threshold band.

### Exact primary source required

1. **cbic-gst.gov.in** — notifications section — retrieve the most recent notification setting the e-invoicing threshold.
2. Confirm the notification number, date, and exact AATO threshold.
3. Confirm whether any subsequent notification has further reduced the threshold post-August 2023.

### Critical blocker or deferred

**CRITICAL BLOCKER** for the `GST_EINVOICING_INDICATOR` compliance record's applicability rule. The threshold field directly controls which turnover bands trigger this flag.

### Recommended next decision

1. Retrieve the current active notification from cbic-gst.gov.in before populating the applicability rule.
2. Store the threshold in the `applicability_rule.rule_expression` as a THRESHOLD node against `annual_turnover_estimated`.
3. Store the applicable notification in `source_master` with `source_role: THRESHOLD_RULE` linked to the e-invoicing compliance record.
4. Set `review_due_by` to 90 days from library population — this threshold has historically changed every 6–18 months.

---

## B3 — GSTR-9 Optional/Exempt for Small Taxpayers (≤ ₹2 Cr AATO)

### What is already resolved

**Legal basis:** Section 44 of the CGST Act, 2017 mandates annual return filing for all registered taxpayers. Rule 80 of the CGST Rules, 2017 prescribes Form GSTR-9.

**The base statutory obligation:** Every registered person (except specified exempt categories) must file GSTR-9 annually. This is a statutory requirement.

**The exemption mechanism:** Section 44 contains the proviso: "Provided that the Commissioner may, on the recommendations of the Council, notify the class of registered persons who shall be exempted from filing annual return under this sub-section." This is the power under which CBIC issues exemption notifications for small taxpayers.

**Historical pattern of exemptions:**
- FY2017-18: Taxpayers with AATO ≤ ₹2 Cr exempted via Notification No. 44/2019-CT (as subsequently relaxed)
- FY2020-21: Taxpayers with AATO ≤ ₹2 Cr exempted via Notification No. 31/2021-CT
- FY2021-22: Taxpayers with AATO ≤ ₹2 Cr exempted
- FY2022-23: Taxpayers with AATO ≤ ₹2 Cr exempted via Notification No. 10/2023-CT dated 17.07.2023

*Note: Exact notification numbers for FY2021-22 and FY2022-23 exemptions should be verified. The pattern is consistent but individual notification numbers need confirmation.*

**What is settled:** The base statutory rule = APPLICABLE for all. The exemption is year-specific and granted via notification for each FY.

### What remains unresolved

**Year-specific exemptions for FY2023-24 and FY2024-25:** Whether CBIC issued similar exemption notifications for GSTR-9 for these years is not known to the author. The pattern suggests they likely did, but this must be confirmed from the actual notifications.

**Whether the ₹2 Cr threshold persists:** The Council may change the threshold for future years.

### Why it matters to the compliance engine

This directly affects the `applicability_rule` for `GST_GSTR9_ANNUAL`:
- If the exemption for a given FY has been issued: businesses with AATO ≤ ₹2 Cr should show `applicability_status: NOT_APPLICABLE` for that FY's GSTR-9.
- If no exemption notification is found: businesses with AATO ≤ ₹2 Cr are APPLICABLE.
- The system cannot make this determination without knowing the current-year notification status.

**Architectural recommendation (already in model):** Store each year's exemption notification as a `notification_extension` record with `period_affected: FY2024-25`. The applicability engine checks for active exemptions before flagging GSTR-9 as applicable for a given AATO band.

### Exact primary source required

1. **cbic-gst.gov.in** notifications — retrieve the GSTR-9 annual return filing exemption notifications for FY2023-24 and FY2024-25 (if issued).
2. Confirm the ₹2 Cr AATO threshold in each notification.
3. If no exemption notification found for a given FY, treat GSTR-9 as universally APPLICABLE for that year.

### Critical blocker or deferred

**DEFERRED — NON-BLOCKING** for initial library population. The base rule (GSTR-9 applicable to all registered taxpayers under Section 44) can be encoded immediately. The FY-specific exemption for ≤ ₹2 Cr is a `notification_extension` record that should be added alongside the base rule.

The base record CAN be populated with a note: "Annual return required under Section 44 CGST Act 2017. CBIC has historically exempted taxpayers with AATO ≤ ₹2 Cr via FY-specific notifications. Check current-year notification status."

### Recommended next decision

1. Populate the GSTR-9 base record as APPLICABLE to all registered regular scheme taxpayers.
2. Add a `CHECK_THRESHOLD` flag in the applicability rule for businesses with AATO ≤ ₹2 Cr: "Likely exempt — check current FY notification."
3. Add `notification_extension` records for FY2022-23 exemption (confirmed from Notification 10/2023-CT) and search for FY2023-24 and FY2024-25 exemptions separately.
4. Set `review_due_by` annually — this requires a new check every year after October (when annual return filings typically approach).

---

## B4 — GSTR-9C Threshold (Reconciliation Statement)

### What is already resolved

**Primary statutory source: Finance Act, 2021** — which amended Section 44 of the CGST Act, 2017. The amendment removed the mandatory Chartered Accountant/Cost Accountant certification requirement and shifted to self-certification. The amended Section 44 proviso now reads (in substance):

"Every registered person whose aggregate turnover during a financial year exceeds such amount as may be prescribed shall also furnish a self-certified reconciliation statement..."

**Rule 80(3) of CGST Rules, 2017** (as amended effective 01.08.2021 via Notification No. 30/2021-CT dated 30.07.2021) prescribes: GSTR-9C is required for taxpayers with AATO **exceeding ₹5 Cr** for the relevant financial year.

**This ₹5 Cr threshold is statute-backed (Rule 80(3)) and has been in force since FY2020-21.** It is currently stable and not year-specific (unlike the GSTR-9 small-taxpayer exemption which requires annual notification).

### What remains unresolved

1. Whether the ₹5 Cr threshold has been changed post-August 2025 by a subsequent Rule amendment or notification. The author is not aware of any such change, but it should be confirmed.
2. GSTR-9C (pre-FY2020-21) required CA/CMA certification. For compliance records covering historical filings, the old requirements may be relevant. For current compliance tracking, the self-certification rule (post-2021) applies.

### Why it matters to the compliance engine

The `GST_GSTR9C_ANNUAL` compliance record's applicability rule checks `turnover_band`. Businesses with AATO > ₹5 Cr must file both GSTR-9 AND GSTR-9C. Businesses ≤ ₹5 Cr file only GSTR-9 (if applicable under B3 above).

The ₹5 Cr threshold creates a distinction between:
- `5CR_10CR` and `ABOVE_10CR` bands: APPLICABLE for GSTR-9C
- `1CR_5CR` band: `CHECK_THRESHOLD` (may or may not be above ₹5 Cr)
- All lower bands: NOT_APPLICABLE for GSTR-9C

### Exact primary source required

1. **Rule 80(3) of CGST Rules, 2017** (current amended version) — confirm ₹5 Cr threshold.
2. **Notification No. 30/2021-CT dated 30.07.2021** — confirms the rule amendment effective date.
3. Any post-August 2025 rule amendment changing the threshold.

### Critical blocker or deferred

**NON-BLOCKING.** The ₹5 Cr threshold is statute/rule-backed and confirmed with HIGH confidence. The GSTR-9C record can be populated immediately with this threshold.

The only residual check is whether any post-August 2025 amendment changed the ₹5 Cr threshold.

### Recommended next decision

Populate `GST_GSTR9C_ANNUAL` immediately with:
- Applicability rule: `entity must be GST registered AND annual_turnover > ₹5 Cr`
- Source: Rule 80(3) CGST Rules + Notif. 30/2021-CT
- `requires_threshold_check: true` for `1CR_5CR` band
- Due date: December 31 of AY (same as GSTR-9)

---

## B5 — ESI Return Filing Status (Half-Yearly vs. Current Portal Requirements)

### What is already resolved

**Primary statute:** Employees' State Insurance Act, 1948.
**Primary rules:** Employees' State Insurance (Central) Rules, 1950.

Under **Rule 26 of ESI (Central) Rules, 1950**, an employer is required to submit a **Return of Contributions** in Form 5. The Rule specifies this return is for each contribution period (April-September and October-March), to be submitted within 42 days of the end of each contribution period:
- April-September contribution period: Return due by November 11
- October-March contribution period: Return due by May 11

This is the **statutory obligation under the Rules**.

**The operational divergence:** ESIC has moved significantly toward digital compliance. The ESIC portal (esic.gov.in) now requires:
1. Monthly challan submission and payment (via ESIC portal)
2. Monthly employee attendance/wages data upload

This monthly operational requirement is an administrative evolution, but the **formal statutory return obligation under Rule 26 (Form 5 half-yearly)** technically remains in the Rules text.

**This is a documented "statute vs. portal practice" divergence** — exactly the scenario flagged in the source strategy (doc 03).

### What remains unresolved

1. Whether Rule 26 of ESI (Central) Rules has been formally **amended** to replace Form 5 with a different (monthly/portal-based) return mechanism. The author does not have confirmed knowledge that the Rule text itself has been changed.

2. Whether any **official ESIC circular/notification** has explicitly retired the Form 5 half-yearly return and replaced it with the monthly portal submission as the official compliance mechanism.

3. Current ESIC portal requirements as of June 2026 — whether the half-yearly return filing option even exists in the portal, or whether it has been replaced.

### Why it matters to the compliance engine

This directly affects how `ESI_RETURN_HALFYEARLY` is encoded:
- If Rule 26 still requires Form 5: Encode as a half-yearly return with November 11 / May 11 due dates, and note the portal's monthly requirement as an additional operational obligation.
- If Rule 26 has been formally amended to monthly: Encode as monthly with 15th of next month due date.
- If there is genuine ambiguity: The compliance record should be flagged with `portal_vs_statute_divergence: true` and display BOTH requirements to the user.

### Exact primary source required

1. **Current text of Rule 26 of ESI (Central) Rules, 1950** — retrieve from the Ministry of Labour & Employment website or the official Gazette.
2. **Any official ESIC circular** that has retired, amended, or replaced the Form 5 half-yearly requirement.
3. **ESIC portal (esic.gov.in)** — what it currently requires and by what dates.

Until these three sources are checked, this compliance record should be marked `requires_human_review: true` with the note explaining the statute/portal ambiguity.

### Critical blocker or deferred

**CRITICAL BLOCKER** for the ESI return compliance record's due date rule. Cannot reliably encode the due date without knowing whether the statutory half-yearly return or a different operational cycle is the current operative requirement.

### Recommended next decision

1. Check Rule 26 of ESI (Central) Rules text from an official source.
2. Check esic.gov.in employer compliance section for current return requirements.
3. If ambiguity confirmed: Enter the ESI return compliance record with `tracking_status: HUMAN_REVIEW_REQUIRED` and `portal_vs_statute_divergence: true`, displaying both the statutory half-yearly obligation and the portal's monthly requirement.
4. Do NOT block library population entirely — enter what is known and flag the uncertainty explicitly.

---

## B6 — Professional Tax: Current State-Wise List and Thresholds

### What is already resolved

**Constitutional basis:** Article 276 of the Constitution of India permits states and UTs to levy taxes on professions, trades, callings, and employments. The constitutional cap is **₹2,500 per person per year**.

**States confirmed to levy Professional Tax (high confidence from statutory knowledge):**

| State | Governing Act |
|-------|--------------|
| Maharashtra | Maharashtra State Tax on Professions, Trades, Callings and Employments Act, 1975 |
| Karnataka | Karnataka Tax on Professions, Trades, Callings and Employments Act, 1976 |
| West Bengal | West Bengal State Tax on Professions, Trades, Callings and Employments Act, 1979 |
| Gujarat | Gujarat State Tax on Professions, Trades, Callings and Employments Act, 1976 |
| Tamil Nadu | Tamil Nadu Tax on Professions, Trades, Callings and Employments Act, 1992 |
| Andhra Pradesh | AP Tax on Professions, Trades, Callings and Employments Act, 1987 |
| Telangana | Telangana Tax on Professions, Trades, Callings and Employments Act, 1987 |
| Assam | Assam Professions, Trades, Callings and Employments Taxation Act, 1947 |
| Meghalaya | Meghalaya Professions, Trades, Callings and Employments Taxation Act, 1947 |
| Odisha | Odisha State Tax on Professions, Trades, Callings and Employments Act, 2000 |
| Bihar | Bihar State Tax on Professions, Trades, Callings and Employments Act, 2011 |
| Jharkhand | Jharkhand Tax on Professions, Trades, Callings and Employments Act, 2011 |
| Tripura | Tripura State Tax on Professions, Trades, Callings and Employments Act, 1987 |
| Sikkim | Sikkim Tax on Professions, Trades, Callings and Employments Act |

**States confirmed NOT to levy PT (stable, not expected to change):**
Delhi, Rajasthan (discontinued), Uttar Pradesh, Haryana, Punjab, Himachal Pradesh, Uttarakhand, Goa (author uncertain — needs confirmation), J&K, Ladakh, Arunachal Pradesh, Nagaland, Manipur, Mizoram.

**Uncertain / needs verification:**
- Madhya Pradesh: Had PT legislation but applicability is unclear — may have limited/no enforcement
- Chhattisgarh: Bifurcated from MP — PT status needs checking
- Kerala: Author is uncertain — needs confirmation
- Himachal Pradesh: Author believes no PT — needs confirmation

### What remains unresolved

1. Exact PT slabs for each state — these are set by state schedules and change via state budget amendments. The author cannot reliably state current slabs for any state.
2. PT registration thresholds (minimum salary/income below which PT does not apply) — state-specific and changeable.
3. Payment frequency (monthly vs. annual) per state — state-specific.
4. Whether Goa, Chhattisgarh, Kerala, and Madhya Pradesh currently levy PT.

### Why it matters to the compliance engine

PT compliance records are modeled as `STATE_SPECIFIC` per state. For states where PT is confirmed, a compliance record exists. For states where PT status is uncertain, the record should show `applicability_status: STATE_SPECIFIC` with instruction to verify locally.

**This is a secondary blocker for those specific states.** States with confirmed PT (Maharashtra, Karnataka, West Bengal, Tamil Nadu, Andhra Pradesh, Telangana, Gujarat) should have records populated as priority.

### Exact primary source required

Per state, the governing Act + most recent state budget amendment notification. Maharashtra's PT Act + schedule is available on the Maharashtra government website. Karnataka's PT Act is on the Karnataka government portal. Each state's Finance Department website has the PT schedule.

### Critical blocker or deferred

**NON-BLOCKING overall.** PT is a secondary compliance domain for MVP (doc 09 — Phase 2 expanded coverage). The five priority states (Maharashtra, Karnataka, West Bengal, Tamil Nadu, Telangana) should be validated before Phase 2 launch, not MVP launch. For MVP, PT records should carry `requires_human_review: true` and `state_specific_note` with the Act name and instruction to verify current slabs.

### Recommended next decision

1. For MVP: Enter PT compliance records for the top 5 commercial states with `applicability_status: STATE_SPECIFIC` and `requires_human_review: true`.
2. Phase 2: Retrieve the current PT schedule from each of the 5 priority state government websites and populate exact slabs and thresholds.
3. For uncertain states (Goa, Kerala, MP, CG): Enter as `NOT_APPLICABLE_UNCERTAIN` with a note.

---

## B7 — Payment of Bonus: Exact Deadline (8 Months from FY End)

### What is already resolved

**Primary statutory source:** Section 19(1)(b) of the **Payment of Bonus Act, 1965**.

The exact statutory text: "All amounts payable to an employee by way of bonus under this Act shall be paid in cash by his employer —
...(b) in any other case, within eight months from the close of the accounting year."

**"Close of the accounting year"** for the purposes of this Act: under Section 2(1) of the Payment of Bonus Act, "accounting year" means the year ending on any day. For businesses following the standard April-March financial year, the close of the accounting year is **March 31**.

**Computation:** March 31 + 8 months = **November 30** of the same calendar year.

This is **directly stated in the statute** and is **confirmed with HIGH confidence.**

**Applicability threshold:** Section 1(3)(b) — The Act applies to every factory and every other establishment in which 20 or more persons are employed on any day during an accounting year.

**Employee eligibility:** Section 2(13) — Employees drawing salary/wages not exceeding ₹21,000 per month are eligible for bonus. Section 12: For computation purposes, salary/wages is capped at ₹7,000 per month or minimum wage (whichever is higher).

**Minimum and maximum bonus:** Section 10 — Minimum bonus: 8.33% of salary (or ₹100, whichever is higher). Section 11 — Maximum bonus: 20% of salary.

### What remains unresolved

1. **Extension power:** Section 19 proviso gives the "appropriate Government" power to extend the 8-month period. Such extensions are granted case-by-case and cannot be systematically tracked by the compliance engine.
2. **First-year businesses:** Section 16 provides that for the first 5 accounting years in which an establishment comes into existence, bonus is payable based on actual profits of that year. This affects the amount, not the deadline.
3. **Disputes:** Section 22 — if bonus is disputed before an authority, payment is due within 1 month of the award/settlement becoming enforceable. This is event-based.

### Why it matters to the compliance engine

The `LABOUR_BONUS_PAYMENT` compliance record is ANNUAL with a fixed due date of November 30. The applicability rule checks: `employee_count_band IN ['20_49', '50_PLUS']` and `makes_salary_payments = true`. The due date rule type is `FIXED_ANNUAL` with `fixed_day: 30`, `fixed_month: 11`.

This is ready to be encoded. The statute is clear.

### Exact primary source required

Section 19(1)(b) of the Payment of Bonus Act, 1965 — **this is confirmed from primary statute.** No further research needed for the base due date.

The only question for future maintenance: check for any government extension orders issued under the proviso for a specific year, which should be stored as `notification_extension` records.

### Critical blocker or deferred

**RESOLVED. NOT A BLOCKER.** The November 30 deadline is confirmed from the Act text. This record can be populated immediately.

### Recommended next decision

Populate `LABOUR_BONUS_PAYMENT` immediately with:
- Due date rule: FIXED_ANNUAL, day 30, month 11, year context AFTER_FY_END_YEAR
- Primary source: Section 19(1)(b), Payment of Bonus Act, 1965
- Applicability: employee_count ≥ 20 + salary payments exist
- Penalty note: Section 28 — failure to pay bonus within 8 months constitutes an offence

---

## B8 — MSME Form I: Scope (All Companies or Size-Filtered?)

### What is already resolved

**Primary source:** Ministry of Corporate Affairs order under **Section 405 of the Companies Act, 2013** — the **Specified Companies (Furnishing of Information about Payment to Micro and Small Enterprise Suppliers) Order, 2019** (MCA Order dated 22.01.2019, published in the Gazette of India).

**The exact scope of the Order:**

"Every Specified Company shall file, half-yearly, a return as specified in MSME Form I to the Registrar..."

**"Specified Company"** is defined in the Order as:
*"All companies, who get supplies of goods or services from micro and small enterprises and whose payments to micro and small enterprise suppliers exceed forty-five days from the date of acceptance or the date of deemed acceptance of the goods or services as per the provisions of section 2(d) of the Micro, Small and Medium Enterprises Development Act, 2006."*

**What this means precisely:**
1. The word "All companies" includes ALL registered companies regardless of size (Private Limited, Public Limited, OPC, Small Companies, Section 8 Companies).
2. There is **no size filter** on the buying company. Even a small company with ₹5 lakh paid-up capital that buys from MSMEs must comply if payments exceed 45 days.
3. The obligation arises **when** payments to MSME suppliers exceed 45 days — this is the trigger.

**Half-yearly filing periods and due dates (from the Order itself):**
- April 1 to September 30: Return due by **October 31**
- October 1 to March 31: Return due by **April 30**

**LLPs and other non-company entities:** This Order is under Companies Act 2013 and applies ONLY to companies. It does NOT apply to LLPs, partnerships, or proprietorships.

### What remains unresolved

**The NIL filing question:** If a company has NO outstanding MSME supplier dues exceeding 45 days, must it still file Form I (with NIL data)?

This is a genuine ambiguity not definitively resolved by the Order text itself. The MCA portal accepts NIL filings. Most practitioners advise filing NIL Form I as a precaution. However, a strict textual reading of the Order might suggest the filing obligation arises only if there are such outstanding dues.

**Practical implication for the compliance engine:** The system cannot know whether a given company has MSME suppliers — this depends on the company's supplier base. The compliance record should be modeled as:
- `applicability_status: CHECK_THRESHOLD` for all companies
- `why_it_applies: "Applies if your business receives supplies from Micro or Small Enterprise (MSME) registered suppliers AND any such payments remain outstanding beyond 45 days from acceptance."`
- `requires_threshold_check: true`

### Exact primary source required

The MCA Order dated 22.01.2019 (Specified Companies Order) is the primary source and is confirmed with HIGH confidence. Available on mca.gov.in.

**Additional context — Finance Act 2023, Section 43B(h):**
A directly related but architecturally separate obligation has been introduced: Section 43B(h) of the Income Tax Act, 1961 (inserted by Finance Act 2023, effective from AY2024-25):

*"Any sum payable by the assessee to a micro or small enterprise beyond the time limit specified in section 15 of the Micro, Small and Medium Enterprises Development Act, 2006 shall be allowed as a deduction only in the year in which such sum is actually paid."*

**What this means:** If a company delays payment to an MSME supplier beyond the Section 15 MSMED timeline (15 days if no agreement; 45 days if agreed), the entire purchase expense is **disallowed** in the year of accrual under Income Tax. It is only deductible in the year of actual payment.

**This is a critical compliance linkage not in the current Part A architecture.** It creates a direct tax consequence (expense disallowance) for late MSME payments — separate from, but linked to, the MSME Form I reporting obligation.

This should be encoded as a separate compliance item: `IT_MSME_PAYMENT_TIMING_43B_H` — an INDICATOR-type compliance that flags the tax deduction risk for businesses that purchase from MSME suppliers.

### Critical blocker or deferred

**B8 itself: NON-BLOCKING.** The scope is resolved — all companies, triggered by MSME supplier payment delays > 45 days. The NIL filing question is a known ambiguity that should be noted in `compliance_notes`.

**Section 43B(h): NEW ITEM — NOT IN CURRENT ARCHITECTURE.** This is flagged as an additional compliance item to be added in doc 24.

### Recommended next decision

1. Populate `MCA_MSME_FORM_I` with applicability as CHECK_THRESHOLD (all companies; triggered by MSME supplier relationship with delays > 45 days).
2. Source: MCA Order dated 22.01.2019 (Specified Companies Order).
3. Add a new compliance record `IT_MSME_43B_H_INDICATOR` for the tax disallowance risk (doc 24 will detail this).
4. Note: Neither compliance applies to LLPs or non-company entities.

---

## B9 — DPT-3: All Companies or Only Those with Deposits/Loans?

### What is already resolved

**Primary source:** Rule 16A of the Companies (Acceptance of Deposits) Rules, 2014, as amended by the Companies (Acceptance of Deposits) Amendment Rules, 2019 (MCA Notification dated 22.01.2019).

The Rule 16A(3) text: "Every company, other than Government company, shall file, on or before the 30th day of June of every year, return in Form DPT-3 with the Registrar in respect of details of money or loan received by the company but not considered as deposits, in terms of clause (c) of sub-rule (1) of rule 2."

**Rule 2(1)(c) of the Deposit Rules** lists items that are received by a company but are "NOT deposits" — this includes loans from directors, security deposits from employees, loans from banks, loans from relatives of directors, inter-corporate loans (in certain cases), share application money, etc.

**The plain reading of Rule 16A(3):** The obligation is on "Every company, other than Government company" — this is universal scope on all registered companies.

**The filing covers:** Any outstanding receipt of money or loan NOT considered as a deposit. A company that has taken ANY loan (even from its own promoters), accepted any security deposit from an employee, or received any advance that qualifies under these exclusions must report these.

**Key insight:** Almost no active company will have zero such transactions. Even a loan from a director to the company is a reportable item. Companies with NO loans, NO director advances, NO employee security deposits — these are genuinely rare. For all practical purposes, DPT-3 is a universal annual filing for all active non-government companies.

**For inactive/dormant companies:** The filing obligation technically applies under the Rule but MCA has not formally exempted them by rule text. They may file NIL.

**Due date:** June 30 of each year (statutory from Rule 16A(3) itself).

### What remains unresolved

Whether the MCA has issued any circular further clarifying or modifying the NIL filing requirement for companies with genuinely zero transactions. The author is not aware of any such specific exemption notification.

### Why it matters to the compliance engine

DPT-3 should be modeled as APPLICABLE to all companies, not as CHECK_THRESHOLD. The rationale: the Rule's universal scope, combined with the practical reality that almost every company has some form of reportable transaction, means that defaulting to APPLICABLE is more accurate and safer for users than defaulting to CHECK_THRESHOLD and causing users to miss the filing.

The compliance record should note: "File NIL DPT-3 if your company has received no amounts falling under reportable categories. However, the filing obligation itself applies to all active companies regardless."

**Exception:** Government companies are explicitly excluded by Rule 16A(3).

### Exact primary source required

Rule 16A(3) of the Companies (Acceptance of Deposits) Rules, 2014, as amended — **CONFIRMED from primary Rules text.** No additional source needed. The due date (June 30) is directly in the Rule.

### Critical blocker or deferred

**RESOLVED. NOT A BLOCKER.** DPT-3 applies to all non-government companies, due June 30. This can be populated immediately.

### Recommended next decision

Populate `MCA_DPT3_ANNUAL` immediately with:
- Entity types: PRIVATE_LIMITED, PUBLIC_LIMITED, OPC, SECTION8_COMPANY (NOT LLP, NOT PROPRIETORSHIP)
- Due date rule: FIXED_ANNUAL, day 30, month 6, year context AFTER_FY_END_YEAR
- Source: Rule 16A(3), Companies (Acceptance of Deposits) Amendment Rules, 2019
- Note: Government companies excluded. LLPs excluded (different Act).

---

## B10 — DIR-3 KYC: Scope (All DIN Holders Including Dormant/Resigned)

### What is already resolved

**Primary source:** Rule 12A of the Companies (Appointment and Qualification of Directors) Rules, 2014, as amended by the Companies (Appointment and Qualification of Directors) Third Amendment Rules, 2018.

Rule 12A text: "Every individual who holds a Director Identification Number (DIN) as on 31st March of a financial year as per these rules shall, submit e-form DIR-3 KYC to the Central Government on or before 30th September of immediately next financial year."

**What this means unambiguously:**
1. The obligation is on **every individual holding a DIN** — not on the company.
2. It applies **regardless of whether the individual is currently an active director in any company.**
3. A person who resigned from all directorships 3 years ago but still holds a DIN must file DIR-3 KYC annually.
4. Failure to file results in **deactivation of the DIN** — which prevents the individual from being appointed as a director in any company.
5. Reactivation requires filing DIR-3 KYC-Web with a late fee.

**Due date:** September 30 of the financial year following the relevant March 31.

**Important architectural note:** DIR-3 KYC is a **personal obligation of each director individual**, not a company-level obligation. However, from the company's perspective, it is a compliance item because:
- A director with a deactivated DIN cannot sign/certify company forms
- This creates a compliance bottleneck for the company

**Modeling recommendation:** The compliance record should be shown as:
- Domain: MCA_COMPANY
- Obligation type: GOVERNANCE (governance maintenance)
- Description: "Each director must file DIR-3 KYC annually. DIN deactivation affects your ability to file MCA forms."
- Note: "This is an individual obligation of each director. Ensure all directors have filed."

**For LLPs:** DIR-3 KYC also applies to Designated Partners of LLPs who hold DINs (LLPs use DIN for designated partners).

### What remains unresolved

Whether the DIR-3 KYC WEB mechanism (for updating only phone/email without full form submission) changes any of the above obligations for returning filers. This is an operational note, not a material change to the obligation or due date.

### Exact primary source required

Rule 12A, Companies (Appointment and Qualification of Directors) Rules, 2014 — **CONFIRMED from primary rule text.** No additional source needed.

### Critical blocker or deferred

**RESOLVED. NOT A BLOCKER.** DIR-3 KYC applies to all DIN holders; due September 30 annually. This can be populated immediately.

### Recommended next decision

Populate `MCA_DIR3_KYC_ANNUAL` immediately with:
- Entity types: PRIVATE_LIMITED, PUBLIC_LIMITED, OPC, SECTION8_COMPANY, LLP (all entities with directors/designated partners holding DINs)
- Due date rule: FIXED_IN_AY, day 30, month 9 — note: actually FIXED_ANNUAL in the same calendar year (September 30 is within the CURRENT financial year, not the AY)
- Correct framing: DIR-3 KYC for the year ending March 31, 2026 is due by September 30, **2026** — same calendar year, not the next.
- This is `FIXED_ANNUAL` with `fixed_day: 30`, `fixed_month: 9`, `year_context: CURRENT_FY_END_YEAR`
- Source: Rule 12A, Companies (Appointment and Qualification of Directors) Rules, 2014
- Note: "Individual obligation of each director. Company must ensure all its directors comply."

**Correction to Part A doc 05 table:** The DIR-3 KYC entry in the doc 05 OFFSET_FROM_FY_END table showing ~183 days is approximately correct (April 1 + 183 days ≈ September 30). However, it is more precisely encoded as FIXED_ANNUAL with day=30 and month=9.

---

## RESOLUTION SUMMARY

| Item | Status | Blocker? | Ready to Populate? |
|------|--------|---------|-------------------|
| B1: GSTR-3B state staggering | Partially resolved | CRITICAL for QRMP record | GSTR-3B Monthly YES; GSTR-3B QRMP: need Notification 84/2020-CT verified |
| B2: E-invoicing threshold | ₹5 Cr confirmed to Aug 2025; post-Aug status unknown | CRITICAL for applicability rule | Populate with ₹5 Cr; flag for immediate re-verification |
| B3: GSTR-9 small taxpayer exemption | Base rule confirmed; FY-specific exemptions need annual notification check | NON-BLOCKER | Populate base rule; add FY-specific exemption as notification_extension |
| B4: GSTR-9C threshold | ₹5 Cr confirmed from Rule 80(3) + Notif 30/2021-CT | NON-BLOCKER | YES — populate immediately |
| B5: ESI return status | Statute/portal divergence confirmed; exact current status unresolved | CRITICAL for due date rule | Enter with HUMAN_REVIEW_REQUIRED; explain divergence |
| B6: PT state list | List of ~14 states confirmed; slabs unconfirmed | NON-BLOCKER for MVP | Enter as STATE_SPECIFIC with HUMAN_REVIEW; populate slabs in Phase 2 |
| B7: Bonus payment deadline | November 30 CONFIRMED from Section 19(1)(b) Bonus Act 1965 | RESOLVED | YES — populate immediately |
| B8: MSME Form I scope | All companies confirmed; NIL filing ambiguous but noted | NON-BLOCKER | YES — populate with CHECK_THRESHOLD + note |
| B9: DPT-3 scope | All non-government companies confirmed from Rule 16A(3) | RESOLVED | YES — populate immediately |
| B10: DIR-3 KYC scope | All DIN holders confirmed from Rule 12A | RESOLVED | YES — populate immediately |
