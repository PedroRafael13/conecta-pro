# PLANO DE EVOLUÇÃO - MÓDULO OPERACIONAL
## Conecta PRO - Sistema de Gestão de Facilities

**Data:** 2026-01-18
**Versão:** 1.0
**Responsável:** Equipe de Desenvolvimento

---

## 1. PRE-MORTEM: ANÁLISE DE RISCOS E POSSÍVEIS FALHAS

### 1.1 O que pode dar errado se NÃO evoluirmos o módulo?

| Risco | Probabilidade | Impacto | Consequência |
|-------|---------------|---------|--------------|
| Perda de controle operacional | ALTA | CRÍTICO | Supervisores sem visibilidade em tempo real = problemas não detectados |
| Comunicação falha entre setores | ALTA | ALTO | DP/RH desalinhado com Operações = atrasos em processos |
| Medidas administrativas manuais | ALTA | MÉDIO | Advertências no papel = sem histórico, sem rastreabilidade |
| Falta de documentação digital | ALTA | ALTO | Funcionário não assina documento = empresa sem comprovação legal |
| Ocorrências não registradas | MÉDIA | CRÍTICO | Incidente grave sem registro = responsabilidade legal |
| Diaristas sem controle fiscal | MÉDIA | ALTO | RPA não emitida = problema trabalhista |

### 1.2 O que pode dar errado DURANTE a implementação?

| Risco | Mitigação |
|-------|-----------|
| **Complexidade excessiva** | Implementar em fases, MVP primeiro |
| **Resistência dos usuários** | Treinamento, interface simples, Bartolo como guia |
| **Integração DP/RH falha** | Definir contratos de API claros, testes de integração |
| **Performance degradada** | Índices otimizados, cache, paginação |
| **Notificações em excesso** | Configurar preferências por perfil, agrupamento |
| **Dados inconsistentes** | Validações rigorosas, transações atômicas |
| **Bartolo desinformado** | Atualizar prompts a cada nova funcionalidade |

### 1.3 O que pode dar errado APÓS a implementação?

| Risco | Mitigação |
|-------|-----------|
| **Funcionários não usam o sistema** | Gamificação, obrigatoriedade, treinamento contínuo |
| **Supervisores burlam processos** | Auditoria automática, alertas para gestores |
| **Excesso de ocorrências não tratadas** | SLA de resposta, escalação automática |
| **Medidas administrativas incorretas** | Workflow de aprovação, revisão jurídica |
| **Assinaturas não reconhecidas legalmente** | Certificação digital, conformidade ICP-Brasil |

### 1.4 Premissas que podem estar erradas

| Premissa | Validação Necessária |
|----------|---------------------|
| Supervisores têm celular com internet | Pesquisa de campo, plano B offline |
| Funcionários sabem usar sistema | Interface ultra-simples, treinamento |
| DP responde em tempo hábil | SLA definido, alertas de atraso |
| Gestores aprovam medidas rapidamente | Timeout com escalação automática |

---

## 2. PLANO DE IMPLEMENTAÇÃO

### 2.1 Visão Geral das Fases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVOLUÇÃO MÓDULO OPERACIONAL                          │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│   FASE 1    │   FASE 2    │   FASE 3    │   FASE 4    │      FASE 5         │
│  Ocorrências│   Medidas   │ Comunicação │ Ponto Avançado│ Relatórios + IA   │
│  (2 sprints)│ (2 sprints) │ (2 sprints) │  (1 sprint)  │   (2 sprints)      │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘
```

---

### 2.2 FASE 1: MÓDULO DE OCORRÊNCIAS (Prioridade P1)

**Objetivo:** Registrar e gerenciar todos os eventos operacionais em tempo real.

#### 2.2.1 Entidades

```python
# OCCURRENCE (Ocorrência)
class Occurrence:
    id: UUID
    code: str                    # OCC-2026-00001
    tenant_id: UUID

    # Localização
    post_id: UUID                # Posto onde ocorreu
    client_id: UUID              # Cliente
    contract_id: UUID            # Contrato

    # Classificação
    category: OccurrenceCategory # SEGURANCA, LIMPEZA, MANUTENCAO, COMPORTAMENTO, ACIDENTE, OUTRO
    severity: Severity           # BAIXA, MEDIA, ALTA, CRITICA
    type: OccurrenceType         # INCIDENTE, PROBLEMA, SUGESTAO, ELOGIO

    # Descrição
    title: str
    description: text

    # Pessoas envolvidas
    reported_by_id: UUID         # Quem registrou
    employee_involved_id: UUID   # Funcionário envolvido (opcional)
    witness_ids: List[UUID]      # Testemunhas (opcional)

    # Status e workflow
    status: OccurrenceStatus     # ABERTA, EM_ANALISE, PENDENTE_ACAO, RESOLVIDA, ARQUIVADA
    priority: Priority           # URGENTE, ALTA, NORMAL, BAIXA

    # Resolução
    resolution: text
    resolved_by_id: UUID
    resolved_at: datetime
    resolution_type: str         # PROCEDENTE, IMPROCEDENTE, PARCIAL

    # Escalação
    escalated: bool
    escalated_to_id: UUID
    escalated_at: datetime
    escalation_reason: str

    # Medida administrativa gerada
    disciplinary_action_id: UUID # Se gerou advertência/suspensão

    # Auditoria
    created_at: datetime
    updated_at: datetime
    created_by: UUID

