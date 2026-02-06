# Exemplos de Uso - Módulo CONFIG

## Casos de Uso Comuns

### 1. Gestão de Tenants

#### Listar Tenants Ativos
```typescript
import { useTenants } from '@/hooks/useConfig';

function TenantsListPage() {
  const { data, isLoading, error } = useTenants({
    status: 'active',
    limit: 50,
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h1>Tenants Ativos: {data?.total}</h1>
      {data?.items.map((tenant) => (
        <TenantCard key={tenant.id} tenant={tenant} />
      ))}
    </div>
  );
}
```

#### Criar Novo Tenant
```typescript
import { useCreateTenant } from '@/hooks/useConfig';

function CreateTenantForm() {
  const createMutation = useCreateTenant();

  const handleSubmit = async (values) => {
    await createMutation.mutateAsync({
      name: values.name,
      slug: values.slug,
      plan: 'trial',
      tenant_type: 'condominium',
      email: values.email,
      phone: values.phone,
    });
    // Toast automático de sucesso
    // Cache invalidado automaticamente
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ... campos ... */}
      <button
        type="submit"
        disabled={createMutation.isPending}
      >
        {createMutation.isPending ? 'Criando...' : 'Criar Tenant'}
      </button>
    </form>
  );
}
```

#### Converter Trial para Pago
```typescript
import { useConvertTrialTenant } from '@/hooks/useConfig';

function ConvertTrialButton({ tenantId }) {
  const convertMutation = useConvertTrialTenant();

  const handleConvert = async () => {
    await convertMutation.mutateAsync(tenantId);
  };

  return (
    <button
      onClick={handleConvert}
      disabled={convertMutation.isPending}
    >
      Converter para Plano Pago
    </button>
  );
}
```

### 2. Feature Flags

#### Verificar Feature Flag
```typescript
import { useEvaluateFeatureFlag } from '@/hooks/useConfig';

function FeatureComponent() {
  const { data: evaluation } = useEvaluateFeatureFlag({
    flag_key: 'new_dashboard',
    context: {
      tenant_id: currentTenantId,
      user_id: currentUserId,
    },
  });

  if (!evaluation?.enabled) {
    return <OldDashboard />;
  }

  return <NewDashboard />;
}
```

#### Configurar Gradual Rollout
```typescript
import { useSetGradualRollout } from '@/hooks/useConfig';

function FeatureFlagRolloutPanel({ flagId }) {
  const rolloutMutation = useSetGradualRollout();

  const handleRollout = async (percentage) => {
    await rolloutMutation.mutateAsync({
      id: flagId,
      rollout: {
        start_percentage: 0,
        target_percentage: percentage,
        increment_percentage: 10,
        increment_interval_hours: 24,
      },
    });
  };

  return (
    <div>
      <h3>Gradual Rollout</h3>
      <button onClick={() => handleRollout(25)}>25%</button>
      <button onClick={() => handleRollout(50)}>50%</button>
      <button onClick={() => handleRollout(100)}>100%</button>
    </div>
  );
}
```

### 3. Configurações de Tenant

#### Obter Valor de Configuração
```typescript
import { useTenantSettings } from '@/hooks/useConfig';
import { getSettingValue } from '@/services/config';

function NotificationSettings({ tenantId }) {
  const { data: settings } = useTenantSettings(tenantId, {
    category: 'notifications',
  });

  const emailEnabled = getSettingValue(
    settings?.items || [],
    'notifications.email.enabled',
    true
  );

  return (
    <div>
      <p>Email Notifications: {emailEnabled ? 'Enabled' : 'Disabled'}</p>
    </div>
  );
}
```

#### Atualizar Configuração
```typescript
import { useUpdateTenantSettingValue } from '@/hooks/useConfig';

function SettingToggle({ settingId, currentValue }) {
  const updateMutation = useUpdateTenantSettingValue();

  const handleToggle = async () => {
    await updateMutation.mutateAsync({
      id: settingId,
      value: { value: !currentValue },
    });
  };

  return (
    <Switch checked={currentValue} onCheckedChange={handleToggle} />
  );
}
```

