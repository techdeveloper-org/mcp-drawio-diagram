---
name: uml-activity-diagram-core
description: "Generates UML 2.5.1 activity diagrams modeling workflows, business processes, and algorithm flow with Petri net semantics. Use when modeling business process workflows, algorithm flowcharts, parallel processing pipelines, swimlane responsibility assignments, or exception handling patterns. Keywords: activity diagram UML, workflow diagram, business process model UML, swimlane diagram, Petri net workflow, parallel activity fork join, exception handler activity, BPMN to UML"
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/uml-activity-diagram-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# UML Activity Diagram Core

## Description

Produces UML 2.5.1 activity diagrams (Chapter 15 of the OMG specification) covering the complete ActivityNode hierarchy, token flow semantics, Petri net correspondence, swimlane partitioning, exception handling, BPMN mapping, and cyclomatic complexity analysis. Applies formal token conservation, guard predicate logic, and graph-coloring theory for swimlane assignment. Addresses RBI IT circular, IRDAI workflow, NIC-SSDLC, and NASSCOM BPM standards applicable to Indian regulated industries.

---

## 1. UML 2.5.1 Activity Metamodel

The authoritative metaclasses from OMG UML 2.5.1 Chapter 15:

**Activity:** Subclass of Behavior. Owns ActivityNodes connected by ActivityEdges. isReadOnly: Boolean; isSingleExecution: Boolean.

**ActivityNode (abstract) — three concrete subtypes:**

*ActionNode (abstract):* OpaqueAction (arbitrary behavior), CallBehaviorAction (invokes another Activity), CallOperationAction (invokes an Operation), SendSignalAction (sends a Signal asynchronously), AcceptEventAction (waits for an event or signal), ValueSpecificationAction (produces a value).

*ControlNode (abstract):* InitialNode (black filled circle; exactly 1 outgoing, 0 incoming); ActivityFinalNode (bullseye; terminates all flows); FlowFinalNode (circle-with-X; terminates one flow thread); ForkNode (horizontal/vertical bar; 1 incoming, 2+ outgoing); JoinNode (bar; 2+ incoming, 1 outgoing); MergeNode (diamond or bar; 2+ incoming, 1 outgoing; fires on any token); DecisionNode (diamond; 1 incoming, 2+ outgoing; only one guard fires).

*ObjectNode (abstract):* ActivityParameterNode (boundary parameter), CentralBufferNode (FIFO buffer), DataStoreNode (persistent storage), InputPin and OutputPin (on actions).

**ActivityEdge (abstract):** ControlFlow (carries control tokens), ObjectFlow (carries data tokens). Attributes: guard: ValueSpecification (Boolean expression, default `true`); weight: ValueSpecification (token count required to fire, default `1`).

**ActivityPartition:** Swimlane grouping. isDimension: Boolean; isExternal: Boolean. Multi-dimensional partitions create matrix swimlanes.

**ExceptionHandler:** Protects a set of actions. When exception of handlerBody's exceptionType is raised, the handler body executes.

**StructuredActivityNode:** An Action that also owns a nested Activity sub-graph (sequence, loop, or conditional structured node subtypes).

OCL well-formedness from spec:
```
context DecisionNode inv:
  self.incoming->size() = 1 and self.outgoing->size() >= 2
context JoinNode inv:
  self.incoming->size() >= 2 and self.outgoing->size() = 1
```

---

## 2. Notation Reference

| Element | Symbol |
|---------|--------|
| Action | Rounded rectangle |
| InitialNode | Filled black circle |
| ActivityFinalNode | Black circle inside ring (bullseye) |
| FlowFinalNode | Circle with X |
| DecisionNode / MergeNode | Diamond |
| ForkNode / JoinNode | Thick horizontal or vertical bar |
| ControlFlow | Solid arrow |
| ObjectFlow | Arrow with object node |
| ActivityPartition (swimlane) | Named dashed-border lane |
| ExceptionHandler | Lightning-bolt arrow from protected region to handler |
| InterruptibleActivityRegion | Dashed rounded rectangle |

