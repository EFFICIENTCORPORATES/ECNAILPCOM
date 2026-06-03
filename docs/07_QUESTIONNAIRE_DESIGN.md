# Document 07 — Business Questionnaire Design
## Structured Question Domains and Field-to-Applicability Mapping

---

## 1. QUESTIONNAIRE DESIGN PRINCIPLES

### 1.1 Progressive Disclosure
Questions are shown only when relevant. An LLP is never asked about board meetings. A sole proprietor is never asked about share capital. The questionnaire is adaptive.

### 1.2 Mandatory Minimum vs. Optional Detail
A short set of mandatory questions produces a basic compliance checklist.
Optional follow-up questions improve applicability confidence.

### 1.3 Questions Must Produce Flags, Not Just Store Answers
Every question must map to one or more `BusinessProfile` fields that drive applicability rules.
A question with no downstream effect on any compliance rule should not be asked.

### 1.4 Ordering Strategy
Order questions to prune the largest number of irrelevant compliances early:
1. Entity type (eliminates ~60% of non-applicable items immediately)
2. GST status (eliminates or confirms entire GST domain)
3. Employee count (eliminates EPF/ESI domain if zero)
4. Activity type (eliminates factory/manufacturing if service-only)
5. States of operation (triggers state-specific domains)

---

## 2. QUESTIONNAIRE DOMAINS

---

### DOMAIN A: BUSINESS IDENTITY (Mandatory)

**A1. What type of legal entity is your business?**
- Sole Proprietorship
- Partnership Firm
- Limited Liability Partnership (LLP)
- Private Limited Company
- One Person Company (OPC)
- Public Limited Company
- Other (with text field)

→ Populates: `entity_type`
→ Immediately determines: which MCA/LLP/secretarial compliances apply; governance requirements; audit requirements

**A2. When did your business start operations / get incorporated?**
- Date picker (incorporation date for formal entities, commencement date for proprietorships)

→ Populates: `incorporation_date`, `commencement_date`
→ Determines: which FY the first filings apply to; first AGM window (for companies)

**A3. What is your principal state of business?**
- Dropdown with Indian states/UTs

→ Populates: `principal_state`
→ Determines: state-specific compliances (PT, S&E, Factory), GST state code, state-wise GSTR-3B due date group

**A4. How many states does your business operate in?**
- 1 state / 2–5 states / More than 5 states

→ Populates: `number_of_states`
→ Triggers: multi-state GST flag, state-specific compliance breadth

*If > 1 state:*
**A4a. List all states where you have an office, warehouse, employees, or regular business activity**
- Multi-select state checkboxes

→ Populates: `state_codes_present`

**A5. What type of business activity best describes your operations?**
- Primarily a service business (consulting, software, professional services, etc.)
- Primarily a trading/distribution business (buying and selling goods)
- Primarily a manufacturing business (making, processing, or fabricating goods)
- Mixed (combination of the above)

→ Populates: `activity_type`
→ Determines: manufacturing-specific compliances (Factory Act, environment), GST applicability profile, books/audit requirements

**A6. What sector/industry is your primary business in?**
- Retail / FMCG
- Technology / IT / Software
- Professional Services (CA, Legal, Consulting)
- Healthcare / Pharma
- Food / Restaurant / Hospitality
- Manufacturing / Industrial
- Construction / Real Estate
- E-commerce / Online marketplace
- Import / Export / Trading
- Education
- Other (text field)

→ Populates: `sector`
→ Triggers: sector-specific flags (FSSAI for food, environment for manufacturing, IEC for export/import)

**A7. Is your business in a regulated sector?** (e.g., banking, insurance, telecom, pharmaceuticals, SEBI-registered entity, NBFC)
- Yes / No

→ Populates: `is_regulated_sector`
→ If yes: flag for human review — sector-specific regulator compliance may apply outside this system's scope

---

### DOMAIN B: TAX PROFILE (Mandatory)

**B1. Does your business have a PAN?**
- Yes / No / Applied for

→ Populates: `pan_obtained`

**B2. Is your business registered for GST?**
- Yes, I have a GSTIN
- No, but I think I should register
- No, my turnover is below the registration threshold
- Not sure

