# C2 — Legal-to-Data Translation Standard
## Method for Converting Validated Legal Provisions into Structured Rule Records

---

## 1. Objective

Define a disciplined, repeatable methodology for transforming a validated legal text — an Act section, Rule provision, Notification, or Circular — into a structured compliance rule record in the master library.

The goal is to ensure that the full meaning, scope, conditions, and consequences of a legal provision are preserved in machine-evaluable form without losing legal nuance, introducing unsupported assumptions, or silently discarding edge cases.

---

## 2. Why It Matters to the Compliance Engine

Legal text is written for legal interpretation. Structured data is written for computational evaluation. The gap between these two worlds is where compliance product failures most often originate. A rule that is structurally present but semantically incomplete — for example, a rule that captures the filing obligation but omits the exemption condition — will produce incorrect outputs at runtime. This methodology closes that gap systematically.

---

## 3. Design Principles

**P1 — Source-first, structure-second.** Never begin structuring a rule until the primary source has been identified, read in full, and its confidence level assessed. Do not reverse-engineer a source from assumed knowledge.

**P2 — Decompose completely before encoding.** Every legal provision must be fully decomposed into its logical components before any field is populated. Partial decomposition leads to partial rules.

**P3 — Explicit over implicit.** Every assumption, inference, or interpretation that is not directly stated in the source text must be labeled as such in the `interpretation_notes` field. Nothing is silently assumed.

**P4 — Preserve ambiguity.** Where the legal text is ambiguous, the structured record must reflect that ambiguity via the appropriate validation state and interpretation notes. Do not resolve ambiguity by choosing the most convenient interpretation.

**P5 — One provision, one rule.** A single legal provision that creates multiple distinct obligations (e.g., a section that requires both filing and payment) should produce two separate compliance rule records, not one combined record.

---

## 4. The Translation Procedure — Ten Steps

### Step 1: Identify the Operative Provision

Before writing a single field, locate the exact provision in the primary source text.

| Task | What to do |
|------|-----------|
| Identify the Act/Rules | Full official name, year, jurisdiction |
| Identify the section/rule/regulation | Exact number and sub-number |
| Obtain the full provision text | Read the complete section, including sub-sections, provisos, exceptions, and explanations |
| Verify currency | Confirm the provision has not been amended. If amended, use the latest in-force version. If uncertain, mark as `PENDING_PRIMARY_CONFIRMATION`. |
| Assess confidence level | HIGH: provision confirmed from official source. MEDIUM: provision likely correct but full text not retrieved. LOW: inferred from secondary sources only. |

**Disqualifying condition:** If the provision cannot be located in an official source and its content is known only from professional commentary or blog summaries, do NOT proceed to Step 2. Record the rule as `validation_state = PENDING_PRIMARY_CONFIRMATION` and stop.

---

### Step 2: Extract the Obligation Language

Identify the precise language that creates the legal obligation.

Legal obligations are typically expressed with words like:
- "Every [person/company/employer/registered person] shall..."
- "No [person/company] shall, unless..."
- "It shall be the duty of..."
- "Within [N days] of..."

**What to capture:**

| Extraction Target | Example |
|-------------------|---------|
| The obligated party | "Every company, other than Government Company" |
| The modal verb (shall/must/may) | "shall file" (mandatory), "may apply" (optional/permissive) |
| The required action | "file a return in Form DPT-3 with the Registrar" |
| The time reference | "on or before the 30th day of June of every year" |
| Conditions or provisos | "Provided that..." / "Subject to..." |

**Record the verbatim operative text** in the `operative_legal_text` field. Do not paraphrase at this stage.

---

### Step 3: Identify the Subject of Obligation

"Who must comply?"

This maps directly to the applicability logic of the rule.

| Subject Question | How to Answer |
|-----------------|--------------|
| Which legal entity types? | Is it "every company"? (excludes LLPs, proprietorships) Or "every person"? (includes all) |
| Which registration status? | "Every registered person" under CGST Act means GST-registered only |
| Which size threshold? | "Every factory employing not less than ten workers" |
| Which activity type? | "Every manufacturer of goods" — excludes pure service providers |
| Which geography? | State Acts apply to residents/establishments in that state only |

**Common errors to avoid:**
- "Every company" under Companies Act does NOT include LLPs (LLP is governed by LLP Act, not Companies Act)
- "Every person" under Income Tax Act includes individuals, HUFs, firms, companies, LLPs, AOPs, BOIs
- "Every employer" under EPF Act means employers of establishments covered by the Act (≥20 employees or voluntarily registered)

