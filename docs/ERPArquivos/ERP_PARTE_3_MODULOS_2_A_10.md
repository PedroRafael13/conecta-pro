# ERP CONECTA MAIS - PARTE 3: MÓDULOS 2-10 DETALHADOS

---

## 4.2 MÓDULO 2: Gestão de Contratos Inteligente

### 4.2.1 Visão Geral

**Objetivo:** Gerenciar todo o ciclo de vida dos contratos, desde a criação até o encerramento, com automações inteligentes para renovações, reajustes, aditivos e SLAs.

**Escopo:**
- Contratos recorrentes (mensalidades)
- Contratos pontuais (projetos únicos)
- Templates de contratos
- Cláusulas e condições
- Renovação automática
- Reajustes por índices econômicos
- Aditivos contratuais
- Gestão de SLA
- Penalidades e multas
- Histórico e auditoria

**Usuários:**
- Comercial
- Jurídico
- Financeiro
- Operações
- Clientes (via Conecta Plus)

### 4.2.2 Funcionalidades Detalhadas

**RF-CONT-001: Criação de Contratos**
- Criação a partir de proposta aprovada (integração com CRM)
- Criação manual
- Seleção de template
- Preenchimento automático de dados (cliente, serviços, valores)
- Cláusulas customizáveis
- Anexos (propostas, documentos, certificados)

**RF-CONT-002: Templates de Contratos**
- Templates pré-configurados por tipo de serviço:
  - Vigilância patrimonial
  - Portaria remota
  - Segurança eletrônica
  - Monitoramento 24h
  - Facilities (limpeza, jardinagem, manutenção)
- Editor de templates com variáveis dinâmicas
- Versionamento de templates
- Aprovação jurídica de templates

**RF-CONT-003: Cláusulas Inteligentes**
- Biblioteca de cláusulas padrão
- Cláusulas obrigatórias por tipo de contrato
- Cláusulas opcionais
- Variáveis dinâmicas: {cliente.nome}, {contrato.valor}, {data.inicio}
- Validação automática de cláusulas conflitantes

**RF-CONT-004: Tipos de Contratos**

**A. Contratos Recorrentes:**
- Faturamento mensal automático
- Renovação automática (se configurado)
- Reajuste anual por índice (IGPM, IPCA, INPC)
- Controle de vigência
- Notificações de vencimento (30, 60, 90 dias antes)

**B. Contratos Pontuais:**
- Valor fixo
- Entrega única
- Faturamento único ou parcelado
- Conclusão manual

**RF-CONT-005: Gestão de Vigência**
- Data de início e fim
- Período de carência
- Prazo de aviso prévio (rescisão)
- Status: Rascunho, Aguardando Assinatura, Ativo, Suspenso, Cancelado, Encerrado
- Alerta de vencimento próximo
- Renovação automática ou manual

**RF-CONT-006: Renovação Automática**
- Configuração de renovação automática (sim/não)
- Período de renovação (12 meses, 24 meses, etc)
- Notificação ao cliente antes da renovação (30 dias)
- Cliente pode aceitar ou recusar renovação via portal
- Se não houver manifestação, renovar automaticamente
- Aplicar reajuste na renovação (se configurado)

**RF-CONT-007: Reajustes de Contratos**
- Reajuste anual automático
- Índices suportados:
  - IGPM (FGV)
  - IPCA (IBGE)
  - INPC (IBGE)
  - Percentual fixo
  - Personalizado
- Integração com APIs de índices econômicos
- Data base de reajuste (aniversário do contrato)
- Cálculo automático do novo valor
- Geração de aditivo contratual
- Notificação ao cliente
- Aprovação do cliente (via portal)
- Atualização automática de faturamento

**Exemplo de Cálculo:**
```python
def calcular_reajuste(contrato):
    """
    Calcula reajuste anual do contrato
    """
    # Buscar índice do período
    data_base = contrato.start_date
    data_reajuste = data_base + relativedelta(years=1)
    
    if contrato.reajuste_indice == 'IGPM':
        # Buscar IGPM acumulado nos últimos 12 meses
        igpm = await get_igpm_acumulado(data_base, data_reajuste)
        percentual = igpm
    elif contrato.reajuste_indice == 'IPCA':
        ipca = await get_ipca_acumulado(data_base, data_reajuste)
        percentual = ipca
    elif contrato.reajuste_indice == 'FIXO':
        percentual = contrato.reajuste_percentual_fixo
    
    # Calcular novo valor
    valor_atual = contrato.valor_mensal
    valor_reajustado = valor_atual * (1 + percentual / 100)
    
    # Criar aditivo
    aditivo = Aditivo(
        contrato_id=contrato.id,
        tipo='reajuste',
        valor_anterior=valor_atual,
        valor_novo=valor_reajustado,
        percentual_reajuste=percentual,
        indice_utilizado=contrato.reajuste_indice,
        data_aplicacao=data_reajuste
    )
    
    return aditivo
```

