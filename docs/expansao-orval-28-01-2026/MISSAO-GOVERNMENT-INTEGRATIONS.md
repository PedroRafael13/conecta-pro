# 🏛️ MISSÃO: COMPLETAR COBERTURA GOVERNMENT INTEGRATIONS (26% → 100%)

**Data:** 28/01/2026
**Módulo:** GOVERNMENT INTEGRATIONS (Integrações Governamentais)
**Status Atual:** 🔴 26% COBERTURA (56/209 endpoints)
**Status Alvo:** ✅ 100% COBERTURA (209/209 endpoints)
**Prioridade:** 🔴 CRÍTICO (Compliance obrigatório)

---

## 📊 SITUAÇÃO ATUAL

```
╔════════════════════════════════════════════════════════════════╗
║  MÓDULO GOVERNMENT INTEGRATIONS - STATUS ATUAL                 ║
╠════════════════════════════════════════════════════════════════╣
║  📦 Endpoints Backend:           209                           ║
║  ✅ Endpoints Implementados:     56 (26%)                      ║
║  ❌ Endpoints FALTANTES:         153 (74%)                     ║
║  📁 Controllers:                 24                            ║
║  🎯 Prioridade:                  ALTO (Compliance)             ║
╚════════════════════════════════════════════════════════════════╝
```

### Análise por Controller

| Controller | Endpoints | Status | Prioridade |
|------------|-----------|--------|------------|
| `sync_controller.py` | 16 | ⚠️ Parcial | 🔴 Crítico |
| `nfse_manaus_controller.py` | 8 | ⚠️ Parcial | 🔴 Crítico |
| `nfse_nacional_controller.py` | 12 | ⚠️ Parcial | 🔴 Crítico |
| `sped_fiscal_controller.py` | 13 | ⚠️ Parcial | 🔴 Crítico |
| `sped_contabil_controller.py` | 13 | ⚠️ Parcial | 🔴 Crítico |
| `esocial_controller.py` | 3 | ⚠️ Parcial | 🔴 Crítico |
| `sefaz_controller.py` | 2 | ⚠️ Parcial | 🔴 Crítico |
| `sefaz_am_controller.py` | 8 | ⚠️ Parcial | 🟡 Alto |
| `fgts_digital_controller.py` | 11 | ❌ Ausente | 🔴 Crítico |
| `fgts_inss_controller.py` | 3 | ⚠️ Parcial | 🔴 Crítico |
| `dctfweb_controller.py` | 11 | ❌ Ausente | 🟡 Alto |
| `efd_reinf_controller.py` | 9 | ❌ Ausente | 🟡 Alto |
| `ecac_controller.py` | 9 | ❌ Ausente | 🟡 Alto |
| `simples_nacional_controller.py` | 10 | ❌ Ausente | 🟡 Alto |
| `govbr_controller.py` | 12 | ❌ Ausente | 🟢 Médio |
| `cte_controller.py` | 10 | ❌ Ausente | 🟢 Médio |
| `mdfe_controller.py` | 14 | ❌ Ausente | 🟢 Médio |
| `nfce_controller.py` | 9 | ❌ Ausente | 🟡 Alto |
| `receita_federal_controller.py` | 3 | ✅ Completo | ✅ |
| `certificate_controller.py` | 7 | ❌ Ausente | 🟡 Alto |
| `status_controller.py` | 2 | ✅ Completo | ✅ |
| `jobs_controller.py` | 8 | ❌ Ausente | 🟡 Alto |
| `dashboard_controller.py` | 6 | ❌ Ausente | 🟢 Médio |
| `extraction_controller.py` | 10 | ❌ Ausente | 🟢 Médio |

**TOTAL:** 209 endpoints

---

## 🎯 GAPS IDENTIFICADOS

### 1. Service Layer Frontend
**Arquivo:** `/opt/conecta-pro/frontend/src/lib/services/diarist-fiscal.ts`
- ✅ 10 métodos implementados (diaristas)
- ❌ Service dedicado para integrações governamentais: **AUSENTE**
- ❌ Tipos TypeScript: **MANUAIS**

