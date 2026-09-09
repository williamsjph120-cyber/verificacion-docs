-- Migration: Create initial schema
-- Run: psql -d verificacion_docs -f 001_create_tables.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(36) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    document_type VARCHAR(100) NOT NULL,
    holder_name VARCHAR(255) NOT NULL,
    holder_id VARCHAR(100),
    file_url VARCHAR(1000) NOT NULL,
    file_key VARCHAR(500) NOT NULL,
    qr_code_url VARCHAR(1000),
    is_active BOOLEAN DEFAULT TRUE,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_token ON documents(token);
CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_verifications_document ON verifications(document_id);
CREATE INDEX idx_users_email ON users(email);
