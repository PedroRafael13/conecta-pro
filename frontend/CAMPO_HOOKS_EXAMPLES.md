# Exemplos de Uso - Hooks CAMPO Orval

## 1. Ordens de Serviço

### Listar OS com paginação
```typescript
import { useListarOsApiV1CampoOsGet } from '@/api/campo/generated/campo-ordens-de-servico/campo-ordens-de-servico';

export function ListaOS() {
  const { data, isLoading, error } = useListarOsApiV1CampoOsGet({
    skip: 0,
    limit: 20,
    status: 'AGENDADA'
  });

  if (isLoading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error.message}</div>;

  return (
    <div>
      {data.items.map(os => (
        <div key={os.id}>
          <h3>{os.numero} - {os.titulo}</h3>
          <p>Status: {os.status}</p>
          <p>Técnico: {os.tecnico_id}</p>
        </div>
      ))}
    </div>
  );
}
```

### Criar nova OS
```typescript
import { useCriarOsApiV1CampoOsPost } from '@/api/campo/generated/campo-ordens-de-servico/campo-ordens-de-servico';
import { OrdemServicoCreate } from '@/api/campo/generated/models';

export function NovaOS() {
  const { mutate, isPending } = useCriarOsApiV1CampoOsPost();

  const handleSubmit = () => {
    const novaOS: OrdemServicoCreate = {
      tipo: 'MANUTENCAO',
      prioridade: 'ALTA',
      cliente_id: 'uuid-cliente',
      endereco_servico: 'Rua Exemplo, 123',
      titulo: 'Manutenção preventiva',
      descricao: 'Verificação geral do sistema'
    };

    mutate({ data: novaOS }, {
      onSuccess: (os) => {
        console.log('OS criada:', os.numero);
      },
      onError: (error) => {
        console.error('Erro:', error);
      }
    });
  };

  return (
    <button onClick={handleSubmit} disabled={isPending}>
      {isPending ? 'Criando...' : 'Criar OS'}
    </button>
  );
}
```

### Fazer check-in em OS
```typescript
import { useFazerCheckinApiV1CampoOsOsIdCheckinPost } from '@/api/campo/generated/campo-ordens-de-servico/campo-ordens-de-servico';

export function CheckinOS({ osId }: { osId: string }) {
  const { mutate } = useFazerCheckinApiV1CampoOsOsIdCheckinPost();

  const handleCheckin = () => {
    mutate(
      {
        osId,
        data: {
          latitude: -23.5505,
          longitude: -46.6333,
          observacao: 'Chegada no local'
        }
      },
      {
        onSuccess: () => {
          console.log('Check-in realizado!');
        }
      }
    );
  };

  return <button onClick={handleCheckin}>Fazer Check-in</button>;
}
```

### Dashboard de OS
```typescript
import { useObterDashboardApiV1CampoOsDashboardGet } from '@/api/campo/generated/campo-ordens-de-servico/campo-ordens-de-servico';

export function DashboardOS() {
  const { data } = useObterDashboardApiV1CampoOsDashboardGet({
    periodo_inicio: '2026-01-01',
    periodo_fim: '2026-01-31'
  });

  if (!data) return null;

  return (
    <div className="grid grid-cols-4 gap-4">
      <div className="card">
        <h3>Total</h3>
        <p className="text-3xl">{data.total}</p>
      </div>
      <div className="card">
        <h3>Pendentes</h3>
        <p className="text-3xl">{data.por_status.PENDENTE || 0}</p>
      </div>
      <div className="card">
        <h3>Em Andamento</h3>
        <p className="text-3xl">{data.por_status.EM_ANDAMENTO || 0}</p>
      </div>
      <div className="card">
        <h3>Concluídas</h3>
        <p className="text-3xl">{data.por_status.CONCLUIDA || 0}</p>
      </div>
    </div>
  );
}
```

---

## 2. Visitas Técnicas/Comerciais

### Criar visita
```typescript
import { useCriarVisitaApiV1CampoVisitasPost } from '@/api/campo/generated/campo-visitas/campo-visitas';
import { VisitaCreate } from '@/api/campo/generated/models';

export function NovaVisita() {
  const { mutate } = useCriarVisitaApiV1CampoVisitasPost();

  const handleSubmit = () => {
    const visita: VisitaCreate = {
      tipo: 'COMERCIAL',
      cliente_id: 'uuid-cliente',
      responsavel_id: 'uuid-vendedor',
      data_agendada: '2026-02-01T10:00:00',
      objetivo: 'Apresentar novos serviços',
      prospect_nome: 'João Silva',
      prospect_empresa: 'Empresa XYZ',
      prospect_telefone: '11999999999'
    };

    mutate({ data: visita });
  };

  return <button onClick={handleSubmit}>Agendar Visita</button>;
}
```