**RF-CONT-008: Aditivos Contratuais**
- Tipos de aditivos:
  - Reajuste de valor
  - Alteração de escopo (adicionar/remover serviços)
  - Alteração de prazo (prorrogação/antecipação)
  - Alteração de equipe/postos
  - Alteração de equipamentos
  - Outras alterações
- Geração automática de documento de aditivo
- Assinatura digital
- Histórico completo de aditivos
- Versionamento do contrato

**RF-CONT-009: Gestão de SLA (Service Level Agreement)**
- Definição de indicadores por contrato:
  - Tempo de resposta a incidentes
  - Taxa de disponibilidade (uptime)
  - Tempo de resolução
  - Satisfação do cliente (CSAT, NPS)
- Metas e tolerâncias
- Cálculo automático de atingimento
- Penalidades por descumprimento (desconto em fatura)
- Bonificações por superação
- Relatório mensal de SLA

**Exemplo de SLA:**
```python
class SLA:
    def __init__(self, contrato_id):
        self.contrato_id = contrato_id
        self.indicadores = {
            'tempo_resposta': {
                'meta': 15,  # minutos
                'unidade': 'minutos',
                'peso': 30,  # % no cálculo geral
                'penalidade': 5  # % de desconto se não atingir
            },
            'disponibilidade': {
                'meta': 99.5,  # %
                'unidade': 'percentual',
                'peso': 40,
                'penalidade': 10
            },
            'satisfacao': {
                'meta': 8.0,  # nota 0-10
                'unidade': 'nota',
                'peso': 30,
                'penalidade': 5
            }
        }
    
    def calcular_atingimento_mensal(self, mes, ano):
        """Calcula % de atingimento do SLA no mês"""
        resultados = {}
        score_total = 0
        
        for indicador, config in self.indicadores.items():
            # Buscar dados do indicador no mês
            valor_real = self.buscar_valor_real(indicador, mes, ano)
            meta = config['meta']
            peso = config['peso']
            
            # Calcular atingimento
            if indicador == 'tempo_resposta':
                atingimento = min((meta / valor_real) * 100, 100)
            else:
                atingimento = min((valor_real / meta) * 100, 100)
            
            resultados[indicador] = {
                'meta': meta,
                'real': valor_real,
                'atingimento': atingimento
            }
            
            # Ponderar pelo peso
            score_total += atingimento * (peso / 100)
        
        # Aplicar penalidade se necessário
        penalidade_total = 0
        if score_total < 100:
            for indicador, resultado in resultados.items():
                if resultado['atingimento'] < 100:
                    penalidade_total += self.indicadores[indicador]['penalidade']
        
        return {
            'score': score_total,
            'resultados': resultados,
            'penalidade': penalidade_total
        }
```

**RF-CONT-010: Penalidades e Multas**
- Penalidades por descumprimento de SLA (automáticas)
- Multas rescisórias (configuráveis)
- Multas por atraso de pagamento
- Desconto automático em fatura
- Registro e auditoria de penalidades

**RF-CONT-011: Assinatura Digital**
- Integração com DocuSign, Clicksign, ClickSign
- Fluxo de assinaturas:
  1. Cliente assina
  2. Representante legal da Conecta Mais assina
  3. Testemunhas (se necessário)
- Certificado ICP-Brasil
- Validade jurídica
- Armazenamento seguro (blockchain opcional)

**RF-CONT-012: Gestão Documental**
- Armazenamento de contratos assinados
- Anexos (propostas, termos, certificados, apólices)
- Versionamento
- Controle de acesso
- Busca full-text
- Download de documentos

**RF-CONT-013: Notificações Automáticas**
- Vencimento próximo (30, 60, 90 dias)
- Renovação automática pendente
- Reajuste aplicado
- Aditivo criado
- SLA não atingido
- Inadimplência
- Via: e-mail, SMS, WhatsApp, push notification (app)

**RF-CONT-014: Portal do Cliente (Conecta Plus)**
- Cliente visualiza seus contratos
- Faz download de documentos
- Solicita aditivos
- Aprova renovações
- Acompanha SLA
- Histórico de alterações

