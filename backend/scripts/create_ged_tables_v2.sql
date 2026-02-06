-- GED_FOLDERS
CREATE TABLE ged_folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES ged_folders(id),
    path VARCHAR(1000) NOT NULL DEFAULT '/',
    level INTEGER DEFAULT 0,
    folder_type foldertype DEFAULT 'condominio',
    status folderstatus DEFAULT 'ativa',
    condominium_id UUID,
    contract_id UUID,
    employee_id UUID,
    client_id UUID,
    owner_id UUID NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    inherit_permissions BOOLEAN DEFAULT TRUE,
    permissions JSONB,
    max_file_size_mb INTEGER,
    allowed_extensions TEXT[],
    require_approval BOOLEAN DEFAULT FALSE,
    auto_versioning BOOLEAN DEFAULT TRUE,
    retention_days INTEGER,
    retention_policy VARCHAR(100),
    delete_after_retention BOOLEAN DEFAULT FALSE,
    icon VARCHAR(50),
    color VARCHAR(7),
    "order" INTEGER DEFAULT 0,
    tags TEXT[],
    extra_metadata JSONB,
    document_count INTEGER DEFAULT 0,
    subfolder_count INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    archived_by UUID
);

-- GED_DOCUMENTS
CREATE TABLE ged_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    folder_id UUID NOT NULL REFERENCES ged_folders(id),
    document_type documenttype DEFAULT 'outro',
    category documentcategory DEFAULT 'outro',
    status documentstatus DEFAULT 'rascunho',
    confidentiality documentconfidentiality DEFAULT 'interno',
    file_name VARCHAR(255) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    file_type filetype DEFAULT 'outro',
    file_path VARCHAR(1000) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    thumbnail_path VARCHAR(1000),
    preview_path VARCHAR(1000),
    current_version INTEGER DEFAULT 1,
    version_count INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    condominium_id UUID,
    contract_id UUID,
    employee_id UUID,
    client_id UUID,
    resident_id UUID,
    occurrence_id UUID,
    owner_id UUID NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    inherit_folder_permissions BOOLEAN DEFAULT TRUE,
    permissions JSONB,
    valid_from DATE,
    valid_until DATE,
    is_perpetual BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID,
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    is_signed BOOLEAN DEFAULT FALSE,
    signature_count INTEGER DEFAULT 0,
    requires_signature BOOLEAN DEFAULT FALSE,
    signature_deadline TIMESTAMP,
    is_ocr_processed BOOLEAN DEFAULT FALSE,
    ocr_text TEXT,
    ocr_confidence FLOAT,
    ocr_processed_at TIMESTAMP,
    is_indexed BOOLEAN DEFAULT FALSE,
    indexed_at TIMESTAMP,
    search_keywords TEXT[],
    extra_metadata JSONB,
    custom_fields JSONB,
    external_reference VARCHAR(100),
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,
    last_downloaded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    archived_at TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    archived_by UUID
);

-- GED_DOCUMENT_VERSIONS
CREATE TABLE ged_document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES ged_documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    version_type versiontype DEFAULT 'minor',
    status versionstatus DEFAULT 'ativo',
    file_path VARCHAR(1000) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    change_summary TEXT,
    change_notes TEXT,
    is_current BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    restored_at TIMESTAMP,
    restored_by UUID
);

-- GED_DOCUMENT_TAGS
CREATE TABLE ged_document_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) NOT NULL,
    description TEXT,
    tag_type tagtype DEFAULT 'geral',
    color tagcolor DEFAULT 'blue',
    icon VARCHAR(50),
    usage_count INTEGER DEFAULT 0,
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL
);

-- GED_DOCUMENT_TAG_ASSOCIATIONS
CREATE TABLE ged_document_tag_associations (
    document_id UUID NOT NULL REFERENCES ged_documents(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES ged_document_tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    PRIMARY KEY (document_id, tag_id)
);

-- GED_DOCUMENT_SHARES
CREATE TABLE ged_document_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES ged_documents(id) ON DELETE CASCADE,
    share_type sharetype NOT NULL,
    shared_with_id UUID,
    shared_with_email VARCHAR(255),
    permission sharepermission DEFAULT 'leitura',
    status sharestatus DEFAULT 'ativo',
    access_token VARCHAR(64) UNIQUE,
    public_url VARCHAR(500),
    password_hash VARCHAR(255),
    expires_at TIMESTAMP,
    max_downloads INTEGER,
    download_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    notify_on_access BOOLEAN DEFAULT FALSE,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    last_accessed_at TIMESTAMP,
    revoked_at TIMESTAMP,
    revoked_by UUID
);

-- GED_DOCUMENT_SIGNATURES
CREATE TABLE ged_document_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES ged_documents(id) ON DELETE CASCADE,
    signer_id UUID,
    signer_name VARCHAR(255) NOT NULL,
    signer_email VARCHAR(255) NOT NULL,
    signer_cpf VARCHAR(14),
    signer_role signaturerole DEFAULT 'signatario',
    signature_type signaturetype DEFAULT 'eletronica',
    status signaturestatus DEFAULT 'pendente',
    signature_data TEXT,
    signature_hash VARCHAR(64),
    certificate_data TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    geolocation JSONB,
    "order" INTEGER DEFAULT 0,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_at TIMESTAMP,
    expires_at TIMESTAMP,
    rejected_at TIMESTAMP,
    rejection_reason TEXT,
    created_by UUID NOT NULL
);

-- Indices
CREATE INDEX ix_ged_folders_parent_id ON ged_folders(parent_id);
CREATE INDEX ix_ged_folders_path ON ged_folders(path);
CREATE INDEX ix_ged_folders_status ON ged_folders(status);
CREATE INDEX ix_ged_folders_condominium_id ON ged_folders(condominium_id);
CREATE INDEX ix_ged_documents_folder_id ON ged_documents(folder_id);
CREATE INDEX ix_ged_documents_status ON ged_documents(status);
CREATE INDEX ix_ged_documents_document_type ON ged_documents(document_type);
CREATE INDEX ix_ged_documents_condominium_id ON ged_documents(condominium_id);
CREATE INDEX ix_ged_document_tags_slug ON ged_document_tags(slug);
CREATE INDEX ix_ged_document_versions_document_id ON ged_document_versions(document_id);
CREATE INDEX ix_ged_document_shares_document_id ON ged_document_shares(document_id);
CREATE INDEX ix_ged_document_signatures_document_id ON ged_document_signatures(document_id);
