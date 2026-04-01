# RELATÓRIO DE CORREÇÃO — INFRAESTRUTURA HTTP/HTTPS

## Data: 14/03/2026
## Servidor: 82.25.75.74 (erp.conectamais.pro)
## Diretório: /opt/conecta-pro/

---

## PROBLEMA IDENTIFICADO

**Cenários A + B + C + D combinados:**

O auditor reportou que endpoints HR com parâmetros (`?limit=50`) retornavam **503 Service Unavailable**.
A causa raiz era **Mixed Content**: o FastAPI gerava redirects 307 com scheme `http://` em vez
de `https://`, e o browser bloqueava a requisição.

Problemas encontrados:

| # | Problema | Cenário | Impacto |
|---|----------|---------|---------|
| 1 | FastAPI sem ProxyHeadersMiddleware | B | 307 redirect para http:// → Mixed Content → 503 |
| 2 | Frontend com http://localhost hardcoded em 6 arquivos | C | Mixed Content em produção |
| 3 | CORS duplicado (nginx + FastAPI) | D | Browser rejeita headers duplicados |
| 4 | Endpoints /hr/vacations/, /hr/leaves/, /hr/documents/ inexistentes | — | 404 Not Found |
| 5 | Reembolso approvals exigia condominio_id para admin | — | 400 Bad Request |
| 6 | 11 páginas DP com localStorage.getItem('token') errado | — | Dashboard 0 colaboradores |
| 7 | Botões esocial/documentos sem onClick | — | Botões sem feedback |
| 8 | 307 redirect por trailing slash (FastAPI) | A | Latência extra, confunde auditoria |

---

## AÇÕES REALIZADAS

### FASE 1 — Diagnóstico (executado)
1. Verificada configuração completa do Nginx (sites-enabled, proxy_pass, headers)
2. Verificados containers Docker (status, env vars, portas)
3. Verificada configuração do Backend FastAPI (CORS, middlewares, .env)
4. Verificada configuração do Frontend Next.js (env vars, api.ts, axios-instance.ts)
5. Testadas chamadas HTTP vs HTTPS (307 redirect, CORS headers, redirect Location)

### FASE 2 — Identificação
- Confirmado: `location: http://erp.conectamais.pro/...` (HTTP, não HTTPS)
- Confirmado: CORS duplicado (2x Access-Control-Allow-Origin)
- Confirmado: Frontend com URLs http:// hardcoded

### FASE 3 — Correções Infraestrutura

**3.1 Backend — ProxyHeadersMiddleware:**
```python
# main_production.py — ADICIONADO
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])
```

**3.2 Nginx — CORS sem duplicação + rewrite trailing slash:**
```nginx
# Removido CORS duplicado (FastAPI gerencia CORS)
# Adicionado rewrite para evitar 307:
rewrite ^(/api/v1/[^.?]*[^/])$ $1/ break;
```

**3.3 Frontend — 6 arquivos corrigidos para HTTPS:**
- `src/lib/axios-instance.ts` — fallback http://localhost:8000 → detecção inteligente
- `src/api/client/axios-instance.ts` — fallback http://localhost:8080 → detecção
- `src/app/modulos/layout.tsx` — fallback http://localhost:8080 → detecção
- `src/app/modulos/empresas/migrador/page.tsx` — hardcoded → detecção hostname
- `src/app/modulos/financeiro/relatorios/page.tsx` — hardcoded → detecção hostname
- `src/app/modulos/licitacoes/ia/page.tsx` — fallback → detecção

**3.4 Frontend — .env.production criado:**
```
NEXT_PUBLIC_API_URL=https://erp.conectamais.pro
NEXT_PUBLIC_APP_URL=https://erp.conectamais.pro
```

### FASE 4 — Correções Adicionais

**4.1 Endpoints faltantes criados:**
- `leave_controller.py` — GET /hr/leaves/ (listagem de afastamentos)
- `document_controller.py` — GET /hr/documents/ (listagem de documentos)
- `vacation_controller.py` — GET /hr/vacations/ (listagem direta)
- `aggregator.py` — registrados os novos routers

**4.2 Reembolso approvals — admin fix:**
```python
# reimbursement_controller.py — get_condominio_id()
# ANTES: raise HTTPException(400, "Usuário não possui condomínio associado")
# DEPOIS: return None (permite admin listar sem condomínio)
```

