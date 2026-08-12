---
name: drawio-xml-generation-core
description: "Generates editable Draw.io (mxGraph) XML files for all 13 UML diagram types using correct shape stencils, style strings, and Bezier edge routing. Use when generating Draw.io files programmatically, converting UML specifications to editable diagrams, creating shareable diagram URLs, or producing diagram artifacts for SDLC documentation. Keywords: draw.io XML generation, mxGraph diagram code, drawio UML stencils, draw.io class diagram code, mxCell XML, drawio sequence diagram, draw.io shareable URL, mxGraph style string"
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/drawio-xml-generation-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# Draw.io XML Generation Core

## Description

This skill provides the complete technical specification for generating Draw.io (mxGraph) XML files programmatically. It covers the mxGraphModel XML schema, shape stencils for all 13 UML diagram types, style strings for nodes and edges, Bezier edge routing configuration, and shareable URL generation via the app.diagrams.net API. It enables systematic creation of editable, professional-grade .drawio artifacts that open in Draw.io desktop, app.diagrams.net, and VS Code with the Draw.io extension. The skill includes the full mxCell hierarchy, geometry model, connection point anchoring, and compressed/uncompressed encoding for URL sharing.

## 1. mxGraph XML Schema

The mxGraph XML schema is the native format used by Draw.io (app.diagrams.net). Every .drawio file is a UTF-8 XML document whose root element is `<mxGraphModel>`.

### 1.1 mxGraphModel Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| dx, dy | int | Viewport translation (pixels) |
| grid | 0\|1 | Grid snap enabled |
| gridSize | int | Grid cell size in pixels (default 10) |
| guides | 0\|1 | Alignment guides enabled |
| tooltips | 0\|1 | Hover tooltips enabled |
| connect | 0\|1 | Connection points shown on hover |
| arrows | 0\|1 | Direction arrows on hover |
| fold | 0\|1 | Collapse/expand containers |
| page | 0\|1 | Page border shown |
| pageScale | float | Logical units per pixel |
| pageWidth | int | Page width in pixels (A4 landscape = 1169) |
| pageHeight | int | Page height in pixels (A4 landscape = 827) |
| math | 0\|1 | LaTeX math rendering enabled |
| shadow | 0\|1 | Drop shadows on shapes |

### 1.2 mxCell Attributes

Every diagram element is an `mxCell`. Cells are **always siblings** inside `<root>` — never nested.

| Attribute | Type | Required | Purpose |
|-----------|------|----------|---------|
| id | string | YES | Unique identifier. id="0" and id="1" are reserved |
| value | string | YES (can be "") | Label text (may contain HTML when html=1 in style) |
| style | string | for user cells | Semicolon-separated style properties |
| vertex | "1" | for shapes | Marks cell as a vertex (shape) |
| edge | "1" | for edges | Marks cell as an edge (connector) |
| source | string | for edges | id of source vertex |
| target | string | for edges | id of target vertex |
| parent | string | YES | id of parent cell. All user cells: parent="1" |

### 1.3 mxGeometry Attributes

`<mxGeometry>` is a child of `<mxCell>` with the attribute `as="geometry"`.

| Attribute | Vertex / Edge | Purpose |
|-----------|--------------|---------|
| x | vertex | Left edge x-coordinate (pixels from origin) |
| y | vertex | Top edge y-coordinate (pixels from origin) |
| width | vertex | Shape width in pixels |
| height | vertex | Shape height in pixels |
| relative | edge | Must be "1" for edge geometry |

### 1.4 Critical Structure Rules

1. **mxCell elements are ALWAYS siblings** inside `<root>`. Parent-child relationships use the `parent=` attribute only. mxCell elements must NEVER be nested inside another mxCell element.
2. `id="0"` is the graph root cell — always present, always empty.
3. `id="1"` is the default layer cell with `parent="0"` — always present, always empty.
4. User content starts at `id="2"` and increments.
5. Every vertex cell requires `vertex="1"`. Every edge cell requires `edge="1"`.
6. Edge `<mxGeometry>` must always carry `relative="1"`.

### 1.5 Minimal Skeleton

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
              tooltips="1" connect="1" arrows="1" fold="1" page="1"
              pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <!-- User cells start at id="2" with parent="1" -->
  </root>