# OCCURRENCE_ATTACHMENT (Anexos)
class OccurrenceAttachment:
    id: UUID
    occurrence_id: UUID
    file_type: str               # IMAGE, VIDEO, DOCUMENT, AUDIO
    file_path: str
    file_name: str
    file_size: int
    description: str
    captured_at: datetime        # Quando a foto/vídeo foi feito
    latitude: float              # Geolocalização
    longitude: float
    uploaded_by: UUID
    uploaded_at: datetime

# OCCURRENCE_COMMENT (Comentários/Timeline)
class OccurrenceComment:
    id: UUID
    occurrence_id: UUID
    author_id: UUID
    content: text
    is_internal: bool            # Visível só para gestores
    created_at: datetime

# OCCURRENCE_CATEGORY (Categorias configuráveis)
class OccurrenceCategory:
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: str
    severity_default: Severity
    requires_photo: bool
    requires_witness: bool
    auto_escalate: bool
    escalate_to_role: str
    sla_hours: int               # Tempo máximo para resolução
    is_active: bool
```

#### 2.2.2 Endpoints da API

```
POST   /api/v1/operacional/ocorrencias                    # Criar ocorrência
GET    /api/v1/operacional/ocorrencias                    # Listar com filtros
GET    /api/v1/operacional/ocorrencias/{id}               # Detalhe
PATCH  /api/v1/operacional/ocorrencias/{id}               # Atualizar
DELETE /api/v1/operacional/ocorrencias/{id}               # Arquivar

POST   /api/v1/operacional/ocorrencias/{id}/anexos        # Upload de anexo
GET    /api/v1/operacional/ocorrencias/{id}/anexos        # Listar anexos
DELETE /api/v1/operacional/ocorrencias/{id}/anexos/{aid}  # Remover anexo

POST   /api/v1/operacional/ocorrencias/{id}/comentarios   # Adicionar comentário
GET    /api/v1/operacional/ocorrencias/{id}/comentarios   # Listar timeline

POST   /api/v1/operacional/ocorrencias/{id}/escalar       # Escalar ocorrência
POST   /api/v1/operacional/ocorrencias/{id}/resolver      # Resolver ocorrência
POST   /api/v1/operacional/ocorrencias/{id}/reabrir       # Reabrir ocorrência

GET    /api/v1/operacional/ocorrencias/dashboard          # Dashboard ocorrências
GET    /api/v1/operacional/ocorrencias/pendentes          # Pendentes por perfil
GET    /api/v1/operacional/ocorrencias/sla-vencendo       # Próximas de vencer SLA

GET    /api/v1/operacional/ocorrencias/categorias         # Categorias disponíveis
POST   /api/v1/operacional/ocorrencias/categorias         # Criar categoria
```

#### 2.2.3 Regras de Negócio

1. **Criação automática de medida administrativa:** Se categoria = COMPORTAMENTO e severity >= ALTA, sugerir criação de advertência
2. **Escalação automática:** Se SLA excedido, escalar para próximo nível hierárquico
3. **Notificações:**
   - Ocorrência CRÍTICA → Notifica Gerente Operações imediatamente
   - Ocorrência com funcionário → Notifica Supervisor do posto
   - Comentário adicionado → Notifica participantes
4. **Permissões:**
   - Porteiro/Vigilante: Criar ocorrência do seu posto
   - Supervisor: Criar, analisar, resolver do seu grupo de postos
   - Gerente: Tudo + relatórios consolidados

#### 2.2.4 Integração com DP/RH

```
OCORRÊNCIA COMPORTAMENTAL
         │
         ▼
┌─────────────────────┐
│  Análise Supervisor │
│  (24h para analisar)│
└─────────────────────┘
         │
         ▼ Procedente?
    ┌────┴────┐
   SIM       NÃO
    │         │
    ▼         ▼
┌─────────┐  Arquivar
│ Gerar   │
│ Medida  │
│ Admin.  │
└─────────┘
    │
    ▼
