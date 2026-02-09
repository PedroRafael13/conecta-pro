# Conformidade LGPD - Auditoria Conecta PRO

> Análise de proteção de dados pessoais e conformidade com Lei Geral de Proteção de Dados (LGPD)

**Data da Auditoria:** 2026-02-05
**Versão do Sistema:** Conecta PRO v2.0
**Responsável:** Equipe de Segurança

---

## 📋 Resumo Executivo

| Aspecto | Status | Notas |
|---------|--------|-------|
| **Mapeamento de Dados** | ⚠️ Parcial | Dados pessoais identificados em 15+ módulos |
| **Consentimento** | ✅ Implementado | Tabela `user_consents` com rastreamento |
| **Direitos do Titular** | ⚠️ Parcial | Exportação implementada, exclusão/anomização parcial |
| **Segurança Técnica** | ✅ Adequada | Criptografia, autenticação, rate limiting |
| **Retenção de Dados** | ❌ Não Auditado | Políticas de retenção não documentadas |

**Risco Geral:** 🟡 MÉDIO - Ações necessárias para compliance total

---

## 🗺️ Mapa de Dados Pessoais

### Módulo: Clientes (`modules/clients/`)

| Campo | Tipo | Sensibilidade | Finalidade | Retenção |
|-------|------|---------------|------------|----------|
| `cnpj` | Cadastral | Alta | Identificação fiscal | 5 anos (obrigatório) |
| `email` | Contato | Média | Comunicação | Durante contrato + 2 anos |
| `telefone` | Contato | Média | Comunicação | Durante contrato + 2 anos |
| `endereco` | Localização | Média | Prestação de serviço | Durante contrato |
| `technical_contact_email` | Contato | Média | Suporte técnico | Durante contrato |

### Módulo: Funcionários/HR (`modules/hr/`)

| Campo | Tipo | Sensibilidade | Notas LGPD |
|-------|------|---------------|------------|
| `cpf` | PII | Alta | Base legal: execução contrato |
| `rg` | PII | Média | Cópia digital - criptografar |
| `foto` | Imagem | Média | Consentimento específico necessário |
| `email_pessoal` | Contato | Média | - |
| `telefone` | Contato | Média | - |
| `endereco` | Localização | Média | - |
| `ctps` | Trabalhista | Alta | Obrigatório por lei |
| `pis_pasep` | Trabalhista | Alta | Obrigatório por lei |
| `aso_pdf` | Saúde | **Muito Alta** | Dado sensível - consentimento explícito |
| `ponto_biometrico` | Biométrico | **Muito Alta** | Consentimento específico obrigatório |

### Módulo: Campo/Operacional (`modules/campo/`)

| Campo | Tipo | Sensibilidade | Contexto |
|-------|------|---------------|----------|
| `prospect_cpf` | PII | Alta | Visitas comerciais |
| `prospect_cnpj` | Cadastral | Alta | Visitas comerciais |
| `prospect_email` | Contato | Média | - |
| `prospect_telefone` | Contato | Média | - |
| `endereco` | Localização | Média | Endereço do serviço |
| `contato_telefone` | Contato | Média | Ordem de serviço |
| `contato_email` | Contato | Média | Ordem de serviço |

### Módulo: Licitações (`modules/bidding/`)

| Campo | Tipo | Sensibilidade | Contexto |
|-------|------|---------------|----------|
| `orgao_cnpj` | Cadastral | Alta | Órgão público |
| `certificate.cnpj` | Cadastral | Alta | Certidões de empresa |

### Módulo: Audit (`modules/audit/`)

| Campo | Tipo | Sensibilidade | Notas |
|-------|------|---------------|-------|
| `user_email` | Contato | Média | Logs de auditoria - legítimo interesse |

---

## ✅ Direitos do Titular - Implementação

### 1. Direito de Acesso (Art. 18, I)

| Implementação | Endpoint/Funcionalidade | Status |
|---------------|------------------------|--------|
| Dados da conta | `GET /api/v1/me` | ✅ Implementado |
| Histórico de acesso | `GET /api/v1/audit/access-history` | ✅ Implementado |
| Dados de notificações | Via `LGPDManager` | ✅ Implementado |

### 2. Direito de Portabilidade (Art. 18, II)