### Registrar resultado de visita
```typescript
import { useRegistrarResultadoApiV1CampoVisitasVisitaIdResultadoPost } from '@/api/campo/generated/campo-visitas/campo-visitas';

export function ResultadoVisita({ visitaId }: { visitaId: string }) {
  const { mutate } = useRegistrarResultadoApiV1CampoVisitasVisitaIdResultadoPost();

  const handleResultado = () => {
    mutate({
      visitaId,
      data: {
        resultado: 'CONCLUIDA',
        observacoes: 'Cliente demonstrou interesse em contratar',
        necessidades_identificadas: ['Sistema de acesso', 'CFTV'],
        proximos_passos: 'Enviar proposta comercial'
      }
    });
  };

  return <button onClick={handleResultado}>Registrar Resultado</button>;
}
```

### Converter visita em OS
```typescript
import { useConverterParaOsApiV1CampoVisitasVisitaIdConverterOsPost } from '@/api/campo/generated/campo-visitas/campo-visitas';

export function ConverterVisita({ visitaId }: { visitaId: string }) {
  const { mutate, isPending } = useConverterParaOsApiV1CampoVisitasVisitaIdConverterOsPost();

  const handleConverter = () => {
    mutate(
      { visitaId },
      {
        onSuccess: (os) => {
          console.log('OS gerada:', os.numero);
        }
      }
    );
  };

  return (
    <button onClick={handleConverter} disabled={isPending}>
      Converter para OS
    </button>
  );
}
```

---

## 3. Checklists Dinâmicos

### Iniciar checklist
```typescript
import { useIniciarChecklistApiV1CampoChecklistsOsOsIdIniciarPost } from '@/api/campo/generated/campo-checklists/campo-checklists';

export function IniciarChecklist({ osId }: { osId: string }) {
  const { mutate } = useIniciarChecklistApiV1CampoChecklistsOsOsIdIniciarPost();

  const handleIniciar = () => {
    mutate({
      osId,
      data: {
        observacao_inicial: 'Iniciando checklist de manutenção'
      }
    });
  };

  return <button onClick={handleIniciar}>Iniciar Checklist</button>;
}
```

### Responder item do checklist
```typescript
import { useResponderItemApiV1CampoChecklistsChecklistIdItemsItemIdRespostaPost } from '@/api/campo/generated/campo-checklists/campo-checklists';

export function ResponderItem({
  checklistId,
  itemId,
  tipo
}: {
  checklistId: string;
  itemId: string;
  tipo: string;
}) {
  const { mutate } = useResponderItemApiV1CampoChecklistsChecklistIdItemsItemIdRespostaPost();

  const handleResposta = (valor: any) => {
    mutate({
      checklistId,
      itemId,
      data: {
        valor_resposta: valor,
        observacao: 'Verificado OK'
      }
    });
  };

  if (tipo === 'SIM_NAO') {
    return (
      <div>
        <button onClick={() => handleResposta('SIM')}>Sim</button>
        <button onClick={() => handleResposta('NAO')}>Não</button>
      </div>
    );
  }

  if (tipo === 'NUMERO') {
    return (
      <input
        type="number"
        onBlur={(e) => handleResposta(parseFloat(e.target.value))}
      />
    );
  }

  return (
    <input
      type="text"
      onBlur={(e) => handleResposta(e.target.value)}
    />
  );
}
```

### Obter checklist com itens
```typescript
import { useObterChecklistApiV1CampoChecklistsChecklistIdGet } from '@/api/campo/generated/campo-checklists/campo-checklists';

export function DetalhesChecklist({ checklistId }: { checklistId: string }) {
  const { data } = useObterChecklistApiV1CampoChecklistsChecklistIdGet(checklistId);

  if (!data) return null;

  return (
    <div>
      <h2>Checklist: {data.template_id}</h2>
      <p>Status: {data.status}</p>
      <p>Progresso: {data.itens_respondidos}/{data.total_itens}</p>

      <div className="itens">
        {data.itens.map(item => (
          <div key={item.id}>
            <h4>{item.titulo}</h4>
            <p>{item.descricao}</p>
            {item.resposta_valor && (
              <p>Resposta: {item.resposta_valor}</p>
            )}
          </div>
        ))}
      </div>

      {data.score_obtido !== null && (
        <p>Score: {data.score_obtido}/{data.score_maximo}</p>
      )}
    </div>
  );
}
```

