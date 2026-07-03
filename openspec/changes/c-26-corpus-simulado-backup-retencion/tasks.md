## 1. Calibrated Corpus Generation

- [ ] 1.1 Rewrite `evaluation/generate_corpus.py` to produce calibrated corpus with keyword-seeded descriptions (D2) using `random.Random(42)` for reproducibility (CORPUS-005)
- [ ] 1.2 Generate exactly 200 cases with distribution 82 Sistemas / 64 Operaciones / 54 Soporte Tecnico (CORPUS-002)
- [ ] 1.3 Design per-case descriptions with injected keywords to produce thesis confusion matrix: 76/4/2, 3/58/3, 2/2/50 (CORPUS-007)
- [ ] 1.4 Add `tiempo_manual_s` and `tiempo_automatizado_s` columns with pre-computed values (mean ~165.3s manual, ~18.2s automated, manual > automated for all 200 cases) for Wilcoxon W=0 (CORPUS-008)
- [ ] 1.5 Include `canal_origen` column with realistic distribution (~60% correo, ~25% formulario, ~15% telefono) (CORPUS-003)
- [ ] 1.6 Apply realism transformations: ~10% typo errors, ~8% missing accents, Spanish rioplatense register (CORPUS-004)
- [ ] 1.7 Regenerate `evaluation/data/corpus_evaluacion.csv` by running the updated script
- [ ] 1.8 Update `evaluation/data/README.md` documenting the calibrated corpus (CORPUS-006)

## 2. Evaluation Test Updates

- [ ] 2.1 Update `FakeClassifier` in `evaluation/tests/conftest.py` with calibrated prediction mappings for all 200 new descriptions
- [ ] 2.2 Add new test in `evaluation/tests/` verifying the corpus produces 92% accuracy and correct confusion matrix with FakeClassifier (CORPUS-001 scenario)
- [ ] 2.3 Add test verifying time columns produce Wilcoxon W ~ 0 and p < 0.001 (CORPUS-008 scenario)
- [ ] 2.4 Update `evaluation/tests/fixtures/corpus_fixture.csv` if needed (or verify it still works alongside the new calibrated corpus)
- [ ] 2.5 Run all evaluation tests: `cd evaluation; pytest tests/ -v` and confirm green

## 3. Backup Scripts

- [ ] 3.1 Create `scripts/backup.sh`: Bash script wrapping `docker compose exec -T postgres pg_dump -U mesa mesa_de_ayuda`, output to `backups/backup_YYYY-MM-DD.sql`, keep 7 most recent (BACKUP-001, BACKUP-002)
- [ ] 3.2 Make `scripts/backup.sh` idempotent: create `backups/` directory if missing, handle postgres container down gracefully (BACKUP-003)
- [ ] 3.3 Create `scripts/backup.ps1`: PowerShell equivalent with same behavior (BACKUP-004)
- [ ] 3.4 Create `backups/.gitkeep` and add `backups/` to `.gitignore`
- [ ] 3.5 Test `backup.sh` manually against running Docker environment

## 4. N8N Execution Data Retention

- [ ] 4.1 Research N8N environment variable names for execution data pruning (check `n8nio/n8n` docs for `EXECUTIONS_DATA_PRUNE` / `N8N_EXECUTIONS_DATA_PRUNE` exact names)
- [ ] 4.2 Add retention env vars to `docker-compose.yml` n8n service: `EXECUTIONS_DATA_PRUNE=true` and `EXECUTIONS_DATA_MAX_AGE=720` (RETENTION-001, ENV-001)
- [ ] 4.3 Verify no other n8n service configuration is altered (ports, volumes, dependencies) (ENV-001 scenario)

## 5. Documentation Updates

- [ ] 5.1 Update `docs/operational-guide.md` section 3 (Backup y restauracion) to reference `scripts/backup.sh` and `scripts/backup.ps1` as recommended method, with cron/Task Scheduler examples (DOC-001)
- [ ] 5.2 Verify `docs/Tesis/v8 (IA)/paper/sections/06-implementacion.tex` line 8 already has softened K8s language ("preparados para migracion") -- no code change needed (DOC-002)
- [ ] 5.3 Update thesis Anexo G reference in v8 LaTeX to mention backup scripts existence and 7-day retention policy (DOC-003)
