# Relatório de Análise de Dependências - Conecta PRO

**Data da Análise:** 05 de Fevereiro de 2026
**Versão do Sistema:** Conecta PRO v2.0
**Responsável:** Análise Automatizada de Segurança

---

## 📋 Resumo Executivo

Este relatório apresenta uma análise completa das dependências do Conecta PRO, identificando vulnerabilidades conhecidas (CVEs), riscos de supply chain e recomendações de atualização prioritárias.

### Status Geral

| Categoria | Status | Críticas | Altas | Médias | Baixas |
|-----------|--------|----------|---------|--------|--------|
| Backend | ⚠️ **ATENÇÃO** | 2 | 1 | 0 | 0 |
| Frontend | 🔴 **CRÍTICO** | 1 | 2 | 0 | 0 |

---

## 🔴 Backend - Python Dependencies

### Tabela de Dependências com CVEs Conhecidos

| Pacote | Versão Atual | Última Versão | CVEs Conhecidas | Severidade | Status |
|--------|-------------|---------------|-----------------|------------|--------|
| **python-jose** | 3.3.0 | 3.4.0 | CVE-2024-33663, CVE-2024-33664, CVE-2025-61152 | 🔴 **CRÍTICA** | ⚠️ VULNERÁVEL |
| fastapi | 0.115.6 | 0.115.8 | Nenhuma direta | 🟢 Nenhuma | ✅ OK |
| sqlalchemy | 2.0.36 | 2.0.48 | Nenhuma direta | 🟢 Nenhuma | ✅ OK |
| uvicorn | 0.34.0 | 0.34.0 | Nenhuma conhecida | 🟢 Nenhuma | ✅ OK |
| pydantic | 2.10.4 | 2.11.0 | Nenhuma direta | 🟢 Nenhuma | ✅ OK |
| celery | 5.4.0 | 5.4.0 | Nenhuma conhecida | 🟢 Nenhuma | ✅ OK |
| redis | 5.2.1 | 5.2.1 | Nenhuma conhecida | 🟢 Nenhuma | ✅ OK |
| bcrypt | 4.2.1 | 4.3.0 | Nenhuma conhecida | 🟢 Nenhuma | ✅ OK |
| cryptography | >=42.0.0 | 44.0.1 | Nenhuma conhecida | 🟢 Nenhuma | ✅ OK |

### Detalhes das Vulnerabilidades Críticas

#### 🔴 CVE-2024-33663 (python-jose)
- **Severidade:** Alta
- **Descrição:** Vulnerabilidade de confusão de algoritmo (Algorithm Confusion) com chaves ECDSA OpenSSH e outros formatos de chave. Permite que um atacante contorne verificações de assinatura criptográfica.
- **CWE:** CWE-327 (Uso de Algoritmo Criptográfico Quebrado ou Arriscado)
- **Impacto:** Bypass de autenticação JWT
- **Correção:** Atualizar para python-jose >= 3.4.0

#### 🔴 CVE-2024-33664 (python-jose)
- **Severidade:** Alta
- **Descrição:** Manipulação inadequada de dados altamente comprimidos (Data Amplification/JWT Bomb). Atacantes podem causar negação de serviço através de tokens JWE craftados com alta taxa de compressão.
- **CWE:** CWE-400 (Consumo de Recursos Não Controlado)
- **Impacto:** DoS via exaustão de recursos
- **Correção:** Atualizar para python-jose >= 3.4.0

#### 🔴 CVE-2025-61152 (python-jose)
- **Severidade:** Crítica
- **Descrição:** Permite tokens JWT com 'alg=none' sejam decodificados e aceitos sem verificação de assinatura criptográfica.
- **Impacto:** Bypass completo de autenticação
- **Correção:** Atualizar imediatamente para python-jose >= 3.4.0

### Dependências Backend Não Utilizadas (Potenciais)

Baseado em análise estática do código:

| Pacote | Justificativa | Recomendação |
|--------|---------------|--------------|
| pyOpenSSL | Não encontrado uso direto no código | Verificar se é dependência transitiva necessária |
| hvac | Integração Vault não detectada | Remover se não estiver em uso |
| psutil | Uso não identificado em monitoramento | Verificar necessidade real |
| scipy | Importado mas uso limitado | Avaliar substituição por numpy puro |

---

## 🔴 Frontend - Node.js Dependencies

### Tabela de Dependências com CVEs Conhecidos

| Pacote | Versão Atual | Última Versão | CVEs Conhecidas | Severidade | Status |
|--------|-------------|---------------|-----------------|------------|--------|
| **next** | 16.1.3 | 16.1.6 | CVE-2025-66478, CVE-2025-55184 | 🔴 **CRÍTICA** | ⚠️ VULNERÁVEL |
| react | 19.2.3 | 19.2.4 | CVE-2025-55182 | 🔴 **CRÍTICA** | ⚠️ VULNERÁVEL |
| react-dom | 19.2.3 | 19.2.4 | CVE-2025-55182 | 🔴 **CRÍTICA** | ⚠️ VULNERÁVEL |
| axios | 1.13.2 | 1.13.4 | Nenhuma direta | 🟢 Nenhuma | ✅ OK |
| zod | 4.3.6 | 3.25.54* | Incompatibilidade de versão | 🟡 Atenção | ⚠️ VERIFICAR |
| jspdf | 4.0.0 | 3.0.1* | Versão suspeita | 🟡 Atenção | ⚠️ VERIFICAR |

*Nota: Versões marcadas com * indicam possível erro de versão no package.json

### Detalhes das Vulnerabilidades Críticas

#### 🔴 CVE-2025-66478 (Next.js)
- **Severidade:** Crítica (CVSS 10.0)
- **Versões Afetadas:** >=15.0.0-canary.0 <15.6.0-canary.61, >=16.0.0-beta.0 <16.1.1-canary.16, >=16.1.1 <16.1.5
- **Descrição:** Remote Code Execution (RCE) no React Server Components. Permite execução de código arbitrário no servidor.
- **Vetor de Ataque:** App Router com React Server Components ativado
- **Correção:** Atualizar para Next.js >= 16.1.6 ou >= 15.6.0

#### 🔴 CVE-2025-55184 (Next.js)
- **Severidade:** Alta
- **Descrição:** Denial of Service via Partial Prerendering resume endpoint quando requisições POST não autenticadas com corpos grandes são processadas.
- **Correção:** Atualizar para Next.js >= 16.1.5

#### 🔴 CVE-2025-55182 (React)
- **Severidade:** Crítica (CVSS 10.0)
- **Descrição:** Remote Code Execution no protocolo Flight usado por React Server Components.
- **Apelido:** "React2Shell"
- **Correção:** Atualizar React e React-DOM para >= 19.2.4

### Dependências Frontend Não Utilizadas

| Pacote | Justificativa | Recomendação |
|--------|---------------|--------------|
| shepherd.js | Tour/onboarding não detectado em uso | Remover se não estiver implementado |
| xlsx | Exportação Excel não encontrada | Verificar necessidade real |
| @lhci/cli | Lighthouse CI - apenas dev | Manter em devDependencies ✅ |
| @playwright/test | Testes E2E não detectados | Mover para devDependencies |

### Inconsistências de Versão Detectadas

| Pacote | Versão Declarada | Última Estável | Problema |
|--------|-----------------|----------------|----------|
| zod | 4.3.6 | 3.25.54 | Versão major incorreta (v4 não existe) |
| jspdf | 4.0.0 | 3.0.1 | Versão não existe na registry |
| @types/node | 25.0.9 | 22.x | Versão major inexistente |

---

## ⚠️ Supply Chain Risks

### Riscos Identificados

| Categoria | Risco | Nível | Mitigação |
|-----------|-------|-------|-----------|
| **Python-JOSE** | Biblioteca de autenticação com múltiplas CVEs críticas | 🔴 Alto | Migrar para `PyJWT` ou `jose-py` |
| **Next.js/React** | Framework core com RCE conhecido | 🔴 Crítico | Atualizar IMEDIATAMENTE |
| **Radix UI** | Múltiplos componentes de UI | 🟡 Médio | Manter atualizado, monitorar CVEs |
| **Axios** | Cliente HTTP popular, alvo frequente | 🟡 Médio | Considerar fetch nativo |
| **xlsx** | Biblioteca não mantida (SheetJS) | 🟡 Médio | Migrar para `exceljs` |

### Dependências de Desenvolvimento com Risco

