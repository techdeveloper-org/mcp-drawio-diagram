---
name: uml-sequence-diagram-core
description: "Generates UML 2.5.1 sequence diagrams with all message types, combined fragments, interaction uses, and duration constraints for modeling message-passing protocols. Use when designing API call sequences, documenting protocol interactions, modeling microservice communication patterns, creating test scenario specifications, or specifying request-response flows. Keywords: sequence diagram UML, message sequence chart, lifeline diagram, combined fragment alt loop, API interaction diagram, microservice sequence, protocol sequence diagram, synchronous async message UML"
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/uml-sequence-diagram-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# UML Sequence Diagram Core

## Description

Generates complete UML 2.5.1 sequence diagrams covering all lifeline types, all six MessageSort literals, all twelve InteractionOperatorKind combined fragments, activation intervals, interaction uses with gate semantics, duration and time constraints, and general ordering constraints. Applies the OMG UML 2.5.1 specification (ISO/IEC 19505-2:2012) Chapter 17 metamodel precisely. Use when designing API call sequences, documenting protocol interactions, modeling microservice communication patterns, creating test scenario specifications, or specifying request-response flows.

## 1. Core Metaclasses and Notation

### 1.1 Interaction and Lifeline

An Interaction is a BehavioredClassifier that owns Lifelines, Messages, CombinedFragments, and OccurrenceSpecifications. A Lifeline represents a process or object participating in the interaction and connects to a ConnectableElement via the represents property.

Notation rules:
- Lifeline header box: objectName : ClassName (underlined instance name, colon-separated class)
- Anonymous lifeline: : ClassName
- Dashed vertical line extends downward from the header
- Actor lifeline: stick figure header
- Stereotype variants: boundary, control, entity annotated on header box

### 1.2 Message Sorts (Six Literals)

UML 2.5.1 MessageSort enum has exactly six literals:

| MessageSort | Arrowhead | Meaning |
|-------------|-----------|---------|
| synchCall | Solid filled arrowhead | Synchronous call; sender blocks until reply received |
| asynchCall | Open half-arrowhead | Asynchronous call; sender does not block |
| asynchSignal | Open half-arrowhead | Signal with no return expected |
| reply | Dashed open arrowhead | Return message from called lifeline |
| createMessage | Open arrowhead to header | Creates the target lifeline instance |
| deleteMessage | Arrow to X mark | Destroys the target lifeline |

### 1.3 ExecutionSpecification

An ExecutionSpecification (activation box) is a gray or white rectangle on a lifeline representing active computation. Properties: start (OccurrenceSpecification at upper edge) and finish (OccurrenceSpecification at lower edge).

Synchronous calls create activation on the callee from receipt of synchCall until reply is sent. Activations nest for recursive calls.

### 1.4 Combined Fragments

A CombinedFragment is drawn as a rectangle with a pentagon label in the top-left corner showing the InteractionOperatorKind. It contains one or more InteractionOperand regions separated by dashed horizontal lines.

All twelve InteractionOperatorKind literals:

| Operator | Operands | Semantics |
|----------|----------|-----------|
| alt | 2+ with guards | Exactly one operand executes based on guards |
| opt | 1 | Executes if guard true; otherwise skip |
| break | 1 | Execute operand then break out of enclosing fragment |
| par | 2+ | All operands execute in any interleaved order |
| seq | 2+ | Sequential; per-lifeline order maintained, cross-lifeline relaxed |
| strict | 2+ | All events in operand N before any in N+1 across all lifelines |
| neg | 1 | Traces of this operand are invalid (prohibited) |
| critical | 1 | Atomic; no interleaving with enclosing par |
| ignore | 1 | Listed message set is ignored in traces |
| consider | 1 | Only messages in listed set are considered |
| assert | 1 | Operand traces are mandatory; violations are errors |
| loop | 1 with bounds | Repeats operand; loop(n,m) means n to m iterations |

## 2. Interaction Notation Details

### 2.1 Gates and Interaction Use

A Gate is a MessageEnd at the boundary of an Interaction frame. Formal gates appear on the defining Interaction boundary; actual gates appear on the InteractionUse referencing it. Gate parameters match by name.

InteractionUse notation: frame with ref in the pentagon, naming the referenced interaction.

### 2.2 Duration and Time Constraints

DurationConstraint specifies [min, max] duration between two OccurrenceSpecification events, shown as a brace-annotated double arrow spanning the two events.

