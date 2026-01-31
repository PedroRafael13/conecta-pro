# Security LGPD Module

Módulo completo de Compliance LGPD (Lei 13.709/2018) - Lei Geral de Proteção de Dados.

## Visão Geral

Este módulo implementa todos os requisitos técnicos e operacionais necessários para compliance com a LGPD, incluindo:

- **Gestão de Consentimentos** (Art. 7, 8, 9)
- **Criptografia de Dados Sensíveis** (AES-256-GCM, ChaCha20, RSA)
- **Trilha de Auditoria com Hash Chain** (Art. 46)
- **Direito ao Esquecimento** (Art. 18)
- **Avaliação de Impacto à Privacidade (PIA/DPIA)** (Art. 38)
- **Mascaramento de PII** (CPF, email, telefone, etc)
- **Monitoramento de Status e Health Check**

## Arquitetura

### Services (7 arquivos - 1.886 linhas)

#### 1. ConsentService
Gestão de consentimentos LGPD conforme Art. 7, 8 e 9.

```typescript
import { ConsentService } from '@/services/security-lgpd';

// Registrar consentimento
await ConsentService.registerConsent({
  titular_id: '123e4567-e89b-12d3-a456-426614174000',
  titular_email: 'usuario@exemplo.com',
  purpose: 'marketing',
  legal_basis: 'consent',
  expiration_days: 365,
});

// Revogar consentimento
await ConsentService.revokeConsent(consentId, 'Não desejo mais receber');

// Listar consentimentos ativos
const consents = await ConsentService.getConsents(titularId);
```

#### 2. EncryptionService
Criptografia de dados sensíveis com múltiplos algoritmos.

```typescript
import { EncryptionService } from '@/services/security-lgpd';

// Criptografar dados
const result = await EncryptionService.encryptData(
  'dados sensíveis',
  'AES-256-GCM'
);

// Helpers específicos
const encryptedCPF = await EncryptionService.encryptCPF('12345678900');
const encryptedEmail = await EncryptionService.encryptEmail('email@exemplo.com');

// Batch encryption
const batch = await EncryptionService.encryptBatch(['dado1', 'dado2', 'dado3']);
```

**Algoritmos Suportados:**
- AES-256-GCM (Recomendado)
- AES-256-CBC
- Fernet
- ChaCha20-Poly1305
- RSA-OAEP

#### 3. AuditService
Trilha de auditoria imutável com hash chain (Art. 46).

```typescript
import { AuditService } from '@/services/security-lgpd';

// Registrar evento
await AuditService.createAuditLog({
  action: 'ACCESS',
  resource_type: 'personal_data',
  resource_id: '123',
  user_id: 'user-456',
  severity: 'medium',
  details: { ip_address: '192.168.1.1' },
});

// Helpers específicos
await AuditService.logDataAccess(userId, resourceType, resourceId);
await AuditService.logDataModification(userId, resourceType, resourceId, changes);
await AuditService.logSecurityIncident(userId, type, description, 'critical');
```

#### 4. ErasureService
Direito ao Esquecimento (Art. 18, VI).

```typescript
import { ErasureService } from '@/services/security-lgpd';

// Solicitação de exclusão total
await ErasureService.requestFullErasure(titularId, email, 'Motivo da exclusão');

// Exclusão parcial (apenas dados pessoais)
await ErasureService.requestPersonalDataErasure(titularId, email, motivo);

// Consultar status
const status = await ErasureService.getErasureStatus(requestId);
```

**Escopos de Exclusão:**
- `all`: Remove todos os dados (irreversível)
- `personal`: Remove dados pessoais, mantém transações anonimizadas
- `transactional`: Remove histórico transacional

#### 5. PIAService
Avaliação de Impacto à Proteção de Dados (Art. 38).

