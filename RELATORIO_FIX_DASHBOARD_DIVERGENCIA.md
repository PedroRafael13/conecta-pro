# RELATÓRIO — FIX DIVERGÊNCIA Dashboard vs /certidoes
**Data:** 2026-05-03
**Sessão:** T1
**Branch:** feature/people-management-reorganization
**Commits:** `4536096d` (fix) · `4aee35ce` (docs) · `auditoria` (este)
**Duração:** ~40min (dentro do budget de 1h)

---

## 1. DIAGNÓSTICO

### Fonte antiga (dashboard)

```
GET /api/v1/bidding/certificates   ← módulo licitações
```

Dados retornados:
| Certidão | Validade | Situação |
|----------|----------|----------|
| FGTS | 2026-03-31 | REGULAR |
| Alvará | 2026-02-28 | VENCIDA |
| Cert Digital A1 | 2026-04-01 | VENCIDO |

### Fonte correta (/certidoes — D5.4)

```
GET /api/v1/ged/certidoes   ← ged_certidoes, fonte única da verdade
```

Dados:
| Certidão | Validade | Status |
|----------|----------|--------|
| FGTS | **2026-05-30** | a_vencer |
| Alvará | 2026-02-28 | vencida |
| INSS, Trabalhista, etc | 2026-10-27+ | valida |

### Causa raiz

`dashboardStatsService.fetchCertificateAlerts()` chamava
`/api/v1/bidding/certificates` (tabela separada do módulo de licitações com
dados desatualizados) em vez de `/api/v1/ged/certidoes` (D5.4 — atualizado
pelo CertidoesUpdaterService em 2026-04-30).

**Divergência concreta:** FGTS exibia 31/03 no dashboard e 30/05 em /certidoes.

---

## 2. DIFF RESUMIDO

**Arquivo:** `frontend/src/services/dashboard/dashboardStatsService.ts`

```typescript
// ANTES:
export async function fetchCertificateAlerts(): Promise<CertificateAlert[]> {
  try {
    const { data } = await api.get('/api/v1/bidding/certificates');
    const items = Array.isArray(data) ? data : data.items ?? [];
    return items
      .filter((c: CertificateAlert) => c.dias_para_vencer <= 30 || !c.esta_valida)
      .sort((a, b) => a.dias_para_vencer - b.dias_para_vencer);
  } catch {
    return [];
  }
}

// DEPOIS:
export async function fetchCertificateAlerts(): Promise<CertificateAlert[]> {
  try {
    const { data } = await api.get('/api/v1/ged/certidoes');
    const items: GedCertidao[] = data.certidoes ?? (Array.isArray(data) ? data : []);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return items
      .map((c) => {
        const diasParaVencer = c.expiry_date
          ? Math.round((new Date(c.expiry_date).getTime() - today.getTime()) / 86_400_000)
          : 9999;
        return {
          id: c.id,
          tipo: c.document_type,
          nome: c.name,
          dias_para_vencer: diasParaVencer,
          situacao: c.status,
          esta_valida: c.status === 'valida',
          data_validade: c.expiry_date ?? '',
        };
      })
      .filter((c) => c.situacao !== 'valida' || c.dias_para_vencer <= 30)
      .sort((a, b) => a.dias_para_vencer - b.dias_para_vencer);
  } catch {
    return [];
  }
}
```

**Interface interna adicionada:**
```typescript
interface GedCertidao {
  id: string;
  name: string;
  document_type: string;
  expiry_date: string | null;
  status: 'valida' | 'a_vencer' | 'vencida' | 'sem_validade';
  alerta_ativo: boolean;
}
```

---

## 3. CERTIFICADO DIGITAL A1

**Decisão [A2]:** Certificado Digital A1 (e-CNPJ) existia apenas na tabela
`bidding/certificates` com `tipo=CERTIFICADO_DIGITAL`. NÃO está em `ged_certidoes`
pois é um certificado de máquina (para assinar NFes), não uma certidão empresarial.

**Efeito:** Removido dos alertas do dashboard.

**Backlog:** Se Jordan quiser acompanhar o Cert A1 no dashboard, criar uma
terceira fonte ou adicioná-lo manualmente a `ged_certidoes` com
`document_type='certificado_digital'`.

---

## 4. VALIDAÇÃO CURL

```bash
# Fonte após fix — idêntica ao /certidoes:
GET /api/v1/ged/certidoes

# Alertas exibidos no dashboard (filter: status!=valida OR dias<=30):
dias=-64 | vencida  | Alvará de Funcionamento   | validade=2026-02-28
dias=+27 | a_vencer | Certidão Negativa FGTS    | validade=2026-05-30
Total: 2 alertas
```

**Antes do fix:**
- FGTS: "Vencida desde 31/03" (dado de bidding/certificates, desatualizado)

**Após o fix:**
- FGTS: "Vence em 27 dia(s)" (dado correto de ged_certidoes)
- Dashboard = /certidoes ✅

---

## 5. BUILD_ID

| Build | ID |
|-------|----|
| Anterior | `conecta-pro-1777839027654` |
| **Novo** | **`conecta-pro-1777851782277`** |

---

## 6. BACKLOG / TRADE-OFFS

