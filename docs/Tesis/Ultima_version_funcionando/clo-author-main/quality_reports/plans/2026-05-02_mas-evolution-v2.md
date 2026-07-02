# Plan: clo-author MAS Evolution v2

**Status:** DRAFT
**Date:** 2026-05-02
**Supersedes:** `clo-author-mas-evolution-plan.md` (2026-04-29)

---

## Context

clo-author is the most complete AI-assisted research tool in economics — 20 agents, 11 skills, dependency-driven orchestration, worker-critic pairs, journal-calibrated peer review. Nobody else has this: Goldsmith-Pinkham has a workflow (no agents, no quality gates), Cunningham has an adversarial audit (no pipeline), OpenAI Prism has a writing UX (no data analysis). But the system has real brittleness in three areas: (1) the orchestrator hardcodes all routing, (2) there's no resumable state across sessions, and (3) the writer — the most user-visible agent — produces generic output that doesn't match the user's voice and can draft results it hasn't actually seen.

This plan draws on 10 MAS papers (OxyGent, PaperOrchestra, CycleResearcher, Data-to-Paper, Agent Laboratory, MetaGPT, CAMEL, MAR, SciAgents, PaperDebugger), competitive analysis (Goldsmith-Pinkham, Cunningham, Korinek, OpenAI Prism), and orchestration patterns from CrewAI, LangGraph, OpenAI Agents SDK, AWS/Azure registry architectures, and MasRouter (ACL 2025).

Each phase is independently valuable, backward compatible, and documented for public discussion.

---

## Phase 1: Artifact Contracts + Permission Registry

### BEFORE

The orchestrator hardcodes three things across three files:

**Dependency graph** (`orchestrator.md`, lines 15-26):
```
| Phase | Requires | Agents |
| Discovery | Research idea | Librarian + librarian-critic, Explorer + explorer-critic |
| Strategy | Literature OR data assessment | Strategist + strategist-critic |
...
```

**Dispatch rules** (`workflow.md`, Section 2, lines 93-109):
```
| Task Involves | Agents Dispatched |
| Literature/references | librarian + librarian-critic |
| Data sourcing | explorer + explorer-critic |
...
```

**Escalation routing** (`agents.md`, Section 3, lines 98-107):
```
| Pair | Escalation Target |
| coder + coder-critic | strategist-critic |
| writer + writer-critic | Orchestrator |
...
```

Adding a new agent (e.g., the theorist pair added in v4.2.0) requires editing all three files plus the quality weights in `quality.md`.

### THE PROBLEM

- **Fragile coupling:** Adding or modifying an agent requires touching 3-4 files. The theorist pair addition in v4.2.0 is a case study — it required edits to orchestrator.md, workflow.md, agents.md, and quality.md.
- **No artifact schema:** The strategist produces a "strategy memo" but there's no formal contract for what sections it must contain. The coder reads it hoping the right sections exist. When they don't, the coder guesses or fails silently.
- **No validation at handoff:** Nothing checks that an agent's output actually matches what the next agent expects.

### THE LITERATURE

- **OxyGent** (arxiv 2604.25602): Permission-driven dynamic planning — agents declare capabilities, the planner resolves dependencies at runtime. "Hot-swappable" components.
- **AWS/Azure dynamic dispatch patterns**: A registry tracks agents with capability descriptors. The orchestrator resolves which agent to invoke based on task attributes, not hardcoded tables.
- **MasRouter** (ACL 2025): LLM classifies tasks and routes to best-fit agent based on capability metadata and past performance.
- **LangGraph**: Typed state objects flow between nodes with explicit schemas — each node declares what it produces and consumes.
- **MetaGPT** (arxiv 2308.00352): SOPs encoded as prompt sequences where each agent verifies the previous stage's output before proceeding.

### THE CHANGE

**Create:** `.claude/rules/permissions.md`

Central registry where each agent entry declares:

```markdown
## strategist
- **PHASE:** Strategy
- **PARALLEL_GROUP:** strategy
- **REQUIRES:** [quality_reports/literature/ OR quality_reports/data-assessment/]
- **PRODUCES:** quality_reports/strategy_memo_{project}.md
  - Required sections: Estimand, Specification, Assumptions, Robustness Plan, Threats
- **CRITIC:** strategist-critic
- **ESCALATION_TARGET:** User
- **QUALITY_WEIGHT:** 25% (identification validity)
```