### 4. Notification Templates

#### Listar Templates por Canal
```typescript
import { useNotificationTemplates } from '@/hooks/useConfig';

function TemplatesList() {
  const { data: emailTemplates } = useNotificationTemplates({
    channel: 'email',
    status: 'active',
  });

  const { data: smsTemplates } = useNotificationTemplates({
    channel: 'sms',
    status: 'active',
  });

  return (
    <div>
      <section>
        <h2>Email Templates ({emailTemplates?.total})</h2>
        <TemplateGrid templates={emailTemplates?.items} />
      </section>
      <section>
        <h2>SMS Templates ({smsTemplates?.total})</h2>
        <TemplateGrid templates={smsTemplates?.items} />
      </section>
    </div>
  );
}
```

#### Renderizar Template com Preview
```typescript
import { useRenderNotificationTemplate } from '@/hooks/useConfig';

function TemplatePreview({ templateId }) {
  const [variables, setVariables] = useState({
    user_name: 'João Silva',
    action_date: '2026-01-28',
  });

  const renderMutation = useRenderNotificationTemplate();

  const handleRender = async () => {
    const result = await renderMutation.mutateAsync({
      id: templateId,
      render: { variables },
    });
    console.log('Rendered:', result.rendered_content);
  };

  return (
    <div>
      <h3>Preview</h3>
      <button onClick={handleRender}>Render Preview</button>
      {renderMutation.data && (
        <div dangerouslySetInnerHTML={{
          __html: renderMutation.data.rendered_content
        }} />
      )}
    </div>
  );
}
```

### 5. Dashboards

#### Dashboard de Configurações
```typescript
import { useConfigDashboard } from '@/hooks/useConfig';

function ConfigDashboardPage() {
  const { data: dashboard, isLoading } = useConfigDashboard();

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        title="Total Tenants"
        value={dashboard.tenants_stats.total}
        icon="🏢"
      />
      <StatCard
        title="Active Tenants"
        value={dashboard.tenants_stats.active}
        icon="✅"
      />
      <StatCard
        title="Feature Flags"
        value={dashboard.feature_flags_stats.total}
        icon="🚩"
      />
      <StatCard
        title="Templates"
        value={dashboard.templates_stats.total}
        icon="📧"
      />
    </div>
  );
}
```

#### Dashboard de Tenant Específico
```typescript
import { useTenantDashboard } from '@/hooks/useConfig';

function TenantDashboardPage({ tenantId }) {
  const { data: dashboard } = useTenantDashboard(tenantId);

  return (
    <div>
      <h1>Dashboard - {dashboard?.tenant_name}</h1>
      <div className="stats">
        <div>
          <h3>Settings</h3>
          <p>{dashboard?.settings_count} configurações</p>
        </div>
        <div>
          <h3>Features</h3>
          <p>{dashboard?.enabled_features_count} habilitadas</p>
        </div>
        <div>
          <h3>Storage</h3>
          <p>{dashboard?.storage_used_mb} MB / {dashboard?.storage_limit_mb} MB</p>
        </div>
      </div>
    </div>
  );
}
```

## Padrões Avançados

### 1. Otimização de Cache

#### Prefetch de Dados
```typescript
import { useQueryClient } from '@tanstack/react-query';
import { tenantsKeys, getTenant } from '@/hooks/useConfig';

function TenantsList() {
  const queryClient = useQueryClient();
  const { data: tenants } = useTenants();

  const handleHover = (tenantId: string) => {
    // Prefetch dos detalhes ao hover
    queryClient.prefetchQuery({
      queryKey: tenantsKeys.detail(tenantId),
      queryFn: () => getTenant(tenantId),
    });
  };

  return (
    <div>
      {tenants?.items.map((tenant) => (
        <div
          key={tenant.id}
          onMouseEnter={() => handleHover(tenant.id)}
        >
          {tenant.name}
        </div>
      ))}
    </div>
  );
}
```