| Formato | Implementação | Status |
|---------|--------------|--------|
| JSON | `LGPDManager._collect_user_data()` | ✅ Implementado |
| CSV | Não implementado | ❌ Pendente |
| XLSX | Não implementado | ❌ Pendente |

**Observação:** Portabilidade apenas para dados fornecidos pelo titular (não inclui dados derivados).

### 3. Direito de Correção (Art. 18, III)

| Funcionalidade | Endpoint | Status |
|----------------|----------|--------|
| Atualização de dados | `PUT /api/v1/me` | ✅ Implementado |
| Atualização de perfil | Via frontend | ✅ Implementado |

### 4. Direito de Exclusão/Anonimização (Art. 18, VI)

| Cenário | Implementação | Status |
|---------|--------------|--------|
| Soft delete | `is_active = False` | ⚠️ Parcial |
| Hard delete com anonimização | Não implementado | ❌ Crítico |
| Anonimização de logs | Não implementado | ❌ Crítico |

**Risco:** Não há endpoint para exclusão completa com anonimização de dados relacionados.

### 5. Direito de Oposição (Art. 18, VII)

| Tipo | Implementação | Status |
|------|--------------|--------|
| Marketing | `marketing_consent` | ✅ Implementado |
| Processamento | `data_processing_consent` | ✅ Implementado |
| Notificações push | `notification_preferences` | ✅ Implementado |

### 6. Informações sobre Compartilhamento (Art. 18, VIII)

| Implementação | Status |
|--------------|--------|
| Registro de integrações | ⚠️ Parcial (logs existem) |
| Relatório ao titular | ❌ Não implementado |

---

## 🔒 Medidas de Segurança Técnicas

| Medida | Implementação | Status | Evidência |
|--------|--------------|--------|-----------|
| **Criptografia em Repouso** | PostgreSQL SSL | ✅ | `docker-compose.yml` |
| **Criptografia em Trânsito** | TLS 1.2+ | ✅ | Nginx config |
| **Senhas Hasheadas** | bcrypt | ✅ | `core/auth/security.py` |
| **Autenticação 2FA** | pyotp | ✅ | Implementado opcional |
| **Rate Limiting** | slowapi + Redis | ✅ | `core/rate_limit.py` |
| **Headers de Segurança** | CSP, HSTS, etc. | ✅ | `main.py` |
| **Audit Logging** | Todas as ações | ✅ | `core/audit/` |
| **Mascaramento em Logs** | Não implementado | ❌ | CPF/email aparecem em logs |

---

## ⚠️ Riscos LGPD Identificados

### 🔴 CRÍTICO - Resolver em 7 dias

#### 1. Ausência de Endpoint de Exclusão Completa
**Descrição:** Não existe endpoint para exercício do direito ao esquecimento com anonimização de dados relacionados.

**Impacto:** Não conformidade com Art. 18, VI da LGPD. Multa de até 2% do faturamento.

**Ação Requerida:**
```python
# Implementar em LGPDManager:
async def delete_user_data(user_id: UUID) -> DeletionReport:
    """
    1. Anonimizar dados em tabelas relacionadas
    2. Substituir PII por hash irreversível
    3. Manter dados fiscais obrigatórios (máscara)
    4. Gerar relatório de exclusão
    """
```

**Responsável:** Backend Lead
**Prazo:** 7 dias

---

#### 2. Logs Expondo Dados Pessoais
**Descrição:** Logs de aplicação contêm CPF, email e outros PII sem mascaramento.

**Evidência:**
```python
# Código encontrado em audit/access_history.py:
user_email = Column(String(255), nullable=True)  # Email em plaintext
```

**Ação Requerida:**
```python
# Implementar função de mask:
def mask_email(email: str) -> str:
    return email[:3] + "***@" + email.split("@")[1]

def mask_cpf(cpf: str) -> str:
    return "***." + cpf[4:7] + "." + cpf[8:11] + "-**"
```

**Responsável:** Backend Lead
**Prazo:** 7 dias

---

### 🟠 ALTO - Resolver em 30 dias

#### 3. Consentimento para Dados Biométricos
**Descrição:** Dados biométricos de ponto (fingerprint) coletados sem consentimento específico documentado.