</mxGraphModel>
```

---

## 2. UML Shape Stencils

Draw.io ships the `mxgraph.uml.*` stencil library. The table below maps every major UML element to its correct style or shape value.

| UML Element | Style / Shape Value | Notes |
|-------------|---------------------|-------|
| Class box (with compartments) | `swimlane;fontStyle=1;align=center;startSize=26;` | Most common class notation; value = class name |
| Abstract class | `swimlane;fontStyle=3;align=center;startSize=26;` | fontStyle=3 = bold (1) + italic (2) |
| Interface (lollipop/ball) | `shape=mxgraph.uml.interface2;align=center;html=1;` | Ball notation for component diagrams |
| Interface (box) | `swimlane;fontStyle=3;align=center;startSize=26;dashed=1;` | Dashed box notation |
| Package | `swimlane;startSize=20;fillColor=#f5f5f5;fontStyle=1;` | Tab folder shape |
| Component | `shape=mxgraph.uml.component;align=left;html=1;` | Component icon top-right |
| Node (3D box) | `shape=cube;whiteSpace=wrap;html=1;` | Deployment node |
| ExecutionEnvironment | `shape=cube;whiteSpace=wrap;html=1;dashed=1;` | Dashed variant inside Node |
| Artifact | `shape=mxgraph.uml.artifact;whiteSpace=wrap;html=1;` | Dog-eared document icon |
| Actor (use case) | `shape=mxgraph.uml.actor;` | Stick figure |
| Use case | `ellipse;whiteSpace=wrap;html=1;` | Plain ellipse |
| System boundary | `swimlane;startSize=20;` | Rectangle with name label |
| Note / comment | `shape=mxgraph.uml.note;whiteSpace=wrap;html=1;backgroundOutline=1;` | Dog-eared box |
| Initial state (filled circle) | `ellipse;fillColor=#000000;strokeColor=#000000;` | Solid black circle |
| Final state (activity) | `shape=mxgraph.uml.end_state;` | Bullseye — circle in ring |
| Decision / merge node | `rhombus;whiteSpace=wrap;html=1;` | Diamond |
| Fork / join bar | `shape=mxgraph.uml.fork;` | Horizontal or vertical thick bar |
| Lifeline (sequence) | `shape=mxgraph.uml.lifeline;` | Dashed vertical line with header box |
| Activation box | `shape=mxgraph.uml.activation;` | Narrow execution occurrence rectangle |
| CombinedFragment frame | `shape=mxgraph.uml.frame;` | Rectangle with pentagon label (alt, opt, loop, ...) |
| Collaboration | `shape=mxgraph.uml.collaboration;` | Dashed oval |
| Provided interface | `shape=mxgraph.uml.interface2;` | Ball (lollipop) |
| Required interface | `shape=mxgraph.uml.lollipop;` | Socket (half-circle) |
| Destroy (lifeline end X) | `shape=mxgraph.uml.destroy;` | X mark on lifeline |
| Text / label only | `text;html=1;strokeColor=none;fillColor=none;` | Invisible bounding box, text only |
| Separator line (class compartment) | `line;strokeColor=inherit;fillColor=none;` | Horizontal divider |

---

## 3. UML Relationship Edge Styles

Every UML relationship corresponds to a specific edge style string.

| UML Relationship | Edge Style String |
|-----------------|-------------------|
| Inheritance (generalization) | `edgeStyle=orthogonalEdgeStyle;endArrow=block;endFill=0;` |
| Realization (interface impl) | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=block;endFill=0;` |
| Composition (filled diamond at whole) | `edgeStyle=orthogonalEdgeStyle;startArrow=diamondThin;startFill=1;endArrow=none;` |
| Aggregation (open diamond at whole) | `edgeStyle=orthogonalEdgeStyle;startArrow=diamondThin;startFill=0;endArrow=none;` |
| Association (navigable) | `edgeStyle=orthogonalEdgeStyle;endArrow=open;endFill=0;` |
| Dependency (dashed arrow) | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;` |
| Include (use case) | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;` with label: «include» |
| Extend (use case) | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;` with label: «extend» |
| Message — sync call | `edgeStyle=elbowEdgeStyle;endArrow=block;endFill=1;` |
| Message — async call | `edgeStyle=elbowEdgeStyle;endArrow=open;endFill=0;` |
| Message — return | `edgeStyle=elbowEdgeStyle;dashed=1;endArrow=open;endFill=0;` |
| Deployment arrow | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;` |
| PackageImport | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;` with label: «import» |
| PackageMerge | `edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;` with label: «merge» |
| CommunicationPath (node link) | `edgeStyle=orthogonalEdgeStyle;endArrow=none;` |

---

## 4. Complete XML Examples

