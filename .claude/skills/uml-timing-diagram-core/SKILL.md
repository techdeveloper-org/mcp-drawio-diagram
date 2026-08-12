---
name: uml-timing-diagram-core
description: "Generates UML 2.5.1 timing diagrams showing state and value changes over time for real-time and embedded systems. Use when documenting embedded system timing requirements, specifying protocol timing constraints, validating WCET compliance, creating hardware-software interface timing specifications, or analyzing timing hazards. Keywords: timing diagram UML, real-time UML timing, state timeline diagram, value lifeline diagram, WCET diagram, timing constraint specification, hardware interface timing, embedded timing UML"
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/uml-timing-diagram-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# UML Timing Diagram Core

## Description

Generates complete UML 2.5.1 timing diagrams showing state and value changes over time for real-time systems, embedded firmware, and hardware-software interface specifications. Covers TimeObservation, DurationObservation, StateInvariant, value lifelines as step functions, duration constraints, timing constraints, setup/hold time specifications, WCET annotations, and clock period notation. Applies OMG UML 2.5.1 Chapter 17.8 metamodel precisely. Use when documenting embedded system timing requirements, specifying protocol timing constraints, validating WCET compliance, creating hardware-software interface timing specifications, or analyzing timing hazards.

## 1. Core Metaclasses and Notation

### 1.1 Timing Diagram Metaclasses

Timing diagrams use a subset of the Interaction metamodel (UML 2.5.1 Chapter 17.8) plus timing-specific elements:

- TimeObservation: marks a point in time on a lifeline; properties: event (NamedElement), firstEvent (Boolean -- true = rising edge, false = falling edge)
- DurationObservation: measures duration between two time points; properties: event[1..2] (two NamedElements), firstEvent[1..2] (Boolean array)
- TimeExpression: ValueSpecification with optional observation references; represents an absolute time value
- Duration: ValueSpecification expressing a duration; may reference one or more DurationObservations
- StateInvariant: Constraint that holds for a duration on a specific Lifeline; shown as a named horizontal bar on the timeline
- OccurrenceSpecification: tick marks at state or value transitions on the timeline
- Lifeline: displayed as a horizontal timeline (time axis runs left to right, states/values on Y-axis)

### 1.2 Diagram Layout

Timing diagram axes:
- X-axis: time (left to right, increasing)
- Y-axis per lifeline: discrete state names (for state lifelines) or continuous/discrete value labels (for value lifelines)

Multiple lifelines are stacked vertically, each with its own Y-axis. A shared X-axis (time ruler) runs across the bottom or top.

### 1.3 State Lifeline Notation

A state lifeline shows discrete state changes over time:
- Horizontal bar at a specific state level = StateInvariant (system is in that state for the duration)
- Vertical line between horizontal bars = state transition (OccurrenceSpecification)
- State names appear as labels on or beside the horizontal bars

### 1.4 Value Lifeline Notation

A value lifeline shows continuous or discrete value changes:
- Step function: horizontal segment at a value level, vertical jump to next value
- For analog values: waveform annotation
- Crossing lines (X pattern): value is undefined or transitioning

### 1.5 Timing Constraint Notation

Duration constraints are shown as:
- Brace span {d} between two OccurrenceSpecifications labeled with the duration variable or range [min, max]
- Double-headed horizontal arrow spanning the constrained duration

Time constraints are shown as:
- Brace annotation {t} at a single OccurrenceSpecification labeled with the absolute time or range

## 2. Hardware Timing Specifications

### 2.1 Clock Period and Frequency

Clock period: T = 1/f where f is the clock frequency in Hz. For a 100 MHz clock: T = 10 ns.

On the timing diagram: the clock lifeline shows a square wave with period T, alternating between HIGH (logic 1) and LOW (logic 0) states. Rise/fall transitions are vertical lines.

### 2.2 Setup and Hold Times

Setup time t_setup: the minimum time interval that data must be stable BEFORE the active clock edge. Violation causes data to be sampled incorrectly (metastability risk).

Hold time t_hold: the minimum time interval that data must remain stable AFTER the active clock edge. Violation causes the flip-flop to lose the captured value.

Notation on timing diagram: annotate t_setup and t_hold as duration constraints relative to the clock edge OccurrenceSpecification.

### 2.3 Propagation Delay

