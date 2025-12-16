#!/bin/bash
# Run script for Path Payment Terminal API Emulator

cd "$(dirname "$0")"
source venv/bin/activate

# Run uvicorn with explicit paths and exclude venv from watching
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude "venv/*" --reload-exclude "*/__pycache__/*"
