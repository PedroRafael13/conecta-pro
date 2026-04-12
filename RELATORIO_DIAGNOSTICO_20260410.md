# Relatório de Diagnóstico — Conecta PRO ERP
**Data:** 2026-04-10
**Sessão:** Diagnóstico NFS-e / Holerite PDF / Solides VA
**Executado por:** Claude Code (claude-sonnet-4-6)

---

## Resumo Executivo

| Item | Status | Ação Necessária |
|------|--------|-----------------|
| NFS-e — Consulta/Dashboard | ✅ Funcionando | Nenhuma |
| NFS-e — Emissão (endpoint) | ⚠️ Sem endpoint POST | Implementar |
| Holerite PDF — CRUD | ✅ Endpoint OK | Nenhuma |
| Holerite PDF — Geração PDF | ❌ Sem endpoint `/pdf` | Implementar |
| Solides VA — Credenciais | ✅ Token configurado | Nenhuma |
| Solides VA — Status | ✅ 200 OK | Nenhuma |
| Solides VA — Benefícios CCT | ⚠️ Endpoint 404 | Verificar registro |
| Certificado Banco Inter | ❌ Corrompido (ASN.1) | Reemitir no portal Inter |

---

## 1. NFS-e — Infraestrutura

### Estado atual
- **Endpoint ativo:** `GET /api/v1/financial/nfse` → **HTTP 200** ✅
- **Dashboard ativo:** `GET /api/v1/financial/nfse/dashboard` → **HTTP 200** ✅
- **Banco de dados:** 27 NFS-e registradas, status `autorizada`
- **Controller:** `modules/ged/controllers/nfse_controller.py`
- **Registro no main:** `api_router.include_router(nfse_router, prefix="/financial")`
- **NFS-e Entrada:** Registrada condicionalmente (`if nfse_entrada_router`)
- **NFS-e Multi-empresa:** `prefix="/fiscal"` — endpoint 404 (não carregado)

### Rotas disponíveis
```
GET  /api/v1/financial/nfse              ← lista com paginação (27 registros)
GET  /api/v1/financial/nfse/dashboard    ← dashboard financeiro
GET  /api/v1/financial/contracts         ← contratos
GET  /api/v1/financial/contracts/summary ← sumário
```

### Gap identificado
- **Sem endpoint de emissão:** `POST /api/v1/financial/nfse/emitir` → 404
- O controller define rotas de consulta mas não de transmissão para a prefeitura
- A integração com ABRASF/ISSNET está em `modules/government_integrations/core/nfse_manaus.py` mas não está exposta via endpoint REST no controller do GED

### Recomendação
O módulo de NFS-e de **consulta está funcional** para os 13 clientes ativos. A transmissão automática à prefeitura de Manaus (ABRASF 2.04) existe no código mas precisa de endpoint dedicado se o fluxo não for automático via Celery.

---

## 2. Holerite PDF — Estado Atual

### Estado atual
- **Endpoint CRUD ativo:** `GET /api/v1/people-management/dp/payslips/` → **HTTP 200** ✅
- **Controller:** `modules/people_management/employee_portal/controllers/dp_payslips_controller.py`
- **Prefixo:** `/dp/payslips` registrado com `prefix="/people-management"`
- **Banco de dados:** 0 holerites cadastrados (tabela vazia — aguarda importação)

### Rotas disponíveis
```
GET    /api/v1/people-management/dp/payslips/              ← lista
POST   /api/v1/people-management/dp/payslips/              ← criar
GET    /api/v1/people-management/dp/payslips/{id}          ← detalhe
PATCH  /api/v1/people-management/dp/payslips/{id}/publicar ← publicar para portal
PATCH  /api/v1/people-management/dp/payslips/{id}/rascunho ← voltar para rascunho
DELETE /api/v1/people-management/dp/payslips/{id}          ← excluir
POST   /api/v1/people-management/dp/payslips/importar-lote ← importação em lote
```

### Gap identificado
- **Sem endpoint PDF:** Não existe `GET /api/v1/people-management/dp/payslips/{id}/pdf`
- O CRUD de contracheques está implementado (criar, publicar, importar em lote)
- Mas não há geração de PDF do holerite para download (nem pelo DP nem pelo portal do funcionário)
- O módulo `folha/` tem `calculo_service.py` e `folha_controller.py` que complementam — verificar integração

### Recomendação
Implementar `GET /{payslip_id}/pdf` no `dp_payslips_controller.py` usando reportlab (já disponível no container), similar ao que foi feito para contratos em M7. O `payslip_service.py` deve ter os dados necessários para renderização.

---

## 3. Solides VA — Estado Atual

