# Document 02 — Compliance Domains
## Legal/Regulatory Coverage Analysis

This document defines every compliance domain the system must cover, identifies the precise
legal sources, and notes the specific modeling requirements for each domain.

---

## DOMAIN 1 — GST (Goods and Services Tax)

### 1.1 Primary Legal Sources

| Source | Reference |
|--------|-----------|
| Central Act | Central Goods and Services Tax Act, 2017 (CGST Act) |
| Central Act | Integrated Goods and Services Tax Act, 2017 (IGST Act) |
| Central Act | Union Territory Goods and Services Tax Act, 2017 (UTGST Act) |
| Rules | CGST Rules, 2017 (as amended) |
| Rules | IGST Rules, 2017 |
| Notifications | CBIC Notifications (Central Tax, Integrated Tax, Rate, etc.) |
| Circulars | CBIC Trade Circulars |
| Portal | gst.gov.in (official GST portal) |
| Act Sections | Sec 22 (registration), Sec 37 (GSTR-1), Sec 38 (GSTR-2A/2B auto), Sec 39 (GSTR-3B), Sec 44 (GSTR-9), Sec 47 (late fee), Sec 50 (interest) |

### 1.2 Compliance Items to Model

#### Registration
| Item | Trigger | Source |
|------|---------|--------|
| GST Registration | Aggregate turnover > ₹20L services / ₹40L goods (Sec 22 CGST Act); ₹10L for special category states | CGST Act Sec 22, 23, 24 + Notifications |
| Mandatory registration irrespective of turnover | Interstate supply, e-commerce operator, casual taxable person, non-resident, reverse charge mechanism supplier | CGST Act Sec 24 |
| Composition scheme enrollment | Turnover ≤ ₹1.5 Cr (₹75L for special category states); not available for service-only businesses exceeding ₹50L | CGST Act Sec 10 + Notification |
| Registration amendment | Change in legal name, address, constitution, etc. | CGST Act Sec 28 |

#### Returns — Regular Scheme

| Return | Frequency | Due Date Rule | Legal Source |
|--------|-----------|---------------|--------------|
| GSTR-1 | Monthly (turnover > ₹5 Cr) | 11th of following month | CGST Act Sec 37 + Rule 59 |
| GSTR-1 | Quarterly (QRMP, turnover ≤ ₹5 Cr) | 13th of month after quarter-end | CBIC Notification 82/2020-CT |
| IFF (Invoice Furnishing Facility) | Monthly M1/M2 under QRMP | 13th of following month (optional) | CBIC Notification 82/2020-CT |
| GSTR-3B | Monthly (turnover > ₹5 Cr OR non-QRMP) | State-staggered: 20th/22nd/24th of following month | CGST Act Sec 39 + Rule 61 + Notifications |
| GSTR-3B | Quarterly (QRMP) | 22nd/24th of month after quarter-end | CBIC Notification 84/2020-CT |
| GSTR-9 | Annual | 31st December following FY end | CGST Act Sec 44 + Rule 80 |
| GSTR-9C | Annual reconciliation (for turnover > ₹5 Cr) | 31st December following FY end | CGST Act Sec 44 + Rule 80 |

**CRITICAL NOTE on GSTR-3B State Staggering:**
CBIC has issued notifications staggering GSTR-3B due dates by state groups.
- Group A (large states/UTs including Maharashtra, Karnataka, Tamil Nadu, Gujarat, etc.): 20th
- Group B (remaining states): 22nd
- Group C (NE states and small UTs): 24th

The exact grouping is defined in the latest CBIC Notification under Central Tax.
**This must be verified against the current active notification before populating the database.**

#### Returns — Composition Scheme

| Return | Frequency | Due Date Rule | Legal Source |
|--------|-----------|---------------|--------------|
| CMP-08 (Challan-cum-Statement) | Quarterly | 18th of month after quarter-end | CGST Act Sec 10 + Rule 62 |
| GSTR-4 | Annual | 30th April following FY end | CGST Act Sec 44 + Rule 62 |

