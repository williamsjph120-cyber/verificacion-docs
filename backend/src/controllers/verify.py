import base64
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.config.settings import settings
from src.models.models import Document, Verification
from src.schemas.schemas import VerifyRequest
from src.services.captcha import generate_captcha_text, generate_captcha_image

router = APIRouter(prefix="/api/verify", tags=["Verificación"])

captcha_store = {}


def get_file_url(doc):
    use_r2 = settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY
    if use_r2:
        from src.services.storage import storage
        return storage.get_presigned_url(doc.file_key, expires_in=7200)
    return doc.file_url


@router.get("/{organization}/{serial}/captcha")
def get_captcha(organization: str, serial: str, db: Session = Depends(get_db)):
    doc = (
        db.query(Document)
        .filter(
            Document.organization == organization,
            Document.serial == serial,
            Document.is_active == True,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado o inactivo")

    captcha_text = generate_captcha_text()
    captcha_store[serial] = captcha_text.upper()

    img_buffer = generate_captcha_image(captcha_text)
    img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")

    return {
        "captcha_image": f"data:image/png;base64,{img_base64}",
        "serial": serial,
        "organization": organization,
    }


@router.post("/{organization}/{serial}")
def verify_document(
    organization: str,
    serial: str,
    request: VerifyRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    doc = (
        db.query(Document)
        .filter(
            Document.organization == organization,
            Document.serial == serial,
            Document.is_active == True,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado o inactivo")

    stored_captcha = captcha_store.get(serial)
    if not stored_captcha:
        raise HTTPException(status_code=400, detail="CAPTCHA expirado. Solicite uno nuevo.")

    if request.captcha_text.upper() != stored_captcha:
        del captcha_store[serial]
        raise HTTPException(status_code=400, detail="Código de seguridad incorrecto")

    del captcha_store[serial]

    verification = Verification(
        document_id=doc.id,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
    )
    db.add(verification)
    db.commit()

    file_url = get_file_url(doc)

    return {
        "success": True,
        "message": "Documento verificado exitosamente",
        "document": {
            "id": str(doc.id),
            "serial": doc.serial,
            "organization": doc.organization,
            "title": doc.title,
            "description": doc.description,
            "document_type": doc.document_type,
            "holder_name": doc.holder_name,
            "holder_id": doc.holder_id,
            "file_url": file_url,
            "verified_at": verification.verified_at.isoformat(),
        },
    }


@router.get("/{organization}/{serial}/download")
def download_document(organization: str, serial: str, db: Session = Depends(get_db)):
    doc = (
        db.query(Document)
        .filter(
            Document.organization == organization,
            Document.serial == serial,
            Document.is_active == True,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado o inactivo")

    file_url = get_file_url(doc)

    return {"download_url": file_url, "filename": f"{doc.serial}.pdf"}