---

## 4. Roteirização Inteligente

### Otimizar rota
```typescript
import { useOtimizarRotaApiV1CampoRotasOtimizarPost } from '@/api/campo/generated/campo-roteirizacao/campo-roteirizacao';

export function OtimizarRota() {
  const { mutate, data, isPending } = useOtimizarRotaApiV1CampoRotasOtimizarPost();

  const handleOtimizar = () => {
    mutate({
      data: {
        os_ids: ['uuid-os-1', 'uuid-os-2', 'uuid-os-3'],
        tecnico_id: 'uuid-tecnico',
        ponto_partida: {
          latitude: -23.5505,
          longitude: -46.6333
        },
        considerar_prioridade: true,
        considerar_sla: true,
        considerar_habilidades: true
      }
    });
  };

  return (
    <div>
      <button onClick={handleOtimizar} disabled={isPending}>
        Otimizar Rota
      </button>

      {data && (
        <div className="resultado">
          <h3>Rota Otimizada</h3>
          <p>Distância total: {data.distancia_total_km.toFixed(2)} km</p>
          <p>Tempo estimado: {data.tempo_total_minutos} min</p>

          <ol>
            {data.ordem_visitas.map((os, idx) => (
              <li key={os.os_id}>
                {idx + 1}. OS {os.numero} - {os.endereco}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
```

### Analisar capacidade de equipe
```typescript
import { useAnalisarEquipeApiV1CampoRotasAnalisarEquipeGet } from '@/api/campo/generated/campo-roteirizacao/campo-roteirizacao';

export function AnaliseEquipe() {
  const { data } = useAnalisarEquipeApiV1CampoRotasAnalisarEquipeGet({
    data: '2026-02-01'
  });

  if (!data) return null;

  return (
    <div>
      <h2>Análise de Equipe - {data.data}</h2>

      {data.tecnicos.map(tec => (
        <div key={tec.tecnico_id} className="card">
          <h3>{tec.nome}</h3>
          <p>Capacidade: {tec.os_alocadas}/{tec.capacidade_maxima}</p>
          <p>Horas alocadas: {tec.horas_alocadas}h</p>
          <p>Status: {tec.disponivel ? 'Disponível' : 'Lotado'}</p>

          {tec.os_alocadas > 0 && (
            <ul>
              {tec.os.map(os => (
                <li key={os.id}>{os.numero} - {os.horario}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}
```

---

## 5. Estoque Campo

### Requisitar materiais
```typescript
import { useRequisitarMateriaisApiV1CampoEstoqueRequisitarPost } from '@/api/campo/generated/campo-estoque/campo-estoque';

export function RequisitarMateriais({ osId }: { osId: string }) {
  const { mutate } = useRequisitarMateriaisApiV1CampoEstoqueRequisitarPost();

  const handleRequisitar = () => {
    mutate({
      data: {
        os_id: osId,
        tecnico_id: 'uuid-tecnico',
        itens: [
          { produto_id: 'uuid-produto-1', quantidade: 2 },
          { produto_id: 'uuid-produto-2', quantidade: 5 }
        ],
        observacao: 'Materiais para instalação'
      }
    });
  };

  return <button onClick={handleRequisitar}>Requisitar Materiais</button>;
}
```

### Verificar disponibilidade
```typescript
import { useVerificarDisponibilidadeApiV1CampoEstoqueDisponibilidadeGet } from '@/api/campo/generated/campo-estoque/campo-estoque';

export function VerificarEstoque({ produtoId }: { produtoId: string }) {
  const { data } = useVerificarDisponibilidadeApiV1CampoEstoqueDisponibilidadeGet({
    produto_id: produtoId,
    quantidade: 10
  });

  if (!data) return null;

  return (
    <div>
      {data.disponivel ? (
        <span className="text-green-600">✓ Disponível ({data.quantidade_disponivel})</span>
      ) : (
        <span className="text-red-600">✗ Indisponível</span>
      )}
    </div>
  );
}
```

---

## 6. Monitoramento

