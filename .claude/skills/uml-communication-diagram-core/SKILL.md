---
name: uml-communication-diagram-core
description: "Generates UML 2.5.1 communication diagrams (formerly collaboration diagrams) showing object networks with sequenced messages. Use when visualizing object interaction topology, refactoring sequence diagrams to show object network structure, documenting GoF pattern interactions, or analyzing message routing in distributed systems. Keywords: communication diagram UML, collaboration diagram, object network interaction, sequenced message UML, GoF pattern collaboration, object relationship message flow, numbered message sequence, interaction network diagram"
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/uml-communication-diagram-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# UML Communication Diagram Core

## Description

Generates complete UML 2.5.1 communication diagrams (formerly called collaboration diagrams) showing object networks with labeled, sequenced messages on directed links. Semantically equivalent to sequence diagrams -- both express the same Interaction metamodel -- but communication diagrams emphasize topology (which objects communicate) rather than temporal ordering. Use when visualizing object interaction topology, refactoring sequence diagrams to show object network structure, documenting GoF pattern interactions, or analyzing message routing in distributed systems.

## 1. Core Metaclasses and Notation

### 1.1 Metamodel Basis

Communication diagrams share the same Interaction metamodel as sequence diagrams (UML 2.5.1 Chapter 17.7). Key metaclasses:

- Interaction: BehavioredClassifier; owns Lifelines, Messages, and OccurrenceSpecifications
- Lifeline: displayed as a rectangle (named object box, not a dashed line as in sequence diagrams)
- Message: directed arrow on a Link between two Lifelines, labeled with a SequenceExpression
- Link: association instance between two object nodes; can carry multiple messages (in both directions)
- SequenceExpression: dot-decimal notation encoding the message ordering

### 1.2 Lifeline Notation

In a communication diagram, each Lifeline is drawn as a labeled rectangle (not a dashed vertical line). Label format: objectName : ClassName (same as sequence diagram header). Objects may be anonymous (: ClassName) or fully named.

### 1.3 Link Notation

A Link is drawn as a plain solid line between two object rectangles. Multiple messages may travel along a single link in either direction. The link does not have an arrowhead; arrows belong to the individual message labels.

### 1.4 Message Label Format

Each message label on a link consists of a SequenceExpression followed by a colon and the message name:

  sequenceExpression : messageName(parameters)

Example: 1.2.1 : getValue() means the first sub-message of the second sub-message of the first top-level message.

### 1.5 Object Node Layout

Objects are placed as nodes in a free-layout graph (no mandatory vertical axis). Layout typically uses force-directed placement (Kamada-Kawai) to cluster closely communicating objects. Links are straight lines connecting communicating objects.

## 2. Sequence Expression Grammar

### 2.1 Formal BNF Grammar

The SequenceExpression grammar (UML 2.5.1 Chapter 17.7):

```
seq_expr   ::= level ('.' level)* modifier? ':' msg_name
level      ::= integer | name
modifier   ::= '*' | '[' guard ']' | '*[' guard ']'
msg_name   ::= identifier '(' params? ')'
params     ::= param (',' param)*
```

### 2.2 Sequence Number Patterns

| Pattern | Meaning |
|---------|---------|
| 1 : msg() | Top-level message 1 |
| 1.1 : msg() | First sub-message of message 1 |
| 1.2.3 : msg() | Third sub-message of second sub-message of message 1 |
| 2* : msg() | Message 2 repeated (iteration) |
| 3[i=1..n] : msg() | Message 3 iterated with index variable i |
| 1a : msg() | Concurrent message 1a (parallel to 1b, 1c, ...) |
| 1b : msg() | Concurrent message 1b (executes in parallel with 1a) |

### 2.3 Worked Sequence Expression Tree

Scenario: A top-level call (message 1) causes two sub-calls (1.1 and 1.2), and 1.2 causes a sub-sub-call (1.2.1).

Tree representation:
```
1 : start()
  1.1 : init()
  1.2 : process()
    1.2.1 : compute()
```