**Create:** `.claude/rules/lifecycle.md`

Handoff validation protocol:
- **PRE:** Before dispatching an agent, verify its REQUIRES artifacts exist and contain required sections
- **POST:** After agent completes, verify its PRODUCES artifact exists and contains required sections
- **FAIL-FAST:** If PRE validation fails, report missing inputs with clear message instead of dispatching

**Modify:**
- `orchestrator.md` — Replace hardcoded tables (lines 15-26, 36-46) with: "Read `permissions.md` to determine dependencies, dispatch rules, and escalation targets"
- `workflow.md` — Replace hardcoded dispatch table (Section 2, lines 93-109) and phase dependency table (Section 3) with registry references
- `agents.md` — Replace hardcoded escalation table (Section 3, lines 98-107) with registry reference
- `quality.md` — Replace hardcoded weight table with registry reference (each agent entry declares its own weight)

**Verify:**
- Add a fake agent entry to `permissions.md` → orchestrator should recognize it
- Remove a REQUIRES artifact → orchestrator should refuse to dispatch with clear message
- Run `/new-project` → same execution graph as before (backward compatibility)

### WHY THIS MATTERS

For economists using clo-author: you can now add specialized agents (e.g., a "data-visualizer" that produces publication-quality figures, or a "replication-checker" that verifies external validity) by adding one registry entry and one agent file. Zero orchestrator surgery. The registry also serves as living documentation — look at one file to understand the entire system's routing.

For the MAS literature: this implements the registry pattern validated by AWS, Azure, and MasRouter in a Claude Code subagent architecture where agents are markdown files, not code modules.

---

## Phase 2: Pipeline Checkpointing

### BEFORE

State lives in three places, none resumable:
- **Research journal** (`quality_reports/research_journal.md`): append-only text log of agent invocations
- **Session report** (`SESSION_REPORT.md`): append-only narrative of what happened
- **Git history**: commits capture file changes but not pipeline position

After context compression or a new session, the orchestrator must reconstruct state by reading the journal, session report, git log, and inferring where things stand. This is slow, error-prone, and loses information about in-progress work (e.g., "the coder-critic pair is on round 2 of 3").

### THE PROBLEM

- **No resume:** If a session ends mid-pipeline, the next session starts over or guesses
- **No structured diagnostics:** When something fails, you read prose logs to figure out what happened
- **Round tracking is ephemeral:** The 3-strike protocol resets if the session ends between rounds

### THE LITERATURE

- **LangGraph**: Built-in checkpointing — every state transition is persisted, enabling time-travel debugging, human-in-the-loop pauses, and failure recovery. The key insight: checkpoints are not just logs, they're resumable state.
- **OxyGent** (arxiv 2604.25602): Execution traces with observability — not just what happened, but the full execution graph with timing, scores, and decision points.
- **CrewAI Flows**: Event-driven state with explicit distinction between ephemeral state (within a run) and persistent state (across runs).

### THE CHANGE

**Create:** `templates/pipeline-state.json`

Schema for resumable pipeline state:

```json
{
  "project": "commute",
  "phase": "execution",
  "last_updated": "2026-05-02T14:30:00Z",
  "agents_completed": [
    {
      "agent": "librarian",
      "critic": "librarian-critic",
      "score": 88,
      "artifact": "quality_reports/literature/commute/annotated_bibliography.md",
      "rounds": 1,
      "timestamp": "2026-05-01T10:00:00Z"
    }
  ],
  "agents_in_progress": [
    {
      "agent": "coder",
      "critic": "coder-critic",
      "current_round": 2,
      "max_rounds": 3,
      "last_score": 72,
      "issues_remaining": ["missing robustness checks", "no event study plot"]
    }
  ],
  "agents_pending": ["writer"],
  "artifacts": {
    "quality_reports/strategy_memo_commute.md": {"exists": true, "score": 85},
    "paper/tables/": {"exists": false}
  },
  "overall_score": null,
  "blocked_by": "coder-critic score < 80"
}
```

**Create:** `templates/execution-trace.md`

Post-run visualization:

```markdown
## Execution Trace — [Project] — [Date]

### Execution Graph (Mermaid)
[Mermaid flowchart of actual execution path]

### Agent Invocation Table
| Agent | Rounds | Final Score | Duration | Status |
|-------|--------|-------------|----------|--------|

### Escalation Events
[Any 3-strike escalations with context]

### Artifacts Produced
[List with paths and scores]
```

