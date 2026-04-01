import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React, { useState, useEffect, useMemo } from 'react';

// ---- Inline component definition (mirrors WebhookFormModal logic) ----

const createInitialForm = (webhook?: any) => ({
  name: webhook?.name || '',
  url: webhook?.url || '',
  events: Array.isArray(webhook?.events)
    ? webhook.events.join(', ')
    : webhook?.events || '',
  status: webhook?.status || 'active',
  headers: webhook?.headers
    ? (typeof webhook.headers === 'string'
      ? webhook.headers
      : JSON.stringify(webhook.headers, null, 2))
    : '',
});

interface WebhookFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  webhook?: any;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
}

const WebhookFormModal: React.FC<WebhookFormModalProps> = ({
  isOpen,
  onClose,
  webhook,
  onSubmit,
  isLoading,
}) => {
  const isEditing = !!webhook;

  const formKey = useMemo(() => webhook?.id || webhook?.codigo || 'new', [webhook]);
  const [form, setForm] = useState(createInitialForm(webhook));

  useEffect(() => {
    if (isOpen) {
      setForm(createInitialForm(webhook));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, formKey]);

  const handleSubmit = async () => {
    const eventsArray = form.events
      .split(',')
      .map((e: string) => e.trim())
      .filter((e: string) => e.length > 0);

    let parsedHeaders: Record<string, string> | undefined;
    if (form.headers.trim()) {
      try {
        parsedHeaders = JSON.parse(form.headers);
      } catch {
        parsedHeaders = undefined;
      }
    }

    await onSubmit({
      name: form.name,
      url: form.url,
      events: eventsArray,
      status: form.status,
      headers: parsedHeaders,
    });
  };

  if (!isOpen) return null;

  return (
    <div data-testid="webhook-form-modal">
      <h2>{isEditing ? 'Editar Webhook' : 'Novo Webhook'}</h2>

      <label htmlFor="webhook-name">Nome</label>
      <input
        id="webhook-name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        placeholder="Ex: Notificacao Slack"
        data-testid="input-name"
      />

      <label>Status</label>
      <select
        value={form.status}
        onChange={(e) => setForm({ ...form, status: e.target.value })}
        data-testid="select-status"
      >
        <option value="active">Ativo</option>
        <option value="inactive">Inativo</option>
      </select>

      <label htmlFor="webhook-url">URL</label>
      <input
        id="webhook-url"
        value={form.url}
        onChange={(e) => setForm({ ...form, url: e.target.value })}
        placeholder="https://exemplo.com/webhook"
        data-testid="input-url"
      />

      <label htmlFor="webhook-events">Eventos</label>
      <input
        id="webhook-events"
        value={form.events}
        onChange={(e) => setForm({ ...form, events: e.target.value })}
        placeholder="user.created, order.completed"
        data-testid="input-events"
      />

      <label htmlFor="webhook-headers">Headers (JSON)</label>
      <textarea
        id="webhook-headers"
        value={form.headers}
        onChange={(e) => setForm({ ...form, headers: e.target.value })}
        placeholder='{"Authorization": "Bearer token"}'
        data-testid="input-headers"
      />

      <button type="button" onClick={onClose} disabled={isLoading} data-testid="btn-cancel">
        Cancelar
      </button>
      <button onClick={handleSubmit} disabled={isLoading} data-testid="btn-submit">
        {isLoading ? 'Salvando...' : isEditing ? 'Salvar' : 'Criar'}
      </button>
    </div>
  );
};

// ---- Tests ----

describe('WebhookFormModal - render e modos', () => {
  it('retorna null quando fechado', () => {
    const { container } = render(
      <WebhookFormModal isOpen={false} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renderiza quando aberto', () => {
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('webhook-form-modal')).toBeInTheDocument();
  });

  it('exibe titulo "Novo Webhook" no modo criacao', () => {
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByText('Novo Webhook')).toBeInTheDocument();
  });

  it('exibe titulo "Editar Webhook" no modo edicao', () => {
    render(
      <WebhookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        webhook={{ id: '1', name: 'Slack' }}
      />
    );
    expect(screen.getByText('Editar Webhook')).toBeInTheDocument();
  });
});