Meaning: start() (message 1) triggers init() and process() as nested calls. process() further triggers compute() as its first sub-call. The decimal nesting mirrors the call stack depth.

## 3. Semantic Equivalence to Sequence Diagrams

### 3.1 Bijection Overview

Communication diagrams and sequence diagrams are semantically isomorphic: both express the same Interaction model. The conversion algorithm (communication to sequence):

Step 1: Parse the SequenceExpression tree T from all message labels on all links.

Step 2: Topological sort T by sequence number to produce a total linear ordering of messages.

Step 3: Map each tree node (message) to one OccurrenceSpecification pair (send, recv) in the sequence diagram.

Step 4: Parallel letter suffixes (1a, 1b) map to par CombinedFragment in the sequence diagram.

Step 5: Guard notation (message[guard]) maps to alt or opt CombinedFragment in the sequence diagram.

### 3.2 Complementary Emphasis

| Aspect | Sequence Diagram | Communication Diagram |
|--------|-----------------|----------------------|
| Primary emphasis | Temporal ordering | Object network topology |
| Layout axis | Vertical (time) | Free graph layout |
| Message ordering | Explicit by vertical position | Encoded in SequenceExpression |
| Object relationships | Implicit from message arrows | Explicit as named links |
| Best for | Protocol flow documentation | Object collaboration patterns |

## 4. Python Generation Pattern

```python
def build_communication_object(name: str, classifier: str,
                               x: int, y: int) -> dict:
    """Build an object node cell for a communication diagram in mxGraph format.

    Args:
        name: Instance name (e.g., subject).
        classifier: Classifier name (e.g., ConcreteSubject).
        x: Horizontal position in pixels.
        y: Vertical position in pixels.

    Returns:
        Dictionary with mxCell vertex attributes for the object rectangle.
    """
    label = name + " : " + classifier
    return {
        "value": label,
        "style": "rounded=0;whiteSpace=wrap;html=1;fontStyle=4;",
        "vertex": "1",
        "x": x, "y": y, "width": 140, "height": 40
    }


def build_communication_link(src_id: str, tgt_id: str) -> dict:
    """Build a plain link (association instance) between two object nodes.

    Args:
        src_id: Source object mxCell id.
        tgt_id: Target object mxCell id.

    Returns:
        Dictionary with mxCell edge attributes for the undirected link.
    """
    return {
        "style": "endArrow=none;html=1;",
        "edge": "1",
        "source": src_id,
        "target": tgt_id
    }


def build_communication_message(seq_expr: str, msg_name: str,
                                src_id: str, tgt_id: str) -> dict:
    """Build a directed message label on a communication diagram link.

    Args:
        seq_expr: SequenceExpression string (e.g., 1.2 or 1a).
        msg_name: Message name with parameters (e.g., notify(event)).
        src_id: Source object mxCell id.
        tgt_id: Target object mxCell id.

    Returns:
        Dictionary with mxCell edge attributes for the sequenced message.
    """
    label = seq_expr + " : " + msg_name
    return {
        "value": label,
        "style": "edgeStyle=orthogonalEdgeStyle;endArrow=open;endFill=0;",
        "edge": "1",
        "source": src_id,
        "target": tgt_id
    }
```

## 5. Deep Mathematical Foundations

### M1: Collaboration Graph

A communication diagram is a labeled directed multigraph G = (L, E) where:
- L = finite set of lifeline nodes (object instances, each labeled objectName : ClassName)
- E = set of labeled directed edges; each edge e = (src, dst, label) where label = SequenceExpression : messageName

Unlike sequence diagrams, G can have cycles (Object A can send to B, B can send back to A). Multiple messages between the same pair of objects appear as multiple parallel edges on the same undirected link, distinguished by their SequenceExpression labels.

Worked example -- Observer pattern notification collaboration graph:

Objects: {Subject, ObserverA, ObserverB}.

Links: Subject--ObserverA (link 1), Subject--ObserverB (link 2).

