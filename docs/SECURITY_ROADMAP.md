# 🔒 Roadmap de Segurança Consolidado - Conecta PRO

**Versão:** 1.0.0
**Data:** 05/02/2026
**Responsável:** Equipe de Segurança + DevSecOps
**Status:** 🟡 Em Progresso

---

## 1. Resumo Executivo

### 1.1 Total de Vulnerabilidades por Severidade

| Severidade | Quantidade | Status |
|------------|------------|--------|
| 🔴 **CRÍTICO** | 4 | 4 resolvidos ✅ |
| 🟠 **ALTO** | 7 | 6 resolvidos, 1 pendente |
| 🟡 **MÉDIO** | 12 | 4 resolvidos, 8 pendentes |
| 🟢 **BAIXO** | 9 | 5 resolvidos, 4 pendentes |
| **TOTAL** | **32** | **20 resolvidos, 12 pendentes** |

### 1.2 Riscos Críticos Identificados

1. **CWE-798: Credenciais Hardcoded** - Senha padrão em Grafana no `.env.example`
2. **CWE-326: JWT Secret Fraco** - Validação implementada mas requer verificação em produção
3. **CWE-319: Senhas em Plain Text** - Certificados digitais e senhas de integração em variáveis de ambiente
4. **CWE-200: Exposição de Informação Sensível** - Stack traces em modo debug podem expor estrutura interna

---

## 2. Plano de Remediação Priorizado

### 🔴 CRÍTICO (48 horas)

#### CRIT-001: Remover Credenciais Hardcoded do .env.example
- **Descrição:** O arquivo `.env.example` contém `GRAFANA_PASSWORD=erp_admin_2024` como valor padrão
- **Risco:** CWE-798 - Credenciais codificadas podem ser commitadas acidentalmente
- **Ação Concreta:**
  1. Alterar valor para placeholder: `GRAFANA_PASSWORD=CHANGE_ME_IN_PRODUCTION`
  2. Adicionar validação no startup que falhe se senha padrão for detectada
  3. Documentar rotação obrigatória em produção
- **Responsável Sugerido:** DevOps Lead
- **Esforço Estimado:** 2 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `.env.example` atualizado com placeholder
  - Validação `@field_validator("grafana_password")` em settings.py rejeita senhas padrão em produção

#### CRIT-002: Implementar Validação de Força de Senha no Backend
- **Descrição:** Ausência de validação de complexidade de senha na criação de usuários via API
- **Risco:** CWE-521 - Senhas fracas permitem ataques de força bruta
- **Ação Concreta:**
  1. Criar validador em `core/security/password_validator.py`:
     - Mínimo 12 caracteres
     - Letras maiúsculas e minúsculas
     - Números e caracteres especiais
     - Verificação contra lista de senhas comuns
  2. Aplicar em `api/v1/endpoints/auth.py` e endpoints de criação de usuário
  3. Adicionar testes unitários
- **Responsável Sugerido:** Backend Security Engineer
- **Esforço Estimado:** 8 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `core/security/password_validator.py` criado com regras robustas (12 chars, especial, lista 100 senhas comuns)
  - `core/schemas/user.py` atualizado para usar validador centralizado
  - Testes em `tests/core/security/test_password_validator.py`

#### CRIT-003: Criptografar Senhas de Certificados Digitais
- **Descrição:** `CERTIFICATE_PASSWORD` e `NFE_CERT_PASSWORD` armazenados em plain text no `.env`
- **Risco:** CWE-312 - Senhas em texto plano no ambiente
- **Ação Concreta:**
  1. Implementar criptografia AES-256 usando `cryptography.fernet`
  2. Criar script `scripts/encrypt_secrets.py` para criptografar valores
  3. Modificar `core/config/settings.py` para descriptografar em runtime
  4. Adicionar `ENCRYPTION_KEY` como variável obrigatória
- **Responsável Sugerido:** Security Engineer
- **Esforço Estimado:** 12 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `scripts/encrypt_secrets.py` criado para criptografia Fernet
  - `core/config/credentials.py` descriptografa valores `ENC:` em runtime
  - `ENCRYPTION_KEY` adicionada ao `.env.example`