### 4.1 Two-Class Inheritance Diagram

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
              tooltips="1" connect="1" arrows="1" fold="1" page="1"
              pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="2" value="Animal" style="swimlane;fontStyle=1;align=center;startSize=26;"
            vertex="1" parent="1">
      <mxGeometry x="100" y="100" width="200" height="120" as="geometry" />
    </mxCell>
    <mxCell id="3" value="+ name: String" style="text;html=1;strokeColor=none;fillColor=none;align=left;"
            vertex="1" parent="2">
      <mxGeometry x="0" y="30" width="200" height="30" as="geometry" />
    </mxCell>
    <mxCell id="4" value="+ speak(): void" style="text;html=1;strokeColor=none;fillColor=none;align=left;"
            vertex="1" parent="2">
      <mxGeometry x="0" y="60" width="200" height="30" as="geometry" />
    </mxCell>
    <mxCell id="5" value="Dog" style="swimlane;fontStyle=1;align=center;startSize=26;"
            vertex="1" parent="1">
      <mxGeometry x="100" y="320" width="200" height="120" as="geometry" />
    </mxCell>
    <mxCell id="6" value="+ breed: String" style="text;html=1;strokeColor=none;fillColor=none;align=left;"
            vertex="1" parent="5">
      <mxGeometry x="0" y="30" width="200" height="30" as="geometry" />
    </mxCell>
    <mxCell id="7" value="+ speak(): void" style="text;html=1;strokeColor=none;fillColor=none;align=left;"
            vertex="1" parent="5">
      <mxGeometry x="0" y="60" width="200" height="30" as="geometry" />
    </mxCell>
    <mxCell id="8" value="" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;endFill=0;"
            edge="1" source="5" target="2" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>
```

Note: mxCell id="3" and id="4" have `parent="2"` (child of Animal class box), and id="6", id="7" have `parent="5"` (child of Dog class box). This is how compartment text cells work — they are child mxCells of their container swimlane cell, positioned relatively within it.

### 4.2 Sequence Diagram with Two Lifelines

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
              tooltips="1" connect="1" arrows="1" fold="1" page="1"
              pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="2" value="Client" style="shape=mxgraph.uml.lifeline;"
            vertex="1" parent="1">
      <mxGeometry x="100" y="40" width="120" height="400" as="geometry" />
    </mxCell>
    <mxCell id="3" value="Server" style="shape=mxgraph.uml.lifeline;"
            vertex="1" parent="1">
      <mxGeometry x="400" y="40" width="120" height="400" as="geometry" />
    </mxCell>
    <mxCell id="4" value="request()" style="edgeStyle=elbowEdgeStyle;endArrow=block;endFill=1;"
            edge="1" source="2" target="3" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="5" value="response" style="edgeStyle=elbowEdgeStyle;dashed=1;endArrow=open;endFill=0;"
            edge="1" source="3" target="2" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>
```

---

## 5. Deep Mathematical Foundations

### M1: mxGraph Object Model Hierarchy

The mxGraph model is a rooted directed tree. Every element is an `mxCell` node. Parent-child relationships define containment and rendering order; sibling order defines Z-order.

**Formal tree structure:**

```
mxGraphModel
  root
    mxCell[id=0]                    <- graph root; no parent attribute
    mxCell[id=1, parent=0]          <- default layer
    mxCell[id=2, parent=1, ...]     <- first user vertex
    mxCell[id=3, parent=1, ...]     <- second user vertex
    mxCell[id=4, parent=1, ...]     <- edge between 2 and 3
    mxCell[id=5, parent=2, ...]     <- label child of vertex 2
```

**Vertex cell complete object model:**

```
mxCell {
  id:       string              unique hash-map key
  value:    string              display label (plain text or HTML)
  style:    string              parsed into {key: value} map
  vertex:   "1"                 identifies cell as a shape node
  parent:   string              id of container cell (usually "1")
  geometry: mxGeometry {
    x:      float               top-left corner x (pixels)
    y:      float               top-left corner y (pixels)
    width:  float               shape width (pixels)
    height: float               shape height (pixels)
  }
}
```

**Edge cell complete object model:**

```
mxCell {
  id:       string
  value:    string              edge label (may be empty)
  style:    string
  edge:     "1"                 identifies cell as a connector
  source:   string              id of source vertex
  target:   string              id of target vertex
  parent:   string              id of layer cell (typically "1")
  geometry: mxGeometry {
    relative: "1"               mandatory for edge geometry
    Array: [mxPoint, ...]       optional intermediate waypoints
  }
}
```

**Minimal working 2-class diagram (complete, immediately loadable in Draw.io):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel>
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="2" value="ClassA" style="swimlane;fontStyle=1;startSize=26;"
            vertex="1" parent="1">
      <mxGeometry x="80" y="80" width="160" height="80" as="geometry" />
    </mxCell>
    <mxCell id="3" value="ClassB" style="swimlane;fontStyle=1;startSize=26;"
            vertex="1" parent="1">
      <mxGeometry x="320" y="80" width="160" height="80" as="geometry" />
    </mxCell>
    <mxCell id="4" value="" style="edgeStyle=orthogonalEdgeStyle;endArrow=open;"
            edge="1" source="2" target="3" parent="1">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>
