default:
  help

help:
    @just --list

build:
    @echo "Running uv build..."
    uv build

clean:
    @echo "Cleaning cache dirs..."
    uv clean
    fd -uE .venv "__pycache__|.*_cache|dist|egg-info" | xargs rm -rf

test: clean
    @echo "Running tests..."
    pytest
    mypy src/acmsg

sync:
    @echo "Running uv sync..."
    uv sync --all-packages --dev

bump-version:
    @echo "Running bump-version..."
    nix run .#bump-version
