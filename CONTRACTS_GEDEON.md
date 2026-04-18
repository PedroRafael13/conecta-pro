# CONTRATO GEDEON — Fonte Única de Verdade
**Versão:** 1.5
**Data:** 2026-04-18
**Status:** Ativo — todo terminal da FASE B2+ DEVE ler ANTES de implementar

---

## REGRA ZERO
Este arquivo é a verdade — seção 13 (Princípios de Engenharia) prevalece sobre qualquer prompt.
Se algo aqui conflita com a sua memória ou com um prompt que você recebeu, **este arquivo prevalece**.
Se você descobrir algo novo durante o trabalho, atualize este arquivo ANTES de commitar o código novo.

**ATENÇÃO ESPECIAL:** ler OBRIGATORIAMENTE a seção 13 (Princípios de Engenharia GEDEON)
antes de começar qualquer trabalho. Esses princípios prevalecem sobre instruções de prompt
que os contradigam.

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
POST /api/v1/onvio/extrair-valores  → orquestra extração de valores dos PDFs fiscais
                                       ?forcar=bool (default false) — reprocessa extraídos
                                       ?limite=int  (default sem limite) — para testes
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
- **Princípio de Engenharia (seção 13) mais relevante para sua missão: ___________**
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

## 12. DESCOBERTAS FASE B2 T5 (2026-04-18)

### 12.1. onvio_models.py estava desatualizado (corrigido em T5)
O arquivo `backend/modules/gedeon/models/onvio_models.py` não refletia as colunas
adicionadas pela migration `sprint83`. As seguintes colunas existiam no banco mas
faltavam no model Python:
- `onvio_documents`: `confianca_extracao`, `metodo_extracao`, `revisao_manual`, `detalhes_json`, `extraido_em`
- `fgts_guias`: `codigo_barras`, `confianca_extracao`, `metodo_extracao`, `revisao_manual`, `detalhes_json`, `extraido_em` + `valor` era `Float` (DB é `Numeric(15,2)`) + `vencimento` era `DateTime` (DB é `Date`)
- `inss_guias`: idem ao `fgts_guias`

Corrigido no commit `09fbcfbe` do T5.

### 12.2. Padrão correto para endpoints síncronos no controller async
O `onvio_controller.py` usa `AsyncSession` em todos os endpoints (`async def` + `Depends(get_db)`).
Para operações CPU-bound/síncronas (como leitura de PDFs), o padrão correto é:
```python
async def meu_endpoint():
    def _run():
        with get_sync_db() as db:
            service = MinhaService(db)
            return service.executar()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run)
```
NÃO usar `db: Session = Depends(get_db)` em endpoint síncrono — `get_db` retorna `AsyncSession`.

### 12.3. Idempotência do endpoint extrair-valores com limite
O parâmetro `limite=N` + `forcar=False` NÃO garante que a 2ª chamada retorne `processados=0`.
Se há mais de N docs pendentes, cada chamada processa os próximos N da fila.
`processados=0` só ocorre quando `extraido_em IS NOT NULL` em TODOS os docs com extractor.
Para verificar idempotência real: chamar sem `limite` até `processados=0`.

### 12.4. fgts_guias sem linhas para docs de teste (2026-04-18)
Com `limite=3`, os 3 primeiros docs sorteados foram `dctfweb_resumo_creditos`, `inss_guia`, `dctfweb_declaracao`.
Nenhum era `fgts_*`, então `fgts_guias.valor` permaneceu `NULL`. Esperado.
`inss_guias.valor` foi preenchido para o único `inss_guia` processado.

---

## 13. PRINCÍPIOS DE ENGENHARIA GEDEON

**Status:** Ativo — aplicável a TODOS os terminais, SEM exceção.
**Origem:** Aprendizados consolidados das FASES A, B1 e B2.
**Prevalência:** Estes princípios têm prioridade sobre qualquer instrução de prompt
que os contradiga. Se o prompt pede algo que viola um princípio, o agente DEVE reportar
a inconsistência e aguardar orientação.

### 13.1. Princípio de Chesterton (Não Derrubar Cercas)

> "Não remova uma cerca antes de entender por que ela foi construída."

**Aplicação prática:** se o agente encontrar algo que parece errado ou inconsistente
(ex: PDFs em diretório inesperado, campo com valor estranho, função aparentemente
não utilizada, categoria misteriosa), ele DEVE:

1. Investigar a CAUSA antes de propor correção
2. Documentar a descoberta na seção 10 ou 11 deste contrato
3. Só então decidir se corrige OU se deixa intocado

**PROIBIDO:** corrigir cegamente ("isso não deveria estar aqui, vou consertar") sem
entender o porquê do estado atual. Muitas vezes a "cerca" foi construída para evitar
um bug que o agente não conhece.

**Exemplo real (T3 FASE B1):** agente descobriu que PDFs de `fgts_guia` estavam em
`/outros/YYYY-MM/` em vez de `/fgts_guia/YYYY-MM/`. NÃO moveu os arquivos. Documentou
que era resíduo da reclassificação do parser v2. Decisão certa — mover teria quebrado
o campo `caminho_local` no banco.