Propagation delay t_pd: time from input signal change to output signal reaching 50% of its final value. Annotated as a duration constraint between the input OccurrenceSpecification and the output OccurrenceSpecification.

### 2.4 Protocol Timing

I2C timing requirements (100kHz standard mode): SCL period = 10us; SCL high time >= 4us; SCL low time >= 4.7us; SDA setup time to SCL rising >= 250ns; SDA hold time from SCL falling >= 0ns. These become DurationConstraints on the SCL and SDA timing diagram lifelines.

## 3. Notation Quick Reference

```
           0        5       10       15       20  (time, ms)
CLK  _____|--|_____|--|_____|--|_____|--|_____|--|
     LOW  HIGH  LOW HIGH LOW  HIGH  LOW  HIGH  LOW

DATA XXXX|======= VALID ========|XXXXX|= NEW =|

     <-- t_setup ->|<-- t_hold -->
               CLK_EDGE

STATE  [== IDLE ==]|[=== ACTIVE ===]|[= COMPLETE =]
                   ^                ^
              OccurrenceSpec   OccurrenceSpec

      |<------- {d: 10ms to 50ms} ------->|
```

## 4. Python Generation Pattern

```python
def build_state_lifeline(name: str, states: list, y: int) -> list:
    """Build state transition bars for a timing diagram lifeline.

    Args:
        name: Lifeline name (e.g., MotorState).
        states: List of (state_name, start_x, end_x) tuples in pixels.
        y: Vertical position of this lifeline in pixels.

    Returns:
        List of mxCell dictionaries for state bars and transition ticks.
    """
    cells = []
    for state_name, start_x, end_x in states:
        cells.append({
            "value": state_name,
            "style": "shape=mxgraph.uml.state_machine;whiteSpace=wrap;html=1;",
            "vertex": "1",
            "x": start_x, "y": y, "width": end_x - start_x, "height": 30
        })
    return cells


def build_duration_constraint(label: str, start_x: int, end_x: int,
                              y: int) -> dict:
    """Build a duration constraint annotation spanning two time points.

    Args:
        label: Constraint label (e.g., {d: 5ms..20ms}).
        start_x: Left OccurrenceSpecification x-position in pixels.
        end_x: Right OccurrenceSpecification x-position in pixels.
        y: Vertical position for the constraint annotation in pixels.

    Returns:
        Dictionary with mxCell edge attributes for the duration span.
    """
    return {
        "value": label,
        "style": "edgeStyle=none;endArrow=block;startArrow=block;dashed=1;endFill=0;startFill=0;",
        "edge": "1",
        "sourcePoint": {"x": start_x, "y": y},
        "targetPoint": {"x": end_x, "y": y}
    }


def build_clock_waveform(period_px: int, cycles: int,
                          x_start: int, y: int) -> list:
    """Build a square-wave clock lifeline for a timing diagram.

    Args:
        period_px: Clock period in pixels (half period = period_px // 2).
        cycles: Number of clock cycles to render.
        x_start: Left edge starting x-position in pixels.
        y: Vertical position for the clock HIGH level in pixels.

    Returns:
        List of mxCell dictionaries for clock high and low segments.
    """
    cells = []
    half = period_px // 2
    for i in range(cycles):
        x_high = x_start + i * period_px
        x_low = x_high + half
        cells.append({
            "style": "line;strokeColor=#000000;",
            "vertex": "1",
            "x": x_high, "y": y, "width": half, "height": 2
        })
        cells.append({
            "style": "line;strokeColor=#000000;",
            "vertex": "1",
            "x": x_low, "y": y + 20, "width": half, "height": 2
        })
    return cells
```

## 5. Deep Mathematical Foundations

### M1: TCTL Temporal Logic for Timing Constraints

Timed Computation Tree Logic (TCTL) is the formal specification language for real-time behavioral properties on timed automata. TCTL syntax:

  phi ::= p | NOT phi | phi_1 AND phi_2 | EF_{[a,b]} phi | AG_{[a,b]} phi | EU_{[a,b]}(phi_1, phi_2)

Semantics over timed automaton A with clock set C:
- EF_{[a,b]} phi: there exists a path and a time t in [a,b] along that path where phi holds
- AG_{[a,b]} phi: on all paths, phi holds at every time point in the interval [a,b]
- EU_{[a,b]}(phi_1, phi_2): there exists a path where phi_1 holds continuously until phi_2 holds, with the transition occurring at some time in [a,b]

