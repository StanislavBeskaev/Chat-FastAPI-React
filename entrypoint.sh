#!/bin/bash
envsubst '$APP_WS_ADDRESS','$FRONTEND_DEBUG_MODE' < /app/frontend/public/config.js > /app/frontend/build/config_tmp.js
mv /app/frontend/build/config_tmp.js /app/frontend/build/config.js

cd /app/ || exit
uvicorn backend.main:app --host 0.0.0.0 --port 8000