┌─────────────────────┐
│  Notifica DP/RH     │
│  para providências  │
└─────────────────────┘
```

---

### 2.3 FASE 2: MEDIDAS ADMINISTRATIVAS (Prioridade P1)

**Objetivo:** Digitalizar advertências, suspensões e controle disciplinar.

#### 2.3.1 Entidades

```python
# DISCIPLINARY_ACTION (Medida Administrativa)
class DisciplinaryAction:
    id: UUID
    code: str                    # ADV-2026-00001, SUS-2026-00001
    tenant_id: UUID

    # Tipo
    action_type: ActionType      # ADVERTENCIA_VERBAL, ADVERTENCIA_ESCRITA, SUSPENSAO, DEMISSAO_JUSTA_CAUSA

    # Funcionário
    employee_id: UUID
    employee_name: str           # Snapshot para histórico
    employee_cpf: str
    employee_position: str
    employee_admission_date: date

    # Posto/Local
    post_id: UUID
    client_id: UUID

    # Motivo
    reason_category: str         # FALTA, ATRASO, INSUBORDINACAO, DANO_PATRIMONIO, etc.
    reason_description: text
    occurrence_id: UUID          # Ocorrência que originou (opcional)

    # Datas
    incident_date: date          # Data do fato
    application_date: date       # Data da aplicação
    suspension_start_date: date  # Se suspensão
    suspension_end_date: date    # Se suspensão
    suspension_days: int         # 1 a 30 dias

    # Documento
    document_text: text          # Texto completo do documento
    document_template_id: UUID   # Template usado

    # Testemunhas
    witness_1_name: str
    witness_1_cpf: str
    witness_2_name: str
    witness_2_cpf: str

    # Status e workflow
    status: ActionStatus         # RASCUNHO, PENDENTE_APROVACAO, APROVADA, PENDENTE_ASSINATURA,
                                 # ASSINADA, RECUSADA_ASSINATURA, APLICADA, CANCELADA

    # Aprovação (workflow)
    requires_approval: bool
    approved_by_id: UUID
    approved_at: datetime
    approval_notes: str

    # Assinaturas
    employee_signature_id: UUID  # Referência à assinatura
    employee_signed_at: datetime
    employee_refused_sign: bool
    refusal_witness_1: str
    refusal_witness_2: str

    supervisor_signature_id: UUID
    supervisor_signed_at: datetime

    hr_signature_id: UUID
    hr_signed_at: datetime

    # Ciência
    employee_acknowledged: bool
    acknowledged_at: datetime

    # Histórico disciplinar (snapshot)
    previous_warnings_count: int
    previous_suspensions_count: int

    # Auditoria
    created_at: datetime
    created_by: UUID
    updated_at: datetime

# DISCIPLINARY_TEMPLATE (Templates de Documentos)
class DisciplinaryTemplate:
    id: UUID
    tenant_id: UUID
    action_type: ActionType
    name: str
    description: str
    content: text                # Template com placeholders {{employee_name}}, {{date}}, etc.
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

# DIGITAL_SIGNATURE (Assinatura Digital)
class DigitalSignature:
    id: UUID
    tenant_id: UUID
    signer_id: UUID              # Quem assinou
    signer_type: str             # EMPLOYEE, SUPERVISOR, WITNESS, HR
    document_type: str           # ADVERTENCIA, SUSPENSAO, CONTRATO, etc.
    document_id: UUID

    # Dados da assinatura
    signature_data: text         # Base64 da assinatura manuscrita (canvas)
    signature_hash: str          # Hash SHA-256 do documento no momento
    ip_address: str
    user_agent: str

    # Geolocalização
    latitude: float
    longitude: float

    # Validação
    is_valid: bool
    validated_at: datetime

    created_at: datetime
```

#### 2.3.2 Endpoints da API

```
# Medidas Administrativas
POST   /api/v1/operacional/medidas-administrativas                     # Criar
GET    /api/v1/operacional/medidas-administrativas                     # Listar
GET    /api/v1/operacional/medidas-administrativas/{id}                # Detalhe
PATCH  /api/v1/operacional/medidas-administrativas/{id}                # Atualizar
DELETE /api/v1/operacional/medidas-administrativas/{id}                # Cancelar

POST   /api/v1/operacional/medidas-administrativas/{id}/submeter       # Enviar para aprovação
POST   /api/v1/operacional/medidas-administrativas/{id}/aprovar        # Aprovar
POST   /api/v1/operacional/medidas-administrativas/{id}/rejeitar       # Rejeitar
POST   /api/v1/operacional/medidas-administrativas/{id}/assinar        # Registrar assinatura
POST   /api/v1/operacional/medidas-administrativas/{id}/recusar-assinatura  # Recusa de assinatura

GET    /api/v1/operacional/medidas-administrativas/funcionario/{eid}   # Histórico do funcionário
GET    /api/v1/operacional/medidas-administrativas/pendentes           # Pendentes de ação
GET    /api/v1/operacional/medidas-administrativas/estatisticas        # Estatísticas

# Templates
GET    /api/v1/operacional/medidas-administrativas/templates           # Listar templates
POST   /api/v1/operacional/medidas-administrativas/templates           # Criar template
GET    /api/v1/operacional/medidas-administrativas/templates/{id}      # Detalhe
PATCH  /api/v1/operacional/medidas-administrativas/templates/{id}      # Atualizar
POST   /api/v1/operacional/medidas-administrativas/gerar-documento     # Gerar documento do template

# Assinaturas
POST   /api/v1/operacional/assinaturas                                 # Registrar assinatura
GET    /api/v1/operacional/assinaturas/{id}                            # Verificar assinatura
GET    /api/v1/operacional/assinaturas/documento/{doc_id}              # Assinaturas de um documento
```

#### 2.3.3 Workflow de Medida Administrativa

```
┌─────────────────┐
│   RASCUNHO      │ ← Supervisor cria
└────────┬────────┘
         │ Submeter
         ▼
