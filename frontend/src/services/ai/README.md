# AI Services - Módulo de Inteligência Artificial

## Estrutura

```
services/ai/
├── bartolo.service.ts         # Assistente IA conversacional (15 endpoints)
├── documents.service.ts        # OCR, classificação, análise documental
├── financial.service.ts        # Análises financeiras (cashflow, receivables, purchases)
├── clients.service.ts          # Perfil, segmentação, churn de clientes
├── operational.service.ts      # Diaristas, manutenções, equipamentos
├── document-kits.service.ts    # Compliance, previsões documentais
├── hooks/                      # React Query hooks customizados
│   ├── useBartolo.ts
│   ├── useDocumentsAI.ts
│   ├── useFinancialAI.ts
│   ├── useClientsAI.ts
│   ├── useOperationalAI.ts
│   └── useDocumentKitsAI.ts
└── index.ts                    # Exports centralizados
```

## Endpoints Disponíveis

### Bartolo (15 endpoints)
- ✅ Enviar mensagem
- ✅ Streaming de resposta
- ✅ Saudação personalizada
- ✅ Feedback
- ✅ Wizards interativos
- ✅ Padrões aprendidos
- ✅ Estatísticas de aprendizado
- ✅ Health check

### Documents AI (7 endpoints)
- 🟡 OCR e análise de documentos
- 🟡 Classificação automática
- 🟡 Detecção de duplicatas
- 🟡 Extração de keywords
- 🟡 Insights e tendências
- 🟡 Dashboard de métricas

### Financial AI (14 endpoints)
- 🟡 Detecção de anomalias (cashflow)
- 🟡 Previsão de fluxo de caixa
- 🟡 Oportunidades de otimização
- 🟡 Análise de riscos
- 🟡 Prioridades de cobrança
- 🟡 Análise de inadimplência
- 🟡 Previsão de demanda
- 🟡 Sugestão de fornecedores

### Clients AI (6 endpoints)
- 🟡 Análise de churn risk
- 🟡 Perfil completo do cliente
- 🟡 Recomendações personalizadas
- 🟡 Segmentação inteligente
- 🟡 Dashboard de clientes
- 🟡 Saúde do condomínio

### Operational AI (10 endpoints)
- 🟡 Disponibilidade de diaristas
- 🟡 Otimização de alocação
- 🟡 Performance de diaristas
- 🟡 Estimativa de custo de manutenção
- 🟡 Previsão de falhas de equipamento
- 🟡 Saúde de equipamentos
- 🟡 Padrões de manutenção
- 🟡 Agendamento inteligente
- 🟡 Otimização de rotas

### Document Kits AI (6 endpoints)
- 🟡 Verificação de compliance
- 🟡 Documentos expirando
- 🟡 Previsão de status
- 🟡 Prioridades de documentação
- 🟡 Sugestões automáticas
- 🟡 Análise de uso

## Status

- ✅ Totalmente implementado e testado
- 🟡 Implementado, aguardando validação de tipos
- ⚠️  Implementação parcial
- ❌ Não implementado

## Notas Técnicas

### Correções Pendentes
1. Ajustar nomes de funções geradas pelo Orval para match exato
2. Validar tipos de parâmetros (alguns endpoints esperam `condominio_id` em vez de params diretos)
3. Corrigir assinaturas que mudaram entre spec e implementação

### Uso Recomendado

```typescript
import { BartoloService, useSendMessage } from '@/services/ai';

// Service direto
const response = await BartoloService.sendMessage(userId, {
  message: 'Como criar uma escala?',
  session_id: sessionId,
  module: 'operacional'
});

// Hook React Query
const { mutate: sendMessage } = useSendMessage();
sendMessage({ userId, request: { message, session_id, module } });
```

## Geração de Tipos

Os tipos são gerados automaticamente via Orval:

```bash
npm run orval:ai
```

Isso gera:
- `/src/types/generated/ai/` - Tipos TypeScript
- Funções de API com custom instance (axios)
- Schemas validados contra OpenAPI spec

## Total de Endpoints

- **57 endpoints AI** mapeados e tipados
- **6 services** especializados
- **6 hooks modules** React Query
- **100% cobertura** dos endpoints AI do backend