**RF-CONT-015: Relatórios e Analytics**
- Contratos ativos por cliente
- Contratos por tipo de serviço
- Faturamento recorrente (MRR/ARR)
- Taxa de renovação
- Taxa de churn
- Vida útil média de contrato (LTV)
- Contratos próximos do vencimento
- Histórico de reajustes

### 4.2.3 Modelo de Dados

```python
from sqlalchemy import Column, Integer, String, Decimal, DateTime, Boolean, ForeignKey, Enum, Text, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class ContractType(enum.Enum):
    RECURRING = "recurring"  # Recorrente (mensal)
    ONE_TIME = "one_time"    # Pontual (único)

class ContractStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    TERMINATED = "terminated"

class Contract(Base):
    __tablename__ = "contracts"
    
    # Identificação
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False)
    contract_number = Column(String(20), unique=True, nullable=False)  # CONT-2024-0001
    
    # Relacionamentos
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=True)
    
    # Tipo e Status
    contract_type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    
    # Template
    template_id = Column(Integer, ForeignKey('contract_templates.id'), nullable=True)
    
    # Valores
    monthly_value = Column(Decimal(10, 2), nullable=False)  # Para recorrente
    total_value = Column(Decimal(10, 2), nullable=False)     # Para pontual
    setup_fee = Column(Decimal(10, 2), default=0)            # Taxa de instalação
    
    # Vigência
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # Null = indeterminado
    grace_period_days = Column(Integer, default=0)
    notice_period_days = Column(Integer, default=30)  # Aviso prévio para rescisão
    
    # Renovação
    auto_renewal = Column(Boolean, default=True)
    renewal_period_months = Column(Integer, default=12)
    
    # Reajuste
    adjustment_enabled = Column(Boolean, default=True)
    adjustment_index = Column(String(20), nullable=True)  # IGPM, IPCA, INPC, FIXO
    adjustment_fixed_percent = Column(Decimal(5, 2), nullable=True)
    adjustment_base_date = Column(Date, nullable=True)
    last_adjustment_date = Column(Date, nullable=True)
    next_adjustment_date = Column(Date, nullable=True)
    
    # SLA
    has_sla = Column(Boolean, default=True)
    sla_config = Column(JSON, nullable=True)  # Configuração dos indicadores
    
    # Conteúdo
    content = Column(Text, nullable=False)  # Texto completo do contrato
    clauses = Column(JSON, nullable=True)   # Cláusulas específicas
    
    # Assinatura
    signature_required = Column(Boolean, default=True)
    signature_provider = Column(String(50), nullable=True)
    signature_document_id = Column(String(100), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    signed_by_client = Column(String(200), nullable=True)
    signed_by_company = Column(String(200), nullable=True)
    
    # Documentos
    pdf_file_path = Column(String(255), nullable=True)
    
    # Responsáveis
    commercial_manager_id = Column(Integer, ForeignKey('users.id'))
    account_manager_id = Column(Integer, ForeignKey('users.id'))
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamentos
    client = relationship("Client", back_populates="contracts")
    opportunity = relationship("Opportunity", back_populates="contract")
    template = relationship("ContractTemplate")
    addendums = relationship("ContractAddendum", back_populates="contract")
    services = relationship("ContractService", back_populates="contract")
    posts = relationship("Post", back_populates="contract")
    invoices = relationship("Invoice", back_populates="contract")
    sla_reports = relationship("SLAReport", back_populates="contract")

class ContractTemplate(Base):
    __tablename__ = "contract_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    service_type = Column(String(50))  # vigilancia, eletronica, facilities, etc
    content_template = Column(Text, nullable=False)  # Template com variáveis
    clauses = Column(JSON)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    approved_by_legal = Column(Boolean, default=False)
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

class ContractAddendum(Base):
    __tablename__ = "contract_addendums"
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    addendum_number = Column(String(20), nullable=False)  # ADI-2024-0001
    
    # Tipo
    addendum_type = Column(String(50), nullable=False)  # reajuste, escopo, prazo, etc
    
    # Valores (para reajuste)
    previous_value = Column(Decimal(10, 2))
    new_value = Column(Decimal(10, 2))
    adjustment_percent = Column(Decimal(5, 2))
    adjustment_index = Column(String(20))
    
    # Datas
    effective_date = Column(Date, nullable=False)
    
    # Descrição
    description = Column(Text, nullable=False)
    reason = Column(Text)
    
    # Assinatura
    signed = Column(Boolean, default=False)
    signed_at = Column(DateTime)
    signature_document_id = Column(String(100))
    
    # Documento
    pdf_file_path = Column(String(255))
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamento
    contract = relationship("Contract", back_populates="addendums")

class ContractService(Base):
    """Serviços incluídos no contrato"""
    __tablename__ = "contract_services"
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Decimal(10, 2), nullable=False)
    total_price = Column(Decimal(10, 2), nullable=False)
    
    description = Column(Text)
    
    # Relacionamentos
    contract = relationship("Contract", back_populates="services")
    service = relationship("Service")

class SLAReport(Base):
    """Relatório mensal de SLA"""
    __tablename__ = "sla_reports"
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    
    # Período
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    
    # Resultados
    indicators = Column(JSON, nullable=False)  # Resultados de cada indicador
    overall_score = Column(Decimal(5, 2), nullable=False)  # Score geral 0-100
    
    # Penalidades
    penalty_applied = Column(Boolean, default=False)
    penalty_percent = Column(Decimal(5, 2), default=0)
    penalty_amount = Column(Decimal(10, 2), default=0)
    
    # Status
    status = Column(String(20), default='draft')  # draft, approved, disputed
    
    # Auditoria
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamento
    contract = relationship("Contract", back_populates="sla_reports")
```

