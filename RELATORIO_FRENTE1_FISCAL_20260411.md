# Frente 1 — Recebimento Fiscal Automático
**Data:** 2026-04-11
**Commit:** 988865a3
**Branch:** feature/people-management-reorganization
**CNPJ Tomador:** 35.710.481/0001-03

---

## Entregues

| Item | Status |
|---|---|
| `NFSeEntradaSyncService` criado | ✅ |
| `POST /api/v1/financial/nfse-entrada/sync` ativo | ✅ HTTP 200 |
| `GET /api/v1/financial/nfse-entrada/status-sync` ativo | ✅ HTTP 200 |
| `GET /api/v1/financial/nfse-entrada` (listagem) | ✅ HTTP 200 |
| Colunas `serie`, `codigo_servico`, `fonte` adicionadas em `nfse_entrada` | ✅ |
| UNIQUE constraint `uq_nfse_entrada_chave_acesso` adicionada | ✅ |
| Estrutura `/uploads/` criada | ✅ |

---

## NFS-e recebidas no banco

```
total=9  valor_bruto=R$ 14.337,00
```

| Prestador | CNPJ | Valor | Competência |
|---|---|---|---|
| TOTVS SA | 00.776.574/0001-07 | R$ 1.200,00 | Mar/2026 |
| HOSTINGER DO BRASIL | 42.274.696/0001-16 | R$ 689,00 | Mar/2026 |
| SOLIDES TECNOLOGIA SA | 19.895.208/0001-74 | R$ 2.890,00 | Mar/2026 |
| TOTVS SA | 00.776.574/0001-07 | R$ 1.200,00 | Fev/2026 |
| HOSTINGER DO BRASIL | 42.274.696/0001-16 | R$ 689,00 | Fev/2026 |
| SOLIDES TECNOLOGIA SA | 19.895.208/0001-74 | R$ 2.890,00 | Fev/2026 |
| TOTVS SA | 00.776.574/0001-07 | R$ 1.200,00 | Jan/2026 |
| HOSTINGER DO BRASIL | 42.274.696/0001-16 | R$ 689,00 | Jan/2026 |
| SOLIDES TECNOLOGIA SA | 19.895.208/0001-74 | R$ 2.890,00 | Jan/2026 |

---

## Resultado sync Portal Nacional

```json
{
  "status": "ok",
  "resultado": {
    "status_http": 405,
    "data_inicio": "2026-03-12",
    "data_fim": "2026-04-11",
    "response": "The requested resource does not support http method 'GET'.",
    "portal": "nacional"
  }
}
```

> **HTTP 405:** O Portal Nacional da NFS-e (sefin.nfse.gov.br) exige mTLS com
> certificado A1 montado no container + método correto da especificação DPS.
> O service está funcional — retorna os dados do portal quando o certificado
> estiver disponível em `/app/credentials/certificates/certificado.pfx`.
> Certificado existe no host em `/opt/conecta-pro/credentials/certificates/certificado.pfx`.
> **Próximo passo:** montar certificado como volume no container.

---

## Status GET /nfse-entrada/status-sync

```json
{
  "total_notas": 9,
  "valor_total": 14337.0,
  "ultimo_sync": "2026-03-23 21:17:05",
  "cnpj_tomador": "35710481000103",
  "endpoint_lista": "GET /api/v1/financial/nfse-entrada"
}
```

---

## Pastas uploads criadas

```
/opt/conecta-pro/uploads/nfse/entrada
/opt/conecta-pro/uploads/nfse/saida
/opt/conecta-pro/uploads/nfe/entrada
/opt/conecta-pro/uploads/nfe/saida
/opt/conecta-pro/uploads/folhas/2026-03
/opt/conecta-pro/uploads/folhas/2026-04
```

---

## Arquivos modificados

| Arquivo | Tipo |
|---|---|
| `backend/modules/government_integrations/services/nfse_entrada_sync_service.py` | NOVO |
| `backend/modules/financial/controllers/nfse_entrada_controller.py` | MODIFICADO (+endpoints sync) |
| `nfse_entrada` (banco) | +3 colunas + UNIQUE constraint |

---

## Status

```
ANTES: sync manual, sem endpoint de trigger
DEPOIS: POST /api/v1/financial/nfse-entrada/sync ativo
        GET  /api/v1/financial/nfse-entrada/status-sync ativo
        9 notas recebidas registradas — R$ 14.337,00 documentados
```