| Pacote | Risco | Recomendação |
|--------|-------|--------------|
| jsdom | Ambiente DOM simulado - potencial para XSS em testes | Isolar em ambiente de CI |
| msw | Mock Service Worker - intercepta requisições | Não usar em produção |
| vitest | Test runner - manter atualizado | Atualizar para 3.x |

---

## 📋 Recomendações de Atualização Prioritárias

### 🔴 URGENTE (Aplicar Imediatamente)

```bash
# Backend
pip install --upgrade "python-jose[cryptography]>=3.4.0"

# Frontend
npm install next@16.1.6 react@19.2.4 react-dom@19.2.4
```

### 🟡 ALTA PRIORIDADE (Aplicar em 7 dias)

```bash
# Backend
pip install --upgrade \
  fastapi>=0.115.8 \
  sqlalchemy>=2.0.48 \
  pydantic>=2.11.0 \
  bcrypt>=4.3.0 \
  cryptography>=44.0.0

# Frontend - Corrigir versões
npm install zod@^3.25.0 jspdf@^3.0.1 @types/node@^22.0.0
```

### 🟢 MÉDIA PRIORIDADE (Aplicar em 30 dias)

```bash
# Backend
pip install --upgrade \
  celery>=5.5.0 \
  redis>=5.2.1 \
  alembic>=1.15.0

# Frontend
npm update
```

---

## 🔧 Comandos para Validação

### Verificar Vulnerabilidades (Backend)

```bash
# Instalar safety
pip install safety

# Verificar requirements.txt
safety check -r /opt/conecta-pro/backend/requirements.txt

# Verificar ambiente atual
safety check
```

### Verificar Vulnerabilidades (Frontend)

```bash
# Usando npm audit
cd /opt/conecta-pro/frontend
npm audit

# Usando Snyk (requer CLI)
npm install -g snyk
snyk test

# Usando yarn audit (se aplicável)
yarn audit
```

### Verificar Dependências Desatualizadas

```bash
# Backend
pip list --outdated

# Frontend
npm outdated
```

---

## 📊 Matriz de Compatibilidade

| Componente | Versão Atual | Versão Recomendada | Breaking Changes |
|------------|-------------|-------------------|------------------|
| python-jose | 3.3.0 | 3.4.0 | Não esperado |
| next | 16.1.3 | 16.1.6 | Não esperado (patch) |
| react | 19.2.3 | 19.2.4 | Não esperado (patch) |
| fastapi | 0.115.6 | 0.115.8 | Não esperado (patch) |
| sqlalchemy | 2.0.36 | 2.0.48 | Não esperado (patch) |

---

## 🔄 Processo de Atualização Recomendado

1. **Backup** - Criar snapshot do banco de dados e código
2. **Ambiente de Teste** - Aplicar atualizações em staging primeiro
3. **Testes Automatizados** - Executar suite completa de testes
4. **Testes Manuais** - Verificar funcionalidades críticas (auth, pagamentos, etc.)
5. **Deploy Gradual** - Canary deployment se possível
6. **Monitoramento** - Observar métricas e logs por 24h

---

## 📚 Referências

- [Snyk Vulnerability Database](https://security.snyk.io/)
- [NVD - National Vulnerability Database](https://nvd.nist.gov/)
- [GitHub Security Advisories](https://github.com/advisories)
- [CVE-2024-33663 Detail](https://nvd.nist.gov/vuln/detail/CVE-2024-33663)
- [CVE-2024-33664 Detail](https://nvd.nist.gov/vuln/detail/CVE-2024-33664)
- [Next.js Security Advisory](https://nextjs.org/blog/security)

---

## ✅ Checklist de Ação

- [ ] Atualizar python-jose para >= 3.4.0
- [ ] Atualizar Next.js para >= 16.1.6
- [ ] Atualizar React/React-DOM para >= 19.2.4
- [ ] Corrigir versão do zod para 3.x
- [ ] Corrigir versão do jspdf para 3.x
- [ ] Executar `npm audit fix`
- [ ] Executar `safety check`
- [ ] Rodar testes automatizados
- [ ] Realizar testes manuais de autenticação
- [ ] Verificar integrações fiscais (NF-e)
- [ ] Monitorar logs por 48h após deploy

---

**Próxima Revisão:** 05 de Março de 2026

*Este relatório foi gerado automaticamente e deve ser revisado por um especialista em segurança antes de aplicar mudanças em produção.*