→ Populates: `gst_registered`, `gst_scheme` (pending next question)

*If B2 = Yes:*

**B2a. What is your GSTIN?**
- Text input (validated format)
→ Populates: `gstin`

**B2b. What GST scheme are you under?**
- Regular taxpayer
- Composition scheme

→ Populates: `gst_scheme`

**B2c. Are you a monthly or quarterly filer for GSTR-1 and GSTR-3B?**
- Monthly (turnover above ₹5 crore OR I chose monthly)
- Quarterly under QRMP scheme (turnover ≤ ₹5 crore and enrolled in QRMP)
- Not sure

→ Populates: `gst_filing_frequency`
→ Determines: GSTR-1 and GSTR-3B due dates and cycles

**B3. What is your annual turnover (or estimated annual turnover for this financial year)?**
- Below ₹20 lakh
- ₹20 lakh – ₹40 lakh
- ₹40 lakh – ₹1 crore
- ₹1 crore – ₹5 crore
- ₹5 crore – ₹10 crore
- Above ₹10 crore
- Not sure yet / first year

→ Populates: `turnover_band`, `annual_turnover_estimated`
→ Determines: GST registration threshold, tax audit threshold, e-invoicing applicability, GST QRMP eligibility, composition eligibility, small company status

**B4. Does your business make supply of goods or services outside your home state?**
- Yes, regularly
- Occasionally
- No

→ Populates: `has_interstate_supply`
→ Determines: GST registration mandatory regardless of turnover; IGST applicability

**B5. Does your business export goods or services?**
- Yes
- No

→ Populates: `has_exports`
→ Triggers: IEC requirement check, LUT/bond under GST, FEMA/DGFT obligations flag

**B6. Does your business import goods or services?**
- Yes
- No

→ Populates: `has_imports`
→ Triggers: IEC, Customs, FEMA obligations flag

**B7. Does your business sell through or operate an e-commerce platform?** (e.g., Amazon, Flipkart, own website)
- Yes, I sell through a third-party marketplace (Amazon, Flipkart, etc.)
- Yes, I have my own e-commerce website
- No

→ Populates: `has_ecommerce`
→ Triggers: mandatory GST registration regardless of turnover (for marketplace sellers), TCS under GST for operators

---

### DOMAIN C: TDS PROFILE (Conditional: if has employees or makes significant B2B payments)

**C1. Does your business pay salaries to employees?**
- Yes / No

→ Populates: `makes_salary_payments`
→ Determines: TDS under Section 192 applicability; TAN requirement; Form 16 issuance

*If C1 = Yes:*
**C1a. Do you have a TAN (Tax Deduction Account Number)?**
- Yes / No / Applied for

→ Populates: `tan_obtained`

**C2. Does your business pay contractors, sub-contractors, or freelancers for services?**
- Yes, regularly (e.g., IT contractors, agency workers, consultants)
- Occasionally
- No

→ Populates: `makes_contractor_payments`
→ Determines: TDS Section 194C applicability

**C3. Does your business pay rent for office/warehouse/factory space exceeding ₹50,000/month (or ₹2.4 lakh/year)?**
- Yes / No

→ Populates: `makes_rent_payments`
→ Determines: TDS Section 194I applicability

**C4. Does your business pay professional fees to lawyers, CAs, consultants, or technical service providers exceeding ₹30,000 per payment?**
- Yes / No

→ Populates: `makes_professional_fee_payments`
→ Determines: TDS Section 194J applicability

---

### DOMAIN D: EMPLOYMENT PROFILE (Mandatory if has employees)

**D1. How many people work in your business (full-time employees on your payroll)?**
- 0 (no employees, I am the only person)
- 1–9
- 10–19
- 20–49
- 50–199
- 200 or more

→ Populates: `employee_count_band`, `employee_count`
→ Determines: EPF threshold (20+), ESI threshold (10+), Bonus Act threshold (20+), Gratuity Act threshold (10+), Contract Labour threshold, Maternity benefit applicability

*If D1 > 0:*

**D2. Are your employees formally on a payroll with salary slips?**
- Yes, I run formal payroll
- No, they are paid in cash without formal payroll
- Some are formal, some are informal