---

## 3. Activity Partition (Swimlane) Design

Swimlanes partition action responsibilities by actor, system component, or organizational unit.

**Assignment rules:**
- Each action belongs to exactly one swimlane (the responsible actor/system).
- Control flow and object flow arrows may cross swimlane boundaries freely.
- If an action involves joint responsibility, use the nearest single responsible party or a matrix swimlane.

**Multi-dimensional swimlanes:** Rows = one dimension (e.g., organizational role); columns = another dimension (e.g., system component). Each cell is a swimlane. Place action in the cell at the intersection of its role and system.

**Common swimlane patterns:**
- Horizontal lanes, left-to-right flow: suitable for sequential workflow with role handoffs.
- Vertical lanes, top-to-bottom flow: suitable for component interaction across layers.
- Matrix lanes: suitable for system-role matrix in large enterprise workflows.

---

## 4. Exception Handling and Interruption

**ExceptionHandler construction:**
1. Identify the protected body (set of actions that may raise an exception).
2. Specify the exceptionType (Signal or Exception classifier).
3. Draw the handler body (set of actions that execute when the exception is raised).
4. Connect with an exception handler edge (lightning-bolt arrow style in PlantUML).

**InterruptibleActivityRegion:**
Enclose a set of nodes in a dashed rounded rectangle. When an interrupt signal is received (an AcceptEventAction or a cancel signal), all tokens within the region are destroyed, and an Interrupt edge carries a token to the continuation outside the region.

Use case: timeout handling in long-running workflows.

---

## 5. BPMN to UML Activity Diagram Mapping

| BPMN Element | UML Activity Element |
|-------------|---------------------|
| Process | Activity |
| Task | CallBehaviorAction or OpaqueAction |
| Start Event | InitialNode |
| End Event | ActivityFinalNode |
| Intermediate Event (catch) | AcceptEventAction |
| Intermediate Event (throw) | SendSignalAction |
| Exclusive Gateway (XOR) | DecisionNode / MergeNode |
| Parallel Gateway (AND) | ForkNode / JoinNode |
| Inclusive Gateway (OR) | DecisionNode with multiple guards (multi-fire) |
| Pool | ActivityPartition (top-level swimlane) |
| Lane | ActivityPartition (nested swimlane) |
| Sequence Flow | ControlFlow edge |
| Data Object | ObjectNode (CentralBufferNode) |
| Compensation | ExceptionHandler |

Key difference: BPMN Inclusive Gateway (OR-split) has no direct UML equivalent. Model as multiple parallel paths each guarded by a condition, merging at a join point.

---

## 6. Deep Mathematical Foundations

### M1: Petri Net Correspondence

**Definition.** A Petri net N = (P, T, F) where:
- P = finite set of places (circles)
- T = finite set of transitions (bars), P ∩ T = ∅
- F ⊆ (P × T) ∪ (T × P) = flow relation (directed arcs)

**UML Activity → Petri Net mapping:**

| UML Activity Element | Petri Net Element |
|----------------------|------------------|
| ActionNode | Transition t |
| ObjectNode (CentralBufferNode) | Place p (token = data object) |
| ControlFlow edge (between actions) | Place p (control token) + arc from preceding transition to p to next transition |
| ForkNode | Transition with multiple output places (AND-split: fires once, puts token in ALL output places) |
| JoinNode | Transition that fires only when ALL input places have >= 1 token (AND-join) |
| DecisionNode | Transition with guard on output arcs (OR-split: exactly one arc fires) |
| MergeNode | Transition that fires when ANY input place has >= 1 token (OR-join) |
| InitialNode | Source place pre-loaded with 1 token at Activity start |
| ActivityFinalNode | Sink transition that consumes all remaining tokens |
| FlowFinalNode | Sink transition that consumes only the arriving token |

**Worked example — 3-step parallel workflow:**

Steps: A(Receive Order), B(Check Inventory), C(Process Payment), D(Ship Order)
B and C execute in parallel after A; D starts after both B and C complete.

