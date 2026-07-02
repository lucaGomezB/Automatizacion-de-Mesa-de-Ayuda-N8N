# MAS Evolution v2: Before and After

**Date:** 2026-05-09
**Version:** 26.05
**Sources:** OxyGent (arxiv 2604.25602), LangGraph, Data-to-Paper (arxiv 2404.17605), MAR (arxiv 2512.20845), Cunningham's Referee 2, Goldsmith-Pinkham's style-guide concept

---

## Phase 3: Writer Evolution

### The Problem

The writer was the most user-visible agent — economists judge writing output most harshly — but it had three critical gaps:

1. **It could draft results it hadn't seen.** The writer would produce prose about findings using predictions from the strategy memo, not actual numbers from the tables. "The coefficient is 4.2 percentage points" when no table file existed yet.

2. **Voice calibration was optional.** If the personal style guide was missing, the writer would fall back to generic academic prose. Generic prose is immediately identifiable as AI-generated.

3. **No traceability.** There was no mechanism to verify that every number in the manuscript actually appeared in an output file. Referees could ask "where does this 4.2 come from?" and nobody could point to a script line.

4. **The writer-critic was accidentally deleted.** The `writer-critic` agent existed since 26.03.4 (208 lines, 8 categories) but was dropped from the working tree in the 26.05 commit during the HTML report pipeline overhaul. The file was referenced across the codebase but no longer present on disk — review invocations that tried to dispatch it silently fell through.

---

### Change 3A: Rebuild and expand writer-critic.md

**BEFORE:** The writer-critic existed since 26.03.4 (208 lines, 8 categories) but was accidentally deleted in the 26.05 commit (HTML report pipeline + guide overhaul). The original had 8 categories: Argument Structure, Claims-Evidence Alignment, Identification Fidelity, Writing Quality, Results Narration, Grammar & Polish, Compilation & LaTeX Quality, Paper-Type Coherence.

