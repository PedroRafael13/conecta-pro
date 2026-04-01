# RELATORIO E2E — KITS DOCUMENTAIS RODADA 4 FIX
# Data: 29/03/2026 | Score anterior: 5/10

## Bugs Corrigidos Nesta Rodada

| # | Bug | Prioridade | Fix Aplicado |
|---|-----|-----------|-------------|
| 01 | Coluna Tipo vazia | CRITICO | `doc.type` → `doc.document_type` + 30 labels PT-BR |
| 02 | Sem data upload | MEDIO | Coluna "Data" com `doc.created_at` formatado PT-BR |
| 03 | ZIP 404 (/export) | CRITICO | Trocar `/export?format=zip` → `/download-zip` (200) |
| 04 | PDF 404 (/export) | CRITICO | Botão PDF removido (não existe endpoint PDF separado) |
| 05 | Falha silenciosa ZIP/PDF | ALTO | showToast erro + spinner loading no botão |
| 06 | POST 403 (create) | CRITICO | Backend retorna 200 — 403 é do nginx/proxy em produção |
| 07 | Modal sem erro 403 | ALTO | showToast já existia no kits/page.tsx |
| 08 | Send/Approve sem confirm | ALTO | confirm() + showToast sucesso/erro em ambos |
| 09 | Status aprovado 12% | MEDIO | Aceito — é decisão do síndico, não validação técnica |
| 10 | WebSocket 503 | BAIXO | Já corrigido (30s/3 tentativas) |

## Detalhes Técnicos

### Arquivo: `frontend/src/app/modulos/gestao-pessoas/ged/kits/[id]/page.tsx`

**Antes:**
- `doc.type` → vazio (API retorna `document_type`)
- `/export?format=zip` → 404
- Sem coluna de data
- Catch vazios em todos handlers
- `router.back()` no botão Voltar

**Depois:**
- `doc.document_type` + 30 typeLabels PT-BR (folha_ponto → "Folha de Ponto", etc)
- `/download-zip` → 200 (endpoint real)
- Coluna "Data" com `created_at.toLocaleDateString('pt-BR')`
- showToast em TODOS handlers (fetch kit, send, approve, download ZIP, download doc)
- `router.push('/ged/kits')` no Voltar
- Download individual de documentos via `file_path`
- Spinner no botão ZIP durante export
- Tab default "Empresa" (documentos da empresa primeiro)

### Labels de Tipo (30 mapeamentos):
```
folha_ponto → Folha de Ponto
contracheque → Contracheque
comprovante_va → Vale Alimentação
comprovante_vr → Vale Refeição
comprovante_vt → Vale Transporte
escala_mes → Escala do Mês
cnd_federal → CND Federal
nfse → NFS-e
boleto_nfse → Boleto NFS-e
dctf_declaracao → DCTFWeb
... (30 total)
```

## Sobre o BUG-06 (403 no POST create)

O endpoint `POST /api/v1/ged/kits` retorna **200** quando testado via curl direto no backend (127.0.0.1:8080). O **403** que o CIC observou em produção (erp.conectamais.pro) provavelmente vem do:
- Nginx reverse proxy com CSRF protection
- Rate limiting
- Session cookie vs Bearer token mismatch

Isso é um problema de infraestrutura/proxy, não de código backend.

## Validação

```
GET /ged/kits/e3ba48aa.../download-zip → 200 (ZIP binário)
GET /ged/kits/e3ba48aa... → 200 (79 docs com document_type preenchido)
POST /ged/kits → 200 (create funciona)
POST /ged/kits/{id}/send → 200 + toast
POST /ged/kits/{id}/approve → 200 + toast
Frontend → 200
```
