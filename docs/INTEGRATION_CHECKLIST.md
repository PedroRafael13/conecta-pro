# Checklist de Integração - Quick Wins Fase 1
**Para:** Desenvolvedores que vão completar as features
**Criado por:** Agente #10 - QA
**Data:** 2026-01-26

---

## 🎯 Como Usar Este Checklist

1. Escolha uma feature da lista abaixo
2. Siga os passos na ordem
3. Marque ✅ cada item completado
4. Teste antes de marcar feature como DONE
5. Faça commit incremental (não espere tudo pronto)

---

## Feature 1: Templates de Escalas

### Backend
- [ ] **1.1. Criar ScaleTemplateService**
  - [ ] Arquivo: `/backend/modules/operacional/services/scale_template_service.py`
  - [ ] Métodos necessários:
    ```python
    async def create_template(data, tenant_id, user_id) -> ScaleTemplate
    async def update_template(id, data, tenant_id) -> ScaleTemplate
    async def delete_template(id, tenant_id) -> bool
    async def get_template(id, tenant_id) -> ScaleTemplate
    async def list_templates(tenant_id, filters) -> List[ScaleTemplate]
    async def apply_template(id, apply_data, tenant_id, user_id) -> Scale
    async def preview_template(id, apply_data, tenant_id) -> Scale
    async def create_from_scale(scale_id, name, tenant_id, user_id) -> ScaleTemplate
    async def get_stats(tenant_id) -> ScaleTemplateStats
    ```
  - [ ] Usar `ScaleTemplateRepository` já existente
  - [ ] Adicionar validações de negócio
  - [ ] Logging apropriado

- [ ] **1.2. Criar ScaleTemplateController**
  - [ ] Arquivo: `/backend/modules/operacional/controllers/scale_template_controller.py`
  - [ ] Endpoints REST:
    ```python
    GET    /api/v1/operacional/scale-templates
    GET    /api/v1/operacional/scale-templates/:id
    POST   /api/v1/operacional/scale-templates
    PUT    /api/v1/operacional/scale-templates/:id
    DELETE /api/v1/operacional/scale-templates/:id
    POST   /api/v1/operacional/scale-templates/:id/apply
    POST   /api/v1/operacional/scale-templates/:id/preview
    POST   /api/v1/operacional/scale-templates/from-scale
    GET    /api/v1/operacional/scale-templates/stats
    ```
  - [ ] Usar `ScaleTemplateService`
  - [ ] Autenticação: `Depends(get_current_user)`
  - [ ] Validação de tenant
  - [ ] Error handling apropriado

- [ ] **1.3. Registrar Rotas**
  - [ ] Abrir: `/backend/modules/operacional/__init__.py`
  - [ ] Importar: `from .controllers.scale_template_controller import router as scale_template_router`
  - [ ] Adicionar ao app: `app.include_router(scale_template_router)`

- [ ] **1.4. Testar Backend**
  ```bash
  # Listar templates
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8080/api/v1/operacional/scale-templates

  # Criar template
  curl -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Template Teste","template_data":{...}}' \
    http://localhost:8080/api/v1/operacional/scale-templates
  ```

### Frontend
- [ ] **1.5. Criar Service**
  - [ ] Arquivo já existe: `/frontend/src/lib/services/scale-templates.ts`
  - [ ] Verificar se está chamando endpoints corretos
  - [ ] Adicionar tratamento de erros

- [ ] **1.6. Criar UI - Listagem**
  - [ ] Arquivo: `/frontend/src/app/modulos/operacional/templates/page.tsx`
  - [ ] Usar hook: `const { templates, total, isLoading } = useTemplates()`
  - [ ] Tabela com colunas: Nome, Descrição, Vezes Usado, Última Uso, Ações
  - [ ] Botões: Ver, Editar, Aplicar, Deletar
  - [ ] Filtros: Nome, Mostrar inativos
  - [ ] Paginação

- [ ] **1.7. Criar UI - Modal Criar/Editar**
  - [ ] Component: `<TemplateFormModal />`
  - [ ] Campos:
    - Nome (required)
    - Descrição
    - Tipo de escala
    - Postos (multi-select)
    - Padrões de turnos (lista editável)
  - [ ] Validações
  - [ ] Loading state
  - [ ] Error handling

