---
name: uml-use-case-diagram-core
description: "Generates UML 2.5.1 use case diagrams showing system scope, actor interactions, and functional requirements coverage. Use when capturing functional requirements from stakeholders, defining system boundaries, showing feature-actor matrix, or creating requirements traceability to use cases. Keywords: use case diagram, functional requirements diagram, actor system interaction, system boundary diagram, include extend UML, use case hierarchy, stakeholder requirements, feature traceability"
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/uml-use-case-diagram-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# UML Use Case Diagram Core

## Description

Produces UML 2.5.1 use case diagrams (Chapter 18 of the OMG specification) covering actor identification, system boundary definition, include/extend relationships, goal-level classification, and requirements traceability. Applies formal bipartite graph theory, Cockburn completeness criteria, MOSCOW priority scoring, and full coverage metrics. Addresses NIC-SSDLC, STQC CMMI, and MeitY SDLC mandates applicable to Indian government and enterprise software projects.

---

## 1. UML 2.5.1 Use Case Metamodel

The authoritative metaclasses from OMG UML 2.5.1 Chapter 18:

**UseCase:** BehavioredClassifier. Attributes: subject: Classifier[*] (the systems the use case applies to); include: Include[*]; extend: Extend[*]; extensionPoints: ExtensionPoint[*].

**Actor:** BehavioredClassifier (external agent). Associated to UseCase via bidirectional Association. Actors are outside the system boundary — they are never inside the subject rectangle.

**Include:** DirectedRelationship. addition: UseCase (the use case that is added). Arrow direction: base use case → included use case. Semantic: the included use case ALWAYS executes as a mandatory part of the base. Notation: dashed arrow labeled `«include»`.

**Extend:** DirectedRelationship. extension: UseCase (the extending use case). extendedCase: UseCase (base use case). condition: Constraint (guard). extensionLocation: ExtensionPoint[1..*]. Arrow direction: extending use case → base use case. Semantic: the extending use case CONDITIONALLY inserts behavior at named extension points. Notation: dashed arrow labeled `«extend»` with condition note.

**ExtensionPoint:** NamedElement owned by UseCase. Marks a named location in the base use case where extension inserts.

OCL well-formedness constraint from spec:
```
context Extend inv: self.extension.subject->intersection(self.extendedCase.subject)->notEmpty()
```
Both the extending and extended use case must share at least one common subject (system boundary).

**Actor Generalization:** Actors form a generalization hierarchy. A specialized actor inherits all use case associations of the general actor. Example: `PrivilegedUser --|> User` means PrivilegedUser can trigger all use cases User can, plus additional ones.

---

## 2. System Boundary and Subject Classifier

The system boundary rectangle (named by the subject classifier) partitions the universe:

- All UseCase instances appear INSIDE the rectangle.
- All Actor instances appear OUTSIDE the rectangle.
- Associations cross the boundary connecting actors to use cases.
- Component, Subsystem, or System may serve as the subject classifier.

A single use case diagram may have multiple subject rectangles when modeling a multi-system interaction (e.g., a buyer system and a seller system on the same diagram).

**Notation rule:** Actor = stick figure with name below. Use case = oval with name inside. System boundary = rectangle with subject name in top-left or top-center.

---

## 3. Include Relationship Construction

Include models mandatory, reusable sub-behavior extracted from multiple use cases.

Pattern: if two or more use cases share a common sequence of steps, extract that sequence into a new use case UC_shared and add `UC_base «include»→ UC_shared`.

Design criteria for when to use Include:
1. The included behavior has no meaning on its own (it is not independently initiated by an actor).
2. The base use case cannot complete successfully without executing the included use case.
3. The same included use case is referenced by at least two base use cases (DRY principle).

Example include chain:
```
Place Order «include»→ Authenticate User
Track Order «include»→ Authenticate User
Cancel Order «include»→ Authenticate User «include»→ Log Audit Event
```
Transitivity: if `A «include»→ B` and `B «include»→ C`, then all traces of A contain the traces of B, which contain the traces of C. C is an indirect mandatory part of A.

---

## 4. Extend Relationship Construction

Extend models optional, conditional extensions that augment a base use case without modifying it.

The base use case is complete and meaningful without the extension. The extending use case is a separate behavioral chunk that inserts at named extension points only when a guard condition holds.

Construction steps:
1. Identify the base use case UC_base.
2. Add an ExtensionPoint ep_name to UC_base at the appropriate step.
3. Create a new UseCase UC_ext representing the conditional behavior.
4. Draw `UC_ext «extend»→ UC_base` with condition note `{condition: [guard_predicate]}`.

