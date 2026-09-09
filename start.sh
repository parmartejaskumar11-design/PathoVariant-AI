#!/bin/sh
set -e

PORT="${PORT:-3000}"
sed -i "s/listen 3000;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf

# Serve the SPA static bundle and proxy /api -> uvicorn on port 8000
nginx -g "daemon off;" &

cd /app/backend
exec uvicorn main:app --host 127.0.0.1 --port 8000