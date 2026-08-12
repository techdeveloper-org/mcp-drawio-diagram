---
name: uml-profile-diagram-core
description: "Generates complete UML 2.5.1 Profile Diagrams -- Stereotype-to-Metaclass Extension, tagged values, Profile application to Packages, stereotype inheritance and multiple extension, and the expressiveness boundary between lightweight Profile extension and heavyweight MOF metamodeling. Use when designing a domain-specific vocabulary layered on standard UML (e.g. SysML-style, MARTE-style, or a custom DSL), documenting stereotypes and tagged values, or deciding whether a Profile suffices versus a full new metamodel. Keywords: UML profile, stereotype, tagged value, metaclass extension, profile application, domain-specific language DSL, SysML profile, MARTE profile, lightweight extension."
allowed-tools: Read,Glob,Grep
user-invocable: true
---


<!-- generated-by: claude-global-library/tools/project_sync -->
<!-- source: skills/uml-profile-diagram-core/SKILL.md -- edit the library, then re-run sync_project.py -->

# UML Profile Diagram Core

## Description

Provides authoritative UML 2.5.1 Profile Diagram knowledge (OMG UML 2.5.1 Clause 12 "Profiles") -- the 14th and final UML diagram type, covering the Profile extension mechanism: Stereotype-as-metaclass-extension, tagged values as typed attribute slots, Profile application to a Package's namespace, stereotype inheritance and multiple extension, icon/notation customization, and the formal expressiveness boundary between a lightweight Profile and a heavyweight MOF-based metamodel. Generates draw.io Profile-Diagram-shape-library XML (the only renderer in this domain's toolchain with native Profile Diagram support) and a class-diagram-with-guillemet-annotation fallback for Mermaid, which has no native Profile Diagram grammar.

## 1. Profile Mechanism Foundation

### 1.1 Core Metaclasses (Clause 12)

**Profile** -- specialization of Package; the container that owns Stereotypes and imports the base metaclasses it extends via `ElementImport`/`PackageImport` (e.g. importing `Class`, `Component`, `Property` from the UML metamodel package).

**Stereotype** -- specialization of Class; `self.allOwningPackages()` must transitively resolve to a Profile (a Stereotype is owned by a Profile, either directly or via a nested Package owned by a Profile).

**Extension** -- specialization of Association; connects a Stereotype to a Metaclass. Always has exactly 2 memberEnds: one navigable end on the Stereotype side (named for the lowercase stereotype name), one `ExtensionEnd` (specialization of Property) on the metaclass side (named `base_<Metaclass>`, e.g. `base_Class`).

**ExtensionEnd** -- the metaclass-typed end of an Extension; `upper=1` always (one stereotype application per instance); `lower in {0,1}` -- `isRequired(ext) := (lower == 1)` means every instance of the base metaclass must carry this stereotype.

**ProfileApplication** -- specialization of PackageImport; applies a Profile's stereotypes to a target Package's namespace.

### 1.2 Key Formal Distinction: Extension vs. Generalization

Generalization (see `uml-class-diagram-core` M2) is a same-abstraction-level `<=_C` partial order ("is-a"). Extension is **not** an order relation at all -- it is a co-instantiation pairing: an Extension instance means "whenever an instance of metaclass `m` exists AND has this stereotype applied, a paired Stereotype-instance simultaneously exists holding the tag slots." This is dynamic multiple classification, not subtyping, and is the single most common point of learner confusion in this domain.

### 1.3 Render-Mode Notation