### 2. Hooks React Query
**Diretório:** `/opt/conecta-pro/frontend/src/hooks/`
- ❌ `useGovernment.ts`: **AUSENTE**
- ❌ `useNFSe.ts`: **AUSENTE**
- ❌ `useESocial.ts`: **AUSENTE**
- ❌ `useSEFAZ.ts`: **AUSENTE**
- ❌ `useFGTS.ts`: **AUSENTE**
- ❌ `useSPED.ts`: **AUSENTE**

### 3. Componentes UI
**Diretório:** `/opt/conecta-pro/frontend/src/components/`
- ❌ Componentes de integrações: **AUSENTES**

### 4. Página
**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/fiscal/page.tsx`
```typescript
// ESTADO ATUAL: ComingSoon placeholder
export default function FiscalPage() {
  return <ComingSoon title="Fiscal" />;
}
```
- ❌ Dashboard de integrações: **AUSENTE**
- ❌ Monitoramento de sync: **AUSENTE**
- ❌ Status de conectividade: **AUSENTE**

---

## 🚀 ROADMAP DE IMPLEMENTAÇÃO (40h / 1 semana)

### FASE 1: ANÁLISE E SETUP (4h)

#### 1.1 Baixar OpenAPI Spec Completo (30min)
```bash
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json
```

**Validação:**
- ✅ Arquivo baixado (>2MB)
- ✅ 209 endpoints de governo presentes

#### 1.2 Criar Script de Extração (1h)
```bash
cd /opt/conecta-pro/docs/expansao-orval-28-01-2026
```

**Arquivo:** `extract-government-spec.py`

```python
#!/usr/bin/env python3
"""
Extrai apenas endpoints do módulo Government Integrations.
Filtro: /api/v1/government/
"""

import json
import sys
from pathlib import Path

def extract_government_spec(input_file, output_file):
    with open(input_file, 'r') as f:
        full_spec = json.load(f)

    # Filtrar paths
    gov_paths = {
        path: data
        for path, data in full_spec["paths"].items()
        if "/api/v1/government/" in path
    }

    # Coletar schemas referenciados
    # ... (mesma lógica do GED)

    print(f"✅ Endpoints extraídos: {len(gov_paths)}")

if __name__ == "__main__":
    extract_government_spec(
        "/tmp/openapi-conecta-pro.json",
        "/tmp/openapi-government.json"
    )
```

**Entregável:** `openapi-government.json` (~400KB)

#### 1.3 Configurar Orval (1h)
**Arquivo:** `orval.config.government.ts`

```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  government: {
    input: './openapi-government.json',
    output: {
      target: './src/types/generated/government/index.ts',
      client: 'axios',
      mode: 'tags-split',
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'api',
        },
      },
    },
  },
});
```

#### 1.4 Gerar Tipos (30min)
```bash
cd /opt/conecta-pro/frontend
npm install -D orval
npm run orval:government
```

**Resultado esperado:**
```
src/types/generated/government/
├── nfse-manaus.ts          # 15 tipos
├── nfse-nacional.ts        # 20 tipos
├── esocial.ts              # 25 tipos
├── sefaz.ts                # 18 tipos
├── sped-fiscal.ts          # 22 tipos
├── sped-contabil.ts        # 20 tipos
├── fgts-digital.ts         # 15 tipos
├── fgts-inss.ts            # 10 tipos
├── efd-reinf.ts            # 12 tipos
├── dctfweb.ts              # 14 tipos
├── simples-nacional.ts     # 12 tipos
├── ecac.ts                 # 10 tipos
├── cte.ts                  # 16 tipos
├── mdfe.ts                 # 18 tipos
├── nfce.ts                 # 12 tipos
├── govbr.ts                # 15 tipos
├── certificate.ts          # 8 tipos
├── sync.ts                 # 20 tipos
├── jobs.ts                 # 10 tipos
├── dashboard.ts            # 8 tipos
├── extraction.ts           # 12 tipos
├── receita-federal.ts      # 8 tipos
├── status.ts               # 5 tipos
└── common.ts               # Tipos compartilhados
```

**Entregável:** ~312 tipos TypeScript gerados

**Checkpoint Fase 1:**
- [ ] OpenAPI spec extraído
- [ ] Orval configurado
- [ ] Tipos gerados sem erros
- [ ] `npm run types:check` passa

---

### FASE 2: SERVICE LAYER (12h)

#### 2.1 Criar Service Principal (4h)

**Arquivo:** `/opt/conecta-pro/frontend/src/lib/services/government.ts`

```typescript
/**
 * Service para API de Integrações Governamentais
 * Cobertura completa: 209 endpoints
 */

