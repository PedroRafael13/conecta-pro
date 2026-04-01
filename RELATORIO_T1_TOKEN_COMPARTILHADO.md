# Relatório T1 — Token Compartilhado & Rate Limit Fix

**Data:** 01/04/2026
**Branch:** `feature/people-management-reorganization`
**Commit:** `21fa4eef`
**Responsável:** Jordan Jesus / Claude Sonnet 4.6

---

## Resumo Executivo

Refatoração do sistema de agentes autônomos para eliminar o gargalo de rate limit
que causava score `0.6/10` no ciclo de monitoramento. A causa raiz era que cada um
dos 19 agentes fazia um login individual no backend, excedendo o limite de 5 req/janela
do endpoint `/api/v1/auth/login`.

**Resultado:** `12/12` agentes rodando com token OK. Zero bloqueados por rate limit.

---

## Checklist dos 5 Passos

| Passo | Descrição | Status |
|-------|-----------|--------|
| SETUP | Token + Container obtidos | ✅ |
| PASSO 1 | Git push commits T3 pendentes | ✅ já sincronizado |
| PASSO 2 | Refatorar `BaseAgent` — aceitar token externo | ✅ |
| PASSO 3 | Refatorar `BaseOrchestrator` — token compartilhado | ✅ |
| PASSO 4 | Validar imports e sintaxe | ✅ todos os testes OK |
| PASSO 5 | Commit `21fa4eef` + push | ✅ |

---

## Mudanças Implementadas

### `agents/core/base_agent.py`

**Antes:**
```python
def __init__(self):
    self.token: Optional[str] = None
    ...

def obter_token(self) -> str:
    # sempre fazia login no backend
    r = subprocess.run(['curl', ..., '/auth/login'], ...)
    self.token = json.loads(r.stdout).get('access_token', '')
    return self.token

# Em executar():
self.obter_token()  # login individual por agente
```

**Depois:**
```python
def __init__(self, token: str = None):
    self.token: Optional[str] = token  # injetado pelo orquestrador
    ...

def obter_token(self) -> str:
    """Retorna token atual ou obtém um novo (fallback)."""
    if self.token:
        return self.token
    return self._obter_token_proprio()

def _obter_token_proprio(self) -> str:
    """Login no backend — usado apenas como fallback."""
    r = subprocess.run(['curl', ..., '/auth/login'], ...)
    self.token = json.loads(r.stdout).get('access_token', '')
    return self.token

# Em executar():
if not self.token:
    self._obter_token_proprio()  # só chama se não foi injetado
```

### `agents/core/base_orchestrator.py`

**Antes:**
```python
def executar(self) -> dict:
    scores = []
    for AgenteClass in self.AGENTES:
        agente = AgenteClass()          # sem token
        resultado = agente.executar()   # cada um fazia login
```

**Depois:**
```python
def _obter_token_compartilhado(self) -> str:
    """Obtém token JWT único — compartilhado com todos os agentes do módulo."""
    r = subprocess.run(['curl', ..., '/auth/login'], ...)
    token = json.loads(r.stdout).get('access_token', '')
    if token:
        logger.info(f"[{self.MODULO}] Token compartilhado obtido")
    return token

def executar(self) -> dict:
    # Token único obtido UMA VEZ — injetado em todos os agentes
    token_compartilhado = self._obter_token_compartilhado()

    scores = []
    for AgenteClass in self.AGENTES:
        agente = AgenteClass(token=token_compartilhado)  # token injetado
        resultado = agente.executar()                    # zero logins extras
```

---

## Impacto no Rate Limit

| Métrica | Antes | Depois |
|---------|-------|--------|
| Logins por ciclo de módulo (12 agentes) | 12 | **1** |
| Logins por ciclo completo (19 agentes, 2 módulos) | 19 | **2** |
| Agentes bloqueados (limite: 5 req/janela) | 14/19 | **0** |
| Score geral ciclo #1 | 0.6/10 | — |
| Score módulo financeiro com fix | — | **1.9/10** |
| Agentes financeiro com token OK | 5/12 | **12/12** |

> **Nota:** O score `1.9/10` no financeiro reflete bugs reais nos endpoints
> (422 em `/payables`, `/receivables`, `/cashflow/dashboard` por falta de query params
> obrigatórios). Esses são os próximos itens de correção — não são mais rate limit.

---

## Resultado dos Testes (PASSO 4)

```
✅ PASSO 2 — BaseAgent aceita token externo
✅ PASSO 2 — fallback None preservado
✅ PASSO 3 — _obter_token_compartilhado presente
✅ PASSO 3 — executar assinatura: (self) -> dict
✅ PASSO 4 — TODOS OS TESTES PASSARAM
```

**Teste de integração (módulo financeiro real):**
```
Score financeiro: 1.9/10
Agentes OK: 12/12
Token bloqueados por rate limit: 0
Tempo: 5.3s

  dashboard:            3.3/10  ← 1/3 endpoints OK
  contratos:           10.0/10  ✅
  contas_pagar:         0.0/10  ← 422 (query params)
  contas_receber:       0.0/10  ← 422 (query params)
  fluxo_caixa:          0.0/10  ← 422 + 404
  conciliacao_bancaria: 0.0/10  ← próximo fix
  boletos_cobr:         0.0/10  ← próximo fix
  fornecedores:         0.0/10  ← próximo fix
  contabilidade:       10.0/10  ✅
  faturamento:          0.0/10  ← próximo fix
  precificacao:         0.0/10  ← próximo fix
  relatorios_fin:       0.0/10  ← próximo fix
```

---

## Commit

```
commit 21fa4eef
feat(agents/core): token compartilhado — elimina rate limit no ciclo 24h

- BaseAgent.__init__ aceita token externo (token: str = None)
- BaseAgent.obter_token() retorna token existente sem novo login
- BaseAgent._obter_token_proprio() faz login apenas como fallback
- BaseOrchestrator._obter_token_compartilhado() obtém 1 token por ciclo
- BaseOrchestrator.executar() injeta token em todos os agentes via AgenteClass(token=...)
- Resolve score 0.6/10 causado por 14/19 agentes bloqueados por rate limit (5 req/janela)
- Validado: 12/12 agentes financeiro com token OK — 0 bloqueados

 2 files changed, 35 insertions(+), 5 deletions(-)
```

---

## Próximos Passos (T2)

Os endpoints com `0.0/10` no módulo financeiro têm bugs reais a corrigir:

1. **`/financial/payables`** — retorna 422: falta `company_id` ou parâmetro de filtro
2. **`/financial/receivables`** — retorna 422: mesmo problema
3. **`/financial/cashflow/dashboard`** — retorna 422: parâmetros de período obrigatórios
4. **`/financial/bi/revenue`** e **`/financial/bi/cashflow`** — retornam 404: endpoints não existem

**Estratégia:** Ajustar os `ENDPOINTS` de cada agente para incluir os query params
obrigatórios, ou criar payloads de teste que satisfaçam as validações do backend.

---

## Como Baixar este Relatório

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T1_TOKEN_COMPARTILHADO.md ~/Downloads/
```

---

*Gerado por Claude Sonnet 4.6 — Conecta PRO Monitor System*
