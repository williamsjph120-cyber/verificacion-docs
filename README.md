# Verificación de Documentos

Sistema de verificación de documentos con código QR y CAPTCHA, similar al portal del gobierno dominicano.

## Características

- **Código QR** único por documento para verificación rápida
- **CAPTCHA** con imagen distorsionada para prevenir bots
- **Panel de administración** completo (CRUD de documentos)
- **Almacenamiento** en Cloudflare R2 (compatible S3)
- **Autenticación** JWT segura
- **Registro** de verificaciones (IP, fecha, dispositivo)

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3 + FastAPI |
| Frontend | React + Vite + Tailwind CSS |
| Base de datos | PostgreSQL |
| Almacenamiento | Cloudflare R2 |

## Instalación

### 1. Requisitos

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ (para frontend)

### 2. Configurar base de datos

```bash
./setup.sh
```

### 3. Configurar variables de entorno

```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales de Cloudflare R2
```

### 4. Iniciar backend

```bash
cd backend
source ../venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### 5. Iniciar frontend

```bash
cd frontend
npm install
npm run dev
```

## Credenciales por defecto

- **Email:** admin@test.com
- **Contraseña:** admin123

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/auth/register | Registrar usuario |
| POST | /api/auth/login | Iniciar sesión |
| GET | /api/auth/me | Obtener usuario actual |
| POST | /api/documents/ | Subir documento |
| GET | /api/documents/ | Listar documentos |
| GET | /api/documents/{id} | Obtener documento |
| DELETE | /api/documents/{id} | Eliminar documento |
| GET | /api/verify/{token}/captcha | Obtener CAPTCHA |
| POST | /api/verify/{token} | Verificar documento |
| GET | /api/verify/{token}/download | Descargar documento |

## Flujo de Verificación

1. Admin sube documento PDF → Se genera token UUID y código QR
2. QR se imprime en documento físico
3. Usuario escanea QR → Abre `/verificar/{token}`
4. Ingresa código de seguridad (CAPTCHA)
5. Sistema valida y muestra documento verificado
6. Usuario puede descargar PDF

## API Docs

Disponible en: `http://localhost:8000/api/docs`
