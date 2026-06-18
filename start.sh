#!/bin/bash
set -e

python -m pip install --upgrade pip
pip install -r uvicorn fastapi

python -m uvicorn company_portal:app --host 0.0.0.0 --port 8000