┌─────────────────┐
│   PENDENTE      │ ← Aguarda aprovação DP/RH
│   APROVAÇÃO     │
└────────┬────────┘
    ┌────┴────┐
  Aprovar   Rejeitar
    │         │
    ▼         ▼
┌─────────┐  ┌─────────┐
│APROVADA │  │CANCELADA│
└────┬────┘  └─────────┘
     │ Solicitar assinatura
     ▼
┌─────────────────┐
│   PENDENTE      │ ← Funcionário precisa assinar
│   ASSINATURA    │
└────────┬────────┘
    ┌────┴────────────┐
  Assinar         Recusar
    │                 │
    ▼                 ▼
┌─────────┐    ┌─────────────┐
│ ASSINADA│    │  RECUSADA   │
└────┬────┘    │ ASSINATURA  │
     │         └──────┬──────┘
     │                │ Testemunhas assinam
     │                ▼
     │         ┌─────────────┐
     │         │  APLICADA   │
     │         │ (com recusa)│
     │         └─────────────┘
     │
     ▼
┌─────────────────┐
│    APLICADA     │ → Registrado no histórico
└─────────────────┘
         │
         ▼
    Notifica DP/RH
    Atualiza eSocial (S-2240 se afastamento)
```

#### 2.3.4 Integração com DP/RH

| Evento | Ação no DP/RH |
|--------|---------------|
| Advertência aplicada | Registrar no prontuário do funcionário |
| Suspensão aplicada | Gerar afastamento, atualizar folha, eSocial S-2230 |
| 3ª advertência | Alertar para possível demissão por justa causa |
| Demissão justa causa | Iniciar processo de rescisão |

---

### 2.4 FASE 3: COMUNICAÇÃO OPERACIONAL (Prioridade P2)

**Objetivo:** Canal de comunicação em tempo real entre todos os níveis.

#### 2.4.1 Entidades

```python
# ANNOUNCEMENT (Comunicados)
class Announcement:
    id: UUID
    tenant_id: UUID

    # Segmentação
    target_type: str             # ALL, DEPARTMENT, CLIENT, POST, EMPLOYEE
    target_ids: List[UUID]       # IDs específicos
    target_roles: List[str]      # Cargos específicos

    # Conteúdo
    title: str
    content: text
    priority: str                # NORMAL, IMPORTANTE, URGENTE
    category: str                # INFORMATIVO, PROCEDIMENTO, ALERTA, TREINAMENTO

    # Período
    publish_at: datetime
    expires_at: datetime

    # Confirmação de leitura
    requires_acknowledgment: bool

    # Anexos
    attachments: List[Attachment]

    # Status
    status: str                  # DRAFT, SCHEDULED, PUBLISHED, EXPIRED, CANCELLED

    created_at: datetime
    created_by: UUID

# ANNOUNCEMENT_READ (Confirmação de Leitura)
class AnnouncementRead:
    id: UUID
    announcement_id: UUID
    user_id: UUID
    read_at: datetime
    acknowledged_at: datetime    # Se requer confirmação
    ip_address: str

# NOTIFICATION (Notificações Push)
class Notification:
    id: UUID
    tenant_id: UUID
    user_id: UUID

    # Conteúdo
    title: str
    body: str
    type: str                    # OCORRENCIA, MEDIDA, COMUNICADO, ESCALA, ALERTA

    # Referência
    reference_type: str          # occurrence, disciplinary_action, announcement, etc.
    reference_id: UUID

    # Status
    sent_at: datetime
    read_at: datetime
    clicked_at: datetime

    # Canais
    channels: List[str]          # PUSH, EMAIL, SMS, WHATSAPP

# CHAT_MESSAGE (Chat Operacional) - Futuro
class ChatMessage:
    id: UUID
    tenant_id: UUID
    channel_id: UUID             # Pode ser: post_id, client_id, department_id
    sender_id: UUID
    content: text
    message_type: str            # TEXT, IMAGE, FILE, LOCATION
    sent_at: datetime
    read_by: List[UUID]
```

#### 2.4.2 Endpoints da API

```
# Comunicados
POST   /api/v1/operacional/comunicados                     # Criar
GET    /api/v1/operacional/comunicados                     # Listar
GET    /api/v1/operacional/comunicados/{id}                # Detalhe
PATCH  /api/v1/operacional/comunicados/{id}                # Atualizar
DELETE /api/v1/operacional/comunicados/{id}                # Remover
POST   /api/v1/operacional/comunicados/{id}/publicar       # Publicar
POST   /api/v1/operacional/comunicados/{id}/confirmar      # Confirmar leitura
GET    /api/v1/operacional/comunicados/{id}/leituras       # Quem leu

# Notificações
GET    /api/v1/operacional/notificacoes                    # Minhas notificações
POST   /api/v1/operacional/notificacoes/{id}/lida          # Marcar como lida
POST   /api/v1/operacional/notificacoes/marcar-todas       # Marcar todas como lidas
GET    /api/v1/operacional/notificacoes/nao-lidas/count    # Contador

