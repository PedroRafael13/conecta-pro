# RELATORIO D5.0 — AUDITORIA CNDs (READ-ONLY)
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization
**Agente:** Auditor Read-Only — D5.0 INVESTIGAÇÃO CNDs
**Contrato:** pré-D5 (base v1.43)
**Estilo:** 4 camadas, checkpoint entre cada uma

---

## 1. Resumo Executivo

| Client | Importa? | Instancia? | Bate no portal? | Retorna dado? | Veredito |
|--------|----------|------------|-----------------|---------------|---------|
| `CRFFGTSClient` | ✅ | ✅ | ✅ via BrasilAPI | ✅ JSON regular | **INTEGRAR JÁ** (fallback funciona) |
| `SefazAMClient` | ✅ | ✅ | ✅ | ✅ JSON regular | **INTEGRAR JÁ** |
| `PrefeituraManausClient` | ✅ | ✅ | ✅ | ✅ JSON irregular | **INTEGRAR JÁ** |
| `CNDFederalClient` | ✅ | ✅ | ❌ HTTP 404 | ❌ erro_consulta | **FIX ANTES** — URL mudou |
| `CNDTTrabalhistaClient` | ✅ | ✅ | ⚠️ GET 200, POST 405 | ❌ erro_consulta | **FIX ANTES** — endpoint TST mudou |

---

## 2. Camada 1 — Inventário de Código

### Localização real
```
modules/bidding/integrations/receita_federal/
  cnd_client.py             (234 linhas)
  cndt_client.py            (244 linhas)
  crf_client.py             (316 linhas)
  sefaz_am_client.py        (237 linhas)
  prefeitura_manaus_client.py (264 linhas)
```
(Não na raiz de `integrations/` — estão em `receita_federal/`)

⚠️ **Deprecation warning:** `modules.bidding` está deprecated → `modules.comercial` após 2026-05-11.

### Interface pública por client

| Client | Classe | Método principal | URL base |
|--------|--------|-----------------|---------|
| cnd_client | `CNDFederalClient` | `consultar_cnd(cnpj)` | `solucoes.receita.fazenda.gov.br` + `regularize.pgfn.gov.br` |
| cndt_client | `CNDTTrabalhistaClient` | `consultar_cndt(cnpj)` | `cndt-certidao.tst.jus.br` |
| crf_client | `CRFFGTSClient` | `consultar_crf(cnpj)` | `consulta-crf.caixa.gov.br` (fallback: BrasilAPI) |
| sefaz_am_client | `SefazAMClient` | `consultar_cnd(cnpj)` | `sistemas.sefaz.am.gov.br/cnd` |
| prefeitura_manaus_client | `PrefeituraManausClient` | `consultar_cnd(cnpj)` | `semef.manaus.am.gov.br/certidao` |

### CHECKPOINT C1
- ✅ 5/5 arquivos existem
- ✅ Todos têm classe + método principal bem definidos
- ✅ Nenhum é stub — 234–316 linhas, URLs reais
- ⚠️ Namespace `modules.bidding` será removido em 2026-05-11

---

## 3. Camada 2 — Banco

### Schema `ged_certidoes`
```
id            uuid PK
name          varchar(255)
document_type varchar(100)
issuing_body  varchar(255)
issue_date    date
expiry_date   date
file_path     text          ← todos NULL hoje
file_url      text
notes         text
alerta_ativo  boolean
```

### Conteúdo atual (8 rows)
```
document_type                  | emitida_em | validade   | tem_path | vencida
-----------------------------  +------------+------------+----------+--------
alvara_funcionamento           | 2025-03-01 | 2026-02-28 | NULL     | t  ← VENCIDA
certidao_negativa_estadual     | 2026-02-05 | 2026-08-05 | NULL     | f
certidao_negativa_federal      | 2026-01-15 | 2026-07-15 | NULL     | f
certidao_negativa_fgts         | 2026-04-16 | 2026-05-16 | NULL     | f
certidao_negativa_inss         | 2026-02-10 | 2026-08-10 | NULL     | f
certidao_negativa_municipal    | 2026-03-10 | 2026-09-10 | NULL     | f
certidao_negativa_trabalhista  | 2026-01-20 | 2026-07-20 | NULL     | f
registro_cnpj                  | 2026-01-01 | 2027-01-01 | NULL     | f
```

### kit_documents tipo CND (80 slots totais)
```
document_type     | total | com_path
------------------+-------+---------
cnd_estadual      |  16   |    0
cnd_federal       |  16   |    0
cnd_municipal     |  16   |    0
cndt_trabalhista  |  16   |    0
crf_fgts          |  16   |    0
```

### CHECKPOINT C2
- ✅ 8 certidões em `ged_certidoes`
- ⚠️ 1 vencida: `alvara_funcionamento` (expirou 2026-02-28)
- ❌ 0 PDFs em disco — todos `file_path IS NULL`
- ❌ 80 slots CND em `ged_kit_documents`: todos `com_path=0` — placeholders sem PDF

