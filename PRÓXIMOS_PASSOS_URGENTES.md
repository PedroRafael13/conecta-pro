# Próximos Passos URGENTES - Conecta PRO
## Ações Imediatas Pós-Integração

**Data:** 26/01/2026 - 04:15 UTC
**Responsável Anterior:** Agente #5 - DevOps
**Status Sistema:** 72% Funcional
**Bloqueadores Críticos:** 1

---

## 🔴 CRÍTICO - Fazer AGORA (< 1h)

### 1. Registrar Routers de Notificações
**Problema:** API de notificações push retorna 404
**Causa:** Routers implementados mas não registrados em `/api/v1/__init__.py`

**Ação:**
```python
# Editar: /opt/conecta-pro/backend/api/v1/__init__.py

# Adicionar no início do arquivo (após outros imports):
from modules.notifications.controllers.notification_controller import router as notification_router

# Adicionar no bloco de registros (linha ~490):
# ===================================================================
# NOTIFICATIONS - SISTEMA DE NOTIFICAÇÕES
# ===================================================================
router.include_router(notification_router, tags=["Notifications - Sistema de Notificações"])
```

**Validação:**
```bash
docker compose restart backend
sleep 20
curl -sL "http://localhost:8080/api/v1/notifications/push" | jq
# Esperado: 401 Unauthorized (não mais 404)
```

---

## 🟡 ALTO - Fazer Hoje (< 4h)

### 2. Criar Seeds de Dados de Teste

**Arquivo:** `/opt/conecta-pro/backend/seeds/dev_data.py`

```python
"""Seeds para ambiente de desenvolvimento."""
from sqlalchemy.orm import Session
from modules.operacional.models import Post, Employee, Scale
from datetime import datetime, timedelta

def seed_dev_data(db: Session):
    """Popula banco com dados de teste."""

    # Postos
    postos = [
        Post(nome="Portaria Principal", codigo="P001", ativo=True),
        Post(nome="Guarita Fundos", codigo="P002", ativo=True),
        Post(nome="Ronda Noturna", codigo="P003", ativo=True),
    ]
    db.add_all(postos)
    db.commit()

    # Colaboradores
    colaboradores = [
        Employee(nome="João Silva", cpf="111.111.111-11", ativo=True),
        Employee(nome="Maria Santos", cpf="222.222.222-22", ativo=True),
        Employee(nome="Pedro Oliveira", cpf="333.333.333-33", ativo=True),
    ]
    db.add_all(colaboradores)
    db.commit()

    # Escalas
    hoje = datetime.now()
    escalas = [
        Scale(
            nome="Escala Janeiro",
            data_inicio=hoje,
            data_fim=hoje + timedelta(days=30),
            posto_id=postos[0].id,
            status="EM_ANDAMENTO"
        ),
    ]
    db.add_all(escalas)
    db.commit()

    print("✅ Seeds criados com sucesso!")
```

**Executar:**
```bash
docker exec -it e5578cd1bf93_conecta-pro-backend python -c "
from seeds.dev_data import seed_dev_data
from database import SessionLocal
db = SessionLocal()
seed_dev_data(db)
db.close()
"
```

### 3. Instalar TypeScript Types

**Problema:** Usando `any` como workaround para Shepherd.js

**Ação:**
```bash
cd /opt/conecta-pro/frontend
npm install --save-dev @types/shepherd.js
```

**Se não existir @types:**
Criar `/opt/conecta-pro/frontend/src/types/shepherd.d.ts`:
```typescript
declare module 'shepherd.js' {
  export default class Shepherd {
    static Tour: any;
  }
}
```

**Rebuild:**
```bash
npm run build
docker compose build frontend --no-cache
docker compose up -d frontend
```

### 4. Testes E2E Básicos

**Criar:** `/opt/conecta-pro/tests/e2e/basic_flow.test.ts`

```typescript
import { test, expect } from '@playwright/test';

test('Login e Dashboard', async ({ page }) => {
  await page.goto('http://localhost:3001/login');
  await page.fill('input[name="email"]', 'admin@conectaplus.com.br');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.locator('h1')).toContainText('Dashboard');
});

test('Busca Global (Atalho /)', async ({ page }) => {
  await page.goto('http://localhost:3001/modulos/operacional');
  await page.keyboard.press('/');

  const searchModal = page.locator('[role="dialog"]');
  await expect(searchModal).toBeVisible();

  await page.fill('input[type="search"]', 'João');
  await page.waitForTimeout(500);

  // Verificar resultados
  const results = page.locator('.search-results');
  await expect(results).toBeVisible();
});

test('Command Palette (Ctrl+K)', async ({ page }) => {
  await page.goto('http://localhost:3001/modulos/operacional');
  await page.keyboard.press('Control+K');

  const palette = page.locator('[role="dialog"]');
  await expect(palette).toBeVisible();
});
```