TimeConstraint specifies an absolute time expression for a single event, shown as a brace with expression.

GeneralOrdering specifies a before->after ordering constraint between events on different lifelines, shown as a dotted arrow.

### 2.3 Loop Bounds

loop(n, m) uses InteractionConstraint with min=n and max=m. The operand body executes at least n and at most m times. loop(1,*) denotes one or more iterations (unbounded maximum).

## 3. Notation Quick Reference

```
:Client          :Server
   |                 |
   |--request()--->> |   synchCall (solid filled arrow)
   |                [|]  activation box on Server
   |<<--reply()------|   reply (dashed open arrow)
   |                 |
   | alt [cond]      |
   |----+------------|
   |    |  --ok()>>> |
   | [else]          |
   |----+------------|
   |    |  --err()>> |
   |_________________|
   |                 |
   | loop(1, 5)      |
   |  |--poll()--->> |
   |  |<<--data()--- |
   |_________________|
```

## 4. Python Generation Pattern

```python
def build_sequence_lifeline(name: str, classifier: str, x: int) -> dict:
    """Build a lifeline cell for a sequence diagram in mxGraph XML format.

    Args:
        name: Instance name (e.g., client).
        classifier: Classifier name (e.g., Client).
        x: Horizontal position in pixels.

    Returns:
        Dictionary with mxCell data for the lifeline header.
    """
    label = name + " : " + classifier
    return {
        "value": label,
        "style": "shape=mxgraph.uml.lifeline;whiteSpace=wrap;html=1;",
        "vertex": "1",
        "x": x, "y": 40, "width": 110, "height": 50
    }


def build_sync_message(label: str, src_id: str, tgt_id: str) -> dict:
    """Build a synchronous call message edge for a sequence diagram.

    Args:
        label: Message signature including parameters.
        src_id: Source lifeline mxCell id.
        tgt_id: Target lifeline mxCell id.

    Returns:
        Dictionary with mxCell edge attributes for the synchronous message.
    """
    return {
        "value": label,
        "style": "edgeStyle=elbowEdgeStyle;endArrow=block;endFill=1;",
        "edge": "1",
        "source": src_id,
        "target": tgt_id
    }


def build_reply_message(label: str, src_id: str, tgt_id: str) -> dict:
    """Build a reply message edge returning from callee to caller.

    Args:
        label: Return value or message label.
        src_id: Source (replying) lifeline mxCell id.
        tgt_id: Target (original caller) lifeline mxCell id.

    Returns:
        Dictionary with mxCell edge attributes for the reply message.
    """
    return {
        "value": label,
        "style": "edgeStyle=elbowEdgeStyle;dashed=1;endArrow=open;endFill=0;",
        "edge": "1",
        "source": src_id,
        "target": tgt_id
    }


def build_combined_fragment(operator: str, x: int, y: int,
                            width: int, height: int) -> dict:
    """Build a combined fragment frame cell for the given interaction operator.

    Args:
        operator: InteractionOperatorKind literal (e.g., alt, loop(1,5), par).
        x: Left edge position in pixels.
        y: Top edge position in pixels.
        width: Frame width in pixels.
        height: Frame height in pixels.

    Returns:
        Dictionary with mxCell vertex attributes for the combined fragment.
    """
    return {
        "value": operator,
        "style": "shape=mxgraph.uml.frame;whiteSpace=wrap;html=1;",
        "vertex": "1",
        "x": x, "y": y, "width": width, "height": height
    }
```

## 5. Deep Mathematical Foundations

### M1: MSC Formal Algebra

A Message Sequence Chart is defined as m = (L, M, <) where L is the finite set of lifelines, M is the set of message events (each message msg has send/receive pair: send(msg, l_i) and recv(msg, l_j) with l_i and l_j in L), and < is the partial happens-before order (irreflexive, transitive, antisymmetric).

Two mandatory axioms define the partial order:

Causal ordering axiom: For every message msg, send(msg, l_i) < recv(msg, l_j). Reception cannot precede transmission.

Lifeline ordering axiom: For each lifeline l_i, the restriction of < to events on l_i is a total order. Each process executes its events sequentially.

A trace of m is any linearization e_1, e_2, ..., e_n consistent with <. The trace language T(m) is the set of all valid traces. Conformance: an execution is correct iff its event sequence belongs to T(m).

Worked example -- 3-lifeline ping-pong with lifelines A, B, C:

Messages: req (A to B), fwd (B to C), resp (C to B), rpl (B to A).