---

## 4.3 MÓDULO 3: Gestão de Postos e Escalas

### 4.3.1 Visão Geral

**Objetivo:** Gerenciar alocação de funcionários em postos de trabalho, escalas de trabalho, turnos, folgas e substituições de forma automatizada e inteligente.

**Escopo:**
- Cadastro de postos
- Tipos de escala (12x36, 6x1, 5x2, turno administrativo)
- Alocação de funcionários
- Geração automática de escalas
- Controle de folgas
- Gestão de substituições
- Banco de horas
- Otimização de alocação (IA)

### 4.3.2 Funcionalidades Detalhadas

**RF-POST-001: Cadastro de Postos**
- Informações do posto:
  - Nome/Identificação
  - Cliente/Contrato
  - Local (endereço)
  - Tipo de serviço (vigilante, porteiro, recepcionista, etc)
  - Turno (diurno, noturno, 24h)
  - Requisitos (qualificações necessárias)
  - Equipamentos necessários
- Status: Ativo, Inativo, Temporário
- Histórico de funcionários alocados

**RF-POST-002: Tipos de Escala**

**A. 12x36 (12 horas de trabalho x 36 horas de descanso):**
- Mais comum em segurança
- Turnos de 12h (07h-19h ou 19h-07h)
- 15 dias trabalhados por mês
- Cálculo automático de horas extras

**B. 6x1 (6 dias de trabalho x 1 dia de folga):**
- Comum em portaria
- Jornada de 8h/dia
- 1 folga semanal

**C. 5x2 (5 dias x 2 dias de folga):**
- Escala administrativa
- Segunda a sexta
- Fim de semana livre

**D. Turnos Revezamento:**
- Manhã (06h-14h)
- Tarde (14h-22h)
- Noite (22h-06h)
- Rodízio semanal ou quinzenal

**RF-POST-003: Alocação de Funcionários**
- Vincular funcionário a posto
- Data de início
- Data de fim (se temporário)
- Escala de trabalho
- Salário/custo
- Observações

**RF-POST-004: Geração Automática de Escalas (IA)**
- Sistema gera escala mensal automaticamente
- Considera:
  - Tipo de escala do posto
  - Feriados
  - Férias de funcionários
  - Atestados médicos
  - Folgas programadas
  - Banco de horas
  - Preferências de funcionários (se configurado)
- Otimização para minimizar horas extras
- Distribuição justa de turnos

