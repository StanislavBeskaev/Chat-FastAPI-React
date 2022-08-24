#!/bin/bash
cd /app/frontend || exit
echo "Чистим файл frontend/.env"
cat /dev/null > .env
echo "Записываем REACT_APP_WS_ADDRESS=$REACT_APP_WS_ADDRESS в frontend/.env"
echo "REACT_APP_WS_ADDRESS=$REACT_APP_WS_ADDRESS" >> .env
npm run build

cd /app/ || exit
uvicorn backend.main:app --host 0.0.0.0 --port 8000