Causal constraints: send_req < recv_req; send_fwd < recv_fwd; send_resp < recv_resp; send_rpl < recv_rpl.

Lifeline B sequential constraints: recv_req < send_fwd (B receives req before forwarding) and recv_resp < send_rpl (B receives resp before replying). Lifeline C: recv_fwd < send_resp.

Combined total causal chain: send_req < recv_req < send_fwd < recv_fwd < send_resp < recv_resp < send_rpl < recv_rpl.

This is the unique valid linearization for this fully synchronous chain. Any reordering violating a causal or lifeline constraint is excluded from T(m).

### M2: Lifeline Activation Interval

An activation a = [t_start, t_end] is a closed time interval on lifeline l. For synchronous calls: t_start = time of recv(call) on the callee; t_end = time of send(reply) from the callee.

Nesting predicate: a_1 is nested within a_2 iff t_start(a_2) <= t_start(a_1) and t_end(a_1) <= t_end(a_2).

Activation stack: each synchCall creates a new activation starting at recv; each reply terminates the innermost activation at send. Maximum nesting depth equals the maximum call stack depth.

Worked example -- recursive activation on lifeline F called from A and calling itself:

Events on F: r1 = recv outer call (activation a_outer starts), s2 = send inner self-call, r2 = recv inner self-call (activation a_inner starts), s3 = send inner reply (a_inner ends), r3 = recv inner reply, s4 = send outer reply (a_outer ends).

Activations: a_outer = [r1, s4]; a_inner = [r2, s3].

Nesting check: t_start(a_outer) = r1 <= r2 = t_start(a_inner), and t_end(a_inner) = s3 <= s4 = t_end(a_outer). Therefore a_inner is nested within a_outer. The diagram shows the inner activation box drawn inside the outer activation box on lifeline F.

### M3: Combined Fragment Semantics via CSP

UML CombinedFragments map to CSP (Communicating Sequential Processes) operators over trace sets. Let traces(F) denote the set of valid event sequences for fragment F.

All twelve InteractionOperatorKind CSP mappings:

alt(f1, f2): traces(f1) UNION traces(f2). External choice; exactly one branch executes per guard evaluation.

par(f1, f2): symmetric interleaving product. All interleavings preserving per-lifeline ordering within each operand.

seq(f1, f2): sequential composition preserving per-lifeline order in each operand but relaxing cross-lifeline ordering between operands.

strict(f1, f2): total separation -- all events in f1 precede all events in f2 across all lifelines.

loop(f, n, m): traces(f)^n concatenated with (traces(f) UNION {epsilon})^(m-n). Between n and m full executions.

neg(f): marks traces(f) as invalid; T_enclosing becomes T_enclosing SETMINUS traces(f).

opt(f): traces(f) UNION {epsilon}. Equivalent to alt(f, skip).

critical(f): atomic block; no events from surrounding par operands may interleave within f.

ignore({I}): project traces of f onto events not involving messages in set I.

consider({I}): restrict traces of f to events involving only messages in set I.

assert(f): traces(f) are mandatory; executions outside traces(f) are error conditions.

break(f): execute traces(f) then abandon continuation of the enclosing combined fragment.

Worked example -- alt inside par:

Fragment: par( alt(f_a, f_b) on L1, f_c on L2 ).

CSP expression: (traces(f_a) UNION traces(f_b)) ||| traces(f_c).

Expansion: {t_a interleaved with t_c : t_a in traces(f_a), t_c in traces(f_c)} UNION {t_b interleaved with t_c : t_b in traces(f_b), t_c in traces(f_c)}.

Interpretation: all interleavings of f_c with either f_a or f_b (mutually exclusive choice), while preserving per-lifeline ordering within each selected sub-fragment.

### M4: Duration Constraint Satisfiability

A duration constraint set DC = {(e_i, e_j, [l_ij, u_ij])} specifies l_ij <= time(e_j) - time(e_i) <= u_ij for each triple.

Simple Temporal Network (STN) formulation: directed graph G = (V, E_c) where V = set of events. Each constraint (e_i, e_j, [l, u]) adds:
- Forward edge e_i -> e_j with weight u (upper bound on the delay)
- Backward edge e_j -> e_i with weight -l (negated lower bound)

Satisfiability condition: The STN is satisfiable iff G contains no negative-weight cycle. Bellman-Ford detects negative cycles in O(|V| * |E_c|) time.

Worked example -- 3-event system with events e0 (request sent), e1 (request received), e2 (reply sent):