- [ ] **1.8. Criar UI - Modal Aplicar**
  - [ ] Component: `<TemplateApplyModal />`
  - [ ] Campos:
    - Template (select)
    - Mês/Ano da nova escala
    - Posto (se diferente)
    - Mapeamento de funcionários (opcional)
  - [ ] Preview antes de aplicar
  - [ ] Confirmação

- [ ] **1.9. Integrar em Escalas**
  - [ ] Abrir: `/frontend/src/app/modulos/operacional/escalas/page.tsx`
  - [ ] Adicionar botão: "Aplicar Template"
  - [ ] Ao abrir modal de criar escala, mostrar opção "Usar Template"

- [ ] **1.10. Adicionar "Salvar como Template"**
  - [ ] Em: `/frontend/src/app/modulos/operacional/escalas/[id]/page.tsx`
  - [ ] Botão: "Salvar como Template"
  - [ ] Modal com nome e descrição
  - [ ] Usar `createFromScale` mutation

### Testes
- [ ] **1.11. Teste Manual**
  - [ ] Criar template do zero
  - [ ] Criar template de escala existente
  - [ ] Listar templates
  - [ ] Editar template
  - [ ] Aplicar template (criar nova escala)
  - [ ] Deletar template
  - [ ] Verificar contadores (times_used, last_used)

- [ ] **1.12. Teste de Regressão**
  - [ ] Criar escala normal (sem template) ainda funciona
  - [ ] Editar escala normal ainda funciona

---

## Feature 2: Auto-save em Formulários

### Frontend
- [ ] **2.1. Integrar em Formulário de Postos**
  - [ ] Abrir: `/frontend/src/app/modulos/operacional/postos/page.tsx`
  - [ ] Importar hook:
    ```tsx
    import { useAutoSave } from '@/hooks/useAutoSave';
    ```
  - [ ] No component do modal:
    ```tsx
    const autoSave = useAutoSave({
      key: 'posto_form',
      data: formData,
      enabled: isOpen && !isEditing,
      debounceMs: 2000,
    });
    ```
  - [ ] Adicionar indicador visual:
    ```tsx
    {autoSave.saving && <span>Salvando...</span>}
    {autoSave.lastSaved && <span>Salvo às {format(autoSave.lastSaved, 'HH:mm')}</span>}
    ```
  - [ ] Ao abrir modal, verificar rascunho:
    ```tsx
    useEffect(() => {
      if (isOpen && !isEditing) {
        const draft = autoSave.restore();
        if (draft) {
          setShowRestoreAlert(true);
        }
      }
    }, [isOpen]);
    ```
  - [ ] Alert de restauração:
    ```tsx
    <RestoreAlert
      hasDraft={autoSave.hasDraft}
      onRestore={() => {
        const draft = autoSave.restore();
        setFormData(draft);
        setShowRestoreAlert(false);
      }}
      onDiscard={() => {
        autoSave.clear();
        setShowRestoreAlert(false);
      }}
    />
    ```
  - [ ] Ao salvar com sucesso, limpar rascunho:
    ```tsx
    const handleSave = async () => {
      await api.createPosto(formData);
      autoSave.clear(); // Limpar rascunho
      onClose();
    };
    ```

- [ ] **2.2. Integrar em Formulário de Escalas**
  - [ ] Repetir processo acima em: `/frontend/src/components/operacional/scale-editor.tsx`
  - [ ] Key: `'escala_form'`

- [ ] **2.3. Integrar em Formulário de Ocorrências**
  - [ ] Repetir em: `/frontend/src/components/operacional/occurrence-form-modal.tsx`
  - [ ] Key: `'ocorrencia_form'`

### Testes
- [ ] **2.4. Teste Manual**
  - [ ] Abrir formulário de Posto
  - [ ] Digitar dados
  - [ ] Aguardar 2s → Ver "Salvando..."
  - [ ] Ver "Salvo às HH:MM"
  - [ ] Fechar modal sem salvar
  - [ ] Reabrir modal → Alert de rascunho aparece
  - [ ] Clicar "Restaurar" → Dados preenchidos
  - [ ] Salvar formulário → Rascunho limpo
  - [ ] Reabrir modal → Sem alert (rascunho foi limpo)