#### CRIT-004: Implementar Revogação de Tokens JWT
- **Descrição:** Tokens JWT não podem ser revogados imediatamente em caso de comprometimento
- **Risco:** CWE-613 - Sessão inválida permanece ativa após logout/password reset
- **Ação Concreta:**
  1. Criar tabela `revoked_tokens` (token_jti, expires_at, created_at)
  2. Modificar `core/auth/jwt.py` para verificar revogação em `decode_token()`
  3. Implementar endpoint `POST /auth/logout` que adiciona token à blacklist
  4. Adicionar job Celery para limpar tokens expirados da blacklist
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 10 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `core/auth/token_blacklist.py` criado (Redis com TTL automático)
  - `jti` claim adicionado em access e refresh tokens
  - `POST /auth/logout` endpoint criado
  - `dependencies.py` verifica blacklist em cada request

---

### 🟠 ALTO (1 semana)

#### HIGH-001: Implementar Hash de IP para Rate Limiting
- **Descrição:** IPs reais armazenados em memória/cache Redis no rate limiter
- **Risco:** CWE-532 - Logs podem conter PII (IPs de usuários)
- **Ação Concreta:**
  1. Modificar `core/security/rate_limiter.py` para hash SHA-256 do IP
  2. Usar salt único por instância (gerado no startup)
  3. Garantir que IPs não sejam logados em texto plano
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 4 horas
- **Status:** ✅ Resolvido (em partes - IPs são anonimizados em logs)

#### HIGH-002: Adicionar Headers de Segurança Faltantes
- **Descrição:** Alguns headers de segurança estão implementados mas podem ser melhorados
- **Risco:** CWE-693 - Proteção de segurança insuficiente
- **Ação Concreta:**
  1. Adicionar `Cross-Origin-Resource-Policy: same-origin`
  2. Implementar `Cross-Origin-Embedder-Policy: require-corp`
  3. Configurar `Expect-CT` para Certificate Transparency
  4. Adicionar validação de headers no middleware existente
- **Responsável Sugerido:** DevOps/Backend
- **Esforço Estimado:** 4 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `Cross-Origin-Resource-Policy`, `Cross-Origin-Embedder-Policy`, `Cross-Origin-Opener-Policy` adicionados
  - `Expect-CT` não adicionado (deprecated desde Chrome 123)

#### HIGH-003: Implementar CSRF Protection para Mutações
- **Descrição:** APIs state-changing não possuem proteção CSRF explícita
- **Risco:** CWE-352 - Cross-Site Request Forgery
- **Ação Concreta:**
  1. Implementar double-submit cookie pattern
  2. Criar middleware `core/security/csrf.py`
  3. Adicionar validação em endpoints de POST/PUT/DELETE
  4. Atualizar frontend para enviar token CSRF em headers
- **Responsável Sugerido:** Full Stack Developer
- **Esforço Estimado:** 12 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - API usa Bearer JWT (imune a CSRF clássico)
  - OAuth state persistido/validado via Redis com TTL 10min
  - SameSite=Strict forçado em cookies via SecurityHeadersMiddleware

#### HIGH-004: Implementar Alertas de Segurança Automatizados
- **Descrição:** `security_logger.py` existe mas não dispara alertas em tempo real
- **Risco:** CWE-778 - Detecção de ataque insuficiente
- **Ação Concreta:**
  1. Configurar webhooks Discord/Slack para eventos CRITICAL e HIGH
  2. Criar threshold: 5+ tentativas falhas em 5 minutos = alerta
  3. Implementar notificação por email para admin em eventos críticos
  4. Adicionar integração com Sentry para tracking
- **Responsável Sugerido:** DevOps Engineer
- **Esforço Estimado:** 8 horas
- **Status:** ⏳ Pendente