Timing constraint formula for stimulus-response systems:

  AG_{[0,d]}(trigger -> AF_{[0,t]} response)

Meaning: Always (for all times up to d), if trigger occurs, then there exists a future time within t where response holds. This encodes the requirement: every trigger must be followed by a response within t time units.

Region automaton: The timed automaton A is transformed into a finite region automaton A_R for model checking. Clock region: equivalence class of clock valuations differing only in fractional parts. Region count: O(|C|! * (2K)^|C|) where K = maximum clock bound in any constraint.

Worked example -- TCTL formula for a 3-constraint embedded system:

System: motor controller with trigger = motor_start_cmd, response = motor_running, deadline t = 50ms.

Property 1: AG_{[0,infinity]}(motor_start_cmd -> AF_{[0,50ms]} motor_running). Every start command causes motor running within 50ms.

Property 2: AG_{[0,infinity]}(motor_running -> AG_{[0,500ms]} NOT motor_fault). Once motor is running, no fault occurs within 500ms.

Property 3: EF_{[0,100ms]}(motor_idle). The motor reaches idle state within 100ms at some point.

These three TCTL formulas correspond to three DurationConstraints on the timing diagram: the duration from motor_start_cmd to motor_running must be in [0, 50ms]; the fault-free running duration must be in [0, 500ms]; and the time to reach idle must be in [0, 100ms].

### M2: Value Lifeline as Step Function

A value lifeline V models a time-varying quantity as a step function:

  V: R_{>=0} -> S

where R_{>=0} is the non-negative real time axis and S is the state domain (a discrete set of values or named states).

Definition: V is a right-continuous step function: V(t) = s_i for all t in [t_i, t_{i+1}) where s_i is the state value during the i-th interval.

Transition event at t_i: V(t_i^-) != V(t_i) (the left limit differs from the right limit), meaning a state change occurs at exactly t_i. The OccurrenceSpecification in UML maps to this transition event.

Duration of state s_i: delta_i = t_{i+1} - t_i.

Formal properties:
- Total duration: sum of all delta_i from i=0 to n-1 equals the total observation period T_obs
- State coverage: fraction of time in state s = sum of delta_i where V(t_i) = s, divided by T_obs

Worked example -- 4-state signal for a motor controller over 100ms:

States: IDLE -> ACCELERATING -> RUNNING -> DECELERATING.

Step function definition: V(t) = IDLE for t in [0, 10ms); V(t) = ACCELERATING for t in [10ms, 25ms); V(t) = RUNNING for t in [25ms, 80ms); V(t) = DECELERATING for t in [80ms, 100ms).

Transition events: t_0 = 0 (start in IDLE); t_1 = 10ms (transition IDLE -> ACCELERATING); t_2 = 25ms (transition ACCELERATING -> RUNNING); t_3 = 80ms (transition RUNNING -> DECELERATING).

Durations: delta_IDLE = 10ms; delta_ACCELERATING = 15ms; delta_RUNNING = 55ms; delta_DECELERATING = 20ms. Total = 100ms.

State coverage: RUNNING occupies 55ms / 100ms = 55% of the observation period. The timing diagram shows four horizontal bars at each state level with vertical transitions between them.

### M3: Timing Constraint Satisfiability via STNU

Timing constraint set C = {(e_i, e_j, [min_ij, max_ij])} where e_i and e_j are OccurrenceSpecification events and the interval specifies the allowed duration between them.

Satisfiability: find a time assignment tau: Events -> R_{>=0} such that for all (e_i, e_j, [l, u]): l <= tau(e_j) - tau(e_i) <= u.

Simple Temporal Network (STN) formulation: create directed graph G = (V, E_c). For each constraint (e_i, e_j, [l, u]):
- Add forward edge e_i -> e_j with weight u (upper bound)
- Add backward edge e_j -> e_i with weight -l (negated lower bound)

Satisfiability condition: G has no negative-weight cycle. Bellman-Ford detection: O(|V| * |E_c|) time.

Worked example -- 4-event embedded system constraint check:

Events: e0 = interrupt_triggered, e1 = interrupt_handled, e2 = computation_complete, e3 = output_updated.

Constraints: (e0, e1, [0us, 10us]) interrupt latency max 10 microseconds; (e1, e2, [5us, 100us]) computation time 5 to 100 microseconds; (e2, e3, [0us, 5us]) output update within 5 microseconds; (e0, e3, [10us, 200us]) total response time 10 to 200 microseconds.