#### Payment
| Item | Due Date Rule |
|------|--------------|
| GST monthly payment | Same as GSTR-3B due date |
| GST quarterly payment (QRMP) | Via PMT-06: 25th of each month in first two months of quarter, balance with quarterly 3B |

#### Other GST-Related Obligations
| Item | Trigger |
|------|---------|
| E-invoicing (IRP) | Aggregate turnover > ₹5 Cr (currently). Threshold has been reduced multiple times — verify latest. |
| E-way bill | Movement of goods > ₹50,000 value. Interstate and intrastate (state-specific for intrastate). |
| LUT / Bond (for zero-rated exports) | Exporters supplying under zero-rating without payment of tax |

#### Penalty/Late Fee Structure (GST)
| Non-compliance | Consequence | Source |
|----------------|-------------|--------|
| Late GSTR-1 | ₹50/day (₹25 CGST + ₹25 SGST), maximum ₹10,000 | CGST Act Sec 47 |
| Late GSTR-1 (nil return) | ₹20/day (₹10+₹10), max ₹10,000 | CGST Act Sec 47 + Notification |
| Late GSTR-3B | ₹50/day (₹25+₹25), max ₹10,000; ₹20/day for nil returns | CGST Act Sec 47 |
| Late GSTR-9 | ₹200/day (₹100+₹100), max = 0.25% of turnover in state | CGST Act Sec 47 |
| Interest on delayed payment | 18% p.a. | CGST Act Sec 50 |
| Interest on excess ITC | 24% p.a. | CGST Act Sec 50(3) |

**NOTE:** CBIC has issued notifications waiving/reducing late fees during Covid periods and for specific filing campaigns. The system must store these as time-bounded overrides, not as base rules.

---

## DOMAIN 2 — INCOME TAX

### 2.1 Primary Legal Sources

| Source | Reference |
|--------|-----------|
| Central Act | Income Tax Act, 1961 |
| Rules | Income Tax Rules, 1962 |
| Circulars | CBDT Circulars |
| Notifications | CBDT Notifications |
| Portal | incometax.gov.in |

### 2.2 Return Filing

| Entity Type | Form | Due Date | Source |
|-------------|------|----------|--------|
| Individual / HUF (non-business / no audit) | ITR-1, 2, 3 | 31st July of AY | IT Act Sec 139(1) |
| Individual / HUF (business, no audit) | ITR-3 | 31st July of AY | IT Act Sec 139(1) |
| Company | ITR-6 | 31st October of AY | IT Act Sec 139(1) |
| Audit cases (individuals/firms/LLPs) | ITR-3/5 | 31st October of AY | IT Act Sec 139(1) |
| Cases with TP/international transactions | All | 30th November of AY | IT Act Sec 92E + 139(1) |
| LLP | ITR-5 | 31st July (no audit) or 31st October (audit) | IT Act Sec 139(1) |
| Proprietorship | ITR-3 | 31st July (no audit) or 31st October (audit) | IT Act Sec 139(1) |

**CRITICAL ENTITY-TYPE NOTE for Proprietorship:**
A proprietorship is not a separate legal entity for income tax. The proprietor files their personal ITR with business income included. This is a critical compliance architecture point — the ITR obligation belongs to the individual (proprietor), not the "business."

### 2.3 Tax Audit

| Criterion | Threshold | Form | Source |
|-----------|-----------|------|--------|
| Business turnover | > ₹1 Cr (general) | 3CA + 3CD | IT Act Sec 44AB |
| Business turnover (cash transactions ≤ 5%) | > ₹10 Cr | 3CA + 3CD | IT Act Sec 44AB proviso |
| Profession gross receipts | > ₹50L | 3CB + 3CD | IT Act Sec 44AB(b) |
| Presumptive taxation opt-out after opting in | Sec 44AD/44ADA income declared lower than prescribed | 3CB + 3CD | IT Act Sec 44AB |

**Due Date:** Tax Audit Report must be filed 1 month before ITR due date.
For audit cases: October 31 is ITR date → September 30 is audit report date.

### 2.4 Advance Tax