**Modify:**
- `orchestrator.md` — Add "Pipeline State Management" responsibility: write `pipeline_state.json` after every agent completion; read it on session start to resume
- `logging.md` — Add Section 4 "Pipeline State" with location, triggers, relationship to research journal (journal is narrative; state is structured)
- `workflow.md` — Add to "Session Recovery" (Section 5): first action is read `pipeline_state.json`, not reconstruct from prose

**Verify:**
- Run `/discover lit` → `pipeline_state.json` created with librarian entry
- Kill session mid-pipeline → restart → orchestrator reads state and resumes from correct position
- Run `/new-project` end-to-end → execution trace appears in `quality_reports/traces/`

### WHY THIS MATTERS

For economists: your research pipeline survives session boundaries. Start a project Monday, come back Wednesday, pick up exactly where you left off — the system knows the strategist scored 85 and the coder is on round 2 with two issues remaining. No more "let me figure out what happened last time."

For the MAS literature: this implements LangGraph-style checkpointing in a file-based architecture, proving the pattern works without a runtime engine.

---

## Phase 3: Writer Evolution

### BEFORE

The writer agent (`writer.md`) has sophisticated argument-move templates and a cleanup pass, but:

1. **Can draft with placeholders.** The commute paper plan explicitly says "Results section uses `[TBD]` throughout since we have no data yet." The writer produces prose about results it hasn't seen.
2. **Style guide is optional.** The writer checks if `personal-style-guide.md` has "real content" and if not, defaults to generic academic voice. The extraction machinery exists (`/write style-guide`) but isn't enforced.
3. **Doesn't read actual output files.** Drafts from the strategy memo and "approved code" concept, not from the actual `.tex` table files and figures.
4. **No section-level checkpoints.** Drafts the entire paper, then the critic scores it. One bad framing choice in the introduction cascades through everything.
5. **Writer-critic doesn't check voice.** Scores structure, claims, identification, LaTeX — but not whether the draft sounds like the user.

### THE PROBLEM

The writer is the most user-visible agent, and it produces the output economists judge most harshly. Generic academic prose that doesn't match the user's voice is immediately identifiable as AI-generated. Writing results without actual numbers produces hollow narration. And a full-paper-then-score loop wastes entire drafts when the introduction framing is wrong.

### THE LITERATURE

- **Goldsmith-Pinkham** (Yale/Princeton mini-series): The personal style guide concept — feed Claude your own published papers so it writes in your voice, not generic AI. His key insight: LLMs are editors, not judgment-outsourcers.
- **Data-to-Paper** (arxiv 2404.17605): Programmatic back-tracing of every claim to its data source and code line. Information traceability is essential for economics where referees demand reproducibility.
- **Agent Laboratory** (arxiv 2501.04227): Human-in-the-loop at each stage, not just the end. Domain judgment about identification and framing cannot be fully automated.
- **PaperOrchestra** (arxiv 2604.05018): Separation between "raw materials" (data, notes, results) and "manuscript generation." The system accepts messy inputs and orchestrates them into structured LaTeX.
- **CycleResearcher** (arxiv 2411.00816): Paired researcher-reviewer iterative loop. CycleReviewer achieves 26.89% MAE reduction vs. individual human reviewers.

### THE CHANGE

**Modify `writer.md`:**

1. **Hard gate on results.** Add to "Your Task" section:
   ```
   BEFORE drafting Results or Conclusion:
   - Verify paper/tables/ contains at least one .tex file with actual numbers
   - Verify paper/figures/ contains at least one .pdf figure
   - If either is empty: STOP. Report: "Cannot draft Results — no output files found.
     Run /analyze first, or point me to existing results."
   - You MAY draft Introduction, Data, and Empirical Strategy from the strategy memo alone.
   ```

2. **Style guide as hard dependency.** Add to the voice calibration section:
   ```
   If personal-style-guide.md is still a template:
   - STOP drafting.
   - Ask the user: "Point me to 2-3 of your published papers (.tex or .pdf)
     so I can calibrate to your voice. Run /write style-guide [paper-dir]."
   - Do NOT proceed with generic academic voice for any section.
   ```