```

---

### M2: mxGeometry Coordinate System

The mxGraph canvas coordinate system has origin (0, 0) at the top-left corner. X increases rightward; Y increases downward. All values are floating-point pixels at the default pageScale=1.

**Vertex geometry bounding box:**

```
TopLeft     = (x, y)
TopRight    = (x + width, y)
BottomLeft  = (x, y + height)
BottomRight = (x + width, y + height)
Center      = (x + width/2, y + height/2)
```

**Placing N vertices in a horizontal row:**

Given parameters: class width W, horizontal gap G, left margin L, row Y:

```
x_i = L + i * (W + G)   for i in {0, 1, ..., N-1}
y_i = Y                  (constant for all classes in row)
```

**Worked example — 3 classes in a row (W=160, G=40, L=80, Y=80):**

```
Class 0 (User):    x = 80 + 0*(160+40) = 80,   y = 80
Class 1 (Order):   x = 80 + 1*(160+40) = 280,  y = 80
Class 2 (Product): x = 80 + 2*(160+40) = 480,  y = 80
```

Resulting mxGeometry elements:

```xml
<mxGeometry x="80"  y="80" width="160" height="100" as="geometry" />
<mxGeometry x="280" y="80" width="160" height="100" as="geometry" />
<mxGeometry x="480" y="80" width="160" height="100" as="geometry" />
```

**Edge geometry (relative mode):**

When `relative="1"`, the optional `<Array as="points">` child contains `<mxPoint>` elements at absolute canvas coordinates defining intermediate waypoints:

```xml
<mxGeometry relative="1" as="geometry">
  <Array as="points">
    <mxPoint x="300" y="200" />
    <mxPoint x="300" y="350" />
  </Array>
</mxGeometry>
```

Edge label placement: setting the `x` attribute on `<mxGeometry relative="1">` positions the label as a fraction along the edge length (0.0 = source end, 0.5 = midpoint, 1.0 = target end).

---

### M3: Style String EBNF Grammar

Style strings are parsed by Draw.io's renderer into an ordered key-value map controlling every visual property of a cell.

**EBNF grammar:**

```
style      ::= (pair ';')* ;
pair       ::= assignment | flag ;
assignment ::= key '=' value ;
flag       ::= identifier ;
key        ::= [a-zA-Z][a-zA-Z0-9]* ;
value      ::= [^;]* ;
identifier ::= [a-zA-Z][a-zA-Z0-9]* ;
```

**Parsing rules:**
- Semicolons separate pairs; a trailing semicolon after the last pair is legal.
- No spaces around `=` or `;` — any space becomes part of the value token.
- Keys and values are case-sensitive.
- Boolean values are `0` (false) or `1` (true); never `true`/`false`.
- Unknown keys are silently ignored by the renderer.

**Shape properties reference:**

| Key | Values | Default | Effect |
|-----|--------|---------|--------|
| shape | stencil name string | (built-in) | Renders named stencil |
| rounded | 0, 1 | 0 | Rounded corners |
| whiteSpace | wrap, nowrap | nowrap | Text wrapping |
| html | 0, 1 | 0 | HTML in label value |
| container | 0, 1 | 0 | Allow child containment |
| startSize | int | 30 | Swimlane header height px |
| arcSize | int (%) | 10 | Corner radius as % of shorter dimension |

**Color and stroke properties:**

| Key | Values | Default |
|-----|--------|---------|
| fillColor | #RRGGBB or none | #FFFFFF |
| strokeColor | #RRGGBB or none | #000000 |
| strokeWidth | int | 1 |
| dashed | 0, 1 | 0 |
| opacity | 0-100 | 100 |
| gradientColor | #RRGGBB or none | none |

**Font properties:**

| Key | Values | Default |
|-----|--------|---------|
| fontStyle | bitmask int | 0 |
| fontSize | int pt | 12 |
| fontFamily | string | Helvetica |
| fontColor | #RRGGBB | #000000 |
| align | left, center, right | center |
| verticalAlign | top, middle, bottom | middle |

fontStyle bitmask: 1=bold, 2=italic, 4=underline, 8=strikethrough. Combined examples: bold+italic=3, bold+underline=5, bold+italic+underline=7.

**Edge properties:**

| Key | Values | Default |
|-----|--------|---------|
| edgeStyle | orthogonalEdgeStyle, elbowEdgeStyle, entityRelationEdgeStyle | (none) |
| endArrow | none, classic, block, open, oval, diamond, diamondThin, box, circle | classic |
| startArrow | same as endArrow | none |
| endFill | 0, 1 | 1 |
| startFill | 0, 1 | 1 |
| curved | 0, 1 | 0 |
| orthogonal | 0, 1 | 0 |
| exitX, exitY | 0.0-1.0 | (auto) |
| entryX, entryY | 0.0-1.0 | (auto) |

**Complete style string for a UML class box:**

```
swimlane;fontStyle=1;align=center;startSize=26;fillColor=#dae8fc;strokeColor=#6c8ebf;
```

**Complete style string for a UML inheritance (generalization) arrow:**

```
edgeStyle=orthogonalEdgeStyle;endArrow=block;endFill=0;strokeColor=#000000;strokeWidth=1;
```

---

### M4: Bezier Edge Routing via Exit/Entry Constraints

Draw.io supports constrained Bezier curves for edge routing when `curved=1` is set in the edge style. The exit and entry constraints specify normalized attachment positions on the source and target shape boundaries, and the implied tangent direction controls cubic Bezier control point placement.

**Cubic Bezier formula:**

```
P(t) = (1-t)^3 * P0 + 3*(1-t)^2*t * P1 + 3*(1-t)*t^2 * P2 + t^3 * P3