import { api } from '../api';

// Importar TODOS os tipos gerados
import type {
  // NFS-e Manaus
  EmitirNFSeRequest,
  EmitirNFSeResponse,
  ConsultarNFSeResponse,
  CancelarNFSeRequest,
  // NFS-e Nacional
  NFSeNacionalRequest,
  NFSeNacionalResponse,
  // eSocial
  ESocialEventRequest,
  ESocialEventResponse,
  // SEFAZ
  NFERequest,
  NFEResponse,
  // ... (importar TODOS os 312 tipos)
} from '@/types/generated/government';

const BASE_URL = '/api/v1/government';

// =============================================================================
// NFS-e MANAUS (8 endpoints)
// =============================================================================

export const nfseManausService = {
  // POST /nfse-manaus/emitir
  async emitir(data: EmitirNFSeRequest): Promise<EmitirNFSeResponse> {
    const response = await api.post(`${BASE_URL}/nfse-manaus/emitir`, data);
    return response.data;
  },

  // GET /nfse-manaus/consultar/{numero}
  async consultar(numero: string): Promise<ConsultarNFSeResponse> {
    const response = await api.get(`${BASE_URL}/nfse-manaus/consultar/${numero}`);
    return response.data;
  },

  // POST /nfse-manaus/cancelar
  async cancelar(data: CancelarNFSeRequest): Promise<void> {
    await api.post(`${BASE_URL}/nfse-manaus/cancelar`, data);
  },

  // POST /nfse-manaus/substituir
  async substituir(data: SubstituirNFSeRequest): Promise<void> {
    await api.post(`${BASE_URL}/nfse-manaus/substituir`, data);
  },

  // GET /nfse-manaus/validar-conexao
  async validarConexao(): Promise<ValidarConexaoResponse> {
    const response = await api.get(`${BASE_URL}/nfse-manaus/validar-conexao`);
    return response.data;
  },

  // POST /nfse-manaus/lote
  async enviarLote(data: LoteNFSeRequest): Promise<LoteNFSeResponse> {
    const response = await api.post(`${BASE_URL}/nfse-manaus/lote`, data);
    return response.data;
  },

  // GET /nfse-manaus/lote/{numero}
  async consultarLote(numero: string): Promise<LoteNFSeResponse> {
    const response = await api.get(`${BASE_URL}/nfse-manaus/lote/${numero}`);
    return response.data;
  },

  // GET /nfse-manaus/prefeituras
  async listarPrefeituras(): Promise<PrefeituraInfo[]> {
    const response = await api.get(`${BASE_URL}/nfse-manaus/prefeituras`);
    return response.data;
  },
};

// =============================================================================
// NFS-e NACIONAL (12 endpoints)
// =============================================================================