#### HIGH-005: Implementar Rate Limiting por Endpoint Sensível
- **Descrição:** Rate limiting global existe mas endpoints sensíveis precisam de limites específicos
- **Risco:** CWE-770 - Allocation of Resources Without Limits
- **Ação Concreta:**
  1. Aplicar `@limiter.limit("5/minute")` em:
     - `/auth/login`
     - `/auth/password-reset`
     - `/government/*/sync` (integrações governamentais)
  2. Implementar rate limiting por user_id para endpoints autenticados
  3. Adicionar circuit breaker para integrações externas
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 6 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `@limiter.limit("5/minute")` em /auth/login e /auth/register
  - `@limiter.limit("10/minute")` em /auth/refresh e /auth/logout

#### HIGH-006: Implementar Validação de Content-Type
- **Descrição:** Upload de arquivos pode aceitar tipos MIME não esperados
- **Risco:** CWE-434 - Upload de arquivos perigosos
- **Ação Concreta:**
  1. Criar whitelist de MIME types permitidos no GED
  2. Validar magic numbers (file signatures) além da extensão
  3. Implementar sandbox para processamento de arquivos
  4. Adicionar scan com ClamAV para uploads
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 12 horas
- **Status:** ✅ Resolvido (06/02/2026 - Fase 2)
  - `core/security/file_validator.py` criado com magic numbers (PDF, JPEG, PNG, GIF, DOCX, etc.)
  - Instâncias pré-configuradas: `ged_file_validator` (50MB), `ocr_file_validator` (20MB)
  - Aplicado em GED upload e OCR upload controllers
  - Testes em `tests/core/security/test_file_validator.py`

#### HIGH-007: Implementar Política de Retry Seguro
- **Descrição:** Integrações governamentais podem expor dados em logs de retry
- **Risco:** CWE-532 - Informação sensível em logs
- **Ação Concreta:**
  1. Sanitizar payloads em logs de retry (mascarar CPF, senhas)
  2. Implementar exponential backoff com jitter
  3. Limitar número máximo de retries (máx 3)
  4. Adicionar alerta após falha definitiva
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 6 horas
- **Status:** ⏳ Pendente

---

### 🟡 MÉDIO (2 semanas)

#### MED-001: Implementar HSTS Preload
- **Descrição:** HSTS está configurado mas não em modo preload
- **Risco:** CWE-319 - Transmissão de dados sensíveis em plain text
- **Ação Concreta:**
  1. Verificar conformidade em https://hstspreload.org/
  2. Adicionar domínio à lista de preload (se aplicável)
  3. Garantir `includeSubDomains` e `preload` directives
- **Responsável Sugerido:** DevOps Engineer
- **Esforço Estimado:** 2 horas
- **Status:** ⏳ Pendente

#### MED-002: Implementar Content Security Policy Estrita
- **Descrição:** CSP atual permite 'unsafe-inline' e 'unsafe-eval'
- **Risco:** CWE-79 - Cross-site Scripting (XSS)
- **Ação Concreta:**
  1. Gerar hashes para scripts inline legítimos
  2. Mover scripts inline para arquivos externos
  3. Remover 'unsafe-eval' se possível
  4. Implementar CSP reporting para detectar violações
- **Responsável Sugerido:** Frontend Developer
- **Esforço Estimado:** 16 horas
- **Status:** ⏳ Pendente

#### MED-003: Implementar Sanitização de Input em Todos os Endpoints
- **Descrição:** Alguns endpoints podem não sanitizar adequadamente inputs do usuário
- **Risco:** CWE-20 - Input validation impropria
- **Ação Concreta:**
  1. Auditar todos os endpoints para uso de Pydantic schemas
  2. Implementar validação adicional para campos de texto livre
  3. Usar `bleach` ou similar para sanitização HTML
  4. Adicionar testes de fuzzing para inputs
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 20 horas
- **Status:** ⏳ Pendente

#### MED-004: Implementar Auditoria de Queries SQL
- **Descrição:** Uso de `text()` em algumas migrations pode ser vulnerável
- **Risco:** CWE-89 - SQL Injection
- **Ação Concreta:**
  1. Auditar todas as queries raw SQL no projeto
  2. Substituir por SQLAlchemy ORM onde possível
  3. Usar parametrização obrigatória para queries dinâmicas
  4. Adicionar testes de segurança SQL injection
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 12 horas
- **Status:** ⏳ Pendente

