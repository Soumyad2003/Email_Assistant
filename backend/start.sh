#!/bin/bash
# Production start script for Render
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT