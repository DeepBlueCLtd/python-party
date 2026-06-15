# Acoustic Reference Book — Phase 1 pipeline. Single documented command surface.
# Contract: specs/001-codespace-xml-scaffold/contracts/cli-commands.md
#
# Targets that are not yet implemented print a clear pointer and exit non-zero,
# so the onboarding surface is stable even while the pipeline is being built.

.DEFAULT_GOAL := help
.PHONY: help bootstrap verify docs docs-serve generate gen-schema-docs pipeline compare bundle

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Install deps + generate models. Run by the devcontainer.
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev,docs]"
	$(MAKE) generate
	@echo "Bootstrap complete. Run 'make verify' to check the environment."

verify: ## Run lint + type-check + tests — the single 'is the environment good?' command.
	ruff check src tests
	mypy
	pytest

docs: ## Build the attractive HTML docs site (strict — fails on broken links).
	mkdocs build --strict

docs-serve: ## Live-preview the HTML docs at http://localhost:8000
	mkdocs serve

generate: ## Regenerate typed models from schema/*.xsd via xsdata.
	python -m acoustic_dataset.cli generate

gen-schema-docs: ## Generate schema reference pages + Mermaid ERD from the enriched XSD.
	python -m acoustic_dataset.cli gen-schema-docs

pipeline: ## End-to-end: map example input -> objects -> XML -> validate -> round-trip.
	python -m acoustic_dataset.cli pipeline

COMPARE_GENERATED ?= build/acoustic_dataset.xml
COMPARE_REFERENCE ?= examples/reference/trial_known_good.xml

compare: ## Migration-safety diff: $(COMPARE_GENERATED) vs $(COMPARE_REFERENCE) (override the vars).
	python -m acoustic_dataset.cli compare "$(COMPARE_GENERATED)" "$(COMPARE_REFERENCE)"

bundle: pipeline ## Produce distribution bundle (data + schema + generated models) in build/dist.
	python -m acoustic_dataset.cli bundle