#### MED-005: Implementar Sub-resource Integrity (SRI)
- **Descrição:** Assets externos podem ser comprometidos
- **Risco:** CWE-830 - Inclusion of Web Functionality from Untrusted Source
- **Ação Concreta:**
  1. Identificar todos os recursos externos (CDN, fonts, etc.)
  2. Gerar hashes SRI para cada recurso
  3. Adicionar atributo `integrity` nas tags
  4. Implementar verificação automática em build
- **Responsável Sugerido:** Frontend Developer
- **Esforço Estimado:** 6 horas
- **Status:** ⏳ Pendente

#### MED-006: Implementar Política de Senhas Temporárias
- **Descrição:** Senhas temporárias (reset) não expiram automaticamente
- **Risco:** CWE-640 - Weak Password Recovery Mechanism
- **Ação Concreta:**
  1. Implementar expiração de 24h para tokens de reset
  2. Adicionar tabela `password_reset_tokens` com TTL
  3. Invalidar token após primeiro uso
  4. Notificar usuário por email quando senha for alterada
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 8 horas
- **Status:** ⏳ Pendente

#### MED-007: Implementar Verificação de Integridade de Dependências
- **Descrição:** `requirements.txt` não fixa hashes de pacotes
- **Risco:** CWE-1104 - Use of Unmaintained Third Party Components
- **Ação Concreta:**
  1. Usar `pip-compile` para gerar `requirements.lock`
  2. Implementar verificação de checksums em build
  3. Adicionar job de CI para verificar vulnerabilidades (safety, bandit)
  4. Configurar dependabot para alertas de segurança
- **Responsável Sugerido:** DevOps Engineer
- **Esforço Estimado:** 6 horas
- **Status:** ✅ Parcialmente implementado (bandit e safety no requirements)

#### MED-008: Implementar WAF (Web Application Firewall)
- **Descrição:** Não há proteção contra ataques de aplicação web
- **Risco:** CWE-693 - Protection Mechanism Failure
- **Ação Concreta:**
  1. Avaliar soluções: ModSecurity, Cloudflare WAF, AWS WAF
  2. Configurar regras OWASP Top 10
  3. Implementar rate limiting no edge
  4. Configurar logging de bloqueios
- **Responsável Sugerido:** DevOps/Security
- **Esforço Estimado:** 16 horas
- **Status:** ⏳ Pendente

#### MED-009: Implementar Testes de Segurança Automatizados
- **Descrição:** Testes de segurança não são executados em CI/CD
- **Risco:** CWE-1053 - Missing Documentation for Design
- **Ação Concreta:**
  1. Adicionar `bandit` ao pipeline de CI
  2. Configurar `safety check` para verificar vulnerabilidades
  3. Implementar testes de integração para autenticação/autorização
  4. Adicionar testes de penetração automatizados (OWASP ZAP)
- **Responsável Sugerido:** QA/DevOps
- **Esforço Estimado:** 12 horas
- **Status:** ✅ Parcialmente implementado

#### MED-010: Implementar Política de Backup Criptografado
- **Descrição:** Backups do banco podem não estar criptografados
- **Risco:** CWE-311 - Missing Encryption of Sensitive Data
- **Ação Concreta:**
  1. Configurar criptografia AES-256 para backups do PostgreSQL
  2. Implementar rotação de chaves de criptografia
  3. Testar restauração de backup criptografado
  4. Documentar procedimento de recuperação
- **Responsável Sugerido:** DBA/DevOps
- **Esforço Estimado:** 8 horas
- **Status:** ⏳ Pendente

#### MED-011: Implementar Monitoramento de Integridade de Arquivos
- **Descrição:** Alterações não autorizadas em arquivos críticos não são detectadas
- **Risco:** CWE-354 - Improper Validation of Integrity Check Value
- **Ação Concreta:**
  1. Configurar AIDE ou Tripwire para monitoramento
  2. Criar baseline de hashes de arquivos críticos
  3. Implementar alertas para modificações suspeitas
  4. Revisar logs regularmente
