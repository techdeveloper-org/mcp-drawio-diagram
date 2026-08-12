---
name: diagram-layout-algorithms-core
description: "Provides deep mathematical foundations and implementation guidance for graph layout algorithms used in UML and diagram rendering engines. Use when implementing custom diagram renderers, extending draw.io or Mermaid layout capabilities, optimizing large diagram layouts, or understanding the mathematical basis of how diagramming tools position nodes and route edges. Keywords: graph layout algorithm, Sugiyama algorithm UML layout, force-directed graph layout, Kamada-Kawai layout, crossing minimization graph, hierarchical layout algorithm, Bezier edge routing, planarity testing algorithm"
allowed-tools: Read,Glob,Grep,Bash,Edit,Write
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/diagram-layout-algorithms-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# Diagram Layout Algorithms Core

## Description

Mathematical foundations and implementation guidance for the graph layout algorithms underlying
UML diagram renderers. Covers the Sugiyama hierarchical layout (4 phases), Kamada-Kawai
force-directed layout, Barnes-Hut acceleration, NP-hardness of crossing minimization,
Kandinsky orthogonal routing, and O(V+E) planarity testing (Hopcroft-Tarjan 1974 BCC decomposition + de Fraysseix, Ossona de Mendez, Rosenstiehl 2004 LR-planarity criterion).

## 1. Hierarchical Layout — Sugiyama Framework

The Sugiyama framework (1981) is the standard algorithm for drawing directed graphs with a
clear top-to-bottom hierarchy: inheritance trees, call graphs, activity diagrams, dependency
graphs. It proceeds in four phases.

### 1.1 Phase 1 — Cycle Removal

**Problem:** Graph G may contain directed cycles; layer assignment requires a DAG.
**Algorithm:** DFS back-edge reversal.

```
Input:  Directed graph G = (V, E)
Output: DAG G' = (V, E') with reversed set R marked

1. Run DFS on G. Maintain a "grey" set (nodes currently on the DFS stack).
2. For each edge (u, v) encountered:
   a. If v is grey (back edge): reverse to (v, u), add to R.
   b. Otherwise: keep as-is.
3. G' = (V, (E \ R) union {(v, u) | (u, v) in R})
```

Back-edge reversal produces a DAG because: DFS assigns discovery numbers. After reversal,
every edge goes from lower discovery number to higher (tree, forward, cross) or from higher
to lower but reversed so it goes lower-to-higher. Hence a topological ordering exists and G'
is acyclic.

**Bound:** |R| <= |E| (each edge reversed at most once; no edge can be simultaneously a back
edge and a tree edge).

Alternative heuristic — Greedy Minimum Feedback Arc Set:
```
Order vertices by (out_degree(v) - in_degree(v)) descending.
Reverse edges that go "backward" in this ordering.
Produces smaller |R| in practice (~20% fewer reversals than DFS on dense graphs).
```

### 1.2 Phase 2 — Layer Assignment

**Goal:** Assign each node v an integer layer(v) such that for every edge (u, v) in G':
`layer(v) > layer(u)`.

**Longest-Path Algorithm — O(V + E):**
```
1. Topological sort V in G' to get ordering (v_1, v_2, ..., v_n).
2. For sources (in-degree = 0): layer(v) = 0.
3. For each v_i in topological order:
     layer(v_i) = max{ layer(v_j) + 1 : (v_j, v_i) in E' }
                  (default 0 if no predecessors)
```

**Worked step — 5 nodes:**
```
Edges (DAG): A->B, A->C, B->D, C->D, D->E
Topological order: A, B, C, D, E

layer(A) = 0  (no predecessors)
layer(B) = max(layer(A)+1) = 1
layer(C) = max(layer(A)+1) = 1
layer(D) = max(layer(B)+1, layer(C)+1) = 2
layer(E) = max(layer(D)+1) = 3

Layers: {0: [A], 1: [B, C], 2: [D], 3: [E]}
```

**Dummy node insertion:** For edge (u, v) with span = layer(v) - layer(u) > 1:
```
Replace (u, v) with chain: u -> d_1 -> d_2 -> ... -> d_{span-1} -> v
d_i placed at layer layer(u) + i (rendered as invisible waypoints on the edge).
```

**Alternatives:**
- Coffman-Graham algorithm O(V log V + E): optimal under width constraint W (max nodes per layer).
- Network-Simplex (Gansner et al. 1993): minimizes `sum{ layer(v) - layer(u) : (u,v) in E }`;
  produces compact layouts; used in Graphviz `dot`.

### 1.3 Phase 3 — Crossing Minimization

**NP-hardness:** Optimal crossing minimization between two adjacent layers is NP-complete
(reduces to the Bipartite Crossing Number problem, equivalent to BETWEENNESS ordering).
In practice, the Barycenter heuristic gives 1.5–3x optimal.

**Barycenter Heuristic:** For layers L_k (fixed, positions pos(u) = 1, 2, ...) and L_{k+1}
(to reorder):

```
bc(v_j) = (1 / |N(v_j)|) x sum{ pos(u) : u in N(v_j) }
```

where N(v_j) = neighbors of v_j in the adjacent fixed layer L_k.

Sort L_{k+1} by bc(v_j) ascending.

**Sweep strategy:**
```
Initialize: arbitrary ordering within each layer.
Repeat until crossing count stabilizes (or max_iterations = 24):
  Forward sweep (k = 1 to L):
    Fix L_k; sort L_{k+1} by barycenter of L_k neighbors.
  Backward sweep (k = L down to 1):
    Fix L_k; sort L_{k-1} by barycenter of L_k neighbors.
Track best ordering (minimum crossing count) across all iterations.
```

**Crossing count between adjacent layers — O(E log E):**
```
Given edges between L_k and L_{k+1}, sort edges by (pos(u), pos(v)).
Count inversions in the pos(v) sequence using merge-sort.
Number of inversions = number of crossings.
```

