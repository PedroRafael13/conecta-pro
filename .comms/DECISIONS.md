# Decisões de Arquitetura — Conecta PRO

> Decisões tomadas durante o desenvolvimento. Ambas IAs devem consultar antes de propor alternativas.

## DEC-001: Stack Principal (vigente)
- **Data:** 2026-02-05
- **Decisão:** Backend Python 3.12 + FastAPI, Frontend Next.js 16 + React 19 + TypeScript 5.9
- **Contexto:** Stack definida pelo projeto
- **Status:** Vigente

## DEC-002: Orval como Codegen (vigente)
- **Data:** 2026-02-05
- **Decisão:** Orval 7.13.2 para geração de tipos e hooks React Query a partir do OpenAPI
- **Contexto:** Garante type-safety entre backend e frontend
- **Regra:** NUNCA editar arquivos gerados manualmente
- **Status:** Vigente

## DEC-003: TypeScript Strict Mode (vigente)
- **Data:** 2026-02-05
- **Decisão:** `strict: true`, `noUncheckedIndexedAccess: true`, `ignoreBuildErrors: false`
- **Contexto:** Migração completa de 227 erros para 0
- **Status:** Vigente

## DEC-004: Commits em Português (vigente)
- **Data:** 2026-02-05
- **Decisão:** Formato `tipo(escopo): descrição` em português brasileiro
- **Contexto:** Padrão da equipe
- **Status:** Vigente

## DEC-005: Deploy via Docker Compose na VPS (vigente)
- **Data:** 2026-02-07
- **Decisão:** Sem Kubernetes. Deploy direto via docker compose na VPS.
- **Contexto:** Infraestrutura atual é VPS única
- **Status:** Vigente

## DEC-006: Comunicação Inter-IA via Filesystem (vigente)
- **Data:** 2026-02-07
- **Decisão:** Diretório `.comms/` com JSONL para mensagens e Markdown para estado
- **Contexto:** Ambas IAs (Claude + Kimi) operam no mesmo servidor
- **Status:** Vigente

## DEC-007: Regra de Ouro — Qualidade 99%+ (vigente)
- **Data:** 2026-02-07
- **Decisão:** Não aceitar codificação inferior a 99%. Qualidade obrigatoriamente superior a 99%.
- **Contexto:** Definido pelo usuário/dono do projeto como regra não negociável
- **Métricas Obrigatórias:**
  - Cobertura de testes: ≥ 99%
  - Type safety: 100% (strict mode)
  - Linting: 0 erros/warnings
  - Security: 0 vulnerabilidades críticas
  - Code review: Aprovação obrigatória
- **Processo:** Checklist pré-commit obrigatório (ver QUALITY_RULES.md)
- **Responsabilidades:**
  - Claude Opus 4.6: Planejamento, auditoria, code review final
  - Kimi K2.5: Implementação, testes 99%+, type checking, linting
- **Status:** Vigente
- **Arquivos Relacionados:**
  - `/opt/conecta-pro/QUALITY_RULES.md`
  - `/opt/conecta-pro/AGENTS.md` (seção "Regra de Ouro")