| Render mode | Notation | Tooling support |
|---|---|---|
| Text-only | Base shape + `<<name>>` guillemet label | Mermaid `classDiagram` (approximate fallback only -- no native stereotype styling) |
| Icon-decorated | Base shape retained, glyph badge added | draw.io Profile Diagram shape library |
| Icon-replaced | Shape swapped entirely for the glyph (e.g. UML's own `<<Actor>>` stick figure) | draw.io Profile Diagram shape library |

**Mermaid has no `profileDiagram` grammar and does not auto-style `<<stereotype>>` guillemet text inside `classDiagram` bodies (it renders as inert literal text) -- see `mermaid-syntax-engine-core` for the exact fallback pattern.** draw.io has a dedicated "UML Profile Diagrams" shape library with proper closed-filled-arrowhead Extension connectors, Metaclass shapes, and Stereotype shapes -- see `drawio-xml-generation-core` for the rendering mechanics. This skill states the render-mode mapping but delegates the rendering mechanics of both tools to those two skills rather than re-deriving them.

---

## Deep Mathematical Foundations

### M1: Stereotype as Metaclass Extension

**Formal setup.** Let `M` = the set of UML metaclasses available for reference inside a Profile `P` (imported via `ElementImport`). Let `S` = the set of Stereotypes owned (directly or via a nested Package) by `P`. An Extension is a triple `ext = (s, m, mult)`, `s in S`, `m in M`, `mult = (lower, upper)` the multiplicity of its ExtensionEnd, with `upper = 1` always and `lower in {0,1}`; `isRequired(ext) := (lower == 1)`.

**Well-formedness (OCL, derived from Clause 12's base constraints):**
```
context Extension inv ExactlyTwoEnds:
    self.memberEnd->size() = 2
context Extension inv HasOneExtensionEnd:
    self.memberEnd->exists(e | e.oclIsKindOf(ExtensionEnd))
context Stereotype inv OwnedByProfileTransitively:
    self.allOwningPackages()->exists(p | p.oclIsKindOf(Profile))
```

**Worked example.** `<<SecurityCritical>>` extends `Class`: `ext1 = (SecurityCritical, Class, (0,1))`, so `isRequired(ext1) = false` -- any Class MAY carry the stereotype, none are required to.

### M2: Tagged Values as Stereotype-Attribute Typed Slots

**Formal setup.** `TD(ST) = {t_1, ..., t_k}` = tag definitions owned by Stereotype `ST`, each `t_i = (name, type, lower, upper, default)`. When `ST` is applied to a base element `e`, an implicit StereotypeApplication (realized as an InstanceSpecification typed by `ST`) creates a Slot per `t_i`:

```
valid_assignment(t_i, v_set) iff |v_set| in [lower_i, upper_i]
                              and forall v in v_set: typeOf(v) <=_C type(t_i)
```

(`<=_C` reuses the subtype partial order from `uml-class-diagram-core` M2.)

**Worked example.** Tag `reviewLevel: SecurityLevel[1]` (enum HIGH/MEDIUM/LOW), default MEDIUM. Applied to `PaymentProcessor`: `slot(reviewLevel, PaymentProcessor) = HIGH`. Check: `1 in [1,1]` OK; `typeOf(HIGH) = SecurityLevel` OK -- valid.

### M3: Profile Application as Namespace-Import-Like Operation

**Formal setup.** ProfileApplication specializes PackageImport: `PA = (Pkg, P)`.
```
appliedProfiles(Pkg)      = {P | ProfileApplication(Pkg,P) exists}
availableStereotypes(Pkg) = union over P in appliedProfiles(Pkg) of ownedStereotype(P)
```

**Collision rule** (derived from base `Namespace::membersAreDistinguishable()`, not a Profile-specific OCL clause the spec states verbatim -- flagged as derived, not quoted): if two applied Profiles both own a stereotype with the same `name` and overlapping applicable metaclass, the combined namespace violates `membersAreDistinguishable()` unless references are qualified (`P1::Persistent` vs `P2::Persistent`). OMG does not define aliasing for ProfileApplication at the base-spec level -- most tooling treats this as an authoring-time error requiring rename or merge, not an application-time-resolvable one.

**Worked example.** `PaymentModule` applies `SecurityProfile` (`<<SecurityCritical>>`) and `ComplianceProfile` (`<<AuditRequired>>`) -- no collision, distinct names. A third profile also defining `<<SecurityCritical>>` on `Class` would be ill-formed.

### M4: Stereotype Inheritance and Multiple Extension

Two distinct multiplicities:

**(a) Multiple extension** -- one Stereotype can have several Extensions to *different* metaclasses: `Extensions(ST) = {ext | ext.stereotype = ST}`, `|Extensions(ST)| >= 1`. Applicability: `applicable(ST, m) iff exists ext in Extensions(ST): m <=_C ext.metaclass` (subtype targets qualify too).

**(b) Stereotype generalization** -- since Stereotype IS-A Class, ordinary Generalization applies between Stereotypes, forming the same `<=_C` partial order (restricted to `S`) already established in `uml-class-diagram-core` M2.

**Inheritance propagation:**
```
TD(ST_child) = TD_own(ST_child) union (union over parent in directParents(ST_child) of TD(parent))
applicableMetaclasses(ST) = ownExtensions(ST).metaclass union (union over parent of applicableMetaclasses(parent))
```
Redefinition of an inherited tag must narrow covariantly: `type(t_child) <=_C type(t_parent)` and `[lower_child, upper_child] subset-or-equal [lower_parent, upper_parent]`.

**Worked example.** `<<Persistent>>` extends `Class`, tag `storageEngine: String[1]` default "RDBMS". `<<CachedPersistent>> --|> <<Persistent>>` adds its own Extension to `Component`, inherits `storageEngine` (redefines default to "NoSQL"), adds own tag `cacheTTLSeconds: Integer[1]`. Result: `applicableMetaclasses(CachedPersistent) = {Class, Component}`.

### M5: Icon/Notation Customization as Presentation-Layer Mapping

**Formal setup.** Three render modes (see section 1.3), formalized as a function `render: (Stereotype, m, Icon?) -> GraphicalRepresentation`: text-only (base `Notation(m)` shape + guillemet label), icon-decorated (base shape retained, glyph badge added), icon-replaced (shape swapped for the glyph entirely -- UML's own built-in `<<Actor>>` stick figure is the canonical example of this mode applied to a Classifier).

**Tooling-reality constraint (not a formal proof, but load-bearing for Output Expectations):** Mermaid's `classDiagram` grammar has no `profileDiagram` keyword and does not auto-style `<<stereotype>>` text -- only render-mode 1 is reachable, and only by hand-writing the guillemet annotation inside a `classDiagram` class body. draw.io's dedicated Profile Diagram shape library is the only renderer in this domain's toolchain capable of modes 2 or 3, or a literal spec-faithful Profile Diagram layout with proper Extension-arrow notation.

### M6: DSL via Profiles (Lightweight) vs. Full MOF Metamodel (Heavyweight) -- Expressiveness Boundary

**Formal setup.** Let `MOF` = the set of MOF-level constructs (new metaclass, new meta-association, new meta-attribute, new meta-operation, OCL constraint -- arbitrary new abstract syntax). Let `PROF` = the set of Profile-level constructs (Stereotype as decoration of an existing metaclass, Extension as pairing to an existing metaclass, TaggedValue as data-slot-only addition, OCL constraint restricting only).

**Claim: `PROF` is a strict subset of `MOF`.**

*Forward direction (every Profile construct translates to a MOF construct):* every Stereotype can be mechanically translated to a subclass Metaclass of its extended base (a known Profile-to-MOF bridging transformation).

*Reverse direction fails (some MOF constructs are unreachable from Profile constructs):*
1. A Profile cannot conjure a wholly new abstract-syntax metaclass with no pre-existing UML host -- every Stereotype MUST anchor to some `m in M` via Extension.
2. A Profile cannot add new relationship kinds structurally distinct from Association/Generalization/Dependency -- it can only add data (tags) to existing relationship instances.
3. Icon substitution (M5) is presentation-only -- a stereotyped `Class` instance remains ontologically an instance of `Class` first (true multiple classification, not a new type); generic UML tooling that only understands `Class` still partially validates it, whereas a genuine new MOF metaclass produces instances no pre-existing UML tool recognizes at all.

**Decision criterion.** Use a Profile when concepts are refinements of existing UML semantics AND round-trip interoperability with standard UML tooling matters. Use a full MOF metamodel when the domain has genuinely novel abstract syntax with no natural UML host metaclass, or new relationship/constraint kinds Association/Dependency/Generalization cannot express.

**Worked grounding example.** SysML 1.x is built entirely as a UML Profile: `Block` extends `Class`, `FlowPort` extends `Port` -- pure decoration, so SysML 1.x models remain valid UML models any UML tool can open. MARTE similarly: `Nfp` extends `Property`, `NfpConstraint` extends `Constraint`. By contrast, later SysML work moved toward a dedicated new MOF-based metamodel (KerML) rather than a UML Profile, because a unified type system could not be cleanly expressed purely as decoration of existing UML metaclasses -- an empirical instance of crossing the `PROF subset MOF` boundary. (Verify the current OMG ratification status/version of any KerML-related claim against the live spec before citing a specific date -- this detail is architectural precedent, not a versioned fact this skill pins down.)

---

## Anti-Patterns to Avoid

1. **Applying a stereotype to a metaclass instance when the Extension's `isRequired` flag actually demands universal application, and treating it as optional anyway**: M1's `isRequired(ext) := (lower == 1)` distinguishes optional (lower=0, any instance MAY carry it) from required (lower=1, every instance of the extended metaclass MUST carry it) extensions. Treating a `lower=1` Extension as if the stereotype were merely a suggestion misreads a genuine multiplicity constraint on the metamodel, not just a documentation convention.

2. **Assigning a tagged-value slot without checking both the cardinality bound and the type-conformance condition**: M2's `valid_assignment` requires BOTH `|v_set| in [lower_i, upper_i]` AND `typeOf(v) <=_C type(t_i)` for every value — satisfying only the cardinality bound while assigning a value of the wrong type (or vice versa) produces an ill-formed StereotypeApplication even if it looks superficially correct.

3. **Applying two profiles that both define a same-named stereotype on overlapping metaclasses without qualifying references**: M3's collision rule states this violates `membersAreDistinguishable()` unless disambiguated with qualified names (`P1::Persistent` vs `P2::Persistent`). Since OMG doesn't define aliasing for ProfileApplication at the base-spec level, most tooling treats this as an authoring-time error requiring rename or merge — assuming the tool will "figure it out" at application time is misplaced trust.

4. **Redefining an inherited tagged value with a wider type or cardinality than the parent stereotype's tag**: M4's inheritance propagation requires covariant narrowing — `type(t_child) <=_C type(t_parent)` and `[lower_child,upper_child] ⊆ [lower_parent,upper_parent]`. A child stereotype redefinition that WIDENS the inherited tag's type or cardinality bounds breaks the subtyping relationship the inheritance mechanism depends on.

5. **Computing a stereotype's applicable metaclasses from only its own Extensions, ignoring inherited applicability**: M4's `applicableMetaclasses(ST)` is the UNION of the stereotype's own Extension targets AND every ancestor's applicable metaclasses (the worked example shows CachedPersistent inheriting Class-applicability from Persistent while adding its own Component-applicability). Checking only a stereotype's directly-declared Extensions when determining where it can be applied misses the metaclasses it can legitimately decorate via inheritance.

6. **Assuming Mermaid's `classDiagram` grammar supports icon-decorated or icon-replaced stereotype rendering**: M5's tooling-reality constraint is explicit — Mermaid has no `profileDiagram` keyword and doesn't auto-style `<<stereotype>>` text, so only render-mode 1 (text-only guillemet annotation) is reachable, and only by hand-writing it. Attempting to author a profile diagram expecting icon substitution in Mermaid output will silently fall back to plain text with no error.

7. **Choosing Profile-based lightweight extension when the domain requires genuinely new relationship kinds**: M6's reverse-direction failure #2 states a Profile "can only add data (tags) to existing relationship instances" — it cannot create structurally new relationship kinds distinct from Association/Generalization/Dependency. Trying to model a domain-specific relationship semantics that doesn't reduce to decorating an existing UML relationship forces an awkward Profile-based workaround where a full MOF metamodel extension was actually needed.

8. **Treating a stereotyped Class instance as if it were ontologically a new, distinct type recognized by all UML tooling**: M6's reverse-direction failure #3 notes icon substitution is presentation-only — a stereotyped Class remains an instance of Class FIRST (not true multiple classification), so generic UML tooling that only understands `Class` still partially validates it. Assuming stereotype application creates a genuinely new metaclass that non-profile-aware tools would reject overstates what the lightweight extension mechanism actually accomplishes.

9. **Using a Profile to introduce a wholly new abstract-syntax metaclass with no pre-existing UML host**: M6's reverse-direction failure #1 is explicit — every Stereotype MUST anchor to some existing metaclass `m in M` via Extension; a Profile cannot conjure new abstract syntax from nothing. A domain concept that has no reasonable existing UML metaclass to extend is a signal that a full MOF metamodel (per the decision criterion) is needed instead, not a sign to force-fit an awkward Extension.

10. **Citing KerML's specific OMG ratification status or version as a settled fact without verification**: M6's worked grounding example explicitly flags this — the SysML 1.x-to-KerML architectural trajectory is cited as precedent for the PROF⊊MOF boundary, but any specific ratification date or version number for KerML should be checked against the live OMG spec before being stated as fact, since this skill's content doesn't pin down that detail as current.

---

## Response Rules

1. Always cite UML version (2.5.1, Clause 12 "Profiles") when referencing the metamodel rules in this skill.
2. Always distinguish Extension (co-instantiation pairing) from Generalization (subtyping) explicitly -- never describe a Stereotype as "inheriting from" its base metaclass.
3. When generating OCL constraints on Extension/Stereotype/ProfileApplication, use the exact `context X inv Name:` prefix, matching `uml-class-diagram-core`'s convention.
4. State the render mode (text-only / icon-decorated / icon-replaced) explicitly and route to draw.io for modes 2-3, Mermaid class-diagram-with-guillemet fallback for mode 1 only.
5. Never claim Mermaid has native Profile Diagram support -- it does not; state the fallback explicitly per M5.
6. When a design question is "should this be a Profile or a new metamodel," apply M6's decision criterion rather than defaulting to a Profile out of familiarity.
7. Mark required stereotype applications (`isRequired`, ExtensionEnd `lower=1`) explicitly -- do not leave application cardinality implicit.
8. For India context, cite IS/ISO 19505-1/-2 as in `uml-class-diagram-core`, since Profile Diagrams share the same base standard.
9. Delegate OCL formal soundness proofs (denotational semantics, type-system completeness of the Extension mechanism) to `uml-diagram-mathematics-expert`.
10. Delegate draw.io XML generation mechanics to `drawio-xml-generation-core` and Mermaid fallback syntax mechanics to `mermaid-syntax-engine-core` -- this skill states the render-mode mapping, not the rendering code.

---

## What Not to Do

- Do not describe Stereotype-extends-Metaclass as inheritance/generalization -- it is a distinct co-instantiation (Extension) relationship (see M1's explicit distinction).
- Do not claim Mermaid can natively render a Profile Diagram or auto-style stereotype guillemets -- it cannot (M5).
- Do not omit the ExtensionEnd multiplicity (`isRequired`) when specifying a Stereotype -- leaving it implicit hides whether the stereotype is mandatory or optional on its base metaclass.
- Do not recommend a Profile for a domain that needs genuinely new abstract syntax (new relationship kinds, metaclasses with no UML host) -- apply M6's expressiveness-boundary criterion and recommend a MOF metamodel instead.
- Do not silently allow two applied Profiles with colliding stereotype names -- flag the `membersAreDistinguishable()` violation and require qualification or rename (M3).
- Do not generate `[TODO]` or placeholder OCL invariants for Extension/Stereotype well-formedness -- write actual boolean expressions per M1-M4.

---

## Output Expectations

For Profile Diagram requests, produce:
1. draw.io XML using the Profile Diagram shape library (preferred renderer) for icon-decorated or icon-replaced stereotypes, OR a Mermaid `classDiagram` with explicit guillemet annotations when only text-mode is needed -- state which was chosen and why.
2. Full Stereotype/Extension/Metaclass table: stereotype name, extended metaclass(es), `isRequired`, owned tag definitions with types and defaults.
3. At least one OCL well-formedness invariant per Extension or ProfileApplication specified in requirements.
4. An explicit M6 decision-criterion statement whenever the request could plausibly be served by either a Profile or a new metamodel.
5. India compliance note citing IS/ISO 19505 when context is Indian government or NASSCOM-certified software, matching `uml-class-diagram-core`'s convention.

---

## Skill Scope

**In scope:**
- UML 2.5.1 Profile Diagram metaclasses and notation (Clause 12 "Profiles")
- Stereotype-as-metaclass-extension, tagged values, Profile application, stereotype inheritance/multiple extension
- Icon/notation customization and its render-mode mapping to draw.io vs. Mermaid
- Lightweight-Profile-vs-heavyweight-MOF-metamodel expressiveness boundary and decision criterion
- India regulatory context (BIS IS/ISO 19505), consistent with `uml-class-diagram-core`

**Out of scope:**
- Class diagram generalization/association/OCL fundamentals -- see `uml-class-diagram-core`
- draw.io XML generation mechanics -- see `drawio-xml-generation-core`
- Mermaid syntax mechanics -- see `mermaid-syntax-engine-core`
- Full OCL denotational semantics proofs -- delegate to `uml-diagram-mathematics-expert`
- Full MOF metamodel authoring beyond the Profile-vs-MOF decision criterion -- out of this domain's scope entirely

---

## Version

1.1.0 -- Added Anti-Patterns to Avoid section (10 bullets grounded in M1-M6)
1.0.0 -- Initial release, Domain 46 UML and Diagram Engineering
