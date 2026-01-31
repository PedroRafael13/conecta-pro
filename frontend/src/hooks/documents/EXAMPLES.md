# Exemplos de Uso - Módulo Documents

Guia prático para utilizar os hooks do módulo Document Intelligence.

## Upload de Documentos

### Upload Único

```tsx
import { useUploadDocument } from '@/hooks/documents';

function UploadForm() {
  const uploadMutation = useUploadDocument();

  const handleUpload = async (file: File) => {
    await uploadMutation.mutateAsync({
      file,
      tenant_id: 'abc-123',
      source: 'upload',
      auto_process: true,
    });
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUpload(file);
        }}
        accept=".pdf,.png,.jpg,.jpeg,.tiff"
      />
      {uploadMutation.isPending && <p>Enviando...</p>}
    </div>
  );
}
```

### Upload em Lote

```tsx
import { useUploadBatch } from '@/hooks/documents';

function BatchUploadForm() {
  const batchMutation = useUploadBatch();

  const handleBatchUpload = async (files: FileList) => {
    const filesArray = Array.from(files);

    await batchMutation.mutateAsync({
      files: filesArray,
      tenant_id: 'abc-123',
    });
  };

  return (
    <input
      type="file"
      multiple
      onChange={(e) => {
        if (e.target.files) handleBatchUpload(e.target.files);
      }}
    />
  );
}
```

## Processamento de Documentos

### OCR

```tsx
import { useRunOCR } from '@/hooks/documents';

function OCRButton({ documentId }: { documentId: string }) {
  const ocrMutation = useRunOCR();

  const handleOCR = async () => {
    const result = await ocrMutation.mutateAsync({
      document_id: documentId,
      provider: 'tesseract', // ou 'easyocr', 'google_vision'
      languages: 'por,eng',
    });

    console.log(`OCR concluído: ${result.words} palavras em ${result.pages} páginas`);
    console.log(`Confiança: ${result.confidence}%`);
  };

  return (
    <button onClick={handleOCR} disabled={ocrMutation.isPending}>
      {ocrMutation.isPending ? 'Processando OCR...' : 'Executar OCR'}
    </button>
  );
}
```

### Classificação Automática

```tsx
import { useClassifyDocument } from '@/hooks/documents';

function ClassifyButton({ documentId }: { documentId: string }) {
  const classifyMutation = useClassifyDocument();

  const handleClassify = async () => {
    const result = await classifyMutation.mutateAsync(documentId);

    console.log(`Tipo: ${result.document_type}`);
    console.log(`Confiança: ${result.confidence * 100}%`);
    console.log('Keywords encontradas:', result.matched_keywords);
  };

  return (
    <button onClick={handleClassify}>Classificar Documento</button>
  );
}
```

### Extração de Dados

```tsx
import { useExtractData } from '@/hooks/documents';

function ExtractButton({ documentId }: { documentId: string }) {
  const extractMutation = useExtractData();

  const handleExtract = async (templateId?: string) => {
    const result = await extractMutation.mutateAsync({
      document_id: documentId,
      template_id: templateId, // opcional
    });

    console.log(`Campos extraídos: ${result.fields_extracted}`);
    console.log('Dados:', result.fields);
  };

  return (
    <button onClick={() => handleExtract()}>Extrair Dados</button>
  );
}
```

### Validação de Dados

```tsx
import { useValidateData } from '@/hooks/documents';

function ValidateButton({ documentId }: { documentId: string }) {
  const validateMutation = useValidateData();

  const handleValidate = async () => {
    const result = await validateMutation.mutateAsync(documentId);

    if (result.is_valid) {
      console.log('Documento válido!');
    } else {
      console.log('Erros:', result.errors);
      console.log('Avisos:', result.warnings);
    }
  };

  return (
    <button onClick={handleValidate}>Validar Dados</button>
  );
}
```

### Processamento Completo (Pipeline)

```tsx
import { useProcessDocument } from '@/hooks/documents';

function ProcessButton({ documentId }: { documentId: string }) {
  const processMutation = useProcessDocument();

  const handleFullProcess = async () => {
    const result = await processMutation.mutateAsync({
      document_id: documentId,
      request: {
        classify: true,
        extract: true,
        validate: true,
        template_id: null, // opcional
      },
    });

    console.log('Processamento completo:', result);
    console.log('Tipo:', result.document_type);
    console.log('Status:', result.status);
    console.log('Requer revisão?', result.needs_review);
    console.log('Dados extraídos:', result.extracted_data);
  };

  return (
    <button onClick={handleFullProcess} disabled={processMutation.isPending}>
      {processMutation.isPending ? 'Processando...' : 'Processar Documento'}
    </button>
  );
}
```

## Templates de Extração

### Listar Templates

```tsx
import { useTemplates } from '@/hooks/documents';

function TemplatesList() {
  const { data: templates, isLoading } = useTemplates({
    category: 'fiscal', // opcional
    document_type: 'nota_fiscal', // opcional
    include_builtin: true,
  });

  if (isLoading) return <p>Carregando templates...</p>;

  return (
    <ul>
      {templates?.map((template) => (
        <li key={template.id}>
          {template.name} - {template.document_type}
          <span>
            ({template.fields_count} campos, {template.success_rate}% sucesso)
          </span>
          {template.is_official && <span>✓ Oficial</span>}
        </li>
      ))}
    </ul>
  );
}
```

### Criar Template