where t in [0, 1]
P0 = exit point on source boundary
P3 = entry point on target boundary
P1 = first control point (tangent direction from P0)
P2 = second control point (tangent direction toward P3)
```

**Exit/entry constraint normalization:**

`(exitX, exitY)` in [0,1]^2 specifies normalized position on the source cell boundary:

```
(0.5, 0.0) = top center
(1.0, 0.5) = right center
(0.5, 1.0) = bottom center
(0.0, 0.5) = left center
```

The actual exit point in canvas coordinates, given cell geometry (cx, cy, cw, ch):

```
exit_x_abs = cx + exitX * cw
exit_y_abs = cy + exitY * ch
```

**Tangent direction from exit/entry constraint:**

```
if exitX = 0:   tangent_exit = (-1, 0)   exits left
if exitX = 1:   tangent_exit = (+1, 0)   exits right
if exitY = 0:   tangent_exit = (0, -1)   exits upward
if exitY = 1:   tangent_exit = (0, +1)   exits downward
```

**Control point construction:**

```
tension = min(width_source, width_target) * 0.5    heuristic, typically 50-100 px
P1 = P0 + tension * tangent_exit
P2 = P3 - tension * tangent_entry
```

**Worked example — left-to-right connection:**

```
Source ClassA: x=80, y=80, w=160, h=80  -> right center exit: P0 = (240, 120)
Target ClassB: x=320, y=80, w=160, h=80 -> left center entry: P3 = (320, 120)

exitX=1, exitY=0.5  -> tangent_exit  = (+1, 0)
entryX=0, entryY=0.5 -> tangent_entry = (-1, 0)
                         entry tangent direction in = (+1, 0) for P2 formula

tension = min(160, 160) * 0.5 = 80

P1 = (240 + 80*1, 120 + 80*0) = (320, 120)
P2 = (320 - 80*1, 120 - 80*0) = (240, 120)

Bezier at midpoint t=0.5:
P(0.5) = (1/8)*(240,120) + (3/8)*(320,120) + (3/8)*(240,120) + (1/8)*(320,120)
       = ((30+120+90+40)/1, (15+45+45+15)/1)
       = (280, 120)
```

The curve passes through the horizontal midpoint between the two classes, as expected for a left-to-right connection. Draw.io style string to activate constrained Bezier:

```
edgeStyle=elbowEdgeStyle;curved=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;endArrow=open;
```

Bezier C1/G1 continuity proofs for multi-segment smooth splines and full spline derivation are delegated to the `uml-diagram-mathematics-expert` agent.

---

### M5: Shape Stencil SVG Path Algebra

Draw.io stencil shapes are defined as SVG path sequences inside an XML `<shape>` element. The mxGraph stencil engine scales these paths to fit the cell's mxGeometry bounding box at render time.

**SVG path commands used in mxGraph stencils:**

| Command | Syntax | Meaning |
|---------|--------|---------|
| M | M x y | Move to (x, y) without drawing |
| L | L x y | Line to (x, y) from current position |
| C | C cp1x cp1y cp2x cp2y x y | Cubic Bezier curve to (x,y) |
| A | A rx ry x-rot laf sf x y | Elliptical arc to (x,y) |
| Z | Z | Close path (straight line back to start point) |

**Stencil XML structure:**

```xml
<shape name="mxgraph.uml.myshape" aspect="fixed" strokewidth="inherit">
  <background>
    <path>
      <move x="0" y="0"/>
      <line x="1" y="0"/>
      <line x="1" y="1"/>
      <line x="0" y="1"/>
      <close/>
    </path>
  </background>
  <foreground>
    <fillstroke/>
    <path>
      <!-- foreground detail paths -->
    </path>
    <stroke/>
  </foreground>
</shape>
```

Stencil coordinates use a normalized 1x1 unit square. The renderer scales x-coordinates by cell width and y-coordinates by cell height.

**SVG path for a UML note shape (dog-eared rectangle):**

The note is a rectangle with a triangular fold at the top-right. Using normalized coordinates (0,0 = top-left, 1,1 = bottom-right) with fold size f = 0.15:

Main outline:
```
M 0 0         -- top-left corner
L (1-f) 0     -- top edge to fold start
L 1 f         -- diagonal fold (top-right to fold-end)
L 1 1         -- right edge down
L 0 1         -- bottom edge left
Z             -- close to top-left
```

Fold triangle detail (foreground):
```
M (1-f) 0     -- fold top
L (1-f) f     -- fold vertical
L 1 f         -- fold horizontal
```

The pre-built stencil `shape=mxgraph.uml.note` renders this path automatically. Custom stencil registration in the JavaScript API:

```javascript
mxStencilRegistry.registerStencil(
    "mxgraph.custom.note",
    new mxStencil(stencilXmlElement)
);
```

---

### M6: Shareable URL Generation Pipeline

Draw.io supports zero-server-storage diagram sharing by embedding the entire diagram XML into a URL fragment. The encoding compresses and encodes the XML so the full diagram fits in a URL.

**5-step encoding pipeline:**

```
Step 1: Raw mxGraph XML string (UTF-8 text)
Step 2: Encode string to UTF-8 bytes
Step 3: Apply raw DEFLATE compression (Python: zlib.compress(bytes,9)[2:-4])
         -> wbits=-15 removes the 2-byte zlib header and 4-byte Adler-32 trailer