### Estado atual
- **Token configurado:** `SOLIDES_API_TOKEN=***` no `.env` ✅
- **Configurações adicionais presentes:**
  - `SOLIDES_WEBHOOK_SECRET`
  - `SOLIDES_SYNC_INTERVAL_MINUTES`
  - `SOLIDES_CONFLICT_STRATEGY`
  - `SOLIDES_AUTO_CREATE_DEPARTMENTS`
  - `SOLIDES_AUTO_CREATE_POSITIONS`
  - `SOLIDES_RATE_LIMIT_PER_MINUTE`
- **Status endpoint:** `GET /api/v1/integrations/solides/status` → **HTTP 200** ✅
- **Controller:** `modules/integrations/controllers/solides_controller.py`
- **Prefixo controller:** `/solides` — mas não está no prefixo `/integrations` no main

### Connector completo
O conector Solides é robusto — possui:
```
connector.py         ← cliente HTTP Solides API
sync_service.py      ← sincronização bidirecional
integration_service.py
webhook_handler.py   ← recebe webhooks do Solides
conflict_resolver.py ← resolve conflitos de dados
mappers.py           ← mapeamento Solides ↔ Conecta PRO
tasks.py             ← Celery tasks para sync assíncrono
```

### Gap identificado
- **CCT Benefícios (VA/VR/VT):** `GET /api/v1/people-management/hr/beneficios` → 404
  - O `benefits_controller.py` existe em `modules/cct/controllers/` com rotas `/beneficios`
  - O CCT principal está registrado com `prefix="/people-management/hr"` — mas o `benefits_controller` específico pode não estar incluído
- **Sync endpoint:** `POST /api/v1/integrations/solides/sync` → 404 (sync provavelmente roda via Celery cron)
- A integração VA/VR/VT é via CCT (Convenção Coletiva) — dados de benefícios definidos pela SINDECOMPRESTS

### Recomendação
Verificar se o `benefits_controller` do CCT está sendo incluído no router principal. O `beneficios` da CCT (VA R$25,50/dia, VR, VT) está modelado mas pode estar sem rota exposta.

---

## 4. Certificado Banco Inter — Diagnóstico

### Problema identificado
O certificado `Inter_API_Certificado.crt` está **corrompido no nível ASN.1**:

```
Campo corrompido: subject.countryName
Esperado: "BR"  (bytes: 42 52)
Encontrado: "1\x00"  (bytes: 31 00 — byte nulo)
```

**Resultado dos testes:**
- `openssl x509`: ❌ Unable to load certificate
- `python ssl.load_cert_chain()`: ❌ PEM lib error
- `pyOpenSSL`: ❌ wrong tag / nested ASN1 error
- `python cryptography`: ❌ InvalidValue no PrintableString
- Chave privada `.key`: ✅ RSA key ok

### Causa raiz
O certificado foi gerado com defeito pelo portal do Banco Inter — o campo país do Subject tem um byte nulo que viola o RFC 5280 (PrintableString não permite caracteres de controle). **Não é problema de truncamento ou encoding** — o DER tem 1151 bytes (completo conforme o cabeçalho SEQUENCE), mas o conteúdo é inválido.

### Solução
1. Acessar [developers.inter.co](https://developers.inter.co/) → "Meus Apps"
2. Selecionar a aplicação → **"Gerar novo certificado"** ou **"Renovar certificado"**
3. Baixar o novo par `.crt` + `.key`
4. Enviar para instalação via este chat

**A chave privada atual está OK** — se o Inter permitir reemitir apenas o certificado (assinado com a mesma chave), não será necessário novo par.

---

## Checklist de Próximas Ações

| Prioridade | Item | Esforço |
|-----------|------|---------|
| 🔴 Alta | Banco Inter: reemitir certificado no portal | 5 min (Jordan) |
| 🔴 Alta | Holerite PDF: implementar endpoint `/pdf` | 2-3h (Claude) |
| 🟡 Média | NFS-e Emissão: endpoint POST se necessário | 1-2h (Claude) |
| 🟡 Média | CCT Benefícios: verificar registro do benefits_controller | 30min (Claude) |
| 🟢 Baixa | Solides sync: confirmar se cron está ativo | 15min |

---

## Ambiente no Momento do Diagnóstico

```
Data:        2026-04-10
Backend:     FastAPI running (conecta-pro-backend — healthy)
Branch:      feature/people-management-reorganization
NFS-e:       27 notas autorizadas em banco
Holerites:   0 registros (tabela vazia)
Solides:     Token configurado, status 200
Inter cert:  Corrompido — ASN.1 countryName inválido
```
