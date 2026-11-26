.PHONY: help lint interrogate

UV ?= uv

# Interrogate measures docstring presence in the Python files under
# INTERROGATE_TARGETS; add a new Python directory there. No `--python` pin: a
# managed interpreter would be downloaded.
INTERROGATE_VERSION ?= 1.7.0
INTERROGATE_TARGETS ?= skills tools
# The media-project tool declares Python 3.14 or later and uses `type` aliases,
# which older interpreters cannot parse, so ask for a compatible interpreter.
INTERROGATE = $(UV) tool run --python '>=3.14' --from 'interrogate==$(INTERROGATE_VERSION)' interrogate --fail-under 100 \
	--exclude '*/.venv' --exclude '*/.uv-cache' --exclude '*/.uv-tools'

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS=":"; printf "Available targets:\n"} {printf "  %-20s %s\n", $$1, $$2}'

# To list each undocumented definition, run
# `make interrogate INTERROGATE_TARGETS="-vv skills tools"`.
interrogate: ## Enforce complete Python docstring coverage
	$(INTERROGATE) $(INTERROGATE_TARGETS)

# The media-project tool keeps its own Makefile for its remaining lints; this
# target covers the whole repository's Python docstrings.
lint: ## Run the docstring-coverage gate
	$(MAKE) interrogate