Example:
```
Base: Process Insurance Claim
ExtensionPoint: after_approval
Extension: Apply No-Claims Bonus
Extend arrow: Apply No-Claims Bonus «extend»→ Process Insurance Claim
Condition: {policyholder has 3+ claim-free years}
```

Include vs Extend decision rule:
| Criterion | Include | Extend |
|-----------|---------|--------|
| Base UC complete without it? | No | Yes |
| Executes always? | Yes | Conditionally |
| Arrow direction | base → included | extending → base |
| Changes base? | No (adds steps) | No (inserts at EP) |

---

## 5. Goal Hierarchy and Use Case Leveling

Cockburn's goal levels classify use cases by abstraction:

**Kite level (cloud/summary):** Corporate or regulatory goals. Too abstract to be a use case. Example: "Maximize shareholder value."

**Sea level (wave):** User goals — the primary use case level. One successful interaction delivering value to an actor. Example: "Place an order." These are the main use cases on the diagram.

**Fish level (underwater):** Sub-functions or steps. Too detailed for a primary use case; typically modeled as included use cases or activity steps. Example: "Validate credit card number."

**Seagull level (above kite):** Enterprise or societal goals. Even more abstract than kite.

Rule: A well-formed use case diagram contains ONLY sea-level use cases as the primary ovals, with kite-level context provided by subject name and fish-level details delegated to include relationships or activity diagrams.

---

## 6. Feature-to-Actor Traceability Matrix

A requirements traceability matrix (RTM) maps:
- Rows: Functional Requirements (FR-001, FR-002, ...)
- Columns: Use Cases (UC-001, UC-002, ...)
- Cells: `X` if use case implements the functional requirement

Generation algorithm:
1. For each UseCase UC, identify which FRs it satisfies.
2. For each Include(UC_base, UC_included), propagate FR coverage: FRs of UC_included are also partially addressed by UC_base.
3. Check FR_coverage = |{fr | exists uc: traces_to(uc, fr)}| / |FR| = 1.0 (all FRs must be covered).

Actor-Feature matrix:
- Rows: Actors
- Columns: Use Cases
- Cell: `P` (primary initiator), `S` (secondary participant), blank (no association)

---

## 7. Deep Mathematical Foundations

### M1: Actor-Use Case Bipartite Graph

**Definition.** The use case model defines a bipartite graph B = (A, U, I) where:
- A = set of actors (external agents, nodes outside system boundary)
- U = set of use cases (system functions, nodes inside system boundary)
- I subset of A × U = association edges (actor can initiate or participate in use case)
- A and U are disjoint: A ∩ U = ∅ (bipartite property)

**Primary actor:** a in A is a primary actor for uc in U if the association (a, uc) in I AND a initiates uc (placed on the left of the system boundary by convention).

**Secondary actor:** a in A is secondary for uc in U if (a, uc) in I AND uc is initiated by another actor (a provides services to or receives notifications from the system during uc; placed on the right).

**Graph properties:**
- Bipartite: no edge connects two actors or two use cases
- Not necessarily connected: isolated use cases (no actor) violate completeness
- Not necessarily simple: multiple associations between same actor and use case are valid (different roles)
- Degree constraint: deg_U(uc) >= 1 for all uc in U (every use case has at least one associated actor)

**Worked example — Online Shopping System:**

Actors: A = {Customer, PaymentGateway, InventorySystem, Admin}
Use Cases: U = {BrowseCatalog, PlaceOrder, TrackShipment, ProcessRefund, ManageProducts}

Associations I:
- (Customer, BrowseCatalog), (Customer, PlaceOrder), (Customer, TrackShipment), (Customer, ProcessRefund)
- (PaymentGateway, PlaceOrder), (PaymentGateway, ProcessRefund)
- (InventorySystem, PlaceOrder), (InventorySystem, ManageProducts)
- (Admin, ManageProducts)

Bipartite check: No A-A or U-U edges. Degree check: all use cases have deg >= 1. Isolated use case check: none.

Adjacency matrix (rows=Actors, cols=UseCases):
```
                 Browse  Place  Track  Refund  Manage
Customer           1       1      1      1       0
PaymentGateway     0       1      0      1       0
InventorySystem    0       1      0      0       1
Admin              0       0      0      0       1
```

### M2: Include/Extend Dependency Chain

**Include formal semantics.** Let traces(uc) denote the set of valid execution traces of use case uc.

