# Makefile - optional convenience wrapper for Automatizacion-Mesa-de-Ayuda-N8N.
#
# Make is NOT required: the paired scripts are the source of truth. On systems
# without make (for example a fresh Windows install), run scripts/up.sh or
# scripts/up.ps1 directly.
#
# Usage:
#   make up      # start the full local stack (delegates to the paired script)
#   make down    # stop and remove the stack (volumes persist)
#   make ps      # show service status and health
#   make logs    # follow logs from all services
#   make health  # query the HTTPS health endpoints

# Detect the operating system. GNU Make sets OS=Windows_NT on Windows; on
# Linux/macOS it is empty.
ifeq ($(OS),Windows_NT)
UP_COMMAND := powershell -NoProfile -ExecutionPolicy Bypass -File scripts/up.ps1
PYTHON := python
else
UP_COMMAND := bash scripts/up.sh
PYTHON := python3
endif

.PHONY: up down ps logs health dry-run dry-run-email

up: ## Start the full local stack
	$(UP_COMMAND)

down: ## Stop and remove the stack (volumes persist)
	docker compose down

ps: ## Show service status and health
	docker compose ps

logs: ## Follow logs from all services
	docker compose logs -f

health: ## Query the HTTPS health endpoints
	curl -k https://localhost/api/v1/health
	curl -k https://localhost/api/v1/health/db

dry-run: ## Run the zero-cost local dry-run harness (scripts/dry_run/)
	$(PYTHON) scripts/dry_run/dry_run.py

dry-run-email: ## OPT-IN: dry-run harness plus the free email channel (needs DRY_RUN_EMAIL_* env)
	$(PYTHON) scripts/dry_run/dry_run.py --with-email