Step 4: Base64 encode compressed bytes (standard base64 alphabet)
Step 5: URL-safe transform: replace '+' with '-', '/' with '_', strip trailing '=' padding
```

**Why raw DEFLATE specifically:**
- gzip wraps data with 18 bytes of header/trailer (magic 0x1f 0x8b + metadata + CRC32)
- zlib (wbits=+15) adds 2-byte header (0x78 0x9c) + 4-byte Adler-32 checksum
- raw DEFLATE (wbits=-15) is headerless — smallest output — what Draw.io decoder expects
- Python `zlib.compress(data, level)[2:-4]` slices off zlib header (first 2 bytes) and checksum (last 4 bytes)

**Python implementation:**

```python
import base64
import zlib


def encode_drawio_url(xml_content: str) -> str:
    """Encode mxGraph XML into a shareable app.diagrams.net URL fragment.

    Uses raw DEFLATE compression (no zlib/gzip headers) followed by
    standard base64 with URL-safe character substitution, matching the
    encoding expected by app.diagrams.net and viewer.diagrams.net.

    Args:
        xml_content: Raw mxGraph XML string to encode.

    Returns:
        URL-safe encoded fragment string for use after the #R prefix.
    """
    encoded_bytes = xml_content.encode("utf-8")
    compressed = zlib.compress(encoded_bytes, level=9)[2:-4]
    b64 = base64.b64encode(compressed).decode("ascii")
    url_safe = b64.replace("+", "-").replace("/", "_").rstrip("=")
    return url_safe


def build_shareable_url(xml_content: str) -> str:
    """Build a complete app.diagrams.net shareable URL from mxGraph XML.

    The returned URL opens the diagram in the Draw.io online editor.
    No data is stored server-side; the full diagram is in the URL fragment.

    Args:
        xml_content: Raw mxGraph XML string.

    Returns:
        Complete shareable URL string with the #R encoded fragment.
    """
    fragment = encode_drawio_url(xml_content)
    return f"https://app.diagrams.net/#R{fragment}"


def build_viewer_url(xml_content: str) -> str:
    """Build a read-only viewer URL for the given mxGraph XML.

    Args:
        xml_content: Raw mxGraph XML string.

    Returns:
        Complete viewer.diagrams.net URL with navigation controls.
    """
    fragment = encode_drawio_url(xml_content)
    return (
        f"https://viewer.diagrams.net/"
        f"?highlight=0000ff&edit=_blank&layers=1&nav=1#R{fragment}"
    )
```

**Worked size estimate for a 10-class diagram:**

```
Uncompressed XML:  ~3,000 bytes (10 classes, 15 edges, labels)
After DEFLATE:     ~600 bytes  (80% compression typical for repetitive XML)
After base64:      ~800 chars  (base64 adds ~33% overhead)
Final URL length:  ~850 chars  (well within 2,048-char URL limit)
```

**MCP server shortcut:** The `mcp__drawio-diagram__get_shareable_url` tool performs this encoding automatically when given a diagram name. Raw XML generation is required when: (a) the MCP server is unavailable, (b) debugging XML structure directly, or (c) embedding XML in .drawio files (which store uncompressed XML — no encoding needed).

> **Privacy Note — Shareable URLs:** The shareable URL encodes the FULL diagram XML (all class
> names, method names, service names, network topology) in the URL fragment. Use shareable URLs
> ONLY for public or non-confidential diagrams where access to app.diagrams.net is acceptable
> per your organization's security policy.
> Do NOT use shareable URLs for diagrams containing: internal hostnames or IP addresses, internal
> service names or architecture, authentication flows, or database schema details.
> **Alternative:** Save as a `.drawio` file (local, uncompressed XML) and share the file directly.
> For on-premises use: self-hosted draw.io is available at https://github.com/jgraph/drawio

---

## 6. Anti-Patterns to Avoid

1. **Assigning a vertex's `parent` attribute to another vertex's id instead of the layer cell**: M1's formal tree structure has ordinary vertices parented to the default layer cell (id="1"), not to each other — using a vertex as another vertex's parent to imply visual nesting produces actual mxGraph containment semantics (the child moves/resizes with the parent, is clipped to its bounds), not the intended standalone shape relationship.

2. **Omitting `relative="1"` on an edge's mxGeometry**: M1's edge cell object model marks `relative: "1"` as mandatory for edge geometry. An edge geometry without this flag is interpreted by the renderer using absolute-position semantics intended for vertices, producing incorrect or undefined edge routing.

3. **Using boolean string values `"true"`/`"false"` instead of `"0"`/`"1"` in style strings**: M3's EBNF grammar and parsing rules are explicit — boolean values are `0` or `1`, never `true`/`false`. Since unknown keys and malformed values are silently ignored by the renderer (not errored), a `rounded=true` style string silently fails to apply rounding rather than raising a visible error.

4. **Adding spaces around `=` or `;` in a style string**: M3's parsing rule states any space becomes part of the value token — `fillColor = #dae8fc;` (with spaces) parses the value as `" #dae8fc"` (leading space included) or breaks key matching entirely, rather than the intended `#dae8fc`.