| Installment | Due Date | Cumulative % of Tax Liability | Source |
|------------|----------|-------------------------------|--------|
| Q1 | June 15 of FY | 15% | IT Act Sec 211 |
| Q2 | September 15 of FY | 45% | IT Act Sec 211 |
| Q3 | December 15 of FY | 75% | IT Act Sec 211 |
| Q4 | March 15 of FY | 100% | IT Act Sec 211 |

**Exemptions:**
- Resident senior citizens (age ≥ 60) with no business income are exempt (Sec 207)
- Presumptive taxation assessees: full tax by March 15 only (special rule Sec 44AD)
- Estimated tax liability < ₹10,000: exempt from advance tax

### 2.5 TDS (Tax Deducted at Source)

**Applicability:**
TDS obligations arise when a payer makes specified payments above threshold amounts. Applicability depends on:
- Whether the business has a TAN
- Nature of payments made (salary, rent, professional fees, contractor payments, etc.)
- Payment thresholds per section

**Key TDS Sections Relevant to Businesses:**

| Section | Payment Type | Basic Rate | Threshold |
|---------|-------------|-----------|-----------|
| 192 | Salary | Slab rate | Above basic exemption limit |
| 194C | Contractor / sub-contractor | 1% (individual) / 2% (company) | ₹30K per payment / ₹1L aggregate |
| 194I | Rent (land/building) | 10% | ₹2.4L p.a. |
| 194I(a) | Rent (plant/machinery) | 2% | ₹2.4L p.a. |
| 194J | Professional/technical services | 10% (2% for some technical) | ₹30K |
| 194A | Interest (non-bank) | 10% | ₹5,000 |
| 194H | Commission / brokerage | 5% | ₹15K |
| 194B | Lottery/winnings | 30% | ₹10K |
| 194Q | Purchase of goods | 0.1% | Buyer turnover > ₹10 Cr + purchase > ₹50L |

*Note: This is not exhaustive. Rates and thresholds may change via Finance Act amendments.*

**TDS Deposit Due Dates:**

| Month of Deduction | Due Date for Deposit |
|-------------------|---------------------|
| April to February | 7th of the following month |
| March | 30th April |

*Government deductors have different rules (same day or 7th).*

**TDS Return Filing Due Dates:**

| Quarter | Period | Due Date |
|---------|--------|----------|
| Q1 | April – June | 31st July |
| Q2 | July – September | 31st October |
| Q3 | October – December | 31st January |
| Q4 | January – March | 31st May |

**TDS Certificate Issuance:**

| Certificate | For | Due Date |
|------------|-----|----------|
| Form 16 | Salary (Sec 192) | 15th June of AY |
| Form 16A | Non-salary | 15 days from TDS return due date |

*Form 16A Q4 certificate: Due by approximately 15th June (15 days after May 31 TDS return).*

**Penalty Structure (TDS):**

| Non-compliance | Consequence | Source |
|----------------|-------------|--------|
| Failure to deduct TDS | 30% of TDS amount disallowed as expense + 1% interest per month from date of deductibility to deduction | IT Act Sec 40(a)(ia) + Sec 201 |
| Failure to deposit TDS after deduction | 1.5% per month from date of deduction to deposit date | IT Act Sec 201(1A) |
| Late TDS return | ₹200/day (Sec 234E) up to TDS amount, plus penalty under Sec 271H (₹10K–₹1L) | IT Act Sec 234E + 271H |
| Late/incorrect TDS certificate | Penalty ₹100/day up to ₹10,000 per certificate | IT Act Sec 272A(2) |

---

## DOMAIN 3 — MCA / COMPANIES ACT / LLP ACT

### 3.1 Primary Legal Sources

| Source | Reference |
|--------|-----------|
| Central Act | Companies Act, 2013 |
| Rules | Various Companies Rules (Filing, Meetings, Accounts, etc.) |
| Central Act | Limited Liability Partnership Act, 2008 |
| Rules | LLP Rules, 2009 |
| Portal | mca.gov.in (MCA21 system) |
| Circulars | MCA General Circulars |

### 3.2 Company Annual Compliance

**AGM (Annual General Meeting):**
- Must be held within 6 months of FY end: by September 30 for March-ending companies
- Except first AGM: within 9 months of first financial year end
- Source: Companies Act, 2013, Sec 96