export const nfseNacionalService = {
  // POST /nfse-nacional/emitir
  async emitir(data: NFSeNacionalRequest): Promise<NFSeNacionalResponse> {
    const response = await api.post(`${BASE_URL}/nfse-nacional/emitir`, data);
    return response.data;
  },

  // GET /nfse-nacional/consultar/{numero}
  async consultar(numero: string): Promise<NFSeNacionalResponse> {
    const response = await api.get(`${BASE_URL}/nfse-nacional/consultar/${numero}`);
    return response.data;
  },

  // POST /nfse-nacional/cancelar
  async cancelar(data: CancelarNFSeNacionalRequest): Promise<void> {
    await api.post(`${BASE_URL}/nfse-nacional/cancelar`, data);
  },

  // GET /nfse-nacional/validar-conexao
  async validarConexao(): Promise<ValidarConexaoResponse> {
    const response = await api.get(`${BASE_URL}/nfse-nacional/validar-conexao`);
    return response.data;
  },

  // POST /nfse-nacional/lote
  async enviarLote(data: LoteNFSeNacionalRequest): Promise<LoteResponse> {
    const response = await api.post(`${BASE_URL}/nfse-nacional/lote`, data);
    return response.data;
  },

  // ... (mais 7 métodos)
};

// =============================================================================
// eSocial (3 endpoints)
// =============================================================================

export const esocialService = {
  // POST /esocial/evento
  async enviarEvento(data: ESocialEventRequest): Promise<ESocialEventResponse> {
    const response = await api.post(`${BASE_URL}/esocial/evento`, data);
    return response.data;
  },

  // GET /esocial/consultar/{protocolo}
  async consultarStatus(protocolo: string): Promise<ESocialStatusResponse> {
    const response = await api.get(`${BASE_URL}/esocial/consultar/${protocolo}`);
    return response.data;
  },

  // GET /esocial/eventos-suportados
  async listarEventosSuportados(): Promise<EventoESocial[]> {
    const response = await api.get(`${BASE_URL}/esocial/eventos-suportados`);
    return response.data;
  },
};

// =============================================================================
// SEFAZ (2 endpoints)
// =============================================================================

export const sefazService = {
  // POST /sefaz/nfe/emitir
  async emitirNFe(data: NFERequest): Promise<NFEResponse> {
    const response = await api.post(`${BASE_URL}/sefaz/nfe/emitir`, data);
    return response.data;
  },

  // GET /sefaz/nfe/consultar/{chave_acesso}
  async consultarNFe(chaveAcesso: string): Promise<NFEResponse> {
    const response = await api.get(`${BASE_URL}/sefaz/nfe/consultar/${chaveAcesso}`);
    return response.data;
  },
};

// =============================================================================
// SEFAZ-AM (8 endpoints)
// =============================================================================

export const sefazAmService = {
  // ... 8 métodos
};

// =============================================================================
// SPED FISCAL (13 endpoints)
// =============================================================================

export const spedFiscalService = {
  // ... 13 métodos
};

// =============================================================================
// SPED CONTÁBIL (13 endpoints)
// =============================================================================

export const spedContabilService = {
  // ... 13 métodos
};

// =============================================================================
// FGTS DIGITAL (11 endpoints)
// =============================================================================

export const fgtsDigitalService = {
  // ... 11 métodos
};

// =============================================================================
// FGTS/INSS (3 endpoints)
// =============================================================================

export const fgtsInssService = {
  // ... 3 métodos
};

// =============================================================================
// EFD-REINF (9 endpoints)
// =============================================================================

export const efdReinfService = {
  // ... 9 métodos
};

// =============================================================================
// DCTFWeb (11 endpoints)
// =============================================================================

export const dctfWebService = {
  // ... 11 métodos
};

// =============================================================================
// SIMPLES NACIONAL (10 endpoints)
// =============================================================================

export const simplesNacionalService = {
  // ... 10 métodos
};

// =============================================================================
// e-CAC (9 endpoints)
// =============================================================================

export const ecacService = {
  // ... 9 métodos
};

// =============================================================================
// CT-e (10 endpoints)
// =============================================================================

export const cteService = {
  // ... 10 métodos
};

// =============================================================================
// MDF-e (14 endpoints)
// =============================================================================

export const mdfeService = {
  // ... 14 métodos
};

// =============================================================================
// NFC-e (9 endpoints)
// =============================================================================