Constraints: (e0, e1, [5, 20]) for network latency 5ms to 20ms; (e1, e2, [10, 100]) for server processing 10ms to 100ms; (e0, e2, [30, 200]) for end-to-end round-trip 30ms to 200ms.

STN edges: e0->e1 weight 20; e1->e0 weight -5; e1->e2 weight 100; e2->e1 weight -10; e0->e2 weight 200; e2->e0 weight -30.

Cycle weight checks: cycle e0->e1->e0 = 20 + (-5) = 15 > 0; cycle e1->e2->e1 = 100 + (-10) = 90 > 0; cycle e0->e2->e0 = 200 + (-30) = 170 > 0. No negative cycles -- satisfiable.

Valid time assignment: time(e0) = 0, time(e1) = 10, time(e2) = 50. Verification: (e0,e1): 10 in [5,20] YES; (e1,e2): 40 in [10,100] YES; (e0,e2): 50 in [30,200] YES.

### M5: Sequence to State Machine Synthesis

Algorithm: convert a UML sequence diagram to a per-lifeline Behavioral State Machine.

Step 1: For each lifeline l_i, extract E_i = (e_1, ..., e_n) as the total ordering of events on l_i from the partial order < restricted to l_i.

Step 2: Create states {q_0, q_1, ..., q_n}. q_0 is the initial state (preceded by an InitialPseudostate). q_n is the final state.

Step 3: For each event e_k in E_i, create Transition q_{k-1} -> q_k. If e_k = send(msg): Transition trigger is completion + effect = SendSignalAction(msg). If e_k = recv(msg): Transition trigger = AcceptEventAction triggered by Signal(msg).

Step 4: For alt fragments on lifeline l_i: introduce a ChoicePseudostate c at the branch point. Each InteractionOperand guard g_i becomes a guarded outgoing Transition from c.

Step 5: For loop(n, m) fragments: introduce integer variable iteration_count in context. Self-loop Transition with guard [iteration_count < m] and increment effect. Forward Transition with guard [iteration_count >= n] to post-loop state.

Worked example -- 2-lifeline with alt, lifelines Client and Server:

Sequence: Client sends req(); Server receives req(); alt([success]: Server sends ok(); [else]: Server sends err()); Client receives response.

Client state machine: q0 --(send req, effect SendSignalAction(req))--> q1 --(recv ok OR recv err, AcceptEventAction)--> q2.

Server state machine: q0 --(recv req, AcceptEventAction(req))--> q1_choice (ChoicePseudostate); q1_choice --[success]--> q2a --(send ok, SendSignalAction(ok))--> q3; q1_choice --[else]--> q2b --(send err, SendSignalAction(err))--> q3.

The ChoicePseudostate on Server corresponds exactly to the alt CombinedFragment. Guards [success] and [else] become Constraint predicates on the outgoing Transitions from the choice pseudostate.

### M6: k-Path Scenario Coverage

A k-path is a sequence of k consecutive messages appearing in execution order in a sequence diagram. k-path analysis is a structural adequacy criterion for interaction-based testing.

For a linear message sequence of length |M|: total k-paths = max(0, |M| - k + 1).

For a diagram with alt branching: enumerate all execution paths. For path p of length len(p), count k-paths(p) = max(0, len(p) - k + 1). Total distinct k-paths = size of the union of k-path sets across all paths.

Coverage(k, S) = |k-paths observed in test suite S| / |total distinct k-paths in diagram|.

Recommended thresholds: k=1 coverage = 1.0 means every message exercised at least once (minimum). k=2 coverage >= 0.90 catches message-ordering bugs. k=3 coverage >= 0.80 catches three-step protocol state bugs.

Worked example -- 5-message diagram with one alt containing branches A and B:

Messages: m1, m2. alt([cond]: m3a, [else]: m3b). m4, m5.

Path A (m3a branch): m1, m2, m3a, m4, m5 (length 5). 2-paths: (m1,m2), (m2,m3a), (m3a,m4), (m4,m5). Count = 4.

Path B (m3b branch): m1, m2, m3b, m4, m5 (length 5). 2-paths: (m1,m2), (m2,m3b), (m3b,m4), (m4,m5). Count = 4.

Distinct 2-paths: {(m1,m2), (m2,m3a), (m3a,m4), (m4,m5), (m2,m3b), (m3b,m4)} = 6 unique pairs.

