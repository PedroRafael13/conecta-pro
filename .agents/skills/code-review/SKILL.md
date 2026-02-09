---
title: Code Review
description: Revisão de código com checklist OWASP para Conecta PRO
standard: OWASP Top 10 2021
---

# Code Review

Processo de revisão de código com foco em segurança (OWASP) para Conecta PRO.

## Processo de Review

```
1. Visão Geral    → Contexto e objetivo
2. Funcionalidade → Requisitos atendidos
3. Segurança      → Checklist OWASP
4. Qualidade      → Padrões de código
5. Testes         → Cobertura e casos
6. Performance    → Impacto identificado
```

## Checklist OWASP

### A01: Broken Access Control
- [ ] Autenticação em todos os endpoints
- [ ] Verificação de autorização (RBAC)
- [ ] IDs não sequenciais/previsíveis
- [ ] CORS configurado corretamente

### A02: Cryptographic Failures
- [ ] Senhas hasheadas (bcrypt/Argon2)
- [ ] Dados sensíveis criptografados
- [ ] TLS 1.3 em todas as conexões
- [ ] Secrets em vault (não no código)

### A03: Injection
- [ ] Queries parametrizadas
- [ ] Input sanitizado
- [ ] No eval() ou exec() dinâmico

### A07: Auth Failures
- [ ] JWT com expiração curta
- [ ] Refresh tokens rotacionados
- [ ] Rate limiting implementado

### A09: Security Logging
- [ ] Logs de autenticação/falhas
- [ ] Dados sensíveis mascarados
- [ ] Integridade dos logs

## Padrões de Código

```python
# ✅ Correto
async def get_fatura(
    fatura_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not await has_permission(current_user, "fatura:read"):
        raise HTTPException(403)
    return await service.get(fatura_id)

# ❌ Incorreto
def get_fatura(id):  # Sem auth, id int
    return db.query(Fatura).get(id)
```

## Checklist Geral

- [ ] Código limpo (DRY, KISS)
- [ ] Tipagem estática completa
- [ ] Documentação atualizada
- [ ] Testes unitários + integração
- [ ] Sem FIXME/TODO críticos
- [ ] Changelog atualizado
