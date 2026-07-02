# Plan: Guide Website Restructure

**Status:** APPROVED
**Date:** 2026-04-09
**Origin:** UX audit scored 6/10 — "describes instead of shows, repeats instead of links, front-loads complexity instead of value"
**Target:** 8/10

---

## Diagnosis

The guide has good raw material in the wrong arrangement. The reference page and agents page work well. The problems are:

1. **user-guide.qmd** tries to be a tutorial, reference, and architecture doc (370 lines, close-the-tab risk)
2. **index.qmd** front-loads the 17-agent system before showing value
3. Content duplicated across pages instead of linked (peer review in 4 places, talk formats 3x, config table 2x)
4. Zero examples of actual output — all feature descriptions, no "here's what you get"

---

## Proposed Structure (7 pages → 7 pages)

No new pages. Restructure what's inside them.

### Page 1: `index.qmd` — Landing Page

**Current:** Quick start + behind the scenes + Day 1 checklist + prerequisites + origin
**Problem:** "Behind the Scenes" paragraph dumps 17-agent architecture on newcomers

**Restructure:**
- Keep the one-sentence elevator pitch (line 1-6) — it's good
- Keep "Get Started in 5 Minutes" (steps 1-3) — it's good
- **Replace** "What Happens Behind the Scenes" dense paragraph with a 3-line version:
  > You describe tasks in plain English. Claude dispatches specialized agents — one creates, another reviews — and presents results for your approval. Quality gates run in the background so broken work never ships.
- **Add** a "Just want to try 2 commands?" callout box:
  > Already have a paper? Start with `/review paper/main.tex`. Want to draft a section? `/write intro`. Everything else is optional.
