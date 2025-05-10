default:
  help

help:
  @just --list

build:
  @echo "Running uv build..."
  uv build

clean:
  @echo "Cleaning cache dirs..."
  fd -uE ".venv" "__pycache__|.*_cache|egg-info" -x rm -rf

test:
  @echo "Running tests..."
  uv run pytest --cov=acmsg --cov-report=xml
  uv run mypy src/acmsg
  just clean

sync:
  @echo "Running uv sync..."
  uv sync --all-packages --dev

bump-version:
  @echo "Running bump-version..."
  nix run .#bump-version "$@"
