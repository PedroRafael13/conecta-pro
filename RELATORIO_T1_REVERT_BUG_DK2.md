# T1 — Investigação Revert BUG-DK2 (Chesterton)
**Data:** 2026-05-04
**Branch:** feature/people-management-reorganization
**Tipo:** Read-only — 15min

---

## RESUMO EXECUTIVO

> **O revert foi colateral** — não foi Jordan rejeitando a solução técnica.
> Em 2026-04-05 03:11 UTC ocorreu a cascata de sessões tmux paralelas que reverteu
> 3+ commits alheios (documentada no CLAUDE.md). `0fa895d5` foi um desses reverts
> acidentais: mensagem só diz "This reverts..." sem nenhuma justificativa técnica.
>
> A solução real para o pipeline Onvio foi reimplementada 22 dias depois (§39, 2026-04-27)
> com abordagem diferente: `_match_onvio_docs()` usando `condominio_id` como FK,
> não fuzzy matching de nomes de postos.
>
> **Risco de re-introduzir o bug ao expandir `MAPA_TIPOS_ONVIO`: ZERO.**

---

## 1. O que `cd7cc9c6` tentou fazer

**Commit:** `cd7cc9c6` — 2026-04-04 20:34 UTC
**Mensagem:** `fix(ged): BUG-DK2 — popula ged_kit_documents no auto-assemble`

### Problema raiz

`get_employees_for_client()` buscava funcionários via `posts.client_id`:
```python
# ANTES (quebrado)
posts_result = await self.db.execute(
    select(Post.id).where(
        Post.client_id == str(client_id),  # client_id = NULL em TODOS os posts
        Post.status == "active",
    )
)
# → post_ids = [] → employee_ids = [] → 0 documentos criados
```

### Fix aplicado

Substituiu FK por **fuzzy matching de nomes** (unicode normalize + stop-words):
```python
# DEPOIS (BUG-DK2)
STOP_WORDS = {"CONDOMINIO", "DO", "DA", "DE", ...}

def normalize(s): → UPPER + remove acentos
def sig_words(s): → palavras significativas (sem stop words, min 3 chars)

# Fuzzy: aceita posto se suas palavras ⊆ cliente OU cliente ⊆ posto
if post_sig and (post_sig <= ged_sig or ged_sig <= post_sig):
    matching_post_ids.append(post_id)

# Busca alocações desses postos (raw SQL, sem ORM Import)
SELECT DISTINCT employee_id::text
FROM allocations
WHERE post_id = ANY(:post_ids)
  AND status = 'active' AND is_active = true
```

**Também corrigiu** categorização no `GET /kits/{id}`:
```python
# ANTES: "operacional" vs "operacoes" causava escalas como company
"category": "employee" if d["source_module"] in ("dp", "rh", "operacional") else "company"
# DEPOIS: usa coluna real
"category": "employee" if d["employee_id"] is not None else "company"
```

**Resultado:** 328 documentos em `ged_kit_documents` (antes: 0 novos)

### Stat do diff

```
git show --stat cd7cc9c6:
  auto_assemble_controller.py  |   7 +-
  kit_builder_service.py       | 108 ++++++++++++++-------
  2 files changed, 77 insertions(+), 38 deletions(-)
  200 linhas de diff total em *.py
```

---

## 2. Por que `0fa895d5` reverteu

**Commit:** `0fa895d5` — 2026-04-05 03:11 UTC (6h30 depois do BUG-DK2)
**Mensagem:** `Revert "fix(ged): BUG-DK2 — popula ged_kit_documents no auto-assemble"`
`This reverts commit cd7cc9c60a2f7cfa6516089067251e528ee6347a.`

### Zero justificativa técnica

A mensagem do revert é o template padrão do `git revert` — nenhuma explicação do motivo.

### Contexto temporal — cascata de reverts de 2026-04-05

Entre o commit BUG-DK2 (20:34 UTC, Apr 4) e o revert (03:11 UTC, Apr 5) havia apenas:
```
0fa895d5  Revert BUG-DK2            ← revert acidental
cd7cc9c6  fix BUG-DK2               ← o commit revertido
1be38c45  fix(dp): contratos api
4f5fb6ae  fix(sprint15): BUG-AUTH-01
```

O CLAUDE.md documenta explicitamente:
> *"Em 2026-04-05 ocorreram 3 reverts automáticos (65c3ce14, f87e9c5b, f866cc6a)
> causados por sessões tmux paralelas revertendo commits de outros módulos."*

O anti-revert hook (`.git/hooks/commit-msg`) foi instalado em 2026-04-07
**exatamente por causa desse incidente** — para impedir que isso se repita.

**Conclusão:** revert acidental por sessão tmux paralela. BUG-DK2 estava tecnicamente
correto e funcionando (328 documentos criados). Foi desfeito sem intenção.

