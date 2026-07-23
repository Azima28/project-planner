# Domain Probe Library

This is a list of trigger questions and probing amplifiers. Do not use this as a static provider facts, pricing, design, or technology recommendation list. Research up-to-date sources every time an answer affects a decision.

When a domain probe activates a capability (third column below), also read `references/capability-catalog.md` for the corresponding feature expansion triggers and policy requirements.

| Domain signal | Probe | Potentially active capability |
|---|---|---|
| Commerce/booking | Can items/seats run out or be booked simultaneously? | `limited_inventory`, `money_movement` |
| Health/education/public service | What data is sensitive or regulated? Who is the authority? | `sensitive_data`, `regulated` |
| Finance/payment | Who holds the money and handles disputes/refunds? | `money_movement`, `regulated` |
| Logistics/location | How accurate is the location and what is the fallback if stale? | `real_time`, `offline_sync`, `sensitive_data` |
| Community/content | Who moderates abuse and handles appeals? | `identity_access`, `custom` |
| AI/data | Where does the data/model come from, how is it evaluated, who corrects? | `data_ai`, `sensitive_data` |
| Internal ops/event | Who runs the procedure when it fails or in the field? | `operations`, `physical_safety` |
| Legacy migration | What must not be lost, how to rollback, and when is cutover? | `migration` |

## Domain-Specific Probing Amplifiers

When a domain signal is detected from the user's initial description, use these amplifiers to generate deeper, domain-relevant questions during Phase 3 (Role Deep Dive) of the interview process. **These are probing directions, not feature lists.** Generate specific questions from context.

### Education / Exam / LMS
- **Lifecycle**: Academic year → semester → exam period → grading → report card → next year. Where does this app fit in that cycle?
- **Content**: How are questions created? Bank shared across teachers? Versioned across years? Difficulty tagging? Topic categorization?
- **Assessment types**: Only multiple choice? Essay? Oral? Project-based? Mixed? Each type has different grading, timing, and review needs.
  - **PG (Multiple choice/pilihan ganda)**: Single correct answer, auto-graded.
  - **Multi-select**: One or more correct answers — partial credit policy? (all-or-nothing vs proportional per correct option).
  - **Essay**: Manual grading needed. Rubric support? Word/character limits?
  - **Scoring logic configurable**: Per-soal vs per-ujian, passing grade, weight per question.
- **Exam vs Practice mode (Ujian vs Latihan)**:
  - Exam: strict timer, no pause, anti-cheat active, score visibility configurable (admin decides show/hide), one attempt only.
  - Practice: relaxed rules, can retry, immediate score + explanation, anti-cheat optional/off.
  - How do these modes relate? Separate or combined in the same screen?
- **Grading**: Auto-grade vs manual. Rubric system? Grade curves? Weighted sections? Minimum passing score?
- **Analytics**: Per-student trends? Per-topic weakness? Class comparison? School-wide statistics? Parent-visible reports? Export (Excel/PDF)?
- **Integrity / Anti-cheat**:
  - Detection methods: Page Visibility API (tab switch), window blur event, copy/paste/right-click disable, screenshot heuristics, concurrent login prevention.
  - Penalty system (configurable per exam): **Off** (warning only), **Fixed** (same duration per violation), **Progressive** (escalating duration per violation tier), **Max violations cap** (X strikes → auto anulir).
  - Timer behaviour: always runs during penalty (no pause).
  - Violation logging: timestamp, type, detail, auto/anulir flag. Visible to admin in real-time monitor.
  - Override: admin can manually anulir or clear violation record.
- **Role hierarchy pattern** (common for exam platforms):
  - **Student**: responsive web/mobile, can take exams, view results (if permitted).
  - **Teacher**: web desktop, manages question bank, sets up exam drafts, grades essays, views analytics.
  - **Admin**: web desktop, deploys exams (publishes teacher drafts), real-time monitoring, master data (CRUD + import Excel), reports, manual anulir.
  - **Super Admin**: inherits admin + manages other admins, system configuration (branding, defaults), audit log, hard delete, impersonate view (read-only).
  - **Content workflow**: Teacher creates draft → Admin deploys → Student takes exam → Teacher grades (essay) → Results published.
- **Visibility control**: Score visibility per exam (show/hide from students). Result history visibility per exam. Configurable per exam by teacher/admin.
- **Communication**: Schedule announcements? Grade notifications? Parent portal? Teacher-student messaging?
- **Administration**: Class/section management? Teacher assignment? Academic calendar? Bulk operations? Import Excel for master data (students, teachers, classes, subjects).

### Commerce / Marketplace / Booking
- **Lifecycle**: Browse → select → pay → fulfill → review → return. Which parts does this app handle?
- **Catalog**: How many products/services? Categories? Search/filter? Recommendations?
- **Inventory**: Limited stock? Reservations? Multiple locations? Real-time availability?
- **Payment**: Who holds money? Escrow? Split payment? Subscription? Refund flow?
- **Fulfillment**: Digital delivery? Physical shipping? Booking/appointment? Self-service?
- **Loyalty**: Points? Tiers? Referral? Coupons/discounts?
- **Communication**: Order updates? Promotional notifications? Chat between buyer/seller?
- **Administration**: Seller dashboard? Revenue reports? Dispute resolution? Commission tracking?

### Healthcare / Clinic / Wellness
- **Lifecycle**: Appointment → check-in → consultation → prescription → follow-up.
- **Data**: Patient history? Medication interactions? Lab results? Insurance claims?
- **Analytics**: Visit frequency? Treatment outcomes? Revenue per service?
- **Compliance**: HIPAA/local equivalents? Consent management? Audit trails?

### Logistics / Delivery / Fleet
- **Lifecycle**: Order → assign → pick up → transit → deliver → confirm.
- **Fleet**: Vehicle management? Route optimization? Warehouse zones?
- **Analytics**: Delivery time? Driver performance? Cost per delivery?

### Internal Ops / Enterprise Tools
- **Lifecycle**: Request → approve → execute → verify → close.
- **Tracking**: Asset tracking? Procedure templates? Shift/schedule?
- **Analytics**: SLA compliance? Bottleneck analysis? Cost tracking?

### Unknown / Niche Domain
When no domain signal matches, rely entirely on the universal 7-dimension framework from `references/interview-decision-tree.md`. Generate domain questions by reasoning about the entities, roles, and workflows described by the user, rather than looking up a table.
