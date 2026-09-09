from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "admin"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class DocumentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: str
    holder_name: str
    holder_id: Optional[str] = None
    organization: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    token: str
    serial: str
    organization: str
    title: str
    description: Optional[str]
    document_type: str
    holder_name: str
    holder_id: Optional[str]
    file_url: str
    qr_code_url: Optional[str]
    verify_url: Optional[str]
    is_active: bool
    created_at: datetime


class SerialPreviewResponse(BaseModel):
    serial: str
    organization: str


class VerifyRequest(BaseModel):
    captcha_text: str


class VerifyResponse(BaseModel):
    success: bool
    message: str
    document: Optional[dict] = None


class VerificationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    ip_address: Optional[str]
    verified_at: datetime