#### Invalidação Seletiva
```typescript
import { useQueryClient } from '@tanstack/react-query';
import { tenantsKeys } from '@/hooks/useConfig';

function BulkActionsPanel() {
  const queryClient = useQueryClient();

  const handleBulkUpdate = async (tenantIds: string[]) => {
    // ... fazer updates ...

    // Invalidar apenas os tenants afetados
    tenantIds.forEach((id) => {
      queryClient.invalidateQueries({
        queryKey: tenantsKeys.detail(id)
      });
    });

    // Invalidar lista
    queryClient.invalidateQueries({
      queryKey: tenantsKeys.lists()
    });
  };
}
```

### 2. Composição de Hooks

#### Hook Customizado Composto
```typescript
import { useTenants, useTenantsStats } from '@/hooks/useConfig';

function useTenantsWithStats() {
  const tenantsQuery = useTenants();
  const statsQuery = useTenantsStats();

  return {
    tenants: tenantsQuery.data?.items || [],
    stats: statsQuery.data,
    isLoading: tenantsQuery.isLoading || statsQuery.isLoading,
    error: tenantsQuery.error || statsQuery.error,
  };
}

// Usar
function Dashboard() {
  const { tenants, stats, isLoading } = useTenantsWithStats();
  // ...
}
```

### 3. Error Handling

#### Retry e Error Boundary
```typescript
import { useTenants } from '@/hooks/useConfig';

function TenantsListWithRetry() {
  const { data, error, isLoading, refetch } = useTenants(
    { status: 'active' },
    {
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    }
  );

  if (error) {
    return (
      <ErrorBoundary>
        <ErrorMessage
          error={error}
          onRetry={refetch}
        />
      </ErrorBoundary>
    );
  }

  // ...
}
```

## Performance Tips

1. **Use enabled para queries condicionais:**
```typescript
const { data } = useTenant(tenantId, !!tenantId);
```

2. **Prefetch dados relacionados:**
```typescript
queryClient.prefetchQuery({
  queryKey: tenantsKeys.detail(id),
  queryFn: () => getTenant(id),
});
```

3. **Invalidação granular:**
```typescript
// Específico
queryClient.invalidateQueries({ queryKey: tenantsKeys.detail(id) });

// Lista
queryClient.invalidateQueries({ queryKey: tenantsKeys.lists() });
```

4. **Cache time otimizado:**
```typescript
const { data } = useTenants(params, {
  staleTime: 5 * 60 * 1000, // 5 minutos
  cacheTime: 10 * 60 * 1000, // 10 minutos
});
```

## Testes

### Unit Test de Service
```typescript
import { getTenant } from '@/services/config';
import { axiosInstance } from '@/lib/axios-instance';

jest.mock('@/lib/axios-instance');

describe('getTenant', () => {
  it('should fetch tenant by id', async () => {
    const mockTenant = { id: '1', name: 'Test' };
    axiosInstance.get.mockResolvedValue({ data: mockTenant });

    const result = await getTenant('1');

    expect(axiosInstance.get).toHaveBeenCalledWith('/api/v1/config/tenants/1');
    expect(result).toEqual(mockTenant);
  });
});
```

### Integration Test de Hook
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTenants } from '@/hooks/useConfig';

describe('useTenants', () => {
  it('should fetch tenants', async () => {
    const queryClient = new QueryClient();
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const { result } = renderHook(() => useTenants(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items).toBeDefined();
  });
});
```

## Conclusão

O módulo CONFIG fornece uma API completa e type-safe para gestão de configurações, tenants, feature flags e templates. Use os hooks fornecidos para integração fácil e otimizada com React Query.
