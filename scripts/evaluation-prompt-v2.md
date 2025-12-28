# Prompt: Evaluate an Abstract Interpretation Tool on Mini If/While Programs

**Version:** 2.0 (Revised for scientific rigor and fairness)

You are evaluating **[INSERT TOOL_NAME]** (hereafter: TOOL) 
to assess whether it can **prove assertions** for small programs 
in a tiny "if/while + assignments + assert" language.

Ground all conclusions in TOOL's **documented examples, API, and (if available) source code**. 
Avoid speculation; if evidence is unavailable, state so explicitly.

---

## Critical Constraints (Non-negotiable)

You MUST NOT:
- Speculate about features not documented or exemplified in TOOL
- Assume TOOL handles constructs without explicit evidence
- Extrapolate from one example to untested cases
- Be less rigorous with TOOL than with reference tools

If uncertain, answer: "Cannot determine from available evidence" and specify 
what documentation/code would resolve the uncertainty.

---

## Evidence-Gathering Requirements

### 1. Examples from TOOL

Find and cite **at least 3** example programs or usage demonstrations in TOOL's official 
documentation, repository, or published papers. For each, provide:
- **URL/path** where found
- **Brief summary** (2–3 sentences)
- **What language constructs it uses** (loops, conditionals, domains, etc.)

If fewer than 3 examples exist, report the actual count and note any limitations.

### 2. Reference Benchmarks from Your Tool

You must read and summarize the following **reference programs** from your tool 
(these define the language/constructs you care about):

- `/workspace/examples/benchmarks/if-else-trivial/if-else-trivial.txt`
  - **Summary to provide:** [What it tests, key constructs]
  
- `/workspace/examples/benchmarks/petter3/petter3.txt`
  - **Summary to provide:** [What it tests, key constructs]
  
- `/workspace/examples/benchmarks/sum-is-n-square/sum-is-n-square.txt`
  - **Summary to provide:** [What it tests, key constructs]

**If any benchmark file is not accessible**, explicitly state:
> "Benchmark [name] at [path] could not be accessed. Analysis adjusted to..."

Do NOT skip or assume their content.

### 3. Codebase Inspection (TOOL)

Identify **at least 5** distinct, public-facing functions/classes that directly implement 
one of these roles:

- Parser or input handler
- CFG builder or AST representation
- Fixpoint iteration engine or iteration control
- Transfer functions (abstract semantics for operators)
- Abstract domain operations (join, widening, meet, etc.)
- Assertion or safety property checker

**For each function/class, report:**
- Symbol name (e.g., `class PolyhedralDomain`, `def analyze_loop(...)`)
- File and module location
- Role (select one from list above)
- 1–2 sentence description of what it does

**Utility functions** (logging, I/O formatting) do NOT count.

**If TOOL is closed-source or code is inaccessible**, state explicitly:
> "Source code not accessible. Analysis based on [API docs / published papers] only."

Then proceed with public API/docs as the evidence base.

**If fewer than 5 functions exist** matching the above criteria, report the actual count 
and explain why (e.g., TOOL is a library wrapping a solver, so there are only 2 user-facing 
API functions).

### 4. Loop Handling Evidence

You must answer each of these explicitly:

| Question | Answer | Evidence/Citation |
|----------|--------|-------------------|
| Does TOOL have a built-in fixpoint iteration engine? | Yes / No / Unknown | [cite doc section, code module, or paper] |
| If yes, which widening/narrowing strategies exist? | [list, or "None documented"] | [cite] |
| Can the fixpoint threshold or iteration limit be configured? | Yes / No / Unknown | [cite] |
| If no built-in fixpoint engine, what does TOOL expect the user to do? | [e.g., "provide invariants", "use external SMT solver"] | [cite] |

**If loop handling is not documented or evidenced**, state:
> "No evidence of a built-in loop fixpoint engine found in [sources checked]."

---

## The Three Evaluation Examples

### Language Specification

Programs consist of:
- **Variables**: mathematical integers (or reals if TOOL uses reals; **specify which**)
- **Statements**: `x = expr`, sequencing, `if (cond) { ... } else { ... }`, 
  `while (cond) { ... }`, `assert(cond)`
- **Expressions**: constants, variables, `+`, `−`, `*` (use only what TOOL supports)
- **Conditions**: `<`, `≤`, `>`, `≥`, `==`, `&&` (use only what TOOL supports)

**Semantics**: Standard imperative semantics. `assert(P)` succeeds iff P holds on 
**all reachable states** at that program point.

**Important**: Ignore external bounds metadata; only executable program text and 
stated initial constraints count.

---

### Example 1: Linear Loop + Linear Assert

```
Init: 0 <= x <= 20

while (x < 10) {
  x = x + 1
}
assert(x > 5)
```

### Example 2: If-Join Precision