# Alertas (tempo real)
GET    /api/v1/operacional/alertas                         # Alertas ativos
WebSocket /ws/operacional/alertas                          # Stream de alertas
```

---

### 2.5 FASE 4: CONTROLE DE PONTO AVANÇADO (Prioridade P3)

**Objetivo:** Check-in com geolocalização e prova de vida.

#### 2.5.1 Melhorias no Shift (Turno)

```python
# Campos adicionais no Shift
class ShiftEnhanced:
    # ... campos existentes ...

    # Check-in avançado
    check_in_latitude: float
    check_in_longitude: float
    check_in_accuracy: float     # Precisão em metros
    check_in_photo_path: str     # Selfie do check-in
    check_in_device_id: str
    check_in_ip: str

    # Check-out avançado
    check_out_latitude: float
    check_out_longitude: float
    check_out_accuracy: float
    check_out_photo_path: str
    check_out_device_id: str
    check_out_ip: str

    # Validações
    check_in_within_radius: bool  # Estava no raio do posto?
    check_in_validated: bool
    check_in_validation_method: str  # GPS, WIFI, MANUAL

    # Anomalias
    has_anomaly: bool
    anomaly_type: str            # FORA_LOCAL, HORARIO_ERRADO, FOTO_INVALIDA
    anomaly_notes: str
    anomaly_resolved: bool
    anomaly_resolved_by: UUID
```

#### 2.5.2 Validações de Check-in

```python
def validate_check_in(shift, check_in_data):
    validations = []

    # 1. Validar geolocalização
    post = get_post(shift.post_id)
    distance = calculate_distance(
        check_in_data.latitude,
        check_in_data.longitude,
        post.latitude,
        post.longitude
    )
    if distance > post.allowed_radius_meters:  # Default 100m
        validations.append({
            "type": "FORA_LOCAL",
            "message": f"Check-in a {distance}m do posto (máximo {post.allowed_radius_meters}m)",
            "severity": "HIGH"
        })

    # 2. Validar horário
    tolerance_minutes = 15
    expected_time = shift.start_time
    actual_time = check_in_data.time
    diff_minutes = (actual_time - expected_time).minutes

    if diff_minutes > tolerance_minutes:
        validations.append({
            "type": "ATRASO",
            "message": f"Check-in com {diff_minutes} minutos de atraso",
            "severity": "MEDIUM"
        })

    # 3. Validar foto (prova de vida) - Integrar com AI
    if check_in_data.photo:
        face_validation = validate_face(
            check_in_data.photo,
            shift.employee_id
        )
        if not face_validation.is_valid:
            validations.append({
                "type": "FOTO_INVALIDA",
                "message": "Não foi possível validar identidade na foto",
                "severity": "HIGH"
            })

    return validations
```

---

### 2.6 FASE 5: RELATÓRIOS AVANÇADOS E IA (Prioridade P4)

#### 2.6.1 Relatórios Operacionais

```
1. Relatório de Cobertura Diária
   - Postos x Presenças
   - Faltas e substituições
   - Horas extras
   - Exportar PDF/Excel

2. Relatório de Ocorrências
   - Por período, cliente, categoria
   - Tempo médio de resolução
   - Taxa de escalação
   - Gráficos de tendência

3. Relatório Disciplinar
   - Medidas por funcionário
   - Reincidências
   - Por cliente/posto
   - Comparativo mensal

4. Relatório para Cliente
   - Cobertura do período
   - Ocorrências relevantes
   - Indicadores de qualidade
   - Exportar em formato profissional

5. Indicadores de Performance
   - Por funcionário
   - Por supervisor
   - Por cliente
   - Ranking e metas
```

#### 2.6.2 Expansão do Bartolo para Operacional

```python
# Novos prompts para o módulo operacional no Bartolo

