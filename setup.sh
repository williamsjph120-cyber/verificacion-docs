#!/bin/bash

echo "=== Verificación de Documentos ==="
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q 2>/dev/null; then
    echo "⚠ PostgreSQL no está corriendo. Iniciando..."
    sudo systemctl start postgresql
fi

# Create database if not exists
echo "Verificando base de datos..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='verificacion_docs'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE verificacion_docs;"

# Run migrations
echo "Ejecutando migraciones..."
sudo -u postgres psql -d verificacion_docs -f database/migrations/001_create_tables.sql

# Create admin user with proper password hash
echo "Creando usuario admin..."
python3 -c "
import sys
sys.path.insert(0, 'backend')
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hash_val = pwd_context.hash('admin123')
print(f\"INSERT INTO users (email, password_hash, full_name, role) VALUES ('admin@test.com', '{hash_val}', 'Administrador', 'admin') ON CONFLICT (email) DO NOTHING;\")
" | sudo -u postgres psql -d verificacion_docs

echo ""
echo "✅ Base de datos configurada"
echo ""
echo "Para iniciar el backend:"
echo "  cd backend && source ../venv/bin/activate && uvicorn src.main:app --reload --port 8000"
echo ""
echo "Para iniciar el frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Credenciales admin:"
echo "  Email: admin@test.com"
echo "  Contraseña: admin123"