STN edge construction: e0->e1 weight 10; e1->e0 weight 0; e1->e2 weight 100; e2->e1 weight -5; e2->e3 weight 5; e3->e2 weight 0; e0->e3 weight 200; e3->e0 weight -10.

Cycle checks (all must be non-negative):
- e0->e1->e0: 10 + 0 = 10 > 0 OK
- e1->e2->e1: 100 + (-5) = 95 > 0 OK
- e2->e3->e2: 5 + 0 = 5 > 0 OK
- e0->e3->e0: 200 + (-10) = 190 > 0 OK
- Path e0->e1->e2->e3->e0: 10 + 100 + 5 + (-10) = 105 > 0 OK

No negative cycles -- satisfiable. Valid assignment: tau(e0) = 0, tau(e1) = 8us, tau(e2) = 50us, tau(e3) = 53us. Verification: (e0,e1): 8 in [0,10] YES; (e1,e2): 42 in [5,100] YES; (e2,e3): 3 in [0,5] YES; (e0,e3): 53 in [10,200] YES.

### M4: WCET Correspondence

Worst-Case Execution Time (WCET) is the maximum time a task T can take to execute over all possible inputs and execution paths. WCET is a hard upper bound: WCET(T) >= actual_execution_time(T, input) for all inputs.

UML timing diagram annotation: the duration constraint on task T satisfies d_T <= WCET(T). If the timing diagram shows duration constraint [d_min, d_max] for task T, then d_max <= WCET(T) is required for the timing specification to be feasible.

IPET (Implicit Path Enumeration Technique) for WCET computation:

Objective: WCET = maximize sum over all basic blocks b of (c_b * x_b)

where c_b = worst-case execution cycles for block b, x_b = number of times block b executes in one task invocation.

Subject to flow constraints: For each internal node n in the control flow graph, sum of x_b for incoming edges = sum of x_b for outgoing edges (flow conservation). For the entry node: sum of outgoing x_b = 1. For the exit node: sum of incoming x_b = 1. Integer constraints: x_b >= 0, x_b in Z.

Solution via Integer Linear Programming (ILP); the optimal x_b values correspond to the worst-case execution path.

Worked example -- WCET annotation on a motor control task timing diagram:

Task T = motor_control_cycle. Basic blocks: B1 (sensor read, c_B1 = 3 cycles), B2 (PID computation, c_B2 = 45 cycles), B3 (actuator write, c_B3 = 5 cycles). Path: B1 -> B2 -> B3 (always sequential, no branching).

WCET = 3 + 45 + 5 = 53 cycles. At 100 MHz (10ns/cycle): WCET = 530ns.

Timing diagram annotation: place duration constraint {d: 0..530ns} on the motor_control_cycle lifeline spanning from task_start to task_complete OccurrenceSpecifications. The constraint d <= WCET = 530ns is validated by the ILP solution.

### M5: Timing Ruler Discretization

A continuous timing diagram is rendered on a discrete time ruler with sample rate f_s (samples per second). Nyquist-Shannon theorem: f_s >= 2 * f_max to avoid aliasing, where f_max is the highest-frequency signal component to be represented.

Quantization: each OccurrenceSpecification event is snapped to the nearest sample point at interval T_s = 1/f_s. Quantization error: <= T_s/2 = 1/(2*f_s).

Discretization of continuous constraint [l, u] into sample units: discrete lower bound = ceil(l * f_s); discrete upper bound = floor(u * f_s). The discrete constraint [ceil(l*f_s), floor(u*f_s)] is satisfiable iff ceil(l*f_s) <= floor(u*f_s), i.e., the constraint interval contains at least one sample point.

Aliasing: if f_s < 2 * f_max, a signal at frequency f_signal appears on the timing diagram at aliased frequency f_alias = |f_signal - round(f_signal / f_s) * f_s|. High-frequency transitions appear as lower-frequency artifacts.

Worked example -- discretization for a 100Hz square wave signal with 1kHz sample rate:

Signal: square wave at f_signal = 100Hz (period = 10ms). Sample rate: f_s = 1000Hz (T_s = 1ms).

Nyquist check: f_s = 1000 >= 2 * 100 = 200. Condition met; no aliasing.

