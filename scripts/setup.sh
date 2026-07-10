#!/usr/bin/env bash
# ==============================================================================
# Ops Brain Local — OSDHack 2026 Setup Script
# Theme: On Device AI | Industrial Knowledge Intelligence, Fully Offline
# Strategy: Strip Enterprise to Zero. Run Everything Local. Win on Privacy + Performance.
# ==============================================================================

set -e

echo "=========================================================================="
echo "           OPS BRAIN LOCAL — SETUP & INITIALIZATION SCRIPT                "
echo "=========================================================================="

echo "[1/4] Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "[2/4] Downloading spaCy English model (en_core_web_sm)..."
python -m spacy download en_core_web_sm || pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

echo "[3/4] Checking and downloading AI models (~2.2GB, OpenVINO INT4)..."
python scripts/download_model.py --backend openvino

echo "[4/4] Seeding industrial databases and building NetworkX knowledge graph..."
python scripts/seed.py

echo "=========================================================================="
echo "           SETUP COMPLETE! READY TO LAUNCH OPS BRAIN LOCAL                "
echo "=========================================================================="
echo "To run the full demo (UI + API):"
echo "  python run.py --demo"
echo ""
echo "To run benchmarks (OpenVINO INT4):"
echo "  python scripts/benchmark.py"
echo "=========================================================================="
