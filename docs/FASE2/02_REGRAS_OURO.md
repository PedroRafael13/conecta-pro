# REGRAS DE OURO - INEGOCIAVEIS
## ERP CONECTA MAIS - FASE 2

**Versao:** 2.0
**Status:** OBRIGATORIO
**Violacao:** BLOQUEANTE (sprint nao pode ser finalizado)

---

## REGRA 1: QUALIDADE DE CODIGO 100/100

### 1.1 Pylint Score
```
MINIMO ACEITAVEL: 99/100
META: 100/100

NUNCA aceitar sprint com score < 99
NUNCA desabilitar regras do Pylint sem justificativa
SEMPRE corrigir warnings, nao ignorar
```

### 1.2 Como Garantir
```bash
# Rodar ANTES de cada commit
pylint --rcfile=.pylintrc backend/

# Se score < 100, corrigir ANTES de continuar
# Documentar qualquer disable com justificativa

# Exemplo de disable aceitavel:
# pylint: disable=too-few-public-methods  # DTO simples
```

### 1.3 Regras Especificas
```python
# SEMPRE usar type hints
def calculate_price(value: Decimal, tax_rate: Decimal) -> Decimal:
    pass

# SEMPRE docstrings em funcoes publicas
def process_payment(payment_id: UUID) -> PaymentResult:
    """
    Processa pagamento e retorna resultado.

    Args:
        payment_id: ID unico do pagamento

    Returns:
        PaymentResult com status e detalhes

    Raises:
        PaymentError: Se pagamento falhar
    """
    pass

# NUNCA usar Any sem justificativa
# NUNCA ignorar excecoes silenciosamente
# SEMPRE logar erros com contexto
```

---

## REGRA 2: AUDITOR DE CODIGO SEMPRE ATIVO

### 2.1 Execucao Obrigatoria
```
QUANDO: Antes de cada commit
QUANDO: Apos cada merge
QUANDO: Antes de deploy
QUANDO: Review de PR
```

### 2.2 Comando do Auditor
```bash
# Script de auditoria completa
cd /opt/erp-conecta-mais/backend
source venv/bin/activate

# 1. Pylint
echo "=== PYLINT ==="
pylint --rcfile=.pylintrc modules/ core/ tests/
# Deve ser >= 99/100

# 2. Type checking
echo "=== MYPY ==="
mypy modules/ core/ --ignore-missing-imports
# Deve ter 0 errors

# 3. Formatacao
echo "=== BLACK ==="
black --check modules/ core/
# Deve passar sem changes

# 4. Import sorting
echo "=== ISORT ==="
isort --check-only modules/ core/
# Deve passar

# 5. Seguranca
echo "=== BANDIT ==="
bandit -r modules/ core/ -ll
# Deve ter 0 high/critical

# 6. Testes
echo "=== PYTEST ==="
pytest tests/ -v --cov=modules --cov-report=term-missing
# Cobertura >= 85%
```

### 2.3 Bloqueio de Deploy
```
SE auditor falhar:
  - Deploy BLOQUEADO
  - Sprint NAO pode ser marcado como concluido
  - Corrigir ANTES de qualquer outra atividade
```

---

## REGRA 3: OPUS 4.5 EXCLUSIVO

### 3.1 Modelo Obrigatorio
```
UNICO MODELO PERMITIDO: claude-opus-4-5-20251101
ALIAS: Claude Opus 4.5

NUNCA usar:
- Claude Sonnet
- Claude Haiku
- GPT-4
- Gemini
- Qualquer outro modelo
```

### 3.2 Justificativa
```
Por que Opus 4.5 exclusivo:
1. Qualidade superior de codigo
2. Entendimento profundo de contexto
3. Consistencia entre sprints
4. Melhor raciocinio para arquitetura
5. Menos erros, menos retrabalho
```

### 3.3 Configuracao Claude Code
```json
{
  "model": "claude-opus-4-5-20251101",
  "temperature": 0,
  "max_tokens": 8192,
  "language": "pt-BR"
}
```

---

## REGRA 4: SPRINTS MAXIMOS 2 SEMANAS

### 4.1 Timeboxing Rigoroso
```
DURACAO MAXIMA: 2 semanas (10 dias uteis)
SE MAIOR: Dividir em sprints menores
NUNCA: Estender prazo para "terminar tudo"
```

### 4.2 Se Sprint Estourar
```
DIA 10 - Sprint deveria terminar:

CENARIO A: 90% concluido
  -> Terminar o que falta em mais 2 dias
  -> Documentar razao do atraso
  -> Post-mortem para evitar recorrencia

CENARIO B: 70% concluido
  -> PARAR desenvolvimento
  -> O que nao cabe, vira proximo sprint
  -> Entregar o que esta pronto
  -> Revisar estimativas

CENARIO C: < 50% concluido
  -> PARAR imediatamente
  -> Reuniao de crise
  -> Re-planejar completamente
  -> Identificar o que deu errado
```