Quantization error: <= T_s/2 = 0.5ms. A rising edge at t = 10.3ms is snapped to t_discrete = round(10.3ms / 1ms) * 1ms = 10ms. Quantization error = 0.3ms <= 0.5ms.

Discretization of constraint [9ms, 11ms]: lower = ceil(9ms * 1000Hz) = ceil(9) = 9 samples; upper = floor(11ms * 1000Hz) = floor(11) = 11 samples. Discrete constraint [9, 11] samples at 1ms resolution. Satisfiable since 9 <= 11.

If f_s = 50Hz (undersampling): f_s = 50 < 2 * 100 = 200. Aliasing occurs. The 100Hz signal appears at alias frequency |100 - round(100/50)*50| = |100 - 100| = 0Hz -- the signal appears constant (completely aliased away). The timing diagram would show no oscillation, masking the actual switching behavior.

### M6: Hazard Detection

In digital logic, a timing hazard is a brief spurious output that occurs during signal transitions. The Boolean difference calculus identifies hazard conditions.

Boolean difference of function f with respect to variable x_i:

  delta_f/delta_x_i = f(x_1,...,x_i,...,x_n) XOR f(x_1,...,NOT x_i,...,x_n)

The Boolean difference delta_f/delta_x_i is non-zero for input combinations where f is sensitive to a change in x_i (i.e., where the output should change when x_i changes).

Static hazard types:
- Static-1 hazard: output should remain HIGH but momentarily goes LOW during input transition
- Static-0 hazard: output should remain LOW but momentarily goes HIGH during input transition

Detection condition: a static-1 hazard exists on path P_1 (output stays HIGH) if there is another path P_2 (output momentarily LOW) that is slower than P_1 by a propagation delay difference. The glitch duration = |t_pd(P_1) - t_pd(P_2)|.

Dynamic hazard: output changes more than once during a single input transition (output oscillates before settling). Indicates multiple paths with different parity counts.

Setup time violation: a flip-flop captures incorrect data if the data input changes within t_setup before the clock edge. Hold time violation: data changes within t_hold after the clock edge, causing the flip-flop to lose the captured value.

Worked example -- hazard detection for a combinational circuit:

Circuit: two-input NAND gate with inputs A and B, output Y = NOT(A AND B).

Boolean difference with respect to A: delta_Y/delta_A = Y(A,B) XOR Y(NOT_A, B) = NOT(A AND B) XOR NOT(NOT_A AND B) = NOT(A AND B) XOR NOT(0 AND B when B=0 OR 0 when B=0) ... simplified: delta_Y/delta_A = B (non-zero when B=1).

Hazard condition: a hazard exists when A transitions while B=1. On the timing diagram: if A changes from HIGH to LOW while B remains HIGH, a static-0 glitch may appear on Y (Y should go from LOW to HIGH via the path NOT(A AND B) = NOT(HIGH AND HIGH) = NOT(HIGH) = LOW -> NOT(LOW AND HIGH) = NOT(LOW) = HIGH, but if A arrives at the gate before the gate output settles, a brief LOW pulse on Y constitutes a static-0 hazard).

The timing diagram shows: at t = t_A_transition, A transitions from 1 to 0. Y shows a glitch from LOW briefly back to LOW before settling at HIGH. Glitch duration = t_pd(gate) where both paths through the gate produce a brief intermediate state. Adding a DurationConstraint {d_glitch: 0..t_pd} on the Y glitch duration to the timing diagram documents the hazard specification.

## 6. Anti-Patterns to Avoid

1. **Treating EF and AG TCTL operators as interchangeable existential/universal quantifiers**: M1's semantics are precise — EF_[a,b] phi asserts phi holds at SOME time in the interval along SOME path, while AG_[a,b] phi asserts phi holds at EVERY time point along ALL paths. Writing "AG_[0,50ms] motor_running" when the intended requirement is only "eventually reaches running within 50ms" (EF, not AG) asserts a far stronger and likely unsatisfiable property.

2. **Modeling a value lifeline's transition as occurring over an interval rather than at a single instant**: M2 defines V as a right-continuous STEP function — the transition event at t_i is instantaneous (V(t_i⁻) ≠ V(t_i)), not a gradual ramp. Drawing a sloped or gradual transition on a value lifeline where the underlying signal is genuinely discrete misrepresents the step-function semantics the state-coverage and duration calculations depend on.