Petri net:
- Places: p0 (initial), p1 (after A), p2 (B ready), p3 (C ready), p4 (B done), p5 (C done), p6 (D ready)
- Transitions: tA (action A), tFork (fork after A), tB (action B), tC (action C), tJoin (join before D), tD (action D)
- Arcs: p0→tA, tA→p1, p1→tFork, tFork→p2, tFork→p3, p2→tB, tB→p4, p3→tC, tC→p5, p4→tJoin, p5→tJoin, tJoin→p6, p6→tD

tFork fires when p1 has a token → puts tokens in BOTH p2 and p3.
tJoin fires only when BOTH p4 and p5 have tokens (synchronization).

### M2: Token Flow Conservation (Kirchhoff's Law for Petri Nets)

**Token conservation.** At every internal node (non-initial, non-final) in steady-state execution, the number of tokens entering equals the number leaving:

For a transition t:
```
sum_{p in input_places(t)} tokens_consumed(p, t) = sum_{p in output_places(t)} tokens_produced(t, p)
```

Specific rules:
- ForkNode: n_in = 1 token consumed, n_out tokens produced (one per output place). n_out >= 2.
- JoinNode: n_in tokens consumed (one from each input place, all must be present), n_out = 1 token produced. Deadlock condition at JoinNode: at least one input place never receives a token → JoinNode never fires → deadlock.
- DecisionNode: 1 token consumed, 1 token produced on exactly one output arc (guard true).
- MergeNode: 1 token consumed (from whichever input fires first), 1 token produced.

**Deadlock detection.** A deadlock state exists when:
- There exists at least one token in the net, AND
- No transition is enabled (no transition has all input places marked with >= 1 token).

In UML activity terms: workflow is stuck with unfinished work and no action can fire. Cause: a JoinNode whose inputs are never simultaneously satisfied (e.g., one branch never produces a token due to a false guard with no merge path).

**Worked example — Fork-Join token conservation verification:**

ForkNode splits into 3 parallel branches. Token count at fork: 1 in → 3 out.
After branches complete: JoinNode has 3 inputs, each with 1 token → fires → 1 out.

Kirchhoff check at JoinNode: 3 tokens consumed, 1 token produced. Conservation holds within the fork-join pair (1 in at fork = 1 out at join).

If one branch has a FlowFinalNode instead of routing to JoinNode: that branch token is consumed at FlowFinalNode; JoinNode receives tokens from only 2 branches → deadlock if JoinNode expects 3 inputs. Fix: replace FlowFinalNode with a path back to JoinNode, or restructure using an OR-join (MergeNode) instead of AND-join (JoinNode).

### M3: Decision/Merge Guard Predicates

**Guard predicate on ActivityEdge.** Each outgoing edge of a DecisionNode carries a guard [g] where g is a Boolean-valued ValueSpecification (typically an OpaqueExpression in a constraint language such as OCL or natural language).

**Exclusive-OR semantics at DecisionNode.** For a DecisionNode with n outgoing edges guarded by g_1, g_2, ..., g_n:
1. Completeness: ∀ token arrival, exactly one g_i evaluates to true (no stuck state).
   Formal: g_1 ∨ g_2 ∨ ... ∨ g_n = true (guards partition the input domain).
2. Exclusivity: at most one g_i is true at any evaluation point.
   Formal: ∀ i ≠ j: g_i ∧ g_j = false (guards are mutually exclusive).

**Special guard `[else]`:** The else guard fires when all other guards evaluate to false. It serves as the completeness guarantee without requiring explicit enumeration of all false conditions.

**Guard on JoinNode (join specification):** A JoinNode may have a `joinSpec` attribute (ValueSpecification) that specifies a non-default join condition. Default: AND (all inputs must be marked). Custom joinSpec can implement OR-join semantics for more flexible synchronization.

**Worked example — Order processing decision:**

DecisionNode after "Validate Payment":
- Edge 1: [payment_status = 'approved'] → SendConfirmationEmail
- Edge 2: [payment_status = 'declined'] → NotifyCustomerDecline
- Edge 3: [payment_status = 'pending'] → WaitForSettlement

