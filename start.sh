#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOGS_DIR="$PROJECT_DIR/logs"
NVM_DIR="$HOME/.nvm"

mkdir -p "$LOGS_DIR"

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

echo "=== Iniciando Sistema de Verificación de Documentos ==="
echo ""

# Kill any existing processes
"$PROJECT_DIR/stop.sh" 2>/dev/null

# Start backend
echo "Iniciando backend (puerto 8000)..."
cd "$BACKEND_DIR"
source "$PROJECT_DIR/venv/bin/activate"
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > "$LOGS_DIR/backend.log" 2>&1 &
echo $! > "$LOGS_DIR/backend.pid"
echo "  Backend PID: $(cat "$LOGS_DIR/backend.pid")"

sleep 2

# Check backend
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "  Backend OK"
else
    echo "  Backend falló. Revisa logs/backend.log"
fi

# Start frontend
echo ""
echo "Iniciando frontend (puerto 5173)..."
cd "$FRONTEND_DIR"
nohup npm run dev -- --host 0.0.0.0 > "$LOGS_DIR/frontend.log" 2>&1 &
echo $! > "$LOGS_DIR/frontend.pid"
echo "  Frontend PID: $(cat "$LOGS_DIR/frontend.pid")"

sleep 3

# Check frontend
if curl -s http://localhost:5173/ > /dev/null 2>&1; then
    echo "  Frontend OK"
else
    echo "  Frontend falló. Revisa logs/frontend.log"
fi

echo ""
echo "=== Sistema corriendo ==="
echo "  Panel admin:  http://localhost:5173"
echo "  API docs:     http://localhost:8000/api/docs"
echo "  Login:        admin@test.com / admin123"
echo ""
echo "Para parar: ./stop.sh"
echo "Logs:      tail -f logs/backend.log"
