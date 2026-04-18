# CONTRATO GEDEON — Fonte Única de Verdade
**Versão:** 1.2
**Data:** 2026-04-18
**Status:** Ativo — todo terminal da FASE B2+ DEVE ler ANTES de implementar

---

## REGRA ZERO
Este arquivo é a verdade. Se algo aqui conflita com a sua memória ou
com um prompt que você recebeu, **este arquivo prevalece**. Se você
descobrir algo novo durante o trabalho, atualize este arquivo ANTES
de commitar o código novo.

---

## 1. AUTENTICAÇÃO ONVIO (validado em produção 17-18/04/2026)

### 1.1. Fluxo de 3 etapas (imutável)
1. OIDC login → recebe `code` + `state`
2. `POST /api/security/v1/oidc/auth-code/session` → retorna JWT
3. `POST /api/security/v3/sessions/jwt` com `Authorization: Bearer <JWT>` → retorna **LongToken** (32 chars hex)

### 1.2. Header CORRETO para todas chamadas subsequentes
```
Authorization: UDSLongToken <LongToken>
```
**NÃO usar:** `UDS-Session-Token`, `Authorization: Bearer` (jwt), cookies apenas.

### 1.3. Redis (sessão ativa)
- **DB:** 1 (não 0)
- **Key:** `onvio:session`
- **TTL:** 57600s (16 horas)
- **Payload (JSON):** `cookies`, `uds_token` (JWT), `long_token` (32 chars), `extracted_at`

### 1.4. Base URL
```
https://onvio.com.br/api/storage/v1/...   (clientcenter — CORRETO)
```
**NÃO usar:** `api.onvio.com.br` (Developers API — não aplicável a este cliente)

### 1.5. Identidade do cliente
- `clientId`: `92A4D531C6314E309B62FDF3D9F1359C`
- `companyId`: `74E4323F0E014F579EA28DD4C7835AA6`

### 1.6. Renovação automática
- Script: `/opt/conecta-pro/onvio_auth.py`
- Cron: `0 4 * * *` (diário 04:00)
- Credenciais: lidas de `.env` (ONVIO_PASS, ONVIO_IMAP_PASSWORD)
- MFA via IMAP: `imap.titan.email:993`

---

## 2. PATHS CANÔNICOS DE CÓDIGO (pós-consolidação FASE A)

### 2.1. Backend Python
```
backend/modules/gedeon/onvio/
├── onvio_client.py          (OnvioClient — HTTP)
├── onvio_parser.py          (classificar_documento + extract_mes_ref)
├── onvio_sync_service.py    (OnvioSyncService — orquestração)
└── controllers/
    └── onvio_controller.py  (FastAPI router)

backend/modules/gedeon/models/
└── onvio_models.py          (OnvioDocument, OnvioSyncLog, FgtsGuia, InssGuia)
```

### 2.2. Path proibido (duplicatas eliminadas)
- ❌ `backend/app/modules/integrations/onvio/` (deletado)
- ❌ `backend/modules/integrations/onvio/` (deletado)
- ❌ `backend/modules/ged/models/onvio_models.py` (deletado — era duplicata)
- ❌ `/app/modules/gedeon/gedeon/` (fantasma limpo)

### 2.3. Container (Docker)
```
/app/modules/gedeon/onvio/...     (caminho ATIVO)
/app/uploads/onvio/               (storage de PDFs — volume montado)
```

### 2.4. Storage de PDFs
```
STORAGE_BASE = Path("/app/uploads/onvio")

Estrutura: /app/uploads/onvio/<categoria>/<mes_ref>/<nome_seguro>.pdf
Exemplo:   /app/uploads/onvio/fgts_guia/03.2026/GFD FGTS 03.2026.pdf
```

---

## 3. SCHEMA DE BANCO DE DADOS (validado em produção)

### 3.1. `onvio_documents` (13 colunas)
```
id              UUID PK
onvio_id        str UNIQUE        (ID do Onvio)
onvio_folder_id str               (containerId do Onvio)
nome_arquivo    str
categoria       str               (37 categorias — ver seção 4)
mes_ref         str | NULL        (formato "MM.YYYY" ou "YYYY" — NUNCA "YYYY-MM")
caminho_local   str               (path no container)
tamanho_bytes   int
data_onvio      timestamp         (createdDate do Onvio — auditoria apenas)
processado      bool              (default False)
created_at      timestamp
updated_at      timestamp
```