Test suite covering only Path A: 4/6 = 66.7% 2-path coverage. Adding Path B test: 6/6 = 100%. Both branches must be tested to meet the k=2 threshold of 90%.

## 6. Anti-Patterns to Avoid

1. **Modeling a reply as happening before or concurrently with its own request**: M1's causal ordering axiom requires send(msg, l_i) < recv(msg, l_j) for every message — reception cannot precede transmission. A diagram or generated trace where a reply's receive event is placed before its corresponding request's send event violates this mandatory axiom, not just a stylistic convention.

2. **Drawing two overlapping (non-nested, non-disjoint) activation boxes on the same lifeline**: M2's activation intervals must be either fully nested (a_1 within a_2 iff t_start(a_2) ≤ t_start(a_1) and t_end(a_1) ≤ t_end(a_2)) or fully disjoint — a single-threaded lifeline's call stack cannot produce partially-overlapping activations. An activation diagram showing partial overlap describes an impossible execution on a sequential lifeline.

3. **Using `seq` when `strict` total ordering across all lifelines was actually required**: M3's CSP mapping distinguishes `seq(f1,f2)` (relaxes cross-lifeline ordering between operands, only preserves per-lifeline order) from `strict(f1,f2)` (total separation — every event in f1 precedes every event in f2 across ALL lifelines). Using the weaker `seq` semantics for a genuinely strict phase barrier permits interleavings the real system forbids.

4. **Treating `neg` as marking traces as forbidden for the whole diagram instead of relative to the enclosing fragment**: M3 defines neg(f) as `T_enclosing SETMINUS traces(f)` — it removes f's traces from the ENCLOSING fragment's trace set, not from some global trace universe. Applying `neg` without correctly scoping it to its enclosing context produces an incorrectly-restricted (or unrestricted) overall trace set.

5. **Declaring a duration-constrained interaction satisfiable without running the negative-cycle check**: M4's STN satisfiability condition is precise — the constraint graph is satisfiable iff it contains NO negative-weight cycle, checked via Bellman-Ford in O(|V|·|E_c|). Eyeballing individual duration constraints as "each looks reasonable" without computing cycle sums across the full constraint graph can miss a genuinely infeasible combination (e.g. a round-trip upper bound tighter than the sum of its component lower bounds).

6. **Converting an alt fragment to a state machine without introducing an explicit ChoicePseudostate**: M5's synthesis algorithm (Step 4) requires each alt fragment's branch point to become a ChoicePseudostate with each InteractionOperand's guard becoming a guarded outgoing Transition. Collapsing the branch into an implicit unlabeled fork in the synthesized state machine loses the guard conditions that determine which branch actually fires.

7. **Synthesizing a loop(n,m) fragment as an unbounded self-loop without the iteration_count guard**: M5's Step 5 requires an explicit iteration_count variable with a guarded self-transition `[iteration_count < m]` and a forward transition guarded `[iteration_count >= n]`. A synthesized state machine that loops indefinitely (or exits after any single pass) fails to preserve the original loop fragment's declared minimum and maximum bounds.

8. **Measuring k-path coverage with k=1 alone and calling test coverage adequate**: M6's recommended thresholds are tiered by what each k actually catches — k=1 (every message exercised) is the bare minimum, k=2 ≥ 0.90 catches message-ordering bugs, and k=3 ≥ 0.80 catches three-step protocol state bugs. A test suite achieving 100% k=1 coverage can still miss real ordering and protocol-state defects that only k=2/k=3 analysis would surface.

9. **Computing total distinct k-paths as the sum across branches instead of the union**: M6's worked example computes distinct 2-paths as the UNION of each path's k-path set (6 unique pairs from two 4-count paths, because (m1,m2) and (m4,m5) are shared between both alt branches) — summing per-path counts (4+4=8) overcounts by double-counting the shared k-paths common to multiple branches.

10. **Assuming testing only one alt branch achieves full k-path coverage**: M6's worked example shows testing only Path A yields 4/6 = 66.7% 2-path coverage — the branch-specific k-paths ((m2,m3a),(m3a,m4) for Path A vs (m2,m3b),(m3b,m4) for Path B) are NOT covered by the other branch's test. Every alt branch must be exercised to reach the full distinct k-path set, not just the "primary" or most commonly executed one.

---

## 7. India Layer

NPCI UPI: The NPCI UPI Interoperability Specification uses sequence diagrams as the canonical format for payment API flow documentation. The six-lifeline UPI payment sequence is Customer -> UPI App -> PSP -> NPCI Switch -> Beneficiary PSP -> Beneficiary Bank. All PSP integrators and third-party application providers must document API interaction flows using sequence diagrams before live certification.