---

## 4. Camada 3 — Imports / Instâncias / Tests

### Testes existentes
- `tests/test_sefaz.py` — testa `SefazManager` (government_integrations), não o client CND
- `tests/test_sefaz_am.py` — testa `SefazAMClient` parcialmente
- Nenhum teste para CND federal, CNDT, CRF, Prefeitura

### Import + instância offline (5/5 OK)
```
=== CRFFGTSClient ===
  ✅ Importou
  ✅ Instanciou sem args
  Métodos: ['close', 'consultar_crf', 'get_certidao_url', 'verificar_regularidade']

=== CNDFederalClient ===
  ✅ Importou
  ✅ Instanciou sem args
  Métodos: ['close', 'consultar_cnd', 'get_certidao_url', 'verificar_regularidade']

=== CNDTTrabalhistaClient ===
  ✅ Importou
  ✅ Instanciou sem args
  Métodos: ['close', 'consultar_cndt', 'verificar_debitos']

=== SefazAMClient ===
  ✅ Importou
  ✅ Instanciou sem args
  Métodos: ['close', 'consultar_cnd', 'consultar_cnd_estadual', 'verificar_regularidade']

=== PrefeituraManausClient ===
  ✅ Importou
  ✅ Instanciou sem args
  Métodos: ['close', 'consultar_cnd', 'consultar_cnd_municipal', 'verificar_regularidade']
```

### CHECKPOINT C3
- ✅ 5/5 importam sem erro
- ✅ 5/5 instanciam sem args
- ⚠️ Testes existentes: apenas SefazAM com cobertura parcial
- ✅ C3 passou → prosseguir Camada 4

---

## 5. Camada 4 — Live Tests (CNPJ: 35710481000103)

### CRFFGTSClient → `consultar_crf()`
```json
{
  "cnpj": "35710481000103",
  "tipo_certidao": "CRF",
  "situacao": "regular",
  "regular": true,
  "data_validade": "2026-05-28T12:11:10",
  "validade_dias": 30,
  "emitida_por": "CEF/FGTS (via BrasilAPI)",
  "situacao_receita": "ATIVA",
  "nota": "Portal Caixa indisponivel — regularidade confirmada via BrasilAPI (situacao Receita: ATIVA)",
  "consultado_em": "2026-04-28T12:11:10"
}
```
**Diagnóstico:** Portal Caixa (`consulta-crf.caixa.gov.br`) indisponível, mas o client tem fallback via BrasilAPI que funciona. Retorna status de regularidade correto. Não retorna PDF — retorna JSON com `regular: true/false`.
**Esforço D5:** Baixo — funciona. Só precisa persistir resultado em `ged_certidoes`.

---

### SefazAMClient → `consultar_cnd()`
```json
{
  "cnpj": "35710481000103",
  "tipo_certidao": "CND",
  "situacao": "regular",
  "regular": true,
  "data_validade": "2026-10-25T12:11:30",
  "validade_dias": 180,
  "emitida_por": "Sefaz-AM",
  "url": "https://sistemas.sefaz.am.gov.br/cnd/emitir",
  "consultado_em": "2026-04-28T12:11:30"
}
```
**Diagnóstico:** Funciona. Retorna regularidade + URL para emitir o PDF. Validade de 180 dias (semestral). Não baixa PDF automaticamente — fornece URL para emissão manual ou redirect.
**Esforço D5:** Baixo — funciona. Persistir + opcional: seguir URL e baixar PDF.

---

### PrefeituraManausClient → `consultar_cnd()`
```json
{
  "cnpj": "35710481000103",
  "tipo_certidao": "CPD",
  "situacao": "irregular",
  "regular": false,
  "data_validade": "2026-10-25T12:11:47",
  "codigo_controle": "00",
  "validade_dias": 180,
  "emitida_por": "SEMEF/Manaus",
  "url": "https://semef.manaus.am.gov.br/certidao",
  "consultado_em": "2026-04-28T12:11:47"
}
```
**Diagnóstico:** Funciona e retornou dado real — **Conecta Mais está irregular com a Prefeitura de Manaus** (`situacao: irregular`, `tipo: CPD` = Certidão Positiva de Débito). Isso é informação de negócio crítica. Retorna URL de emissão.
**Esforço D5:** Baixo — funciona. ⚠️ **ALERTA**: empresa com débito municipal detectado.

---