**Annual Return (MGT-7 / MGT-7A):**
- Form MGT-7: Companies other than OPC and small companies
- Form MGT-7A: OPC and small companies
- Due date: Within 60 days of AGM
- For companies with AGM on Sep 30: Due by November 29
- Source: Companies Act, 2013, Sec 92 + Rule 11 of Companies (Management & Administration) Rules

**Financial Statements (AOC-4):**
- AOC-4: Within 30 days of AGM
- AOC-4 XBRL: For certain class of companies (per Companies (Filing of Documents in XBRL) Rules)
- For AGM on Sep 30: Due by October 30
- Source: Companies Act, 2013, Sec 137 + Rule 12 of Companies (Accounts) Rules

**Auditor Appointment (ADT-1):**
- Within 15 days of AGM (annual reappointment)
- For first auditor: Within 30 days of incorporation
- Source: Companies Act, 2013, Sec 139 + ADT Rules

**Other Recurring Annual Filings:**

| Form | Purpose | Frequency | Due Date | Source |
|------|---------|-----------|----------|--------|
| DIR-3 KYC | Director KYC | Annual | September 30 | Companies (Appointment and Qualification of Directors) Rules, Rule 12A |
| DPT-3 | Return of deposits/money received | Annual | June 30 | Companies (Acceptance of Deposits) Rules |
| MSME Form I | Outstanding payments to MSMEs > 45 days | Half-yearly | Oct 31 (Apr-Sep period) / Apr 30 (Oct-Mar period) | Sec 405 Companies Act + MSME Form I Notification 2019 |
| BEN-2 | Beneficial ownership declaration | On event + annual | Within 30 days of declaration by BOs | Companies (Significant Beneficial Owners) Rules |

**Board Meeting Requirements:**
- Minimum 4 board meetings per year
- Maximum gap between two meetings: 120 days
- Source: Companies Act, 2013, Sec 173

**Note:** Board meeting compliance is a governance record obligation, not a filing. The system should flag it as a governance indicator, not compute a filing due date. Minutes must be maintained within 30 days of meeting.

### 3.3 LLP Annual Compliance

| Form | Purpose | Due Date | Source |
|------|---------|----------|--------|
| Form 8 | Statement of Accounts and Solvency | October 30 (within 30 days of end of 6 months from FY close) | LLP Act Sec 34 + LLP Rules |
| Form 11 | Annual Return | May 30 | LLP Act Sec 35 + LLP Rules Rule 25 |

**LLP Audit Requirement:**
- Mandatory if: turnover > ₹40 lakhs in a year, OR contribution > ₹25 lakhs
- Source: LLP Rules, 2009, Rule 24

**LLP Partner Changes (Event-Based):**

| Event | Form | Due Date | Source |
|-------|------|----------|--------|
| Addition of partner | Form 4 | Within 30 days | LLP Rules Rule 22 |
| Cessation of partner | Form 4 | Within 30 days | LLP Rules Rule 22 |
| Change in DP details | Form 6 | Within 30 days | LLP Rules |
| Change in LLP name | Form 5 | On approval | LLP Rules |
| Change in registered office | Form 15 | Within 30 days | LLP Rules Rule 17 |

### 3.4 Event-Based Company Filings

| Event | Form | Due Date | Source |
|-------|------|----------|--------|
| Director appointment | DIR-12 | Within 30 days of appointment | Sec 168 + Rule 15 |
| Director resignation | DIR-11 (by director) + DIR-12 | Within 30 days | Sec 168 + Rule 15 |
| Change in registered office (same city) | INC-22 | Within 30 days | Sec 12 |
| Change in registered office (other city) | INC-23 (NCLT) + INC-22 | Variable | Sec 12 |
| Allotment of shares | PAS-3 | Within 30 days | Sec 39 |
| Increase in authorized capital | SH-7 | Within 30 days | Sec 61 |
| Charge creation | CHG-1 | Within 30 days (60 with condonation) | Sec 77 |
| Charge satisfaction | CHG-4 | Within 30 days | Sec 82 |
| Change in company name | INC-24 | On approval | Sec 13 |

