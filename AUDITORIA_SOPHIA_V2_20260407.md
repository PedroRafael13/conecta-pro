# AUDITORIA — SOPHIA v2.0 | Commit `0375fbd4`
**Data:** 2026-04-07
**Auditor:** Claude Sonnet 4.6
**Missão:** Verificar se o commit `0375fbd4` implementou 100% do prompt enviado
**Metodologia:** Verificação ao vivo — container, banco, endpoints, código

---

## RESULTADO GERAL

| Categoria | Score |
|-----------|-------|
| Código (38 itens) | **36/38 (95%)** ⚠️ |
| Banco (colunas + índices) | **8/8 (100%)** ✅ |
| Container (import + métodos) | **8/8 (100%)** ✅ |
| Endpoints (6) | **6/6 (100%)** ✅ |
| Event Bus Subscriber (arquivo) | **✅ existe** |
| Event Bus Subscriber (integração) | **❌ não wired** |

**Veredicto: 97% implementado — 2 gaps de código + 1 gap de integração**

---

## AUDITORIA 1 — CÓDIGO

**Arquivo:** `backend/modules/gedeon/agents/sophia.py`
**Linhas:** 1.145 | **Tamanho:** 39.278 chars

### Itens do prompt ✅ implementados (36/38):

| Item | Status |
|------|--------|
| versão 2.0 declarada | ✅ |
| módulo dp | ✅ |
| módulo rh | ✅ |
| módulo ged | ✅ |
| módulo operacional | ✅ |
| módulo fiscal | ✅ |
| módulo contratos | ✅ |
| módulo licitacoes | ✅ |
| módulo financeiro | ✅ |
| `MODULOS_ESCOPO` dict | ✅ |
| `TERMOS_MODULOS` dict | ✅ |
| `EMBEDDING_DIM = 1536` | ✅ |
| `def _texto_para_vetor` | ✅ |
| `def _similaridade_coseno` | ✅ |
| `def _gerar_embedding` | ✅ |
| fallback `sophia_dense_1536` | ✅ |
| `class Sophia` | ✅ |
| `def _inicializar` | ✅ |
| `def _detectar_modulo` | ✅ |
| `def indexar_documento` | ✅ |
| `def buscar` | ✅ |
| `def perguntar` | ✅ |
| `def buscar_impacto_folha` | ✅ |
| `def alertas_vencimento` | ✅ |
| `def reindexar_acervo` | ✅ |
| `def indexar_acervo_completo` | ✅ |
| `def status` | ✅ |
| filtro `impacto_folha` | ✅ |
| filtro `vencendo_em_dias` | ✅ |
| filtro `modulos` (lista) | ✅ |
| coluna `modulo` no INSERT | ✅ |
| coluna `vencimento` no INSERT | ✅ |
| coluna `impacto_folha` no INSERT | ✅ |
| `sophia = Sophia()` singleton | ✅ |
| backup `sophia_v1_backup.py` | ✅ |
| Anthropic client `_get_client` | ✅ |

### ❌ Gaps de código (2/38):

#### GAP-01 — `TIPOS_POR_MODULO` ausente
O prompt exigia explicitamente este dicionário:
```python
TIPOS_POR_MODULO = {
    "dp": ["holerite","contrato_trabalho","rescisao",...],
    "rh": ["avaliacao_desempenho","treinamento",...],
    ...
}
```
**O que foi implementado:** apenas `TERMOS_MODULOS` (termos de busca) e `MODULOS_ESCOPO` (metadados dos módulos). O dict `TIPOS_POR_MODULO` não existe no arquivo.
**Impacto:** baixo — os tipos são usados indiretamente via metadados. Não quebra nenhuma funcionalidade.

#### GAP-02 — `SIMILARITY_THRESH` ausente como constante global
O prompt especificava:
```python
SIMILARITY_THRESH = 0.60
```
**O que foi implementado:** threshold hardcoded na assinatura dos métodos:
```python
def buscar(self, query, top_k=10, filtros=None, threshold=0.30):
```
E no `perguntar`: `threshold=0.25` / `threshold=0.20`.
**Impacto:** funcional mas não segue o padrão do prompt. O threshold padrão (0.30) também é diferente do 0.60 especificado — mais permissivo, o que gera mais resultados mas com menor precisão.

---

## AUDITORIA 2 — BANCO

### Colunas `gedeon_document_index`:

| Coluna | Tipo | Status |
|--------|------|--------|
| `embedding_anthropic` | ARRAY (FLOAT8[]) | ✅ |
| `embedding_model` | VARCHAR(100) | ✅ |
| `embedding_dim` | INTEGER | ✅ |
| `modulo` | VARCHAR(50) | ✅ |
| `submodulo` | VARCHAR(100) | ✅ |
| `funcionario_id` | UUID | ✅ |
| `vencimento` | DATE | ✅ |
| `impacto_folha` | BOOLEAN | ✅ |

### Índices criados:

| Índice | Status |
|--------|--------|
| `idx_gdi_modulo` | ✅ |
| `idx_gdi_funcionario` | ✅ |
| `idx_gdi_vencimento` | ✅ |
| `idx_gdi_impacto_folha` | ✅ |
| `idx_gdi_embedding_model` | ✅ |

### Distribuição atual do acervo:

| Módulo | Docs | Com embedding Anthropic |
|--------|------|------------------------|
| dp | 270 | 152 |
| operacoes | 48 | 48 |
| fiscal | 41 | 41 |
| rh | 16 | 16 |
| ged | 9 | 9 |
| operacional | 2 | 2 |
| financeiro | 1 | 1 |
| contratos | 1 | 1 |
| licitacoes | 1 | 1 |
| **Total** | **389** | **271** |