### Dashboard de monitoramento
```typescript
import { useGetMonitoringDashboardApiV1CampoMonitoringDashboardGet } from '@/api/campo/generated/monitoring/monitoring';

export function MonitoringDashboard() {
  const { data, isLoading } = useGetMonitoringDashboardApiV1CampoMonitoringDashboardGet();

  if (isLoading) return <div>Carregando...</div>;
  if (!data) return null;

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="card">
        <h3>Técnicos Ativos</h3>
        <p className="text-4xl">{data.tecnicos_ativos}</p>
      </div>
      <div className="card">
        <h3>OS em Andamento</h3>
        <p className="text-4xl">{data.os_em_andamento}</p>
      </div>
      <div className="card">
        <h3>Taxa de Conclusão</h3>
        <p className="text-4xl">{data.taxa_conclusao}%</p>
      </div>
    </div>
  );
}
```

---

## 7. Padrões Avançados

### Query com refetch automático
```typescript
export function ListaOSAoVivo() {
  const { data } = useListarOsApiV1CampoOsGet(
    { status: 'EM_ANDAMENTO' },
    {
      query: {
        refetchInterval: 30000, // Atualiza a cada 30s
        refetchOnWindowFocus: true
      }
    }
  );

  return <div>{/* ... */}</div>;
}
```

### Invalidação de cache após mutação
```typescript
import { useQueryClient } from '@tanstack/react-query';
import { useConcluirOsApiV1CampoOsOsIdConcluirPost } from '@/api/campo/generated/campo-ordens-de-servico/campo-ordens-de-servico';

export function ConcluirOS({ osId }: { osId: string }) {
  const queryClient = useQueryClient();
  const { mutate } = useConcluirOsApiV1CampoOsOsIdConcluirPost();

  const handleConcluir = () => {
    mutate(
      {
        osId,
        data: {
          solucao_aplicada: 'Problema resolvido',
          observacao_conclusao: 'Trabalho concluído com sucesso'
        }
      },
      {
        onSuccess: () => {
          // Invalida cache da lista de OS
          queryClient.invalidateQueries({
            queryKey: ['listarOsApiV1CampoOsGet']
          });
          // Invalida cache do dashboard
          queryClient.invalidateQueries({
            queryKey: ['obterDashboardApiV1CampoOsDashboardGet']
          });
        }
      }
    );
  };

  return <button onClick={handleConcluir}>Concluir OS</button>;
}
```

### Optimistic update
```typescript
export function AtualizarStatusOS({ osId, statusAtual }: { osId: string; statusAtual: string }) {
  const queryClient = useQueryClient();
  const { mutate } = useAtualizarOsApiV1CampoOsOsIdPatch();

  const handleUpdate = (novoStatus: string) => {
    mutate(
      {
        osId,
        data: { status: novoStatus }
      },
      {
        onMutate: async () => {
          // Cancela queries em andamento
          await queryClient.cancelQueries({ queryKey: ['obterOsApiV1CampoOsOsIdGet', osId] });

          // Snapshot do valor anterior
          const previousOS = queryClient.getQueryData(['obterOsApiV1CampoOsOsIdGet', osId]);

          // Update otimista
          queryClient.setQueryData(['obterOsApiV1CampoOsOsIdGet', osId], (old: any) => ({
            ...old,
            status: novoStatus
          }));

          return { previousOS };
        },
        onError: (err, variables, context) => {
          // Rollback em caso de erro
          if (context?.previousOS) {
            queryClient.setQueryData(
              ['obterOsApiV1CampoOsOsIdGet', osId],
              context.previousOS
            );
          }
        },
        onSettled: () => {
          // Refetch após conclusão
          queryClient.invalidateQueries({
            queryKey: ['obterOsApiV1CampoOsOsIdGet', osId]
          });
        }
      }
    );
  };

  return (
    <select value={statusAtual} onChange={(e) => handleUpdate(e.target.value)}>
      <option value="PENDENTE">Pendente</option>
      <option value="AGENDADA">Agendada</option>
      <option value="EM_ANDAMENTO">Em Andamento</option>
      <option value="CONCLUIDA">Concluída</option>
    </select>
  );
}
```

---

## Arquivos Gerados

**Localização:** `/opt/conecta-pro/frontend/src/api/campo/generated/`

**Estrutura:**
- `campo-ordens-de-servico/` - 94 hooks
- `campo-visitas/` - 104 hooks
- `campo-checklists/` - 82 hooks
- `campo-roteirizacao/` - 44 hooks
- `campo-estoque/` - 60 hooks
- `models/` - 792 tipos TypeScript

**Total:** 728 hooks React Query type-safe prontos para uso!