Include(uc_base, uc_included): traces(uc_base) ⊇ traces(uc_included)

This means every trace of uc_base contains all steps of uc_included as a mandatory sub-sequence.

**Extend formal semantics.** Let ep be an extension point in uc_base, and g be a guard predicate.

Extend(uc_ext, uc_base, ep, g): traces(uc_base with ep active and g=true) = traces(uc_base) augmented-with traces(uc_ext) inserted at ep.

When g = false, uc_ext does not execute and traces(uc_base) is unchanged.

**Chain transitivity for Include:**

Lemma: If Include(A, B) and Include(B, C), then C is an indirect mandatory part of A.

Proof: traces(A) ⊇ traces(B) (by Include(A, B)) and traces(B) ⊇ traces(C) (by Include(B, C)). By transitivity of set inclusion: traces(A) ⊇ traces(C). Therefore C is a mandatory sub-sequence of A.

**Worked example — 4 use case dependency chain:**

UC1: Complete Purchase
UC2: Process Payment       (Include from UC1)
UC3: Validate Card         (Include from UC2)
UC4: Log Transaction       (Include from UC2)
UC5: Apply Loyalty Points  (Extend UC1 at ep_checkout, condition: customer has loyalty account)

Chain: traces(UC1) ⊇ traces(UC2) ⊇ traces(UC3)
       traces(UC1) ⊇ traces(UC2) ⊇ traces(UC4)

Execution of UC1 always runs UC2, which always runs both UC3 and UC4. UC5 only inserts at ep_checkout when the loyalty condition holds.

### M3: Cockburn Completeness Criterion

**Goal level classification function:**
```
goal_level: UseCase → {kite, sea, fish}
```

**Sea-level completeness metric:**

Let UC_sea = {uc in U | goal_level(uc) = sea} (sea-level use cases).
Let UC_tested = {uc in UC_sea | has_at_least_one_test_scenario(uc)} (use cases with at least one concrete test scenario).

Sea-level completeness:
```
Completeness = |UC_tested| / |UC_sea|
```

**Threshold:** Completeness >= 0.90 for production systems. All sea-level use cases without test scenarios represent unverified requirements.

**Worked example — E-Commerce System Goal Hierarchy:**

| Use Case | Goal Level | Has Test? | Verdict |
|----------|-----------|-----------|---------|
| Maximize GMV | Kite | N/A | Excluded |
| Place Order | Sea | Yes | Counted |
| Browse Catalog | Sea | Yes | Counted |
| Track Shipment | Sea | No | Gap |
| Process Refund | Sea | Yes | Counted |
| Validate Credit Card | Fish | N/A | Excluded (use Include) |

UC_sea = {Place Order, Browse Catalog, Track Shipment, Process Refund} → |UC_sea| = 4
UC_tested = {Place Order, Browse Catalog, Process Refund} → |UC_tested| = 3
Completeness = 3/4 = 0.75 < 0.90 — incomplete. Action: add test scenario for Track Shipment.

### M4: System Boundary Partition

**Formal partition.** Let O be the universe of all model elements.

The subject system S partitions O into two disjoint sets:
- O_in = {x in O | x is a system responsibility} (inside boundary)
- O_ext = {x in O | x is outside the system} (outside boundary)

Constraints:
- All actors: ∀ a in A → a in O_ext
- All use cases: ∀ uc in U → uc in O_in
- O_in ∩ O_ext = ∅ (partition property)
- O_in ∪ O_ext = O (covers all elements)

**Boundary rigidity principle:** Use cases on the boundary represent system capabilities (what the system does). Actors on the boundary represent external stakeholders (who initiates or benefits). No use case may be attributed to an actor — use cases belong exclusively to O_in.

**Multiple systems.** When multiple system boundaries appear on one diagram, let S_1 and S_2 be two subject systems with O_{in,1} and O_{in,2}. An actor may appear outside both boundaries and associate with use cases in both systems. This models integration scenarios.

**Worked example — Payment System Boundary:**

System: PaymentProcessingService
O_in = {AuthorizePayment, CapturePayment, RefundPayment, ValidateCard, LogTransaction}
O_ext = {Merchant (primary actor), Issuing Bank (secondary actor), Fraud Detection Service (secondary actor)}

Association cross-boundary:
- (Merchant, AuthorizePayment): Merchant initiates
- (Merchant, RefundPayment): Merchant initiates
- (IssuingBank, AuthorizePayment): Bank responds during authorization
- (FraudDetection, AuthorizePayment): Fraud service participates during authorization

