#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS_DIR="$PROJECT_DIR/logs"

echo "=== Deteniendo servidores ==="

# Stop backend
if [ -f "$LOGS_DIR/backend.pid" ]; then
    PID=$(cat "$LOGS_DIR/backend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "  Backend (PID $PID) detenido"
    else
        echo "  Backend ya no estaba corriendo"
    fi
    rm -f "$LOGS_DIR/backend.pid"
else
    echo "  No hay PID de backend"
fi

# Stop frontend
if [ -f "$LOGS_DIR/frontend.pid" ]; then
    PID=$(cat "$LOGS_DIR/frontend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "  Frontend (PID $PID) detenido"
    else
        echo "  Frontend ya no estaba corriendo"
    fi
    rm -f "$LOGS_DIR/frontend.pid"
else
    echo "  No hay PID de frontend"
fi

# Kill any remaining uvicorn/vite processes on our ports
lsof -ti:8000 2>/dev/null | xargs -r kill 2>/dev/null
lsof -ti:5173 2>/dev/null | xargs -r kill 2>/dev/null

echo ""
echo "=== Servidores detenidos ==="