→ Populates: Payroll formalization flag
→ Note: Informs whether labour law advice needs to emphasize setup vs. ongoing compliance

**D3. Are you registered with EPFO (Provident Fund)?**
- Yes, I have a PF establishment code
- No, but I think I need to register
- No, I am below the threshold
- Not sure

→ Populates: `pf_registered`
→ Determines: EPF monthly compliance items

**D4. Are you registered with ESIC (Employee State Insurance)?**
- Yes, I have an ESIC establishment code
- No, but I think I need to register
- No, I am below the threshold / Not in an ESI-covered area
- Not sure

→ Populates: `esi_registered`

**D5. Do any of your employees earn a gross monthly salary below ₹21,000?**
- Yes (most employees are below ₹21,000)
- Mixed (some above, some below)
- No (all are above ₹21,000)

→ Refines ESI applicability — ESI applies only to employees with gross salary ≤ ₹21,000

**D6. Do you hire contract workers through a contractor for any work?**
- Yes
- No

→ Populates: `contract_worker_count` flag
→ Triggers: Contract Labour Act (CLRA) check if ≥ 20 contract workers

**D7. Do you have any female employees?**
- Yes / No

→ Populates: `has_female_employees`
→ Triggers: Maternity Benefit Act flag if ≥ 10 employees with female employees present

---

### DOMAIN E: OWNERSHIP / GOVERNANCE (Entity-type conditional)

*Shown only for LLP, Private Limited, Public Limited, OPC, Partnership*

**E1. How many directors / partners / designated partners does your business have?**
- 1 (OPC only)
- 2–5
- 6–10
- More than 10

→ Populates: `num_directors_or_partners`

**E2. Is any director, partner, or owner a foreign national or NRI?**
- Yes / No

→ Populates: `has_foreign_director_partner`
→ Triggers: FEMA compliance flag; additional MCA disclosures possible

**E3. Does any foreign entity or person own shares or contribution in your business?**
- Yes / No

→ Populates: `has_foreign_ownership`
→ Triggers: FEMA/FDI compliance flag — human review required

*For companies only:*

**E4. Has your company appointed a statutory auditor?**
- Yes / No / In process

→ Populates: `has_appointed_auditor`
→ Determines: ADT-1 filing status; audit-related annual compliance

**E5. What is your company's paid-up share capital?**
- Below ₹1 lakh
- ₹1 lakh – ₹10 lakh
- ₹10 lakh – ₹1 crore
- ₹1 crore – ₹10 crore
- Above ₹10 crore

→ Populates: `paid_up_capital`
→ Determines: Small company status (≤ ₹2 Cr paid-up + ₹20 Cr turnover), XBRL applicability, MGT-7 vs MGT-7A

**E6. Have there been any changes in directors, partners, or registered office in the last 3 months?**
- Yes, change in directors/designated partners
- Yes, change in registered office address
- Yes, change in company/LLP name
- Yes, change in shareholding/capital
- No changes

→ Populates: event-based change flags
→ Triggers: relevant event-based filings with computed due dates from event date

---

### DOMAIN F: PREMISES / OPERATIONS

**F1. What type of premises does your business operate from?**
(Multi-select)
- Registered office / administrative office
- Retail shop / commercial establishment
- Warehouse / godown
- Factory / production facility
- None (purely digital/home-based)

→ Populates: `premise_type`
→ Determines: Shops & Establishments applicability, Factory Act applicability

**F2. Do you own or rent your business premises?**
- Own
- Rent
- Both
- No fixed premises

→ Determines: TDS on rent applicability (if renting > ₹2.4L p.a.)

**F3. [If manufacturing activity selected] Does your manufacturing process use electric power or other machinery?**
- Yes
- No (purely manual)

→ Populates: `uses_power_in_mfg`
→ Determines: Factories Act threshold (10 workers with power, 20 without)

**F4. [If manufacturing activity selected] Do you use or store any hazardous chemicals, materials, or waste?**
- Yes
- No

→ Populates: `has_hazardous_material`
→ Triggers: Environment/pollution compliance flag (human review required)

**F5. Is your business in the food or beverage industry?**
(Includes: restaurant, food processing, packaged food, catering)
- Yes
- No

