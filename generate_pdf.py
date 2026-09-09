from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def create_deploy_guide():
    doc = SimpleDocTemplate(
        "/home/williamsperdomo/verificacion-documentos/deploy-guide.pdf",
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=22, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=16, spaceAfter=10, spaceBefore=20)
    sub_heading = ParagraphStyle('SubHeading', parent=styles['Heading2'], fontSize=13, spaceAfter=8, spaceBefore=12)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, spaceAfter=6, leading=14)
    code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=9, spaceAfter=4, leftIndent=20, backColor=colors.Color(0.95,0.95,0.95))

    story = []

    story.append(Paragraph("Guía de Despliegue", title_style))
    story.append(Paragraph("Sistema de Verificación de Documentos", body_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("1. Pré-requisitos", heading_style))
    story.append(Paragraph("- Cuenta en <b>Render.com</b> (gratuita)", body_style))
    story.append(Paragraph("- Cuenta en <b>Cloudflare</b> (gratuita)", body_style))
    story.append(Paragraph("- Repositorio en <b>GitHub</b>", body_style))
    story.append(Paragraph("- Dominio <b>firmagob.com.do</b> (comprar mañana)", body_style))

    story.append(Paragraph("2. Subir código a GitHub", heading_style))
    story.append(Paragraph("En la carpeta del proyecto, ejecutar:", body_style))
    story.append(Paragraph("git init && git add . && git commit -m 'v1' && git remote add origin https://github.com/TU_USUARIO/repo.git && git push -u origin main", code_style))

    story.append(Paragraph("3. Crear base de datos en Render", heading_style))
    story.append(Paragraph("a) Ir a Render Dashboard > New > PostgreSQL", body_style))
    story.append(Paragraph("b) Nombre: <b>verificacion-db</b>", body_style))
    story.append(Paragraph("c) Plan: Free", body_style))
    story.append(Paragraph("d) Copiar el <b>Internal Database URL</b>", body_style))

    story.append(Paragraph("4. Crear servicio Backend en Render", heading_style))
    story.append(Paragraph("a) New > Web Service", body_style))
    story.append(Paragraph("b) Conectar repositorio GitHub", body_style))
    story.append(Paragraph("c) Configuración:", body_style))
    story.append(Paragraph("- Name: <b>verificacion-backend</b>", code_style))
    story.append(Paragraph("- Runtime: Docker", code_style))
    story.append(Paragraph("- Dockerfile Path: <b>backend/Dockerfile</b>", code_style))
    story.append(Paragraph("- Docker Context: <b>.</b>", code_style))
    story.append(Paragraph("d) Variables de entorno (Environment):", body_style))

    env_data = [
        ['Variable', 'Valor'],
        ['DATABASE_URL', 'Pegar Internal Database URL de Render'],
        ['SECRET_KEY', 'Generar con: python -c "import secrets; print(secrets.token_urlsafe(32))"'],
        ['R2_ACCOUNT_ID', 'De Cloudflare (ver paso 5)'],
        ['R2_ACCESS_KEY_ID', 'De Cloudflare (ver paso 5)'],
        ['R2_SECRET_ACCESS_KEY', 'De Cloudflare (ver paso 5)'],
        ['R2_BUCKET_NAME', 'verificacion-documentos'],
        ['FRONTEND_URL', 'https://verificacion-frontend.onrender.com'],
    ]
    t = Table(env_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.Color(0.95,0.95,0.95)]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph("e) Click <b>Create Web Service</b>", body_style))

    story.append(Paragraph("5. Configurar Cloudflare R2", heading_style))
    story.append(Paragraph("a) Ir a Cloudflare Dashboard > R2 Object Storage", body_style))
    story.append(Paragraph("b) Create bucket: <b>verificacion-documentos</b>", body_style))
    story.append(Paragraph("c) Manage R2 API Tokens > Create API Token", body_style))
    story.append(Paragraph("d) Permissions: <b>Object Read & Write</b>", body_style))
    story.append(Paragraph("e) Copiar <b>Access Key ID</b> y <b>Secret Access Key</b>", body_style))
    story.append(Paragraph("f) Pegar en las variables de entorno del backend en Render", body_style))

    story.append(Paragraph("6. Crear servicio Frontend en Render", heading_style))
    story.append(Paragraph("a) New > Web Service", body_style))
    story.append(Paragraph("b) Conectar repositorio GitHub", body_style))
    story.append(Paragraph("c) Configuración:", body_style))
    story.append(Paragraph("- Name: <b>verificacion-frontend</b>", code_style))
    story.append(Paragraph("- Runtime: Docker", code_style))
    story.append(Paragraph("- Dockerfile Path: <b>frontend/Dockerfile</b>", code_style))
    story.append(Paragraph("- Docker Context: <b>.</b>", code_style))
    story.append(Paragraph("d) Variable de entorno:", body_style))
    story.append(Paragraph("- VITE_API_URL: https://verificacion-backend.onrender.com", code_style))
    story.append(Paragraph("e) Click <b>Create Web Service</b>", body_style))

    story.append(Paragraph("7. Configurar dominio personalizado", heading_style))
    story.append(Paragraph("a) Comprar <b>firmagob.com.do</b> en registrar dominio", body_style))
    story.append(Paragraph("b) En Render: Frontend > Settings > Custom Domains", body_style))
    story.append(Paragraph("c) Agregar <b>buzon.firmagob.com.do</b>", body_style))
    story.append(Paragraph("d) Render mostrará registros DNS a configurar", body_style))
    story.append(Paragraph("e) En Cloudflare (o donde compre el dominio), agregar:", body_style))
    story.append(Paragraph("- Record A apuntando a la IP de Render", code_style))
    story.append(Paragraph("- Record CNAME: buzon -> verificacion-frontend.onrender.com", code_style))
    story.append(Paragraph("f) Esperar propagación DNS (5-30 minutos)", body_style))

    story.append(Paragraph("8. Verificar despliegue", heading_style))
    story.append(Paragraph("a) Abrir https://verificacion-backend.onrender.com/docs", body_style))
    story.append(Paragraph("b) Abrir https://verificacion-frontend.onrender.com", body_style))
    story.append(Paragraph("c) Login: admin@test.com / admin123", body_style))
    story.append(Paragraph("d) Subir documento y verificar QR genera enlace correcto", body_style))

    story.append(Paragraph("9. Estructura de URLs", heading_style))
    story.append(Paragraph("- Admin: https://verificacion-frontend.onrender.com/dashboard", body_style))
    story.append(Paragraph("- Verificación: https://buzon.firmagob.com.do/app/unicaribe/DOC-2026-001", body_style))

    doc.build(story)
    print("PDF generado: deploy-guide.pdf")

if __name__ == "__main__":
    create_deploy_guide()