MODULE_PROMPTS["operacional_avancado"] = {
    "category": ModuleCategory.OPERACOES,
    "name": "Operacional Avançado",
    "description": "Gestão completa de operações com IA",
    "prompt": """Você é o assistente especializado em Operações da Conecta Mais.

CONHECIMENTO PROFUNDO DO MÓDULO:

📍 POSTOS DE TRABALHO
- Tipos: Portaria, Vigilância, Limpeza, Manutenção, Administrativo
- Campos: Nome, endereço, cliente, contrato, turno, headcount
- Cada posto tem um raio de geolocalização para check-in (padrão 100m)

📅 ESCALAS E TURNOS
- Tipos de escala: 12x36, 6x1, 5x2, Administrativo, Personalizado
- Turno diurno: 07:00-19:00, Noturno: 19:00-07:00
- Regras CLT: máximo 44h semanais, 11h descanso entre jornadas
- Adicional noturno 20% (22h-05h), hora extra 50%/100%

👥 ALOCAÇÕES
- Funcionário é alocado a um posto (primário ou temporário)
- Qualificações necessárias por posto (curso vigilante, CNH, etc.)
- Funcionário pode ter alocações em múltiplos postos

🔄 SUBSTITUIÇÕES
- Motivos: Falta, férias, atestado, emergência
- Workflow: Solicitar → Confirmar substituto → Completar
- Sistema sugere substitutos com base em disponibilidade e custo

⏰ BANCO DE HORAS (CLT)
- Crédito: Horas extras trabalhadas
- Débito: Compensação de horas
- Validade: 6 meses (individual) ou 12 meses (acordo coletivo)
- Limite: 2 horas extras por dia

🚨 OCORRÊNCIAS
- Categorias: Segurança, Limpeza, Comportamento, Acidente, Manutenção
- Severidade: Baixa, Média, Alta, Crítica
- SLA de resolução por categoria
- Podem gerar medidas administrativas

📋 MEDIDAS ADMINISTRATIVAS
- Tipos: Advertência verbal, Advertência escrita, Suspensão
- Workflow: Criar → Aprovar DP → Assinar → Aplicar
- Progressão: 1ª advertência → 2ª advertência → Suspensão → Justa causa
- Suspensão: 1 a 30 dias (desconto em folha)

👷 DIARISTAS (PJ)
- Profissionais autônomos contratados por diária
- Emissão de RPA (Recibo de Pagamento Autônomo)
- Retenção de INSS (11%) e ISS quando aplicável
- Não têm vínculo CLT

INTEGRAÇÃO COM DP/RH:
- Medidas administrativas notificam DP automaticamente
- Suspensões geram afastamento no sistema de ponto
- Afastamentos > 15 dias podem virar auxílio-doença (INSS)
- Eventos são enviados ao eSocial quando aplicável

COMANDOS QUE POSSO EXECUTAR:
- Consultar escala de um posto ou funcionário
- Verificar quem está trabalhando agora
- Listar ocorrências pendentes
- Gerar relatório de cobertura
- Calcular horas extras de um funcionário
- Verificar histórico disciplinar
- Sugerir substituto para uma falta
- Criar rascunho de advertência

EXEMPLOS DE PERGUNTAS:
- "Quem está de plantão no posto X hoje?"
- "Quantas faltas tivemos essa semana?"
- "Qual o saldo de banco de horas do João?"
- "Liste as ocorrências críticas abertas"
- "O funcionário X tem advertências anteriores?"
- "Quanto de hora extra fizemos no cliente Y?"
""",
    "capabilities": [
        # Consultas
        "consultar_escala", "consultar_turno_atual", "verificar_presenca",
        "listar_ocorrencias", "consultar_historico_disciplinar",
        "consultar_banco_horas", "consultar_substituicoes",

        # Relatórios
        "gerar_relatorio_cobertura", "gerar_relatorio_ocorrencias",
        "gerar_relatorio_horas_extras", "gerar_relatorio_cliente",

        # Ações
        "criar_ocorrencia", "escalar_ocorrencia", "resolver_ocorrencia",
        "criar_medida_administrativa", "sugerir_substituto",
        "aprovar_banco_horas", "alocar_funcionario",

        # Cálculos
        "calcular_horas_extras", "calcular_custo_substituicao",
        "calcular_cobertura_periodo",
    ],
    "wizards": [
        "registrar_ocorrencia_completa",
        "criar_advertencia_passo_a_passo",
        "montar_escala_mensal",
        "substituir_funcionario",
    ],
}
```

---

## 3. INTEGRAÇÃO DP/RH - MAPA COMPLETO

### 3.1 Fluxos de Integração

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MÓDULO OPERACIONAL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Ocorrências │ Medidas Admin │ Turnos │ Banco Horas │ Substituições        │
└──────┬───────┴───────┬───────┴───┬────┴──────┬──────┴─────────┬────────────┘
       │               │           │           │                │
       ▼               ▼           ▼           ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE INTEGRAÇÃO                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Event Bus  │  │ Notificação│  │   Webhook  │  │    Sync    │            │
│  │ (Interno)  │  │   Service  │  │  (Externo) │  │   Service  │            │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘            │
└──────┬───────────────┬───────────────┬───────────────┬──────────────────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MÓDULO RH/DP                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Funcionários │ Folha Pagamento │ Afastamentos │ eSocial │ Prontuário      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Eventos e Ações

| Evento Operacional | Ação no DP/RH | Prioridade |
|-------------------|---------------|------------|
| Advertência aplicada | Registrar no prontuário | Imediata |
| Suspensão aplicada | Criar afastamento + Ajustar folha | Imediata |
| Falta não justificada | Descontar do salário | Fechamento folha |
| Atestado médico | Criar afastamento + Validar | Em até 24h |
| Hora extra aprovada | Registrar para folha | Fechamento folha |
| Banco de horas compensado | Registrar compensação | Imediata |
| Acidente de trabalho | CAT + eSocial S-2210 | Imediata |
| Funcionário afastado > 15 dias | Encaminhar INSS | Em até 48h |

### 3.3 Contratos de API entre Módulos

```python
# Operacional → RH: Notificar medida administrativa
@dataclass
class DisciplinaryActionEvent:
    action_id: UUID
    action_type: str  # ADVERTENCIA_VERBAL, ADVERTENCIA_ESCRITA, SUSPENSAO
    employee_id: UUID
    applied_at: datetime
    suspension_days: Optional[int]
    requires_payroll_adjustment: bool
    requires_esocial: bool
    created_by: UUID

