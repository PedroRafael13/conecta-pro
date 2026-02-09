# 🏆 REGRAS DE QUALIDADE — CONECTA PRO
## Versão: 99%+ Standard | Data: $(date '+%Y-%m-%d')

> ⚠️ **REGRA DE OURO — NÃO NEGOCIÁVEL**
>
> "Não aceito codificação inferior a 99%. A qualidade dos códigos precisa ser obrigatoriamente superior a 99%."
> — Usuário/Dono do Projeto

---

## 📊 Métricas Obrigatórias

| Métrica | Meta | Mínimo Aceitável | Status |
|---------|------|------------------|--------|
| Cobertura de Testes | 100% | 99% | 🎯 |
| Type Safety | 100% | 100% | 🎯 |
| Linting | 0 erros | 0 erros/warnings | 🎯 |
| Security Scan | 0 críticos | 0 críticos/alto | 🎯 |
| Code Review | Aprovado | Aprovado | 🎯 |
| Documentação | 100% APIs | 100% públicas | 🎯 |

---

## ✅ Checklist Pré-Commit (OBRIGATÓRIO)

### Backend (Python/FastAPI)
```bash
# 1. Testes (DEVE passar 100%)
pytest --cov=modules --cov-report=term-missing
# RESULTADO ESPERADO: coverage ≥ 99%

# 2. Type Checking (DEVE ter 0 erros)
mypy modules/
# RESULTADO ESPERADO: Success: no issues found

# 3. Linting (DEVE ter 0 erros/warnings)
ruff check modules/
black --check modules/
isort --check-only modules/
# RESULTADO ESPERADO: 0 erros

# 4. Security (DEVE ter 0 críticos)
bandit -r modules/
safety check
# RESULTADO ESPERADO: 0 issues

# 5. Código morto
vulture modules/ --min-confidence 80
# RESULTADO ESPERADO: 0 ou justificado
```

### Frontend (Next.js/TypeScript)
```bash
# 1. Testes (DEVE passar 100%)
npm run test:coverage
# RESULTADO ESPERADO: coverage ≥ 99%

# 2. Type Checking (DEVE ter 0 erros)
npm run type-check
# RESULTADO ESPERADO: 0 erros

# 3. Linting (DEVE ter 0 erros/warnings)
npm run lint
# RESULTADO ESPERADO: 0 erros

# 4. Security (DEVE ter 0 críticos)
npm audit --audit-level=critical
# RESULTADO ESPERADO: 0 vulnerabilities

# 5. Build (DEVE compilar)
npm run build
# RESULTADO ESPERADO: Compiled successfully
```

---

## 🚫 Política de Qualidade

### Níveis de Qualidade

```
100%  = ✅ EXCELENTE — Pode commitar
99%   = ✅ APROVADO — Pode commitar
95%   = ⚠️ REJEITADO — Melhorar antes
90%   = ❌ REJEITADO — Refazer
<90%  = 🚫 INACEITÁVEL — Nem considerar
```

### O Que NÃO Fazer

❌ Commitar com tests falhando
❌ Ignorar warnings de linter
❌ Deixar código sem type
❌ Aceitar cobertura < 99%
❌ Commitar sem code review
❌ Deixar de documentar APIs públicas

### O Que FAZER Sempre

✅ Testar edge cases
✅ Tipar TUDO (strict mode)
✅ Documentar com docstrings/TSDoc
✅ Revisar código antes de commitar
✅ Rodar full checklist antes de push
✅ Justificar qualquer exceção (com aprovação)

---

## 🔄 Processo de Desenvolvimento

### Fluxo Obrigatório

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PLANEJAR  │ →  │ IMPLEMENTAR │ →  │   TESTAR    │
│  (Claude)   │    │   (Kimi)    │    │   (Kimi)    │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                              │
┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│   COMMIT    │ ←  │    LINT     │ ←  │ TYPE CHECK  │
│  (Aprovado) │    │  (0 erros)  │    │  (0 erros)  │
└─────────────┘    └─────────────┘    └─────────────┘
       ↑
┌──────┴──────┐
│    REVIEW   │
│  (Claude)   │
└─────────────┘
```

### Responsabilidades

**Claude Opus 4.6:**
- Planejamento arquitetural
- Code review final
- Aprovação de qualidade
- Documentação técnica

**Kimi K2.5:**
- Implementação de código
- Escrita de testes (99%+ coverage)
- Type checking (100% strict)
- Linting (0 erros)

---

## 📝 Exemplos de Qualidade

### ✅ Código Aprovado (99%+)

```python
# backend/modules/crm/services/client_service.py
from typing import Optional
from modules.crm.models.client import Client
from modules.crm.repositories.client_repository import ClientRepository
from modules.crm.schemas.client_schema import ClientCreate, ClientResponse

class ClientService:
    """Serviço de gestão de clientes.

    Responsabilidades:
    - CRUD de clientes
    - Validações de negócio
    - Cache de consultas frequentes

    Coverage: 100%
    Type Safety: 100%
    """

    def __init__(self, repo: ClientRepository) -> None:
        self._repo = repo

    async def create_client(
        self,
        data: ClientCreate
    ) -> ClientResponse:
        """Cria um novo cliente.

        Args:
            data: Dados do cliente

        Returns:
            Cliente criado

        Raises:
            DuplicateError: Se email já existe
            ValidationError: Se dados inválidos
        """
        # Validação
        if await self._repo.email_exists(data.email):
            raise DuplicateError(f"Email {data.email} já cadastrado")

        # Criação
        client = await self._repo.create(data)

        # Log
        logger.info(f"Cliente criado: {client.id}")

        return ClientResponse.model_validate(client)
```

### ❌ Código Rejeitado (< 99%)

```python
# ❌ SEM TIPAGEM
def create_client(data):
    client = repo.create(data)  # ❌ tipo?
    return client  # ❌ retorno não tipado

# ❌ SEM TESTES
class ClientService:
    def create(self, data):  # ❌ sem testes de edge case
        return repo.create(data)

# ❌ SEM DOCUMENTAÇÃO
def process(data):  # ❌ sem docstring
    # código sem comentários
    return result
```

---

## 🎯 Checklist Final (Antes de Cada Commit)

- [ ] Cobertura de testes ≥ 99%
- [ ] Type checking = 0 erros
- [ ] Linting = 0 erros/warnings
- [ ] Security scan = 0 críticos
- [ ] Code review = Aprovado
- [ ] Documentação = Completa
- [ ] Build = Sucesso

**Se qualquer item não estiver marcado → NÃO COMMITAR**

---

*Regra instituída em: $(date '+%Y-%m-%d %H:%M:%S')*
*Responsáveis: Claude Opus 4.6 + Kimi K2.5*
*Versão: 99%+ Standard*