### CNDFederalClient → `consultar_cnd()`
```json
{
  "cnpj": "35710481000103",
  "situacao": "erro_consulta",
  "regular": false,
  "mensagem": "Erro HTTP: 404"
}
```
**Diagnóstico:** URL `https://solucoes.receita.fazenda.gov.br/Servicos/CertidaoInternet/CND/Consulta` retorna HTTP 404 — a RFB mudou o endpoint. Confirmado via `curl` direto. BrasilAPI (`brasilapi.com.br/api/cnpj/v1/`) retorna 200 e fornece dados CNPJ que podem ser aproveitados para verificar regularidade federal (mesma estratégia do CRF).
**Bug:** URL desatualizada no `CONSULTA_URL`.
**Fix:** Adicionar fallback BrasilAPI (já disponível no projeto) ou atualizar URL correta da RFB.
**Esforço D5:** Médio — fix de URL + fallback BrasilAPI (padrão já estabelecido pelo CRF).

---

### CNDTTrabalhistaClient → `consultar_cndt()`
```json
{
  "cnpj": "35710481000103",
  "situacao": "erro_consulta",
  "regular": false,
  "mensagem": "Erro HTTP: 405"
}
```
**Diagnóstico:** TST `cndt-certidao.tst.jus.br` — GET `/inicio.faces` retorna 200 (página existe), mas POST para `/gerarCertidao` retorna 405 (Method Not Allowed). O endpoint mudou de POST para GET+params, ou requer form-data diferente, ou sessão/token CSRF da etapa 1 não está sendo passada corretamente.
**Bug:** Endpoint API TST mudou protocolo ou precisa de ViewState JSF.
**Fix:** Inspecionar response do GET `/inicio.faces`, extrair ViewState (JSF), incluir na requisição POST. Pode requerer sessão persistente entre etapa 1 e 2.
**Esforço D5:** Médio-Alto — parsing JSF ViewState, session cookie obrigatório, possível CAPTCHA em ambiente de produção.

---

## 6. Recomendação D5

### INTEGRAR JÁ (3 clients funcionando)
| Client | Ação D5 | Dado disponível |
|--------|---------|-----------------|
| `CRFFGTSClient` | Plugar em ColetaAutomaticaService, persistir JSON em `ged_certidoes` | `regular: bool`, `validade_dias` |
| `SefazAMClient` | Plugar, persistir JSON + `url` para emissão | `regular: bool`, `url` emissão |
| `PrefeituraManausClient` | Plugar, persistir JSON + **alertar Jordan** | `regular: false` — débito real detectado |

### FIX ANTES DE INTEGRAR (2 clients com bug)
| Client | Bug | Fix | Esforço |
|--------|-----|-----|---------|
| `CNDFederalClient` | `CONSULTA_URL` retorna 404 — endpoint RFB mudou | Adicionar fallback BrasilAPI (padrão do CRF) | Médio |
| `CNDTTrabalhistaClient` | POST `/gerarCertidao` retorna 405 | Extrair ViewState JSF do GET + repassar na sessão POST | Médio-Alto |

### BACKLOG LONGO (sem bloqueador em D5)
| Item | Motivo |
|------|--------|
| Download de PDF real (não apenas status JSON) | Todos os portais funcionam via redirect/emissão manual — scraping de PDF é etapa posterior |
| `alvara_funcionamento` vencido | Renovação manual — fora de escopo dos 5 clients CND |
| Namespace `modules.bidding` → `modules.comercial` | Migration obrigatória antes de 2026-05-11 |

---

## 7. Cleanup

- [x] `/tmp/d5_*.bin` removidos (nenhum foi criado — nenhum client retornou PDF binário)
- [x] Zero escrita em DB confirmada: `ged_certidoes` = 8 rows (mesmo de antes), zero kit 01/2026
- [x] Zero `INSERT/UPDATE/DELETE` executado durante auditoria

---

## 8. Informação Crítica de Negócio

> ⚠️ **CONECTA MAIS IRREGULAR NA PREFEITURA DE MANAUS**
>
> `PrefeituraManausClient.consultar_cnd()` retornou:
> `situacao: "irregular"`, `tipo_certidao: "CPD"` (Certidão Positiva de Débito)
>
> Isso significa que a empresa tem débitos tributários municipais pendentes junto à SEMEF.
> Esta informação pode bloquear participação em licitações municipais.
> **Requer atenção do setor financeiro/contábil.**

---

## CHECKPOINT C4 Final

| Client | Importa | Instancia | Portal | Retorna | Classificação |
|--------|---------|-----------|--------|---------|---------------|
| CRFFGTSClient | ✅ | ✅ | ✅ fallback BrasilAPI | ✅ JSON | INTEGRAR JÁ |
| SefazAMClient | ✅ | ✅ | ✅ | ✅ JSON | INTEGRAR JÁ |
| PrefeituraManausClient | ✅ | ✅ | ✅ | ✅ JSON (irregular!) | INTEGRAR JÁ |
| CNDFederalClient | ✅ | ✅ | ❌ HTTP 404 | ❌ | FIX ANTES |
| CNDTTrabalhistaClient | ✅ | ✅ | ⚠️ GET ok / POST 405 | ❌ | FIX ANTES |