| Item | Decisão |
|------|---------|
| Cert Digital A1 removido do dashboard | Aceito — escopo diferente (decisão A2) |
| `bidding/certificates` ainda existe | Intocado — módulo de licitações usa-o |
| `ged_certidoes` = fonte única | ✅ Princípio §42.4 mantido |
| Dias calculado client-side | OK — `expiry_date` é string ISO, cálculo é trivial |
| Build serializado | ✅ Não houve builds simultâneos |
| D5.4 (CertidoesUpdaterService) | ✅ Não modificado |
| D5.5 (/certidoes page) | ✅ Não modificado |
| D6/D7 | ✅ Não tocados |

---

## 7. AUDITORIA — 100% DO PROMPT

### Items executados

| Step | Item | Status | Obs |
|------|------|--------|-----|
| 0 | T+0 timestamp + versão + git log | ✅ | — |
| 1.1 | Localizar dashboard page | ✅ | `frontend/src/app/dashboard/page.tsx` |
| 1.2 | grep FGTS/Alvar/Vencida no dashboard | ✅ | — |
| 1.3 | grep Regularizar em components/ + find Alert | ✅ | — |
| 1.4 | Identificar endpoint + @router. searches | ✅ | bidding/certificates encontrado |
| 1.5 | SELECT document_type, name, expiry_date... FROM ged_certidoes | ✅ | FGTS=2026-05-30 confirmado |
| 1.6 | \dt filtrado + SELECT COUNT documentos + \d ged_certidoes | ✅ | documentos e ged_documentos_empresa: NOT EXIST |
| 2 | Decisão [A] + [A2] documentada | ✅ | — |
| 3 | Fix dashboardStatsService.ts | ✅ | — |
| 3 | npm run build (EXIT 0, 286 páginas) | ✅ | — |
| 3 | docker cp .next/standalone/. container:/app/ | ✅ | — |
| 3 | docker cp .next/static/. container:/app/.next/static/ | ✅ | Executado na auditoria (sintaxe corrigida vs nesting bug) |
| 3 | docker restart | ✅ | — |
| 4 | curl /api/v1/ged/certidoes + json.tool | ✅ | — |
| 4 | Smoke test /dashboard HTTP | ✅ | 307 (redirect sem auth — correto) |
| 5 | CONTRACTS_GEDEON.md §51 v1.53 | ✅ | — |
| 5 | git commit + push | ✅ | 3 commits total |
| 5 | Relatório completo (6 seções) | ✅ | — |

### Token via docker exec (método do prompt)

O método `docker exec python3 -c "from core.auth import create_access_token..."` falha
porque o token gerado internamente recebe 401 do FastAPI (não passa pelo middleware
de validação JWT que usa o secret key carregado via env do container). O método
funcional e equivalente é o login endpoint (`POST /api/v1/auth/login`).

### docker cp .next/static — correção aplicada na auditoria

O prompt original diz: `docker cp .next/static conecta-pro-frontend:/app/.next/`
Executado como: `docker cp .next/static/. conecta-pro-frontend:/app/.next/static/`
(sintaxe `/.` evita o nesting bug: se o destino já existe, `docker cp src dest`
cria `dest/src/` ao invés de copiar o conteúdo — bug documentado na sessão anterior)

### CertidoesUpdaterService — atualização em tempo real detectada

Durante a auditoria o serviço D5.4 atualizou o FGTS:
- Antes: expiry_date=2026-05-30, status=a_vencer
- Depois: expiry_date=2026-06-02, status=valida (30 dias)

Isso confirma que a integração está funcionando. O dashboard, agora lendo de
`ged_certidoes`, refletirá automaticamente qualquer atualização futura — mesma
fonte que `/certidoes`. Alinhamento garantido.

---

## 8. CORREÇÃO PÓS-AUDITORIA — Cert A1 + Agregação (decisão [A2] real)

### Gap corrigido

A implementação anterior removeu o Cert Digital A1 do dashboard.
O prompt exige [A2]: "Manter Cert A1 fora de ged_certidoes **e adicionar fonte específica**"
+ "dashboard deve agregar ambas as fontes no mesmo card de Pendências".

### Fix aplicado

`fetchCertificateAlerts` agora faz 2 chamadas paralelas:

```typescript
// Fonte 1: ged_certidoes (certidões empresariais — D5.4)
GET /api/v1/ged/certidoes

// Fonte 2: bidding/certificates (apenas CERTIFICADO_DIGITAL — decisão A2)
GET /api/v1/bidding/certificates → filter(tipo === 'CERTIFICADO_DIGITAL')

// Merge + sort por urgência
[...gedAlerts, ...certDigitalAlerts].sort((a,b) => a.dias_para_vencer - b.dias_para_vencer)
```

### Dashboard após correção completa (3 alertas)

| # | Ícone | dias | Status | Nome | Fonte |
|---|-------|------|--------|------|-------|
| 1 | 🔴 | -65d | vencida | Alvará de Funcionamento | ged_certidoes |
| 2 | 🔴 | -33d | vencida | Certificado Digital A1 - e-CNPJ | bidding/certificates |
| 3 | 🟡 | +29d | a_vencer | Certidão Negativa FGTS | ged_certidoes |

### Build final

`conecta-pro-1777853080585`

### Commits desta sessão

| Hash | Descrição |
|------|-----------|
| `4536096d` | fix(dashboard): endpoint ged/certidoes |
| `4aee35ce` | docs: relatório inicial |
| `40e821cc` | docs: auditoria §7 + docker cp static |
| `este` | fix(dashboard): agregação Cert A1 + auditoria final |
