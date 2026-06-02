# Show available recipes
default:
    @just --list
    @echo ""
    @echo "Run 'just install' to get started."

# Install dependencies and set up the project
install:
    uv sync

# Run linting checks
lint:
    uv run ruff check .

# Run formatting checks
format-check:
    uv run ruff format --check .

# Auto-fix lint issues
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run all checks (lint + format)
check: lint format-check

# Run the CLI (pass args after --)
run *ARGS:
    uv run hackerone {{ ARGS }}

# Run the CLI with JSON output (pass args after --)
run-json *ARGS:
    uv run hackerone {{ ARGS }} --json

# Quick smoke test against the API
test:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Testing help..."
    uv run hackerone help > /dev/null
    echo "Testing help --json..."
    uv run hackerone help --json | python3 -m json.tool > /dev/null
    echo "Testing no-creds error..."
    output=$(HACKERONE_USERNAME="" HACKERONE_API_KEY="" uv run hackerone --env-file /dev/null balance 2>&1 || true)
    echo "$output" | grep -q "No username provided" && echo "  OK" || { echo "  FAIL: should error without creds"; exit 1; }
    echo "Testing balance --json..."
    uv run hackerone balance --json | python3 -m json.tool > /dev/null
    echo "Testing programs 1 --json..."
    uv run hackerone programs 1 --json | python3 -m json.tool > /dev/null
    echo "Testing verbose..."
    output=$(uv run hackerone balance -v 2>&1)
    echo "$output" | grep -q "Authenticated" && echo "  OK" || { echo "  FAIL: verbose should show auth info"; exit 1; }
    echo "All tests passed."

# Clean up generated files
clean:
    rm -rf .venv .ruff_cache *.egg-info dist build __pycache__