```
Init: -5 <= x <= 5

if (x < 0) {
  x = x + 10
} else {
  x = x + 1
}
assert(x >= 1)
```

### Example 3: Polynomial Guard + Assert

```
Init: 0 <= x <= 5, 0 <= y <= 5

while (x*x + y*y < 25) {
  x = x + 1
  y = y + 1
}
assert(x*x + y*y >= 25)
```

Note: Example 3 uses **second-degree polynomial constraints**.

---

## Sections to Complete

### Section 1: API Category

**Determine which applies** (provide evidence for each claim):

**Category A — Full Program Analyzer**:
- TOOL can parse/represent an AST or CFG
- TOOL models `if`, `while`, and assignments
- TOOL runs abstract interpretation (fixpoint) automatically
- TOOL checks assertions against the computed abstract state

**Category B — Numeric Domain Library**:
- TOOL provides abstract domain operations (e.g., interval join, polyhedra operations)
- User must build the program representation, transfer functions, and fixpoint loop
- No built-in program analyzer

**Category C — Neither**:
- TOOL is not suitable for this task (e.g., pure numeric solver, optimization library)

**Mandatory deliverable** for Section 1:

Provide exactly ONE of:

```
(A) [TOOL_NAME] is a FULL PROGRAM ANALYZER:
    - Entry point API: [exact function/class name + signature]
    - Loop handling: [mechanism name with citation]
    - Assertion checking: [exact function name + how it reports results]

(B) [TOOL_NAME] is a NUMERIC DOMAIN LIBRARY:
    - Provided domain types: [list]
    - Missing components: [program representation, fixpoint, transfer functions, ...]
    - User responsibility: [what user must implement]

(C) [TOOL_NAME] is NOT SUITABLE for this evaluation:
    - Reason: [specific technical limitation]
```

---

### Section 2: Encoding the Three Examples

Using TOOL's **own documented examples and API as a guide**, explain how to encode 
each example.

For **each of Examples 1, 2, and 3**, provide:

1. **Encoding sketch**: Show the actual syntax TOOL uses, or write precise pseudo-code 
   matching TOOL's API. Reference TOOL's documentation or published examples.

2. **Abstract domain choice**: Which domain(s) would you use?
   (e.g., intervals, octagons, polyhedra, templates, polynomial/semialgebraic domains)

3. **Feasibility statement**: Can TOOL's documented capabilities encode this example 
   (yes/no/partial)? Cite specific TOOL examples or API docs.

4. **Missing features** (if any): What constructs are not supported? 
   (e.g., nonlinear guards, configurable widening)

**Mandatory deliverable** for Section 2:

For each example, provide a table:

| Aspect | Example 1 | Example 2 | Example 3 |
|--------|-----------|-----------|-----------|
| **Domain choice** | [e.g., Intervals] | [e.g., Polyhedra] | [e.g., Polynomial domain] |
| **Encodable (Y/N/Partial)?** | Y / N / Partial | Y / N / Partial | Y / N / Partial |
| **Evidence** | [cite TOOL docs/example] | [cite TOOL docs/example] | [cite TOOL docs/example] |
| **Missing features** | [list, or "None"] | [list, or "None"] | [list, or "None"] |

---

### Section 3: Polynomial Support

Answer explicitly:

| Question | Answer | Evidence |
|----------|--------|----------|
| Can TOOL represent **nonlinear guards** like `x*x + y*y < 25`? | Yes / Partial / No | [cite] |
| Can TOOL handle **nonlinear assignments**? | Yes / Partial / No | [cite] |
| Can TOOL **prove polynomial assertions**? | Yes / Partial / No | [cite] |

**If TOOL is linear-only**, describe the actual workaround available in TOOL:
- Over-approximation via linearization? (describe algorithm)
- Template domains? (describe)
- SMT integration? (describe how to invoke)
- CEGAR refinement? (describe)

**Clarify**: Does the workaround require **building external infrastructure outside TOOL**, 
or is it built-in?

**Mandatory deliverable** for Section 3:

```
Polynomial support: [YES / PARTIAL / NO]

Reasoning: [1–2 sentences grounded in TOOL's documentation]

Workaround (if NO): [describe, or "No workaround found"]
```

---

### Section 4: Expected Outcomes & Limitations

**For each example**, predict the outcome using these criteria:

**PROVES**: 
- TOOL's documented capabilities and API indicate automatic verification 
  of the assertion for **all reachable states**.
- No user-provided invariants or templates are required.
- Evidence: [cite TOOL example or API docs showing this is supported]

**REFUTES**: 
- TOOL can generate a concrete counterexample violating the assertion.
- Evidence: [cite TOOL docs on counterexample generation]

**UNKNOWN**: 
- TOOL's capabilities are insufficient, incompletely documented, 
  require external components, or evidence is missing.

**If outcome is UNKNOWN**, rank the obstacles (most impactful first):