---

## DOMAIN 4 — INCOME TAX (BOOKS / AUDIT / RECORDS)

### 4.1 Books of Account Maintenance

| Entity | Requirement | Source |
|--------|-------------|--------|
| Persons with business/profession | Mandatory if income > ₹1.2L or turnover > ₹10L | IT Act Sec 44AA + Rule 6F |
| Companies | Always mandatory | Companies Act Sec 128 + IT Act |
| LLPs | Mandatory (LLP Act + IT Act) | LLP Act Sec 34 + IT Act |

**Retention Period:** 6 years from end of relevant AY (general rule; FEMA cases different)
Source: IT Act Sec 44AA

---

## DOMAIN 5 — EPF / PF (Employees' Provident Fund)

### 5.1 Primary Legal Sources

| Source | Reference |
|--------|-----------|
| Central Act | Employees' Provident Funds and Miscellaneous Provisions Act, 1952 |
| Scheme | Employees' Provident Fund Scheme, 1952 |
| Scheme | Employees' Pension Scheme, 1995 (EPS) |
| Scheme | Employees' Deposit Linked Insurance Scheme, 1976 (EDLI) |
| Portal | unifiedportal-mem.epfindia.gov.in / epfindia.gov.in |

### 5.2 Applicability

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| Headcount | ≥ 20 employees | Once registered, continues even if headcount drops |
| Voluntary registration | Any size | Possible before threshold |
| Salary ceiling | ₹15,000/month basic + DA for mandatory contribution | Employees earning above can opt out |

### 5.3 Compliance Items

| Item | Due Date | Notes |
|------|----------|-------|
| PF contribution deposit (ECR) | 15th of following month | Employee share 12% + Employer 12% (split into EPS+EPF+EDLI) |
| ECR filing (Electronic Challan-cum-Return) | 15th of following month | Combined deposit + return |

**Contribution Rates:**
- Employee: 12% of basic + DA
- Employer: 12% split as — EPS 8.33% (capped on ₹15,000 = ₹1,250), EDLI 0.5%, EPF balance

### 5.4 Penalty/Interest

| Non-compliance | Consequence | Source |
|----------------|-------------|--------|
| Default in deposit | 12% p.a. simple interest + damages (penal interest) at rate declared by Govt | EPF Act Sec 7Q + Para 32A |
| Non-maintenance of records | Prosecution possible | EPF Act |

---

## DOMAIN 6 — ESI (Employees' State Insurance)

### 6.1 Primary Legal Sources

| Source | Reference |
|--------|-----------|
| Central Act | Employees' State Insurance Act, 1948 |
| Regulations | ESI (Central) Rules, 1950 |
| Portal | esic.gov.in |

### 6.2 Applicability

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| Headcount | ≥ 10 employees (in most states) | Factories: ≥ 10 employees |
| Salary ceiling | ₹21,000/month gross | Employees above this are exempt |
| Geographic | ESI Act operational areas only | Covered under Gazette notification areas |

**NOTE:** ESI is not uniformly applicable across India. Certain areas/districts may not be notified yet. The system must store geographic coverage status as a compliance flag.

### 6.3 Compliance Items

| Item | Due Date | Notes |
|------|----------|-------|
| ESI contribution deposit | 15th of following month | Employee 0.75% + Employer 3.25% of gross wages |
| ESI half-yearly return | Nov 11 (Apr-Sep) / May 11 (Oct-Mar) | Form 5-IE (pending verification of current portal requirements) |

---

## DOMAIN 7 — PROFESSIONAL TAX (PT)

### 7.1 Applicability

Professional Tax is a state-level tax. Not all states levy PT. The following states/UTs levy PT as of current knowledge:

**States with PT:** Maharashtra, Karnataka, West Bengal, Gujarat, Tamil Nadu, Andhra Pradesh, Telangana, Madhya Pradesh (limited), Tripura, Assam, Meghalaya, Orissa, Bihar, Jharkhand, Chhattisgarh

**States without PT:** Rajasthan (discontinued), Delhi (no PT), Uttar Pradesh, Haryana, Punjab, Himachal Pradesh, Jammu & Kashmir, Uttarakhand, Goa, and others

