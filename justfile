default:
    echo "Available recipes: pack, clean"

# Package the plugin into out/OMFG.zip
pack:
    #!/usr/bin/env bash
    set -euo pipefail
    PLUGIN_NAME="OMFG"
    OUT_DIR="out"
    TMP_DIR="$(mktemp -d)"
    BASE="${TMP_DIR}/${PLUGIN_NAME}"

    mkdir -p "${BASE}/dist" "${BASE}/py_modules/omfg"

    # Frontend
    cp dist/index.js "${BASE}/dist/"
    cp dist/index.js.map "${BASE}/dist/" 2>/dev/null || true

    # Plugin metadata
    cp main.py plugin.json package.json "${BASE}/"
    cp LICENSE README.md "${BASE}/" 2>/dev/null || true
    cp defaults/defaults.txt "${BASE}/" 2>/dev/null || true

    # Python backend
    cp py_modules/omfg/*.py "${BASE}/py_modules/omfg/"

    # Assemble zip
    OUT_ABS="$(pwd)/${OUT_DIR}"
    mkdir -p "${OUT_ABS}"
    (cd "${TMP_DIR}" && zip -r "${OUT_ABS}/${PLUGIN_NAME}.zip" "${PLUGIN_NAME}")
    rm -rf "${TMP_DIR}"
    echo "✅ Built out/${PLUGIN_NAME}.zip"

# Build frontend then pack
build:
    pnpm build
    just pack

clean:
    rm -rf dist out node_modules