→ Populates: `has_food_business`
→ Triggers: FSSAI registration/license requirement

---

### DOMAIN G: FINANCIAL REPORTING / AUDIT STATUS

**G1. Does your business maintain formal books of account?**
- Yes, fully maintained with accounting software / CA
- Yes, partially maintained
- No

→ Populates: `books_maintained`
→ Triggers: Books of account compliance check; if not maintained, high-severity flag

**G2. Has your business had its accounts professionally audited for any previous financial year?**
- Yes / No / First year

→ Populates: `audited_accounts_done`

**G3. [If company/LLP] What is the financial year for which you last filed annual returns with MCA?**
- FY2024-25 (filed)
- FY2023-24 or earlier (recent but may need check)
- Never filed / Just incorporated

→ Populates: Last MCA filing status
→ Determines: Overdue MCA filings; risk of strike-off for long-missed filings

---

### DOMAIN H: REGISTRATION STATUS (Conditional)

**H1. Do you have a Shops and Establishments registration for your business premises?**
- Yes / No / Not applicable for my type of business

→ Populates: `shops_est_registration`

**H2. [If food business] Do you have an FSSAI registration or license?**
- Yes (Registration / License — specify)
- No, need to obtain
- In process

→ Populates: `fssai_license`

**H3. [If manufacturer with workers] Do you have a Factory License / registration?**
- Yes
- No, need to check if required
- Below threshold / not applicable

→ Populates: `factory_registration`

**H4. [If imports/exports] Do you have an IEC (Import Export Code)?**
- Yes
- No, need to obtain
- Not yet started imports/exports

→ Populates: IEC status flag

**H5. Has your business registered on the Udyam portal as an MSME?**
- Yes
- No
- Not sure if we qualify

→ Populates: MSME registration status
→ Triggers: MSME Form I compliance awareness for buyers from this business

---

## 3. QUESTION → APPLICABILITY RULE MAPPING (KEY CONNECTIONS)

| Question | Answer | Compliance Triggered |
|----------|--------|---------------------|
| Entity = Company | Any | MCA AOC-4, MGT-7, ADT-1, DIR-3 KYC, Board meetings, DPT-3, BEN-2 |
| Entity = LLP | Any | Form 8, Form 11, LLP partner KYC |
| GST registered = Yes | Any | GSTR-1, GSTR-3B, GSTR-9; (annual: GSTR-9C if >₹5Cr) |
| GST scheme = Composition | Any | CMP-08 (quarterly), GSTR-4 (annual) instead of GSTR-1/3B |
| Turnover > ₹1 Cr (business) | Any | Tax audit (IT Act Sec 44AB) |
| Turnover > ₹10 Cr (cash ≤5%) | Any | Revised tax audit threshold |
| Turnover > ₹5 Cr | GST | E-invoicing required; GSTR-9C required |
| Employee count ≥ 20 | Any | EPF registration and monthly ECR |
| Employee count ≥ 10 | Any | ESI registration; Gratuity Act; Maternity Benefit |
| Employee count ≥ 20 | Bonus Act | Bonus payment by Nov 30 |
| Has salary payments | TDS | Sec 192 TDS; TAN required; Form 16 |
| Has contractor payments | TDS | Sec 194C TDS (if above threshold) |
| Interstate supply | GST | Mandatory GST registration regardless of turnover |
| Manufacturing + power + ≥10 workers | Factories | Factory Act registration |
| Food business | FSSAI | FSSAI registration/license |
| Export | IEC/GST/FEMA | IEC required; LUT under GST; FEMA flag |
| Foreign ownership | FEMA | FDI compliance; FEMA annual return; human review |
| E-commerce sales | GST | Mandatory GST registration |

---

## 4. PROFILE COMPLETENESS SCORING

The system should compute a `profile_completeness_pct` (0–100) that represents how many questions have been answered vs. how many are applicable.

At 40% completion: basic entity + GST checklist can be shown
At 70% completion: most domains covered with reasonable confidence
At 90%+ completion: high-confidence applicability decisions across all domains

The system should nudge users to complete their profile with messages like:
"You have 3 unanswered questions. Answering them may reveal 5 additional compliance obligations."
