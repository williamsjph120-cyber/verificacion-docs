from datetime import datetime
from sqlalchemy.orm import Session
from src.models.models import Document


def _interleave_name_and_number(name: str, number: int) -> str:
    """
    Intercala letras del nombre con digitos del numero.
    Ejemplo: Juan Perez, 1 -> J0U1A2N3P4E5R6E7Z8
    """
    clean_name = name.replace(' ', '').upper()
    num_str = str(number).zfill(6)

    result = []
    name_idx = 0
    num_idx = 0

    while name_idx < len(clean_name) or num_idx < len(num_str):
        if name_idx < len(clean_name):
            result.append(clean_name[name_idx])
            name_idx += 1
        if num_idx < len(num_str):
            result.append(num_str[num_idx])
            num_idx += 1

    return ''.join(result)


def generate_serial(db: Session, organization: str, holder_name: str) -> tuple[str, int]:
    """
    Genera un serial único para un documento.
    Formato: Letras del nombre intercaladas con numeros
    Ejemplo: J0U1A2N3P4E5R6E7Z8
    """
    year = datetime.now().year

    last_doc = (
        db.query(Document)
        .filter(Document.organization == organization, Document.year == year)
        .order_by(Document.serial_number.desc())
        .first()
    )

    if last_doc:
        next_number = last_doc.serial_number + 1
    else:
        next_number = 1

    serial = _interleave_name_and_number(holder_name, next_number)

    return serial, next_number, year


def get_next_serial_preview(db: Session, organization: str, holder_name: str) -> str:
    """Muestra el próximo serial sin crearlo."""
    serial, _, _ = generate_serial(db, organization, holder_name)
    return serial