Messages:
- On link 1: 1 : attach(obs) (ObserverA -> Subject), 2 : notify() (Subject -> ObserverA), 2.1 : update() (Subject -> ObserverA)
- On link 2: 2 : notify() (Subject -> ObserverB), 2.1 : update() (Subject -> ObserverB)

Graph G has 3 nodes and 2 undirected links, each carrying bidirectional messages. The parallel messages 2 and 2.1 on each link represent the notification broadcast. Message 1 flows opposite to messages 2 and 2.1 on link 1, demonstrating the multigraph nature.

### M2: Sequence Expression Grammar and Partial Order

The SequenceExpression grammar (BNF):

  seq_expr ::= level ('.' level)* modifier? ':' msg_name
  level ::= integer | name
  modifier ::= star | '[' guard ']' | star '[' guard ']'

Ordering relation derived from SequenceExpressions: message m1 precedes m2 iff:
- The integer sequence of m1 is lexicographically less than that of m2 when treating each dot-separated field as an integer, OR
- m1 is an ancestor of m2 in the sequence tree (m2 is a sub-message of m1)

This ordering relation defines a partial order equivalent to the OccurrenceSpecification ordering in the corresponding sequence diagram.

Worked example -- sequence expression tree for a 5-message scenario:

Messages: 1 : login(), 1.1 : authenticate(), 1.1.1 : hashPassword(), 1.2 : loadProfile(), 2 : display().

Tree structure: 1 (login) is the root of the first top-level subtree. 1.1 (authenticate) and 1.2 (loadProfile) are children of 1. 1.1.1 (hashPassword) is a child of 1.1. 2 (display) is a separate top-level message after 1 completes.

Ordering: 1 < 1.1 < 1.1.1 < (1.1.1 complete) < 1.2 < (1.2 complete) < (1 complete) < 2. The topological sort of this tree gives the equivalent sequence diagram ordering.

### M3: Bijection Proof (Communication to Sequence)

Theorem: For any communication diagram D with consistent SequenceExpressions, there exists a unique equivalent sequence diagram S, and vice versa (modulo graph layout information).

Construction algorithm (communication D to sequence S):

Step 1: Parse SequenceExpression strings into a forest T of trees (one tree per top-level message).

Step 2: Topological sort T: for each node n in T, n is ordered after its parent and before all later siblings. The sort produces a total ordering of messages consistent with the partial order.

Step 3: For each message in topological order, create one send event and one recv event in the sequence diagram. Place send on the source lifeline dashed line, recv on the target lifeline dashed line.

Step 4: Parallel messages (letter suffix 1a, 1b) map to a par CombinedFragment grouping those messages. Guard notation [cond] maps to alt or opt CombinedFragment.

Step 5: Links between objects map to lifeline pairs in the sequence diagram; link labels map to message arrows between those lifeline pairs.

Bijection holds iff: each SequenceExpression in D is syntactically valid, no two messages at the same nesting level have the same sequence number without a letter suffix, and parallel branches are consistently labeled.

Worked example -- bijection for a 4-message scenario:

Communication messages: 1 : req(), 1.1 : fetch(id), 1.2 : format(data), 2 : respond().

Equivalent sequence diagram events in order: send req(), recv req(), send fetch(id), recv fetch(id), send format(data), recv format(data), send respond(), recv respond().

The 4-node message tree maps to 8 OccurrenceSpecifications in the sequence diagram, preserving the causal ordering derived from the SequenceExpression hierarchy.

### M4: Message Guard Predicate Evaluation

A message labeled seq_expr[guard] : msg_name carries a guard predicate on its execution. Evaluation semantics:

If guard = true in the current context: message msg_name is sent along the link.
If guard = false: message msg_name is skipped (the branch is not taken).

Multiple messages from the same source node with the same base sequence number but different guards correspond to an alt CombinedFragment in the equivalent sequence diagram (exactly one guard must evaluate to true).

Optional message: a single message with a guard and no else-branch corresponds to an opt CombinedFragment.