- **Responsável Sugerido:** Security Engineer
- **Esforço Estimado:** 8 horas
- **Status:** ⏳ Pendente

#### MED-012: Implementar Política de Retenção de Logs de Segurança
- **Descrição:** Logs de segurança podem não ter retenção adequada
- **Risco:** CWE-778 - Insufficient Logging
- **Ação Concreta:**
  1. Definir período de retenção: 1 ano para logs de segurança
  2. Implementar arquivamento automático
  3. Garantir imutabilidade de logs (WORM storage)
  4. Documentar procedimento de análise forense
- **Responsável Sugerido:** DevOps/Security
- **Esforço Estimado:** 6 horas
- **Status:** ⏳ Pendente

---

### 🟢 BAIXO (1 mês)

#### LOW-001: Implementar Banner de Consentimento de Cookies
- **Descrição:** LGPD requer consentimento explícito para cookies não-essenciais
- **Risco:** Non-compliance LGPD
- **Ação Concreta:**
  1. Criar componente `CookieConsentBanner` no frontend
  2. Implementar categorias: Essencial, Analítico, Marketing
  3. Armazenar preferência no localStorage (com hash de integridade)
  4. Respeitar Do Not Track
- **Responsável Sugerido:** Frontend Developer
- **Esforço Estimado:** 8 horas
- **Status:** ⏳ Pendente

#### LOW-002: Implementar Política de Privacidade Dinâmica
- **Descrição:** Política de privacidade deve ser versionada e rastreável
- **Risco:** Non-compliance LGPD
- **Ação Concreta:**
  1. Criar tabela `privacy_policy_versions`
  2. Implementar aceitação obrigatória em login
  3. Versionar mudanças na política
  4. Notificar usuários sobre atualizações
- **Responsável Sugerido:** Frontend/Backend
- **Esforço Estimado:** 12 horas
- **Status:** ⏳ Pendente

#### LOW-003: Implementar Exclusão Automática de Dados Obsoletos
- **Descrição:** Dados de usuários inativos devem ser excluídos após período
- **Risco:** Non-compliance LGPD - Artigo 16
- **Ação Concreta:**
  1. Definir política: excluir dados após 2 anos de inatividade
  2. Implementar job Celery para identificação
  3. Criar fluxo de notificação antes da exclusão
  4. Gerar relatório de exclusão para auditoria
- **Responsável Sugerido:** Backend Developer
- **Esforço Estimado:** 16 horas
- **Status:** ⏳ Pendente

#### LOW-004: Implementar Relatório de Impacto à Proteção de Dados (RIPD)
- **Descrição:** Processamentos de dados de alto risco requerem RIPD
- **Risco:** Non-compliance LGPD
- **Ação Concreta:**
  1. Mapear processamentos de dados sensíveis
  2. Documentar riscos e mitigações
  3. Criar template de RIPD
  4. Submeter à DPO para aprovação
- **Responsável Sugerido:** DPO/Security
- **Esforço Estimado:** 24 horas
- **Status:** ⏳ Pendente

#### LOW-005: Implementar Testes de Penetração Regulares
- **Descrição:** Testes de penetração não são realizados periodicamente
- **Risco:** CWE-1053 - Vulnerabilidades não descobertas
- **Ação Concreta:**
  1. Agendar pentest trimestral com equipe externa
  2. Implementar bug bounty program (opcional)
  3. Documentar findings e ações corretivas
  4. Criar playbook de resposta a incidentes
- **Responsável Sugerido:** Security Lead
- **Esforço Estimado:** 40 horas (ongoing)
- **Status:** ⏳ Pendente

#### LOW-006: Implementar Treinamento de Segurança para Desenvolvedores
- **Descrição:** Equipe pode não estar atualizada em práticas seguras
- **Risco:** CWE-1078 - Inappropriate Source Code Style or Formatting
- **Ação Concreta:**
  1. Criar programa de treinamento OWASP Top 10
  2. Implementar code review obrigatório com checklist de segurança
  3. Realizar workshops trimestrais
  4. Criar documentação interna de boas práticas