export const nfceService = {
  // ... 9 métodos
};

// =============================================================================
// GOV.BR (12 endpoints)
// =============================================================================

export const govbrService = {
  // ... 12 métodos
};

// =============================================================================
// CERTIFICADO DIGITAL (7 endpoints)
// =============================================================================

export const certificateService = {
  // ... 7 métodos
};

// =============================================================================
// SINCRONIZAÇÃO (16 endpoints)
// =============================================================================

export const syncService = {
  // ... 16 métodos
};

// =============================================================================
// JOBS (8 endpoints)
// =============================================================================

export const jobsService = {
  // ... 8 métodos
};

// =============================================================================
// DASHBOARD (6 endpoints)
// =============================================================================

export const dashboardService = {
  // ... 6 métodos
};

// =============================================================================
// EXTRAÇÃO (10 endpoints)
// =============================================================================

export const extractionService = {
  // ... 10 métodos
};

// =============================================================================
// RECEITA FEDERAL (3 endpoints)
// =============================================================================

export const receitaFederalService = {
  // ... 3 métodos
};

// =============================================================================
// STATUS (2 endpoints)
// =============================================================================

export const statusService = {
  // ... 2 métodos
};

// Service agregado
export const governmentService = {
  nfseManaus: nfseManausService,
  nfseNacional: nfseNacionalService,
  esocial: esocialService,
  sefaz: sefazService,
  sefazAm: sefazAmService,
  spedFiscal: spedFiscalService,
  spedContabil: spedContabilService,
  fgtsDigital: fgtsDigitalService,
  fgtsInss: fgtsInssService,
  efdReinf: efdReinfService,
  dctfWeb: dctfWebService,
  simplesNacional: simplesNacionalService,
  ecac: ecacService,
  cte: cteService,
  mdfe: mdfeService,
  nfce: nfceService,
  govbr: govbrService,
  certificate: certificateService,
  sync: syncService,
  jobs: jobsService,
  dashboard: dashboardService,
  extraction: extractionService,
  receitaFederal: receitaFederalService,
  status: statusService,
};
```

**Checklist Implementação:**
- [ ] 209 métodos implementados
- [ ] Tipos gerados do Orval
- [ ] Documentação inline
- [ ] Tratamento de erros

#### 2.2 Validar Build (1h)
```bash
npm run types:check
npm run build
```

**Entregável:** Zero erros TypeScript

**Checkpoint Fase 2:**
- [ ] Service completo (209 métodos)
- [ ] Tipos sincronizados
- [ ] Build sem erros

---

### FASE 3: HOOKS REACT QUERY (8h)

#### 3.1 Criar Hooks por Integração (6h)

**Arquivo:** `/opt/conecta-pro/frontend/src/hooks/useGovernment.ts`

```typescript
/**
 * Hooks React Query para integrações governamentais
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { governmentService } from '@/lib/services/government';
import type {
  EmitirNFSeRequest,
  ESocialEventRequest,
  NFERequest,
  // ... todos os tipos
} from '@/types/generated/government';

// =============================================================================
// NFS-e MANAUS
// =============================================================================

export function useNFSeManaus() {
  const queryClient = useQueryClient();

  const emitir = useMutation({
    mutationFn: (data: EmitirNFSeRequest) =>
      governmentService.nfseManaus.emitir(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['nfse-manaus']);
    },
  });

  const consultar = useQuery({
    queryKey: ['nfse-manaus', numero],
    queryFn: () => governmentService.nfseManaus.consultar(numero),
    enabled: !!numero,
  });

  const cancelar = useMutation({
    mutationFn: governmentService.nfseManaus.cancelar,
    onSuccess: () => {
      queryClient.invalidateQueries(['nfse-manaus']);
    },
  });

  return {
    emitir,
    consultar,
    cancelar,
    // ... outros métodos
  };
}

// =============================================================================
// eSocial
// =============================================================================

export function useESocial() {
  const enviarEvento = useMutation({
    mutationFn: (data: ESocialEventRequest) =>
      governmentService.esocial.enviarEvento(data),
  });

  const consultarStatus = useQuery({
    queryKey: ['esocial-status', protocolo],
    queryFn: () => governmentService.esocial.consultarStatus(protocolo),
    enabled: !!protocolo,
    refetchInterval: 5000, // Polling a cada 5s
  });

  return {
    enviarEvento,
    consultarStatus,
  };
}

// =============================================================================
// SEFAZ
// =============================================================================

export function useSEFAZ() {
  const emitirNFe = useMutation({
    mutationFn: (data: NFERequest) =>
      governmentService.sefaz.emitirNFe(data),
  });

  const consultarNFe = useQuery({
    queryKey: ['nfe', chaveAcesso],
    queryFn: () => governmentService.sefaz.consultarNFe(chaveAcesso),
    enabled: !!chaveAcesso,
  });

  return {
    emitirNFe,
    consultarNFe,
  };
}

// =============================================================================
// SINCRONIZAÇÃO
// =============================================================================

export function useSync() {
  const queryClient = useQueryClient();

  const executarSync = useMutation({
    mutationFn: governmentService.sync.executar,
    onSuccess: () => {
      queryClient.invalidateQueries(['sync-status']);
    },
  });

  const statusSync = useQuery({
    queryKey: ['sync-status', cnpj],
    queryFn: () => governmentService.sync.status(cnpj),
    enabled: !!cnpj,
    refetchInterval: 10000, // Polling a cada 10s
  });

  return {
    executarSync,
    statusSync,
  };
}

// ... (criar hooks para TODOS os 24 controllers)
```

**Entregável:** Hooks completos para 24 integrações

#### 3.2 Hooks de Dashboard (2h)

**Arquivo:** `/opt/conecta-pro/frontend/src/hooks/useGovernmentDashboard.ts`

```typescript
/**
 * Hook consolidado para dashboard de integrações governamentais
 */