3. **Writer reads artifacts directly.** Add new section "Artifact Reading Protocol":
   ```
   Before drafting Results:
   1. Read every .tex file in paper/tables/
   2. Read results_summary.md (produced by /analyze)
   3. Extract: point estimates, standard errors, significance, sample sizes
   4. Narrate from these actual numbers — never from the strategy memo's predictions
   ```

4. **Section-level human approval.** Add new section "Drafting Checkpoints":
   ```
   Draft sections in this order, pausing for user approval at each gate:

   GATE 1: Introduction + Literature positioning
   → Present to user. Wait for approval before proceeding.
   → User may redirect framing, contribution positioning, or literature emphasis.

   GATE 2: Data + Empirical Strategy (or Model, for structural papers)
   → Present to user. Wait for approval.
   → User may adjust sample restrictions, variable definitions, specification details.

   GATE 3: Results + Robustness + Conclusion
   → Requires actual output files (hard gate above).
   → Present to user. Wait for approval.
   ```

5. **Claim-source map.** Add new section "Traceability":
   ```
   For every numerical claim in the manuscript, maintain a claim-source map:

   | Claim | Location | Source Script | Source Line | Table/Figure |
   |-------|----------|---------------|-------------|--------------|
   | "4.2 pp increase" | results.tex:L23 | 09_estimation.R | L142 | main_results.tex:col3 |

   Save to: quality_reports/claim_source_map_{project}.md
   The writer-critic verifies this map against the manuscript.
   ```

**Modify `writer-critic.md`:**

6. **Add voice fidelity check.** New scoring category (Category 9):
   ```
   ### 9. Voice Fidelity (if personal-style-guide.md exists)

   Compare the draft against the style guide:
   - Sentence length distribution: does median match within ±3 words?
   - Lexicon: are "words the author avoids" absent? Are "words the author uses" present?
   - Paragraph openings: do they match the author's documented patterns?
   - Hedging patterns: does hedging match the author's style (not more, not less)?
   - Tone: does the draft match the documented tone markers?

   | Issue | Deduction |
   |-------|-----------|
   | Uses 3+ words from "author avoids" list | -5 per (max -15) |
   | Sentence length median off by >5 words | -5 |
   | Paragraph openings don't match patterns | -3 per (max -9) |
   | Tone mismatch (e.g., bombastic when author is dry) | -10 |
   ```

7. **Add claim-source verification.** New check in Category 2 (Claims-Evidence):
   ```
   - Claim-source map exists? If not, -15
   - Every numerical claim in text has a map entry? -5 per missing
   - Map entries point to files that exist? -10 per broken link
   ```

**Modify `content-invariants.md`:**

8. **Add INV-22:**
   ```
   INV-22. Every numerical claim in the manuscript must have an entry in the
   claim-source map (quality_reports/claim_source_map_{project}.md) traceable
   to a specific script line and output file.
   ```

**Verify:**
- Invoke `/write results` with empty `paper/tables/` → writer refuses with clear message
- Invoke `/write intro` with template style guide → writer asks for papers
- Invoke `/write results` with populated tables → writer reads actual numbers and narrates them
- Check claim-source map against manuscript → all claims traced
- Writer-critic scores a draft → voice fidelity category appears in report

### WHY THIS MATTERS

For economists: the writer now produces prose that sounds like *you*, not like a machine. It refuses to write results it hasn't seen (no more hollow "[TBD]" narration). Every number in the paper traces back to a specific line of code. And you approve the framing before the writer commits to a narrative direction — catching bad choices early instead of rewriting entire drafts.

For the MAS literature: this combines Goldsmith-Pinkham's style-guide insight with Data-to-Paper's traceability and Agent Laboratory's stage-gated human-in-the-loop, adapted for economics-specific concerns (identification framing, causal language, referee expectations).

---

## Phase 4: Cold-Read + Dual Critics

### BEFORE

Critics receive the artifact plus implicit context from the orchestrator's dispatch — they know which round this is, what the worker struggled with, and can read the research journal for prior context. This creates two problems:

1. **Sympathy bias:** A critic that knows the worker tried 3 times unconsciously lowers the bar.
2. **Single-perspective evaluation:** Each worker has exactly one critic. The coder-critic checks code quality but not whether the code implements the strategy. The strategist-critic checks identification but not computational feasibility.

### THE PROBLEM