**Algoritmo de Geração de Escala:**
```python
from datetime import datetime, timedelta
from typing import List, Dict
import holidays

class ScaleGenerator:
    def __init__(self, post: Post, employees: List[Employee], month: int, year: int):
        self.post = post
        self.employees = employees
        self.month = month
        self.year = year
        self.br_holidays = holidays.Brazil(state='AM')  # Amazonas
    
    def generate_12x36_scale(self):
        """Gera escala 12x36"""
        scale = []
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        
        # Alternar entre funcionários
        employee_index = 0
        current_date = datetime(self.year, self.month, 1)
        
        for day in range(1, days_in_month + 1):
            current_date = datetime(self.year, self.month, day)
            
            # Verifica se é dia de trabalho do funcionário atual
            employee = self.employees[employee_index]
            
            shift_entry = {
                'date': current_date,
                'employee_id': employee.id,
                'post_id': self.post.id,
                'shift_type': self.post.shift_type,  # day or night
                'start_time': '07:00' if self.post.shift_type == 'day' else '19:00',
                'end_time': '19:00' if self.post.shift_type == 'day' else '07:00',
                'hours': 12,
                'is_holiday': current_date in self.br_holidays,
                'is_sunday': current_date.weekday() == 6
            }
            
            scale.append(shift_entry)
            
            # Alternar a cada 1 dia (12x36)
            employee_index = (employee_index + 1) % len(self.employees)
        
        return scale
    
    def generate_6x1_scale(self):
        """Gera escala 6x1"""
        scale = []
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        
        employee_index = 0
        days_worked = 0
        
        for day in range(1, days_in_month + 1):
            current_date = datetime(self.year, self.month, day)
            employee = self.employees[employee_index]
            
            if days_worked < 6:
                # Dia de trabalho
                shift_entry = {
                    'date': current_date,
                    'employee_id': employee.id,
                    'post_id': self.post.id,
                    'shift_type': 'regular',
                    'start_time': '08:00',
                    'end_time': '17:00',
                    'hours': 8,
                    'is_off_day': False
                }
                days_worked += 1
            else:
                # Dia de folga
                shift_entry = {
                    'date': current_date,
                    'employee_id': employee.id,
                    'post_id': self.post.id,
                    'is_off_day': True
                }
                days_worked = 0
                employee_index = (employee_index + 1) % len(self.employees)
            
            scale.append(shift_entry)
        
        return scale
    
    def optimize_scale(self, scale: List[Dict]):
        """Otimiza escala para reduzir custos e melhorar distribuição"""
        # IA pode otimizar considerando:
        # - Custo de horas extras
        # - Preferências de funcionários
        # - Distância do funcionário ao posto
        # - Experiência do funcionário
        # - Histórico de performance
        
        # Exemplo simples: balancear turnos noturnos
        night_shifts_per_employee = {}
        
        for entry in scale:
            if not entry.get('is_off_day') and entry.get('shift_type') == 'night':
                employee_id = entry['employee_id']
                night_shifts_per_employee[employee_id] = night_shifts_per_employee.get(employee_id, 0) + 1
        
        # Redistribuir se houver desbalanceamento
        # ... lógica de otimização ...
        
        return scale
```

**RF-POST-005: Substituições**
- Funcionário falta/atesta → Sistema sugere substituto automaticamente
- Critérios de sugestão:
  - Mesma qualificação
  - Disponível no dia
  - Próximo ao local
  - Menor custo (hora extra vs. novo funcionário)
- Aprovação de supervisor
- Notificação ao substituto (app + WhatsApp)
- Registro de substituição

**RF-POST-006: Banco de Horas**
- Controle de saldo de horas por funcionário
- Horas positivas (a favor do empregador)
- Horas negativas (a favor do empregado)
- Compensação em folgas
- Limite máximo (CLT: 2h/dia)
- Relatório mensal

**RF-POST-007: Notificações de Escala**
- Envio automático de escala mensal
- Via app, e-mail, WhatsApp
- Lembrete 1 dia antes do turno
- Alerta de mudança de escala

**RF-POST-008: Dashboard Operacional**
- Postos preenchidos vs. vagos
- Funcionários alocados
- Escalas do dia
- Faltas e substituições
- Horas extras previstas
- Custos de folha por posto

---

## 4.4 MÓDULO 4: Facilities (Limpeza, Jardinagem, Manutenção)

### 4.4.1 Visão Geral

**Objetivo:** Gerenciar serviços de facilities: limpeza, jardinagem, manutenção predial, com checklist, agendamentos e controle de qualidade.

**Escopo:**
- Ordens de serviço
- Checklists de limpeza
- Agendamento de manutenção
- Controle de materiais/produtos
- Avaliação de qualidade
- Relatórios fotográficos

### 4.4.2 Funcionalidades Detalhadas

**RF-FAC-001: Ordens de Serviço**
- Tipos:
  - Limpeza programada
  - Jardinagem
  - Manutenção preventiva
  - Manutenção corretiva
  - Dedetização
  - Pintura
- Status: Pendente, Em Andamento, Concluída, Cancelada
- Prioridade: Baixa, Média, Alta, Urgente

**RF-FAC-002: Checklists Digitais**
- Templates por tipo de serviço
- Checklist de limpeza:
  - Áreas comuns
  - Banheiros
  - Escadas
  - Elevadores
  - Garagem
  - Salão de festas
- Checklist de jardinagem:
  - Poda de árvores
  - Corte de grama
  - Irrigação
  - Adubação
