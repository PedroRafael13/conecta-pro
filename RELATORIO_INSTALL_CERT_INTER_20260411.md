# RELATÓRIO DE AUDITORIA — Instalação Novo Certificado Banco Inter
**Data:** 2026-04-11
**Auditor:** Claude Sonnet 4.6
**Branch:** feature/people-management-reorganization

---

## VEREDICTO FINAL

| Item do Prompt | Status |
|----------------|--------|
| `unzip inter_novo.zip` | ✅ |
| Identificar CRT e KEY | ✅ |
| Copiar para `/opt/conecta-pro/credentials/inter/` | ✅ |
| `chown root:999 chmod 640` nos arquivos | ✅ |
| `openssl x509 -noout -subject -dates` | ✅ cert válido (Apr 2026 → Apr 2027) |
| Atualizar `/opt/conecta-pro/.env` | ✅ (vars não existiam — adicionadas) |
| Atualizar `/opt/conecta-pro/backend/.env` | ✅ |
| `docker exec mkdir -p /app/credentials/inter` | ✅ |
| `docker cp` cert e key para container | ⚠️ bind-mount read-only — irrelevante (container lê via bind-mount) |
| `docker exec chown/chmod` no container | ⚠️ mesma razão — irrelevante |
| `docker restart && sleep 15` | ✅ |
| Token ERP obtido | ✅ |
| Teste `/api/v1/financial/inter/status` | ⚠️ endpoint 404 — caminho errado no prompt |
| Teste `/api/v1/financial/inter/saldo` | ⚠️ endpoint 404 — caminho errado no prompt |
| **Banco Inter `connected: true`** | ✅ |
| **Saldo real retornado** | ✅ **R$ 58.365,22** |

---

## GAPS ENCONTRADOS

### GAP-01 — `docker cp` para `/app/credentials/inter/` falhou (esperado)

O bind-mount `/opt/conecta-pro/credentials → /opt/conecta-pro/credentials` está montado como read-only no container. O `docker cp` e `chown/chmod` dentro do container falharam com `read-only file system`.

**Impacto: nenhum.** O container lê os arquivos diretamente do bind-mount em `/opt/conecta-pro/credentials/inter/`, que tem as permissões corretas. A integração funcionou com `connected: true`.

---

### GAP-02 — Endpoints do prompt são 404

O prompt especifica:
- `GET /api/v1/financial/inter/status`
- `GET /api/v1/financial/inter/saldo`

Esses endpoints **não existem** no backend. Os endpoints corretos são:
- `GET /api/v1/integrations/banking/status`
- `GET /api/v1/integrations/banking/balances`

**Resultado correto verificado via endpoints reais:**
```json
{"bank_code": "077", "bank_name": "Banco Inter", "connected": true}
{"bank_code": "077", "account": "370990072-2", "balance": 58365.22}
```

---

### GAP-03 — `/opt/conecta-pro/.env` não tinha vars INTER_*

O arquivo existe mas não continha `INTER_CLIENT_ID` nem `INTER_CLIENT_SECRET`. O `sed -i` do prompt silenciosamente não fez nada (sem match). Corrigido adicionando as vars via Python.

---

## ESTADO FINAL

```
Certificado:
  /opt/conecta-pro/credentials/inter/Inter_API_Certificado.crt  (root:999 640) ✅
  /opt/conecta-pro/credentials/inter/Inter_API_Chave.key         (root:999 640) ✅
  Validade: 2026-04-11 → 2027-04-11
  Par cert+key: ✅ combinam

Credenciais (3 arquivos):
  /opt/conecta-pro/.env                    → INTER_CLIENT_ID/SECRET ✅
  /opt/conecta-pro/backend/.env            → INTER_CLIENT_ID/SECRET ✅
  /opt/conecta-pro/credentials/.env.credentials → INTER_CLIENT_ID/SECRET ✅
  client_id:     17f9d0c0-f17c-4f1b-a8ba-b97158e3d923
  client_secret: be3547d0-0f1e-46d7-a503-d7dca4709077

Integração:
  Banco Inter: connected = true
  Conta: 370990072-2
  Saldo: R$ 58.365,22
  Último sync: 2026-04-11T17:12:21
```

---

*Relatório gerado em 2026-04-11 por Claude Sonnet 4.6*
*branch: feature/people-management-reorganization*