---

## Feature 3: Atalhos de Teclado

### Frontend
- [ ] **3.1. Integrar useGlobalShortcuts**
  - [ ] Abrir: `/frontend/src/app/layout.tsx`
  - [ ] Adicionar state:
    ```tsx
    'use client';
    const [searchOpen, setSearchOpen] = useState(false);
    const [paletteOpen, setPaletteOpen] = useState(false);
    const [helpOpen, setHelpOpen] = useState(false);
    ```
  - [ ] Integrar hook:
    ```tsx
    import { useGlobalShortcuts } from '@/hooks/useKeyboardShortcuts';

    useGlobalShortcuts({
      onSearchOpen: () => setSearchOpen(true),
      onCommandPaletteOpen: () => setPaletteOpen(true),
      onHelpOpen: () => setHelpOpen(true),
    });
    ```

- [ ] **3.2. Criar Help Overlay**
  - [ ] Component: `/frontend/src/components/ui/help-overlay.tsx`
  - [ ] Modal com lista de atalhos:
    ```tsx
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <h2>Atalhos de Teclado</h2>
        <div className="grid gap-2">
          <ShortcutRow keys={["/"]}>Busca Global</ShortcutRow>
          <ShortcutRow keys={["Ctrl", "K"]}>Command Palette</ShortcutRow>
          <ShortcutRow keys={["Ctrl", "B"]}>Toggle Sidebar</ShortcutRow>
          <ShortcutRow keys={["Alt", "1"]}>Dashboard</ShortcutRow>
          <ShortcutRow keys={["Alt", "2"]}>Operacional</ShortcutRow>
          <ShortcutRow keys={["Shift", "?"]}>Esta ajuda</ShortcutRow>
        </div>
      </DialogContent>
    </Dialog>
    ```
  - [ ] Usar em layout:
    ```tsx
    <HelpOverlay open={helpOpen} onClose={() => setHelpOpen(false)} />
    ```

- [ ] **3.3. Adicionar Badge de Atalho**
  - [ ] Em botões importantes, mostrar atalho:
    ```tsx
    <Button>
      Buscar
      <Badge variant="outline" className="ml-2">/</Badge>
    </Button>
    ```

### Testes
- [ ] **3.4. Teste Manual**
  - [ ] Pressionar `/` → Modal de busca abre
  - [ ] Pressionar `Ctrl+K` → Command palette abre
  - [ ] Pressionar `Ctrl+B` → Sidebar fecha/abre
  - [ ] Pressionar `Alt+1` → Navega para Dashboard
  - [ ] Pressionar `Shift+?` → Help overlay abre
  - [ ] Atalhos NÃO funcionam em inputs/textareas
  - [ ] Atalhos funcionam em qualquer tela

---

## Feature 4: Dark Mode Toggle

### Frontend
- [ ] **4.1. Criar ThemeContext**
  - [ ] Arquivo: `/frontend/src/contexts/ThemeContext.tsx`
  - [ ] Code:
    ```tsx
    'use client';
    import { createContext, useContext, useEffect, useState } from 'react';

    type Theme = 'light' | 'dark';

    const ThemeContext = createContext<{
      theme: Theme;
      setTheme: (theme: Theme) => void;
    }>({
      theme: 'dark',
      setTheme: () => {},
    });

    export function ThemeProvider({ children }: { children: React.ReactNode }) {
      const [theme, setTheme] = useState<Theme>('dark');

      useEffect(() => {
        const saved = localStorage.getItem('theme') as Theme;
        if (saved) setTheme(saved);
      }, []);

      useEffect(() => {
        document.documentElement.classList.toggle('dark', theme === 'dark');
        localStorage.setItem('theme', theme);
      }, [theme]);

      return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
          {children}
        </ThemeContext.Provider>
      );
    }

    export const useTheme = () => useContext(ThemeContext);
    ```

