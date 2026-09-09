import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from src.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    serial = Column(String(50), unique=True, nullable=False, index=True)
    serial_number = Column(Integer, nullable=False)
    organization = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(100), nullable=False)
    holder_name = Column(String(255), nullable=False)
    holder_id = Column(String(100), nullable=True)
    file_url = Column(String(1000), nullable=False)
    file_key = Column(String(500), nullable=False)
    qr_code_url = Column(String(1000), nullable=True)
    verify_url = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner_id = Column(String(36), ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")
    verifications = relationship("Verification", back_populates="document")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    verified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="verifications")