export function useGovernmentDashboard(cnpj: string) {
  // Status geral
  const { data: status } = useQuery({
    queryKey: ['government-status', cnpj],
    queryFn: () => governmentService.status.geral(cnpj),
    refetchInterval: 30000,
  });

  // Jobs ativos
  const { data: jobs } = useQuery({
    queryKey: ['government-jobs', cnpj],
    queryFn: () => governmentService.jobs.ativos(cnpj),
    refetchInterval: 10000,
  });

  // Dashboard metrics
  const { data: metrics } = useQuery({
    queryKey: ['government-dashboard', cnpj],
    queryFn: () => governmentService.dashboard.metrics(cnpj),
  });

  return {
    status,
    jobs,
    metrics,
    isLoading: !status || !jobs || !metrics,
  };
}
```

**Checkpoint Fase 3:**
- [ ] Hooks para 24 integrações
- [ ] Hook de dashboard consolidado
- [ ] Polling configurado
- [ ] Cache otimizado

---

### FASE 4: COMPONENTES UI (8h)

#### 4.1 Dashboard de Integrações (4h)

**Arquivo:** `/opt/conecta-pro/frontend/src/components/government/GovIntegrationsDashboard.tsx`

```typescript
'use client';

import { useGovernmentDashboard } from '@/hooks/useGovernment';