```tsx
import { useCreateTemplate } from '@/hooks/documents';

function CreateTemplateForm() {
  const createMutation = useCreateTemplate();

  const handleCreate = async () => {
    await createMutation.mutateAsync({
      tenant_id: 'abc-123',
      template: {
        name: 'Nota Fiscal Paulista',
        description: 'Template para NF-e do Estado de SP',
        document_type: 'nota_fiscal',
        category: 'fiscal',
        detection_keywords: ['nota fiscal', 'nfe', 'danfe'],
        fields: [
          { name: 'numero_nota', type: 'string', required: true },
          { name: 'valor_total', type: 'decimal', required: true },
          { name: 'data_emissao', type: 'date', required: true },
        ],
      },
    });
  };

  return <button onClick={handleCreate}>Criar Template</button>;
}
```

### Deletar Template

```tsx
import { useDeleteTemplate } from '@/hooks/documents';

function DeleteButton({ templateId }: { templateId: string }) {
  const deleteMutation = useDeleteTemplate();

  const handleDelete = async () => {
    if (confirm('Deseja realmente remover este template?')) {
      await deleteMutation.mutateAsync(templateId);
    }
  };

  return (
    <button onClick={handleDelete} disabled={deleteMutation.isPending}>
      Remover Template
    </button>
  );
}
```

## Metadata e Estatísticas

### Tipos de Documentos

```tsx
import { useDocumentTypes } from '@/hooks/documents';

function DocumentTypeSelect() {
  const { data: types, isLoading } = useDocumentTypes();

  if (isLoading) return <p>Carregando tipos...</p>;

  return (
    <select>
      <option>Selecione o tipo</option>
      {types?.map((type, index) => (
        <option key={index} value={Object.keys(type)[0]}>
          {Object.values(type)[0]}
        </option>
      ))}
    </select>
  );
}
```

### Providers OCR

```tsx
import { useOCRProviders } from '@/hooks/documents';

function OCRProviderSelect() {
  const { data: providers } = useOCRProviders();

  return (
    <select>
      <option>Selecione o provider</option>
      <option value="tesseract">Tesseract (Offline)</option>
      <option value="easyocr">EasyOCR (Offline)</option>
      <option value="google_vision">Google Vision (Online)</option>
    </select>
  );
}
```

### Estatísticas de Armazenamento

```tsx
import { useStorageStats } from '@/hooks/documents';

function StorageStatsCard({ tenantId }: { tenantId: string }) {
  const { data: stats, isLoading } = useStorageStats(tenantId);

  if (isLoading) return <p>Carregando estatísticas...</p>;

  return (
    <div className="card">
      <h3>Estatísticas de Armazenamento</h3>
      <pre>{JSON.stringify(stats, null, 2)}</pre>
    </div>
  );
}
```

### Validação de CPF/CNPJ

```tsx
import { useValidateCPF, useValidateCNPJ } from '@/hooks/documents';

function DocumentValidator() {
  const validateCPF = useValidateCPF();
  const validateCNPJ = useValidateCNPJ();

  const handleValidateCPF = (cpf: string) => {
    validateCPF.mutate(cpf);
    // Toast automático: "CPF válido" ou "CPF inválido"
  };

  const handleValidateCNPJ = (cnpj: string) => {
    validateCNPJ.mutate(cnpj);
    // Toast automático: "CNPJ válido" ou "CNPJ inválido"
  };

  return (
    <div>
      <input
        placeholder="CPF"
        onBlur={(e) => handleValidateCPF(e.target.value)}
      />
      <input
        placeholder="CNPJ"
        onBlur={(e) => handleValidateCNPJ(e.target.value)}
      />
    </div>
  );
}
```

### Validação Silenciosa (sem toast)

```tsx
import { useValidateCPFSilent } from '@/hooks/documents';

function CPFInput() {
  const [cpf, setCPF] = useState('');
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const validateCPF = useValidateCPFSilent();

  const handleBlur = async () => {
    const result = await validateCPF.mutateAsync(cpf);
    setIsValid(result.valid);
  };

  return (
    <div>
      <input
        value={cpf}
        onChange={(e) => setCPF(e.target.value)}
        onBlur={handleBlur}
        className={isValid === false ? 'border-red-500' : ''}
      />
      {isValid === false && <span className="text-red-500">CPF inválido</span>}
    </div>
  );
}
```

## Exemplo Completo: Upload e Processamento

```tsx
import { useState } from 'react';
import {
  useUploadDocument,
  useProcessDocument,
} from '@/hooks/documents';

function DocumentUploadAndProcess() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const uploadMutation = useUploadDocument();
  const processMutation = useProcessDocument();

  const handleUpload = async (file: File) => {
    const result = await uploadMutation.mutateAsync({
      file,
      tenant_id: 'abc-123',
      source: 'upload',
      auto_process: false, // processar manualmente
    });

    if (result.document_id) {
      setDocumentId(result.document_id);
    }
  };

  const handleProcess = async () => {
    if (!documentId) return;

    await processMutation.mutateAsync({
      document_id: documentId,
      request: {
        classify: true,
        extract: true,
        validate: true,
      },
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <input
          type="file"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleUpload(file);
          }}
        />
        {uploadMutation.isPending && <p>Enviando documento...</p>}
      </div>

      {documentId && (
        <div>
          <p>Documento ID: {documentId}</p>
          <button
            onClick={handleProcess}
            disabled={processMutation.isPending}
          >
            {processMutation.isPending
              ? 'Processando...'
              : 'Processar Documento'}
          </button>
        </div>
      )}

      {processMutation.isSuccess && (
        <div className="bg-green-100 p-4 rounded">
          <h3>Processamento Concluído!</h3>
          <pre>
            {JSON.stringify(processMutation.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
```

## Notas

- Todos os hooks incluem toast notifications automáticos
- Loading states disponíveis via `isPending` ou `isLoading`
- Invalidação de cache automática após mutations
- Tipos TypeScript completos e sincronizados com backend
- Tratamento de erros integrado