# Operacional → RH: Registrar afastamento
@dataclass
class AbsenceEvent:
    employee_id: UUID
    absence_type: str  # FALTA, ATESTADO, SUSPENSAO, FERIAS
    start_date: date
    end_date: date
    reason: str
    document_path: Optional[str]
    requires_payroll_deduction: bool

# Operacional → RH: Horas extras para folha
@dataclass
class OvertimeEvent:
    employee_id: UUID
    reference_month: str  # "2026-01"
    normal_overtime_hours: float
    sunday_overtime_hours: float
    holiday_overtime_hours: float
    night_hours: float

# RH → Operacional: Funcionário admitido/demitido
@dataclass
class EmployeeStatusEvent:
    employee_id: UUID
    event_type: str  # ADMISSAO, DEMISSAO, FERIAS_INICIO, FERIAS_FIM, AFASTAMENTO
    effective_date: date
    details: dict
```

---

## 4. EXPANSÃO DO BARTOLO - PERFIS OPERACIONAIS

### 4.1 Novos Perfis a Adicionar

```python
# Adicionar em user_profiles.py

UserRole.INSPETOR = "inspetor"
UserRole.LIDER_POSTO = "lider_posto"
UserRole.ENCARREGADO = "encarregado"

USER_PROFILES[UserRole.INSPETOR] = {
    "department": Department.OPERACOES,
    "is_manager": False,
    "level": "field_supervisor",
    "focus": ["qualidade", "fiscalizacao", "ocorrencias", "clientes"],
    "modules_priority": ["operacoes", "ocorrencias", "escalas", "clientes"],
    "communication_style": "operational",
    "prompt_context": """
Este usuário é um INSPETOR de operações.

RESPONSABILIDADES:
- Fiscalizar postos de trabalho
- Verificar qualidade do serviço
- Registrar ocorrências em visitas
- Avaliar funcionários em campo
- Resolver problemas pontuais com clientes
- Acompanhar substituições

PODE FAZER:
- Registrar ocorrências de qualquer posto que visitar
- Ver escala de todos os postos da sua região
- Consultar histórico de funcionários
- Solicitar substituições
- Aplicar advertências verbais (registro)

NÃO PODE FAZER:
- Aprovar medidas administrativas escritas (só supervisão acima)
- Alterar escalas já publicadas
- Acessar dados financeiros

COMUNICAÇÃO:
- Use linguagem operacional e objetiva
- Foque em ações práticas
- Alerte sobre problemas urgentes
- Sugira soluções rápidas
""",
}

USER_PROFILES[UserRole.LIDER_POSTO] = {
    "department": Department.OPERACOES,
    "is_manager": False,
    "level": "team_lead",
    "focus": ["equipe_posto", "escala", "ocorrencias_locais"],
    "modules_priority": ["operacoes", "ponto", "ocorrencias"],
    "communication_style": "simple_operational",
    "prompt_context": """
Este usuário é um LÍDER DE POSTO.

RESPONSABILIDADES:
- Coordenar equipe no posto
- Distribuir tarefas diárias
- Registrar ocorrências do posto
- Controlar presença da equipe
- Ser ponto de contato com cliente
- Reportar ao supervisor

PODE FAZER:
- Ver escala do seu posto
- Registrar check-in/out da equipe
- Registrar ocorrências do posto
- Consultar banco de horas da equipe
- Solicitar substituição

NÃO PODE FAZER:
- Ver outros postos
- Aplicar medidas administrativas
- Aprovar horas extras
- Alterar escalas

COMUNICAÇÃO:
- Use linguagem simples e direta
- Foque no dia a dia do posto
- Oriente sobre procedimentos básicos
- Escale problemas complexos para supervisor
""",
}

USER_PROFILES[UserRole.ENCARREGADO] = {
    "department": Department.OPERACOES,
    "is_manager": True,
    "level": "coordinator",
    "focus": ["grupo_postos", "escalas", "funcionarios", "clientes"],
    "modules_priority": ["operacoes", "escalas", "ocorrencias", "ponto", "medidas"],
    "communication_style": "operational",
    "prompt_context": """
Este usuário é um ENCARREGADO de operações.

RESPONSABILIDADES:
- Coordenar grupo de postos (região ou cliente)
- Montar e ajustar escalas
- Gerenciar substituições
- Aplicar medidas administrativas
- Resolver problemas operacionais
- Interface entre campo e escritório

PODE FAZER:
- Gerenciar escalas dos seus postos
- Aprovar banco de horas
- Criar e submeter advertências
- Alocar/desalocar funcionários
- Ver relatórios dos seus postos
- Resolver ocorrências

PRECISA APROVAÇÃO PARA:
- Suspensões (aprovação do gerente)
- Horas extras acima do limite
- Contratação de diaristas

COMUNICAÇÃO:
- Linguagem operacional com detalhes
- Foque em gestão de equipe
- Oriente sobre processos e regras
- Destaque pendências e prazos
""",
}
```

### 4.2 Capacidades do Bartolo por Perfil

```python
# Permissões do Bartolo por perfil