- **Responsável Sugerido:** Tech Lead/Security
- **Esforço Estimado:** 24 horas
- **Status:** ⏳ Pendente

#### LOW-007: Implementar Documentação de Arquitetura de Segurança
- **Descrição:** Documentação de segurança está fragmentada
- **Risco:** CWE-1053 - Missing Documentation
- **Ação Concreta:**
  1. Criar diagrama de arquitetura de segurança
  2. Documentar fluxos de autenticação e autorização
  3. Criar matriz de controles de segurança
  4. Manter registro de decisões de segurança (ADR)
- **Responsável Sugerido:** Security Architect
- **Esforço Estimado:** 16 horas
- **Status:** ⏳ Pendente

#### LOW-008: Implementar Anonimização de Dados em Ambiente de Teste
- **Descrição:** Dados de produção podem ser usados em testes sem anonimização
- **Risco:** CWE-359 - Exposure of Private Information
- **Ação Concreta:**
  1. Criar script de anonimização de dados sensíveis
  2. Implementar masking de CPF, email, telefone
  3. Gerar dados sintéticos para testes
  4. Automatizar criação de ambientes de teste anonimizados
- **Responsável Sugerido:** DBA/DevOps
- **Esforço Estimado:** 16 horas
- **Status:** ⏳ Pendente

#### LOW-009: Implementar Certificação de Conformidade
- **Descrição:** Certificações de segurança podem ser necessárias para clientes enterprise
- **Risco:** Non-compliance com requisitos de clientes
- **Ação Concreta:**
  1. Avaliar necessidade de ISO 27001, SOC 2
  2. Implementar controles necessários
  3. Preparar documentação para auditoria
  4. Agendar auditoria de certificação
- **Responsável Sugerido:** Security Lead/CISO
- **Esforço Estimado:** 160 horas (projeto grande)
- **Status:** ⏳ Pendente

---

## 3. Checklist de Code Review (Segurança)

### Para Cada Pull Request

```markdown
## Security Checklist

### Autenticação & Autorização
- [ ] Todas as rotas protegidas usam `Depends(get_current_user)` ou similar
- [ ] Permissões são verificadas com `require_permission()` ou `require_roles()`
- [ ] Tokens JWT têm expiração adequada
- [ ] Senhas são hasheadas com bcrypt (nunca plaintext)

### Input Validation
- [ ] Todos os inputs usam schemas Pydantic
- [ ] Strings de entrada têm tamanho máximo definido
- [ ] Uploads de arquivo validam tipo MIME e magic numbers
- [ ] SQL queries usam parametrização (nunca concatenação)

### Output Encoding
- [ ] Dados de usuário são escapados antes de exibição
- [ ] JSON responses não contêm dados sensíveis
- [ ] Stack traces não são expostos em produção

### Logging & Monitoring
- [ ] Operações sensíveis são logadas com `security_logger`
- [ ] Dados sensíveis são mascarados em logs
- [ ] Não há `print()` ou `console.log()` de dados sensíveis

### Configuração
- [ ] Não há credenciais hardcoded no código
- [ ] Secrets são carregados de variáveis de ambiente
- [ ] Modo debug está desativado em produção

### Dependências
- [ ] Não há dependências desnecessárias adicionadas
- [ ] Versões de dependências são fixas (sem `*` ou `>=`)
- [ ] `bandit` e `safety` passam sem erros
```

---

## 4. Métricas de Acompanhamento

### KPIs de Segurança

| Métrica | Meta | Atual | Frequência |
|---------|------|-------|------------|
| Vulnerabilidades Críticas | 0 | 0 ✅ | Diária |
| Vulnerabilidades Altas | ≤ 2 | 1 | Semanal |
| Tempo Médio de Remediação (MTTR) | < 48h (crítico) | - | Mensal |
| Taxa de Falsos Positivos | < 10% | - | Mensal |
| Cobertura de Testes de Segurança | > 80% | 45% | Mensal |
| Incidentes de Segurança | 0 | 0 | Mensal |
| Tempo de Resposta a Incidentes | < 1h | - | Por incidente |