```typescript
import { PIAService } from '@/services/security-lgpd';

// Criar avaliação completa
await PIAService.createCompletePIA(
  'Novo Sistema',
  'Descrição do projeto',
  ['personal_identification', 'financial'],
  ['service_provision', 'marketing'],
  ['customers', 'employees'],
  ['data_breach', 'unauthorized_access']
);

// Calcular nível de risco
const riskLevel = PIAService.calculateRiskLevel(assessment);
// Retorna: 'low' | 'medium' | 'high' | 'critical'
```

#### 6. MaskingService
Mascaramento de PII (Personally Identifiable Information).

```typescript
import { MaskingService } from '@/services/security-lgpd';

// Mascarar dados
const masked = await MaskingService.maskCPF('123.456.789-00', 'partial');
// Resultado: ***.456.789-00

// Helpers locais (sem chamada API)
const maskedLocal = MaskingService.maskCPFLocal('12345678900', 'partial');
const maskedEmail = MaskingService.maskEmailLocal('usuario@exemplo.com');

// Detecção automática de categoria
const category = MaskingService.detectCategory('123.456.789-00');
// Retorna: 'cpf'
```

**Categorias Suportadas:**
- CPF
- Email
- Telefone
- Nome
- Endereço
- Cartão de Crédito

**Níveis de Mascaramento:**
- `partial`: Exibe parte dos dados
- `full`: Oculta completamente
- `custom`: Regras personalizadas

#### 7. StatusService
Monitoramento de status e health check.

```typescript
import { StatusService } from '@/services/security-lgpd';

// Verificar saúde do módulo
const isHealthy = await StatusService.isHealthy();

// Status completo
const status = await StatusService.getLGPDStatus();

// Status por componente
const components = await StatusService.getComponentsStatus();
// { consent: true, encryption: true, audit: true, ... }

// Score de compliance
const score = StatusService.calculateComplianceScore(statusData);
// Retorna: 0-100
```

### React Query Hooks (8 arquivos - 952 linhas)

#### useConsent (7 hooks)
```typescript
import {
  useRegisterConsent,
  useConsents,
  useRevokeConsent,
  usePurposes,
  useLegalBases,
  useActiveConsents,
  useExpiringConsents,
} from '@/hooks/security-lgpd';

// Registrar consentimento
const { mutate: register } = useRegisterConsent();
register({
  titular_id: '123',
  titular_email: 'usuario@exemplo.com',
  purpose: 'marketing',
  legal_basis: 'consent',
});

// Listar consentimentos
const { data: consents } = useConsents(titularId);

// Consentimentos expirando em 30 dias
const { data: expiring } = useExpiringConsents(titularId, 30);
```

#### useEncryption (8 hooks)
```typescript
import {
  useEncryptData,
  useDecryptData,
  useEncryptCPF,
  useEncryptEmail,
  useAlgorithms,
} from '@/hooks/security-lgpd';

const { mutate: encrypt } = useEncryptData();
encrypt({ data: 'dados sensíveis', algorithm: 'AES-256-GCM' });

const { data: algorithms } = useAlgorithms();
```

#### useAudit (12 hooks)
```typescript
import {
  useCreateAuditLog,
  useAuditLogs,
  useLogDataAccess,
  useLogDataModification,
  useLogsByUser,
} from '@/hooks/security-lgpd';

const { mutate: logAccess } = useLogDataAccess();
logAccess({
  userId: 'user-123',
  resourceType: 'personal_data',
  resourceId: 'data-456',
});

const { data: logs } = useLogsByUser(userId, 100);
```

#### useErasure (5 hooks)
```typescript
import {
  useRequestErasure,
  useErasureStatus,
  useRequestFullErasure,
} from '@/hooks/security-lgpd';

const { mutate: requestErasure } = useRequestFullErasure();
requestErasure({
  titularId: '123',
  titularEmail: 'user@example.com',
  reason: 'Não utilizo mais o serviço',
});

// Status com polling automático a cada 5 segundos
const { data: status } = useErasureStatus(requestId);
```

