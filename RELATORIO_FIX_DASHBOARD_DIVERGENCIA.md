# RELATÓRIO — FIX DIVERGÊNCIA Dashboard vs /certidoes
**Data:** 2026-05-03
**Sessão:** T1
**Branch:** feature/people-management-reorganization
**Commit:** `4536096d`
**Duração:** ~25min (dentro do budget de 1h)

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