**CRITICAL MODELING NOTE:**
PT is a state subject. Each state has its own Act, slab rates, registration requirements, payment cycles, and forms. The system must model PT as `STATE_SPECIFIC` for all states and maintain separate sub-rules per state. This is not a single compliance item — it is a family of state-level items.

### 7.2 Illustrative PT Rules (Maharashtra)

| Item | Rule |
|------|------|
| Applicability Act | Maharashtra State Tax on Professions, Trades, Callings and Employments Act, 1975 |
| Employer enrollment | Mandatory before paying salary to employees |
| Employee registration | For employees earning above slab |
| Payment | Monthly (if annual tax > ₹50,000) or annual |
| Return | Annual |

---

## DOMAIN 8 — LABOUR LAWS (General Obligations)

### 8.1 Minimum Wages Act, 1948

- Applicable to all establishments notified under the Schedule
- Rates: State-specific minimum wage rates notified by State Government
- Record-keeping: Form I (wages), Form II (overtime), Form X (annual returns)
- Annual return: State-specific (generally by January/February)

### 8.2 Payment of Bonus Act, 1965

| Criterion | Rule |
|-----------|------|
| Applicability | Establishments employing ≥ 20 persons (employees with salary ≤ ₹21,000/month eligible) |
| Minimum Bonus | 8.33% of annual salary (or ₹100 minimum) |
| Maximum Bonus | 20% of annual salary |
| Payment Deadline | Within 8 months of financial year end (i.e., by November 30 for March FY) |
| Return | Form D — within 30 days of payment |

### 8.3 Payment of Gratuity Act, 1972

| Criterion | Rule |
|-----------|------|
| Applicability | Establishments employing ≥ 10 persons |
| Trigger | On resignation/retirement after 5 years of continuous service |
| Amount | 15 days' salary per year of service |
| Not a recurring filing | One-time event-based payment |
| Notice | Form F (employee nomination) required |

### 8.4 Maternity Benefit Act, 1961

- Applicable to establishments with ≥ 10 employees
- 26 weeks paid leave for first two children (12 weeks for third+)
- Compliance: Register maintenance, no dismissal during maternity, crèche obligations if ≥ 50 employees

### 8.5 Contract Labour (Regulation & Abolition) Act, 1970

| Criterion | Rule |
|-----------|------|
| Principal Employer applicability | ≥ 20 contract workers on any day in preceding 12 months |
| Contractor applicability | ≥ 20 workers |
| Registration | Form I (principal employer) / Form IV (contractor) |

**Note:** This is a threshold-and-contract-type trigger. The system should flag this if the business indicates use of contract workers.

---

## DOMAIN 9 — SHOPS AND ESTABLISHMENTS

### 9.1 Nature of Domain

Shops and Establishments registration is a **state-level** obligation. Every state has its own Act. There is no central S&E Act.

**Examples:**
- Maharashtra: Maharashtra Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2017
- Karnataka: Karnataka Shops and Commercial Establishments Act, 1961
- Delhi: Delhi Shops and Establishments Act, 1954
- Tamil Nadu: Tamil Nadu Shops and Establishments Act, 1947

### 9.2 Modeling Approach

Given that each state has its own Act and procedures, the system must:
- Store S&E as a `STATE_SPECIFIC` compliance domain
- Maintain state-specific sub-items for at least the top 10 business states
- For other states: flag as "check your state S&E Act"
- Capture: registration timeline, renewal cycle, penalty for non-registration

**Key Common Elements Across States:**
- Registration required before/shortly after commencement of business
- Certificate to be displayed at premises
- Annual renewal (in many states)
- Maintained registers: attendance, wages, leave, etc.

---

## DOMAIN 10 — MSME / UDYAM REGISTRATION

### 10.1 Source

- Micro, Small and Medium Enterprises Development Act, 2006
- MSME Development (Amendment) Act, 2020
- Udyam Registration Portal (udyamregistration.gov.in)

### 10.2 Nature