BARTOLO_CAPABILITIES = {
    UserRole.DIRETOR: {
        "can_view": ["all"],
        "can_execute": ["relatorios", "dashboards", "kpis"],
        "can_approve": ["all"],
        "response_focus": "indicadores_estrategicos",
    },

    UserRole.GERENTE_OPERACOES: {
        "can_view": ["operacoes", "hr_operacional", "ocorrencias", "medidas"],
        "can_execute": ["escalas", "alocacoes", "substituicoes", "medidas", "relatorios"],
        "can_approve": ["suspensoes", "horas_extras", "diaristas"],
        "response_focus": "gestao_operacional",
    },

    UserRole.SUPERVISOR_OPERACOES: {
        "can_view": ["operacoes_regiao", "ocorrencias_regiao", "medidas_regiao"],
        "can_execute": ["escalas", "substituicoes", "advertencias", "ocorrencias"],
        "can_approve": ["banco_horas", "advertencias_escritas"],
        "response_focus": "operacao_diaria",
    },

    UserRole.INSPETOR: {
        "can_view": ["postos_regiao", "funcionarios_regiao", "ocorrencias"],
        "can_execute": ["ocorrencias", "advertencias_verbais"],
        "can_approve": [],
        "response_focus": "fiscalizacao_qualidade",
    },

    UserRole.LIDER_POSTO: {
        "can_view": ["meu_posto", "minha_equipe", "minha_escala"],
        "can_execute": ["check_in", "ocorrencias_posto", "solicitar_substituicao"],
        "can_approve": [],
        "response_focus": "rotina_posto",
    },

    UserRole.PORTEIRO: {
        "can_view": ["minha_escala", "meu_ponto", "meu_banco_horas"],
        "can_execute": ["check_in", "check_out"],
        "can_approve": [],
        "response_focus": "tarefas_basicas",
    },
}
```

---

## 5. CRONOGRAMA ESTIMADO

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              CRONOGRAMA DE IMPLEMENTAÇÃO                              │
├──────────┬───────────────────────────────────────────────────────────────────────────┤
│  Semana  │  Entrega                                                                  │
├──────────┼───────────────────────────────────────────────────────────────────────────┤
│   1-2    │  FASE 1: Módulo de Ocorrências (Backend + Frontend básico)               │
│   3-4    │  FASE 1: Ocorrências completo + Integração DP + Testes                   │
├──────────┼───────────────────────────────────────────────────────────────────────────┤
│   5-6    │  FASE 2: Medidas Administrativas (Backend + Templates)                   │
│   7-8    │  FASE 2: Assinatura Digital + Workflow + Frontend                        │
├──────────┼───────────────────────────────────────────────────────────────────────────┤
│   9-10   │  FASE 3: Comunicação (Comunicados + Notificações)                        │
│  11-12   │  FASE 3: Alertas tempo real + WebSocket + Testes                         │
├──────────┼───────────────────────────────────────────────────────────────────────────┤
│  13-14   │  FASE 4: Ponto Avançado (Geolocalização + Foto)                          │
├──────────┼───────────────────────────────────────────────────────────────────────────┤
│  15-16   │  FASE 5: Relatórios Avançados                                            │
│  17-18   │  FASE 5: Expansão Bartolo + Testes finais                                │
├──────────┼───────────────────────────────────────────────────────────────────────────┤
│    19    │  Treinamento + Documentação                                              │
│    20    │  Go-live + Acompanhamento                                                │
└──────────┴───────────────────────────────────────────────────────────────────────────┘
```

---

## 6. MÉTRICAS DE SUCESSO

| Métrica | Meta | Como Medir |
|---------|------|------------|
| Adoção do sistema | 90% dos supervisores usando | Logins ativos / Total supervisores |
| Tempo registro ocorrência | < 2 minutos | Tempo médio de criação |
| Ocorrências resolvidas no SLA | > 85% | Resolvidas no prazo / Total |
| Medidas com assinatura digital | 100% | Digital / Total medidas |
| Redução de papel | -80% | Documentos físicos antes/depois |
| Satisfação usuário | > 4.0/5.0 | NPS interno |

---

## 7. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Resistência à mudança | Alta | Alto | Treinamento intensivo, Bartolo como guia |
| Problemas de conectividade | Média | Alto | Modo offline com sync posterior |
| Sobrecarga de notificações | Média | Médio | Configuração por perfil, agrupamento |
| Assinatura não aceita juridicamente | Baixa | Crítico | Validar com jurídico, ICP-Brasil |
| Performance em listagens grandes | Média | Médio | Paginação, índices, cache |

---

## 8. PRÓXIMOS PASSOS

1. **Validar este plano** com stakeholders
2. **Definir prioridades** (confirmar ordem das fases)
3. **Alocar equipe** para desenvolvimento
4. **Criar tasks no Jira/Trello**
5. **Iniciar FASE 1** - Módulo de Ocorrências

---

*Documento gerado em 2026-01-18*
*Versão 1.0*