---

### Step 4: Identify Triggering Conditions

"Under what additional conditions does this obligation arise?"

Beyond the base subject, many obligations have secondary triggers:

| Trigger Type | Example |
|-------------|---------|
| Threshold crossing | "whose aggregate annual turnover exceeds ₹5 Cr" |
| Registration event | "upon registration under the Act" |
| Transaction occurrence | "in the financial year in which he makes the payment" |
| Election/choice | "assessees who have opted for presumptive taxation under Section 44AD" |
| Date/period start | "in the first year of registration" |
| Relationship | "every principal employer engaging twenty or more contract labourers" |

**Map each trigger to a specific business profile field.** If the trigger cannot be mapped to a known field, add the missing field to the questionnaire design as a gap item.

---

### Step 5: Identify Thresholds, Exemptions, Carve-Outs, and Conditions

Legal provisions frequently have carved-out classes, exemption limits, and conditional modifications.

**Three categories to identify:**

| Category | Meaning | How to Encode |
|----------|---------|--------------|
| Hard threshold | Obligation arises only above/below a specific number | THRESHOLD node in applicability rule |
| Statutory exemption | Specific class permanently excluded | NOT_APPLICABLE_IF node or entity_types filter |
| Conditional relaxation | Obligation modified (not eliminated) under conditions | Separate compliance record OR applicability variant flag |

**Examples:**
- Bonus Act Section 19: "within eight months" — no threshold, applies to all eligible establishments
- CGST Act Section 44 proviso: "Commissioner may exempt" — year-specific exemption, stored as notification_extension
- Companies Act Section 2(85) — small company definition: ₹4 Cr paid-up AND ₹40 Cr turnover — conjunction matters (AND, not OR)

**Provisos must be read carefully.** A proviso ("Provided that...") may expand, restrict, or completely reverse the main provision. Never skip the proviso.

---

### Step 6: Identify the Required Action

"What exactly must be done?"

| Action Category | What to Record |
|----------------|---------------|
| Filing/Return | Which form, to which authority, through which portal |
| Payment | Of what (tax, fee, contribution), to which authority |
| Registration | One-time action, what must be registered |
| Record-keeping | What records, for how long, in what format |
| Governance | Meeting held, resolution passed, minutes maintained |
| Event reporting | What event triggers which form/disclosure |

Map to `obligation_type` enum. If the provision requires both filing AND payment, these are two separate obligation records.

---

### Step 7: Identify the Timing Language

"By when must the action be completed?"

| Timing Pattern | Example | Due-Date Rule Type |
|---------------|---------|-------------------|
| Fixed calendar date | "by 30th June of every year" | FIXED_ANNUAL |
| Offset from period end | "within 20 days of end of the tax period" | OFFSET_FROM_PERIOD_END |
| Offset from FY end | "within 6 months of close of financial year" | OFFSET_FROM_FY_END |
| Offset from event | "within 30 days of appointment" | OFFSET_FROM_EVENT |
| Relative to assessment year | "on or before 31st July of the assessment year" | FIXED_IN_AY |
| Continuous obligation | "at all times", "during the financial year" | CONTINUOUS |
| Not yet determinable | "such date as may be notified" | PERIOD_UNKNOWN |

**Resolve "month" ambiguity:** In Indian statutes, month generally means calendar month unless otherwise specified. "30 days" and "one month" are sometimes used interchangeably but are legally distinct — record as written.

---

### Step 8: Identify Consequence Language

"What happens if the obligation is not met?"

| Consequence Type | Statutory Language Pattern |
|-----------------|--------------------------|
| Monetary penalty (fixed) | "shall be liable to pay a penalty of ₹X" |
| Monetary penalty (variable) | "penalty not less than ₹X and not more than ₹Y" |
| Late fee (per-day) | "a sum of ₹X for every day of default" |
| Interest | "interest at the rate of X percent per annum" |
| Prosecution | "shall be punishable with imprisonment for a term which may extend to X years" |
| Compounding | "may be compounded for a sum not exceeding ₹X" |
| Business restriction | "registration may be cancelled/suspended" |
| Expense disallowance | "shall not be allowed as a deduction" |

**Capture only what the statute states.** Do not infer prosecution risk where the provision only states a fine. Do not infer interest where the provision only states a penalty.

---

### Step 9: Rate Source Confidence and Document Interpretation Choices

After completing the extraction, assess the overall quality:

| Confidence Level | Criteria |
|-----------------|---------|
| HIGH | Provision read in full from official text. Current version confirmed. No significant ambiguity in the operative clause. |
| MEDIUM | Provision likely correct. Full text not retrieved but well-known provision. Some interpretive inference. |
| LOW | Based on secondary source, commentary, or inference from related provisions. Primary source not confirmed. |

**Document every interpretation choice.** If the legal text is reasonably clear but an interpretation was required (e.g., "does 'accounting year' mean April-March or the company's own year?"), record the adopted interpretation and the reasoning in `interpretation_notes`.

---

### Step 10: Populate the Structured Record

With the extraction complete, populate each schema field in order:

1. Identity fields (code, title) — from Step 1
2. Classification fields (domain, category, obligation_type, frequency_type) — from Step 6 and Step 7
3. Legal basis fields (governing_act, primary_provision_reference, operative_legal_text) — from Steps 1 and 2
4. Applicability fields (entity_types, applicability_rule) — from Steps 3 and 4
5. Exemption and threshold fields — from Step 5
6. Timing fields (due_date_rule, due_date_determinability) — from Step 7
7. Consequence fields (penalty_record, consequence_summary) — from Step 8
8. Trust and lifecycle fields (validation_state, source_confidence_level) — from Step 9

---

## 5. Worked Extraction Example

**Source:** Section 19(1)(b) of the Payment of Bonus Act, 1965.
**Text:** "All amounts payable to an employee by way of bonus under this Act shall be paid in cash by his employer within eight months from the close of the accounting year."

| Step | Extraction | Structured Output |
|------|-----------|-----------------|
| 1 | Payment of Bonus Act, 1965, Section 19(1)(b) | `governing_act: "Payment of Bonus Act, 1965"`, `primary_provision_reference: "Section 19(1)(b)"` |
| 2 | "shall be paid in cash by his employer" | Obligation is mandatory. Obligated party: employer. Action: payment. |
| 3 | "his employer" — employer covered by the Act | `entity_types_applicable: ["ALL"]`; applicability conditioned on establishment having ≥20 employees (from Section 1(3)) |
| 4 | Establishment employing ≥20 persons; employee salary ≤ ₹21,000/month | `threshold_fields_involved: ["employee_count"]`; exemption for employees earning > ₹21,000 |
| 5 | No exemption from the deadline itself (proviso only extends it on govt order) | `extension_possible: true`; note the proviso |
| 6 | "paid in cash" — payment action | `obligation_type: TAX_PAYMENT` (actually LABOUR_PAYMENT); action: pay bonus to employees |
| 7 | "within eight months from the close of the accounting year" → March 31 + 8 months = November 30 | `due_date_rule_type: FIXED_ANNUAL`, `fixed_day: 30`, `fixed_month: 11` |
| 8 | Section 28 — "shall be punishable with imprisonment for a term which may extend to six months, or with fine, or with both" | `prosecution_possible: true`, `imprisonment_possible: true`, `imprisonment_max_months: 6` |
| 9 | Provision read from statute text. HIGH confidence. | `validation_state: VALIDATED_PRIMARY`, `source_confidence_level: HIGH` |

---

## 6. Edge Cases

**What if the provision has been amended and both versions are relevant?** Create two rule records. The older version has `active_flag: false`, `effective_to: [amendment date]`. The newer version has `active_flag: true`, `effective_from: [amendment date]`, `predecessor_id: [old record's UUID]`.

**What if the same obligation arises from two independent provisions?** Record the primary provision as the main source and the second as a secondary source in the source link table with `source_role: PARALLEL_AUTHORITY`. Document in `interpretation_notes` that both provisions independently create the same obligation.

**What if the provision says "as may be prescribed" or "as notified"?** This means the detail is delegated to subordinate legislation. Locate the relevant rule or notification that fills the blank. If not yet found, set `due_date_determinability: PERIOD_UNKNOWN` and `validation_state: PENDING_PRIMARY_CONFIRMATION`.

---

## 7. What Should Be Deferred

- Cross-referencing ALL provisions in a single Act is deferred. Extract provisions rule-by-rule as each compliance obligation is identified and prioritized.
- State-specific provisions: Follow the same procedure per state, but state-specific rules enter the library as separate records with `jurisdiction: SPECIFIC_STATES`.
- Provisions not yet validated: Do not translate until the primary source text is retrieved. Record as `PENDING_PRIMARY_CONFIRMATION` instead.