**Executar:**
```bash
npm install --save-dev @playwright/test
npx playwright test
```

---

## 🟢 MÉDIO - Fazer Esta Semana

### 5. Verificar Console Browser
- Abrir DevTools em http://localhost:3001
- Verificar aba Console
- Documentar erros JavaScript
- Documentar warnings

### 6. Performance Audit
```bash
npm install -g lighthouse
lighthouse http://localhost:3001 --output=html --output-path=./lighthouse-report.html
```

**Métricas esperadas:**
- Performance: > 80
- Accessibility: > 90
- Best Practices: > 85
- SEO: > 80

### 7. Teste Manual de Features

**Checklist:**
- [ ] Login funciona
- [ ] Dashboard carrega KPIs
- [ ] Busca global (/) funciona
- [ ] Command Palette (Ctrl+K) abre
- [ ] Atalhos Alt+1, Alt+2 navegam
- [ ] Modo escuro (toggle) funciona
- [ ] Notificações aparecem
- [ ] Templates de escalas listam
- [ ] Criar template funciona
- [ ] Aplicar template funciona
- [ ] Exportar para Excel funciona
- [ ] Exportar para PDF funciona
- [ ] Auto-save em formulários
- [ ] Tour de onboarding inicia
- [ ] Mobile responsivo

### 8. Atualizar CLAUDE.md

Adicionar seção:
```markdown
## Sessão 20 - Integração e Testes (Agente #5)

### Status Pós-Integração
- ✅ Rebuild completo concluído
- ✅ 72% features funcionais
- ⚠️ 1 bloqueador crítico (notificações)
- ⚠️ Necessário seeds de teste

### Bloqueadores
1. **Notificações Push:** Router não registrado (P0)
2. **TypeScript Types:** Shepherd.js sem @types (P1)
3. **Dados Teste:** Banco vazio (P1)

### Ações Imediatas
Ver: /opt/conecta-pro/PRÓXIMOS_PASSOS_URGENTES.md
```

---

## Comandos Úteis

### Verificar Status
```bash
docker compose ps
docker logs e5578cd1bf93_conecta-pro-backend --tail=50
docker logs conecta-pro-frontend --tail=50
```

### Restart Rápido
```bash
docker compose restart backend frontend
```

### Rebuild Específico
```bash
docker compose build backend --no-cache
docker compose up -d backend
```

### Testes Rápidos de API
```bash
# Health
curl -sL http://localhost:8080/health | jq

# Busca
curl -sL "http://localhost:8080/api/v1/search?q=teste" | jq

# KPI
curl -sL "http://localhost:8080/api/v1/operacional/kpi-trends?period=7d" | jq

# Templates (requer auth)
curl -sL "http://localhost:8080/api/v1/operacional/scales/templates" | jq

# Notificações (404 - CORRIGIR!)
curl -sL "http://localhost:8080/api/v1/notifications/push" | jq
```

---

## Prioridades

1. **AGORA:** Registrar router notificações (15 min)
2. **HOJE:** Seeds de teste (1h)
3. **HOJE:** Testes E2E básicos (2h)
4. **AMANHÃ:** Types TypeScript (30 min)
5. **AMANHÃ:** Performance audit (1h)
6. **ESTA SEMANA:** Testes manuais completos (4h)

---

## Métricas de Sucesso

**Quando considerar 100%:**
- [ ] Todas APIs respondem 200/401 (não 404)
- [ ] Console browser sem erros
- [ ] Lighthouse > 80 em todas métricas
- [ ] Todos atalhos funcionando
- [ ] Dados de teste criados
- [ ] Testes E2E passando
- [ ] Documentação atualizada

---

**Criado por:** Agente #5
**Para:** Próximo agente ou desenvolvedor
**Urgência:** ALTA
**Estimativa:** 6-8h de trabalho total

**BOA SORTE! 🚀**