3. **Computing state coverage as a simple count of transitions rather than time-weighted duration**: M2's state coverage is Σδ_i (where V(t_i)=s) / T_obs — a DURATION-weighted fraction of total observation time, not a count of how many times the state was entered. A state entered many times briefly can have low coverage despite high transition frequency, while a state entered once for a long interval can dominate coverage.

4. **Declaring a timing constraint set satisfiable by checking each constraint individually instead of the full STN negative-cycle test**: M3's satisfiability condition requires NO negative-weight cycle across the ENTIRE constraint graph, verified via Bellman-Ford — the worked example explicitly checks not just adjacent-pair cycles but the full 4-edge path e0→e1→e2→e3→e0. Verifying only pairwise constraints in isolation can miss an infeasible combination that only emerges from the full cycle.

5. **Annotating a timing diagram's duration constraint with d_max exceeding the task's actual WCET**: M4 states the feasibility requirement is d_max ≤ WCET(T) — the diagram's declared maximum duration must not exceed the analytically/ILP-derived worst-case bound. A timing diagram claiming a tighter deadline is achievable than WCET analysis actually supports documents an infeasible specification, not a real guarantee.

6. **Computing WCET via IPET without enforcing flow conservation at every internal control-flow node**: M4's ILP formulation requires Σx_b(incoming) = Σx_b(outgoing) at each internal node, plus the entry/exit boundary constraints. Omitting flow conservation (e.g. allowing an inconsistent number of block executions) produces an ILP solution that doesn't correspond to any actually-executable path through the control flow graph.

7. **Sampling a timing diagram's signal below the Nyquist rate without checking for aliasing**: M5's Nyquist-Shannon condition requires f_s ≥ 2·f_max. The worked example shows a 100Hz signal sampled at 50Hz aliases completely to 0Hz (appears as a constant flat line) — a timing diagram rendered from undersampled data can show NO oscillation at all while the real signal is actively switching, silently masking the actual behavior being documented.

8. **Assuming quantization error is negligible without checking it against the actual constraint tolerance**: M5's quantization error bound is ≤ T_s/2 = 1/(2·f_s) — for a coarse sample rate, this can be a significant fraction of a tight timing constraint's tolerance window. Snapping events to sample points without verifying the discretized constraint [⌈l·f_s⌉, ⌊u·f_s⌋] still contains at least one valid sample point can silently render a satisfiable continuous constraint as unsatisfiable after discretization.

9. **Diagramming a static-1 or static-0 hazard without first computing which input the Boolean difference is actually non-zero for**: M6's hazard detection condition depends on δf/δx_i being non-zero for the specific input combination under transition — the worked NAND-gate example shows the hazard on input A only exists when B=1 (since δY/δA = B). Flagging a hazard for an input transition where the Boolean difference is actually zero (the output isn't sensitive to that input in that context) documents a hazard that cannot physically occur.

10. **Confusing a static hazard (single glitch, wrong intermediate value) with a dynamic hazard (multiple oscillations before settling)**: M6 distinguishes these by cause — static hazards come from a propagation-delay mismatch between two paths agreeing on the final value; dynamic hazards come from multiple paths with DIFFERENT PARITY counts, causing the output to oscillate more than once. Documenting a multi-transition glitch as a "static-1 hazard" on the timing diagram misattributes its root cause and the fix (path-delay balancing for static hazards vs. path-count/parity analysis for dynamic ones) differs accordingly.

---

## 7. India Layer

BIS IS/IEC 61508 (Functional Safety): IS/IEC 61508 is the Bureau of Indian Standards adoption of IEC 61508, covering functional safety requirements for E/E/PE safety-related systems. Timing diagrams document reaction times, interrupt latencies, and safety-function response deadlines required by IS/IEC 61508 for Safety Integrity Level (SIL) assessments. Applicable to: industrial control systems, process automation, power infrastructure in India.

DRDO Embedded Systems: DRDO (Defence Research and Development Organisation) uses timing diagrams for hardware interface protocol specifications in defense embedded systems. Timing diagrams for bus protocols (CAN, MIL-STD-1553, SpaceWire) are mandatory in DRDO technical documentation.

ISRO Space Systems: ISRO uses timing diagrams for PSLV and Gaganyaan mission-critical sequencing. The PSLV launch sequence uses timing diagrams to specify valve actuation delays, ignition sequences, and stage separation timing. Eclipse UML2 is the standard toolchain for ISRO software documentation.