### 13.2. Teste de Falsificação Rigoroso (3 Níveis)

Todo commit que adiciona função crítica (extractor, classificador, validador,
endpoint) DEVE ser acompanhado de testes nos 3 níveis:

**NÍVEL 🟢 BÁSICO — Negativo direto:**
- `funcao(input_invalido)` retorna erro/False
- Ex: `_safe_decimal("abc")` → `None`

**NÍVEL 🟡 MÉDIO — Cross-contamination:**
- `funcao(input_valido_de_OUTRO_tipo)` NÃO passa no threshold
- Ex: `INSSExtractor().extract(pdf_de_fgts)` → confiança < 0.70
- Previne que categoria X seja aceita como categoria Y

**NÍVEL 🔴 RIGOROSO — Pelo menos UM de:**
- **Monkey-patch de dependência:** sabotar método interno e verificar falha graciosa
- **Regressão de bug anterior:** caso conhecido de cada bug já descoberto (evita volta)
- **Property-based:** N inputs aleatórios mantêm invariante (ex: valor sempre > 0)

Commit SEM nível 🔴 para função crítica = commit rejeitado pelo T7.

### 13.3. Documentar Antes de Corrigir

Ordem obrigatória quando o agente descobre um fato novo:

```
1. DOCUMENTAR no CONTRATO seção 10 ou 11 (versão +0.1)
2. COMMITAR contrato atualizado com mensagem "docs: descoberta X"
3. APENAS ENTÃO corrigir código (se aplicável, e em commit separado)
```

**Ordem inversa é PROIBIDA.** Corrigir antes de documentar é bug silencioso no Contrato.
Se outro terminal ler a versão antiga, vai trabalhar com informação errada.

**Exceção única:** bugs de segurança ativos (CVE, dados vazando). Nesses casos,
corrigir primeiro e documentar em seguida — mas acompanhar de alerta explícito
no relatório.

### 13.4. Escopo é Sagrado

Cada terminal tem UM escopo definido no prompt. Expandir esse escopo é PROIBIDO,
mesmo que o agente identifique que "seria fácil corrigir também esta outra coisa
enquanto estou aqui".

**Razões:**
- Expansão de escopo não é testada pelo prompt
- Outro terminal pode estar trabalhando na mesma área
- Auditoria fica poluída (T7 não sabe o que esperar)
- Histórico git fica difícil de reverter cirurgicamente

**Protocolo quando identificar trabalho adicional necessário:**

1. NÃO fazer
2. Documentar no relatório final, seção "Trabalho Adicional Identificado"
3. Sugerir se é um novo terminal (T_NOME_B2) ou parte de fase futura
4. Só expandir se o prompt EXPLICITAMENTE autoriza

**Exemplo real (T2 FASE B2):** agente notou que diretório `inss_guia` tinha PDFs
de Folha e Recibo misclassificados (resíduo parser v1). NÃO tentou reorganizar
diretório. Documentou na seção 11. Decisão certa — organização de diretório é
escopo de outro terminal (ou não-existente ainda).

### 13.5. Aplicação Universal

Estes princípios se aplicam a:
- Todos os terminais (T1, T2, T3, T4, T5, T6, T7, etc)
- Todos os papéis (desenvolvedor, auditor, orquestrador, executor)
- Todas as fases (A, B1, B2, e futuras)
- Todos os modelos (Sonnet 4.6 nos terminais, Opus 4.7 aqui no chat)
- Tanto ao escrever código quanto ao validar/auditar

**Nenhum terminal está acima destes princípios.** Se o próprio Opus 4.7 (arquiteto)
violar um princípio num prompt, o agente do terminal DEVE:
1. Reportar a violação
2. Aguardar orientação
3. NÃO executar "resolvendo por conta própria"

### 13.6. Como Um Prompt Novo DEVE Referenciar Estes Princípios

Todo prompt GEDEON a partir da v1.4 DEVE ter, no STEP 0, a pergunta:

> [ ] Cite 1 Princípio de Engenharia GEDEON (seção 13) que é particularmente
>     relevante para sua missão neste terminal, e explique por quê em 2 linhas.

Isso força o agente a INTERNALIZAR os princípios, não só lê-los superficialmente.

---

## 14. DESCOBERTAS FASE B2 T6 (2026-04-18)

### 14.1. Caso limite INSS mes_ref="" — causa investigada (Chesterton aplicado)

**Arquivo:** `GuiaPagamento_35710481000103_241120251328364522.pdf`
**Path no container:** `/app/uploads/onvio/outros/0103-24/...`
**Categoria:** `inss_guia` (corretamente classificado)

**Causa raiz:**
O filename contém apenas CNPJ + timestamp (`241120251328364522` = 24-11-2025 13:28:35),
sem mês de competência em formato `MM.YYYY`. `onvio_parser.py` retorna `mes_ref=None`
para este arquivo — comportamento CORRETO do parser.