Completeness check: approved ∨ declined ∨ pending covers all possible payment_status values ✓
Exclusivity check: payment_status can have only one value at a time ✓

Missing guard trap: if payment_status = 'error' is possible but not guarded, a token arrives at DecisionNode with no matching guard → stuck (model error). Fix: add `[else]` or explicit error guard.

### M4: Swimlane Partition as Graph Coloring

**Graph coloring formulation.** Let G = (V, E) be the activity graph where V = ActivityNodes and E = ActivityEdges.

A swimlane partition is a coloring function:
```
pi: V → Partitions
```
where Partitions is a finite set of swimlane labels (actor names, system names, etc.).

Each equivalence class pi^{-1}(lane) = the set of nodes belonging to swimlane lane.

**Single-dimension swimlane:** pi: V → {lane_1, lane_2, ..., lane_k}. Nodes with the same color belong to the same lane. Edges crossing lane boundaries represent handoffs or data transfers between responsible parties.

**Multi-dimensional (matrix) swimlane:** Two coloring functions applied simultaneously:
```
pi_1: V → Roles    (rows)
pi_2: V → Systems  (columns)
```
A node v belongs to cell (pi_1(v), pi_2(v)) in the matrix. The matrix swimlane requires that each node has exactly one row assignment AND one column assignment.

**Responsibility semantic:** Nodes in swimlane `lane` represent activities for which `lane` is responsible. An edge from node in lane A to node in lane B models a handoff from A to B.

**Worked example — 2D swimlane (role × system):**

Roles: {Customer, Clerk, Manager}
Systems: {WebPortal, BackendService, Database}

Action: "Submit Application" → pi_1 = Customer, pi_2 = WebPortal → cell (Customer, WebPortal)
Action: "Validate Application" → pi_1 = Clerk, pi_2 = BackendService → cell (Clerk, BackendService)
Action: "Store Record" → pi_1 = Clerk, pi_2 = Database → cell (Clerk, Database)
Action: "Approve Application" → pi_1 = Manager, pi_2 = BackendService → cell (Manager, BackendService)

Edge "Submit Application" → "Validate Application" crosses both row (Customer→Clerk) and column (WebPortal→BackendService), representing a cross-role, cross-system handoff.

### M5: Exception Handler Semantics

**ExceptionHandler formal model.**

Let H = (PB, ET, HB) where:
- PB = protected body (set of actions that may raise an exception)
- ET = exception type (Signal or Exception classifier)
- HB = handler body (set of actions that execute when exception of type ET is raised in PB)

**Execution semantics:**
1. All actions in PB begin normally.
2. If any action in PB raises a signal/exception of type ET:
   - All tokens currently in PB are CONSUMED (destroyed).
   - All currently executing actions in PB are CANCELLED.
   - The handler input pin receives a token typed as ET.
   - Actions in HB execute starting from the handler input pin.
3. If no exception is raised: PB completes normally; HB never executes.

**InterruptibleActivityRegion (IAR) semantics:**

Let IAR = (R, IS) where R = set of enclosed nodes, IS = interrupt signal type.
When an AcceptEventAction inside R receives signal IS:
- All tokens in ALL nodes in R are immediately destroyed.
- An Interrupt edge (lightning-bolt arrow) carries a control token to the designated continuation node outside R.

Use case: implementing timeout cancel in long-running batch processes.

**Worked example — File processing with exception:**

Protected body: {ReadFile, ParseData, ValidateSchema}
Exception type: FileNotFoundException
Handler body: {LogError, NotifyAdministrator, ReturnEmptyResult}

Normal path: ReadFile → ParseData → ValidateSchema → ProcessData
Exception path: ReadFile raises FileNotFoundException → tokens in ParseData/ValidateSchema destroyed → LogError → NotifyAdministrator → ReturnEmptyResult

If FileNotFoundException is NOT listed in the ExceptionHandler, it propagates upward to the enclosing Activity. If no handler exists at any level, the Activity terminates abnormally.