**Barycenter worked trace (3-layer graph):**
```
Layer 0: [A=1, B=2, C=3]   (fixed)
Layer 1: [X=1, Y=2, Z=3]   (to reorder, edges: A-X, A-Z, B-Y, C-X)

bc(X) = (pos(A) + pos(C)) / 2 = (1 + 3) / 2 = 2.0
bc(Y) = pos(B) / 1 = 2 / 1 = 2.0
bc(Z) = pos(A) / 1 = 1 / 1 = 1.0

Sort by bc ascending: Z (1.0) < X=Y (2.0, tie broken by current order)
New ordering: [Z=1, X=2, Y=3]
Crossing count before: A-X crosses A-Z? No. A-Z crosses B-Y? Yes (1 crossing).
Crossing count after: A-X=2 does not cross A-Z=1... 0 crossings. Improved.
```

**Median alternative:** `bc_median(v) = median{ pos(u) : u in N(v) }`. Often better on sparse
graphs; avoids distortion from degree-1 nodes pulling the barycenter to an extreme.

### 1.4 Phase 4 — Coordinate Assignment (Brandes-Kopf)

**Goal:** Assign x-coordinates to nodes such that aligned nodes share the same x, width is
minimized, and the layout is balanced. Complexity: O(V + E).

**Step A — Vertical Alignment (4 passes):**
```
Four combinations: {UP, DOWN} x {LEFT, RIGHT}

For each combination:
  For each node v in sweep direction:
    Find median neighbor m in the adjacent layer (in opposite direction).
    Conflict check:
      Type-1 conflict: inner segment (between dummy nodes) crossing a non-inner edge.
      If m is blocked by a type-1 conflict: skip alignment.
    If not blocked: align v with m (assign v to m's block).
```

**Block:** maximal set of nodes that should share the same x-coordinate. Blocks are chains
formed by alignment; a block's root is the topmost (or bottommost) aligned node.

**Step B — Horizontal Compaction:**
```
For each of the 4 alignments:
  Build block graph (blocks as nodes, separation constraints as edges).
  Topological traversal; assign x(block) using:
    x(b2) >= x(b1) + width(b1)/2 + min_sep + width(b2)/2
  Place each block as far in sweep direction as constraints allow.
```

**Step C — Combine 4 Alignments:**
```
For each node v: candidates = {x_UL(v), x_UR(v), x_DL(v), x_DR(v)}
1. Normalize: shift each alignment so its leftmost node is at x = 0.
2. Compute final x(v):
   Sort 4 candidates. Take mean of 2 middle values (2-median).
   x(v) = (candidates[1] + candidates[2]) / 2
```

The median combination is more robust than arithmetic mean; outlier alignments (when one
sweep direction gives a pathological layout) do not dominate the result.

**Full phase trace — 5-node 6-edge graph:**
```
Graph: A->B, A->C, B->D, C->D, D->E  (after layers: A:0, B:1, C:1, D:2, E:3)
Nodes per layer: {0:[A], 1:[B,C], 2:[D], 3:[E]}

Phase 1 (cycle removal): No cycles. G' = G.
Phase 2 (layer assignment): (shown above in 1.2)
Phase 3 (crossing minimization):
  Layer 1 has [B, C]. Edges from layer 0: A->B, A->C.
  bc(B) = pos(A)/1 = 1.0; bc(C) = pos(A)/1 = 1.0. Tie -> keep [B, C].
  No crossings (A is the only source, connects to both).
Phase 4 (coordinates, UP-LEFT pass):
  Layer 0: x(A) = 100 (arbitrary start)
  Layer 1: median neighbor of B = A (pos 100) -> x(B) = 100. C has same median -> x(C) = 200.
  Layer 2: D's median of {B=100, C=200} -> x(D) = 150.
  Layer 3: x(E) = median(D=150) = 150.
  After combine-4: x(A)=100, x(B)=100, x(C)=200, x(D)=150, x(E)=150.
```

## 2. Force-Directed Layout — Kamada-Kawai

Best for undirected graphs where proximity conveys semantic similarity: object diagrams,
communication diagrams, knowledge graphs.

### 2.1 Energy Function

Model: nodes connected by springs; rest length of spring (i,j) = graph-theoretic distance d_{ij}.

```
E = sum_{i < j} (k_{ij} / 2) x (|p_i - p_j| - d_{ij})^2
```

where:
- `p_i = (x_i, y_i)` = 2D position of node i
- `d_{ij}` = shortest-path distance from i to j (BFS for unweighted graphs)
- `k_{ij} = K / (d_{ij})^2` = spring stiffness (stiffer for nearby nodes)
- `K` = global spring constant (typically 1.0)
- `|p_i - p_j| = sqrt((x_i - x_j)^2 + (y_i - y_j)^2)` = Euclidean distance

Intuition: nodes that are close in graph topology should be close in layout; nodes far apart
in topology should be far in layout. The `d_{ij}^2` denominator makes nearby node springs
stiffer — they contribute more to total energy if misplaced.

### 2.2 Gradient (Partial Derivatives)

```
dE/dx_m = sum_{j != m} k_{mj} x (x_m - x_j) x (1 - d_{mj} / |p_m - p_j|)

dE/dy_m = sum_{j != m} k_{mj} x (y_m - y_j) x (1 - d_{mj} / |p_m - p_j|)
```

Convergence criterion for node m:
```
Delta_m = sqrt((dE/dx_m)^2 + (dE/dy_m)^2)
```
Stop when Delta_m < epsilon for all m (typically epsilon = 0.01).

### 2.3 Newton-Raphson Update

Per-node optimization using 2x2 Newton-Raphson system:

```
[H_m] x [delta_x, delta_y]^T = -[dE/dx_m, dE/dy_m]^T

H_m = 2x2 Hessian:
  d^2E/dx_m^2     = sum_{j!=m} k_{mj} x (1 - d_{mj} x (y_m-y_j)^2 / |p_m-p_j|^3)
  d^2E/dy_m^2     = sum_{j!=m} k_{mj} x (1 - d_{mj} x (x_m-x_j)^2 / |p_m-p_j|^3)
  d^2E/dx_m dy_m  = sum_{j!=m} k_{mj} x d_{mj} x (x_m-x_j) x (y_m-y_j) / |p_m-p_j|^3
```