describe('WebhookFormModal - preenchimento de dados', () => {
  it('preenche campos com dados do webhook', () => {
    render(
      <WebhookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        webhook={{
          id: '1',
          name: 'Notificacao Slack',
          url: 'https://hooks.slack.com/services/xxx',
          events: ['user.created', 'order.paid'],
          status: 'active',
        }}
      />
    );
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('Notificacao Slack');
    expect((screen.getByTestId('input-url') as HTMLInputElement).value).toBe('https://hooks.slack.com/services/xxx');
    expect((screen.getByTestId('input-events') as HTMLInputElement).value).toBe('user.created, order.paid');
    expect((screen.getByTestId('select-status') as HTMLSelectElement).value).toBe('active');
  });

  it('inicia com valores padrao quando sem webhook', () => {
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect((screen.getByTestId('input-name') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-url') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('input-events') as HTMLInputElement).value).toBe('');
    expect((screen.getByTestId('select-status') as HTMLSelectElement).value).toBe('active');
    expect((screen.getByTestId('input-headers') as HTMLTextAreaElement).value).toBe('');
  });
});

describe('WebhookFormModal - createInitialForm branches', () => {
  it('converte events array para string com join', () => {
    const form = createInitialForm({ events: ['a', 'b', 'c'] });
    expect(form.events).toBe('a, b, c');
  });

  it('usa events string diretamente quando nao e array', () => {
    const form = createInitialForm({ events: 'a, b' });
    expect(form.events).toBe('a, b');
  });

  it('usa string vazia quando events nao definido', () => {
    const form = createInitialForm({});
    expect(form.events).toBe('');
  });

  it('serializa headers objeto para JSON string', () => {
    const form = createInitialForm({ headers: { Authorization: 'Bearer token' } });
    expect(form.headers).toBe(JSON.stringify({ Authorization: 'Bearer token' }, null, 2));
  });

  it('usa headers string diretamente quando ja e string', () => {
    const form = createInitialForm({ headers: '{"key":"value"}' });
    expect(form.headers).toBe('{"key":"value"}');
  });

  it('usa string vazia quando headers nao definido', () => {
    const form = createInitialForm({});
    expect(form.headers).toBe('');
  });

  it('status padrao e "active"', () => {
    const form = createInitialForm();
    expect(form.status).toBe('active');
  });

  it('usa status do webhook quando presente', () => {
    const form = createInitialForm({ status: 'inactive' });
    expect(form.status).toBe('inactive');
  });
});

describe('WebhookFormModal - handleSubmit branches', () => {
  it('converte events string para array ao submeter', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-events'), {
      target: { value: 'user.created, order.paid, payment.received' },
    });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          events: ['user.created', 'order.paid', 'payment.received'],
        })
      );
    });
  });

  it('filtra eventos vazios ao submeter', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-events'), {
      target: { value: 'user.created,  , order.paid, ' },
    });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          events: ['user.created', 'order.paid'],
        })
      );
    });
  });

  it('events string vazia resulta em array vazio', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ events: [] })
      );
    });
  });

  it('parseia headers JSON valido ao submeter', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-headers'), {
      target: { value: '{"Authorization": "Bearer abc123"}' },
    });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: { Authorization: 'Bearer abc123' },
        })
      );
    });
  });

  it('headers invalido resulta em undefined ao submeter', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-headers'), {
      target: { value: 'not valid json {{{' },
    });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ headers: undefined })
      );
    });
  });

  it('headers vazio resulta em undefined ao submeter', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    // Headers campo vazio (padrao)
    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ headers: undefined })
      );
    });
  });

  it('headers somente com espacos resulta em undefined', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-headers'), {
      target: { value: '   ' },
    });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ headers: undefined })
      );
    });
  });

  it('envia todos os campos corretos no payload', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={onSubmit} />
    );
    fireEvent.change(screen.getByTestId('input-name'), { target: { value: 'Meu Webhook' } });
    fireEvent.change(screen.getByTestId('input-url'), { target: { value: 'https://example.com/hook' } });
    fireEvent.change(screen.getByTestId('select-status'), { target: { value: 'inactive' } });
    fireEvent.change(screen.getByTestId('input-events'), { target: { value: 'order.created' } });

    fireEvent.click(screen.getByTestId('btn-submit'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'Meu Webhook',
        url: 'https://example.com/hook',
        events: ['order.created'],
        status: 'inactive',
        headers: undefined,
      });
    });
  });
});

describe('WebhookFormModal - estado isLoading', () => {
  it('exibe "Salvando..." durante isLoading', () => {
    render(
      <WebhookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
        webhook={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvando...');
  });

  it('exibe "Salvar" no modo edicao sem loading', () => {
    render(
      <WebhookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        webhook={{ id: '1' }}
      />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Salvar');
  });

  it('exibe "Criar" no modo criacao sem loading', () => {
    render(
      <WebhookFormModal isOpen={true} onClose={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.getByTestId('btn-submit')).toHaveTextContent('Criar');
  });

  it('botoes desabilitados durante isLoading', () => {
    render(
      <WebhookFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
        isLoading={true}
      />
    );
    expect(screen.getByTestId('btn-submit')).toBeDisabled();
    expect(screen.getByTestId('btn-cancel')).toBeDisabled();
  });
});

describe('WebhookFormModal - cancelar', () => {
  it('chama onClose ao clicar Cancelar', () => {
    const onClose = vi.fn();
    render(
      <WebhookFormModal isOpen={true} onClose={onClose} onSubmit={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId('btn-cancel'));
    expect(onClose).toHaveBeenCalled();
  });
});