### 4.3 Divisao de Sprints Grandes
```
SPRINT GRANDE (4 semanas estimadas):
  -> Sprint A: Semanas 1-2 (core features)
  -> Sprint B: Semanas 3-4 (features adicionais)

CADA SPRINT:
  -> Deve entregar valor sozinho
  -> Pode ir para producao independente
  -> Definition of Done completo
```

---

## REGRA 5: NUNCA DEPLOY NA SEXTA

### 5.1 Janela de Deploy
```
PERMITIDO: Segunda a Quinta, 9h-15h
PROIBIDO: Sexta, Sabado, Domingo
PROIBIDO: Vespera de feriado
PROIBIDO: Apos 17h qualquer dia
```

### 5.2 Justificativa
```
Deploy sexta = problema no final de semana
  -> Equipe indisponivel
  -> Cliente irritado
  -> Debug sob pressao
  -> Decisoes ruins

Deploy cedo na semana = tempo para corrigir
  -> Equipe presente
  -> Tempo para rollback
  -> Cliente atendido
  -> Decisoes calmas
```

### 5.3 Excecoes (RARAS)
```
PERMITIDO deploy emergencial se:
  1. Bug critico em producao (sistema down)
  2. Seguranca (vazamento ativo)
  3. Aprovacao explicita do Jordan
  4. Equipe de plantao disponivel

MESMO ASSIM:
  -> Rollback preparado
  -> Monitoramento ativo
  -> Comunicacao com usuarios
```

---

## REGRA 6: DECIMAL PARA DINHEIRO

### 6.1 Nunca Float para Valores Monetarios
```python
# ERRADO - NUNCA fazer isso
price = 19.99  # float tem precisao ruim
total = price * 3  # 59.97000000000001 (!)

# CORRETO - SEMPRE assim
from decimal import Decimal
price = Decimal("19.99")
total = price * 3  # Decimal("59.97") exato!
```

### 6.2 Padrao no Sistema
```python
# Models SQLAlchemy
from sqlalchemy import Numeric

class Proposal(Base):
    # SEMPRE Numeric para dinheiro
    total_value = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=Decimal("0.00"))

# Schemas Pydantic
from decimal import Decimal
from pydantic import Field

class ProposalSchema(BaseModel):
    total_value: Decimal = Field(..., ge=0, decimal_places=2)

# Operacoes
from decimal import Decimal, ROUND_HALF_UP

def calculate_tax(value: Decimal, rate: Decimal) -> Decimal:
    """Calcula imposto com arredondamento correto."""
    return (value * rate).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
```

### 6.3 Validacao
```python
# Em TODOS os testes financeiros
def test_financial_precision():
    """Valida que calculos financeiros sao precisos."""
    # Caso classico que float erra
    price = Decimal("0.1")
    total = sum([price] * 10)
    assert total == Decimal("1.0")  # float daria 0.99999...
```

---

## REGRA 7: TESTES ANTES DE MERGE

### 7.1 Pipeline Obrigatorio
```
ANTES de qualquer merge para main:

1. Todos os testes devem passar (100% green)
2. Cobertura >= 85%
3. Pylint >= 99/100
4. Mypy sem errors
5. Black formatado
6. Isort ordenado

SE QUALQUER FALHAR:
  -> Merge BLOQUEADO
  -> Corrigir antes de continuar
```

### 7.2 Tipos de Testes Exigidos
```python
# 1. TESTES UNITARIOS (obrigatorio)
def test_calculate_proposal_value():
    """Testa calculo isolado."""
    result = calculate_value(Decimal("1000"), Decimal("0.10"))
    assert result == Decimal("1100.00")

# 2. TESTES DE INTEGRACAO (fluxos criticos)
async def test_create_proposal_flow():
    """Testa fluxo completo de criacao."""
    async with AsyncClient(app=app) as client:
        response = await client.post("/api/v1/proposals/", json={...})
        assert response.status_code == 201

# 3. TESTES DE API (endpoints)
async def test_get_proposal_not_found():
    """Testa erro 404."""
    response = await client.get("/api/v1/proposals/uuid-invalido")
    assert response.status_code == 404
```

---

## REGRA 8: COMMITS SEMANTICOS

### 8.1 Formato Obrigatorio
```
tipo: descricao curta em portugues

[corpo opcional com mais detalhes]

[footer opcional com referencias]
```