Solve 2x2 linear system (Cramer's rule):
```
det = H_xx x H_yy - H_xy^2
delta_x = (-grad_x x H_yy + grad_y x H_xy) / det
delta_y = (-grad_y x H_xx + grad_x x H_xy) / det
Update: x_m += delta_x; y_m += delta_y.
```

### 2.4 Algorithm Loop

```
1. All-pairs shortest paths: BFS from each node. O(n(V+E)) for unweighted.
2. Initialize positions: equally spaced on circle of radius (n x node_diameter / 2*pi).
3. Compute Delta_m for all m.
4. Repeat until max(Delta_m) < epsilon:
   a. m* = argmax_m Delta_m
   b. Newton-Raphson step for m* (solve 2x2 system)
   c. Recompute Delta_{m*}
5. Complexity: O(n^3) worst case (n outer iterations x O(n) gradient per node).
```

**Worked step — 3-node triangle (A-B-C, all edges length 1):**
```
d_{AB} = d_{BC} = d_{AC} = 1  (all directly connected)
k_{AB} = k_{BC} = k_{AC} = K / 1^2 = 1.0

Initial positions: A=(0, 86.6), B=(-50, -43.3), C=(50, -43.3) (equilateral triangle, r=100)

At minimum energy: |p_A - p_B| = |p_A - p_C| = |p_B - p_C| = d = 1 x scale

Energy at equilibrium: E = 3 x (1/2) x 1.0 x (|p_i-p_j| - 1)^2
  When |p_i-p_j| = scale for all pairs: E = 0 (perfect equilateral triangle layout).
  The Kamada-Kawai objective is satisfied when the layout is an equilateral triangle.
```

### 2.5 Fruchterman-Reingold (Simpler Alternative)

```
Attractive force (adjacent nodes):   f_a(d) = d^2 / k
Repulsive force (all node pairs):    f_r(d) = -k^2 / d

k = C x sqrt(Area / n),  C = 1.0 (empirical constant)
Area = layout bounding box area

Temperature schedule: t starts at sqrt(Area); decreases by factor (1 - iter/max_iter) per step.
Maximum displacement per step: min(displacement, t).
Complexity: O(n^2) naive (all-pairs repulsion); O(n log n) with Barnes-Hut.
```

## 3. Barnes-Hut Theta-Approximation

Barnes-Hut (1986) reduces the O(n^2) repulsive force summation to O(n log n) by using a
quadtree to aggregate distant nodes.

### 3.1 Quadtree Construction

```
1. Find bounding box of all node positions.
2. If cell contains 0 or 1 nodes: leaf cell.
3. If cell contains > 1 nodes:
   a. Subdivide into 4 equal quadrants (NW, NE, SW, SE).
   b. Assign each node to the appropriate quadrant.
   c. Recurse on each non-empty quadrant.
4. For each internal cell: store:
   a. total_mass = count of nodes in subtree
   b. center_of_mass = weighted mean of node positions
   c. side_length s = (xmax - xmin) or (ymax - ymin)
Build time: O(n log n).
```

### 3.2 Far-Field Approximation Criterion

```
theta-condition: s / d < theta

where:
  s = side length of quadtree cell
  d = Euclidean distance from query node p to cell's center of mass
  theta = approximation parameter (typical: 0.5)

If theta-condition holds:
  Approximate: treat cell as single particle at its center of mass with mass = cell.total_mass.
  Force on p = k^2 x cell.total_mass / d^2  (directed from cell-COM to p)
Else:
  Recurse into cell's children (split approximation further).
```

**Parameter effects:**
- theta = 0: no approximation (exact O(n^2))
- theta = 0.5: standard tradeoff; relative force error O(theta^2) = 0.25
- theta = 1.0: aggressive; relative force error O(1) — not recommended for precision layouts

**Complexity:**
- Cells visited per query: O(log n) on average when theta = 0.5
- Total for n nodes: O(n log n) per iteration
- Error bound: O(theta^2) relative error per force magnitude

**100-node example theta check:**
```
Quadtree cell: s = 200 px, center_of_mass at (500, 500)
Query node p at (100, 100): d = sqrt(400^2 + 400^2) = 565.7 px
theta = 0.5: s/d = 200/565.7 = 0.354 < 0.5  -> APPROXIMATE (use cell as single point-mass)

Closer node p' at (400, 400): d = sqrt(100^2 + 100^2) = 141.4 px
s/d = 200/141.4 = 1.41 > 0.5  -> RECURSE (do not approximate; inspect 4 child cells)
```

## 4. Crossing Minimization — NP-Hardness

**Theorem (Garey-Johnson 1983):** The Bipartite Crossing Number (BCN) problem is NP-complete.

BCN problem: Given bipartite graph H = (A, B, E), find orderings of A and B that minimize
the number of edge crossings when A and B are drawn on two parallel horizontal lines.

**Reduction from BETWEENNESS (NP-complete):**

BETWEENNESS: Given a set of ordered triples (a, b, c) where b must appear between a and c
in a linear ordering, find such an ordering.

Construction of crossing instance from BETWEENNESS instance:
```
For each triple (a, b, c) with constraint "b between a and c":
  Create node b in A-layer.
  Create nodes a, c in B-layer.
  Add edges (b, a) and (b, c) to H.

Key property: in the constructed H, the number of crossings between edges of the same triple
is 0 if b is between a and c, and 1 otherwise.

Hence: min-crossings layout of H corresponds to satisfying max BETWEENNESS triples.
Since BETWEENNESS is NP-complete -> BCN is NP-complete.
```

**Consequence for k-layer graphs (k >= 2):**
Even with all but one layer fixed, optimal crossing minimization is NP-complete. Hence the
Sugiyama Phase 3 heuristic (Barycenter) is justified — no polynomial exact algorithm exists
unless P = NP.

**Crossing count K_{3,3} example:**
```
K_{3,3}: A-layer = {a1, a2, a3}, B-layer = {b1, b2, b3}, all 9 edges present.

Ordering [a1, a2, a3] x [b1, b2, b3] (worst-case): crossings = 9.
  K_{3,3} graph crossing number = 1 (minimum over ALL drawings, not just 2-layer).
  2-layer bipartite crossing number of K_{3,3} = 1 (achieved with optimal B-layer ordering).
  Worst-case ordering produces up to 9 crossings; optimal ordering achieves 1 crossing.

Barycenter for K_{3,3}:
  bc(a1) = (1+2+3)/3 = 2.0; bc(a2) = 2.0; bc(a3) = 2.0 (all equal, no ordering improvement).
  Barycenter gives no benefit for complete bipartite graph — illustrating the gap between
  heuristic and optimal.

Full-delegate note: formal reduction proof details and inapproximability bounds ->
uml-diagram-mathematics-expert.
```

## 5. Orthogonal Routing — Kandinsky

Kandinsky algorithm produces rectilinear (orthogonal) edge paths for UML class and component
diagrams, minimizing bends and avoiding node overlap.

### 5.1 Port Assignment

Each rectangular node has 4 faces: North (N), South (S), East (E), West (W).
Each edge endpoint is assigned a port on one face.

Port assignment rules:
```
1. For edge (u, v) where v is directly below u (layer(v) = layer(u)+1):
   Source port: u.South face; Target port: v.North face.
2. For edges that skip layers (via dummy nodes): same S/N rule applies at each dummy.
3. Distribute multiple edges across a face using equal-spaced ports.
   Port spacing: face_width / (edge_count_on_face + 1).
4. Port ordering constraint: ports on same face must be ordered consistently
   with the ordering of edge endpoints in the adjacent layer (no crossing within the same face).
```

### 5.2 Minimum Bend Count per Edge

```
Same horizontal AND vertical position (rare): 0 bends.
Only Δx != 0 (or only Δy != 0): 0 bends (straight horizontal/vertical segment).
Both Δx != 0 AND Δy != 0:        min 1 bend.
Specific port-face combinations:
  Source on N/S, target on N/S, positions offset: min 2 bends (L-shape impossible).
  Source on E/W, target on E/W, same side:        min 2 bends.
  Source on N, target on S (or E/W), offset:      min 1 bend (L-shape).
General upper bound: every orthogonal path between two distinct ports needs at most 3 bends.
```

**4-edge bend minimization example:**
```
Nodes: A (left column), B (right column, same level), C (below A), D (below B)
Edges: A->B (horizontal, same layer), A->C (vertical, straight), B->D (vertical), A->D (diagonal)

A->B: Δy=0 -> 0 bends (straight horizontal).
A->C: Δx=0 -> 0 bends (straight vertical).
B->D: Δx=0 -> 0 bends (straight vertical).
A->D: Δx!=0, Δy!=0 -> min 1 bend.

Total minimum bends: 0 + 0 + 0 + 1 = 1 bend.
```

### 5.3 Bend Minimization Formulation

LP relaxation for bend minimization:

```
Decision variables: y_{e,b} in [0, 1]  (1 = bend b used for edge e)

Minimize: sum_{e in E} sum_{b} y_{e,b}

Constraints:
  Connectivity:  the path segments for edge e form a connected rectilinear path
                 from source port to target port.
  Non-overlap:   path segments do not intersect node bounding boxes.
  Separation:    parallel segments separated by min_clearance pixels.
  Integrality:   y_{e,b} in {0, 1} (relaxed to [0, 1] for LP).

LP solve: O(E x grid_size) iterations via simplex.
Round fractional values to 0/1 using largest-first greedy.
```

A* alternative (grid-based routing):
```
Overlay routing grid with cell size = min(node_width, node_height) / 4.
Edge weight: bend_cost = 10 (high penalty); straight segment = 1.
A* per edge: O(grid_cells x log(grid_cells)).
Total: O(E x grid_cells x log(grid_cells)).
Kandinsky strict rule: max 1 edge per port (no port sharing).
Kandinsky relaxed rule: allow port sharing with visual offset.
```

Full LP constraint matrix derivation -> uml-diagram-mathematics-expert.

## 6. Deep Mathematical Foundations

### M1: Sugiyama Phase 1 + Phase 2 — Cycle Removal and Layer Assignment

**DAG proof for back-edge reversal:**

DFS on G = (V, E) assigns each vertex v a discovery time disc(v) and finish time fin(v).
An edge (u, v) is a back edge iff disc(v) <= disc(u) and fin(u) <= fin(v) (v is an ancestor
of u in the DFS forest).

After reversing all back edges, define a total preorder by fin(v) descending. For any remaining
edge (u, v) in G':
- Tree edge (u, v): disc(u) < disc(v) < fin(v) < fin(u) -> fin(u) > fin(v) -> u before v in order -> ok.
- Forward edge (u, v): same argument as tree edge.
- Cross edge (u, v): disc(v) < fin(v) < disc(u) -> fin(u) > fin(v) -> ok.
- Back edges (u, v) were reversed to (v, u): now fin(v) > fin(u) -> ok.

Every edge goes from larger fin-time to smaller fin-time in reversed direction — i.e., follows
topological order. Hence G' has a topological ordering, which is equivalent to G' being a DAG.

**Layer assignment proof of optimality:**

Longest-path layer assignment minimizes the maximum span `max(layer(v) - layer(u))` over all
edges, and trivially satisfies `layer(v) > layer(u)` for each edge. Proof that it satisfies
the edge constraint: by induction on the topological order. Base: sources get layer 0. Step:
if all predecessors u of v have been assigned with layer(u) < layer(v) = max(layer(u)+1), then
layer(v) > layer(u) for all predecessors. The maximum ensures no edge is violated.

**Dummy node count:** Σ_{(u,v) in E'} max(0, layer(v) - layer(u) - 1). For a DAG with average
span S, dummy count = |E| x (S-1). Dummy nodes are invisible; rendered as edge waypoints.

**Complexity summary:**
| Phase | Algorithm | Complexity |
|-------|-----------|------------|
| Cycle removal | DFS back-edge reversal | O(V + E) |
| Layer assignment | Longest-path / topological sort | O(V + E) |
| Dummy node insertion | One pass over edge list | O(E x max_span) |
| Coffman-Graham (width-bounded) | Priority-queue scan | O(V log V + E) |
| Network-Simplex (compact) | Dual simplex on spanning tree | O(V x E) amortized |

### M2: Sugiyama Phase 3 — Crossing Minimization

**Barycenter formula derivation:**

For layer L_{k+1} being sorted, with L_k fixed at positions pos(u_1) < pos(u_2) < ... < pos(u_p):

The barycenter of node v in L_{k+1} is:
```
bc(v) = (1 / |N(v)|) x sum{ pos(u) : u in N(v) }
```

This is the arithmetic mean of neighbor positions. Sorting by bc produces an ordering that
minimizes the number of crossings in expectation, given random neighbor positions.

**Crossing count by merge-sort inversion:**

A crossing between edges (u1, v1) and (u2, v2) exists iff:
`(pos(u1) < pos(u2) AND pos(v1) > pos(v2)) OR (pos(u1) > pos(u2) AND pos(v1) < pos(v2))`

Equivalently: the sequence of v-positions ordered by u-position has an inversion.
Number of inversions = number of crossings. Merge-sort counts inversions in O(E log E):

```python
def merge_count(arr: list[int]) -> tuple[list[int], int]:
    """Sort arr and count inversions via merge-sort.

    Args:
        arr: List of integer positions to sort.

    Returns:
        Tuple of (sorted_list, inversion_count).
    """
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, lc = merge_count(arr[:mid])
    right, rc = merge_count(arr[mid:])
    merged, mc = [], 0
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            mc += len(left) - i
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, lc + rc + mc
```

**Median heuristic comparison:**

Barycenter is mean-based; susceptible to outliers (a node with 1 neighbor at position 1 and
another at position 100 gets bc = 50.5). Median gives the middle value, which for degree-2
nodes gives the same result, but for high-degree nodes is more robust when neighbors have
extreme positions. Empirically, median outperforms barycenter on sparse graphs by ~15%
crossing reduction; barycenter is O(E log E) vs median's O(E log E) — same complexity.

**Sweep convergence:** The sweep terminates because: each sweep pass can only reduce or
maintain crossing count (never increase, since we keep the best ordering). The ordering is
taken from a finite set (n! orderings per layer). Hence the process converges in finite steps.
In practice, convergence occurs in 4–8 sweeps.

### M3: Sugiyama Phase 4 — Brandes-Kopf Coordinate Assignment

**Alignment concepts:**

UP-LEFT (UL) alignment: process layers top-to-bottom; for each node, align to leftmost median
neighbor in the layer above. UP-RIGHT (UR): align to rightmost. DOWN-LEFT (DL), Down-Right (DR):
process bottom-to-top.

**Type-1 conflict definition:**

An inner segment is an edge between two dummy nodes (part of a long edge's chain).
A type-1 conflict occurs when a non-inner edge crosses an inner segment in the given layer
ordering. Type-1 conflicts must be resolved before alignment: the node participating in the
non-inner edge cannot be aligned with the inner segment's dummy node.

Detection: sort edges by left endpoint position; scan for inner segments that cross non-inner
edges (merge-sort style). O(E) per layer.

**Block graph and compaction:**

Block = maximal chain of nodes aligned together (same x-coordinate).
Block graph B = (blocks, separation_constraints):
  Add constraint edge (b1, b2) if b1.rightmost_node is immediately left of b2.leftmost_node.
  Weight of constraint: min_separation = max_node_width/2 + gap + max_node_width/2.

Topological traversal of B assigns x-coordinates in O(|blocks|) = O(V) time.

**Four-alignment combination:**

After 4 alignments, each node v has 4 x-coordinates: x_UL, x_UR, x_DL, x_DR.
Normalization: shift each alignment so min(x in alignment) = 0.
Final: x(v) = average of 2 middle values of {x_UL, x_UR, x_DL, x_DR}.

Mathematical justification: the 4-alignment median minimizes the sum of absolute deviations
from each individual alignment — it is the L1 estimator of center, robust to one outlier
alignment producing a pathological layout.

Full conflict detection algorithm and block graph construction proof:
-> uml-diagram-mathematics-expert (Delegate: Brandes-Kopf Phase 4 formal proof).

### M4: NP-Hardness of Crossing Minimization

**Bipartite Crossing Number (BCN) problem:**

BCN: Given bipartite graph H = (A, B, E) with |A| = m, |B| = n, find permutations sigma_A
of A and sigma_B of B minimizing crossings when A drawn on line y=1 and B on y=0.

Number of crossings for orderings sigma_A, sigma_B:
```
CR(sigma_A, sigma_B) = |{ (i,j,k,l) : sigma_A(i) < sigma_A(k), sigma_B(j) > sigma_B(l),
                            (i,j) in E, (k,l) in E }|
```

**NP-completeness reduction (from BETWEENNESS):**

BETWEENNESS (NP-complete, Opatrny 1979):
  Input: Set U, set T of ordered triples (a, b, c) with a,b,c in U.
  Question: Is there a linear ordering pi of U such that for every (a, b, c) in T,
            b appears between a and c in pi?

Reduction to BCN:
```
For each triple (a, b, c) in T:
  Create variable node v_{abc} in A-layer.
  Create endpoint nodes L_{abc} and R_{abc} in B-layer.
  Add edges (v_{abc}, L_{abc}) and (v_{abc}, R_{abc}).

Claim: CR is minimized (= 0 crossings among same-triple edges) iff BETWEENNESS is satisfied.

Proof sketch:
  Edges of triple (a,b,c): (v, L), (v, R). These cross iff L and R are on the same side
  (not separated by v's position). If v is between L and R in the ordering: 0 crossings.
  If v is not between L and R: 1 crossing.
  Hence minimizing CR is equivalent to solving BETWEENNESS.
  Since BETWEENNESS is NP-complete -> BCN is NP-complete. [Garey-Johnson 1983]
```

Full formal reduction with gap amplification and inapproximability bounds:
-> uml-diagram-mathematics-expert.

### M5: Force-Directed Layout and Barnes-Hut

**Kamada-Kawai energy landscape:**

The energy function E is a sum of squared displacement penalties. At global minimum, every
pair (i,j) satisfies |p_i - p_j| = d_{ij} exactly. For general graphs, this is not always
achievable in 2D without distortion (embedding dimension may need to be higher); the
algorithm finds the nearest local minimum in the 2D embedding.

**Newton-Raphson convergence rate:**

Near a smooth minimum, Newton-Raphson has quadratic convergence: error_{k+1} = O(error_k^2).
For the 2x2 system, convergence from epsilon-neighborhood to machine precision takes O(log log(1/epsilon)) steps.

**Practical initialization:** Circular layout (nodes equally spaced on a circle of radius
r = n x node_size / (2 x pi)) avoids degenerate configurations where all nodes are at the
same point (E = 0 trivially but layout is useless).

**Barnes-Hut theta condition — derivation of error bound:**

Consider a cell C with side s, total mass M, center of mass c_M, and a query point p at
distance d from c_M. The exact force on p from C is:
```
F_exact = sum_{j in C} k^2 x m_j / |p - p_j|^2
```

The approximation replaces with:
```
F_approx = k^2 x M / d^2
```

Relative error: |F_exact - F_approx| / |F_approx| = O((s/d)^2) = O(theta^2).

This follows from a multipole expansion: the monopole term (used by Barnes-Hut) is exact in
the limit s/d -> 0; the leading error term is the quadrupole O((s/d)^2).

**Quadtree depth bound:** For n uniformly distributed nodes in area A, quadtree depth
is O(log(sqrt(A) / node_spacing)) = O(log n). Hence per-query traversal O(log n) cells.

**Barnes-Hut vs naive comparison:**
```
n = 1000 nodes, 50 iterations:
  Naive: 1000^2 x 50 = 50,000,000 pair evaluations
  Barnes-Hut (theta=0.5): ~1000 x 10 x 50 = 500,000 evaluations (100x speedup)
```

### M6: Planarity Testing and Orthogonal Routing

**Kuratowski's Theorem (1930):**

A graph G is planar iff G contains no subgraph homeomorphic to K_5 or K_{3,3}.

"Homeomorphic to X" means obtainable from X by subdividing edges (inserting degree-2 nodes).

Equivalently (Wagner 1937): planar iff G has no K_5 or K_{3,3} as a graph minor (contracting
edges, deleting vertices/edges, not just subdividing).

**O(V+E) Planarity Testing — Hopcroft-Tarjan + LR-Planarity:**

Attribution: Step 1 (DFS + BCC decomposition) follows Hopcroft and Tarjan (1974).
Step 2 (LR-constraint assignment) follows de Fraysseix, Ossona de Mendez, and Rosenstiehl (2004)
"Trémaux trees and planarity" — a distinct algorithm that uses Left-Right DFS ordering.
These two algorithms share the O(V+E) bound but differ in their planarity certificates.

Step 1 — DFS and biconnected component decomposition (Hopcroft-Tarjan 1974):
```
Assign disc(v) and low(v) to each vertex v.
low(v) = min(disc(v), min{disc(w) : (u,w) back edge, u is descendant of v}).
An articulation point u satisfies: disc(u) = min{low(c) : c child of u in DFS tree}.
Biconnected components (BCCs): maximal subgraphs with no articulation points.
G is planar iff every BCC is planar.
```

Step 2 — LR-Planarity test on each BCC (de Fraysseix, Ossona de Mendez, Rosenstiehl 2004):
```
Build palm tree: DFS tree edges + back edges.
Sort children of v by low-point value (ascending).

Assign Left/Right orientation to back edges:
  Two back edges e1 = (u1, v1) and e2 = (u2, v2) (with DFS path intervals):
  - Nesting: DFS interval of e1 is strictly inside e2, or vice versa.
    -> Assign same side (LL or RR).
  - Interlacing: intervals partially overlap.
    -> Must assign opposite sides (LR constraint).

Build constraint graph:
  Add constraint edge (e1, e2) labeled LR when e1, e2 interlace.
  Check: is there an LR-constraint cycle? (i.e., e1 must be L relative to e2, e2 L relative
         to e3, ..., en must be L relative to e1 — impossible).
  LR-cycle -> non-planar. No LR-cycle -> planar.
```

Step 3 — Planarity test execution on K_4 and K_5:

**K_4 (planar, genus=0):**
```
Vertices: {1,2,3,4}, all 6 edges.
DFS from 1: tree edges 1->2->3->4; back edges 1-3, 1-4, 2-4.
Biconnected: entire K_4 is one BCC.
Back edges: {(3,1), (4,1), (4,2)}.
Interval of (3,1) = [disc(1), disc(3)] = [0, 2].
Interval of (4,1) = [0, 3]. (3,1) nesting inside (4,1) -> LL or RR (same side). OK.
Interval of (4,2) = [disc(2), disc(4)] = [1, 3].
(4,2) and (3,1): disc(3)=2 inside [1,3] but disc(1)=0 outside -> interlacing? No: [0,2] and [1,3] overlap partially.
Assign (3,1)=L, (4,2)=R (opposite sides). No LR-cycle. -> PLANAR.
```

**K_5 (non-planar, genus=1):**
```
5 vertices, 10 edges. Euler: V - E + F = 2 -> 5 - 10 + F = 2 -> F = 7.
Planarity requires E <= 3V - 6 = 9. But K_5 has E=10 > 9. -> Non-planar by edge count.
LR-test: DFS produces 4 back edges that form an interlacing pattern with an LR-cycle.
Constraint graph has an odd cycle -> contradiction -> non-planar.
```

**Complexity:** O(V + E) for DFS, BCC decomposition, and LR-planarity test combined.

**Kandinsky bend minimization — LP formulation overview:**

For each edge e in E, let P_e = set of possible rectilinear paths from source_port(e) to
target_port(e). Each path pi in P_e has bend_count(pi) bends.

Integer program:
```
Variables: z_{e, pi} in {0, 1}  (1 = edge e uses path pi)
Minimize:  sum_{e, pi} bend_count(pi) x z_{e, pi}
Subject to:
  (1) sum_{pi in P_e} z_{e, pi} = 1  for all e (each edge uses exactly one path)
  (2) sum_{e: path pi uses grid cell c} z_{e, pi} <= capacity(c)  for each grid cell c
  (3) z_{e, pi} in {0, 1}
```

LP relaxation: replace (3) with 0 <= z_{e, pi} <= 1. Solve LP, then round.
Capacity(c) = max edges per grid cell (Kandinsky strict: 1; relaxed: unlimited).

Full LP standard form matrix and constraint derivation ->
uml-diagram-mathematics-expert.

## 7. Anti-Patterns to Avoid

1. **Reversing back edges without first correctly identifying them via disc/fin times**: M1's DAG proof depends on the precise back-edge definition — disc(v) ≤ disc(u) and fin(u) ≤ fin(v) (v is an ancestor of u). Misclassifying a cross edge or forward edge as a back edge and reversing it unnecessarily can introduce NEW cycles rather than removing the original one, since the topological-order proof only holds when exactly the true back edges are reversed.

2. **Using shortest-path (not longest-path) layer assignment and assuming it still satisfies the edge constraint**: M1's optimality proof specifically uses `layer(v) = max(layer(u)+1)` over predecessors — the maximum, not minimum, is what guarantees layer(v) > layer(u) for every edge. Using min instead of max can assign a node the same or lower layer than one of its predecessors, violating the fundamental hierarchical-layout invariant.

3. **Comparing barycenter and median crossing-minimization heuristics by complexity alone**: M2 notes both are O(E log E) — the same asymptotic complexity — but median empirically outperforms barycenter by ~15% crossing reduction on sparse graphs specifically because barycenter (a mean) is sensitive to outlier neighbor positions while median is robust to them. Choosing barycenter purely because it's "the standard" without considering the graph's degree distribution ignores a known, measurable quality trade-off.

4. **Counting crossings via a naive O(E²) pairwise check instead of the merge-sort inversion-counting algorithm**: M2 shows crossing count is equivalent to counting inversions in the position sequence, computable in O(E log E) via merge-sort. Falling back to brute-force pairwise edge comparison for crossing counts becomes a real bottleneck on large diagrams where the O(E²) vs O(E log E) gap matters.

5. **Aligning a node with an inner-segment dummy node without first resolving Type-1 conflicts**: M3 states type-1 conflicts (a non-inner edge crossing an inner segment) MUST be resolved before alignment — the conflicting node cannot be aligned with the inner segment's dummy node. Skipping this conflict-resolution step before running the four-alignment (UL/UR/DL/DR) pass produces coordinate assignments with visually crossing long-edge chains that the algorithm is specifically designed to avoid.

6. **Averaging all four Brandes-Kopf alignments (UL/UR/DL/DR) instead of the two middle values**: M3's final coordinate rule is explicit — x(v) = average of the 2 MIDDLE values of {x_UL, x_UR, x_DL, x_DR}, which is the L1-estimator median-of-4 construction specifically chosen for robustness to one pathological alignment. Averaging all four values (a mean, not this median-like construction) reintroduces sensitivity to a single bad alignment outlier that the method was designed to reject.

7. **Assuming crossing minimization can be solved exactly in polynomial time for arbitrary graphs**: M4's NP-completeness reduction from BETWEENNESS proves Bipartite Crossing Number minimization is NP-complete — the Sugiyama framework's barycenter/median heuristics are approximations, not exact solvers. Expecting or promising a globally crossing-minimal layout (rather than a good heuristic approximation) for large or dense diagrams sets an achievability expectation the underlying problem's complexity class rules out.

8. **Using Barnes-Hut with a very small theta expecting proportionally better accuracy without checking the actual speedup lost**: M5's relative error is O(theta²) and the speedup example shows theta=0.5 already achieving ~100x speedup at n=1000. Setting theta close to 0 to minimize approximation error degrades toward the O(n²) naive algorithm, losing most of the algorithmic benefit for a quadrupole-order error reduction that's often not perceptible in the final rendered layout.

9. **Testing planarity using only the E ≤ 3V-6 edge-count necessary condition and skipping the full LR-planarity test**: M6's K_5 example shows edge count alone (E=10 > 3×5-6=9) is sufficient to prove non-planarity in that specific case, but the edge-count bound is only a NECESSARY condition for planarity, not sufficient — a graph can satisfy E ≤ 3V-6 while still containing a K_5 or K_{3,3} minor and being non-planar. The full DFS+LR-constraint test (or an explicit Kuratowski/Wagner minor check) is required to actually certify planarity, not just rule it out cheaply.

10. **Modeling Kandinsky bend-minimization as an unconstrained shortest-path problem per edge, ignoring the grid-cell capacity constraint**: M6's ILP formulation includes constraint (2) — the number of edges using any grid cell must not exceed that cell's capacity (1 in strict Kandinsky mode). Routing each edge independently via its own shortest bend-count path without checking capacity produces multiple edges overlapping the same grid cell, violating the routing model's core non-overlap guarantee.

---

## 8. India-Specific Layer

**D3.js and Indian Data Visualization Firms:**
D3.js implements force-directed layout using the Barnes-Hut theta-approximation (theta=0.5
default) in its `d3-force` module. Indian data visualization companies (Hasura for graph
visualization, and internal dashboards at Zepto and Meesho for relationship graphs) build on
D3.js force layouts. Understanding Barnes-Hut is essential for tuning large-graph performance
in these contexts.

**Cytoscape.js and IIT Bioinformatics:**
Cytoscape.js (used in bioinformatics labs at IIT Bombay, IIT Delhi, and NCBS Bangalore for
protein interaction network visualization) implements Dagre layout — a JavaScript port of the
Sugiyama hierarchical algorithm. The Dagre layout engine uses Barycenter crossing minimization
and Brandes-Kopf coordinate assignment. IIT researchers extending Cytoscape plugins need
understanding of Phases 3 and 4 to implement domain-specific layout optimizations.

**Graphviz and DRDO Documentation:**
DRDO (Defence Research and Development Organisation) uses Graphviz `dot` format for software
architecture documentation of embedded systems and command-and-control software. Graphviz `dot`
implements the Sugiyama framework with Network-Simplex layer assignment and Barycenter crossing
minimization — understanding these algorithms is necessary for customizing `dot` output for
complex DRDO architecture diagrams.

**IIT Research on Graph Drawing:**
IIT Bombay and IIT Delhi publish research on graph drawing algorithm variants, including
improved heuristics for crossing minimization on sparse graphs and force-directed algorithms
for biological network visualization. Knowledge of the mathematical foundations (M1–M6 above)
is prerequisite for understanding and contributing to this research.

**NASSCOM Data Visualization Working Group:**
The NASSCOM data visualization working group references force-directed and hierarchical
layouts in its best-practices guide for enterprise dashboard design. Indian product companies
(Freshworks, Zoho, Chargebee) use Cytoscape.js and D3.js for workflow and relationship
visualizations in their SaaS products.

**Indian Startup Ecosystem — Mermaid and Dagre:**
Indian startups documenting microservice architectures in Mermaid (`flowchart TD`) use the
Dagre.js layout engine internally (Sugiyama on DAGs). Understanding that Dagre is a Sugiyama
variant helps engineers debug layout issues (node overlap, poor layer assignment) by tracing
back to the Phase 2 (layer) or Phase 4 (coordinate) algorithmic behavior.

## 9. Response Rules

1. For hierarchical graphs (class diagrams, call graphs): recommend Sugiyama as primary layout.
2. For undirected semantic graphs (communication diagrams, object diagrams): recommend Kamada-Kawai.
3. For graphs with > 500 nodes: recommend Barnes-Hut acceleration (theta = 0.5 default).
4. For class/component diagrams requiring rectilinear edges: recommend Kandinsky orthogonal routing.
5. Test planarity before choosing layout: planar graphs can use planar layout (zero crossings);
   non-planar graphs fallback to Sugiyama or force-directed.
6. Crossing minimization heuristic quality: expect 1.5–3x above optimal — do not promise exact minimum.
7. Always insert dummy nodes for edges that span more than 1 layer (Phase 2 output).
8. Use median variant of barycenter for sparse graphs (degree < 3 average); use mean for dense.
9. Report theta parameter selection explicitly when using Barnes-Hut — affects both speed and accuracy.
10. Full LP constraint matrix and BCN reduction proofs: delegate to uml-diagram-mathematics-expert.

## 10. What Not to Do

- Do not apply Sugiyama to undirected graphs without first orienting edges (run cycle removal first).
- Do not skip dummy node insertion — long edges without dummies produce diagonal lines violating layer constraints.
- Do not use theta > 0.8 for precision layout requirements — error O(theta^2) becomes significant.
- Do not claim the Barycenter heuristic finds optimal crossing count — it is a heuristic with no constant approximation guarantee.
- Do not apply Kandinsky routing to force-directed layouts — orthogonal routing only works with grid-aligned node positions.
- Do not confuse graph-theoretic distance d_{ij} (edge hops) with Euclidean distance |p_i - p_j| in Kamada-Kawai formulas.
- Do not initialize all nodes at the same position in force-directed layout — zero distances cause division by zero in gradient computation.
- Do not skip planarity testing when a planar embedding exists — planar layouts have zero crossings and are always preferred.

## 11. Output Expectations

For each layout algorithm applied:

1. **Algorithm selection rationale**: why this algorithm for this graph type
2. **Phase trace** (Sugiyama): layer assignment table, crossing count before/after Phase 3, final x-coordinates from Phase 4
3. **Energy trace** (Kamada-Kawai): initial E, E at convergence, iteration count
4. **Planarity verdict** (O(V+E) planarity — Hopcroft-Tarjan BCC + LR-planarity test): PLANAR or NON-PLANAR with evidence
5. **Bend count** (Kandinsky): per-edge bend count and total
6. **Python implementation snippet**: runnable code for the chosen algorithm
7. **Performance estimate**: O() complexity and expected time for given node count

Example Phase 3 output table:
```
Layer 0: [A(1), B(2), C(3)]
Layer 1: [X, Y, Z] -> after barycenter: [Z(1.0), X(2.0), Y(2.5)]
Crossings before: 3 | Crossings after: 1 | Improvement: 67%
```

## 12. Skill Scope

**In scope:**
- Sugiyama 4-phase hierarchical layout (all phases, with formulas)
- Kamada-Kawai force-directed layout (energy, gradient, Newton-Raphson)
- Barnes-Hut O(n log n) theta-approximation
- O(V+E) planarity testing (Hopcroft-Tarjan 1974 BCC decomposition + de Fraysseix et al. 2004 LR-planarity criterion)
- Kandinsky orthogonal routing and bend minimization (LP overview)
- NP-hardness of crossing minimization (BCN, BETWEENNESS reduction)
- Python implementation of barycenter heuristic and Kamada-Kawai gradient

**Out of scope:**
- OCL formal semantics and soundness proofs
- Full LP constraint matrix derivation (delegate to uml-diagram-mathematics-expert)
- Brandes-Kopf Phase 4 formal conflict detection proof (delegate)
- BCN inapproximability bounds (delegate)
- 3D graph layout algorithms
- Hypergraph layout (beyond standard graph edges)

## 13. Version

v1.1.0 — Added Section 7 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India-Specific Layer through Version renumbered §8-13.
v1.0.0 — 2026-05-24 | Domain 46: UML & Diagram Engineering