- **Move** the Day 1 Checklist into a collapsible (it's 7 items — not "5 minutes")
- Keep prerequisites table and origin — both are clean
- **Add** a "Where to go next" footer: "Read the [Walkthrough](user-guide.qmd) to see the system in action, or jump to the [Command Reference](reference.qmd) if you already know what you want."

### Page 2: `user-guide.qmd` — Walkthrough (MAJOR REWRITE)

**Current:** 370-line feature dump — every command, every flag, every agent name
**Problem:** Duplicates reference.qmd, reads like a system manual, no examples

**Restructure into a narrative walkthrough:**

```
# How It Works (keep — 4-line table is clear)

# A Typical Workflow
  Replace the code-block wall (lines 25-51) with a simple Mermaid 
  diagram (5 phases, no agent names). One sentence per phase.

# Your First Review (NEW — the missing walkthrough)
  Show what happens step by step when you type /review --peer JHR:
  1. What you type
  2. What Claude does (editor desk review → referee dispatch)
  3. What you get back (describe the report format — or include 
     a formatted markdown example of a condensed referee report)
  4. What you do next
  This is the "fork the repo" moment the audit identified.

# Your First Draft (NEW — second walkthrough)
  Same pattern for /write intro:
  1. What you type
  2. What Claude does (reads paper type, drafts with argument moves)
  3. What you get back
  4. How to iterate

# Discovery & Strategy (LEAN DOWN)
  One paragraph per command. Link to reference.qmd for flags.
  Mention decision records and pre-flight reports briefly.
  Do NOT re-explain agent pairs — link to agents.qmd.

# Execution (LEAN DOWN)
  One paragraph each for /analyze and /write.
  Mention pre-code report. Link to reference.qmd for flags.

# Review & Revision (LEAN DOWN)  
  One paragraph for /review (link to agents.qmd for peer review detail).
  One paragraph for /revise.

# Presentations & Submission (LEAN DOWN)
  One paragraph each for /talk and /submit.
  Link to reference.qmd for the full flag tables.

# Quality Gates (keep but soften)
  Keep the table. Add one sentence: "These run in the background. 
  You'll probably never think about them — they just prevent 
  obviously broken work from being committed."

# Troubleshooting (keep — it's good)

# Upgrading (keep current short version)
```

**What gets cut:** All the detailed flag tables, agent dispatch tables, and per-command multi-paragraph descriptions. These already live in `reference.qmd` — the user-guide should link, not repeat.

**Target length:** ~200 lines (down from 370).

### Page 3: `agents.qmd` — Meet the Agents (MINOR EDITS)

**Current:** Well-structured with honest callout boxes. The audit's best-rated content page.

**Changes:**
- **Collapse** the long Strategist paragraph (lines 52-57) into a table or 4 bullet points (one per paper type)
- Same for Coder and Writer descriptions
- These are single paragraphs with 4 nested conditionals ("For reduced-form: ... For structural: ...") — tables are better for this pattern
- **Add** one formatted example: what a coder-critic report summary looks like (5-6 lines of markdown showing the score breakdown)
- Keep everything else — the "What to Expect" callouts are the guide's best feature

### Page 4: `architecture.qmd` — How It Works Under the Hood (MODERATE EDITS)

**Current:** Covers 6 config layers, agent workflow, orchestrator, plan-first, scoring, slides, governance

**Changes:**
- **Remove** the 6-layer configuration table (lines 10-18) — it's duplicated from customization.qmd. Replace with one sentence linking there.
- **Remove** "Slides & Lectures" section (lines 314-340) — this is stale legacy content about lecture workflows
- **Remove** "Constitutional Governance" section (lines 341-365) — too niche for the main guide; move to customization.qmd as a collapsible or delete
- **Keep** the Mermaid diagrams — they're the page's strength
- **Keep** the scoring protocol section but add the humanizing sentence: "These numbers run in the background. They prevent broken work from shipping — you rarely need to think about them directly."
- **Target length:** ~280 lines (down from ~365)

### Page 5: `customization.qmd` — Make It Yours (MINOR EDITS)

**Current:** Reasonable length, good structure

**Changes:**
- **Keep** the 6-layer table here (canonical location)
- **Fix** the Memory System section: replace "[LEARN]" references with auto-memory (may already be done by the v4.1 sync agent)
- **Move** Exploration Workflow from user-guide.qmd to here (it's a customization/workflow choice, not a tutorial topic)
- **Add** "Constitutional Governance" as a collapsed section if removed from architecture.qmd

### Page 6: `reference.qmd` — Command Reference (NO CHANGES)

The audit rated this the best page. Clean, scannable, minimal prose. Leave it alone.

### Page 7: `changelog.qmd` — What's New (NO CHANGES)

Already updated for v4.1.0. Fine as-is.

---

## De-duplication Map

Each concept gets ONE canonical home. Everything else links.

| Concept | Canonical Page | Linked From |
|---------|---------------|-------------|
| 6-layer config table | customization.qmd | architecture.qmd |
| Peer review workflow (dispositions, pet peeves, editorial decision) | agents.qmd | user-guide.qmd (1 sentence + link), reference.qmd (syntax only) |
| Talk formats table | reference.qmd | user-guide.qmd (1 sentence + link) |
| Quality gates / scoring | architecture.qmd (formula) | user-guide.qmd (table + humanizing note) |
| Paper-type awareness | agents.qmd (per-agent) | user-guide.qmd mentions once, links |
| /revise classification | reference.qmd | user-guide.qmd (1 sentence + link) |
| Exploration workflow | customization.qmd | — |

---

## Example Output Additions

The audit's #1 recommendation: "show, don't describe." Add formatted markdown examples (not screenshots — they go stale) to:

1. **user-guide.qmd** "Your First Review" — a condensed 15-line example of what a `/review --peer` editorial decision looks like
2. **user-guide.qmd** "Your First Draft" — a 10-line example of what `/write intro` produces (the argument-move structure)
3. **agents.qmd** coder-critic section — a 6-line score breakdown example

These are fabricated examples clearly marked as illustrative. They give the reader a mental model of what output to expect.

---

## What This Does NOT Change

- SCSS theme — untouched (audit rated it well)
- Quarto config (_quarto.yml) — untouched
- Reference page — untouched (audit's best page)
- Changelog page — untouched
- Mermaid diagrams — kept (audit liked them)
- "What to Expect" callout boxes — kept (audit's favorite feature)
- 7-page structure — same count, no new pages

---

## Implementation Order

| Step | File | Effort | 
|------|------|--------|
| 1 | user-guide.qmd | Large — major rewrite into walkthrough format |
| 2 | index.qmd | Small — trim behind-the-scenes, add callout |
| 3 | agents.qmd | Medium — collapse long paragraphs into tables, add example |
| 4 | architecture.qmd | Medium — remove duplicated/stale sections |
| 5 | customization.qmd | Small — receive exploration workflow, fix refs |
| 6 | Render + verify | Quarto render, check all links |

---

## Success Criteria

- user-guide.qmd under 220 lines (from 370)
- Zero content duplicated in more than one page (tables, workflows)
- At least 2 formatted output examples in the walkthrough
- "Just want 2 commands?" callout on landing page
- UX re-audit target: 8/10
