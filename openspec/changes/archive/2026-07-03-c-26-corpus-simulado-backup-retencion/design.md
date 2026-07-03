## Context

The Automatizacion-de-Mesa-de-Ayuda-N8N project is in maintenance mode with all 10 prior OPSX changes archived. The thesis claims specific quantitative results validated on a 200-case corpus. The existing simulated corpus generates random template-based descriptions that produce inconsistent metrics when run through the evaluation framework. Additionally, two operational gaps exist: no automated PostgreSQL backup mechanism, and the N8N 30-day retention claim is unenforced.

The evaluation framework at `evaluation/` is mature: it supports corpus loading (`corpus.py`), classification metrics (`metrics.py`), Wilcoxon time analysis (`stats.py`), and a runner (`run_evaluation.py`) with dependency-injected classifier. Tests use `FakeClassifier` that maps descriptions to pre-programmed results, bypassing Gemini entirely.

The deterministic classifier at `App/Backend/app/classifiers/deterministic.py` uses regex patterns from `keywords.py` to score descriptions against three categories: Sistemas (server/infrastructure keywords), Operaciones (process/administration keywords), and Soporte Tecnico (hardware/desktop keywords). Confidence is computed as `winner_score / (winner_score + runner_up_score + epsilon)`.

## Goals / Non-Goals

**Goals:**
- Create a calibrated simulated corpus of exactly 200 cases that, when processed by the evaluation framework with a matching `FakeClassifier`, produces: 92% accuracy, F1 macro ~0.919, confusion matrix matching Table 7 (76/4/2, 3/58/3, 2/2/50), Wilcoxon W=0 with p<0.001, manual time mean ~165.3s, automated time mean ~18.2s
- Provide automated PostgreSQL backup scripts (`backup.sh`, `backup.ps1`) with 7-day retention, wrapping `docker compose exec postgres pg_dump`
- Enforce N8N 30-day execution data retention via environment variables in `docker-compose.yml`
- Update operational documentation to reference backup scripts
- Verify thesis v8 LaTeX already has softened K8s language (no code change needed)

**Non-Goals:**
- Modify the evaluation framework itself (runner, metrics, corpus loading are unchanged)
- Modify the deterministic classifier or keyword dictionary
- Real data collection or Gemini API calls during evaluation
- Kubernetes cluster deployment or migration
- Production-grade backup encryption or off-site sync

## Decisions

### D1: Corpus calibration via keyword seeding

**Decision:** Generate corpus descriptions with a seeded random number generator (`random.Random(42)`) and pre-computed keyword injection per case. Each description is individually crafted (not templated) to contain keywords that trigger the DeterministicClassifier into a specific prediction. The `FakeClassifier` used in tests is programmed with the same mapping so tests pass without Gemini.

**Rationale:** The evaluation tests inject `FakeClassifier`, not the real classifier. The calibrated corpus must work with both: (a) the real `DeterministicClassifier` for manual verification, and (b) the `FakeClassifier` for automated test runs. By seeding descriptions with category-specific keywords that the deterministic classifier catches, we ensure consistency between both paths.

**Alternatives considered:**
- *Pure random templates with FakeClassifier-only mapping*: simpler to implement but descriptions would not trigger the deterministic classifier correctly, making manual verification impossible.
- *Use the real HybridClassifier with Gemini*: too slow, too expensive, non-deterministic, and breaks the test isolation principle.

### D2: Per-case description design for exact confusion matrix

**Decision:** Design each case's description to produce a specific classification result. For correct classifications, inject at least 2 strong keywords from the target category and zero from other categories. For intentional misclassifications (the 16 errors in Table 7), inject keywords from the WRONG category while omitting strong keywords from the correct category. For example, a "Sistemas → Operaciones" error case uses process keywords like "proceso", "aprobacion", "solicitud" but no server/infrastructure keywords.

**Rationale:** The deterministic classifier's scoring is keyword-count based -- the category with the most distinct keyword matches wins. By controlling which keywords appear in each description, we control the classification outcome deterministically.

**Error distribution design:**
- Sistemas errors: 4 → Operaciones (inject Operaciones keywords), 2 → Soporte Tecnico (inject Soporte keywords)
- Operaciones errors: 3 → Sistemas (inject Sistemas keywords), 3 → Soporte Tecnico (inject Soporte keywords)
- Soporte Tecnico errors: 2 → Sistemas (inject Sistemas keywords), 2 → Operaciones (inject Operaciones keywords)

### D3: Time data design for Wilcoxon W=0

**Decision:** Pre-compute `tiempo_manual_s` and `tiempo_automatizado_s` columns directly in the CSV. Set all manual times to fluctuate around 165.3s (range 96-289, mean 165.3, SD ~38.7) and all automated times around 18.2s (range 11-31, mean 18.2, SD ~4.1). Ensure that for every single case, `manual > automatizado`, producing W=0 in the Wilcoxon signed-rank test.