- Preenchimento via app mobile
- Fotos obrigatórias (antes/depois)
- Assinatura digital do responsável

**RF-FAC-003: Agendamento de Manutenção**
- Manutenção preventiva:
  - Programação automática (mensal, trimestral, semestral, anual)
  - Equipamentos: elevadores, geradores, bombas, portões
  - Lembretes automáticos
- Manutenção corretiva:
  - Solicitação via portal (cliente) ou app (funcionário)
  - Priorização automática
  - Prazo de atendimento (SLA)

**RF-FAC-004: Controle de Materiais**
- Consumo de produtos de limpeza
- Estoque mínimo
- Solicitação de compra
- Custos por contrato

**RF-FAC-005: Avaliação de Qualidade**
- Cliente avalia serviço via app
- Nota de 1 a 5 estrelas
- Comentários
- Fotos (se houver problema)
- Feedback para equipe

---

## 4.5 MÓDULO 5: Portaria Remota e Central de Monitoramento 24h

**IMPORTANTE:** Este módulo está no **Conecta Guardian**, mas o ERP precisa se integrar para:
- Enviar dados de contratos/postos
- Receber logs e ocorrências
- Gerar relatórios consolidados

### 4.5.1 Integração ERP ↔ Conecta Guardian

**Dados que o ERP ENVIA:**
- Contratos ativos
- Clientes e endereços
- Postos criados
- Funcionários alocados
- Configurações de acesso
- Moradores/visitantes autorizados

**Dados que o ERP RECEBE:**
- Ocorrências (alarmes, incidentes)
- Logs de acesso
- Fotos/vídeos de eventos
- Status de equipamentos
- Relatórios de atendimento

**APIs de Integração:**
```python
# ERP envia contrato para Guardian
POST /api/guardian/contracts
{
    "contract_id": 123,
    "client_id": 456,
    "address": "...",
    "services": ["remote_gatehouse", "monitoring_24h", "cctv"],
    "start_date": "2024-01-01"
}

# Guardian envia ocorrência para ERP
POST /api/erp/occurrences
{
    "contract_id": 123,
    "occurrence_type": "alarm",
    "severity": "high",
    "description": "Alarme de incêndio disparado",
    "date": "2024-12-29T10:30:00Z",
    "images": ["url1", "url2"],
    "action_taken": "Acionado bombeiros"
}
```

---

## 4.6 MÓDULO 6: Gestão de Equipamentos (Segurança Eletrônica)

### 4.6.1 Visão Geral

**Objetivo:** Gerenciar equipamentos de segurança eletrônica instalados nos clientes: câmeras, alarmes, sensores, controle de acesso, etc.

**Escopo:**
- Cadastro de equipamentos
- Instalação e configuração
- Manutenção (preventiva e corretiva)
- Garantia
- Controle de estoque
- Comodato

### 4.6.2 Funcionalidades Detalhadas

**RF-EQUIP-001: Cadastro de Equipamentos**
- Tipos:
  - Câmeras IP
  - DVR/NVR
  - Alarmes
  - Sensores (movimento, abertura, fumaça)
  - Centrais de controle de acesso
  - Catracas
  - Portões automáticos
- Informações:
  - Marca, modelo, número de série
  - Data de aquisição
  - Valor
  - Fornecedor
  - Garantia (início, fim)
  - Status: Estoque, Instalado, Manutenção, Defeito, Baixa

**RF-EQUIP-002: Instalação**
- Ordem de serviço de instalação
- Técnico responsável
- Data e hora
- Local exato (GPS)
- Fotos da instalação
- Termo de aceite (cliente)
- Configuração técnica (IP, portas, credenciais)

**RF-EQUIP-003: Technology Park (Parque Tecnológico)**
- Visualização de todos os equipamentos instalados por cliente
- Mapa/planta baixa com localização
- Status online/offline
- Último evento
- Próxima manutenção

**RF-EQUIP-004: Manutenção**
- Preventiva (agendada)
- Corretiva (chamado)
- Checklist de manutenção
- Peças substituídas
- Custo
- Relatório técnico

**RF-EQUIP-005: Comodato**
- Equipamentos em comodato (empréstimo ao cliente)
- Contrato de comodato
- Termo de devolução
- Controle de baixa patrimonial

---

## 4.7 MÓDULO 7: Gestão de Ocorrências

### 4.7.1 Visão Geral

**Objetivo:** Registrar, classificar e gerenciar todas as ocorrências operacionais: incidentes, acidentes, desvios, não-conformidades.