Worked example -- guard evaluation on a 3-message scenario:

Messages on a link from Controller to View: 2[data != null] : display(data), 2[data == null] : showEmpty().

These two messages share base sequence number 2 with complementary guards. At runtime, exactly one executes. In the equivalent sequence diagram, this maps to alt([data != null]: display(data), [else]: showEmpty()) CombinedFragment.

At evaluation: if the data object is non-null, display(data) is sent. If data is null, showEmpty() is sent. The guards are evaluated at the source object (Controller) at the point in execution when message 2 would be sent.

### M5: Concurrent Message Interleaving

Messages with parallel sequence number suffixes (1a, 1b, 1c, ...) are concurrent; they execute in some unspecified interleaved order while preserving the constraint that all must complete before any message at the next higher sequence number begins.

For k concurrent messages at the same nesting level (1a, 1b, ..., 1k), the number of valid interleavings is k! (k factorial) because the messages form a symmetric group of permutations.

For multiple groups of concurrent messages with sizes k_1, k_2, ..., k_g at different nesting levels, the total valid interleavings are the product of k_i! over all groups i, provided no cross-group ordering constraints exist.

Worked example -- 2 parallel message groups:

Group 1 (concurrent at level 2): messages 2a : fetchUser(), 2b : fetchRoles(). These are two concurrent database fetches.

Group 2 (sequential after group 1, at level 3): message 3 : merge(user, roles).

Valid interleavings of group 1: {(fetchUser then fetchRoles), (fetchRoles then fetchUser)} = 2! = 2 interleavings.

Group 2 has only one message so 1! = 1 interleaving. Total valid executions = 2 x 1 = 2.

In the equivalent sequence diagram: messages 2a and 2b appear inside a par CombinedFragment. Message 3 appears in a seq operand after the par fragment completes.

### M6: Communication Pattern Topology Analysis

The collaboration graph G = (L, E) supports structural topology analysis to identify architectural patterns.

Betweenness centrality of node l: BC(l) = sum over all s != t != l of sigma_st(l) / sigma_st, divided by ((n-1)(n-2)/2), where sigma_st = total number of shortest paths from s to t, sigma_st(l) = number of those paths passing through l, and n = |L|.

Topology patterns:

Hub-and-spoke: one central node has BC close to 1.0; all other nodes communicate primarily through the hub. Indicator of a Mediator or Facade architectural pattern.

Chain: linear topology; BC forms a gradient from endpoints (BC near 0) to middle nodes (BC near 1.0/(n-1)). Indicator of a pipeline or chain-of-responsibility pattern.

Ring: cyclic topology; uniform BC across all nodes. Indicator of a circular dependency or ring-based routing.

Fully connected: BC near 0 for all nodes (all have direct connections). Indicator of high coupling; may need refactoring.

Worked example -- betweenness centrality for a 5-node collaboration:

Objects: {Client, Facade, ServiceA, ServiceB, ServiceC}. Links: Client--Facade, Facade--ServiceA, Facade--ServiceB, Facade--ServiceC.

Shortest paths: Client to ServiceA: Client -> Facade -> ServiceA (only path, through Facade). Similarly for ServiceB and ServiceC. ServiceA to ServiceB: ServiceA -> Facade -> ServiceB (through Facade).

BC(Facade): Facade lies on all 6 inter-service and client-to-service shortest paths: paths Client->ServiceA, Client->ServiceB, Client->ServiceC, ServiceA->ServiceB, ServiceA->ServiceC, ServiceB->ServiceC = 6 paths. Total possible pairs excluding Facade = C(4,2) = 6. BC(Facade) = 6/6 / (4*3/2) = 1.0 / 6. Wait -- normalized: BC(Facade) = sum(sigma_st(Facade)/sigma_st) / ((n-1)(n-2)/2) = 6/((4)(3)/2) = 6/6 = 1.0.

BC = 1.0 for Facade confirms the hub-and-spoke topology with Facade as the sole intermediary. This matches the Facade GoF pattern structure.