Automotive India (TATA, Mahindra): Indian automotive manufacturers follow ISO 26262 (Road Vehicle Functional Safety) for ASIL-classified systems. Timing diagrams are required for ASIL B/C/D systems documenting actuator response times and sensor sampling rates. AUTOSAR (Automotive Open System Architecture) timing specifications use timing diagrams.

RDSO Railway Standards: RDSO (Research Designs and Standards Organisation) issues specifications for Indian railway signaling systems. Timing diagrams document signal switching times, interlocking logic response times, and track circuit timing for EN 50128 / IEC 62279 compliance in railway safety software.

STQC Safety-Critical Certification: STQC provides certification for safety-critical software under DO-178C (aviation) and IEC 61508. Level A (DO-178C) and SIL 4 (IEC 61508) certification requires timing analysis documentation including timing diagrams showing WCET bounds and interrupt latency constraints.

## 8. Response Rules

1. Draw time on the X-axis (left to right, increasing) and state names or values on the Y-axis per lifeline.
2. Show each state as a horizontal bar (StateInvariant) and each transition as a vertical tick (OccurrenceSpecification).
3. Annotate duration constraints as brace spans between OccurrenceSpecifications with [min, max] ranges.
4. Include the clock lifeline with period annotation when documenting synchronous digital hardware.
5. Annotate t_setup and t_hold relative to clock edges as DurationConstraints on digital signal lifelines.
6. Annotate WCET bounds as DurationConstraints on task execution lifelines with d_max <= WCET(T).
7. Apply Nyquist check (f_s >= 2*f_max) when specifying discretization of continuous timing constraints.
8. Apply DRDO, ISRO, RDSO, or IS/IEC 61508 India context when the domain involves defense, space, railway, or safety-critical embedded systems.
9. Delegate TCTL model checking proofs and IPET ILP solutions to uml-diagram-mathematics-expert.

## 9. What Not to Do

- Never draw timing diagrams with vertical time axis (time must be horizontal).
- Never omit the time ruler (X-axis scale) from a timing diagram.
- Never use continuous curves for discrete state changes; use step functions with vertical transitions.
- Never specify duration constraints without both min and max bounds; open-ended constraints are ambiguous.
- Never ignore Nyquist sampling when discretizing continuous timing requirements to a digital sample grid.
- Never annotate WCET as a fixed value without bounding it to an ILP-computed worst-case path.
- Never mix analog waveform notation with digital state notation on the same lifeline without clear labeling.
- Never confuse t_setup (before clock edge) with t_hold (after clock edge) in clock-relative timing specifications.

## 10. Output Expectations

Timing diagram output includes: all lifelines with horizontal timeline layout, state bars and transition ticks for discrete state lifelines, step function representation for value lifelines, duration constraints as brace annotations with [min, max] bounds, and clock lifelines with period annotation for synchronous hardware.

For mxGraph XML: use horizontal line segments for state bars, vertical line segments for transitions, and edge cells for duration constraint spans. The clock waveform is rendered as alternating horizontal segments at HIGH and LOW y-levels.

For hardware specification: include setup time, hold time, propagation delay, and clock period annotations as DurationConstraints between the relevant OccurrenceSpecifications.

For safety documentation: include WCET annotations, interrupt latency constraints, and STNU satisfiability verification when IS/IEC 61508 or DO-178C compliance is required.

## 11. Skill Scope

Covers: UML 2.5.1 timing diagram notation, TCTL temporal logic for constraint specification (M1), value lifeline step function formalism (M2), timing constraint satisfiability via STNU (M3), WCET correspondence and IPET ILP formulation (M4), Nyquist discretization (M5), hazard detection via Boolean difference (M6), hardware timing conventions, and DRDO/ISRO/RDSO/IS IEC 61508 India layer.

Does not cover: sequence diagram notation (see uml-sequence-diagram-core), communication diagram notation (see uml-communication-diagram-core), mxGraph XML generation mechanics (see drawio-xml-generation-core), TCTL model checking proof and IPET ILP exact solutions (delegate to uml-diagram-mathematics-expert).

## Version

1.1.0 -- Added Section 6 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India Layer through Skill Scope renumbered §7-11.
1.0.0 -- Domain 46 UML and Diagram Engineering initial release.