- **Context contamination:** Critics that share context with workers produce more lenient scores. Cunningham's "Referee 2" protocol spawns a completely fresh Claude instance — no prior context — for exactly this reason.
- **Blind spots:** A single critic evaluates along one dimension. The MAR paper (arxiv 2512.20845) shows that single-agent self-reflection produces "degeneration of thought" — the same errors repeated. Multiple critic personas with diverse lenses, synthesized by a judge, produce stronger evaluation.

### THE LITERATURE

- **Cunningham's Referee 2** (MixtapeTools): Adversarial independence — a fresh Claude instance (new terminal, no prior context) creates its own replication scripts and writes formal referee reports. The reviewer never shares context with the author.
- **MAR: Multi-Agent Reflexion** (arxiv 2512.20845): Multi-persona debaters generate diverse reflections, then a judge synthesizes. Achieves 47% EM on HotPotQA and 82.7% on HumanEval, surpassing single-agent reflexion. Key finding: never let one agent critique itself in isolation.
- **CycleResearcher** (arxiv 2411.00816): CycleReviewer achieves 26.89% MAE reduction vs. individual human reviewers. The paired researcher-reviewer loop is the strongest validated pattern for quality control.

### THE CHANGE

**Modify all 7 critic agents** (librarian-critic, explorer-critic, strategist-critic, theorist-critic, coder-critic, writer-critic, storyteller-critic):