**Obs:** 118 docs ainda com motor `tfidf_sklearn` (111 dims) — precisam ser reindexados com `POST /sophia/reindexar`.

---

## AUDITORIA 3 — CONTAINER E MÉTODOS

Verificação ao vivo `docker exec conecta-pro-backend`:

| Teste | Resultado |
|-------|-----------|
| `from modules.gedeon.agents.sophia import sophia` | ✅ importa sem erro |
| `sophia.status()['versao']` | `"2.0"` ✅ |
| `sophia.status()['motor_ativo']` | `"anthropic_haiku_1536"` ✅ |
| `sophia.status()['usando_anthropic']` | `True` ✅ (API Key ativa) |
| `sophia.status()['dimensao_embedding']` | `1536` ✅ |
| `sophia.status()['modulos_escopo']` | `8 módulos` ✅ |
| `sophia.indexar_documento(...)` | `True` ✅ |
| `sophia.buscar("holerite março")` | `3 resultados, score 0.6085` ✅ |
| `sophia._detectar_modulo("holerite salário")` | `"dp"` ✅ |
| `sophia._detectar_modulo("edital pregão")` | `"licitacoes"` ✅ |
| `sophia._detectar_modulo("certidão CND")` | `"ged"` ✅ |
| `sophia.alertas_vencimento(90)` | `3 docs` ✅ |
| `sophia.buscar_impacto_folha("2026-03")` | `1 doc` ✅ |
| `sophia.perguntar("Tem holerite de março?")` | `docs_usados=8, confiança=0.391` ✅ |
| `sophia.reindexar_acervo(5)` | `reindexados=5, modelo=anthropic_haiku_1536` ✅ |

---

## AUDITORIA 4 — ENDPOINTS

Verificação ao vivo com `curl + Bearer token`:

| Endpoint | Método | HTTP | Status |
|----------|--------|------|--------|
| `/api/v1/gedeon/sophia/status` | GET | 200 | ✅ |
| `/api/v1/gedeon/sophia/buscar?q=holerite` | GET | 200 | ✅ |
| `/api/v1/gedeon/sophia/alertas` | GET | 200 | ✅ |
| `/api/v1/gedeon/sophia/impacto-folha?competencia=2026-03` | GET | 200 | ✅ |
| `/api/v1/gedeon/sophia/perguntar` | POST | 200 | ✅ |
| `/api/v1/gedeon/sophia/reindexar?batch_size=5` | POST | 200 | ✅ |

---

## AUDITORIA 5 — EVENT BUS SUBSCRIBER

### O que foi implementado:
- **Arquivo criado:** `backend/modules/gedeon/subscribers/sophia_subscriber.py` (276 linhas)
- **Mapeamento de módulos:** todos os 8 módulos mapeados via prefixos de evento
- **Padrões de eventos:** 15+ prefixos (`dp.*`, `rh.*`, `ged.*`, `operacional.*`, `fiscal.*`, `contratos.*`, `licitacoes.*`, `financeiro.*`, `gp.funcionario.*`, etc.)
- **Função `registrar_subscriber(event_bus)`:** implementada na linha 231

### ❌ GAP-03 — Subscriber NÃO conectado ao startup (gedeon.py)

O arquivo `sophia_subscriber.py` existe mas **não está importado nem chamado** em nenhum ponto do sistema:

```bash
grep "sophia_subscriber" gedeon.py → (nenhum resultado)
grep "sophia_subscriber" main_production.py → (nenhum resultado)
```

**Impacto:** O subscriber existe mas nunca é registrado no Event Bus. Eventos publicados pelos módulos **não chegam ao SOPHIA**. A indexação automática via eventos **não funciona em produção**.

**O que o prompt exigia:**
```python
# gedeon.py — registrar_subscribers()
from modules.gedeon.subscribers.sophia_subscriber import registrar_subscriber
registrar_subscriber(event_bus)
```

**Obs:** O prompt dizia "Conectar Event Bus ao SOPHIA" — o arquivo foi criado mas a conexão ao bus não foi feita.

---

## RESUMO DOS GAPS

| # | Gap | Severidade | Impacto |
|---|-----|-----------|---------|
| GAP-01 | `TIPOS_POR_MODULO` dict ausente no sophia.py | baixa | Nenhum — funcional sem ele |
| GAP-02 | `SIMILARITY_THRESH = 0.60` ausente como constante | baixa | Threshold padrão é 0.30 (mais permissivo que o especificado) |
| GAP-03 | `sophia_subscriber` não conectado ao Event Bus (gedeon.py) | **média** | Indexação automática via eventos não funciona |

---

## O QUE FUNCIONA 100%

- Motor de busca semântica com 1536 dims ✅
- Anthropic API ativa (claude-3-haiku-20240307) ✅
- Fallback automático dense 1536 ✅
- 8 módulos no escopo ✅
- Todos os 6 endpoints respondendo 200 ✅
- Indexação manual via `indexar_documento` ✅
- Busca com filtros cruzados ✅
- Detecção automática de módulo ✅
- Alertas de vencimento ✅
- Busca de impacto folha ✅
- Perguntas em linguagem natural ✅
- Reindexação de acervo legado ✅
- Banco com 8 colunas novas + 5 índices ✅
- Backup da v1 preservado ✅

---

## RECOMENDAÇÃO

**SOPHIA v2.0 está operacional** para uso direto via API.
O único gap funcional é o GAP-03 (subscriber não registrado) — indexação automática via Event Bus não ativa.

Para 100%: adicionar em `gedeon.py` no método `registrar_subscribers()`:
```python
from modules.gedeon.subscribers.sophia_subscriber import registrar_subscriber
registrar_subscriber(event_bus)
```

---

*Auditoria realizada em 2026-04-07 por Claude Sonnet 4.6*
*Verificação ao vivo: container, banco, endpoints e código*