### M6: Cyclomatic Complexity for Activity Graphs

**Definition.** McCabe's Cyclomatic Complexity for an activity graph G = (V, E):
```
CC = E - N + 2P
```
where E = number of edges, N = number of nodes, P = number of connected components (usually P = 1 for a single activity).

For a single-component activity:
```
CC = E - N + 2
```

**Interpretation:** CC = the minimum number of linearly independent execution paths through the activity. Each independent path is a distinct test case needed for full path coverage.

**Contribution of control nodes:**
- Each DecisionNode with n outgoing edges adds (n-1) to CC (n-1 additional paths).
- Each ForkNode contributes 1 extra path per output beyond the first.
- Loops (back edges in the control flow graph) also contribute +1 per loop.

**Thresholds:**
- CC <= 10: low complexity, easily tested and maintained
- CC 11-20: moderate, consider refactoring long decision chains
- CC > 20: high, mandatory refactoring — extract sub-activities using CallBehaviorAction

**Worked example — 5-decision workflow:**

Workflow: Place Order → [decision: payment method] → 3 paths merge → [decision: inventory] → 2 paths merge → Ship OR Backorder.

Nodes N: InitialNode, PlaceOrder, PaymentDecision, CashPath, CardPath, PayPalPath, PaymentMerge, InventoryDecision, ShipPath, BackorderPath, InventoryMerge, FinalNode = 12 nodes
Edges E: 1 (init→Place), 1 (Place→PayDec), 3 (PayDec→3 paths), 3 (paths→PayMerge), 1 (PayMerge→InvDec), 2 (InvDec→2 paths), 2 (paths→InvMerge), 1 (InvMerge→Final) = 14 edges

CC = 14 - 12 + 2 = 4

Interpretation: 4 independent test paths needed:
1. Cash payment + In Stock
2. Card payment + In Stock
3. PayPal payment + Backordered (same as card for inventory)
4. Cash payment + Backordered

All 4 paths must be tested to achieve full path coverage.

---

## 7. Anti-Patterns to Avoid

1. **Modeling a JoinNode whose inputs can never be simultaneously satisfied**: M2's deadlock condition is explicit — a JoinNode deadlocks when at least one input place never receives a token (e.g. one branch terminates at a FlowFinalNode instead of routing to the join). A workflow that "usually works" in testing but has an untested branch bypassing the join will deadlock in production the first time that branch actually executes.

2. **Using an AND-join (JoinNode) when the intended semantics are OR-join**: M2/M3 distinguish JoinNode (fires only when ALL input places are marked — default AND) from MergeNode or a custom `joinSpec` (OR-join, fires when ANY input is marked). Using a default JoinNode for a "whichever branch finishes first" scenario silently requires every branch to complete, hanging the workflow until the slowest or a never-taken branch blocks it forever.

3. **Leaving a DecisionNode's guards incomplete (not exhaustive)**: M3's completeness requirement is g_1 ∨ g_2 ∨ ... ∨ g_n = true — every possible value the guarded condition can take must be covered. The worked example's "missing guard trap" (an unguarded `payment_status = 'error'` value) shows a token can arrive at a DecisionNode with no matching guard and get stuck; always include an `[else]` guard or enumerate every case explicitly.

4. **Writing overlapping (non-exclusive) guards on a DecisionNode's outgoing edges**: M3's exclusivity requirement is ∀i≠j: g_i ∧ g_j = false. Two guards that can both evaluate true for the same token (e.g. numeric range guards with an overlapping boundary) create a nondeterministic choice the formalism doesn't define, not a deliberate parallel split (which requires a ForkNode, not a DecisionNode).

5. **Coloring a swimlane node with more than one lane assignment in single-dimension partitioning**: M4's coloring function π: V → Partitions assigns exactly one lane per node. An action that legitimately spans two roles' responsibility should be split into two actions with a handoff edge between lanes, not drawn as a single node ambiguously placed across a lane boundary.

