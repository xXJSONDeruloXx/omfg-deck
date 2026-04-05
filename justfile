default:
    @just --list

# Run pytest with coverage (fails if coverage < 95%)
test:
    python3 -m pytest tests/ --cov=omfg --cov-report=term-missing -q

# Run tests verbosely
test-v:
    python3 -m pytest tests/ --cov=omfg --cov-report=term-missing -v

# Build frontend (pnpm) then package with decky CLI if available, else local pack
build:
    pnpm build
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ -x cli/decky ]]; then
        echo "Using decky CLI..."
        rm -rf out/
        cli/decky plugin build .
    else
        just pack
    fi

# Package into out/OMFG.zip without decky CLI (dev convenience)
pack:
    #!/usr/bin/env bash
    set -euo pipefail
    PLUGIN_NAME="OMFG"
    OUT_ABS="$(pwd)/out"
    TMP_DIR="$(mktemp -d)"
    BASE="${TMP_DIR}/${PLUGIN_NAME}"
    mkdir -p "${BASE}/dist" "${BASE}/py_modules/omfg"
    cp dist/index.js "${BASE}/dist/"
    cp dist/index.js.map "${BASE}/dist/" 2>/dev/null || true
    cp main.py plugin.json package.json "${BASE}/"
    cp LICENSE README.md "${BASE}/" 2>/dev/null || true
    cp defaults/defaults.txt "${BASE}/" 2>/dev/null || true
    cp py_modules/omfg/*.py "${BASE}/py_modules/omfg/"
    mkdir -p "${OUT_ABS}"
    (cd "${TMP_DIR}" && zip -r "${OUT_ABS}/${PLUGIN_NAME}.zip" "${PLUGIN_NAME}")
    rm -rf "${TMP_DIR}"
    echo "✅ Built out/${PLUGIN_NAME}.zip"

# Full pipeline: test → build
ci: test build

clean:
    rm -rf dist out node_modules __pycache__ .coverage htmlcov