**4.3 Token fix — 11 páginas DP:**
```javascript
// ANTES (errado):
localStorage.getItem('token')
// DEPOIS (correto):
(localStorage.getItem('access_token') || localStorage.getItem('token'))
```
Páginas corrigidas: page.tsx, admissao, beneficios, contratos, documentos, esocial, ferias, folha, licencas, ponto, rescisao

**4.4 Botões sem feedback — toast adicionado:**
- `esocial/page.tsx` — "Enviar Pendentes" e "Detalhes" com toast
- `documentos/page.tsx` — "Upload Documento", "Visualizar" e "Download" com toast

**4.5 Validação de Email:**
- Verificado: `validateEmail()` existe em `utils/validators.ts`
- Mensagens em PT-BR confirmadas: "E-mail inválido", "E-mail é obrigatório"
- Sem bug a corrigir

---

## ARQUIVOS MODIFICADOS

### Backend (docker cp + docker restart)
| Arquivo | Alteração |
|---------|-----------|
| main_production.py | +ProxyHeadersMiddleware (import + add_middleware) |
| modules/people_management/hr/aggregator.py | +leave_router +document_router |
| modules/people_management/hr/controllers/vacation_controller.py | +GET / (listagem direta) |
| modules/people_management/hr/controllers/leave_controller.py | NOVO (endpoint /hr/leaves/) |
| modules/people_management/hr/controllers/document_controller.py | NOVO (endpoint /hr/documents/) |
| modules/people_management/hr/controllers/time_tracking_controller.py | Comentário atualizado |
| modules/reimbursement/controllers/reimbursement_controller.py | get_condominio_id → return None para admin |

