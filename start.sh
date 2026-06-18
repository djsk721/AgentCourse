#!/bin/bash
set -e
pip install fastapi uvicorn gunicorn openai python-dotenv
python -m uvicorn company_portal:app --host 0.0.0.0 --port 8000