**Base Legal Necessária:** Consentimento específico (Art. 11, I LGPD)

**Ação:** Adicionar checkbox específico no cadastro de funcionário:
- [ ] "Autorizo o uso dos meus dados biométricos exclusivamente para registro de ponto"

---

#### 4. Política de Retenção Não Documentada
**Descrição:** Não há documentação clara sobre períodos de retenção por tipo de dado.

**Ação:** Criar `DATA_RETENTION_POLICY.md` com:
- Dados fiscais: 5 anos (obrigatório)
- Dados de funcionários: 10 anos após desligamento (trabalhista)
- Dados de clientes: 5 anos após término contrato
- Logs de auditoria: 2 anos
- Dados de marketing: 2 anos após último contato

---

### 🟡 MÉDIO - Resolver em 90 dias

#### 5. Portabilidade em Múltiplos Formatos
**Descrição:** Apenas JSON disponível. Deveria oferecer CSV e XLSX.

#### 6. Relatório de Compartilhamento
**Descrição:** Não há funcionalidade para gerar relatório de quem recebeu dados do titular.

#### 7. Dados Sensíveis de Saúde
**Descrição:** ASOs armazenados sem criptografia adicional.

---

## 📊 Inventário de Processamento de Dados (RIPD)

### Agentes de Processamento

| Agente | Papel | Dados Processados |
|--------|-------|-------------------|
| Conecta PRO (Controlador) | Operação do ERP | Todos os dados |
| AWS/Cloud (Operador) | Hospedagem | Todos os dados |
| Sólides DP (Operador) | Folha de pagamento | Dados RH |
| Gov.br (Operador) | Login único | Dados cadastrais |
| Evolution API (Operador) | WhatsApp | Telefone, mensagens |

### Finalidades do Processamento

| Finalidade | Base Legal | Dados | Retenção |
|------------|------------|-------|----------|
| Prestação de serviço | Execução de contrato | Cadastrais, operacionais | Durante contrato |
| Folha de pagamento | Obrigação legal | Dados RH, bancários | 10 anos |
| Faturamento | Obrigação legal | CNPJ, endereço fiscal | 5 anos |
| Marketing | Consentimento | Email, telefone | 2 anos ou até revogação |
| Auditoria | Legítimo interesse | Logs de acesso | 2 anos |

---

## ✅ Checklist de Conformidade

### Implementado ✅
- [x] Coleta de consentimento (marketing, processamento)
- [x] Acesso aos dados (endpoint /me)
- [x] Correção de dados (PUT /me)
- [x] Portabilidade parcial (JSON)
- [x] Registro de acessos (audit logs)
- [x] Autenticação segura (bcrypt, JWT)
- [x] Criptografia em trânsito (TLS)
- [x] Rate limiting (proteção contra brute force)

### Pendente ❌
- [ ] Exclusão/anonimização completa
- [ ] Mascaramento em logs
- [ ] Consentimento específico para biométria
- [ ] Política de retenção documentada
- [ ] Portabilidade CSV/XLSX
- [ ] Relatório de compartilhamento
- [ ] Criptografia adicional para dados sensíveis
- [ ] DPO (Data Protection Officer) nomeado
- [ ] Registro de incidentes de segurança

---

## 📋 Recomendações Imediatas

### Semana 1 (Crítico)
1. Implementar endpoint `DELETE /api/v1/me` com anonimização
2. Adicionar mascaramento em todos os logs
3. Revisar permissões de acesso a dados sensíveis

### Mês 1 (Alto)
4. Criar política formal de retenção de dados
5. Implementar consentimento específico para biometria
6. Documentar todos os agentes de processamento

### Trimestre 1 (Médio)
7. Implementar portabilidade CSV/XLSX
8. Adicionar criptografia para ASOs e dados sensíveis
9. Criar relatório de compartilhamento
10. Treinamento da equipe em LGPD

---

## 📚 Referências

- [Lei nº 13.709/2018 - LGPD](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [OWASP Privacy Risks](https://owasp.org/www-project-top-10-privacy-risks/)
- [ISO/IEC 27701:2019](https://www.iso.org/standard/71670.html)

---

**Próxima Revisão:** 2026-03-05
**Documento Version:** 1.0