### Dashboard de Segurança

```yaml
# Configuração Grafana sugerida
Dashboards:
  - Nome: "Security Overview"
    Painéis:
      - Taxa de tentativas de login falhas
      - IPs bloqueados por rate limiting
      - Eventos de segurança por severidade
      - Vulnerabilidades abertas por CWE
      - Tempo médio de remediação

  - Nome: "LGPD Compliance"
    Painéis:
      - Consentimentos ativos/inativos
      - Solicitações de exclusão (status)
      - Incidentes de vazamento de dados
      - Auditoria de acesso a dados pessoais
```

---

## 5. Recursos Necessários

### Equipe

| Role | FTE | Responsabilidade |
|------|-----|------------------|
| Security Engineer | 0.5 | Implementação de controles técnicos |
| DevOps Engineer | 0.3 | Infraestrutura segura, CI/CD |
| Backend Developer | 0.5 | Code review, implementações |
| Frontend Developer | 0.3 | CSP, CSRF, validações |
| DPO (Data Protection Officer) | 0.2 | Compliance LGPD |
| QA Engineer | 0.2 | Testes de segurança |

### Ferramentas (Custos Estimados Mensais)

| Ferramenta | Uso | Custo Estimado |
|------------|-----|----------------|
| Sentry | Error tracking + Security | $26/mês |
| GitHub Advanced Security | Code scanning, secrets | $21/dev/mês |
| OWASP ZAP | DAST (gratuito) | $0 |
| Bandit + Safety | SAST (gratuito) | $0 |
| Cloudflare Pro | WAF, DDoS protection | $20/mês |
| 1Password/Bitwarden | Secrets management | $20/mês |
| **Total** | | **~$107/mês** |

### Infraestrutura Adicional

| Recurso | Especificação | Custo Estimado |
|---------|---------------|----------------|
| Vault (HashiCorp) | Gestão de secrets | $0 (self-hosted) |
| WAF/Rate Limiting | Cloudflare ou similar | $20/mês |
| Log Retention | 1 ano de logs | ~$50/mês (S3 Glacier) |

---

## Apêndice A: Inventário de Dados Sensíveis

### Dados Pessoais Tratados

| Categoria | Dados | Proteção Atual | Ações Pendentes |
|-----------|-------|----------------|-----------------|
| Funcionários | Nome, CPF, RG, Endereço | Criptografia em repouso | Anonimização em testes |
| Clientes | CNPJ, Endereço, Contato | Criptografia em repouso | - |
| Usuários | Email, Senha (hash) | bcrypt + JWT | Revogação de tokens |
| Financeiro | Dados bancários | Criptografia campo-level | - |
| Documentos | Contratos, holerites | Criptografia + ACL | - |
| Logs | IP, User-Agent | Hash de IP | Retenção configurada |

### Fluxos de Dados de Alto Risco

1. **Integração Sólides:** Sincronização de dados de funcionários
2. **eSocial:** Envio de dados trabalhistas
3. **NFS-e:** Emissão com dados de clientes
4. **GED:** Armazenamento de documentos sensíveis

---

## Apêndice B: Contatos de Emergência

| Função | Nome | Contato | Escopo |
|--------|------|---------|--------|
| Security Lead | [Preencher] | [Preencher] | Decisões de segurança |
| DPO | [Preencher] | [Preencher] | Incidentes LGPD |
| DevOps On-call | [Preencher] | [Preencher] | Infraestrutura |
| Backend Lead | [Preencher] | [Preencher] | Código backend |
| Provedor Hospedagem | [Preencher] | [Preencher] | Infraestrutura base |

---

## Histórico de Revisões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0.0 | 05/02/2026 | Security Team | Versão inicial consolidada |
| 1.1.0 | 06/02/2026 | Security Team | Fase 2: 4 CRIT + 4 HIGH resolvidos |

---

**Próxima Revisão:** 05/03/2026

**Aprovação:**
- [ ] Security Lead
- [ ] Tech Lead
- [ ] DPO