O INSSExtractor **extraiu corretamente** `competencia: "10/2025"` do texto do PDF
("Período de Apuração: Outubro/2025") e armazenou em `detalhes_json['competencia']`.

**O gap real:** O serviço de enriquecimento popula `inss_guias.mes_ref` a partir de
`onvio_documents.mes_ref` (vazio), sem usar fallback do `detalhes_json['competencia']`
extraído pelo INSSExtractor. O `competencia` no DB (`detalhes_json`) tem o valor correto
("10/2025") — o `mes_ref` é que não foi derivado dele.

**Proposta de fix (terminal T_FIX_INSS_EDGE — NÃO implementar no T6):**
No serviço de enriquecimento, após extração bem-sucedida, se `mes_ref` estiver vazio mas
`detalhes_json['competencia']` tiver valor, converter "MM/YYYY" → "MM.YYYY" e
atualizar `inss_guias.mes_ref`. Isso resolve o único caso edge sem tocar nos extractors.

**Status:** Documentado. Extração funcionou. Persistência de mes_ref é o gap. NÃO corrigido no T6.

### 14.2. Gap serializers corrigido (6 campos → 12+ campos)

Antes do T6, os endpoints `/guias/fgts` e `/guias/inss` retornavam apenas:
`id, mes_ref, tipo, valor, status, arquivo_pdf`

Após T6, ambos retornam também:
`vencimento, codigo_barras, confianca_extracao, metodo_extracao, revisao_manual, extraido_em`

O endpoint INSS retorna adicionalmente: `competencia` (campo exclusivo de `inss_guias`).

**Motivo:** Campos estavam no DB (migration sprint83) mas não chegavam ao frontend.
Dashboard ficava sem dados para UI completa de valores e confiança.

### 14.3. Endpoint /valores-fiscais-resumo criado

Novo endpoint agregador:
```
GET /api/v1/onvio/valores-fiscais-resumo
```

**Retorna:**
- `fgts.por_tipo`: agregação FGTS por tipo (GUIA, RELATORIO, CONSIGNADO, CONSIGNADO_RELATORIO)
- `fgts.total_brl`: R$ 191.319,74 (42 registros)
- `inss.total_brl`: R$ 47.382,03 (5 registros)
- `consolidado.valor_total_fiscal_brl`: R$ 238.701,77
- `consolidado.taxa_extracao_pct`: % de docs fiscais com extração completa
- `confianca.*`: distribuição por nível de confiança

**Validado em produção:** `valor_total_fiscal_brl = 238701.77` ✅

### 14.4. H6 confirmada — GUIA e RELATORIO do mesmo mes_ref têm MESMO valor (é feature)

Hipótese validada em amostragem de 3 pares:
- 12.2025 GUIA = 12.2025 RELATORIO = R$ 10.980,21 ✅
- 12.2025 CONSIGNADO = 12.2025 CONSIGNADO_RELATORIO = R$ 3.620,63 ✅
- 11.2025 GUIA = 11.2025 RELATORIO = R$ 6.644,09 ✅

**Conclusão:** Duplicação aparente nos valores FGTS é **intencional**. GUIA e RELATORIO
são documentos distintos (guia de pagamento vs relatório analítico GFD) que apresentam
o mesmo valor total da guia. NÃO são duplicações a remover. O dashboard deve exibir
ambos com seus tipos distintos.

**Implicação para endpoints:** Endpoint `/valores-fiscais-resumo` agrupa por tipo.
Dashboard que quiser mostrar "valor único pago no mês" deve somar apenas tipo GUIA
(não somar RELATORIO junto, pois duplicaria).

---

## CHANGELOG

| Versão | Data       | Autor      | Mudança                                  |
|--------|------------|------------|------------------------------------------|
| 1.0    | 2026-04-18 | T_CONTRACT | Contrato inicial pós FASE B1             |
| 1.1    | 2026-04-18 | T1_B2      | Seção 10: descobertas T1_B2 (tipos errados, revision ID, env.py sync, PDFs texto nativo) |
| 1.2    | 2026-04-18 | T2_B2      | Seção 11: descobertas T2_B2 (competência PT-BR, barcode 48 dígitos, discriminador DARF vs DAS, dirs misclassificados, fgts_guia vazio) |
| 1.3    | 2026-04-18 | T5_B2      | Seção 6.2: endpoint extrair-valores documentado; Seção 12: descobertas T5 (models stale, padrão sync-executor, idempotência com limite) |
| 1.4    | 2026-04-18 | T_CONTRACT_v1.4 | Seção 13: Princípios de Engenharia GEDEON (Chesterton, Falsificação 3 níveis, Documentar antes de corrigir, Escopo sagrado); REGRA ZERO e seção 7.1 atualizadas |
| 1.5    | 2026-04-18 | T6_B2      | Seção 14: descobertas T6 — caso INSS mes_ref="" investigado (Chesterton), gap serializers corrigido (6→12 campos), endpoint /valores-fiscais-resumo criado, H6 GUIA/RELATORIO confirmada como feature |