#### usePIA (5 hooks)
```typescript
import {
  useCreatePIA,
  usePIA,
  useRiskCategories,
} from '@/hooks/security-lgpd';

const { mutate: createPIA } = useCreatePIA();
const { data: assessment } = usePIA(assessmentId);
const { data: categories } = useRiskCategories();
```

#### useMasking (9 hooks)
```typescript
import {
  useMaskData,
  useMaskCPF,
  useMaskEmail,
  useMaskingFormats,
} from '@/hooks/security-lgpd';

const { mutate: maskCPF } = useMaskCPF();
maskCPF({ cpf: '123.456.789-00', level: 'partial' });

const { data: formats } = useMaskingFormats();
```

#### useStatus (4 hooks)
```typescript
import {
  useLGPDStatus,
  useHealthCheck,
  useIsHealthy,
  useComponentsStatus,
} from '@/hooks/security-lgpd';

const { data: status } = useLGPDStatus();
const { data: health } = useHealthCheck();
const { data: isHealthy } = useIsHealthy();
const { data: components } = useComponentsStatus();
```

## Cobertura de Endpoints

Total: **21 endpoints** implementados

### Consentimento (5 endpoints)
- `POST /lgpd/consent/register` - Registrar consentimento
- `GET /lgpd/consent/{titular_id}` - Consultar consentimentos
- `DELETE /lgpd/consent/{consent_id}/revoke` - Revogar consentimento
- `GET /lgpd/consent/purposes/list` - Listar finalidades
- `GET /lgpd/consent/legal-bases/list` - Listar bases legais

### Criptografia (3 endpoints)
- `POST /lgpd/encryption/encrypt` - Criptografar dados
- `POST /lgpd/encryption/decrypt` - Descriptografar dados
- `GET /lgpd/encryption/algorithms` - Listar algoritmos

### Auditoria (4 endpoints)
- `POST /lgpd/audit/log` - Registrar evento
- `GET /lgpd/audit/logs` - Listar eventos
- `GET /lgpd/audit/actions/list` - Listar ações
- `GET /lgpd/audit/resource-types/list` - Listar tipos de recurso

### Direito ao Esquecimento (2 endpoints)
- `POST /lgpd/erasure/request` - Solicitar exclusão
- `GET /lgpd/erasure/{request_id}/status` - Consultar status

### Avaliação de Impacto (3 endpoints)
- `POST /lgpd/pia/create` - Criar avaliação PIA/DPIA
- `GET /lgpd/pia/{assessment_id}` - Consultar avaliação
- `GET /lgpd/pia/risk-categories/list` - Listar categorias de risco

### Mascaramento (2 endpoints)
- `POST /lgpd/masking/mask` - Mascarar dados
- `GET /lgpd/masking/formats` - Listar formatos

### Status (2 endpoints)
- `GET /lgpd/status` - Status do módulo
- `GET /lgpd/health` - Health check

## Compliance LGPD

### Artigos Implementados

✅ **Art. 7** - Tratamento de dados pessoais (bases legais)
✅ **Art. 8** - Consentimento
✅ **Art. 9** - Consentimento de crianças e adolescentes
✅ **Art. 18** - Direitos do titular (direito ao esquecimento)
✅ **Art. 38** - Relatório de impacto à proteção de dados
✅ **Art. 46** - Controles de segurança e registros de acesso

### Boas Práticas

- **Privacy by Design**: Segurança desde a concepção
- **Minimização de Dados**: Coleta apenas dados necessários
- **Transparência**: Logs de auditoria completos
- **Portabilidade**: Exportação de dados estruturados
- **Segurança**: Criptografia de ponta a ponta
- **Accountability**: Rastreabilidade completa

## Estrutura de Arquivos