export function GovIntegrationsDashboard() {
  const { status, jobs, metrics } = useGovernmentDashboard('12345678000190');

  return (
    <div className="space-y-6">
      {/* Status Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatusCard
          title="NFS-e"
          status={status?.nfse}
          icon={<FileText />}
        />
        <StatusCard
          title="eSocial"
          status={status?.esocial}
          icon={<Users />}
        />
        <StatusCard
          title="SEFAZ"
          status={status?.sefaz}
          icon={<Receipt />}
        />
        <StatusCard
          title="SPED"
          status={status?.sped}
          icon={<Database />}
        />
      </div>

      {/* Jobs Ativos */}
      <Card>
        <CardHeader>
          <CardTitle>Sincronizações Ativas</CardTitle>
        </CardHeader>
        <CardContent>
          <JobsList jobs={jobs} />
        </CardContent>
      </Card>

      {/* Métricas */}
      <MetricsGrid metrics={metrics} />
    </div>
  );
}
```

#### 4.2 Componentes de Integração (4h)

Componentes para cada integração:
- `NFSeManausForm.tsx`
- `ESocialEventForm.tsx`
- `SEFAZNFeForm.tsx`
- `SyncScheduler.tsx`
- `IntegrationLogs.tsx`
- `ConnectivityStatus.tsx`

**Checkpoint Fase 4:**
- [ ] Dashboard consolidado
- [ ] 6+ componentes de integração
- [ ] Logs em tempo real
- [ ] Status de conectividade

---

### FASE 5: PÁGINA (3h)

#### 5.1 Refatorar Página Fiscal (3h)

**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/fiscal/page.tsx`

```typescript
'use client';

import { GovIntegrationsDashboard } from '@/components/government/GovIntegrationsDashboard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function FiscalPage() {
  return (
    <div className="container py-6">
      <h1 className="text-3xl font-bold mb-6">Integrações Governamentais</h1>

      <Tabs defaultValue="dashboard">
        <TabsList>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="nfse">NFS-e</TabsTrigger>
          <TabsTrigger value="esocial">eSocial</TabsTrigger>
          <TabsTrigger value="sefaz">SEFAZ</TabsTrigger>
          <TabsTrigger value="sped">SPED</TabsTrigger>
          <TabsTrigger value="sync">Sincronização</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard">
          <GovIntegrationsDashboard />
        </TabsContent>

        <TabsContent value="nfse">
          <NFSeManausManager />
        </TabsContent>

        {/* ... outras tabs */}
      </Tabs>
    </div>
  );
}
```

**Checkpoint Fase 5:**
- [ ] Página completa
- [ ] Navegação por tabs
- [ ] Dashboard visível
- [ ] Todas integrações acessíveis

---

### FASE 6: TESTES (4h)

#### 6.1 Testes de Service (2h)

```typescript
describe('governmentService', () => {
  describe('nfseManaus', () => {
    it('deve emitir NFS-e', async () => {
      const data = { /* ... */ };
      const result = await governmentService.nfseManaus.emitir(data);
      expect(result.numero_nfse).toBeDefined();
    });
  });

  describe('esocial', () => {
    it('deve enviar evento', async () => {
      const data = { /* ... */ };
      const result = await governmentService.esocial.enviarEvento(data);
      expect(result.protocolo).toBeDefined();
    });
  });

  // ... testes para todos os 209 endpoints
});
```

#### 6.2 Testes de Hooks (1h)

```typescript
describe('useGovernment', () => {
  it('useNFSeManaus deve emitir nota', async () => {
    const { result } = renderHook(() => useNFSeManaus());
    await act(async () => {
      await result.current.emitir.mutateAsync(mockData);
    });
    expect(result.current.emitir.isSuccess).toBe(true);
  });
});
```

#### 6.3 Testes de Integração (1h)

**Checkpoint Fase 6:**
- [ ] Testes de service
- [ ] Testes de hooks
- [ ] Testes de integração
- [ ] Cobertura >80%

---

### FASE 7: DOCUMENTAÇÃO (2h)

#### 7.1 README (1h)

**Arquivo:** `/opt/conecta-pro/frontend/src/lib/services/government/README.md`