6. **Omitting the row OR column assignment in a matrix (2D) swimlane**: M4's multi-dimensional swimlane requires each node to have BOTH a row (π₁) and column (π₂) assignment — a node placed at an undefined or ambiguous matrix cell breaks the "exactly one row AND one column" requirement the responsibility semantics depend on.

7. **Assuming an exception handler's protected-body tokens survive after the exception fires**: M5's execution semantics state that when an exception of the handled type is raised, ALL tokens currently in the protected body are CONSUMED (destroyed) and all executing actions are CANCELLED — the handler starts fresh from its own input pin, not from wherever the protected body left off. Modeling a handler that "resumes" mid-protected-body misrepresents the destroy-and-restart semantics.

8. **Failing to route an unhandled exception type to a handler at an enclosing level**: M5 states an exception not listed in the current ExceptionHandler propagates upward to the enclosing Activity, and if no handler exists at ANY level, the Activity terminates abnormally. Diagramming a protected body with only a narrow exception type handled, without confirming a fallback handler exists further up, leaves genuinely possible failure modes with no diagrammed recovery path.

9. **Computing Cyclomatic Complexity by counting only DecisionNodes and ignoring ForkNode/loop contributions**: M6's CC = E - N + 2 counts EVERY edge and node in the graph — DecisionNodes contribute (n-1) per node, ForkNodes contribute 1 extra path per output beyond the first, AND loops (back edges) each contribute +1. Computing CC from only the decision-node count undercounts true path complexity whenever forks or loops are present.

10. **Treating CC > 20 as a suggestion rather than the stated mandatory-refactoring threshold**: M6's thresholds distinguish CC ≤ 10 (low), 11-20 (moderate, "consider refactoring"), and > 20 ("mandatory refactoring — extract sub-activities using CallBehaviorAction"). Leaving a >20-CC activity un-refactored because it "still works" ignores that the threshold marks the point where achieving full path coverage in testing becomes practically infeasible, not just stylistically undesirable.

---

## 8. India-Specific Layer

**RBI Master Direction on IT Framework (NBFC, 2017) and payment system circulars:**
The Reserve Bank of India requires process flow documentation for all payment and banking systems subject to RBI oversight. This includes banks, NBFCs, payment aggregators (Razorpay, PhonePe, etc.), and UPI member banks. Activity diagrams (or equivalent BPMN) serve as acceptable process flow documentation in IT audit evidence packages. RBI Examiners review these diagrams during IT audits to verify that documented processes match implemented systems.

**IRDAI IT Framework for Insurers — Claims Workflow:**
IRDAI guidelines on IT framework require that insurance companies document their claims processing workflows. The UML activity diagram (or BPMN equivalent) is the standard format for this documentation, mapping states from claim submission through review, investigation, approval/rejection, and settlement. Companies such as LIC, ICICI Lombard, and HDFC ERGO use these diagrams for IRDAI audit submissions. The claims lifecycle swimlane typically includes: Policyholder, Claims Officer, Surveyor, Finance, and IT System lanes.

**NIC-SSDLC Phase 2 — Activity Diagrams:**
NIC-SSDLC v2.0 Phase 2 (Requirements) recommends activity diagrams for documenting business process flows for all central government IT systems. Phase 3 (Design) uses activity diagrams for algorithm design. GIGW (Guidelines for Indian Government Websites) recommends UML activity diagrams for documenting user journeys on government portals.

**NASSCOM BPM Sector — Activity Diagrams and BPMN Alignment:**
India's BPM industry (Infosys BPM, Genpact, Wipro BPS, HCL BPO) processes documents, claims, and transactions for global clients. ISO 9001 QMS (widely adopted in Indian BPM) requires documented process flows. NASSCOM recommends UML activity diagrams as semantically equivalent to BPMN 2.0 process flows for organizations that use UML-based modeling tools. The mapping in Section 5 of this skill enables practitioners to translate between BPMN (client specification format) and UML (internal development format).

---

## 9. Response Rules