### 3.2. `onvio_sync_log` (9 colunas)
```
id            UUID PK
mes_ref       str               ("all" ou "MM.YYYY")
status        str               (success / partial / error / running)
docs_baixados int
docs_novos    int
docs_erro     int
duracao_s     float
detalhes      text
created_at    timestamp
```

### 3.3. `fgts_guias` (9 colunas)
```
id           UUID PK
mes_ref      str               (formato "MM.YYYY")
tipo         str               (GUIA / CONSIGNADO / RELATORIO / CONSIGNADO_RELATORIO)
arquivo_pdf  str               (path no container)
valor        Decimal | NULL    (a preencher na FASE B2)
vencimento   date | NULL       (a preencher na FASE B2)
codigo_barras str | NULL       (a preencher na FASE B2)
created_at   timestamp
updated_at   timestamp
```

### 3.4. `inss_guias` (9 colunas)
Estrutura idêntica a `fgts_guias` mas sem campo `tipo`.

### 3.5. Alembic head atual
```
sprint82b_gedeon_schema_fix
```

### 3.6. Regra de migration
- ADICIONAR colunas: OK via alembic revision + upgrade
- DELETAR colunas: PROIBIDO sem aprovação explícita
- MODIFICAR colunas: sempre criar NEW col + migrar dados + DROP old

---

## 4. PARSER V2 — 37 CATEGORIAS (FASE B1)

### 4.1. Assinatura da função
```python
from modules.gedeon.onvio.onvio_parser import classificar_documento

resultado = classificar_documento(nome: str, created_date: Optional[str] = None) -> dict
# Retorna: {"categoria": str, "mes_ref": Optional[str], "confianca": float}
```

### 4.2. mes_ref — regras
1. Extraído do **NOME do arquivo**, NUNCA do `created_date`
2. Formatos aceitos: `"MM.YYYY"` (preferido), `"YYYY"` (fallback anuais), `None`
3. Formato PROIBIDO: `"YYYY-MM"` (foi bug da FASE A)
4. CNPJs (14 dígitos contíguos) são IGNORADOS antes de extrair

### 4.3. Categorias ativas (contagem real pós-T3)
```
folha_pagamento          69    |  dctfweb_recibo          11
recibo_folha             68    |  dctfweb_extrato         10
das_simples_nacional     21    |  dctfweb_creditos         9
outros                   20    |  dctfweb_debitos          8
guia_issqn               20    |  fgts_consignado          9
parcelamento_simples     20    |  fgts_consignado_relatorio 9
documento_digitalizado   16    |  ficha_registro           9
fgts_guia                12    |  empresa_docs             8
fgts_relatorio           12    |  declaracao_vt            8
contrato_trabalho        12    |  decimo_terceiro          8
dctfweb_declaracao       12    |  recibo_decimo_terceiro   8
dctfweb_resumo_debitos   11    |  dar_sefaz                6
dctfweb_resumo_creditos  11    |  autodeclaracao           5
                                   inss_guia                5
                                   rescisao                 5
                                   alvara                   3
                                   afastamento              2
                                   atestado                 2
                                   dctfweb_situacao         2
                                   ferias                   1
                                   folha_ponto              1
                                   aviso_previo             1
                                   aso                      1
                                   portal_empregador        1
```

### 4.4. Como adicionar categoria nova
1. Editar `backend/modules/gedeon/onvio/onvio_parser.py`
2. Adicionar regra em `rules` list (posição crítica — mais específico primeiro)
3. Adicionar caso no bloco `__main__` (testes inline)
4. Rodar: `python3 -m modules.gedeon.onvio.onvio_parser` → deve passar todos
5. Atualizar seção 4.3 deste contrato

---

## 5. ZONAS PROIBIDAS (nunca tocar)

```
financial/                       (pipeline financeiro estável)
government_integrations/         (integrações governo)
main_production.py               (1 exceção documentada — router onvio)
.env e .env.*                    (secrets)
docker-compose*.yml              (infra crítica)
alembic/versions/*               (só ADICIONAR, nunca MODIFICAR)
credentials/                     (certificados)
```