1. **Cold-read protocol.** Add to each critic's header:
   ```
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

2. **Round-aware feedback stays with the orchestrator.** The orchestrator tracks rounds and prior issues internally. When re-dispatching a worker after a failed round, the orchestrator tells the worker what to fix (from the critic's report). But the critic on the next round sees a fresh artifact with no history.

**Modify `orchestrator.md`:**

3. **Dual-critic dispatch for gate artifacts.** Add new section:
   ```
   ## Dual-Critic Dispatch

   For artifacts that gate major phase transitions, dispatch two critics
   with different evaluation lenses:

   | Gate Artifact | Primary Critic | Secondary Lens |
   |---------------|---------------|----------------|
   | Strategy memo | strategist-critic (identification) | coder-critic (implementability) |
   | Main results (code) | coder-critic (code quality) | strategist-critic (strategy alignment) |
   | Final manuscript | writer-critic (prose quality) | strategist-critic (claims-strategy match) |

   The orchestrator synthesizes both scores:
   - Both >= 80 → pass
   - One < 80 → worker fixes issues from the failing critic, both re-evaluate
   - Both < 80 → escalate

   Dual-critic is OPTIONAL and activated only for gate artifacts in the full
   pipeline. Standalone skill invocations use single critics as before.
   ```

**Verify:**
- Run a critic on a revised artifact → critic report shows no awareness of prior rounds
- Run dual-critic on a strategy memo → two reports with different perspectives, orchestrator synthesizes
- Compare scores: cold-read critics should produce tighter (less lenient) scores on flawed artifacts

### WHY THIS MATTERS

For economists: your critics now evaluate your work the way actual referees do — cold, with no sympathy for how hard you worked on it. And for the most important artifacts (strategy memo, main results, manuscript), you get two perspectives: one checking the idea, one checking the execution. This catches the blind spots that a single critic misses.

For the MAS literature: this combines Cunningham's adversarial independence with MAR's multi-persona critique in a practical architecture that scales cost-efficiently (dual critics only for gate artifacts).

---

## Phase 5: Cross-Project Learning Loop

### BEFORE

Learning is manual and per-project:
- `MEMORY.md` stores `[LEARN]` entries appended by hand
- Each project fork starts with the template's default MEMORY.md
- No mechanism to identify patterns across projects
- No automated pattern detection from execution traces

### THE PROBLEM

- **No institutional memory:** When a pattern works across 3 projects (e.g., "strategist-critic always flags missing event studies"), it should become a rule, not a memory entry that exists in one fork.
- **Manual curation:** The user must notice patterns and manually tag `[LEARN]`. Good patterns are lost because nobody flagged them.
- **No feedback to template:** Learnings stay in individual project forks. The template itself doesn't improve from usage.

### THE LITERATURE

- **OxyGent's OxyBank** (arxiv 2604.25602): AI asset management platform that captures online execution traces, applies automated rewarding and human-in-the-loop annotation, and feeds domain-specific knowledge back into the system. Closed-loop learning.
- **CrewAI Memory** (2025 rebuild): Separates ephemeral state (within a run) from persistent memory (across runs). Unified Memory class with distinct stores.
- **SciAgents** (arxiv 2409.05556): Knowledge-graph backbone lets the system find non-obvious connections at scale. The graph accumulates over time.

### THE CHANGE

**Modify `orchestrator.md`:**

1. **Post-pipeline pattern detection.** Add new section:
   ```
   ## Learning Loop (Post-Pipeline)

   After completing a multi-agent skill (/new-project, /analyze, /write full),
   review the execution trace for:

   1. HIGH-PERFORMANCE patterns: Agent-critic pairs that scored >= 90 on first pass.
      What did the worker do right? Is it replicable?

   2. FRICTION patterns: Pairs that hit 3 strikes. What was the root cause?
      Was the issue in the agent prompt, the rubric, or the input quality?

   3. USER ESCALATION patterns: What questions were escalated to the user?
      Could the system have resolved them with better context or rules?

   Surface findings as "Suggested Learnings" at end of the pipeline summary:

   ### Suggested Learnings
   - [PATTERN] strategist-critic consistently flags missing event study
     justification → Consider adding to content-invariants.md
   - [FRICTION] writer-critic round 3 failures always involve voice mismatch
     → Style guide may need retraining
   - [HIGH-PERF] coder first-pass success when results_summary.md is detailed
     → Reinforce this in /analyze output requirements

   NEVER auto-append to MEMORY.md. Present suggestions. User approves or rejects.
   ```

2. **Template promotion protocol.** Add to meta-governance.md:
   ```
   ## Learning Promotion

   When a learning has been validated across 3+ projects (confirmed by user):
   - PATTERN → candidate for new content invariant (INV-XX) or rule addition
   - FRICTION → candidate for agent prompt revision or rubric adjustment
   - HIGH-PERF → candidate for new best-practice in relevant agent's protocol

   Promotion requires user approval. The orchestrator drafts the change;
   the user commits it to the template repo.
   ```

**Modify `logging.md`:**

3. **Trace analysis subsection.** Add:
   ```
   ## Trace Analysis

   After pipeline completion, read the execution trace and the last 5 traces
   (if available) to identify recurring patterns. Log analysis to:
   quality_reports/traces/analysis_{date}.md
   ```

**Verify:**
- Run `/new-project` end-to-end → "Suggested Learnings" section appears in summary
- Approve a learning → it appears in MEMORY.md with `[LEARN]` tag
- Reject a learning → not added
- After 3 projects with same pattern → orchestrator suggests template promotion

### WHY THIS MATTERS

For economists: clo-author gets smarter with every paper you write. Patterns that work are reinforced; friction points are identified and fixed. The template itself improves — every fork benefits from what prior users learned.

For the MAS literature: this implements OxyBank's closed-loop learning in a human-supervised architecture. The system suggests; the user decides. No autonomous self-modification.

---

## Implementation Order

| Priority | Phase | Rationale | Effort |
|----------|-------|-----------|--------|
| 1 | **Phase 3: Writer Evolution** | Biggest pain point, most user-visible, most LinkedIn-worthy | Medium |
| 2 | **Phase 1: Registry** | Architectural foundation that Phases 4 and 5 build on | Medium |
| 3 | **Phase 2: Checkpointing** | Enables resume and diagnostics for all subsequent work | Medium |
| 4 | **Phase 4: Cold-Read + Dual Critics** | Quality improvement, requires registry (Phase 1) for dual-critic dispatch | Low-Medium |
| 5 | **Phase 5: Learning Loop** | Requires traces (Phase 2) and registry (Phase 1) | Low |

## Documentation Deliverables

Each phase produces a standalone document in `docs/evolution/` following this structure:

1. **BEFORE** — current state with file quotes
2. **THE PROBLEM** — concrete examples of what breaks
3. **THE LITERATURE** — arxiv papers and systems, with IDs and key findings
4. **THE CHANGE** — exact before/after diffs, files modified/created
5. **WHY THIS MATTERS** — economics-specific argument (the LinkedIn paragraph)
6. **VERIFICATION** — how to confirm the change works

## Files Summary

| Phase | Modified | Created |
|-------|----------|---------|
| 1 | `orchestrator.md`, `workflow.md`, `agents.md`, `quality.md` | `permissions.md`, `lifecycle.md` |
| 2 | `orchestrator.md`, `logging.md`, `workflow.md` | `templates/pipeline-state.json`, `templates/execution-trace.md` |
| 3 | `writer.md`, `writer-critic.md`, `content-invariants.md` | `templates/claim-source-map.md` |
| 4 | 7 critic agents, `orchestrator.md` | — |
| 5 | `orchestrator.md`, `logging.md`, `meta-governance.md` | — |

**Total:** ~4 new files, ~15 existing files modified (some touched in multiple phases).

## Key Design Decisions

1. **Centralized registry** over distributed declarations (per-agent frontmatter). Reasons: avoids Claude Code rejecting unknown frontmatter keys, single source of truth, matches existing centralized-rules pattern.

2. **File-based checkpointing** over database/runtime state. Reason: clo-author runs in Claude Code with filesystem as the only persistent store. JSON state file is readable, editable, and survives any session boundary.

3. **Cold-read critics** lose round-awareness but gain evaluation integrity. The orchestrator retains round context and communicates it to workers, not critics. Net positive for score quality.

4. **Dual critics only for gate artifacts** — cost-efficiency. Running two critics on every artifact doubles token cost. Gate artifacts (strategy memo, main results, manuscript) are worth it; intermediate artifacts are not.

5. **Human-approved learning** — never auto-modify the template. OxyBank's closed loop is powerful but dangerous in a research context where a wrong learning could systematically bias future papers.

## Backward Compatibility

- Phase 1: Registry encodes the same graph that was hardcoded — identical behavior on day one
- Phase 2: Checkpointing is additive — existing workflows gain a state file, nothing else changes
- Phase 3: Writer gates are new constraints (stricter, not different). Existing behavior is a subset.
- Phase 4: Cold-read is a prompt change — same agents, same rubrics, different context policy
- Phase 5: Learning suggestions are advisory — user approves before anything is saved

## Sources

### MAS Papers
| Paper | arxiv ID | Date | Key Insight |
|-------|----------|------|-------------|
| OxyGent | 2604.25602 | Apr 2026 | Permission-driven dispatch + OxyBank learning loop |
| PaperOrchestra | 2604.05018 | Apr 2026 | Raw materials → manuscript separation |
| CycleResearcher | 2411.00816 | Oct 2024 | Paired researcher-reviewer loop, 26.89% MAE reduction |
| Data-to-Paper | 2404.17605 | Apr 2024 | Information traceability — every claim traced to code |
| Agent Laboratory | 2501.04227 | Jan 2025 | Human-in-the-loop at every stage |
| MetaGPT | 2308.00352 | Aug 2023 | SOP-as-prompt-sequence with stage verification |
| CAMEL | 2303.17760 | Mar 2023 | Role-playing inception prompting |
| MAR | 2512.20845 | Dec 2025 | Multi-persona critique avoids degeneration of thought |
| SciAgents | 2409.05556 | Sep 2024 | Knowledge-graph backbone for hypothesis generation |
| PaperDebugger | 2512.02589 | Dec 2025 | MCP-based in-editor integration |
| MasRouter | ACL 2025 | 2025 | LLM-based task-to-agent routing via capability metadata |

### Competitive Landscape
| Who | What | Key Insight |
|-----|------|-------------|
| Goldsmith-Pinkham | Claude Code for Economists (Princeton series) | Personal style guide from own papers |
| Cunningham | Referee 2 (MixtapeTools) | Adversarial independence — fresh context for review |
| Korinek | AI Agents for Economic Research (NBER w34202) | Step-by-step agent construction for economists |
| OpenAI Prism | Cloud LaTeX workspace (GPT-5.2) | Direct competitor for writing stage |
| Ash et al. | Applied Econometric Framework (NBER w33344) | No-training-leakage constraint for LLM-in-regression |
| Dell | Layout Parser + Deep Learning for Economists | Document digitization as first-class data pipeline |

### Orchestration Patterns
| Source | Pattern | Applicability |
|--------|---------|---------------|
| OpenAI Agents SDK | Handoffs as tool calls | Structured context transfer |
| CrewAI Flows | Event-driven state + ephemeral vs. persistent memory | State management |
| LangGraph | Typed state + checkpointing + reducers | Resumable pipelines |
| AWS/Azure | Dynamic dispatch via capability registry | Agent routing |
| Multi-agent memory research | 36.9% of MAS failures from inter-agent misalignment | Read/write scope enforcement |