- [ ] **4.2. Integrar ThemeProvider**
  - [ ] Abrir: `/frontend/src/contexts/providers.tsx`
  - [ ] Adicionar:
    ```tsx
    import { ThemeProvider } from './ThemeContext';

    export function Providers({ children }) {
      return (
        <ThemeProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </ThemeProvider>
      );
    }
    ```

- [ ] **4.3. Remover Hardcoded Dark**
  - [ ] Abrir: `/frontend/src/app/layout.tsx`
  - [ ] Mudar de:
    ```tsx
    <html lang="pt-BR" className="dark">
    ```
  - [ ] Para:
    ```tsx
    <html lang="pt-BR">
    ```

- [ ] **4.4. Criar ThemeToggle Component**
  - [ ] Arquivo: `/frontend/src/components/ui/theme-toggle.tsx`
  - [ ] Code:
    ```tsx
    'use client';
    import { Moon, Sun } from 'lucide-react';
    import { Button } from './button';
    import { useTheme } from '@/contexts/ThemeContext';

    export function ThemeToggle() {
      const { theme, setTheme } = useTheme();

      return (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          <span className="sr-only">Alternar tema</span>
        </Button>
      );
    }
    ```

- [ ] **4.5. Adicionar Toggle no Header**
  - [ ] Encontrar header principal (dashboard ou modulos layout)
  - [ ] Adicionar:
    ```tsx
    import { ThemeToggle } from '@/components/ui/theme-toggle';

    <header>
      {/* ... outros items ... */}
      <ThemeToggle />
    </header>
    ```

- [ ] **4.6. Verificar Variáveis CSS Light Mode**
  - [ ] Abrir: `/frontend/src/styles/globals.css`
  - [ ] Garantir que existem variáveis para ambos os modos:
    ```css
    :root {
      --background: 0 0% 100%;
      --foreground: 222.2 84% 4.9%;
      /* ... */
    }

    .dark {
      --background: 222.2 84% 4.9%;
      --foreground: 210 40% 98%;
      /* ... */
    }
    ```

### Testes
- [ ] **4.7. Teste Manual**
  - [ ] Clicar no toggle → Tema muda de dark para light
  - [ ] Clicar novamente → Volta para dark
  - [ ] Recarregar página → Tema persiste
  - [ ] Testar em navegador anônimo → Padrão dark
  - [ ] Todas as cores adaptam corretamente
  - [ ] Texto legível em ambos os modos

---

## Feature 5: Sparklines em KPIs

### Backend
- [ ] **5.1. Criar Endpoint de Dados Históricos**
  - [ ] Arquivo: `/backend/modules/operacional/controllers/dashboard_controller.py`
  - [ ] Adicionar endpoint:
    ```python
    @router.get("/kpi-history/{kpi_name}")
    async def get_kpi_history(
        kpi_name: str,
        days: int = 30,
        tenant_id: str = Depends(get_tenant_id),
        db: AsyncSession = Depends(get_db),
    ):
        """Retorna histórico de um KPI para sparklines."""
        if kpi_name == "coverage_rate":
            return await get_coverage_history(tenant_id, days, db)
        elif kpi_name == "monthly_hours":
            return await get_hours_history(tenant_id, days, db)
        # ...
    ```
  - [ ] Implementar queries de histórico

### Frontend
- [ ] **5.2. Criar Component Sparkline**
  - [ ] Arquivo: `/frontend/src/components/ui/sparkline.tsx`
  - [ ] Code:
    ```tsx
    import { LineChart, Line, ResponsiveContainer } from 'recharts';

    interface SparklineProps {
      data: { value: number }[];
      color?: string;
      height?: number;
    }

    export function Sparkline({ data, color = '#10b981', height = 20 }: SparklineProps) {
      return (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data}>
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      );
    }
    ```

- [ ] **5.3. Criar Hook para KPI History**
  - [ ] Arquivo: `/frontend/src/hooks/useKPIHistory.ts`
  - [ ] Code:
    ```tsx
    export function useKPIHistory(kpiName: string, days: number = 30) {
      return useQuery({
        queryKey: ['kpi-history', kpiName, days],
        queryFn: async () => {
          const res = await api.get(`/api/v1/operacional/dashboard/kpi-history/${kpiName}?days=${days}`);
          return res.data;
        },
        staleTime: 5 * 60 * 1000, // 5min
      });
    }
    ```