### Frontend (next build + pm2 restart)
| Arquivo | Alteração |
|---------|-----------|
| .env.production | NOVO (NEXT_PUBLIC_API_URL=https://...) |
| src/lib/axios-instance.ts | Fallback → detecção inteligente HTTPS |
| src/api/client/axios-instance.ts | Fallback → detecção inteligente HTTPS |
| src/app/modulos/layout.tsx | Fallback → detecção inteligente HTTPS |
| src/app/modulos/empresas/migrador/page.tsx | Hardcoded → detecção hostname |
| src/app/modulos/financeiro/relatorios/page.tsx | Hardcoded → detecção hostname |
| src/app/modulos/licitacoes/ia/page.tsx | Fallback → detecção HTTPS |
| src/app/modulos/dp/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/admissao/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/beneficios/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/contratos/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/documentos/page.tsx | Token fix + toast nos botões |
| src/app/modulos/dp/esocial/page.tsx | Token fix + toast nos botões |
| src/app/modulos/dp/ferias/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/folha/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/licencas/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/ponto/page.tsx | Token: 'token' → 'access_token' |
| src/app/modulos/dp/rescisao/page.tsx | Token: 'token' → 'access_token' |

### Nginx
| Arquivo | Alteração |
|---------|-----------|
| /etc/nginx/sites-available/erp.conectamais.pro | Removido CORS duplicado, adicionado rewrite trailing slash |

**Total: 7 arquivos backend + 18 arquivos frontend + 1 nginx = 26 arquivos modificados**

---

## TESTES PÓS-CORREÇÃO

### Endpoints HR via HTTPS com parâmetros (sem trailing slash, sem -L)

| Endpoint | ANTES | DEPOIS (sem auth) | DEPOIS (com auth) |
|----------|-------|--------------------|--------------------|
| /hr/employees?limit=50 | 503 | 403 | **200** |
| /hr/admissions?limit=50 | 503 | 403 | **200** |
| /hr/terminations?limit=50 | 503 | 403 | **200** |
| /hr/contracts?limit=50 | 503 | 403 | **200** |
| /hr/vacations?limit=50 | 404 | 403 | **200** |
| /hr/benefits?limit=50 | 503 | 403 | **200** |
| /hr/leaves?limit=50 | 404 | 403 | **200** |
| /hr/documents?limit=50 | 404 | 403 | **200** |

### Funcionalidades adicionais

| Funcionalidade | ANTES | DEPOIS |
|----------------|-------|--------|
| Colaboradores Ativos | 0 | **44** |
| 307 redirect scheme | http:// | **https://** |
| CORS headers | 2 (duplicado) | **1** |
| Reembolso approvals/pending | 400 | **200** |
| Reembolso stats | 400 | **200** (14 reembolsos) |
| Token nas páginas DP | 'token' (errado) | **'access_token'** |
| Botões esocial/documentos | sem feedback | **toast** |
| Email validação | OK | **OK** (sem bug) |

---

## SERVIÇOS

| Serviço | Status | Detalhe |
|---------|--------|---------|
| conecta-pro-backend | healthy | Docker, porta 8080 |
| conecta-pro-frontend | healthy | Docker, porta interna |
| conecta-pro-frontend (PM2) | online | PM2 pid 9416, porta 3001 |
| Nginx | OK | syntax ok, test successful |

---

## DASHBOARD

- **Colaboradores Ativos: 44** (antes: 0)
- **Reembolsos: 14** (4 submetidos, 4 aprovados, 2 pagos, 3 rascunho, 1 rejeitado)
- **Folha Atual: N/A** (endpoint /dashboard ainda não implementado)

---

## RESULTADO

### [x] PROBLEMA RESOLVIDO

---

## EVIDÊNCIAS

### E1: Serviços rodando
```
conecta-pro-backend    Up 7 minutes (healthy)
conecta-pro-frontend   Up 2 days (healthy)
PM2: conecta-pro-frontend online pid 9416
```

### E2: Nginx OK
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### E3: Health Check
```json
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"production"}
```

### E4: 8/8 endpoints sem auth → 403 (backend respondendo)
```
/hr/employees?limit=50    -> 403
/hr/admissions?limit=50   -> 403
/hr/terminations?limit=50 -> 403
/hr/contracts?limit=50    -> 403
/hr/vacations?limit=50    -> 403
/hr/benefits?limit=50     -> 403
/hr/leaves?limit=50       -> 403
/hr/documents?limit=50    -> 403
```

### E5: 8/8 endpoints com auth → 200
```
/hr/employees?limit=50    -> 200
/hr/admissions?limit=50   -> 200
/hr/terminations?limit=50 -> 200
/hr/contracts?limit=50    -> 200
/hr/vacations?limit=50    -> 200
/hr/benefits?limit=50     -> 200
/hr/leaves?limit=50       -> 200
/hr/documents?limit=50    -> 200
```

### E6: Employee Count
```
total=44 items=20
```

### E7: 307 redirect agora usa HTTPS (causa raiz resolvida)
```
ANTES:  location: http://erp.conectamais.pro/api/v1/people-management/hr/employees/
DEPOIS: location: https://erp.conectamais.pro/api/v1/people-management/hr/employees/
```

### E8: CORS sem duplicação
```
Access-Control-Allow-Origin headers: 1 (antes: 2)
```

### E9: Reembolso
```
/reimbursements/           -> 200 (14 items)
/approvals/pending         -> 200 (0 pendentes)
/stats                     -> 200 (total=14, by_status={rejeitado:1, pago:2, aprovado:4, submetido:4, rascunho:3})
```

### E10: Frontend Homepage
```
Homepage HTTPS: 200
```

### E11: ProxyHeadersMiddleware confirmado no container
```python
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])
```

### E12: Nginx rewrite confirmado
```nginx
rewrite ^(/api/v1/[^.?]*[^/])$ $1/ break;
```

### E13: .env.production confirmado
```
NEXT_PUBLIC_API_URL=https://erp.conectamais.pro
NEXT_PUBLIC_APP_URL=https://erp.conectamais.pro
```

### E14: Token fix confirmado (11 páginas DP)
```
Páginas com access_token: 11
Padrão: (localStorage.getItem('access_token') || localStorage.getItem('token'))
```

### E15: Toast feedback confirmado (8 páginas DP)
```
Páginas com toast: rescisao, contratos, ferias, beneficios, licencas, esocial, documentos, admissao (via sonner)
```

---

## DEPLOY EXECUTADO

1. `docker cp` — 7 arquivos backend copiados para container conecta-pro-backend
2. `docker restart conecta-pro-backend` — backend reiniciado
3. `nginx -t && systemctl reload nginx` — nginx recarregado
4. `NODE_OPTIONS=--max-old-space-size=8192 npx next build` — frontend reconstruído
5. `cp -r public .next/standalone/ && cp -r .next/static .next/standalone/.next/` — static files
6. `pm2 restart conecta-pro-frontend` — frontend reiniciado

---

*Relatório gerado em 14/03/2026 às 20:20 UTC*
*Sessão 25 — Conecta PRO ERP*
