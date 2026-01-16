# Componentes - Conecta PRO Frontend

Este documento descreve os componentes reutilizaveis do sistema, organizados por categoria.

## Indice

- [UI Components](#ui-components)
- [Feedback Components](#feedback-components)
- [Form Components](#form-components)
- [Dashboard Widgets](#dashboard-widgets)

---

## UI Components

Componentes atomicos localizados em `/src/core/components/ui/`.

### Button

Botao com multiplas variantes e suporte a loading state.

```typescript
import { Button } from '@components/ui';

// Variantes
<Button variant="primary">Salvar</Button>
<Button variant="secondary">Cancelar</Button>
<Button variant="outline">Editar</Button>
<Button variant="ghost">Mais opcoes</Button>
<Button variant="danger">Excluir</Button>
<Button variant="link">Ver mais</Button>

// Tamanhos
<Button size="sm">Pequeno</Button>
<Button size="md">Medio</Button>
<Button size="lg">Grande</Button>
<Button size="icon"><PlusIcon /></Button>

// Com loading
<Button loading>Salvando...</Button>

// Com icones
<Button leftIcon={<SaveIcon />}>Salvar</Button>
<Button rightIcon={<ArrowRightIcon />}>Proximo</Button>

// Desabilitado
<Button disabled>Indisponivel</Button>
```

**Props:**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `variant` | `'primary' \| 'secondary' \| 'outline' \| 'ghost' \| 'danger' \| 'link'` | `'primary'` | Estilo visual |
| `size` | `'sm' \| 'md' \| 'lg' \| 'icon'` | `'md'` | Tamanho |
| `loading` | `boolean` | `false` | Exibe spinner |
| `leftIcon` | `ReactNode` | - | Icone a esquerda |
| `rightIcon` | `ReactNode` | - | Icone a direita |
| `disabled` | `boolean` | `false` | Desabilita o botao |

---

### Card

Container com sombra e bordas arredondadas.

```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@components/ui';

// Basico
<Card>
  Conteudo do card
</Card>

// Com header
<Card>
  <CardHeader>
    <CardTitle>Titulo do Card</CardTitle>
  </CardHeader>
  <CardContent>
    Conteudo aqui...
  </CardContent>
</Card>

// Variantes de padding
<Card padding="none">Sem padding</Card>
<Card padding="sm">Padding pequeno</Card>
<Card padding="md">Padding medio</Card>
<Card padding="lg">Padding grande</Card>

// Variantes de sombra
<Card shadow="none">Sem sombra</Card>
<Card shadow="sm">Sombra leve</Card>
<Card shadow="md">Sombra media</Card>
<Card shadow="lg">Sombra forte</Card>
```

**Props (Card):**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `padding` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | Espacamento interno |
| `shadow` | `'none' \| 'sm' \| 'md' \| 'lg'` | `'md'` | Intensidade da sombra |

---

### Input

Campo de entrada de texto com suporte a icones e validacao.

```typescript
import { Input } from '@components/ui';

// Basico
<Input placeholder="Digite seu nome" />

// Com label
<Input label="Email" type="email" />

// Com erro
<Input label="Senha" type="password" error="Senha muito curta" />

// Com hint
<Input label="Usuario" hint="Minimo 3 caracteres" />

// Com icones
<Input leftIcon={<SearchIcon />} placeholder="Buscar..." />
<Input rightIcon={<EyeIcon />} type="password" />
```

**Props:**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `label` | `string` | - | Label do campo |
| `error` | `string` | - | Mensagem de erro |
| `hint` | `string` | - | Texto de ajuda |
| `leftIcon` | `ReactNode` | - | Icone a esquerda |
| `rightIcon` | `ReactNode` | - | Icone a direita |

---

### Modal

Dialog modal com animacoes.

```typescript
import { Modal } from '@components/ui';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Abrir Modal</Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Confirmar Acao"
        description="Tem certeza que deseja continuar?"
      >
        <div className="space-y-4">
          <p>Conteudo do modal...</p>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setIsOpen(false)}>
              Cancelar
            </Button>
            <Button>Confirmar</Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
```

**Props:**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `isOpen` | `boolean` | - | Controla visibilidade |
| `onClose` | `() => void` | - | Callback ao fechar |
| `title` | `string` | - | Titulo do modal |
| `description` | `string` | - | Subtitulo |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| 'full'` | `'md'` | Largura do modal |
| `showClose` | `boolean` | `true` | Exibe botao de fechar |

---

### Badge

Etiqueta para status ou contagens.

```typescript
import { Badge } from '@components/ui';

<Badge variant="default">Default</Badge>
<Badge variant="success">Ativo</Badge>
<Badge variant="warning">Pendente</Badge>
<Badge variant="error">Erro</Badge>
<Badge variant="info">Info</Badge>

// Com contagem
<Badge>3</Badge>
```

---

### Avatar

Imagem de perfil com fallback.

```typescript
import { Avatar } from '@components/ui';

// Com imagem
<Avatar src="/user.jpg" alt="Joao Silva" />

// Com iniciais (fallback)
<Avatar name="Joao Silva" />

// Tamanhos
<Avatar size="sm" name="JS" />
<Avatar size="md" name="JS" />
<Avatar size="lg" name="JS" />
```

---

### Spinner

Indicador de carregamento.

```typescript
import { Spinner } from '@components/ui';

<Spinner />
<Spinner size="sm" />
<Spinner size="lg" />
<Spinner className="text-conecta-laranja" />
```

---

## Feedback Components

Componentes de feedback localizados em `/src/core/components/feedback/`.

### Toast

Sistema de notificacoes toast.

```typescript
import { useToast } from '@hooks/useToast';

function MyComponent() {
  const toast = useToast();

  const handleAction = () => {
    try {
      // acao...
      toast.success('Operacao realizada com sucesso!');
    } catch (error) {
      toast.error('Erro ao realizar operacao');
    }
  };

  // Com titulo
  toast.success({
    title: 'Sucesso!',
    message: 'Dados salvos com sucesso.',
  });

  // Com acao
  toast.info({
    message: 'Nova atualizacao disponivel',
    action: {
      label: 'Atualizar',
      onClick: () => window.location.reload(),
    },
  });

  // Com duracao customizada
  toast.warning({
    message: 'Sessao expirando em 5 minutos',
    duration: 10000, // 10 segundos
  });
}
```

**Metodos:**

| Metodo | Descricao |
|--------|-----------|
| `toast.success(message \| options)` | Toast de sucesso (verde) |
| `toast.error(message \| options)` | Toast de erro (vermelho) |
| `toast.warning(message \| options)` | Toast de aviso (amarelo) |
| `toast.info(message \| options)` | Toast informativo (azul) |

**ToastContainer:**

```typescript
// App.tsx - adicionar uma vez na raiz
import { ToastContainer } from '@components/feedback';

function App() {
  return (
    <>
      {/* resto da app */}
      <ToastContainer />
    </>
  );
}
```

---

### Skeleton

Placeholder animado para loading.

```typescript
import { Skeleton } from '@components/feedback';

// Retangulo
<Skeleton className="h-4 w-full" />

// Circulo
<Skeleton className="h-12 w-12 rounded-full" />

// Card skeleton
<div className="space-y-3">
  <Skeleton className="h-4 w-3/4" />
  <Skeleton className="h-4 w-1/2" />
  <Skeleton className="h-32 w-full" />
</div>
```

---

### ErrorBoundary

Captura erros em componentes filhos.

```typescript
import { ErrorBoundary } from '@components/feedback';

// Uso basico
<ErrorBoundary>
  <ComponenteQuePodeFalhar />
</ErrorBoundary>

// Com fallback customizado
<ErrorBoundary
  fallback={<div>Algo deu errado. Tente novamente.</div>}
>
  <ComponenteQuePodeFalhar />
</ErrorBoundary>
```

---

### ErrorMessage

Exibe mensagem de erro formatada.

```typescript
import { ErrorMessage } from '@components/feedback';

<ErrorMessage
  title="Erro ao carregar dados"
  message="Nao foi possivel conectar ao servidor."
  onRetry={() => refetch()}
/>
```

---

### EmptyState

Placeholder para listas vazias.

```typescript
import { EmptyState } from '@components/feedback';

<EmptyState
  icon={<FileIcon />}
  title="Nenhum documento encontrado"
  description="Comece enviando seu primeiro documento."
  action={{
    label: 'Enviar documento',
    onClick: () => openUploadModal(),
  }}
/>
```

---

### ConfirmDialog

Dialog de confirmacao.

```typescript
import { ConfirmDialog } from '@components/feedback';

const [showConfirm, setShowConfirm] = useState(false);

<ConfirmDialog
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  onConfirm={() => handleDelete()}
  title="Excluir registro"
  message="Tem certeza que deseja excluir? Esta acao nao pode ser desfeita."
  confirmText="Excluir"
  cancelText="Cancelar"
  variant="danger"
/>
```

---

## Form Components

Componentes de formulario localizados em `/src/core/components/forms/`.

### FormField

Wrapper para campos de formulario.

```typescript
import { FormField } from '@components/forms';

<FormField
  label="Nome completo"
  error={errors.name?.message}
  required
  hint="Como aparece no documento"
>
  <Input {...register('name')} />
</FormField>
```

**Props:**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `label` | `string` | - | Label do campo |
| `error` | `string` | - | Mensagem de erro |
| `required` | `boolean` | `false` | Exibe asterisco |
| `hint` | `string` | - | Texto de ajuda |

---

### Select

Dropdown de selecao.

```typescript
import { Select } from '@components/forms';

const options = [
  { value: 'sp', label: 'Sao Paulo' },
  { value: 'rj', label: 'Rio de Janeiro' },
  { value: 'mg', label: 'Minas Gerais' },
];

<Select
  options={options}
  placeholder="Selecione o estado"
  value={selectedState}
  onChange={(e) => setSelectedState(e.target.value)}
/>

// Variantes
<Select variant="default" options={options} />
<Select variant="filled" options={options} />
<Select variant="outlined" options={options} />

// Tamanhos
<Select size="sm" options={options} />
<Select size="md" options={options} />
<Select size="lg" options={options} />

// Com loading
<Select options={options} loading />

// Com erro
<Select options={options} error />
```

**Props:**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `options` | `{ value: string; label: string; disabled?: boolean }[]` | - | Opcoes do select |
| `placeholder` | `string` | `'Selecione...'` | Texto placeholder |
| `variant` | `'default' \| 'filled' \| 'outlined'` | `'default'` | Estilo visual |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Tamanho |
| `loading` | `boolean` | `false` | Exibe spinner |
| `error` | `boolean` | `false` | Estado de erro |
| `fullWidth` | `boolean` | `true` | Ocupa largura total |

---

### DatePicker

Seletor de data com formatacao BR.

```typescript
import { DatePicker } from '@components/forms';

const [date, setDate] = useState<Date | null>(null);

<DatePicker
  value={date}
  onChange={setDate}
  placeholder="dd/mm/aaaa"
/>

// Com limites
<DatePicker
  value={date}
  onChange={setDate}
  minDate={new Date()}
  maxDate={new Date('2025-12-31')}
/>

// Variantes
<DatePicker variant="default" value={date} onChange={setDate} />
<DatePicker variant="filled" value={date} onChange={setDate} />
<DatePicker variant="outlined" value={date} onChange={setDate} />

// Sem botao de limpar
<DatePicker clearable={false} value={date} onChange={setDate} />
```

**Props:**

| Prop | Tipo | Default | Descricao |
|------|------|---------|-----------|
| `value` | `Date \| string \| null` | - | Data selecionada |
| `onChange` | `(date: Date \| null) => void` | - | Callback de mudanca |
| `variant` | `'default' \| 'filled' \| 'outlined'` | `'default'` | Estilo visual |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Tamanho |
| `minDate` | `Date` | - | Data minima |
| `maxDate` | `Date` | - | Data maxima |
| `clearable` | `boolean` | `true` | Permite limpar |
| `dateFormat` | `'dd/MM/yyyy' \| 'yyyy-MM-dd'` | `'dd/MM/yyyy'` | Formato de exibicao |

---

### Textarea

Campo de texto multilinhas.

```typescript
import { Textarea } from '@components/forms';

<Textarea
  placeholder="Descreva o problema..."
  rows={4}
/>

// Com contagem de caracteres
<Textarea
  maxLength={500}
  showCount
/>
```

---

### Checkbox

Caixa de selecao.

```typescript
import { Checkbox } from '@components/forms';

<Checkbox
  label="Aceito os termos de uso"
  checked={accepted}
  onChange={(e) => setAccepted(e.target.checked)}
/>

// Com descricao
<Checkbox
  label="Notificacoes por email"
  description="Receba atualizacoes sobre sua conta"
/>
```

---

## Dashboard Widgets

Componentes de dashboard localizados em `/src/modules/dashboards/widgets/`.

### StatCard

Card de estatistica com indicador de variacao.

```typescript
import { StatCard } from '@modules/dashboards/widgets';

<StatCard
  title="Receita Total"
  value="R$ 1.250.000"
  change={12.5}
  icon={<DollarIcon />}
  trend="up"
/>

<StatCard
  title="Custos"
  value="R$ 450.000"
  change={-3.2}
  icon={<TrendingDownIcon />}
  trend="down"
/>
```

---

### ChartWidget

Container para graficos com header.

```typescript
import { ChartWidget } from '@modules/dashboards/widgets';

<ChartWidget
  title="Vendas Mensais"
  subtitle="Ultimos 12 meses"
  actions={
    <Select options={periodOptions} size="sm" />
  }
>
  <LineChart data={salesData} />
</ChartWidget>
```

---

### ProgressRing

Indicador circular de progresso.

```typescript
import { ProgressRing } from '@modules/dashboards/widgets';

<ProgressRing
  value={75}
  max={100}
  size={120}
  strokeWidth={8}
  label="Compliance"
/>
```

---

### MiniChart

Grafico sparkline compacto.

```typescript
import { MiniChart } from '@modules/dashboards/widgets';

<MiniChart
  data={[10, 25, 15, 30, 20, 35, 28]}
  color="#22c55e"
  height={40}
/>
```

---

### TableWidget

Tabela de dados com ordenacao.

```typescript
import { TableWidget } from '@modules/dashboards/widgets';

<TableWidget
  title="Ultimas Transacoes"
  columns={[
    { key: 'date', label: 'Data' },
    { key: 'description', label: 'Descricao' },
    { key: 'amount', label: 'Valor', align: 'right' },
  ]}
  data={transactions}
  onRowClick={(row) => navigate(`/transactions/${row.id}`)}
/>
```

---

## Exemplo de Uso Combinado

```typescript
import { Card, CardHeader, CardTitle, CardContent } from '@components/ui';
import { FormField } from '@components/forms';
import { Select, DatePicker } from '@components/forms';
import { Button } from '@components/ui';
import { useToast } from '@hooks/useToast';

function CreateOrderForm() {
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await api.post('/orders', data);
      toast.success('Ordem criada com sucesso!');
    } catch (error) {
      toast.error('Erro ao criar ordem');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nova Ordem de Servico</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <FormField label="Cliente" required error={errors.client?.message}>
            <Select
              options={clientOptions}
              {...register('client', { required: true })}
            />
          </FormField>

          <FormField label="Data de Execucao" required>
            <DatePicker
              value={executionDate}
              onChange={setExecutionDate}
              minDate={new Date()}
            />
          </FormField>

          <div className="flex justify-end gap-2">
            <Button variant="ghost" type="button">
              Cancelar
            </Button>
            <Button type="submit" loading={loading}>
              Criar Ordem
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

---

**Documentacao anterior:** [Arquitetura](./ARCHITECTURE.md)