```
Obstacle (a): Missing language construct
  - Specific construct: [e.g., "polynomial guards"]
  - Impact: Example cannot be encoded
  
Obstacle (b): Insufficient domain precision
  - Domain used: [e.g., Intervals]
  - Why insufficient: [e.g., "Loses precision across join"]
  
Obstacle (c): No built-in fixpoint/loop handling
  - Details: [e.g., "No widening strategy documented"]
  
Obstacle (d): Requires user-provided invariants
  - Details: [e.g., "User must supply loop invariant templates"]
  
Obstacle (e): Incomplete documentation
  - Details: [e.g., "Polynomial support not documented; only linear examples shown"]
```

**Mandatory deliverable** for Section 4:

| Example | Outcome | Primary Obstacle | Evidence |
|---------|---------|------------------|----------|
| Example 1 | PROVES / REFUTES / UNKNOWN | [if UNKNOWN, state (a)–(e)] | [cite TOOL docs/code] |
| Example 2 | PROVES / REFUTES / UNKNOWN | [if UNKNOWN, state (a)–(e)] | [cite TOOL docs/code] |
| Example 3 | PROVES / REFUTES / UNKNOWN | [if UNKNOWN, state (a)–(e)] | [cite TOOL docs/code] |

**Recommended validation approach**:
- Which examples to try first? (Why?)
- What output from TOOL would count as "success"?
- What would you need to iterate on?

---

## Output Structure (Required)

Your response MUST include these sections in order:

### 0. Evidence Checklist
- [ ] TOOL examples read: [list 3+ URLs/paths]
- [ ] Reference benchmarks read: [paths, summaries]
- [ ] Code symbols inspected: [list 5+ symbol names + files]
- [ ] Loop handling evidence found: [yes/no, cite]

### 1. API Capability
[Provide the mandatory deliverable above]

### 2. Encoding the Three Examples
[Provide the mandatory deliverable above]

### 3. Polynomial Support
[Provide the mandatory deliverable above]

### 4. Expected Outcome & Limitations
[Provide the mandatory deliverable above]

### 5. Succinct Report (12 bullets)

Provide **exactly 12 bullets**, each answering one question concisely:

1. API category (A/B/C)?
2. Primary entry point?
3. Loop handling mechanism?
4. Example 1 encodable?
5. Example 2 encodable?
6. Example 3 encodable?
7. Polynomial support (Yes/Partial/No)?
8. Example 1 outcome?
9. Example 2 outcome?
10. Example 3 outcome?
11. Most critical limitation for this comparison?
12. Recommended next validation step?

*Each bullet: ≤ 1 sentence, precise language, no vagueness.*

### 6. Summary Table

Provide **exactly one** markdown table with **minimum 5 rows** (sections 1–4 + overall):

| Section | Question | Answer | Evidence Strength |
|---------|----------|--------|------------------|
| 1 | [TOOL_NAME] is (A/B/C)? | [A/B/C] | High / Medium / Low |
| 2 | Example 1 encodable? | Y / N / Partial | High / Medium / Low |
| 3 | Example 2 encodable? | Y / N / Partial | High / Medium / Low |
| 4 | Example 3 encodable? | Y / N / Partial | High / Medium / Low |
| 5 | Polynomial support? | Yes / Partial / No | High / Medium / Low |
| 6 | Example 1 outcome? | PROVES / REFUTES / UNKNOWN | High / Medium / Low |
| 7 | Example 2 outcome? | PROVES / REFUTES / UNKNOWN | High / Medium / Low |
| 8 | Example 3 outcome? | PROVES / REFUTES / UNKNOWN | High / Medium / Low |
| Overall | Ready for publication? | Yes / Needs revision | High / Medium / Low |

---

## Fairness Reminder (if comparing multiple tools)

If you are using this prompt to evaluate **multiple prior tools** alongside your own:

- Apply the **same evaluation process** to every tool (yours and baselines)
- Use the **same three examples** for all tools
- Allocate **equal time** to reading documentation for each
- Do not favor your tool by:
  - Seeking workarounds for baseline tools while accepting "UNKNOWN" for edge cases in your tool
  - Being less critical of missing features in your tool
  - Using different evidence standards (e.g., "documented only" vs. "inferred")

---

## Glossary

| Term | Definition |
|------|------------|
| **TOOL** | The abstract interpretation tool or library you are evaluating |
| **Entry point** | The primary API function/class a user calls to start analysis |
| **Transfer function** | The rule defining how an abstract domain element transforms under an operation |
| **Fixpoint** | The stable abstract state reached after iterating until convergence |
| **Widening** | An operation that accelerates fixpoint convergence (may lose precision) |
| **Narrowing** | An operation that recovers precision after widening |
| **Abstract domain** | A mathematical structure representing sets of concrete states (e.g., Intervals, Polyhedra) |