**Escopo:**
- Registro de ocorrências
- Classificação e priorização
- Investigação
- Planos de ação
- Análise de causas (RCA)
- Prevenção de recorrência

### 4.7.2 Funcionalidades Detalhadas

**RF-OCOR-001: Tipos de Ocorrências**
- Incidentes de segurança:
  - Furto/roubo
  - Invasão
  - Agressão
  - Vandalismo
  - Incêndio
- Acidentes de trabalho:
  - Funcionário
  - Terceiro
  - Cliente
- Desvios operacionais:
  - Atraso de funcionário
  - Abandono de posto
  - Não cumprimento de procedimento
- Não-conformidades:
  - Equipamento com defeito
  - Falta de material
  - Limpeza inadequada

**RF-OCOR-002: Registro de Ocorrência**
- Pode ser registrada por:
  - Funcionário (via app)
  - Supervisor
  - Cliente (via portal)
  - Sistema (automático - ex: alarme)
- Informações:
  - Data/hora
  - Local
  - Tipo de ocorrência
  - Gravidade (Baixa, Média, Alta, Crítica)
  - Descrição detalhada
  - Pessoas envolvidas
  - Testemunhas
  - Fotos/vídeos
  - Ação imediata tomada

**RF-OCOR-003: Notificações**
- Supervisor imediato (sempre)
- Gerente operacional (se gravidade >= Média)
- Diretoria (se crítica)
- Cliente (se impactar o serviço)
- Via: app, e-mail, SMS, WhatsApp, telefone

**RF-OCOR-004: Investigação**
- Atribuir investigador
- Prazo para conclusão
- Entrevistas
- Análise de evidências
- Conclusões

**RF-OCOR-005: Análise de Causa Raiz (RCA)**
- Metodologia 5 Porquês
- Diagrama de Ishikawa (Espinha de Peixe)
- Identificação de causa raiz
- Ações corretivas
- Ações preventivas

**RF-OCOR-006: Plano de Ação**
- Ações a serem tomadas
- Responsável por cada ação
- Prazo
- Status: Pendente, Em Andamento, Concluída
- Evidências de conclusão

**RF-OCOR-007: Dashboard de Ocorrências**
- Ocorrências abertas
- Ocorrências por tipo
- Ocorrências por gravidade
- Ocorrências por cliente
- Tempo médio de resolução
- Recorrências (mesma ocorrência repetida)

---

## 4.8 MÓDULO 8: Gestão de Visitantes e Acesso

### 4.8.1 Visão Geral

**Objetivo:** Gerenciar visitantes, prestadores de serviço, entregas em condomínios e empresas. Integração com controle de acesso e portaria remota.

**Escopo:**
- Pré-cadastro de visitantes
- Autorização de acesso
- Registro de entrada/saída
- Visitantes recorrentes
- Lista negra
- Relatórios de acesso

### 4.8.2 Funcionalidades Detalhadas

**RF-VIS-001: Pré-cadastro (Morador via App)**
- Morador cadastra visitante antes da visita:
  - Nome completo
  - CPF/RG
  - Foto (opcional)
  - Placa do veículo (se vier de carro)
  - Data e hora prevista
  - Observações
- Sistema gera QR Code de autorização
- Morador envia QR Code para visitante (WhatsApp/e-mail)

**RF-VIS-002: Autorização na Portaria**
- Visitante apresenta QR Code ou documento
- Porteiro escaneia QR Code ou busca por nome/CPF
- Sistema valida autorização
- Se autorizado: libera entrada e registra
- Se não autorizado: liga para morador para confirmar
- Foto obrigatória na entrada (app ou câmera)

**RF-VIS-003: Tipos de Visitantes**
- Visitante comum (ocasional)
- Prestador de serviço
- Entrega (delivery, correspondência)
- Motorista de app (Uber, 99)
- Visitante recorrente (ex: faxineira, professor)

**RF-VIS-004: Visitantes Recorrentes**
- Morador pode cadastrar visitante recorrente:
  - Autorização permanente
  - Dias/horários específicos
  - Validade
- Porteiro apenas confere identidade

**RF-VIS-005: Lista Negra**
- Visitantes bloqueados
- Motivo do bloqueio
- Solicitado por morador ou condomínio
- Alerta para porteiro se tentar entrar

**RF-VIS-006: Controle de Saída**
- Registro de saída
- Tempo de permanência
- Se visitante não saiu em tempo esperado → alerta

**RF-VIS-007: Relatórios**
- Visitantes por período
- Visitantes por morador
- Prestadores mais frequentes
- Tempo médio de permanência
- Acessos negados