5. **Computing Bezier control points without first correctly deriving the tangent direction from exitX/exitY**: M4's tangent-direction rule is a lookup based on WHICH boundary edge (exitX=0 → left, exitX=1 → right, exitY=0 → top, exitY=1 → bottom) — using the wrong tangent sign (e.g. treating exitX=1 as pointing left instead of right) inverts the curve's initial direction, producing a Bezier that loops back through the source shape instead of curving smoothly away from it.

6. **Setting `tension` independently of the actual shape widths in constrained Bezier routing**: M4's heuristic `tension = min(width_source, width_target) * 0.5` scales the control-point offset to the connected shapes' actual sizes. A fixed tension value applied uniformly across shapes of very different sizes produces curves that look proportionally correct for some shapes and wildly under/over-curved for others.

7. **Defining a stencil path using absolute pixel coordinates instead of the normalized 0-1 unit square**: M5 states stencil coordinates use a normalized 1×1 unit square that the renderer scales by the actual cell width/height at render time. A stencil path authored in pixel coordinates (e.g. `M 0 0 L 160 0`) instead of normalized ones (`M 0 0 L 1 0`) renders correctly only at one specific cell size and distorts at any other.

8. **Using zlib or gzip compression (with their default headers) instead of raw DEFLATE for shareable URL encoding**: M6 is explicit that Draw.io's decoder expects raw DEFLATE (wbits=-15, headerless) — using standard zlib compression (2-byte header + 4-byte Adler-32 trailer) or gzip (18 bytes of header/trailer) without stripping those bytes produces a URL fragment the Draw.io viewer cannot decode, even though the compression algorithm itself succeeded.

9. **Generating a shareable URL for a diagram containing internal architecture details**: M6's privacy note is explicit — the shareable URL encodes the FULL diagram XML (hostnames, service names, auth flows, schema details) directly in the URL fragment, visible to anyone with the link and potentially logged by browsers/proxies/analytics. Defaulting to shareable-URL generation for internal architecture diagrams without checking organizational data-sensitivity policy risks leaking confidential system design.

10. **Assuming the shareable-URL encoding pipeline scales linearly and ignoring the ~2,048-character URL limit for large diagrams**: M6's worked estimate shows a 10-class diagram produces an ~850-character URL after DEFLATE+base64 — but larger diagrams (50+ classes, dense edge sets) can exceed the practical URL length limit even with 80% compression. For diagrams beyond a moderate size, use `.drawio` file export (uncompressed, no length constraint) rather than assuming the shareable-URL pipeline will always fit.

---

## 7. India Context

**MeitY-approved tooling:** MeitY's SDLC tools approved list for e-governance projects includes Draw.io. Its Apache License satisfies GEM (Government e-Marketplace) procurement guidelines for open-source software acquisition. NIC (National Informatics Centre) projects use Draw.io for system architecture documentation under NIC-SSDLC v2.0 (Phases 2 and 3).

**NASSCOM documentation standards:** NASSCOM digital documentation guidelines reference Draw.io as a standard diagramming tool across Indian IT organizations. The NASSCOM NIIT Advanced Java certification curriculum covers architecture diagramming with Draw.io. Indian IT majors — TCS, Infosys, Wipro, HCL — use Draw.io via the VS Code extension for client delivery architecture artifacts.

**STQC and IT Act compliance:** STQC software product certification audits require a Software Architecture Document (SAD). UML component and deployment diagrams in Draw.io format serve as STQC audit evidence. Under IT Act 2000 Section 43A and SPDI Rules 2011, organizations must demonstrate "reasonable security practices" for sensitive personal data. ISO 27001 ISMS documentation (required for 43A compliance) mandates network topology and system architecture documentation — Draw.io deployment diagrams serve this purpose directly.

**DRDO and defence-offset projects:** STQC DO (Defence Offset) requirements for DRDO and HAL projects accept Draw.io format for component and deployment architecture documentation in software delivery packages.