SEBI Trading Systems: SEBI regulatory RFPs for stock exchange and broker technology systems mandate sequence diagrams for order matching and settlement API flows. BSE and NSE integration documents use sequence diagrams for the full order lifecycle covering placement, matching, confirmation, settlement, and clearing.

ISRO Satellite Communication: ISRO uses sequence diagrams for ground-station to satellite communication protocols on PSLV and Gaganyaan missions. Eclipse UML2 with XMI export is the standard toolchain. Key sequences: telecommand upload (ground to satellite), telemetry downlink (satellite to ground), ranging protocol (ground-satellite-ground round-trip).

NASSCOM and STQC: NASSCOM interoperability certification frameworks use sequence diagrams for API compliance test scenario specification. STQC accepts UML sequence diagrams as test specification artifacts in government software tenders and CMMI appraisals under NIC-SSDLC v2.0.

BIS Applicability: IS/ISO 19505-2:2012 (BIS adoption of UML 2.5.1 Superstructure) governs sequence diagram syntax. MeitY e-governance projects follow STQC guidelines mandating sequence diagrams for API-level documentation in government IT projects above 5 KLOC.

## 8. Response Rules

1. Label every message with its MessageSort through arrow style and message signature notation.
2. Draw activation boxes on synchronous call receivers; omit for asynchronous signals.
3. Show guards on all alt operands; use [else] as the final guard for the unconditional branch.
4. Specify loop bounds explicitly as loop(n, m); never write a loop fragment without bounds.
5. Use ref frames for InteractionUse to reference named interactions rather than copying content inline.
6. Annotate duration constraints as brace expressions spanning the two constrained events.
7. Show formal and actual gates explicitly when designing Interactions for reuse via InteractionUse.
8. Apply NPCI, SEBI, or ISRO India context when the domain involves payment, trading, or embedded systems.
9. Delegate STN Bellman-Ford satisfiability proofs to uml-diagram-mathematics-expert.

## 9. What Not to Do

- Never show a reply message without a matching preceding synchCall on the same pair of lifelines.
- Never use asynchCall when the scenario requires a return value; pair synchCall with reply.
- Never omit guards on alt operands; guards are mandatory for specifying which branch executes.
- Never confuse seq (relaxed cross-lifeline ordering) with strict (total cross-lifeline ordering).
- Never represent parallel concurrent execution with sequential messages; use par combined fragment.
- Never use neg without pairing with assert to form a complete prohibited-trace specification.
- Never place createMessage targeting a lifeline that is already active in the diagram.
- Never omit lifeline header boxes; every participant must have a typed header.

## 10. Output Expectations

Sequence diagram output includes: all lifelines with typed headers, message arrows with MessageSort indicated by arrow style and label, combined fragments with operator labels and guards, activation boxes on synchronous call receivers, and duration or time constraint annotations where specified.

For mxGraph XML: shape=mxgraph.uml.lifeline for headers, shape=mxgraph.uml.activation for activation boxes, shape=mxgraph.uml.frame for combined fragments, edgeStyle=elbowEdgeStyle;endArrow=block;endFill=1 for synchCall, dashed=1;endArrow=open for reply.

For textual output: PlantUML or Mermaid sequenceDiagram syntax with participant declarations, arrow type indicators, and activate/deactivate blocks.

For test adequacy: k-path counts for k=1 and k=2 with coverage percentage calculations.

## 11. Skill Scope

Covers: UML 2.5.1 sequence diagram notation, all six MessageSort literals, all twelve InteractionOperatorKind combined fragments, MSC formal algebra (M1), activation interval nesting (M2), CSP trace semantics (M3), STN duration constraint satisfiability (M4), sequence-to-state-machine synthesis (M5), k-path coverage (M6), gate semantics, interaction use, and NPCI/SEBI/ISRO India layer.

Does not cover: mxGraph XML generation mechanics (see drawio-xml-generation-core), Mermaid syntax (see mermaid-diagram-generation-core), full STN Bellman-Ford proof (delegate to uml-diagram-mathematics-expert), timing diagram notation (see uml-timing-diagram-core).

## Version

1.1.0 -- Added Section 6 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India Layer through Skill Scope renumbered §7-11.
1.0.0 -- Domain 46 UML and Diagram Engineering initial release.