- [ ] **5.4. Integrar em Dashboard**
  - [ ] Abrir: `/frontend/src/app/modulos/operacional/page.tsx`
  - [ ] Buscar dados históricos:
    ```tsx
    const { data: coverageHistory } = useKPIHistory('coverage_rate', 7);
    const { data: hoursHistory } = useKPIHistory('monthly_hours', 30);
    ```
  - [ ] Adicionar sparkline nos cards:
    ```tsx
    <div className="bg-[hsl(var(--card))] p-4">
      <div className="flex items-start justify-between">
        <Activity className="w-5 h-5" />
        <TrendingUp className="w-4 h-4" />
      </div>
      <p className="text-2xl font-bold">{coverageRate}%</p>
      <p className="text-xs text-muted-foreground">Cobertura de Postos</p>
      {coverageHistory && (
        <div className="mt-2">
          <Sparkline
            data={coverageHistory}
            color={coverageRate >= 90 ? '#10b981' : '#ef4444'}
            height={20}
          />
        </div>
      )}
    </div>
    ```

### Testes
- [ ] **5.5. Teste Manual**
  - [ ] Dashboard carrega com sparklines
  - [ ] Gráficos mostram tendência correta
  - [ ] Cores adaptam ao valor (verde/amarelo/vermelho)
  - [ ] Hover mostra tooltip (opcional)
  - [ ] Performance OK (não trava)

---

## 🎯 Ordem Recomendada de Implementação

### Sprint 1 (Semana 1)
1. **Templates de Escalas** (Passo 1.1 a 1.4) - Backend
2. **Auto-save** (Passo 2.1 a 2.3) - Frontend
3. **Atalhos Teclado** (Passo 3.1 a 3.3) - Frontend

### Sprint 2 (Semana 2)
4. **Templates UI** (Passo 1.5 a 1.10) - Frontend
5. **Dark Mode** (Passo 4.1 a 4.6) - Frontend
6. **Sparklines** (Passo 5.1 a 5.4) - Full-stack

### Sprint 3 (Semana 3)
7. **Testes completos** (Passos *.11, *.12)
8. **Performance audit**
9. **Deploy staging**

---

## ✅ Definition of Done

Uma feature só está DONE quando:

- [ ] Backend implementado E testado (se aplicável)
- [ ] Frontend implementado E testado
- [ ] Integração frontend ↔ backend funcionando
- [ ] Usuário consegue usar a feature via UI
- [ ] Testes manuais passando
- [ ] Sem errors no console
- [ ] Performance aceitável
- [ ] Code review aprovado
- [ ] Documentação atualizada
- [ ] Commit + push realizado

**NÃO** marcar como done se:
- ❌ Código existe mas não está integrado
- ❌ Backend OK mas frontend não consome
- ❌ UI criada mas dados mockados
- ❌ Funciona só no localhost do dev
- ❌ Não foi testado por outra pessoa

---

## 🚨 Alertas Importantes

### Antes de Começar
1. **Fazer backup do banco:**
   ```bash
   docker exec conecta-pro-postgres pg_dump -U postgres conecta_pro > backup_$(date +%Y%m%d).sql
   ```

2. **Criar branch:**
   ```bash
   git checkout -b feature/quick-wins-integration
   ```

3. **Verificar que serviços estão UP:**
   ```bash
   docker ps --format "table {{.Names}}\t{{.Status}}"
   ```

### Durante Desenvolvimento
1. **Commitar incrementalmente:** Não esperar tudo pronto
2. **Testar a cada mudança:** Não acumular código não testado
3. **Consultar este checklist:** Marcar items conforme avança

### Ao Finalizar Feature
1. **Demo para colega:** Mostrar funcionando
2. **Merge request:** Code review obrigatório
3. **Atualizar docs:** README, CHANGELOG
4. **Notificar QA:** Para teste formal

---

**Última atualização:** 2026-01-26
**Mantido por:** Agente #10
**Dúvidas:** Consultar /docs/QA_INTEGRATION_REPORT.md