### M5: Use Case Coverage Metric

**Use Case Coverage:**
```
UC_coverage = |{uc in U | has_at_least_one_test_scenario(uc)}| / |U|
```

**Functional Requirement Coverage:**
```
FR_coverage = |{fr in FR | exists uc in U such that traces_to(uc, fr)}| / |FR|
```

where traces_to(uc, fr) is true if use case uc implements or partially implements functional requirement fr.

**Adequacy thresholds:**
- UC_coverage >= 0.95: at least 95% of use cases have at least one test scenario
- FR_coverage = 1.0: every functional requirement traces to at least one use case (hard requirement; any FR without a use case is orphaned and untestable)

**Worked example — Healthcare System Coverage:**

FR set: {FR-001: Register Patient, FR-002: Schedule Appointment, FR-003: View Medical History, FR-004: Prescribe Medication, FR-005: Generate Bill}
Use case set: {UC-01: RegisterPatient, UC-02: BookAppointment, UC-03: ViewHistory, UC-04: PrescribeMedication, UC-05: GenerateBill, UC-06: CancelAppointment}

Test scenarios: UC-01 (1), UC-02 (2), UC-04 (1), UC-06 (1). UC-03 and UC-05 have no test scenarios.

UC_coverage = 4/6 = 0.667 — below 0.95. Action: add test scenarios for UC-03 and UC-05.

FR traceability: FR-001→UC-01, FR-002→UC-02, FR-003→UC-03, FR-004→UC-04, FR-005→UC-05. All FRs covered.
FR_coverage = 5/5 = 1.0 — complete.

### M6: MOSCOW Priority Scoring

