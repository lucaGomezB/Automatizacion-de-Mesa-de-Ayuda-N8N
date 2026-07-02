# Plan: Guide Website Sync to v4.1.0

**Status:** APPROVED
**Date:** 2026-04-09
**Score at start:** 62/100 (front-end audit)
**Target:** 80/100

---

## Phase 1: Content Freshness (fixes 15 deduction points)

### 1a. Version bump
- `index.qmd` line 1: title "The Clo-Author 4.0" → "The Clo-Author"  (drop version from title — it goes stale every release)
- Or: "The Clo-Author 4.1" if version in title is preferred

### 1b. Changelog page (`changelog.qmd`)
- Add v4.1.0 section at top (content invariants, pre-flights, grep linter, decision records, PostToolUse hook)
- Keep same format as existing v4.0.0 entry

### 1c. Reference page (`reference.qmd`)
- `/tools` quick lookup table (line 19): add `lint` and `upgrade` subcommands
- `/tools` detail section (lines 220-230): add `/tools lint [file|dir]` and `/tools upgrade` entries

### 1d. Customization page (`customization.qmd`)
- Hooks section (line 110-126): update "4 essential hooks" → "5 hooks", add PostToolUse lint hook to table

### 1e. User guide (`user-guide.qmd`)
- `/tools` utility table (lines 206-214): add `lint` and `upgrade` rows
- Remove or rewrite "Upgrading from 2.x" section (lines 297-336) — replace with current upgrade path (just run `/tools upgrade`)

### 1f. New v4.1 features mentioned somewhere
- Content invariants: mention in architecture.qmd or customization.qmd (rules section)
- Pre-flight reports: mention in user-guide.qmd under Strategy and Execution phases
- Decision records: mention in user-guide.qmd under Discovery and Strategy phases
- Linter: mention in user-guide.qmd under Utilities

---

## Phase 2: Content Accuracy (fixes 8 deduction points)

### 2a. Customization page rule list (`customization.qmd` lines 44-58)
- Remove `figures.md` and `tables.md` as separate entries (merged into `content-standards.md` in v3.0)
- Remove `domain-profile.md` from rules list (it's in `.claude/references/`, not `.claude/rules/`)
- Add `content-invariants.md` to rules list
- Verify count matches actual files in `.claude/rules/`

### 2b. Reference page path fix
- `reference.qmd` line 87: `Output/cross_language_comparison.md` → `quality_reports/cross_language_comparison.md`

### 2c. User guide path fix
- `user-guide.qmd` line 368: `Preambles/` → `preambles/`

### 2d. User guide stale reference
- `user-guide.qmd` line ~25 area or CLAUDE.md bullets: remove `[LEARN]` tag references, mention auto-memory instead

---

## Phase 3: Accessibility (fixes 5 deduction points)

### 3a. SCSS: `prefers-reduced-motion`
- Add `@media (prefers-reduced-motion: reduce)` block that disables `neon-pulse` and `cursor-blink` animations

### 3b. Scanline overlay contrast
- Reduce scanline opacity from `0.03` to `0.015` (subtle CRT effect without hurting readability)

---

## Phase 4: Render and verify

- Run `quarto render` in `guide/`
- Verify all 7 pages compile without errors
- Spot-check that new content appears correctly

---

## Files to modify

| File | Changes |
|------|---------|
| `guide/index.qmd` | Version in title |
| `guide/changelog.qmd` | Add v4.1.0 section |
| `guide/reference.qmd` | Add lint/upgrade, fix path |
| `guide/customization.qmd` | Fix rules list, update hooks count |
| `guide/user-guide.qmd` | Add lint/upgrade, fix paths, rewrite upgrade section, add v4.1 features |
| `guide/custom.scss` | Add prefers-reduced-motion, reduce scanline opacity |
| `guide/agents.qmd` | No changes needed |
| `guide/architecture.qmd` | Optional: mention content invariants in scoring section |
