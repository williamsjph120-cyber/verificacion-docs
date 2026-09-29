import io
import os
import uuid as uuid_lib
from datetime import datetime
from urllib.parse import urlparse, unquote
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.config.settings import settings
from src.models.models import Document, User
from src.schemas.schemas import DocumentResponse, SerialPreviewResponse, QRPreviewResponse
from src.services.auth import get_current_user
from src.services.qr_generator import generate_qr_code
from src.services.serial_generator import generate_serial, get_next_serial_preview

router = APIRouter(prefix="/api/documents", tags=["Documentos"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file_locally(file_data: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "pdf"
    key = f"{uuid_lib.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, key)
    with open(filepath, "wb") as f:
        f.write(file_data)
    return key


def get_local_url(key: str) -> str:
    return f"http://localhost:8000/uploads/{key}"


def get_frontend_url() -> str:
    return settings.FRONTEND_URL


# Las URLs firmadas (presigned) de R2 caducan, por eso NUNCA se guardan como
# enlace vigente: se firma una URL nueva en cada lectura del documento.
PRESIGNED_URL_TTL = 86400  # 24 horas


def use_r2() -> bool:
    return bool(settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY)


def _key_from_stored_url(url: str, prefixes: tuple, default: str) -> str:
    """Recupera la clave de almacenamiento desde una URL guardada (legacy).

    Cubre documentos ya creados: su `qr_code_url` guardada es una URL firmada
    vencida, pero la clave sigue siendo legible desde su path.
    """
    if url:
        parts = unquote(urlparse(url).path).lstrip("/").split("/")
        for prefix in prefixes:
            if prefix in parts:
                return "/".join(parts[parts.index(prefix):])
        # URLs locales: http://localhost:8000/uploads/qr_SERIAL.png
        if parts and parts[0] == "uploads" and len(parts) > 1:
            return "/".join(parts[1:])
    return default


def get_file_url(doc) -> str:
    """URL vigente del PDF, firmada al momento de leer."""
    if use_r2():
        from src.services.storage import storage
        return storage.get_presigned_url(doc.file_key, expires_in=PRESIGNED_URL_TTL)
    return get_local_url(doc.file_key)


def get_qr_url(doc) -> str:
    """URL vigente del QR, derivada de la clave ya existente en el documento."""
    if use_r2():
        from src.services.storage import storage
        key = _key_from_stored_url(doc.qr_code_url, ("qr-codes",), f"qr-codes/{doc.serial}.png")
        return storage.get_presigned_url(key, expires_in=PRESIGNED_URL_TTL)
    key = _key_from_stored_url(doc.qr_code_url, (), f"qr_{doc.serial}.png")
    return get_local_url(key)


def document_response(doc) -> DocumentResponse:
    """Construye la respuesta con URLs frescas sin modificar el registro guardado."""
    return DocumentResponse(
        id=doc.id,
        token=doc.token,
        serial=doc.serial,
        organization=doc.organization,
        title=doc.title,
        description=doc.description,
        document_type=doc.document_type,
        holder_name=doc.holder_name,
        holder_id=doc.holder_id,
        file_url=get_file_url(doc),
        qr_code_url=get_qr_url(doc),
        verify_url=doc.verify_url,
        is_active=doc.is_active,
        created_at=doc.created_at,
    )


@router.get("/preview-serial/{organization}", response_model=SerialPreviewResponse)
def preview_serial(
    organization: str,
    holder_name: str = "Titular",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    serial = get_next_serial_preview(db, organization, holder_name)
    return SerialPreviewResponse(serial=serial, organization=organization)


@router.get("/preview-qr/{organization}", response_model=QRPreviewResponse)
def preview_qr(
    organization: str,
    holder_name: str = "Titular",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    serial = get_next_serial_preview(db, organization, holder_name)
    frontend_url = get_frontend_url()
    verify_url = f"{frontend_url}/inbox/app/{organization}/{serial}"

    qr_data = generate_qr_code(verify_url)
    qr_base64 = io.BytesIO(qr_data.read()).getvalue()
    import base64
    qr_data_url = f"data:image/png;base64,{base64.b64encode(qr_base64).decode('utf-8')}"

    return QRPreviewResponse(
        serial=serial,
        verify_url=verify_url,
        qr_code_url=qr_data_url,
    )


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    title: str = Form(...),
    description: str = Form(None),
    document_type: str = Form(...),
    holder_name: str = Form(...),
    holder_id: str = Form(None),
    organization: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    serial, serial_number, year = generate_serial(db, organization, holder_name)

    file_data = await file.read()
    use_r2 = settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY

    if use_r2:
        from src.services.storage import storage
        file_key = storage.upload_file(io.BytesIO(file_data), file.filename, file.content_type)
        file_url = storage.get_presigned_url(file_key)
    else:
        file_key = save_file_locally(file_data, file.filename)
        file_url = get_local_url(file_key)

    frontend_url = get_frontend_url()
    verify_url = f"{frontend_url}/inbox/app/{organization}/{serial}"

    doc = Document(
        serial=serial,
        serial_number=serial_number,
        organization=organization,
        year=year,
        title=title,
        description=description,
        document_type=document_type,
        holder_name=holder_name,
        holder_id=holder_id,
        file_url=file_url,
        file_key=file_key,
        verify_url=verify_url,
        owner_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    qr_data = generate_qr_code(verify_url)

    if use_r2:
        from src.services.storage import storage
        qr_key = storage.upload_qr(qr_data, doc.serial)
        doc.qr_code_url = storage.get_presigned_url(qr_key)
    else:
        qr_filename = f"qr_{doc.serial}.png"
        qr_path = os.path.join(UPLOAD_DIR, qr_filename)
        with open(qr_path, "wb") as f:
            f.write(qr_data.read())
        doc.qr_code_url = get_local_url(qr_filename)

    db.commit()
    db.refresh(doc)

    return document_response(doc)


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 50,
    organization: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    if organization:
        query = query.filter(Document.organization == organization)
    docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return [document_response(doc) for doc in docs]


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document_response(doc)


@router.delete("/{doc_id}", status_code=204)
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    use_r2 = settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY
    if use_r2:
        from src.services.storage import storage
        storage.delete_file(doc.file_key)
    else:
        filepath = os.path.join(UPLOAD_DIR, doc.file_key)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.delete(doc)
    db.commit()