What the original lacked:
- No Cold-Read Protocol (added in Phase 4 for all critics)
- No claim-source map verification (INV-22 didn't exist)
- No voice fidelity checking (personal style guide wasn't yet a hard dependency)
- No explicit working-paper-format.md compliance table (deductions were ad hoc)
- No invariant citations in the scoring rubric (critics now must cite "violates INV-X")

**AFTER:** `.claude/agents/writer-critic.md` — rebuilt and expanded (280 lines, 8 categories):

```
1. Structure & Flow — section ordering, paragraph coherence, argument-move fidelity,
   now with paper-type-specific introduction arc checks
2. Claims & Evidence — every claim supported, numbers match tables (INV-11),
   now with claim-source map verification (INV-22)
3. Identification Fidelity — paper matches strategy memo, no overclaiming (INV-8)
4. Writing Quality — now runs the full 24-pattern AI detection check from the
   writer's cleanup pass (4 categories, specific deductions per pattern)
5. LaTeX & Format — now enforces the complete working-paper-format.md deduction
   table (20+ specific checks with point values)
6. Compilation — verifier-lite: compiles, refs resolved, cited tables exist
7. Voice Fidelity (NEW) — sentence length, lexicon, paragraph openings, tone
   vs. personal style guide
8. Notation Consistency (RENAMED) — was "Paper-Type Coherence," now focused
   specifically on notation matching (INV-7)
```

The scoring rubric is now structured as Critical (-15 to -20), Major (-5 to -10), Minor (-1 to -3) with invariant citations. Escalation target: Orchestrator (structural rewrite, not just polish).

**Why it matters:** The rebuilt critic is more rigorous than the original. The old version checked for issues but didn't enforce the full working-paper-format deduction table or require invariant citations. The new version has two entirely new capabilities (voice fidelity and claim-source traceability) and integrates the Cold-Read Protocol from Phase 4. The scoring rubric is now traceable — every deduction points to a specific invariant or format rule.

---

### Change 3B: Style guide becomes a hard dependency

**BEFORE** (writer.md, lines 14-16):
```markdown
If the personal style guide is still a template, draft in the domain-profile
voice and note in your output that running `/write style-guide` would tighten
the match.
```

The writer would proceed with generic academic voice and add a polite footnote suggesting the user calibrate later. In practice, nobody ran the extraction — and every draft sounded like ChatGPT.

**AFTER:**
```markdown
If the personal style guide is still a template: **STOP drafting.** Ask the
user: "Point me to 2-3 of your published papers (.tex or .pdf) so I can
calibrate to your voice. Run `/write style-guide [paper-dir]`." Do NOT
proceed with generic academic voice for any section.
```

The writer now refuses to draft until voice calibration exists. This is a hard gate, not a suggestion.

**Why it matters:** This is the Goldsmith-Pinkham insight operationalized. LLMs are editors, not judgment-outsourcers — but they can only edit toward your voice if they know what your voice sounds like. Making this a hard gate ensures every draft from the system matches the user's actual writing patterns.

---

### Change 3C: Hard gate on results drafting

**BEFORE:** The writer could draft any section at any time. Nothing stopped it from writing "Our main result shows a 4.2 percentage point increase in enrollment" when no table files existed.

**AFTER** (new section in writer.md — "Artifact Prerequisites"):
```markdown
**BEFORE drafting Results or Conclusion:**
- Verify `paper/tables/` contains at least one `.tex` file with actual numbers
- Verify `paper/figures/` contains at least one `.pdf` or `.png` figure
- If either is empty: **STOP.** Report: "Cannot draft Results — no output files
  found in paper/tables/ or paper/figures/. Run `/analyze` first, or point me
  to existing results."
- You MAY draft Introduction, Data, and Empirical Strategy from the strategy
  memo alone.
```

**Why it matters:** This implements the Data-to-Paper principle — information traceability. The writer can draft framing sections (Introduction, Strategy) from the strategy memo, because those sections describe the design, not the findings. But Results and Conclusion require actual numbers. No numbers, no narration.

---

### Change 3D: Artifact Reading Protocol

**BEFORE:** The writer drafted results from the strategy memo's predictions — what the researcher *expected* to find, not what was actually in the tables.

**AFTER** (new section in writer.md):
```markdown
**Before drafting Results:**
1. Read every `.tex` file in `paper/tables/`
2. Read `quality_reports/results_summary.md` (produced by `/analyze`)
3. Extract: point estimates, standard errors, significance levels, sample sizes
4. Narrate from these actual numbers — never from the strategy memo's predictions
5. If a number appears in the text, it must come from an actual output file
```

**Why it matters:** The distinction between "the strategy predicts X" and "the data shows X" is the difference between a proposal and a paper. The writer now reads the actual `.tex` table files before narrating, ensuring every number in the manuscript comes from a real output.

---

### Change 3E: Drafting Checkpoints (Section-Level Gates)

**BEFORE:** The writer drafted the entire paper in one pass, then the critic scored it. A bad framing choice in the introduction cascaded through everything — and the user discovered it only after the full draft was complete.

**AFTER** (new section in writer.md — "Drafting Checkpoints"):
```markdown
**GATE 1: Introduction + Literature positioning**
Present to user. Wait for approval before proceeding.

**GATE 2: Data + Empirical Strategy** (or Model, for structural papers)
Present to user. Wait for approval.

**GATE 3: Results + Robustness + Conclusion**
Requires actual output files (see Artifact Prerequisites above).
Present to user. Wait for approval.
```

**Why it matters:** This implements Agent Laboratory's human-in-the-loop at each stage, adapted for economics. The user approves the framing before the writer commits to a narrative direction. A bad introduction doesn't waste a full draft — it gets caught at Gate 1. This is especially important for the contribution positioning, which is the hardest part to get right and the most costly to get wrong.

---

### Change 3F: Claim-Source Traceability Map

**BEFORE:** No mechanism to trace a number in the manuscript back to the script that produced it.

**AFTER** (new section in writer.md — "Traceability" + new template `templates/claim-source-map.md`):
```markdown
For every numerical claim in the manuscript, maintain a claim-source map:

| Claim              | Location        | Source Script    | Source Line | Table/Figure         |
|--------------------|-----------------|------------------|-------------|----------------------|
| "4.2 pp increase"  | results.tex:L23 | 09_estimation.R  | L142        | main_results.tex:col3|

Save to: quality_reports/claim_source_map_{project}.md
The writer-critic verifies this map against the manuscript (INV-22).
```

**Why it matters:** This is Data-to-Paper's programmatic back-tracing adapted for economics. When a referee asks "where does this number come from?", the answer is immediate: script X, line Y, table Z. The writer-critic checks this map — broken links (script doesn't exist, table column doesn't match) are deductions. INV-22 makes this non-negotiable.

---

### Change 3G: INV-22 added to content-invariants.md

**BEFORE:** 21 content invariants. No invariant covered numerical traceability.

**AFTER:**
```markdown
**INV-22.** Every numerical claim in the manuscript must have an entry in the
claim-source map (quality_reports/claim_source_map_{project}.md) traceable to
a specific script line and output file.
```

The writer-critic's scope in the "How Agents Use This File" table updated from `INV-1 through INV-13` to `INV-1 through INV-13, INV-22`.

**Why it matters:** Making it an invariant means it's non-negotiable — not a suggestion, not a best practice. Every critic that checks invariants will flag a missing claim-source map. This is the enforcement layer for traceability.

---

### Change 3H: Write skill updated

**BEFORE** (write/SKILL.md, Quality Self-Check):
```markdown
- [ ] All tables/figures referenced actually exist in paper/tables/ or paper/figures/
- [ ] Results narrated correctly for output type
```

**BEFORE** (write/SKILL.md, Present to User):
```markdown
Present each section for feedback. Flag items that need attention:
- **TBD items:** Where empirical results are needed but not yet available
- **VERIFY items:** Citations that need user confirmation
- **PLACEHOLDER items:** Effect sizes awaiting final estimates
```

**AFTER** (Quality Self-Check adds 3 items):
```markdown
- [ ] Personal style guide loaded (not template) — or user prompted
- [ ] Claim-source map produced for all numerical claims
- [ ] Results/Conclusion only drafted after verifying actual output files exist
```

**AFTER** (Present to User becomes gate-based):
```markdown
Present sections through drafting gates, pausing for approval at each:

**GATE 1:** Introduction + Literature positioning → present, wait for approval
**GATE 2:** Data + Empirical Strategy (or Model) → present, wait for approval
**GATE 3:** Results + Robustness + Conclusion → present, wait for approval

Flag items that need attention:
- **BLOCKED items:** Results/Conclusion cannot be drafted without output files
- **VOICE items:** Style guide not yet extracted (drafting blocked until resolved)
- **VERIFY items:** Citations that need user confirmation
```

**Why it matters:** The skill file is the user-facing entry point. These changes surface the new gates and hard dependencies to the user — not buried in the agent prompt, but visible in the workflow they interact with.

---

## Phase 1: Artifact Contracts + Permission Registry

### The Problem

Adding or modifying an agent required editing 3-4 files simultaneously. The theorist pair addition in 26.04.3 required edits to `orchestrator.md`, `workflow.md`, `agents.md`, and `quality.md`. The same information — who dispatches whom, who escalates where, what weights apply — was duplicated across files with no single source of truth.

---

### Change 1A: Create permissions.md (Central Registry)

**BEFORE:** Agent dispatch was hardcoded in four places:

`orchestrator.md` (dependency graph — 8 rows):
```markdown
| Phase | Requires | Agents |
|-------|----------|--------|
| Discovery | Research idea | Librarian + librarian-critic, Explorer + explorer-critic |
| Strategy | Literature OR data assessment | Strategist + strategist-critic |
| Execution (Data) | Approved strategy (>= 80) | Data-engineer + coder-critic |
| ...
```

`workflow.md` (dispatch rules — 11 rows):
```markdown
| Task Involves | Agents Dispatched |
|--------------|-------------------|
| Literature/references | librarian + librarian-critic |
| Data sourcing | explorer + explorer-critic |
| ...
```

`agents.md` (escalation routing — 8 rows):
```markdown
| Pair | Escalation Target | What Happens |
|------|-------------------|--------------|
| coder + coder-critic | strategist-critic | Re-evaluates whether... |
| ...
```

`quality.md` (quality weights — 8 rows):
```markdown
| Component | Weight | Source Agent |
|-----------|--------|-------------|
| Literature coverage | 10% | librarian-critic's score of librarian |
| Identification validity | 25% | strategist-critic's score of strategist |
| ...
```

**AFTER:** `.claude/rules/permissions.md` — a single registry where each agent declares everything:

```markdown
## strategist
- **PHASE:** Strategy
- **PARALLEL_GROUP:** strategy
- **REQUIRES:** quality_reports/literature/{project}/ OR quality_reports/data-assessment/{project}/
- **PRODUCES:** quality_reports/strategy/{project}/
  - Required files: strategy_memo.md
  - Required sections: Estimand, Specification, Assumptions, Robustness Plan, Threats
- **CRITIC:** strategist-critic
- **ESCALATION_TARGET:** User — fundamental design question, needs human judgment
- **QUALITY_WEIGHT:** 25% (identification validity)
```

12 agent entries total: librarian, explorer, strategist, theorist, data-engineer, coder, writer, editor, domain-referee, methods-referee, storyteller, verifier.

**Why it matters:** Adding a new agent (e.g., a data-visualizer or a replication-checker) now requires one file change — add an entry to `permissions.md`. No orchestrator surgery. The registry also serves as living documentation: look at one file to understand the entire system's routing. This implements the registry pattern from AWS/Azure dynamic dispatch and OxyGent's permission-driven planning.

---

### Change 1B: Create lifecycle.md (Handoff Validation)

**BEFORE:** No validation between agent handoffs. The orchestrator would dispatch an agent and hope its inputs existed. If the strategy memo was missing a required section, the coder would discover this mid-execution and fail or guess.

**AFTER:** `.claude/rules/lifecycle.md` — three validation stages:

```markdown
## PRE-Dispatch Validation
Before dispatching any agent:
1. REQUIRES artifacts exist (Glob the path, confirm matches)
2. REQUIRES sections present (read the artifact, check headings)
3. If validation fails: do NOT dispatch. Report: "Cannot dispatch [agent]:
   missing [specific artifact or section]"

## POST-Completion Validation
After an agent completes:
1. PRODUCES artifacts exist (verify files created)
2. PRODUCES required sections present (read output, check headings)
3. Critic score recorded in research journal
4. If validation fails: do NOT advance. Re-dispatch with specific gaps.

## FAIL-FAST Principle
Report immediately. Never dispatch with missing inputs. Never advance with
missing outputs.
```

**Why it matters:** This is the difference between "the coder tried and failed because the strategy memo didn't have a Robustness Plan section" and "the orchestrator caught the missing section before dispatching the coder and told the user to run `/strategize` first." Prevention over debugging. This implements MetaGPT's SOP-as-prompt-sequence principle where each agent verifies the previous stage's output.

---

### Change 1C: Orchestrator — replace hardcoded tables with registry references

**BEFORE** (orchestrator.md, Section 1 — 10-line hardcoded dependency table):
```markdown
### 1. Dependency Graph Management
Track which phases can activate based on their inputs:

| Phase | Requires | Agents |
|-------|----------|--------|
| Discovery | Research idea | Librarian + librarian-critic, Explorer + ... |
| Strategy | Literature OR data assessment | Strategist + strategist-critic |
...
```

**AFTER:**
```markdown
### 1. Dependency Graph Management
Read `.claude/rules/permissions.md` for the complete agent registry. Each agent
entry declares: PHASE, PARALLEL_GROUP, REQUIRES, PRODUCES, CRITIC,
ESCALATION_TARGET, and QUALITY_WEIGHT.

Before dispatching any agent:
- Run PRE-dispatch validation per `.claude/rules/lifecycle.md`
- Check that REQUIRES artifacts exist and contain required sections
- If validation fails, report the gap and suggest the prerequisite skill

After any agent completes:
- Run POST-completion validation per `.claude/rules/lifecycle.md`
- Verify PRODUCES artifacts exist with required sections
- Record the critic score in the research journal
```

**BEFORE** (orchestrator.md, Section 3 — 7-line hardcoded escalation table):
```markdown
### 3. Three-Strikes Routing
Track strike count per worker-critic pair. After 3 failed rounds:

| Pair | Escalate To |
|------|-------------|
| Coder + coder-critic | Strategist |
| Writer + writer-critic | Coder or Strategist or User |
...
```

**AFTER:**
```markdown
### 3. Three-Strikes Routing
Track strike count per worker-critic pair. After 3 failed rounds, escalate per
the ESCALATION_TARGET declared in the agent's `permissions.md` entry. See
`.claude/rules/agents.md` Section 3 for the full protocol.
```

**Why it matters:** The orchestrator went from 78 lines with two hardcoded tables to a leaner file that reads its configuration at runtime. The same information exists — it's just in one place now instead of four.

---

### Change 1D: workflow.md — dispatch and dependency tables replaced

**BEFORE** (workflow.md, Section 2 — 11-row dispatch table + 3-line parallel dispatch description):
```markdown
### Agent Dispatch Rules
The Orchestrator selects agents based on what the task requires:

| Task Involves | Agents Dispatched |
|--------------|-------------------|
| Literature/references | librarian + librarian-critic |
| Data sourcing | explorer + explorer-critic |
| Data engineering | data-engineer + coder-critic |
...

### Parallel Dispatch
Independent phases run concurrently:
- Literature and Data discovery run in parallel
- Code and Paper execution run in parallel (after Strategy)
- Presentation can run parallel with Peer Review
```

**AFTER:**
```markdown
### Agent Dispatch Rules
The Orchestrator selects agents by reading `.claude/rules/permissions.md`. Each
agent entry declares its PHASE, REQUIRES, and PARALLEL_GROUP. The Orchestrator
matches the task to the appropriate PHASE and dispatches the agents whose
REQUIRES are satisfied. Before dispatch, it runs PRE-validation per
`.claude/rules/lifecycle.md`.

### Parallel Dispatch
Agents in the same PARALLEL_GROUP run concurrently when their REQUIRES are met.
See `permissions.md` for the complete parallel group table.
```

**BEFORE** (workflow.md, Section 3 — 7-row dependency table):
```markdown
| Phase | Requires | Can Re-enter? |
|-------|----------|---------------|
| Discovery | Research idea | Always — librarian is persistent |
| Strategy | At least one of: literature review OR data assessment | Yes — ... |
...
```

**AFTER:**
```markdown
Phase dependencies are declared in `.claude/rules/permissions.md`. Each agent's
REQUIRES field specifies what must exist before it can be dispatched. The PHASE
field determines sequencing. The PARALLEL_GROUP field determines which agents
can run concurrently.

Re-entry is allowed for all phases except Submission (terminal).
```

The narrative examples ("entering mid-pipeline", "targeted re-entry") are preserved — they explain the *concept*, not the *data*.

---

### Change 1E: agents.md — escalation table replaced

**BEFORE** (agents.md, Section 3 — 8-row escalation routing table):
```markdown
### Escalation Routing

| Pair | Escalation Target | What Happens |
|------|-------------------|--------------|
| coder + coder-critic | strategist-critic | Re-evaluates whether the strategy memo is implementable |
| data-engineer + coder-critic | strategist-critic | Re-evaluates whether the data specification is tractable |
| writer + writer-critic | Orchestrator | Structural rewrite, not just polish |
| strategist + strategist-critic | User | Fundamental design question — needs human judgment |
| theorist + theorist-critic | User | Proof-level disagreement — user adjudicates... |
| librarian + librarian-critic | User | Scope disagreement — user decides breadth vs depth |
| explorer + explorer-critic | User | Data feasibility deadlock — user decides resource trade-offs |
| storyteller + storyteller-critic | User | Talk scope/format disagreement |
```

**AFTER:**
```markdown
### Escalation Routing

Escalation targets are declared in each agent's entry in `.claude/rules/permissions.md`
(ESCALATION_TARGET field). The Orchestrator reads this field when a pair hits 3 strikes.
```

The protocol description (max 3 rounds, logging, clear questions, fresh start post-escalation) is unchanged — those are rules, not data.

---

### Change 1F: quality.md — weight table replaced

**BEFORE** (quality.md, Section 1 — 8-row weight table):
```markdown
### Weighted Aggregation

The overall project score that gates submission (>= 95) is a weighted aggregate:

| Component | Weight | Source Agent |
|-----------|--------|-------------|
| Literature coverage | 10% | librarian-critic's score of librarian |
| Data quality | 10% | explorer-critic's score of explorer |
| Identification validity | 25% | strategist-critic's score of strategist |
| Theory (when present) | 20% | theorist-critic's score of theorist |
| Code quality | 15% | coder-critic's score of coder |
| Paper quality | 25% | Average of domain-referee + methods-referee scores |
| Manuscript polish | 10% | writer-critic's score of writer |
| Replication readiness | 5% | verifier pass/fail (0 or 100) |

**Theory weight applies only to papers with a formal theory section**...
```

**AFTER:**
```markdown
### Weighted Aggregation

The overall project score that gates submission (>= 95) is a weighted aggregate.
Each agent's QUALITY_WEIGHT is declared in `.claude/rules/permissions.md`.

The Orchestrator reads the registry to compute the weighted average:
- Sum each agent's critic score multiplied by its declared weight
- Theory weight applies only when the theorist agent was dispatched
  (see CONDITIONAL flag in `permissions.md`)
- If a component hasn't been scored, exclude it and renormalize remaining weights
```

Gate thresholds (80/90/95), minimum per component, score sources, and when-components-are-missing rules are unchanged.

---

## Phase 2: Pipeline Checkpointing

### The Problem

State lived in three places, none machine-readable: the research journal (append-only prose), the session report (append-only narrative), and git history. After context compression or a new session, the orchestrator had to reconstruct state by reading prose logs and guessing. Information about in-progress work ("the coder-critic pair is on round 2 of 3") was lost.

---

### Change 2A: Create pipeline-state.json template

**BEFORE:** No structured state. Session recovery parsed prose.

**AFTER:** `templates/pipeline-state.json` — a machine-readable schema:

```json
{
  "project": "",
  "phase": "",
  "last_updated": "",
  "agents_completed": [
    { "agent": "", "critic": "", "score": null, "artifact": "", "rounds": 0, "timestamp": "" }
  ],
  "agents_in_progress": [
    { "agent": "", "critic": "", "current_round": 0, "max_rounds": 3,
      "last_score": null, "issues_remaining": [] }
  ],
  "agents_pending": [],
  "artifacts": {},
  "overall_score": null,
  "blocked_by": null
}
```

Active instances live at `quality_reports/pipeline_state.json`.

**Why it matters:** The research pipeline now survives session boundaries. Start a project Monday, come back Wednesday, pick up exactly where you left off — the system knows the strategist scored 85 and the coder is on round 2 with two issues remaining. This implements LangGraph-style checkpointing in a file-based architecture.

---

### Change 2B: Create execution-trace.md template

**BEFORE:** No post-run visualization. To understand what happened during a pipeline run, you read prose logs.

**AFTER:** `templates/execution-trace.md` — a structured post-run report with a Mermaid execution graph, agent invocation table (agent, critic, rounds, score, duration, status), escalation events, artifacts produced, and a pipeline summary.

**Why it matters:** This is the diagnostic layer. When something goes wrong — or right — you can see the full execution path, not reconstruct it from narrative logs. The orchestrator generates a trace after every multi-agent skill completion.

---

### Change 2C: Orchestrator Section 7 — Pipeline State Management

**BEFORE:** The orchestrator had 6 responsibilities (dependency graph, dispatch, three-strikes, rule enforcement, peer review, user communication). No state management.

**AFTER** (new section in orchestrator.md):
```markdown
### 7. Pipeline State Management

Maintain structured pipeline state in `quality_reports/pipeline_state.json`.

**Write triggers:**
- After every agent completion: update agents_completed, move from agents_in_progress
- After every critic score: update the score and round count
- After every phase transition: update the phase field
- After escalation: update blocked_by

**Read triggers:**
- On session start: read pipeline_state.json as the FIRST action in session
  recovery, before reading prose logs

**Execution trace:**
After completing a multi-agent skill, generate an execution trace and save to
quality_reports/traces/YYYY-MM-DD_trace.md

**Relationship to research journal:**
- pipeline_state.json is structured, machine-readable, and overwritten
- research_journal.md is narrative, append-only, and human-readable
- Both are maintained — they serve different purposes
```

---

### Change 2D: logging.md — Pipeline State section added

**BEFORE:** Two logging mechanisms: Session Report and Research Journal. Both prose, both append-only.

**AFTER** (new Section 3):
```markdown
## Pipeline State

Structured pipeline state lives in `quality_reports/pipeline_state.json`.

**Triggers:**
- Created when the first agent in a pipeline completes
- Updated after every agent completion, critic score, or phase transition
- Read as the first action in session recovery

**Relationship to research journal:**
- The research journal is narrative context for humans: "what happened and why"
- The pipeline state is structured context for the orchestrator: "where are we"
```

---

### Change 2E: workflow.md — Session Recovery updated

**BEFORE:**
```markdown
### Session Recovery
After compression or a new session, in order:
0. **Read the most recent checkpoint artifacts:** tail of SESSION_REPORT.md...
1. Read CLAUDE.md + most recent plan...
```

**AFTER:**
```markdown
### Session Recovery
After compression or a new session, in order:
0. **Read pipeline state:** If quality_reports/pipeline_state.json exists,
   read it to determine: current phase, completed agents (with scores),
   in-progress agents (with round count and remaining issues), pending agents,
   and any blocking conditions. This is faster and more reliable than
   reconstructing state from prose logs.
1. **Read the most recent checkpoint artifacts:** tail of SESSION_REPORT.md...
2. Read CLAUDE.md + most recent plan...
```

Pipeline state is now Step 0 — read structured data first, then fill in narrative context.

---

## Phase 4: Cold-Read + Dual Critics

### The Problem

Critics received implicit context from the orchestrator — they knew which round this was, what the worker struggled with, and could read the research journal for prior context. This created sympathy bias: a critic that knows the worker tried 3 times unconsciously lowers the bar. A single critic also evaluates along one dimension — the coder-critic checks code quality but not whether the code implements the strategy.

---

### Change 4A: Cold-Read Protocol added to all 7 critics

**BEFORE:** Critics had no explicit context policy. They received whatever the orchestrator sent, including round history and prior feedback.

**AFTER** (identical section added to all 7 critic agents — librarian-critic, explorer-critic, strategist-critic, theorist-critic, coder-critic, storyteller-critic, writer-critic):

```markdown
## Cold-Read Protocol

You receive ONLY:
- The artifact to evaluate
- Your scoring rubric (this file)
- The severity level (from the orchestrator)
- The relevant content invariants

You do NOT receive:
- What round this is (you don't know if this is attempt 1 or 3)
- What the worker struggled with
- The research journal
- Prior critic reports on this artifact
- Any context about the worker's intent or process

Evaluate the artifact as if seeing it for the first time. Every time.
```

The section is placed immediately after the identity declaration ("You are a CRITIC..."), before "Your Task" — ensuring it's read before any task-specific instructions.

**Why it matters:** This implements Cunningham's adversarial independence principle. A fresh evaluation on every round means the score reflects the artifact's quality, not the worker's effort. The orchestrator retains round context and communicates it to workers (telling them what to fix), but the critics never see this — they evaluate cold. Combined with MAR's multi-persona critique finding (single-agent self-reflection produces "degeneration of thought"), this ensures evaluation integrity.

---

### Change 4B: Orchestrator Section 8 — Dual-Critic Dispatch

**BEFORE:** One critic per worker. The coder-critic checked code quality but not whether the code implemented the strategy. The writer-critic (now that it exists) checks prose but not claims-strategy alignment.

**AFTER** (new section in orchestrator.md):
```markdown
### 8. Dual-Critic Dispatch

For artifacts that gate major phase transitions, dispatch two critics with
different evaluation lenses.

| Gate Artifact       | Primary Critic                  | Secondary Lens                       |
|---------------------|---------------------------------|--------------------------------------|
| Strategy memo       | strategist-critic (identification) | coder-critic (implementability)   |
| Main results (code) | coder-critic (code quality)     | strategist-critic (strategy alignment)|
| Final manuscript    | writer-critic (prose quality)   | strategist-critic (claims-strategy)  |

**Synthesis rules:**
- Both >= 80: pass
- One < 80: worker fixes issues from the failing critic, both re-evaluate
- Both < 80: escalate

**Scope:**
Dual-critic dispatch is OPTIONAL and activates only for gate artifacts in the
full pipeline (/new-project). Standalone skill invocations use single critics.

**Cold-read enforcement:**
Neither critic sees the other's report. The orchestrator synthesizes both scores
independently.
```

**Why it matters:** The strategy memo is the most consequential artifact in the pipeline — everything downstream depends on it. Having the strategist-critic check identification validity AND the coder-critic check implementability catches the common failure mode: "the design is theoretically valid but computationally intractable." Similarly, the manuscript gets checked for both prose quality (writer-critic) and claims-strategy alignment (strategist-critic). Dual critics only fire for gate artifacts, keeping token cost bounded.

---

## Phase 5: Cross-Project Learning Loop

### The Problem

Learning was manual and per-project. When a pattern worked across 3 projects (e.g., "strategist-critic always flags missing event studies"), it should become a rule — not a memory entry that exists in one fork. Good patterns were lost because nobody flagged them.

---

### Change 5A: Orchestrator Section 9 — Learning Loop

**BEFORE:** The pipeline completed and presented results. No pattern analysis.

**AFTER** (new section in orchestrator.md):
```markdown
### 9. Learning Loop (Post-Pipeline)

After completing a multi-agent skill, review the execution trace for patterns:

1. **HIGH-PERFORMANCE patterns:** Agent-critic pairs that scored >= 90 on first
   pass. What did the worker do right? Is it replicable?

2. **FRICTION patterns:** Pairs that hit 3 strikes. What was the root cause?

3. **USER ESCALATION patterns:** What questions were escalated to the user?
   Could the system have resolved them with better context or rules?

Surface findings as "Suggested Learnings" at the end of the pipeline summary.
**NEVER auto-append to MEMORY.md.** Present suggestions. User approves or rejects.
```

**Why it matters:** This implements OxyGent's closed-loop learning in a human-supervised architecture. The system identifies patterns — the user decides what to promote. No autonomous self-modification. Over time, the template gets smarter with every paper.

---

### Change 5B: meta-governance.md — Learning Promotion

**BEFORE:** The meta-governance rule had one section: "The One Rule" (would another researcher benefit? → commit).

**AFTER** (new section):
```markdown
## Learning Promotion

When a learning has been validated across 3+ projects (confirmed by user):

| Pattern Type | Promotion Target |
|-------------|-----------------|
| PATTERN (replicable success) | New best-practice in relevant agent's protocol |
| FRICTION (recurring failure) | Agent prompt revision or rubric adjustment |
| HIGH-PERF (consistent excellence) | New content invariant (INV-XX) or rule addition |

**Protocol:**
1. The orchestrator identifies a pattern recurring across 3+ traces
2. The orchestrator drafts the specific change
3. The user reviews and approves or rejects
4. If approved, the change is committed to the template repo

**Constraint:** Promotion ALWAYS requires user approval.
```

**Why it matters:** This closes the loop between usage and template evolution. Individual project learnings stay local. But when the same pattern appears across 3+ projects, it becomes a candidate for template promotion — a new invariant, a rubric adjustment, an agent prompt improvement. The template itself gets better with each paper written.

---

### Change 5C: logging.md — Trace Analysis

**BEFORE:** Logging was write-only. Logs were written but never systematically read for patterns.

**AFTER** (new subsection under Pipeline State):
```markdown
### Trace Analysis

After pipeline completion, read the execution trace and the last 5 traces
(if available in quality_reports/traces/) to identify recurring patterns.

Analysis covers:
- Agents with first-pass >= 90 (HIGH-PERF)
- Agents that hit 3 strikes (FRICTION)
- Escalations to user (USER ESCALATION)
- Agents whose scores improved most between rounds (learning curve)

Save analysis to: quality_reports/traces/analysis_{date}.md
```

**Why it matters:** The trace analysis turns execution history into actionable intelligence. Instead of asking "what happened?", the system asks "what keeps happening?" — and surfaces the answer for the user to act on.

---

## Summary of Changes

### New Files (6)

| File | Lines | Purpose |
|------|-------|---------|
| `.claude/agents/writer-critic.md` | ~280 | Rebuilt + expanded critic — 8 categories, cold-read, voice fidelity, INV-22 |
| `.claude/rules/permissions.md` | ~140 | Central agent registry (12 entries) |
| `.claude/rules/lifecycle.md` | ~60 | Handoff validation protocol |
| `templates/pipeline-state.json` | ~25 | Resumable pipeline state schema |
| `templates/execution-trace.md` | ~35 | Post-run visualization template |
| `templates/claim-source-map.md` | ~20 | Numerical claim traceability template |

### Modified Files (15)

| File | Phase | What Changed |
|------|-------|--------------|
| `writer.md` | 3 | Hard gates, style enforcement, artifact reading, drafting checkpoints, traceability |
| `content-invariants.md` | 3 | INV-22 added, writer-critic scope updated |
| `write/SKILL.md` | 3 | Quality self-check + gate-based presentation |
| `orchestrator.md` | 1,2,4,5 | Registry references + Sections 7 (state), 8 (dual-critic), 9 (learning) |
| `workflow.md` | 1,2 | Registry references + pipeline state in session recovery |
| `agents.md` | 1 | Escalation table → registry reference |
| `quality.md` | 1 | Weight table → registry reference |
| `logging.md` | 2,5 | Pipeline state section + trace analysis |
| `meta-governance.md` | 5 | Learning promotion protocol |
| `librarian-critic.md` | 4 | Cold-read protocol |
| `explorer-critic.md` | 4 | Cold-read protocol |
| `strategist-critic.md` | 4 | Cold-read protocol |
| `theorist-critic.md` | 4 | Cold-read protocol |
| `coder-critic.md` | 4 | Cold-read protocol |
| `storyteller-critic.md` | 4 | Cold-read protocol |

### Literature Sources

| Paper | Key Concept Used |
|-------|-----------------|
| OxyGent (arxiv 2604.25602) | Permission-driven dispatch, OxyBank learning loop |
| Data-to-Paper (arxiv 2404.17605) | Claim-source traceability |
| MAR (arxiv 2512.20845) | Multi-persona critique, degeneration of thought |
| Cunningham's Referee 2 | Adversarial independence (cold-read) |
| Goldsmith-Pinkham | Personal style guide as hard dependency |
| LangGraph | Typed state checkpointing |
| MetaGPT (arxiv 2308.00352) | SOP-as-prompt with stage verification |
| Agent Laboratory (arxiv 2501.04227) | Human-in-the-loop at each stage |
| MasRouter (ACL 2025) | Capability-based task-to-agent routing |
