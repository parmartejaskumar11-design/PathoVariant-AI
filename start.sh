#!/bin/sh
set -e

# Serve the SPA static bundle and proxy /api -> uvicorn on port 8000
nginx -g "daemon off;" &

cd /app/backend
exec uvicorn main:app --host 0.0.0.0 --port 8000