## 6. Anti-Patterns to Avoid

1. **Treating a communication diagram as a simple graph instead of a labeled directed multigraph**: M1 is explicit that G can have cycles and multiple parallel edges between the same pair of objects — the Observer-pattern worked example shows messages 1, 2, and 2.1 all on the same link but flowing in different directions and at different sequence positions. Collapsing multiple distinct messages between the same object pair into a single edge loses the SequenceExpression labels that distinguish them.

2. **Assigning the same sequence number to sibling messages without a letter suffix**: M3's bijection condition requires that "no two messages at the same nesting level have the same sequence number without a letter suffix" — violating this breaks the bijection's uniqueness guarantee between the communication diagram and its equivalent sequence diagram, since the topological sort in M2/M3 depends on unambiguous ordering.

3. **Assuming the communication-to-sequence bijection holds for any diagram, without checking its three conditions**: M3's bijection is conditional — it holds "iff each SequenceExpression is syntactically valid, no two same-level messages share a sequence number without a letter suffix, and parallel branches are consistently labeled." A diagram violating any one of these three conditions doesn't have a well-defined equivalent sequence diagram, even though it might still render.

4. **Modeling two guard-branches on the same base sequence number without complementary (mutually exclusive) guards**: M4's alt-fragment correspondence requires the guards to be complementary so exactly one evaluates true. Two guards on the same sequence number that can both be false (or both true) simultaneously don't correspond to a valid alt CombinedFragment — they produce an undefined branch outcome the formalism doesn't cover.

5. **Modeling an optional message's guard without recognizing it maps to `opt`, not `alt`**: M4 distinguishes a guarded message with NO else-branch (maps to `opt` — execute or skip) from complementary guarded messages (maps to `alt` — exactly one executes). Treating a single-guard optional message as if it always executes ignores that the guard can legitimately evaluate false and skip the message entirely.

6. **Computing the number of valid interleavings for concurrent messages by adding k_i instead of multiplying k_i!**: M5's formula for the total valid interleavings across multiple concurrent groups is the PRODUCT of k_i! over all groups (provided no cross-group ordering constraints), not a sum. The worked example's 2 groups (sizes 2 and 1) give 2!×1!=2 total valid executions — summing instead of multiplying (or forgetting the factorial) undercounts the actual number of valid execution orderings a test suite would need to cover.

7. **Assuming cross-group ordering constraints don't exist without verifying them**: M5's multiplicative interleaving-count formula explicitly requires "no cross-group ordering constraints" between the groups. If group 2's message actually depends on partial results from group 1 (beyond simple sequencing), the naive product of factorials overcounts valid interleavings that violate the real dependency.

8. **Computing betweenness centrality without the normalization by (n-1)(n-2)/2**: M6's BC(l) formula divides the sum of shortest-path fractions by the total number of possible node pairs excluding l. Reporting the raw unnormalized path-fraction sum as "betweenness centrality" produces a value that isn't comparable across collaborations of different sizes and can't be checked against the "BC close to 1.0" hub-and-spoke threshold.

9. **Misreading a chain topology's BC gradient as evidence of a hub-and-spoke pattern**: M6 distinguishes hub-and-spoke (one node near BC=1.0, all others near 0) from chain topology (a gradient from endpoints near 0 to middle nodes near 1.0/(n-1), never reaching a single dominant 1.0 value). Flagging any node with elevated (but not near-1.0) betweenness as "the hub" misclassifies a pipeline/chain-of-responsibility architecture as a Mediator/Facade one.

10. **Interpreting low betweenness centrality across all nodes as "healthy" without checking whether it indicates full connectivity/high coupling**: M6 states BC near 0 for ALL nodes indicates a fully-connected topology with high coupling that may need refactoring — this is the opposite interpretation from a single node's low BC in a hub topology (which would just mean "not the hub"). The correct read depends on the topology PATTERN across all nodes, not any single node's BC value in isolation.

---

## 7. India Layer

TCS MDAL: TCS Model-Driven Architecture Library (MDAL) uses UML communication diagrams for documenting GoF and enterprise pattern collaborations. Communication diagrams are the standard format for pattern instantiation documentation in TCS architecture reviews.

Infosys RBAP: Infosys Reference Based Architecture Platform (RBAP) uses collaboration diagrams (UML communication diagram format) for documenting architectural pattern interactions. Pattern documentation includes the collaboration graph showing object roles and message sequences.

NASSCOM Certified Architects: The NASSCOM Enterprise Architecture certification program tests candidates on communication diagram reading and writing. NASSCOM SSC/Q0504 (Software Architect, NSQF Level 7) lists UML communication diagrams as a mandatory competency.

STQC Government Tenders: STQC guidelines for government software tenders accept communication diagrams as an alternative to sequence diagrams for API-level documentation, provided SequenceExpressions are consistent with the sequence diagram specification of the same system.

BIS Applicability: IS/ISO 19505-2:2012 (BIS adoption) governs communication diagram syntax. The SequenceExpression grammar and semantic equivalence to sequence diagrams are both specified in the BIS-adopted standard.

## 8. Response Rules

1. Draw all objects as labeled rectangles (objectName : ClassName), not dashed lines.
2. Show links as plain undirected lines between communicating object pairs.
3. Label each message with a complete SequenceExpression : messageName format.
4. Ensure all SequenceExpressions at the same nesting level are sequentially numbered without gaps.
5. Use letter suffixes (1a, 1b) only for genuinely concurrent messages; otherwise use strictly sequential numbers.
6. Show guards in brackets immediately after the sequence number: 2[cond] : msg().
7. Apply betweenness centrality analysis (M6) when architectural coupling assessment is requested.
8. Provide the equivalent sequence diagram when temporal ordering analysis is needed.
9. Apply NASSCOM, STQC, or TCS context when the audience is Indian enterprise architects.

## 9. What Not to Do

- Never use dashed lifeline lines (those are sequence diagram notation); use rectangles for objects.
- Never omit SequenceExpressions on message labels; unlabeled messages cannot be ordered.
- Never assign the same sequence number without a letter suffix to concurrent messages.
- Never place messages directly on the diagram without attaching them to a link between two objects.
- Never show activation boxes (those belong in sequence diagrams, not communication diagrams).
- Never create a diagram with inconsistent sequence numbers (e.g., 1, 1.1, 3 -- missing 2).
- Never confuse the link (undirected, structural) with the message arrow (directed, behavioral).
- Never use communication diagrams for real-time timing requirements; use timing diagrams instead.

## 10. Output Expectations

Communication diagram output includes: all object nodes as labeled rectangles, links as undirected lines between communicating pairs, message labels with SequenceExpressions and names, and guard conditions on conditional messages.

For mxGraph XML: use rounded=0;whiteSpace=wrap;html=1;fontStyle=4 for underlined object names, endArrow=none for links, and edgeStyle=orthogonalEdgeStyle;endArrow=open for sequenced messages.

For topology analysis: betweenness centrality values with pattern identification (hub-and-spoke, chain, ring) when requested.

For equivalence demonstration: the corresponding sequence diagram with the same messages in topological sort order when conversion is requested.

## 11. Skill Scope

Covers: UML 2.5.1 communication diagram notation, collaboration graph formalism (M1), SequenceExpression grammar and partial order (M2), bijection proof to sequence diagrams (M3), guard predicate evaluation (M4), concurrent message interleaving combinatorics (M5), betweenness centrality topology analysis (M6), and TCS/Infosys/NASSCOM India layer.

Does not cover: mxGraph XML generation mechanics (see drawio-xml-generation-core), Mermaid syntax (see mermaid-diagram-generation-core), sequence diagram notation (see uml-sequence-diagram-core), timing constraints (see uml-timing-diagram-core).

## Version

1.1.0 -- Added Section 6 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India Layer through Skill Scope renumbered §7-11.
1.0.0 -- Domain 46 UML and Diagram Engineering initial release.