**Priority set:** P = {M=Must-have, S=Should-have, C=Could-have, W=Won't-have}

**Weights:** w(M) = 0.40, w(S) = 0.30, w(C) = 0.20, w(W) = 0.10

**Priority score for use case uc, given votes from k stakeholders:**

```
Priority_score(uc) = (sum_{p in P} w(p) * count_{uc,p}) / total_votes
```

where count_{uc,p} = number of stakeholders who voted priority p for use case uc, and total_votes = total number of stakeholder votes cast for uc (sum over all priorities).

**Weighted stakeholder matrix:** Rows = use cases, columns = stakeholders, cell = priority letter.

**Final priority determination:**
- If a clear mode exists (majority vote on one priority): use that priority.
- If no majority: use weighted average Priority_score to rank within ambiguous cases.
- Must-have threshold: Priority_score > 0.35 → classify as M.

**Worked example — 5 use cases, 4 stakeholders:**

| Use Case | Dev | PM | CEO | Legal | Score | Final |
|----------|-----|----|----|-------|-------|-------|
| Login | M | M | M | M | 0.40*(4/4) = 0.40 | Must |
| Dashboard | M | M | S | C | 0.40*(2/4)+0.30*(1/4)+0.20*(1/4) = 0.325 | Should |
| Reports | S | C | C | W | 0.30*(1/4)+0.20*(2/4)+0.10*(1/4) = 0.175 | Could |
| Audit Log | S | M | W | M | 0.40*(2/4)+0.30*(1/4)+0.10*(1/4) = 0.30 | Should |
| Dark Mode | C | W | W | W | 0.20*(1/4)+0.10*(3/4) = 0.125 | Won't |

Calculation for Dashboard: 2 votes M, 1 vote S, 1 vote C, 0 votes W.
Score = (0.40*2 + 0.30*1 + 0.20*1 + 0.10*0) / 4 = (0.80+0.30+0.20) / 4 = 1.30/4 = 0.325

---

## 8. Anti-Patterns to Avoid

1. **Modeling a use case with degree 0 (no associated actor)**: M1's degree constraint requires deg_U(uc) >= 1 for every use case in U — an isolated use case with no actor association is a completeness violation, since a use case with no external trigger cannot be initiated and represents a requirements gap.

2. **Attributing a use case to an actor, or treating an actor as inside the system boundary**: M4's partition property requires O_in ∩ O_ext = ∅ with all use cases strictly in O_in and all actors strictly in O_ext. Drawing an actor node inside the system boundary, or a use case node outside it, violates the boundary-rigidity principle and misrepresents who does what.

3. **Treating Extend as equivalent to Include when the extension condition is false**: M2's formal semantics distinguish them precisely — Include is unconditional (`traces(uc_base) ⊇ traces(uc_included)`, always executed), while Extend only augments traces when its guard g evaluates true; when g=false, `traces(uc_base)` is UNCHANGED. Diagramming an Extend relationship as if the extension always fires (like an Include) misrepresents which behavior is conditional.

4. **Assuming Include chain transitivity without verifying every link holds**: M2's transitivity lemma (Include(A,B) ∧ Include(B,C) ⟹ C is mandatory in A) is only valid if BOTH Include relationships in the chain actually hold as stated. Asserting a transitive Include relationship (A always includes C) without confirming both direct links exist in the model produces an unproven, potentially false dependency claim.

5. **Counting fish-level or kite-level use cases in the Sea-level completeness metric**: M3's Completeness = |UC_tested|/|UC_sea| is defined strictly over UC_sea, the sea-level goal tier. Including fish-level (sub-function, like "Validate Credit Card") or kite-level (summary, like "Maximize GMV") use cases in the denominator dilutes the metric and produces a completeness score that doesn't reflect actual user-goal-level test coverage.

6. **Reporting UC_coverage without also checking FR_coverage, or vice versa**: M5 defines these as two DISTINCT metrics with different adequacy thresholds — UC_coverage ≥ 0.95 (test-scenario adequacy) versus FR_coverage = 1.0 (a hard requirement, since any FR without a tracing use case is orphaned and untestable). A project reporting only UC_coverage while an FR sits untraced to any use case has a genuine requirements gap the UC_coverage number doesn't reveal.

7. **Treating FR_coverage below 1.0 as an acceptable trade-off like UC_coverage below 0.95**: M5 explicitly marks FR_coverage = 1.0 as a hard requirement, not a target to approach — any FR that doesn't trace to at least one use case is by definition orphaned and untestable. Applying the same "mostly there" tolerance used for the 0.95 UC_coverage threshold to FR_coverage misapplies the metric's stated severity.

8. **Computing a MOSCOW priority score from raw vote counts without normalizing by total_votes**: M6's Priority_score(uc) = (Σ w(p)·count) / total_votes divides by the actual number of votes cast for that use case, not a fixed stakeholder count. Comparing raw weighted sums across use cases with different numbers of votes cast (e.g. one use case voted on by all 4 stakeholders, another by only 2) without the normalization produces incomparable scores.

9. **Applying the Must-have threshold (Priority_score > 0.35) as a tie-breaker before checking for a clear majority vote**: M6's decision rule is ordered — first check for a clear mode (majority vote on one priority, use that directly), and only fall back to the weighted Priority_score to rank AMBIGUOUS cases with no majority. Applying the numeric threshold first, even when a clean majority exists, can override a stakeholder consensus with a numerically-derived tie-breaker that wasn't needed.

10. **Modeling multiple system boundaries without letting a shared actor cross both**: M4 explicitly supports the case where "an actor may appear outside both boundaries and associate with use cases in both systems" for integration scenarios — duplicating an actor as two separate nodes (one per system boundary) instead of one shared actor node loses the fact that it's the same external stakeholder interacting with both systems.

---

## 9. India-Specific Layer

**NIC-SSDLC (National Informatics Centre — Standardized SDLC v2.0):**
NIC-SSDLC mandates use case coverage traceability in all central government IT projects. Phase 1 (Initiation/Feasibility) requires a use case context diagram. Phase 2 (Requirements) requires complete use case diagrams with FR traceability. The NIC Tender Technical Evaluation Criteria score marks for completeness of use case traceability matrices. All NIC-managed projects (ration card systems, passport portals, income tax e-filing) use NIC-SSDLC.

**STQC SEPC (Software and Electronics Products Certification):**
STQC certification for CMMI Level 3 and above requires a Use Case Coverage Report as a process artifact. The report must show UC_coverage >= 0.95 and FR_coverage = 1.0 for the Requirements Development process area. STQC audit checklist item: "Verify use case traceability matrix against SRS." Missing traceability is a process noncompliance finding.

**MeitY SDLC Phase 2 — Requirements:**
MeitY e-Governance SDLC guidelines (published by STQC/TEC) mandate use case diagrams in the Software Requirements Specification (SRS) for systems of complexity >= 5 KLOC. Guideline reference: STQC/SDLC/Phase2/UC-001. Applies to all projects procured under Digital India, GeM (Government e-Marketplace), and NIC.

**BIS IS/ISO 19505-2:2012 (UML Superstructure):**
The Bureau of Indian Standards has adopted ISO/IEC 19505-2:2012 as IS/ISO 19505-2:2012 without technical modification. This standard covers Chapter 18 (Use Cases). Indian organizations can cite IS/ISO 19505-2:2012 compliance for government and enterprise tenders. Available at bis.gov.in.

**NASSCOM SSC/Q0502 (National Occupational Standards — Software Developer, NSQF Level 6):**
Use case modeling is listed as a core technical competency under SSC/Q0502. UGC NET/JRF Computer Science and GATE CS Software Engineering units include use case diagrams as testable content. AICTE B.Tech (CSE/IT) model curriculum mandates UML use case diagrams in the Software Engineering course.

---

## 10. Response Rules

1. Always identify actors first — ask the user to distinguish primary (initiating) actors from secondary (participating) actors before drawing associations.
2. Apply the goal hierarchy test: reject use cases that are kite-level (too abstract) or fish-level (too detailed) — guide the user to the sea level.
3. Never place actors inside the system boundary rectangle; never place use cases outside it.
4. Use Include only for mandatory, reusable sub-behavior referenced by 2+ base use cases. Use Extend only for conditional, non-essential behavior with a named extension point and guard condition.
5. Verify FR_coverage = 1.0 before finalizing: every functional requirement must trace to at least one use case.
6. Apply MOSCOW scoring when the user has multiple stakeholders and a backlog-prioritization need.
7. For India government projects, explicitly call out NIC-SSDLC Phase 2 compliance requirements and traceability matrix format.
8. Include Mermaid syntax output alongside PlantUML or draw.io XML for maximum tool compatibility.

---

## 11. What Not to Do

- Do not add use cases for implementation details (e.g., "Connect to Database," "Serialize Object") — these are fish-level and belong in design, not requirements.
- Do not use Extend when Include is correct — if the extension ALWAYS executes, it is Include not Extend.
- Do not draw actor-to-actor associations — actors do not communicate directly in a use case diagram.
- Do not omit the system boundary rectangle — boundary is mandatory per UML 2.5.1 Chapter 18.
- Do not place an actor generalization arrow in the wrong direction (specific --|> general, same as class generalization).
- Do not create use cases that map one-to-one with UI screens — use cases are goal-oriented, not screen-oriented.
- Do not write use case names as verb-noun phrases that describe system internals (e.g., "Update Database Row"). Names must describe user goals: "Update Profile."

---

## 12. Output Expectations

For each use case diagram request, deliver:

1. **Actor list:** Name, role (primary/secondary), description, generalization hierarchy if applicable.
2. **Use case list:** Name, goal level (sea/fish/kite classification), associated actors, include/extend relationships.
3. **PlantUML syntax:** Full `@startuml` / `@enduml` block rendering the diagram.
4. **Mermaid syntax** (where supported by diagram structure): `graph LR` or dedicated notation.
5. **FR traceability matrix:** Table mapping FRs to use cases with coverage metrics.
6. **MOSCOW priority matrix** (if stakeholder input provided): weighted scoring table with final priority.
7. **Completeness report:** UC_coverage, FR_coverage, identified gaps.
8. **India compliance note** (if project is government or regulated): applicable standards (NIC-SSDLC, STQC, BIS, MeitY).

---

## 13. Skill Scope

**In scope:**
- UML 2.5.1 Chapter 18 use case diagram notation and semantics
- Actor identification, primary/secondary classification, generalization
- Include and Extend relationships with correct directionality and semantics
- System boundary definition and multi-system diagrams
- Goal hierarchy classification (Cockburn levels)
- FR traceability matrix generation
- Coverage metric computation (UC_coverage, FR_coverage)
- MOSCOW priority scoring
- India regulatory compliance: NIC-SSDLC, STQC CMMI, MeitY, BIS IS/ISO 19505-2
- PlantUML and Mermaid diagram syntax output

**Out of scope:**
- Behavioral specification of use case flows (use activity diagrams — see uml-activity-diagram-core)
- Detailed use case descriptions in template format (use case descriptions are prose documents, not diagrams)
- OCL formal proofs and soundness verification (delegate to uml-diagram-mathematics-expert)
- Draw.io XML generation (see drawio-xml-generation-core)

---

## 14. Version

v1.1.0 — Added Section 8 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India-Specific Layer through Version renumbered §9-14.
v1.0.0 — Initial release. Domain 46: UML & Diagram Engineering. Covers UML 2.5.1 Chapter 18. India layer: NIC-SSDLC, STQC SEPC, MeitY SDLC, BIS IS/ISO 19505-2:2012, NASSCOM SSC/Q0502.
