# PATCH 01: Verificação de Atualização de Dependências

> Checklist de validação para atualização de dependências críticas (CVEs)

---

## 📋 Pré-requisitos

- [ ] Backup dos arquivos originais criado
- [ ] Ambiente de desenvolvimento configurado
- [ ] Acesso ao repositório git (para rollback se necessário)

---

## ✅ Checklist de Verificação

### 1. Verificação de Versões

#### Backend (Python)
```bash
# Verificar versão do python-jose
pip show python-jose | grep Version

# Esperado: Version: 3.4.0 ou superior
# Resultado aceitável: 3.4.0, 3.4.1, 3.5.0, etc.
# Resultado NÃO aceitável: 3.3.0 ou anterior
```

**Comando de validação automatizado:**
```bash
python -c "import jose; assert jose.__version__ >= '3.4.0', f'Versão {jose.__version__} não atende requisito'"
```

#### Frontend (Node.js)
```bash
# Verificar versões instaladas
cd /opt/conecta-pro/frontend
npm list next react react-dom --depth=0

# Esperado:
# next@16.1.6
# react@19.2.4
# react-dom@19.2.4
```

### 2. Auditoria de Segurança (npm audit)

```bash
cd /opt/conecta-pro/frontend

# Verificar vulnerabilidades críticas
npm audit --audit-level=critical

# Esperado: 0 vulnerabilidades críticas
# Resultado NÃO aceitável: Qualquer CVE crítico em next/react
```

**Ignorar vulnerabilidades conhecidas e aceitáveis:**
- Dev dependencies (jest, eslint) - Não afetam produção
- CVEs em pacotes não utilizados em runtime

### 3. Testes de Compatibilidade

#### Backend
```bash
cd /opt/conecta-pro/backend

# Verificar se aplicação inicia
python -c "from jose import jwt; print('python-jose OK')"

# Testar importação de módulos críticos
python -c "
from core.auth.jwt import create_access_token, verify_token
print('JWT imports OK')
"
```

#### Frontend
```bash
cd /opt/conecta-pro/frontend

# Verificar build (sem erros de tipo)
npm run type-check 2>&1 | head -50

# Esperado: 0 erros ou apenas erros pré-existentes não relacionados
# Atenção: Não deve haver erros relacionados a 'next' ou 'react'
```

### 4. Testes Funcionais

#### Autenticação JWT (python-jose)
```bash
# Iniciar backend
cd /opt/conecta-pro/backend
uvicorn main:app --reload --port 8080 &

# Testar login (ajuste os dados conforme necessário)
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'

# Esperado: Retorno de access_token e refresh_token válidos
# Validar estrutura do token JWT em https://jwt.io
```

#### Aplicação Frontend
```bash
# Iniciar frontend
cd /opt/conecta-pro/frontend
npm run dev &

# Verificar se aplicação inicia sem erros
# Acessar: http://localhost:3000

# Validar:
# [ ] Página de login carrega
# [ ] Navegação funciona
# [ ] Nenhum erro 500 no console
# [ ] Nenhum warning crítico de React
```

### 5. Testes E2E (Se disponíveis)

```bash
cd /opt/conecta-pro/frontend

# Executar testes críticos
npm run test:e2e:core 2>/dev/null || npm run test:e2e 2>/dev/null || echo "Testes E2E não configurados"

# Validar:
# [ ] Testes de login passam
# [ ] Testes de navegação passam
# [ ] Nenhum erro relacionado a next/react
```

---

## 🔍 Validação de CVEs Corrigidos

### CVE-2024-33663 (python-jose - Algorithm Confusion)

**Teste de validação:**
```python
# Tentar criar token com alg=none (deve falhar em >= 3.4.0)
python -c "
from jose import jwt
from jose.exceptions import JWTError

try:
    # Token com alg=none (inseguro)
    token = 'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjMifQ.'
    jwt.decode(token, 'secret', algorithms=['HS256'])
    print('⚠️ VULNERÁVEL: Token alg=none foi aceito')
except JWTError:
    print('✓ PROTEGIDO: Token alg=none rejeitado')
"
```

**Esperado:** ✅ `PROTEGIDO: Token alg=none rejeitado`

### CVE-2025-66478 (Next.js - RCE)

**Verificação:**
```bash
# Verificar se Next.js está atualizado
npm list next --depth=0 | grep "next@16.1.6"

# Se versão < 16.1.6, ainda vulnerável
```

### CVE-2025-55182 (React - React2Shell)

**Verificação:**
```bash
# Verificar se React está atualizado
npm list react --depth=0 | grep "react@19.2.4"

# Se versão < 19.2.4, ainda vulnerável
```

---

## 🚨 Rollback (Em caso de problemas)

Se algo der errado, execute o rollback:

```bash
# Restaurar backups
BACKUP_DIR="/opt/conecta-pro/docs/patches/backups_YYYYMMDD_HHMMSS"

cp "$BACKUP_DIR/requirements.txt.bak" /opt/conecta-pro/backend/requirements.txt
cp "$BACKUP_DIR/package.json.bak" /opt/conecta-pro/frontend/package.json

# Reinstalar dependências antigas
cd /opt/conecta-pro/backend
pip install -r requirements.txt

cd /opt/conecta-pro/frontend
npm install
```

---

## ✅ Aprovação Final

| Item | Status | Responsável | Data |
|------|--------|-------------|------|
| Versões atualizadas | ⬜ | | |
| npm audit limpo | ⬜ | | |
| Backend inicia | ⬜ | | |
| Frontend builda | ⬜ | | |
| Login JWT funciona | ⬜ | | |
| Testes E2E passam | ⬜ | | |
| CVEs corrigidos | ⬜ | | |

**Aprovado por:** _________________ **Data:** _________________

---

## 📚 Referências

- [CVE-2024-33663](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-33663) - python-jose algorithm confusion
- [CVE-2024-33664](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-33664) - python-jose JWT bomb
- [CVE-2025-66478](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-66478) - Next.js RCE
- [CVE-2025-55182](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-55182) - React2Shell