```
frontend/src/
├── services/security-lgpd/
│   ├── consentService.ts       (4.279 linhas)
│   ├── encryptionService.ts    (5.530 linhas)
│   ├── auditService.ts         (6.654 linhas)
│   ├── erasureService.ts       (6.795 linhas)
│   ├── piaService.ts           (9.392 linhas)
│   ├── maskingService.ts       (9.621 linhas)
│   ├── statusService.ts        (9.134 linhas)
│   ├── index.ts                (1.498 linhas)
│   └── README.md               (este arquivo)
│
├── hooks/security-lgpd/
│   ├── useConsent.ts           (3.559 linhas)
│   ├── useEncryption.ts        (2.105 linhas)
│   ├── useAudit.ts             (5.320 linhas)
│   ├── useErasure.ts           (2.720 linhas)
│   ├── usePIA.ts               (2.570 linhas)
│   ├── useMasking.ts           (2.747 linhas)
│   ├── useStatus.ts            (1.330 linhas)
│   └── index.ts                (1.684 linhas)
│
└── types/generated/security-lgpd/
    ├── conectaPROLGPDSecurityAPI.schemas.ts
    ├── lgpd-consentimento/
    ├── lgpd-criptografia/
    ├── lgpd-auditoria/
    ├── lgpd-direito-ao-esquecimento/
    ├── lgpd-avaliação-de-impacto-pia-dpia/
    ├── lgpd-mascaramento/
    └── lgpd-status/
```

## Uso Integrado

### Exemplo: Fluxo Completo de Consentimento

```typescript
import {
  useRegisterConsent,
  useLogDataAccess,
  useEncryptData,
} from '@/hooks/security-lgpd';

function ConsentFlow() {
  const { mutate: register } = useRegisterConsent();
  const { mutate: logAccess } = useLogDataAccess();
  const { mutate: encrypt } = useEncryptData();

  const handleConsent = async () => {
    // 1. Registrar consentimento
    register({
      titular_id: user.id,
      titular_email: user.email,
      purpose: 'marketing',
      legal_basis: 'consent',
    });

    // 2. Criptografar dados sensíveis
    encrypt({
      data: user.cpf,
      algorithm: 'AES-256-GCM',
    });

    // 3. Registrar na trilha de auditoria
    logAccess({
      userId: admin.id,
      resourceType: 'consent',
      resourceId: user.id,
    });
  };
}
```

### Exemplo: Dashboard de Compliance

```typescript
import {
  useLGPDStatus,
  useComponentsStatus,
  useAuditLogs,
} from '@/hooks/security-lgpd';

function ComplianceDashboard() {
  const { data: status } = useLGPDStatus();
  const { data: components } = useComponentsStatus();
  const { data: recentLogs } = useAuditLogs({ limit: 10 });

  const score = StatusService.calculateComplianceScore(status?.data);

  return (
    <div>
      <h1>Compliance Score: {score}%</h1>
      <ComponentStatus components={components} />
      <RecentActivity logs={recentLogs} />
    </div>
  );
}
```

## Estatísticas

- **Services**: 7 arquivos, 1.886 linhas de código
- **Hooks**: 8 arquivos, 952 linhas de código
- **Total**: 15 arquivos, 2.838 linhas de código
- **Endpoints**: 21 endpoints REST
- **Hooks React Query**: 48 hooks customizados
- **Tipos TypeScript**: 100% tipado com Orval

## Tecnologias

- **Orval**: Geração de tipos e clients TypeScript
- **React Query**: Gerenciamento de estado assíncrono
- **Axios**: Client HTTP
- **TypeScript**: Tipagem estática
- **LGPD**: Lei 13.709/2018

## Geração de Tipos

Para regenerar os tipos a partir do OpenAPI spec:

```bash
npm run orval:security-lgpd
```

## Testes

```bash
# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

## Licença

Proprietary - Conecta Plus © 2026

---

**Desenvolvido com compliance em mente**
Lei 13.709/2018 - Lei Geral de Proteção de Dados
