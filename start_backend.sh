#!/bin/bash

cd /home/muditsapra/Documents/Illegal

source .venv/bin/activate

nohup uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    > backend.log 2>&1 &

sleep 5

nohup cloudflared tunnel \
    --url http://localhost:8000 \
    > tunnel.log 2>&1 &