Exceção registrada:
- `GOVERNANCE_EXCEPTION_MAIN_PRODUCTION.md` — router Onvio em bceed412

---

## 6. ENDPOINTS PÚBLICOS ATIVOS

### 6.1. GET
```
GET /api/v1/onvio/status            → {sessao_valida, redis_key}
GET /api/v1/onvio/stats             → {total, por_categoria}
GET /api/v1/onvio/documentos        → {total, documentos[]} (paginado)
GET /api/v1/onvio/historico         → [syncs]
GET /api/v1/onvio/guias/fgts        → [fgts_guias]
GET /api/v1/onvio/guias/inss        → [inss_guias]
```

### 6.2. POST
```
POST /api/v1/onvio/sync             → dispara sync (batch todos ou ?mes_ref=MM.YYYY)
POST /api/v1/onvio/reclassificar    → reaplica parser aos docs existentes
```

### 6.3. Regra para NOVOS endpoints (FASE B2)
- Sempre prefixo `/api/v1/onvio/`
- Router registrado em `modules/gedeon/onvio/controllers/onvio_controller.py`
- SEM tocar `main_production.py`
- Documentar neste contrato na seção 6

---

## 7. REGRAS DE INTER-COMUNICAÇÃO ENTRE TERMINAIS

### 7.1. Cabeçalho obrigatório em todo prompt da FASE B2+
```
STEP 0 — LEIA O CONTRATO:
cat /opt/conecta-pro/CONTRACTS_GEDEON.md
Confirme 5 pontos ANTES de agir:
- Header Onvio: ___________
- Redis DB: ___________
- Path canônico do código: ___________
- Storage de PDFs: ___________
- Formato do mes_ref: ___________
```

### 7.2. Interface compartilhada BaseExtractor (FASE B2)
Todo extractor de PDF da FASE B2 HERDA de `BaseExtractor` (T1_B2).
NÃO implementar do zero — sempre `class MinhaExtractor(BaseExtractor)`.

### 7.3. Princípio de falsificação
Todo commit de função crítica inclui teste negativo:
- Se `funcao_x(input_valido)` retorna True → sabotar input e confirmar que retorna False.
- Se `endpoint(dados_reais)` retorna 200 → verificar `COUNT(*) > 0` no DB.
- Falha de falsificação = NÃO commitar.

### 7.4. Hot copy de código (não rebuild)
Backend:  `docker cp <arquivo> conecta-pro-backend:/app/...` + `docker restart`
Frontend: `npm run build` + `docker cp .next/. conecta-pro-frontend:/app/.next/`
NUNCA: rodar múltiplos builds frontend em paralelo (OOM).

---

## 8. CONVENÇÕES DE DADOS (FASE B2)

### 8.1. Valores monetários
- SEMPRE `Decimal` (nunca `float`)
- 2 casas decimais
- Armazenar em centavos OU em Decimal com precisão 15,2
- Formato string aceito: "R$ 1.234,56" / "1.234,56" / "1234.56" / "1,234.56"

### 8.2. Datas
- Sempre `date` (vencimentos) ou `datetime` (timestamps)
- Parser de data brasileira: `dateutil.parser(dayfirst=True)`
- Nunca string ambígua tipo "03/04"

### 8.3. Confiança de extração
- Float 0.0 a 1.0
- >= 0.90 → salva no DB como valor final
- 0.70 a 0.89 → salva com flag `revisao_manual=true`
- < 0.70 → NÃO salva, log como "extração inconclusiva"

### 8.4. CNPJs em dados
- Validar dígitos verificadores antes de aceitar
- Armazenar sem formatação: `35710481000103`
- Exibir com formatação: `35.710.481/0001-03`

---

## 9. PROCEDIMENTO DE ATUALIZAÇÃO DESTE CONTRATO

Se durante a FASE B2 descobrir um fato novo (ex: API do Onvio tem limite de rate de 100 req/min),
o agente que descobriu DEVE:
1. Adicionar seção neste arquivo
2. Incrementar versão (ex: 1.0 → 1.1)
3. Commitar ATOMICAMENTE junto com o código que usa esse fato novo
4. Registrar no changelog abaixo

---

## 10. DESCOBERTAS FASE B2 T1 (2026-04-18)