---

## 4.9 MÓDULO 9: Gestão de Moradores (Condomínios)

### 4.9.1 Visão Geral

**Objetivo:** Gerenciar cadastro de moradores, unidades, veículos, pets, comunicados.

**Escopo:**
- Cadastro de unidades
- Cadastro de moradores
- Veículos
- Pets
- Comunicados
- Reserva de áreas comuns

### 4.9.2 Funcionalidades Detalhadas

**RF-MOR-001: Cadastro de Unidades**
- Número/Bloco
- Proprietário
- Morador(es)
- Inquilino (se for)
- Status: Ocupada, Vaga, Em Obra

**RF-MOR-002: Cadastro de Moradores**
- Dados pessoais (nome, CPF, telefone, e-mail)
- Foto
- Tipo: Proprietário, Morador, Inquilino, Dependente
- Veículos
- Pets
- Credenciais de acesso (tags, biometria)

**RF-MOR-003: Veículos**
- Placa
- Marca/modelo/cor
- Foto
- Vaga de garagem

**RF-MOR-004: Pets**
- Nome
- Tipo (cão, gato, etc)
- Raça
- Foto
- Vacinas em dia

**RF-MOR-005: Comunicados**
- Síndico/Administração envia comunicados
- Via: app, e-mail, SMS
- Confirmação de leitura
- Anexos

**RF-MOR-006: Reserva de Áreas Comuns**
- Salão de festas, churrasqueira, quadra, piscina
- Calendário de reservas
- Regras (quantidade de reservas por mês, antecedência mínima)
- Taxa (se houver)
- Aprovação automática ou manual

---

## 4.10 MÓDULO 10: Gestão de Documentos (GED)

### 4.10.1 Visão Geral

**Objetivo:** Armazenar, organizar e gerenciar todos os documentos da empresa e dos funcionários de forma centralizada e segura.

**Escopo:**
- Documentos da empresa (contratos, CNDs, certificados)
- Documentos de funcionários (RG, CPF, CTPS, atestados, etc)
- Controle de vencimento
- Assinatura digital
- Busca full-text
- Versionamento
- Controle de acesso

### 4.10.2 Funcionalidades Detalhadas

**RF-GED-001: Tipos de Documentos**

**A. Documentos da Empresa:**
- CNDs (Federal, Estadual, Municipal, FGTS, Trabalhista)
- Certidões negativas
- Alvarás
- Licenças
- Certificações (ISO, ABNT, etc)
- Apólices de seguro
- Contratos com fornecedores
- Procurações

**B. Documentos de Funcionários:**
- Pessoais: RG, CPF, CNH, Título de eleitor, Reservista, Comprovante de residência
- Trabalhistas: CTPS, PIS, Contrato de trabalho, Termo de admissão, Exame admissional (ASO), Declaração de dependentes
- Formação: Diplomas, Certificados de curso, Registro profissional (vigilante, técnico, etc)
- Saúde: Exames periódicos (ASO), Atestados médicos, Cartão de vacina
- Outros: Foto 3x4, Comprovante escolaridade dependentes, Certidão de nascimento/casamento

**RF-GED-002: Upload e Armazenamento**
- Upload via web ou app
- Formatos suportados: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX
- OCR automático (extração de texto de imagens)
- Compressão e otimização
- Armazenamento em S3/Blob Storage
- Backup automático

**RF-GED-003: Organização**
- Pastas hierárquicas
- Tags
- Categorias
- Busca por: nome, tipo, data, tags, conteúdo (full-text)

**RF-GED-004: Controle de Vencimento**
- Data de vencimento de documentos
- Alertas automáticos:
  - 60 dias antes
  - 30 dias antes
  - 15 dias antes
  - No dia do vencimento
- Dashboard de documentos vencidos/próximos do vencimento

**RF-GED-005: Assinatura Digital**
- Integração com DocuSign/Clicksign
- Fluxo de assinatura
- Certificado ICP-Brasil

**RF-GED-006: Versionamento**
- Múltiplas versões do mesmo documento
- Histórico de alterações
- Comparação entre versões

**RF-GED-007: Controle de Acesso**
- Permissões por usuário/grupo
- Leitura, escrita, exclusão
- Auditoria de acessos

**RF-GED-008: Integração com Outros Módulos**
- Contratos → Anexar documentos ao contrato
- RH → Documentos do funcionário
- Kits Documentais → Buscar documentos automaticamente

---

**CONTINUA NA PARTE 4...**

