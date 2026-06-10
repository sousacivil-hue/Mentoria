#!/bin/bash
pip install -r requirements.txt -q
playwright install chromium
uvicorn main:app --host 0.0.0.0 --port 8000
