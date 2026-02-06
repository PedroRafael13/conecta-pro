-- Criar ENUMs para GED

-- FolderType
DO $$ BEGIN
    CREATE TYPE foldertype AS ENUM ('sistema', 'condominio', 'contrato', 'funcionario', 'cliente', 'projeto', 'departamento', 'pessoal', 'compartilhada', 'arquivo');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- FolderStatus
DO $$ BEGIN
    CREATE TYPE folderstatus AS ENUM ('ativa', 'arquivada', 'bloqueada', 'excluida');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- DocumentType
DO $$ BEGIN
    CREATE TYPE documenttype AS ENUM ('contrato', 'proposta', 'nota_fiscal', 'boleto', 'comprovante', 'certidao', 'procuracao', 'ata', 'regulamento', 'manual', 'relatorio', 'planilha', 'apresentacao', 'imagem', 'planta', 'projeto', 'laudo', 'orcamento', 'correspondencia', 'outro');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- DocumentStatus
DO $$ BEGIN
    CREATE TYPE documentstatus AS ENUM ('rascunho', 'pendente_aprovacao', 'aprovado', 'rejeitado', 'publicado', 'arquivado', 'expirado', 'excluido');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- DocumentCategory
DO $$ BEGIN
    CREATE TYPE documentcategory AS ENUM ('administrativo', 'financeiro', 'juridico', 'operacional', 'rh', 'comercial', 'tecnico', 'fiscal', 'seguranca', 'outro');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- DocumentConfidentiality
DO $$ BEGIN
    CREATE TYPE documentconfidentiality AS ENUM ('publico', 'interno', 'confidencial', 'restrito', 'secreto');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- FileType
DO $$ BEGIN
    CREATE TYPE filetype AS ENUM ('pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'xml', 'json', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'mp4', 'avi', 'mp3', 'wav', 'zip', 'rar', 'outro');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- VersionType
DO $$ BEGIN
    CREATE TYPE versiontype AS ENUM ('major', 'minor', 'patch', 'revision');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- VersionStatus
DO $$ BEGIN
    CREATE TYPE versionstatus AS ENUM ('ativo', 'arquivado', 'obsoleto');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ShareType
DO $$ BEGIN
    CREATE TYPE sharetype AS ENUM ('usuario', 'grupo', 'email', 'link_publico');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- SharePermission
DO $$ BEGIN
    CREATE TYPE sharepermission AS ENUM ('leitura', 'escrita', 'download', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ShareStatus
DO $$ BEGIN
    CREATE TYPE sharestatus AS ENUM ('ativo', 'revogado', 'expirado');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- TagType
DO $$ BEGIN
    CREATE TYPE tagtype AS ENUM ('geral', 'categoria', 'prioridade', 'status', 'cliente', 'sistema');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- TagColor
DO $$ BEGIN
    CREATE TYPE tagcolor AS ENUM ('blue', 'green', 'red', 'yellow', 'purple', 'orange', 'pink', 'gray');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- SignatureType
DO $$ BEGIN
    CREATE TYPE signaturetype AS ENUM ('eletronica', 'digital', 'manuscrita');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- SignatureStatus
DO $$ BEGIN
    CREATE TYPE signaturestatus AS ENUM ('pendente', 'assinado', 'recusado', 'expirado', 'cancelado');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- SignatureRole
DO $$ BEGIN
    CREATE TYPE signaturerole AS ENUM ('signatario', 'testemunha', 'responsavel', 'aprovador', 'revisor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Alterar colunas para usar ENUMs
ALTER TABLE ged_folders ALTER COLUMN folder_type TYPE foldertype USING folder_type::foldertype;
ALTER TABLE ged_folders ALTER COLUMN status TYPE folderstatus USING status::folderstatus;

ALTER TABLE ged_documents ALTER COLUMN document_type TYPE documenttype USING document_type::documenttype;
ALTER TABLE ged_documents ALTER COLUMN status TYPE documentstatus USING status::documentstatus;
ALTER TABLE ged_documents ALTER COLUMN category TYPE documentcategory USING category::documentcategory;
ALTER TABLE ged_documents ALTER COLUMN confidentiality TYPE documentconfidentiality USING confidentiality::documentconfidentiality;
ALTER TABLE ged_documents ALTER COLUMN file_type TYPE filetype USING file_type::filetype;

ALTER TABLE ged_document_versions ALTER COLUMN version_type TYPE versiontype USING version_type::versiontype;
ALTER TABLE ged_document_versions ALTER COLUMN status TYPE versionstatus USING status::versionstatus;

ALTER TABLE ged_document_tags ALTER COLUMN tag_type TYPE tagtype USING tag_type::tagtype;
ALTER TABLE ged_document_tags ALTER COLUMN color TYPE tagcolor USING color::tagcolor;

ALTER TABLE ged_document_shares ALTER COLUMN share_type TYPE sharetype USING share_type::sharetype;
ALTER TABLE ged_document_shares ALTER COLUMN permission TYPE sharepermission USING permission::sharepermission;
ALTER TABLE ged_document_shares ALTER COLUMN status TYPE sharestatus USING status::sharestatus;

ALTER TABLE ged_document_signatures ALTER COLUMN signature_type TYPE signaturetype USING signature_type::signaturetype;
ALTER TABLE ged_document_signatures ALTER COLUMN status TYPE signaturestatus USING status::signaturestatus;
ALTER TABLE ged_document_signatures ALTER COLUMN signer_role TYPE signaturerole USING signer_role::signaturerole;