Udyam registration is not mandatory for most businesses — it is **voluntary** but unlocks significant benefits:
- Collateral-free loans
- Priority sector lending
- Credit guarantee schemes
- Subsidy on patents
- Reduced electricity tariffs in some states
- MSME Form I filing obligations apply to companies/LLPs purchasing from MSMEs

**Threshold (as of 2020 amendment):**
| Category | Investment in Plant/Machinery | Turnover |
|----------|------------------------------|---------|
| Micro | ≤ ₹1 Cr | ≤ ₹5 Cr |
| Small | ≤ ₹10 Cr | ≤ ₹50 Cr |
| Medium | ≤ ₹50 Cr | ≤ ₹250 Cr |

---

## DOMAIN 11 — IMPORT/EXPORT (FEMA/DGFT/Customs)

### 11.1 Key Obligations

| Item | Trigger | Source |
|------|---------|--------|
| IEC (Import Export Code) | Required for any import/export | DGFT website / FTP |
| FEMA Compliance | Foreign currency transactions | FEMA, 1999 |
| Customs Declarations | On import/export shipments | Customs Act, 1962 |
| LUT/Bond under GST | For zero-rated exports | CGST Act Sec 16 |
| FIRC/Bank Realisation | For export proceeds | FEMA regulations |

**Note:** Deep FEMA compliance modeling is deferred to Phase 2.

---

## DOMAIN 12 — FSSAI (Food Safety)

### 12.1 Source

- Food Safety and Standards Act, 2006
- Food Safety and Standards (Licensing and Registration) Regulations, 2011

### 12.2 Applicability

Mandatory for any business involved in manufacture, processing, storage, distribution, sale, or import of food products.

| Category | Criterion | License Type |
|----------|-----------|-------------|
| Petty food business | Turnover < ₹12L | Registration (Form A) |
| Small manufacturer | Turnover ₹12L–₹20 Cr | State License (Form B) |
| Large manufacturer | Turnover > ₹20 Cr | Central License (Form B) |

---

## DOMAIN 13 — FACTORIES ACT

### 13.1 Source

- Factories Act, 1948
- State Factory Rules (each state has its own rules)

### 13.2 Applicability Screening

| Criterion | Threshold |
|-----------|-----------|
| With power (electricity) | ≥ 10 workers |
| Without power | ≥ 20 workers |
| Seasonal factory | Special provisions |

**If triggered:** Factory registration required (Form 2 to Chief Inspector of Factories)

**Associated compliance:** Safety regulations, welfare provisions, working hours rules, registers, returns to factory inspectorate (state-specific)

**Modeling Note:** Factory Act compliance is highly state-specific (different rules, forms, fees per state). It should be modeled as `STATE_SPECIFIC + CHECK_THRESHOLD` for manufacturing businesses.

---

## DOMAIN 14 — ENVIRONMENT / POLLUTION

### 14.1 Triggers

For manufacturing, chemical processing, hazardous waste businesses:
- Environment Protection Act, 1986
- Water (Prevention and Control of Pollution) Act, 1974
- Air (Prevention and Control of Pollution) Act, 1981
- Hazardous and Other Wastes (Management and Transboundary Movement) Rules, 2016

**Modeling:** Flag as `CHECK_THRESHOLD + STATE_SPECIFIC + HUMAN_REVIEW_REQUIRED` for manufacturing businesses. Do not attempt to model specific compliances here in Phase 1.

---

## DOMAIN 15 — ACCOUNTING / RECORDS / AUDIT SUMMARY

| Obligation | Who | Source |
|-----------|-----|--------|
| Books of account | All businesses above threshold | IT Act Sec 44AA; Companies Act Sec 128; LLP Act Sec 34 |
| Invoice retention | GST registrants | CGST Rules Rule 56 (5 years) |
| Payroll records | Employers | Various labour laws |
| Statutory audit | Companies (all); LLPs above threshold | Companies Act Sec 139; LLP Rules |
| Tax audit | Turnover > ₹1 Cr (business) / ₹50L (profession) | IT Act Sec 44AB |
| GST audit by CA | Optional (GSTR-9C) for turnover > ₹5 Cr | CGST Act Sec 44 + Circular 152/08/2021 |