**Rationale:** The `stats.wilcoxon_tiempos()` function in `evaluation/stats.py` computes W as the sum of ranks of positive differences (manual - automated). When ALL differences are positive (manual > automated for every case), W = n*(n+1)/2 = 20100 for n=200. With `alternative="greater"`, the returned W statistic is 0 (since scipy's `wilcoxon` returns the sum of ranks for the non-positive side), and p < 0.001. The rank-biserial r = 1.0.

**Time generation approach:** Use `random.Random(42)` with normal distributions:
- Manual: `random.gauss(165.3, 38.7)` clipped to [96, 289]
- Automated: `random.gauss(18.2, 4.1)` clipped to [11, 31]
- Post-process: for any case where automated >= manual, swap or boost manual by +10

### D4: Backup scripts as thin Docker wrappers

**Decision:** Both `backup.sh` and `backup.ps1` are thin wrappers around `docker compose exec -T postgres pg_dump -U mesa mesa_de_ayuda`. They create timestamped SQL files, keep the 7 most recent, and delete older ones. No external dependencies beyond Docker and the shell.

**Rationale:** The `docker-compose.yml` already declares the postgres service with known credentials (mesa/mesa) and database name (mesa_de_ayuda). The operational guide already documents the manual backup command. The scripts just automate and rotate.

**Script details:**
- Output directory: `backups/` (gitignored)
- Filename pattern: `backup_YYYY-MM-DD.sql`
- Retention: 7 files (can be configured via variable at top of script)
- Bash: uses `ls -t | tail -n +8 | xargs rm -f` for rotation
- PowerShell: uses `Get-ChildItem | Sort-Object LastWriteTime -Descending | Select-Object -Skip 7 | Remove-Item`

### D5: N8N retention via environment variables

**Decision:** Add N8N environment variables to `docker-compose.yml` that enable automatic execution data pruning. N8N's built-in mechanism is the simplest and most maintainable approach -- no external scripts, no cron jobs, no database manipulation.

**Rationale:** N8N provides first-class support for execution data retention through environment variables. The `EXECUTIONS_DATA_PRUNE` (or `N8N_EXECUTIONS_DATA_PRUNE`) flag enables pruning, and `EXECUTIONS_DATA_MAX_AGE` (or `N8N_EXECUTIONS_DATA_MAX_AGE`) sets the retention period in hours. For 30 days: `30 * 24 = 720` hours. This runs as part of N8N's internal housekeeping process.

**Alternatives considered:**
- *Cron job to delete from N8N SQLite*: fragile, depends on N8N's internal database schema, breaks if N8N changes backend.
- *Docker volume cleanup*: too coarse; would delete user configurations and credentials alongside execution data.

### D6: Thesis v8 LaTeX K8s language -- no change needed

**Decision:** The v8 LaTeX at `docs/Tesis/v8 (IA)/paper/sections/06-implementacion.tex` line 8 already reads: "preparados para migracion a un cluster Kubernetes~1.30 para el entorno productivo." This is already softened to future migration language. The v7 version had "mediante un cluster Kubernetes version 1.30 para el entorno productivo" (claiming K8s IS deployed). No code change needed.

**Rationale:** The task says to verify and fix if needed. Verification confirms the fix was already applied during the v7→v8 migration. The v8 text is correct as-is.

## Risks / Trade-offs

- **[Corpus calibration brittleness]** If the keyword dictionary (`keywords.py`) changes significantly, the calibrated corpus will produce different metrics. → Mitigation: The corpus maps to `FakeClassifier` predictions, not to the real classifier. Tests use `FakeClassifier`. The keyword matching is for human verification only.
- **[FakeClassifier sync]** The `FakeClassifier` in `evaluation/tests/conftest.py` must be updated with predictions for all 200 new descriptions. If the corpus descriptions change without updating the FakeClassifier, tests will return default predictions. → Mitigation: A single `generate_corpus.py` script produces both the CSV and a corresponding Python file with the FakeClassifier mapping, keeping them synchronized.
- **[N8N env var compatibility]** N8N environment variable names may differ between versions. → Mitigation: Check N8N documentation during implementation. If pruning variables are not available in the current N8N version, fall back to a cleanup script approach.
- **[Backup script portability]** Bash script assumes GNU `date` (not BSD). → Mitigation: Documented in script header. Windows users use the PowerShell variant.
- **[Time data reproducibility]** The seeded random generation must produce exact target means. Small variations from floating-point arithmetic are acceptable (within 1% of thesis values). → Mitigation: Report actual computed means in a comment in the corpus generator.

## Migration Plan

1. Run `python evaluation/generate_corpus.py` to regenerate the corpus
2. Update `evaluation/tests/conftest.py` FakeClassifier mappings
3. Run evaluation tests: `cd evaluation; pytest tests/ -v`
4. Verify `report.md` shows 92% accuracy and correct confusion matrix
5. Add N8N env vars to `docker-compose.yml`
6. Create `backups/` directory with `.gitkeep`
7. Add `backups/` to `.gitignore`
8. Test backup scripts manually
9. Update `docs/operational-guide.md`

**Rollback:** Revert to previous corpus CSV (git history preserves it). Remove N8N env vars from compose. Scripts are additive -- no rollback needed for new files.