### 8.2 Tipos Permitidos
```
feat:     Nova funcionalidade
fix:      Correcao de bug
refactor: Refatoracao sem mudanca de comportamento
docs:     Apenas documentacao
test:     Apenas testes
chore:    Manutencao (deps, configs)
style:    Formatacao (sem mudanca de codigo)
perf:     Melhoria de performance
```

### 8.3 Exemplos
```bash
# BOM
git commit -m "feat: adiciona calculo de CCT no pricing engine"
git commit -m "fix: corrige arredondamento de impostos para 2 casas"
git commit -m "refactor: extrai validacao de CNPJ para servico separado"

# RUIM
git commit -m "updates"
git commit -m "fix bug"
git commit -m "WIP"
```

---

## REGRA 9: DOCUMENTACAO OBRIGATORIA

### 9.1 O Que Documentar
```
1. TODA funcao publica: docstring completa
2. TODA classe: docstring com proposito
3. TODO modulo: README.md no diretorio
4. TODA API: endpoint documentado (OpenAPI)
5. TODO schema: campos com descricao
```

### 9.2 Template Docstring
```python
def process_proposal(
    proposal_id: UUID,
    user_id: UUID,
    action: ProposalAction
) -> ProposalResult:
    """
    Processa uma proposta executando a acao solicitada.

    Este metodo valida a proposta, verifica permissoes do usuario,
    executa a acao e registra o historico.

    Args:
        proposal_id: ID unico da proposta
        user_id: ID do usuario executando a acao
        action: Acao a ser executada (APPROVE, REJECT, etc)

    Returns:
        ProposalResult contendo:
        - success: bool indicando sucesso
        - proposal: Proposta atualizada
        - message: Mensagem descritiva

    Raises:
        ProposalNotFoundError: Se proposta nao existe
        PermissionDeniedError: Se usuario sem permissao
        InvalidActionError: Se acao invalida para estado atual

    Example:
        >>> result = process_proposal(
        ...     proposal_id=UUID("..."),
        ...     user_id=UUID("..."),
        ...     action=ProposalAction.APPROVE
        ... )
        >>> print(result.success)
        True
    """
    pass
```

---

## REGRA 10: LOGS ESTRUTURADOS

### 10.1 Padrao de Logging
```python
from core.logging import logger

# SEMPRE usar logger estruturado
logger.info(
    "Proposta criada com sucesso",
    extra={
        "proposal_id": str(proposal.id),
        "client_id": str(proposal.client_id),
        "value": str(proposal.total_value),
        "user_id": str(current_user.id)
    }
)

# NUNCA usar print()
# print("debug aqui")  # ERRADO!

# NUNCA logar dados sensiveis
# logger.info(f"CPF: {cpf}")  # ERRADO! LGPD!
```

### 10.2 Niveis de Log
```python
# DEBUG: Desenvolvimento apenas
logger.debug("Entrando no metodo X", extra={...})

# INFO: Eventos normais de negocio
logger.info("Proposta aprovada", extra={...})

# WARNING: Algo estranho mas nao erro
logger.warning("Taxa acima do normal", extra={...})

# ERROR: Erro que afeta funcionalidade
logger.error("Falha ao salvar proposta", extra={...}, exc_info=True)

# CRITICAL: Sistema em risco
logger.critical("Banco de dados inacessivel", extra={...})
```

---

## CHECKLIST DE VERIFICACAO

Antes de finalizar QUALQUER sprint:

### Codigo
- [ ] Pylint >= 99/100 (meta 100/100)
- [ ] Mypy sem errors
- [ ] Black formatado
- [ ] Isort ordenado
- [ ] Bandit sem high/critical

### Testes
- [ ] Todos os testes passando
- [ ] Cobertura >= 85%
- [ ] Testes de integracao para fluxos criticos

### Documentacao
- [ ] Docstrings em todas funcoes publicas
- [ ] README.md atualizado
- [ ] CHANGELOG.md atualizado

### Processo
- [ ] Code review aprovado
- [ ] Sprint <= 2 semanas
- [ ] Deploy nao e sexta
- [ ] Auditor executado

### Financeiro (se aplicavel)
- [ ] Decimal para todos valores monetarios
- [ ] Testes de precisao financeira
- [ ] Arredondamento correto (ROUND_HALF_UP)

---

## CONSEQUENCIAS DE VIOLACAO

```
VIOLACAO DETECTADA:
  -> Sprint NAO pode ser finalizado
  -> Deploy BLOQUEADO
  -> Correcao OBRIGATORIA antes de continuar
  -> Documentar o que aconteceu
  -> Post-mortem se recorrente

VIOLACAO RECORRENTE (3x):
  -> Revisao de processo
  -> Treinamento adicional
  -> Automatizar prevencao
```

---

*Regras de Ouro - ERP Conecta Mais*
*"Qualidade nao e negociavel"*
