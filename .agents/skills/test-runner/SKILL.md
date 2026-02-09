---
title: Test Runner
description: Execução de testes pytest (6892) e vitest (1985)
tests: {python: 6892, javascript: 1985}
---

# Test Runner

Execução de suítes de teste do Conecta PRO: pytest (backend) e vitest (frontend).

## Pytest - Backend

```bash
# Todos os testes (6892)
pytest

# Com cobertura
pytest --cov=modules --cov-report=html --cov-report=term

# Por módulo
pytest tests/financial/ -v
pytest tests/government/ -k "esocial"

# Paralelo (mais rápido)
pytest -n auto --dist=loadfile

# Testes específicos
pytest -k "test_calculate_nota_fiscal"
pytest tests/test_api.py::TestFaturamento::test_create_invoice

# Debug
pytest --pdb -x  # para no primeiro erro
pytest -s        # mostra prints
```

## Vitest - Frontend

```bash
# Todos os testes (1985)
npm run test

# Watch mode
npm run test:watch

# Com UI
npm run test:ui

# Por arquivo
npx vitest run src/components/Financeiro/

# Cobertura
npx vitest run --coverage

# Filtro
npx vitest run -t "deve calcular imposto"
```

## Testes de Integração

```bash
# Banco de dados de teste
pytest tests/integration/ --db-url=postgresql://test:test@localhost/test_db

# API completa
pytest tests/e2e/ --base-url=http://localhost:8000

# Com Docker
make test-integration
```

## Performance

```bash
# Benchmarks
pytest tests/benchmark/ --benchmark-only

# Load test
locust -f tests/load/locustfile.py --host=https://staging.conecta.pro
```

## Checklist de Qualidade

- [ ] 6892 testes Python passando
- [ ] 1985 testes JavaScript passando
- [ ] Cobertura backend ≥ 80% (atual: 43.37%)
- [ ] Cobertura frontend ≥ 80%
- [ ] Sem warnings de deprecação
- [ ] Testes de contrato API atualizados
- [ ] Snapshots revisados (se houver)
- [ ] Flaky tests identificados