1. Begin by identifying the process type: sequential workflow, parallel workflow, decision-heavy algorithm, or exception-prone process. Choose control nodes accordingly.
2. Apply Petri net semantics check: for every ForkNode, verify a matching JoinNode exists. Orphaned fork branches that never join cause permanent token loss.
3. Verify guard completeness at every DecisionNode: either an explicit else guard or exhaustive guard coverage of the input domain.
4. Use swimlanes for any process involving 2+ responsible parties. Name swimlanes after roles or system components, not individuals.
5. Apply CC calculation to flag high-complexity activities (CC > 20) and recommend extraction via CallBehaviorAction.
6. Map BPMN concepts to UML equivalents when the client provides BPMN specifications.
7. For RBI/IRDAI regulated systems, note the audit evidence requirement and produce swimlane diagrams that clearly show system vs human responsibility separation.
8. Always include InitialNode and ActivityFinalNode. Never leave the activity diagram without clear entry and exit nodes.

---

## 10. What Not to Do

- Do not use ActivityFinalNode to terminate only one flow thread — use FlowFinalNode for partial flow termination; ActivityFinalNode terminates ALL threads in the entire activity.
- Do not connect two ForkNodes in sequence without a matching JoinNode — this creates exponential token multiplication and is a model error.
- Do not place guards on JoinNode incoming edges — guards apply only to DecisionNode outgoing edges and ObjectFlow edges (JoinNode semantics are controlled by its joinSpec, not edge guards).
- Do not confuse DecisionNode (OR-split) with ForkNode (AND-split) — DecisionNode fires exactly one outgoing edge; ForkNode fires ALL outgoing edges simultaneously.
- Do not use the same partition (swimlane) for unrelated responsibilities — each swimlane must have a single clearly defined owner.
- Do not omit ExceptionHandler for actions that interact with external systems (file I/O, network calls, database) in process documentation for regulated systems.

---

## 11. Output Expectations

For each activity diagram request, deliver:

1. **Process description summary:** Brief natural language overview of the modeled workflow.
2. **Node inventory:** List of all ActionNodes, ControlNodes, and Partitions with types.
3. **PlantUML syntax:** Complete `@startuml` / `@enduml` block.
4. **Mermaid flowchart syntax** (for simple workflows without complex parallel paths): `flowchart TD` block.
5. **Petri net correspondence table:** Mapping of UML elements to Petri net components.
6. **Guard completeness verification table:** For each DecisionNode, list guards and confirm ∨ = true.
7. **Cyclomatic Complexity report:** E, N, CC value, threshold assessment.
8. **BPMN mapping table** (if client uses BPMN terminology): side-by-side BPMN → UML mapping.
9. **India compliance note** (if applicable): RBI/IRDAI/NIC-SSDLC specific requirements.

---

## 12. Skill Scope

**In scope:**
- UML 2.5.1 Chapter 15 activity diagram notation and semantics
- Full ActivityNode hierarchy (ActionNode, ControlNode, ObjectNode subtypes)
- Petri net correspondence and token flow semantics
- Guard predicate completeness and exclusivity verification
- Swimlane partitioning (1D and 2D matrix)
- ExceptionHandler and InterruptibleActivityRegion semantics
- BPMN 2.0 ↔ UML Activity element mapping
- Cyclomatic Complexity calculation and threshold guidance
- India regulatory compliance: RBI, IRDAI, NIC-SSDLC, NASSCOM BPM
- PlantUML and Mermaid flowchart syntax output

**Out of scope:**
- Full Petri net reachability analysis and deadlock detection algorithms (delegate to uml-diagram-mathematics-expert)
- BPMN execution semantics verification (use a BPMN engine or workflow tool)
- Business rule extraction from natural language requirements (use requirements engineering techniques)
- Draw.io XML generation for activity diagrams (see drawio-xml-generation-core)

---

## 13. Version

v1.1.0 — Added Section 7 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India-Specific Layer through Version renumbered §8-13.
v1.0.0 — Initial release. Domain 46: UML & Diagram Engineering. Covers UML 2.5.1 Chapter 15. India layer: RBI IT Framework, IRDAI IT Guidelines, NIC-SSDLC v2.0, NASSCOM BPM/ISO 9001.