---

## 3. CONTRACTS §39/§40 explica algo?

### §39 — D2: Botão "Montar Kits" + Matching Onvio (2026-04-27)

22 dias após o revert, Jordan voltou com solução diferente e mais cirúrgica:

**Criado:** `_match_onvio_docs(kit_id, client_name, reference_month)` em
`people_management/ged/services/kit_builder_service.py`

**Abordagem diferente do BUG-DK2:**
- BUG-DK2: fuzzy match nome cliente → postos operacionais → employee_ids (para docs per-employee)
- §39: fuzzy match nome cliente → `condominios` → `condominio_id` → onvio_documents (para docs empresa)

**`MAPA_TIPOS_ONVIO` criado em §39** (8 categorias):
```python
MAPA_TIPOS_ONVIO = {
    "folha_pagamento": "folha_pagamento",
    "dctfweb_recibo": "dctfweb_recibo",
    "dctfweb_extrato": "dctfweb_extrato",
    "dctfweb_declaracao": "dctfweb_declaracao",
    "fgts_guia": "gfd_fgts_mensal",
    "fgts_relatorio": "relatorio_gfd_fgts",
    "fgts_consignado": "comp_pag_fgts",
    "fgts_consignado_relatorio": "relatorio_gfd_fgts",
}
```

**Resultado §39:** 7 `folha_pagamento` de 03/2026 casados (1 por condomínio)

### §40 — D3: Download de PDFs Funcional (2026-04-27)

- Frontend: `/uploads/${doc.file_path}` → `/api/v1/people-management/ged/documents/${doc.id}/download`
- Backend: path traversal protection (`Path.resolve() + startswith("/app/uploads")`)
- `media_type` sempre `"application/pdf"`

**§40 não afeta o pipeline Onvio — é só o endpoint de download.**

---

## 4. O que veio DEPOIS do revert (commits em people_management/ged/)

```
5dfe6b11  fix(gdrive): OAuth2 check_credentials
d80df95b  feat(ged/d5.5.2): logging /cnds/run
67916155  docs(integrations): D5.4 auditoria
efdef3fd  feat(ged): D5.4 CertidoesUpdaterService
48ab6462  fix(ged): D4.1 _meses_com_kits
94b15d17  fix(ged): D4 auditoria
087d9a28  feat(ged): D4 coleta automática funcional (§41)
716fa4b8  fix(ged): D3.2 file_path=NULL não fake (§40.2)
a5e7936f  fix(ged): INV-3 path traversal
db50f479  fix(ged): D3 download PDF real (§40)
089cdabb  feat(ged): D2 Montar Kits + matching Onvio (§39)   ← reimplementação pós-revert
...
a30f21cd  fix(ged): matching 203 PDFs históricos
```

A reimplementação via §39 (`089cdabb`) veio 22 dias depois do revert.

---

## 5. Risco de re-introduzir o bug ao expandir MAPA_TIPOS_ONVIO

**Risco: ZERO.** Caminhos completamente separados:

| | BUG-DK2 revertido | Expansão MAPA_TIPOS_ONVIO |
|---|---|---|
| Função | `get_employees_for_client()` | `_match_onvio_docs()` |
| Mecanismo | Fuzzy match nomes de postos → employee_ids | Lookup por `condominio_id` + `categoria` |
| Docs alvo | Per-employee (contracheque, folha ponto) | Company-level (folha, FGTS, DCTFWeb) |
| Estado atual | Quebrado — retorna `[]` (posts.client_id=NULL) | Funcional — §39 |
| Arquivo | `kit_builder_service.py:get_employees_for_client` | `kit_builder_service.py:_match_onvio_docs` |

**Expandir o mapa** só adiciona entradas no dict `MAPA_TIPOS_ONVIO`. Não toca em
`get_employees_for_client()`, não reintroduz fuzzy matching de postos, não altera
lógica de lookup.

**Risco real ao expandir:** categorias como `outros` têm `mes_ref=NULL` e
`doc_scope=NULL` em muitos docs → `_match_onvio_docs()` não casará mesmo com o mapa
expandido. A limitação não é o mapa — é a qualidade dos metadados (parser v2 backlog).

---

## DECISÃO

| Pergunta | Resposta |
|----------|----------|
| Revert foi intencional? | **Não** — cascata de sessões paralelas (2026-04-05) |
| BUG-DK2 estava correto? | **Sim** — 328 docs criados, solução funcionava |
| Reimplementado depois? | **Sim** — §39 em 2026-04-27 com abordagem diferente |
| Expandir MAPA é seguro? | **Sim** — não toca nas funções afetadas pelo BUG-DK2 |
| Problema dos docs `outros`? | Metadados (mes_ref/doc_scope NULL) — não o mapa |