```markdown
# Government Integrations Service

Cobertura completa: 209 endpoints

## Integrações Disponíveis

### NFS-e
- **Manaus:** 8 endpoints
- **Nacional:** 12 endpoints

### eSocial
- 3 endpoints
- Eventos suportados: S-1000, S-2200, S-2299, etc.

### SEFAZ
- NFe: 2 endpoints
- NFC-e: 9 endpoints
- CT-e: 10 endpoints
- MDF-e: 14 endpoints

### SPED
- Fiscal: 13 endpoints
- Contábil: 13 endpoints

### FGTS/INSS
- Digital: 11 endpoints
- Cálculos: 3 endpoints

### Outros
- EFD-Reinf: 9 endpoints
- DCTFWeb: 11 endpoints
- Simples Nacional: 10 endpoints
- e-CAC: 9 endpoints
- GOV.BR: 12 endpoints

## Uso

\`\`\`typescript
import { governmentService } from '@/lib/services/government';

// Emitir NFS-e
const nfse = await governmentService.nfseManaus.emitir({
  tomador: { /* ... */ },
  servico: { /* ... */ },
});

// Enviar evento eSocial
const evento = await governmentService.esocial.enviarEvento({
  tipo_evento: 'S-2200',
  dados: { /* ... */ },
});
\`\`\`
```

#### 7.2 Guia de Configuração (1h)

**Arquivo:** `CONFIGURACAO-INTEGRACAO.md`

Guia detalhado para configurar cada órgão:
- Certificado digital
- Credenciais GOV.BR
- Inscrições municipais
- Alíquotas

**Checkpoint Fase 7:**
- [ ] README completo
- [ ] Guia de configuração
- [ ] Exemplos de uso
- [ ] Troubleshooting

---

## 📊 MÉTRICAS DE SUCESSO

```
╔═══════════════════════════════════════════════════════════╗
║  MÓDULO GOVERNMENT INTEGRATIONS - APÓS IMPLEMENTAÇÃO      ║
╠═══════════════════════════════════════════════════════════╣
║  ✅ Cobertura:                209/209 (100%)              ║
║  ✅ Tipos sincronizados:      AUTOMÁTICO                  ║
║  ✅ Service completo:          24 sub-services            ║
║  ✅ Hooks React Query:         24 hooks                   ║
║  ✅ Dashboard:                 IMPLEMENTADO               ║
║  ✅ Monitoramento:             TEMPO REAL                 ║
║  ✅ Testes:                    >80% COBERTURA             ║
║  ✅ Documentação:              COMPLETA                   ║
║                                                           ║
║  🎯 COMPLIANCE GOVERNAMENTAL GARANTIDO                    ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🚨 PONTOS CRÍTICOS

### 1. Certificado Digital A1
- ⚠️ Obrigatório para NFS-e, NF-e, CT-e, MDF-e
- ⚠️ Validação de expiração
- ⚠️ Renovação automática

### 2. Credenciais GOV.BR
- ⚠️ Obrigatório para eSocial, FGTS Digital
- ⚠️ Token de acesso tem expiração
- ⚠️ Refresh automático

### 3. Ambientes (Produção/Homologação)
- ⚠️ URLs diferentes por ambiente
- ⚠️ Certificados diferentes
- ⚠️ Toggle no frontend

### 4. Rate Limiting
- ⚠️ Receita Federal: 20 req/min
- ⚠️ eSocial: 100 eventos/hora
- ⚠️ Implementar retry com backoff

### 5. Monitoramento
- ⚠️ Jobs de sincronização falhando
- ⚠️ Certificados expirando
- ⚠️ Conectividade com órgãos

---

## 📅 CRONOGRAMA

| Fase | Duração | Status |
|------|---------|--------|
| Análise e Setup | 4h | 🔄 |
| Service Layer | 12h | ⏳ |
| Hooks React Query | 8h | ⏳ |
| Componentes UI | 8h | ⏳ |
| Página | 3h | ⏳ |
| Testes | 4h | ⏳ |
| Documentação | 2h | ⏳ |
| **TOTAL** | **40h** | **~1 semana** |

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Ler este documento
2. ⏳ Executar Fase 1 (Setup)
3. ⏳ Gerar tipos com Orval
4. ⏳ Implementar service completo
5. ⏳ Criar hooks React Query
6. ⏳ Desenvolver componentes
7. ⏳ Refatorar página
8. ⏳ Testes e documentação

---

**Criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
**Status:** 🚀 PRONTO PARA EXECUÇÃO
