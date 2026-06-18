#!/bin/bash
set -e

python -m pip install --upgrade pip
pip install fastapi uvicorn

python -m gunicorn company_portal:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000