**GitHub India adoption (Mermaid context):** India ranks highest in APAC for Mermaid diagram adoption in GitHub README files. GitHub India engineering blogs document Mermaid adoption for DevOps pipeline visualization. This is relevant context for teams choosing between Mermaid (git-friendly text) and Draw.io (visual editor with richer stencils) — the `mcp__drawio-diagram__convert_mermaid_to_drawio` tool bridges both.

---

## 8. Response Rules

1. Always output syntactically valid XML. Validate before returning: id="0" present and empty, id="1" present with parent="0" and empty, all user cell parent references resolve to existing ids.
2. All mxCell elements are siblings inside `<root>`. Never nest an mxCell inside another mxCell element.
3. Use exact stencil names from Section 2. Do not invent stencil names not in the table.
4. Edge style strings must include `edgeStyle=` for non-default routing.
5. Set `vertex="1"` on all shape cells and `edge="1"` on all connector cells. Never set both on one cell.
6. Include `relative="1"` in every edge `<mxGeometry>` element.
7. For multi-compartment class boxes, add child text cells with `parent` equal to the class cell id.
8. For shareable URLs, use the exact M6 encoding pipeline: UTF-8 bytes → raw DEFLATE [2:-4] → base64 → URL-safe substitution.
9. For sequence diagrams, use `shape=mxgraph.uml.lifeline` for lifeline cells and `shape=mxgraph.uml.activation` for execution occurrence cells.
10. Delegate Bezier C1/G1 continuity proofs and spline derivations to the `uml-diagram-mathematics-expert` agent.

---

## 9. What Not to Do

- Do not nest `<mxCell>` elements inside other `<mxCell>` elements in XML output.
- Do not reuse id="0" or id="1" for any user cell.
- Do not omit `as="geometry"` from `<mxGeometry>` elements.
- Do not include spaces around `=` or `;` in style strings — they become part of the value.
- Do not use boolean literals `true` or `false` in style strings — use `1` or `0`.
- Do not apply gzip or standard zlib (wbits=15) compression for shareable URLs — only raw DEFLATE (wbits=-15 via [2:-4] slice).
- Do not add inline explanatory comments inside code or XML examples.
- Do not invent stencil names not listed in Section 2.
- Do not use `shape=table` layout for class boxes unless explicitly requested.
- Do not omit `edge="1"` or `vertex="1"` flags — Draw.io requires these to distinguish cell type.

---

## 10. Output Expectations

Responses produce one or more of:

1. **Complete mxGraph XML** — a fully formed `<mxGraphModel>` document, immediately loadable in Draw.io desktop, app.diagrams.net, or VS Code Draw.io extension. Contains id=0 and id=1 reserved cells plus all user diagram cells.

2. **Style string** — a semicolon-separated style string for a named UML element type, derived from the reference tables in Sections 2 and 3.

3. **Shareable URL** — a URL beginning with `https://app.diagrams.net/#R` or `https://viewer.diagrams.net/` containing the compressed base64url-encoded diagram XML.

4. **Python generator function** — builds and returns an mxGraph XML string. Has a Google-style docstring. No inline explanatory comments inside the function body. Returns `str`. Uses f-strings for string construction.

5. **Stencil or edge style lookup** — a table entry or style string for a specific UML element type requested by name.

---

## 11. Skill Scope

**In scope:**
- All 13 UML diagram types mapped to mxGraph XML (class, package, component, deployment, object, composite structure, use case, activity, state machine, interaction overview, sequence, communication, timing)
- Complete mxGraph XML generation for any multi-element diagram
- Style string construction for any UML element or relationship type
- Shareable URL generation via M6 encoding pipeline
- Python code for programmatic XML generation (stdlib only, no external dependencies)
- MCP server invocation patterns for `mcp__drawio-diagram__generate_drawio_diagram` and `mcp__drawio-diagram__get_shareable_url`

**Out of scope:**
- Bezier C1/G1 continuity proofs — delegate to `uml-diagram-mathematics-expert`
- Rendering Draw.io XML to PNG/SVG raster output — handled by `uml-diagram` MCP server via Kroki.io
- Mermaid-to-Draw.io conversion algorithm internals — covered in `mermaid-syntax-engine-core`
- UML semantic validation (OCL constraints, metamodel conformance) — covered in UML core skills (1-13)

---

## 12. Version

**Version:** 1.1.0 -- Added Section 6 Anti-Patterns to Avoid (10 bullets grounded in M1-M6); India Context through Version renumbered §7-12. Previously 1.0.0.
**Domain:** UML and Diagram Engineering (Domain 46)
**Standards:** mxGraph XML schema (Draw.io native format); app.diagrams.net URL encoding protocol (raw DEFLATE + base64url)
**Delegation:** Bezier C1/G1 spline math and continuity proofs delegated to `uml-diagram-mathematics-expert`