### 10.1. Colunas pré-existentes com tipos errados (corrigidas em sprint83)
`fgts_guias` e `inss_guias` já tinham `valor` (double precision) e `vencimento` (timestamptz)
de uma migration anterior com tipos incorretos. A sprint83 faz drop + recreate com tipos corretos
(`Numeric(15,2)` e `Date`). Os dados eram NULL — nenhuma perda.

### 10.2. Alembic revision ID — limite de 32 chars
A tabela `alembic_version` tem `version_num VARCHAR(32)`. IDs estilo
`sprint83_gedeon_fase_b2_extraction` (35 chars) excedem o limite.
**Regra:** usar sempre o hash curto gerado automaticamente pelo alembic (ex: `9d91ef5c61f6`).
O texto descritivo vai no docstring da migration.

### 10.3. Container alembic/env.py pode ficar desatualizado
O `env.py` no container pode ficar stale em relação ao host. Antes de qualquer
`alembic upgrade` via `docker exec`, sempre sincronizar:
```bash
docker cp backend/alembic/env.py conecta-pro-backend:/app/alembic/env.py
```

### 10.4. PDFs Onvio são texto nativo (não imagens)
Confirmado em 3 amostras: pdfplumber extrai 3K–17K chars por PDF.
Os PDFs são gerados por software (não digitalizados/CamScanner).
OCR não é necessário para o lote atual — BaseExtractor funciona com regex direto.

---

## 11. DESCOBERTAS FASE B2 T2 (2026-04-18)

### 11.1. Competência INSS em nome PT-BR (não numérico)
A competência do DARF INSS aparece como nome do mês em português seguido de ano:
`Março/2026`, `Janeiro/2026`, `Novembro/2025` — **não** como `03/2026`.
INSSExtractor inclui dicionário `_MESES_PT` e converte para `MM/YYYY` antes de retornar.

### 11.2. Barcode DARF INSS: 48 dígitos (4×11 + 4 check)
O código de barras da linha digitável do DARF tem formato:
`NNNNNNNNNNN D NNNNNNNNNNN D NNNNNNNNNNN D NNNNNNNNNNN D`
(4 grupos de 11 dígitos + 1 check digit por grupo = **48 dígitos** sem espaços).
Começa com `858`. Diferente do formato GPS clássico de 47 dígitos.

### 11.3. Discriminador DARF INSS vs DAS Simples Nacional
Ambos os documentos (INSS e DAS) são gerados pelo sistema SENDA e têm estrutura quase idêntica:
mesmos campos (competência, vencimento, valor, CNPJ, barcode).
A diferença está na **linha 2 do cabeçalho**:
- INSS DARF: `"Documento de Arrecadação\nde Receitas Federais"`
- DAS: `"Documento de Arrecadação\ndo Simples Nacional"`
INSSExtractor aplica cap de `0.65` para documentos sem o marcador "de Receitas Federais",
impedindo que DAS seja aceito como INSS mesmo com todos os outros campos presentes.

### 11.4. Diretório inss_guia contém docs misclassificados (34 vs 4 reais)
`/app/uploads/onvio/inss_guia/` contém **34 PDFs** mas apenas **4 são DARFs INSS reais**
(GuiaPagamento Conecta Mais). Os outros 30 são Folha de Pagamento, Recibos e DAS que foram
classificados antes do parser v2. O DB (`onvio_documents`) tem somente 4–5 com
`categoria='inss_guia'`. T5 deve filtrar por DB, não por filesystem.

### 11.5. fgts_guia vazio no container (2026-04-18)
`/app/uploads/onvio/fgts_guia/` estava vazio no container em 2026-04-18.
A falsificação 2 do INSSExtractor foi executada contra DAS (proxy válido, mesma estrutura).

---

## CHANGELOG

| Versão | Data       | Autor      | Mudança                                  |
|--------|------------|------------|------------------------------------------|
| 1.0    | 2026-04-18 | T_CONTRACT | Contrato inicial pós FASE B1             |
| 1.1    | 2026-04-18 | T1_B2      | Seção 10: descobertas T1_B2 (tipos errados, revision ID, env.py sync, PDFs texto nativo) |
| 1.2    | 2026-04-18 | T2_B2      | Seção 11: descobertas T2_B2 (competência PT-BR, barcode 48 dígitos, discriminador DARF vs DAS, dirs misclassificados, fgts_guia vazio) |
