# ERP CONECTA MAIS - PARTE 2: ESPECIFICAÇÃO DETALHADA DOS 38 MÓDULOS

## Continuação do Guia Completo de Implementação

---

# 4. ESPECIFICAÇÃO DOS 38 MÓDULOS

## Estrutura de Cada Módulo

Cada módulo será documentado com:
1. **Visão Geral**
2. **Funcionalidades Detalhadas**
3. **Requisitos Funcionais**
4. **Requisitos Não-Funcionais**
5. **Modelo de Dados (Entities)**
6. **APIs/Endpoints**
7. **Regras de Negócio**
8. **Integrações**
9. **MCPs Utilizados**
10. **Skills Aplicadas**
11. **Agentes de IA**
12. **Telas/Interfaces**
13. **Fluxos de Processo**
14. **Casos de Uso**
15. **Critérios de Aceitação**

---

## CATEGORIA 1: COMERCIAL E CONTRATOS

### 4.1 MÓDULO 1: CRM e Gestão Comercial Inteligente

#### 4.1.1 Visão Geral

**Objetivo:** Gerenciar todo o ciclo comercial desde a prospecção até o fechamento, com suporte de IA para otimizar conversões e aumentar produtividade da equipe de vendas.

**Escopo:**
- Gestão de leads (captura, qualificação, distribuição)
- Gestão de oportunidades (pipeline, funil)
- Propostas comerciais automatizadas
- Cotações e orçamentos
- Comissões de vendedores
- Análise de performance comercial

**Usuários:**
- Vendedores
- Gerente Comercial
- Diretoria

#### 4.1.2 Funcionalidades Detalhadas

**1. Gestão de Leads**

**RF-CRM-001: Captura de Leads**
- Sistema deve permitir captura de leads por múltiplos canais:
  - Formulário web (site Conecta Mais)
  - Landing pages
  - WhatsApp Business API
  - E-mail (parsing automático)
  - Importação de planilha Excel/CSV
  - API REST (integrações externas)
  - Indicações (cadastro manual)
  - Telefone (registro manual)

**RF-CRM-002: Qualificação Automática de Leads (IA)**
- Agente de IA deve analisar cada lead e atribuir score de 0 a 100 baseado em:
  - Segmento (condomínio = +30, empresa = +20, residência = +10)
  - Porte (número de unidades/funcionários)
  - Localização (Manaus/AM = +15, outras capitais = +10, interior = +5)
  - Budget estimado (extraído de conversas/formulários)
  - Urgência (palavras-chave: "urgente", "preciso agora" = +20)
  - Histórico de interações (engajamento)
  
**Algoritmo de Score:**
```python
def calculate_lead_score(lead: Lead) -> int:
    score = 0
    
    # Segmento
    segment_scores = {
        'condominium': 30,
        'company': 20,
        'residence': 10
    }
    score += segment_scores.get(lead.segment, 0)
    
    # Porte
    if lead.units_count:
        if lead.units_count > 100:
            score += 25
        elif lead.units_count > 50:
            score += 15
        elif lead.units_count > 20:
            score += 10
    
    # Localização
    if lead.city == 'Manaus' and lead.state == 'AM':
        score += 15
    elif lead.city in CAPITAL_CITIES:
        score += 10
    else:
        score += 5
    
    # Budget
    if lead.estimated_budget:
        if lead.estimated_budget >= 10000:
            score += 20
        elif lead.estimated_budget >= 5000:
            score += 15
        elif lead.estimated_budget >= 2000:
            score += 10
    
    # Urgência (NLP)
    urgency_keywords = ['urgente', 'preciso agora', 'imediato', 'rapidamente']
    if any(keyword in lead.message.lower() for keyword in urgency_keywords):
        score += 20
    
    # Engajamento
    interactions_score = min(lead.interactions_count * 2, 15)
    score += interactions_score
    
    return min(score, 100)
```

**RF-CRM-003: Distribuição Inteligente de Leads**
- Sistema deve distribuir leads automaticamente baseado em:
  - Score do lead (leads quentes para vendedores mais experientes)
  - Localização (vendedor responsável pela região)
  - Carga de trabalho atual (balanceamento)
  - Especialidade (vendedor especialista em condomínios, empresas, etc)
  - Performance histórica (vendedor com melhor conversão para aquele perfil)

**RF-CRM-004: Enriquecimento de Dados**
- Sistema deve enriquecer dados do lead automaticamente via:
  - API Receita Federal (CNPJ → razão social, endereço, etc)
  - Google Places API (validar endereço, telefone)
  - LinkedIn (buscar informações da empresa)
  - Web scraping (site da empresa)

**2. Gestão de Oportunidades**

**RF-CRM-005: Pipeline Visual**
- Interface Kanban com arrastar e soltar
- Fases configuráveis:
  1. Lead Novo
  2. Contato Inicial
  3. Levantamento de Necessidades
  4. Proposta Enviada
  5. Negociação
  6. Fechamento
  7. Ganho / Perdido

**RF-CRM-006: Funil de Vendas**
- Visualização gráfica da conversão por etapa
- Taxa de conversão entre etapas
- Tempo médio em cada etapa
- Identificação de gargalos (IA identifica onde leads estão travando)

**RF-CRM-007: Previsão de Fechamento (IA)**
- Modelo de ML prevê probabilidade de fechamento baseado em:
  - Etapa atual
  - Tempo na etapa
  - Histórico de interações
  - Perfil do lead
  - Histórico de propostas similares
  - Sazonalidade

```python
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class OpportunityClosePredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.is_trained = False
    
    def train(self, historical_data):
        """Treina modelo com dados históricos"""
        X = []
        y = []
        
        for opp in historical_data:
            features = self.extract_features(opp)
            X.append(features)
            y.append(1 if opp.status == 'won' else 0)
        
        self.model.fit(X, y)
        self.is_trained = True
    
    def extract_features(self, opportunity):
        """Extrai features para o modelo"""
        return [
            opportunity.lead_score,
            opportunity.days_in_pipeline,
            opportunity.interactions_count,
            opportunity.proposal_count,
            opportunity.estimated_value,
            opportunity.current_stage_number,
            opportunity.days_in_current_stage,
            int(opportunity.has_meeting_scheduled),
            int(opportunity.decision_maker_identified),
            # ... outras features
        ]
    
    def predict_probability(self, opportunity):
        """Prevê probabilidade de fechamento (0-100%)"""
        if not self.is_trained:
            return None
        
        features = self.extract_features(opportunity)
        prob = self.model.predict_proba([features])[0][1]
        return int(prob * 100)
```

**3. Propostas Comerciais**

**RF-CRM-008: Geração Automática de Propostas**
- Templates profissionais pré-configurados
- Preenchimento automático com dados do lead/oportunidade
- Cálculo automático de preços baseado em:
  - Tabela de preços (por serviço, região, porte)
  - Descontos configuráveis (por volume, promoção, etc)
  - Margem de lucro mínima
  - Custos operacionais estimados

**RF-CRM-009: Customização de Propostas**
- Editor visual (drag-and-drop)
- Seções customizáveis:
  - Capa personalizada
  - Sobre a Conecta Mais
  - Escopo de serviços
  - Composição de equipe
  - Equipamentos incluídos
  - Investimento (com e sem equipamentos)
  - Forma de pagamento
  - Prazo de validade
  - Condições gerais
  - Anexos (certificados, cases, etc)

**RF-CRM-010: Assinatura Digital**
- Integração com DocuSign / Clicksign
- Fluxo de aprovação interno (gerente → diretor → envio ao cliente)
- Rastreamento de visualização (quando cliente abriu, quanto tempo leu)
- Notificações automáticas

**RF-CRM-011: Versionamento de Propostas**
- Histórico completo de versões
- Comparação entre versões (diff visual)
- Motivo de cada alteração

**4. Comissões**

**RF-CRM-012: Cálculo de Comissões**
- Regras configuráveis por:
  - Tipo de contrato (recorrente, pontual)
  - Serviço vendido
  - Valor do contrato
  - Vendedor / equipe
- Fórmulas de cálculo:
  - Percentual fixo sobre valor
  - Percentual sobre margem
  - Escala progressiva (quanto mais vende, maior %)
  - Bônus por meta atingida
- Gatilhos de pagamento:
  - Na assinatura do contrato
  - No primeiro pagamento do cliente
  - Parcelado (% a cada recebimento)
- Integração com folha de pagamento

**RF-CRM-013: Relatório de Comissões**
- Extrato individual por vendedor
- Projeção de comissões a receber
- Histórico de comissões recebidas
- Comissões pendentes (aguardando condição)

**5. Análises e Relatórios**

**RF-CRM-014: Dashboard Comercial**
- KPIs em tempo real:
  - Leads novos (hoje, semana, mês)
  - Taxa de conversão Lead → Oportunidade
  - Taxa de conversão Oportunidade → Venda
  - Ticket médio
  - Ciclo de venda médio
  - Pipeline value (valor total em negociação)
  - Forecast (previsão de fechamento)
- Gráficos:
  - Funil de vendas
  - Evolução temporal
  - Performance por vendedor
  - Performance por serviço
  - Performance por região

**RF-CRM-015: Relatórios**
- Leads por origem
- Leads por status
- Oportunidades por fase
- Propostas enviadas vs. aceitas
- Motivos de perda (por que perdemos a venda)
- Tempo médio de resposta
- Ciclo de venda por segmento
- ROI de campanhas de marketing

#### 4.1.3 Modelo de Dados

```python
from sqlalchemy import Column, Integer, String, Decimal, DateTime, Boolean, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class LeadSource(enum.Enum):
    WEBSITE = "website"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    PHONE = "phone"
    REFERRAL = "referral"
    MARKETING = "marketing"
    OTHER = "other"

class LeadStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"

class Lead(Base):
    __tablename__ = "leads"
    
    # Identificação
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False)  # UUID para API pública
    
    # Informações Básicas
    name = Column(String(200), nullable=False, index=True)
    company_name = Column(String(200), nullable=True)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    mobile = Column(String(20), nullable=True)
    
    # Documento
    cpf = Column(String(14), nullable=True)
    cnpj = Column(String(18), nullable=True, index=True)
    
    # Endereço
    zipcode = Column(String(9), nullable=True)
    address = Column(String(255), nullable=True)
    number = Column(String(10), nullable=True)
    complement = Column(String(100), nullable=True)
    neighborhood = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    
    # Classificação
    source = Column(Enum(LeadSource), nullable=False)
    source_detail = Column(String(100), nullable=True)  # Ex: "Google Ads - Campanha X"
    segment = Column(String(50), nullable=True)  # condominium, company, residence
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    
    # Scoring e Qualificação
    score = Column(Integer, default=0)  # 0-100
    is_qualified = Column(Boolean, default=False)
    qualification_notes = Column(Text, nullable=True)
    
    # Estimativas
    units_count = Column(Integer, nullable=True)  # Número de unidades (condomínio)
    employees_count = Column(Integer, nullable=True)  # Número de funcionários (empresa)
    estimated_budget = Column(Decimal(10, 2), nullable=True)
    
    # Mensagem / Interesse
    message = Column(Text, nullable=True)
    services_interest = Column(JSON, nullable=True)  # ['security', 'facilities', 'electronics']
    
    # Responsável
    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    
    # Interações
    interactions_count = Column(Integer, default=0)
    last_interaction_at = Column(DateTime, nullable=True)
    last_interaction_type = Column(String(50), nullable=True)  # call, email, whatsapp, meeting
    
    # Conversão
    converted_to_opportunity_at = Column(DateTime, nullable=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=True)
    
    # Enriquecimento
    enriched = Column(Boolean, default=False)
    enriched_at = Column(DateTime, nullable=True)
    enrichment_data = Column(JSON, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamentos
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    opportunity = relationship("Opportunity", back_populates="lead")
    interactions = relationship("LeadInteraction", back_populates="lead")

class OpportunityStage(enum.Enum):
    NEW_LEAD = "new_lead"
    FIRST_CONTACT = "first_contact"
    NEEDS_ASSESSMENT = "needs_assessment"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    WON = "won"
    LOST = "lost"

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False)
    
    # Relação com Lead
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # Informações Básicas
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pipeline
    stage = Column(Enum(OpportunityStage), default=OpportunityStage.NEW_LEAD)
    stage_changed_at = Column(DateTime, default=datetime.utcnow)
    days_in_current_stage = Column(Integer, default=0)
    days_in_pipeline = Column(Integer, default=0)
    
    # Valores
    estimated_value = Column(Decimal(10, 2), nullable=False)
    discount_percent = Column(Decimal(5, 2), default=0)
    final_value = Column(Decimal(10, 2), nullable=False)
    
    # Probabilidade
    close_probability = Column(Integer, default=0)  # 0-100, calculado por IA
    
    # Datas
    expected_close_date = Column(DateTime, nullable=True)
    actual_close_date = Column(DateTime, nullable=True)
    
    # Responsável
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Propostas
    proposal_count = Column(Integer, default=0)
    last_proposal_sent_at = Column(DateTime, nullable=True)
    
    # Decisores
    decision_maker_identified = Column(Boolean, default=False)
    decision_maker_name = Column(String(200), nullable=True)
    decision_maker_role = Column(String(100), nullable=True)
    
    # Competição
    has_competitors = Column(Boolean, default=False)
    competitors = Column(JSON, nullable=True)
    
    # Motivo de Perda (se perdeu)
    loss_reason = Column(String(100), nullable=True)
    loss_details = Column(Text, nullable=True)
    lost_to_competitor = Column(String(100), nullable=True)
    
    # Conversão em Contrato
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamentos
    lead = relationship("Lead", back_populates="opportunity")
    owner = relationship("User", foreign_keys=[owner_id])
    proposals = relationship("Proposal", back_populates="opportunity")
    interactions = relationship("OpportunityInteraction", back_populates="opportunity")
    contract = relationship("Contract", back_populates="opportunity")

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False)
    proposal_number = Column(String(20), unique=True, nullable=False)  # PROP-2024-0001
    
    # Relação
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # Versão
    version = Column(Integer, default=1)
    parent_proposal_id = Column(Integer, ForeignKey('proposals.id'), nullable=True)
    is_current_version = Column(Boolean, default=True)
    
    # Conteúdo
    title = Column(String(200), nullable=False)
    template_id = Column(Integer, ForeignKey('proposal_templates.id'), nullable=True)
    content_json = Column(JSON, nullable=False)  # Estrutura da proposta
    
    # Valores
    items = Column(JSON, nullable=False)  # Lista de itens/serviços
    subtotal = Column(Decimal(10, 2), nullable=False)
    discount_percent = Column(Decimal(5, 2), default=0)
    discount_value = Column(Decimal(10, 2), default=0)
    total_value = Column(Decimal(10, 2), nullable=False)
    
    # Condições
    payment_terms = Column(Text, nullable=True)
    validity_days = Column(Integer, default=30)
    valid_until = Column(DateTime, nullable=False)
    
    # Status
    status = Column(String(20), default='draft')  # draft, sent, viewed, accepted, rejected, expired
    
    # Envio
    sent_at = Column(DateTime, nullable=True)
    sent_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    sent_to_email = Column(String(150), nullable=True)
    
    # Visualização (tracking)
    viewed_at = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, default=0)
    
    # Decisão
    decided_at = Column(DateTime, nullable=True)
    decision = Column(String(20), nullable=True)  # accepted, rejected
    rejection_reason = Column(Text, nullable=True)
    
    # Assinatura Digital
    signature_requested = Column(Boolean, default=False)
    signature_provider = Column(String(50), nullable=True)  # docusign, clicksign
    signature_document_id = Column(String(100), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    signed_by = Column(String(200), nullable=True)
    
    # Documentos
    pdf_file_path = Column(String(255), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relacionamentos
    opportunity = relationship("Opportunity", back_populates="proposals")
    parent_proposal = relationship("Proposal", remote_side=[id])

class Commission(Base):
    __tablename__ = "commissions"
    
    id = Column(Integer, primary_key=True)
    
    # Relações
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=True)
    salesperson_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Valores
    contract_value = Column(Decimal(10, 2), nullable=False)
    commission_percent = Column(Decimal(5, 2), nullable=False)
    commission_amount = Column(Decimal(10, 2), nullable=False)
    
    # Regra aplicada
    rule_id = Column(Integer, ForeignKey('commission_rules.id'), nullable=True)
    rule_description = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(20), default='pending')  # pending, approved, paid
    
    # Pagamento
    payment_trigger = Column(String(50), nullable=False)  # contract_signed, first_payment, monthly
    payment_due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    opportunity = relationship("Opportunity")
    contract = relationship("Contract")
    salesperson = relationship("User")
```

#### 4.1.4 APIs / Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import date

router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])

# ========== LEADS ==========

class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    mobile: Optional[str]
    company_name: Optional[str]
    cnpj: Optional[str]
    source: LeadSource
    source_detail: Optional[str]
    segment: Optional[str]
    message: Optional[str]
    services_interest: Optional[List[str]]
    
    @validator('phone', 'mobile')
    def validate_phone(cls, v):
        # Validar formato de telefone
        import re
        if v and not re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', v):
            raise ValueError('Invalid phone format')
        return v

class LeadResponse(BaseModel):
    id: int
    uuid: str
    name: str
    email: str
    phone: str
    company_name: Optional[str]
    score: int
    status: LeadStatus
    assigned_to: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True

class LeadUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    status: Optional[LeadStatus]
    assigned_to: Optional[int]
    # ... outros campos

@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead: LeadCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo lead
    
    - **name**: Nome do contato
    - **email**: E-mail do contato
    - **phone**: Telefone
    - **source**: Origem do lead (website, whatsapp, etc)
    """
    # Validar duplicidade por e-mail
    existing = await db.query(Lead).filter(Lead.email == lead.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lead with this email already exists"
        )
    
    # Criar lead
    new_lead = Lead(**lead.dict(), created_by=current_user.id)
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    
    # Enriquecer dados (async task)
    await enrich_lead_task.delay(new_lead.id)
    
    # Calcular score (async)
    await calculate_lead_score_task.delay(new_lead.id)
    
    # Distribuir automaticamente (se configurado)
    if AUTO_ASSIGN_LEADS:
        await assign_lead_automatically(new_lead.id)
    
    # Publicar evento
    await event_bus.publish("LeadCreated", {
        "lead_id": new_lead.id,
        "source": lead.source,
        "created_by": current_user.id
    })
    
    return new_lead

@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    assigned_to: Optional[int] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Lista leads com filtros
    """
    query = db.query(Lead)
    
    # Filtros
    if status:
        query = query.filter(Lead.status == status)
    if source:
        query = query.filter(Lead.source == source)
    if assigned_to:
        query = query.filter(Lead.assigned_to == assigned_to)
    if min_score:
        query = query.filter(Lead.score >= min_score)
    if search:
        query = query.filter(
            (Lead.name.ilike(f"%{search}%")) |
            (Lead.company_name.ilike(f"%{search}%")) |
            (Lead.email.ilike(f"%{search}%"))
        )
    
    # Ordenação
    query = query.order_by(Lead.score.desc(), Lead.created_at.desc())
    
    # Paginação
    leads = await query.offset(skip).limit(limit).all()
    
    return leads

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user)
):
    """Busca lead por ID"""
    lead = await db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    updates: LeadUpdate,
    current_user: User = Depends(get_current_user)
):
    """Atualiza lead"""
    lead = await db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Armazenar valores antigos para auditoria
    old_values = lead.dict()
    
    # Aplicar updates
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    
    await db.commit()
    await db.refresh(lead)
    
    # Auditoria
    await AuditService.log_action(
        user_id=current_user.id,
        action="UPDATE",
        resource_type="Lead",
        resource_id=str(lead_id),
        old_value=old_values,
        new_value=lead.dict()
    )
    
    return lead

@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_opportunity(
    lead_id: int,
    opportunity_data: OpportunityCreate,
    current_user: User = Depends(get_current_user)
):
    """Converte lead em oportunidade"""
    lead = await db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead.status == LeadStatus.CONVERTED:
        raise HTTPException(status_code=400, detail="Lead already converted")
    
    # Criar oportunidade
    opportunity = Opportunity(
        lead_id=lead_id,
        title=opportunity_data.title,
        description=opportunity_data.description,
        estimated_value=opportunity_data.estimated_value,
        owner_id=current_user.id,
        created_by=current_user.id
    )
    db.add(opportunity)
    
    # Atualizar lead
    lead.status = LeadStatus.CONVERTED
    lead.converted_to_opportunity_at = datetime.utcnow()
    lead.opportunity_id = opportunity.id
    
    await db.commit()
    await db.refresh(opportunity)
    
    # Evento
    await event_bus.publish("LeadConverted", {
        "lead_id": lead_id,
        "opportunity_id": opportunity.id,
        "converted_by": current_user.id
    })
    
    return opportunity

@router.post("/leads/{lead_id}/enrich")
async def enrich_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user)
):
    """Enriquece dados do lead via APIs externas"""
    lead = await db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    enriched_data = {}
    
    # Se tem CNPJ, buscar na Receita Federal
    if lead.cnpj:
        rf_data = await receita_federal_api.get_company_data(lead.cnpj)
        if rf_data:
            enriched_data['receita_federal'] = rf_data
            lead.company_name = lead.company_name or rf_data.get('razao_social')
            # Preencher endereço se vazio
            if not lead.address:
                lead.zipcode = rf_data.get('cep')
                lead.address = rf_data.get('logradouro')
                lead.number = rf_data.get('numero')
                lead.neighborhood = rf_data.get('bairro')
                lead.city = rf_data.get('municipio')
                lead.state = rf_data.get('uf')
    
    # Validar endereço via Google Places
    if lead.address:
        places_data = await google_places_api.validate_address(
            f"{lead.address}, {lead.number}, {lead.city}, {lead.state}"
        )
        if places_data:
            enriched_data['google_places'] = places_data
    
    # Salvar dados enriquecidos
    lead.enriched = True
    lead.enriched_at = datetime.utcnow()
    lead.enrichment_data = enriched_data
    
    await db.commit()
    
    return {"message": "Lead enriched successfully", "data": enriched_data}

# ========== OPPORTUNITIES ==========

class OpportunityCreate(BaseModel):
    title: str
    description: Optional[str]
    estimated_value: Decimal
    expected_close_date: Optional[date]

class OpportunityResponse(BaseModel):
    id: int
    uuid: str
    title: str
    stage: OpportunityStage
    estimated_value: Decimal
    close_probability: int
    days_in_pipeline: int
    owner_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

@router.post("/opportunities", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    opportunity: OpportunityCreate,
    current_user: User = Depends(get_current_user)
):
    """Cria nova oportunidade"""
    new_opp = Opportunity(
        **opportunity.dict(),
        owner_id=current_user.id,
        created_by=current_user.id,
        final_value=opportunity.estimated_value  # Inicialmente sem desconto
    )
    db.add(new_opp)
    await db.commit()
    await db.refresh(new_opp)
    
    # Calcular probabilidade de fechamento (IA)
    await calculate_close_probability_task.delay(new_opp.id)
    
    return new_opp

@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    stage: Optional[OpportunityStage] = None,
    owner_id: Optional[int] = None,
    min_value: Optional[Decimal] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Lista oportunidades"""
    query = db.query(Opportunity)
    
    if stage:
        query = query.filter(Opportunity.stage == stage)
    if owner_id:
        query = query.filter(Opportunity.owner_id == owner_id)
    if min_value:
        query = query.filter(Opportunity.estimated_value >= min_value)
    
    query = query.order_by(Opportunity.close_probability.desc(), Opportunity.created_at.desc())
    
    opportunities = await query.offset(skip).limit(limit).all()
    return opportunities

@router.patch("/opportunities/{opp_id}/stage")
async def change_opportunity_stage(
    opp_id: int,
    new_stage: OpportunityStage,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Move oportunidade para outra etapa do pipeline"""
    opp = await db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    old_stage = opp.stage
    opp.stage = new_stage
    opp.stage_changed_at = datetime.utcnow()
    opp.days_in_current_stage = 0
    
    # Recalcular probabilidade
    opp.close_probability = await predictor.predict_probability(opp)
    
    await db.commit()
    
    # Registrar mudança
    stage_history = OpportunityStageHistory(
        opportunity_id=opp_id,
        from_stage=old_stage,
        to_stage=new_stage,
        changed_by=current_user.id,
        notes=notes
    )
    db.add(stage_history)
    await db.commit()
    
    # Se ganhou ou perdeu, registrar
    if new_stage == OpportunityStage.WON:
        await handle_opportunity_won(opp)
    elif new_stage == OpportunityStage.LOST:
        await handle_opportunity_lost(opp)
    
    return {"message": "Stage changed successfully"}

# ========== PROPOSALS ==========

@router.post("/opportunities/{opp_id}/proposals", status_code=201)
async def create_proposal(
    opp_id: int,
    proposal_data: ProposalCreate,
    current_user: User = Depends(get_current_user)
):
    """Cria proposta para oportunidade"""
    opp = await db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Gerar número da proposta
    year = datetime.now().year
    count = await db.query(Proposal).filter(
        Proposal.proposal_number.like(f"PROP-{year}-%")
    ).count()
    proposal_number = f"PROP-{year}-{count+1:04d}"
    
    # Criar proposta
    proposal = Proposal(
        opportunity_id=opp_id,
        proposal_number=proposal_number,
        title=proposal_data.title,
        content_json=proposal_data.content,
        items=proposal_data.items,
        subtotal=proposal_data.subtotal,
        discount_percent=proposal_data.discount_percent,
        discount_value=proposal_data.discount_value,
        total_value=proposal_data.total_value,
        payment_terms=proposal_data.payment_terms,
        validity_days=proposal_data.validity_days,
        valid_until=datetime.now() + timedelta(days=proposal_data.validity_days),
        created_by=current_user.id
    )
    db.add(proposal)
    
    # Atualizar oportunidade
    opp.proposal_count += 1
    
    await db.commit()
    await db.refresh(proposal)
    
    # Gerar PDF (async task)
    await generate_proposal_pdf_task.delay(proposal.id)
    
    return proposal

@router.post("/proposals/{proposal_id}/send")
async def send_proposal(
    proposal_id: int,
    recipient_email: EmailStr,
    message: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Envia proposta por e-mail"""
    proposal = await db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.status != 'draft':
        raise HTTPException(status_code=400, detail="Proposal already sent")
    
    # Atualizar status
    proposal.status = 'sent'
    proposal.sent_at = datetime.utcnow()
    proposal.sent_by = current_user.id
    proposal.sent_to_email = recipient_email
    
    await db.commit()
    
    # Enviar e-mail (async)
    await send_proposal_email_task.delay(
        proposal_id=proposal_id,
        recipient=recipient_email,
        message=message
    )
    
    # Atualizar oportunidade
    opp = await db.query(Opportunity).filter(Opportunity.id == proposal.opportunity_id).first()
    opp.last_proposal_sent_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Proposal sent successfully"}

# ========== ANALYTICS ==========

@router.get("/analytics/funnel")
async def get_sales_funnel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    """Retorna dados do funil de vendas"""
    
    query = db.query(Opportunity)
    
    if start_date:
        query = query.filter(Opportunity.created_at >= start_date)
    if end_date:
        query = query.filter(Opportunity.created_at <= end_date)
    
    # Contar por estágio
    stages_count = {}
    for stage in OpportunityStage:
        count = await query.filter(Opportunity.stage == stage).count()
        stages_count[stage.value] = count
    
    # Calcular conversão
    total = stages_count[OpportunityStage.NEW_LEAD.value]
    won = stages_count[OpportunityStage.WON.value]
    conversion_rate = (won / total * 100) if total > 0 else 0
    
    return {
        "stages": stages_count,
        "total": total,
        "won": won,
        "lost": stages_count[OpportunityStage.LOST.value],
        "conversion_rate": conversion_rate
    }

@router.get("/analytics/performance")
async def get_sales_performance(
    salesperson_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    """Retorna performance de vendas"""
    
    query = db.query(Opportunity)
    
    if salesperson_id:
        query = query.filter(Opportunity.owner_id == salesperson_id)
    if start_date:
        query = query.filter(Opportunity.created_at >= start_date)
    if end_date:
        query = query.filter(Opportunity.created_at <= end_date)
    
    # Métricas
    total_opportunities = await query.count()
    won_opportunities = await query.filter(Opportunity.stage == OpportunityStage.WON).count()
    lost_opportunities = await query.filter(Opportunity.stage == OpportunityStage.LOST).count()
    
    # Valor total ganho
    won_query = query.filter(Opportunity.stage == OpportunityStage.WON)
    total_won_value = await db.query(func.sum(Opportunity.final_value)).select_from(won_query).scalar() or 0
    
    # Ticket médio
    avg_ticket = total_won_value / won_opportunities if won_opportunities > 0 else 0
    
    # Taxa de conversão
    conversion_rate = (won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
    
    # Ciclo de venda médio (dias)
    avg_cycle = await db.query(func.avg(Opportunity.days_in_pipeline)).select_from(won_query).scalar() or 0
    
    return {
        "total_opportunities": total_opportunities,
        "won": won_opportunities,
        "lost": lost_opportunities,
        "in_progress": total_opportunities - won_opportunities - lost_opportunities,
        "total_won_value": float(total_won_value),
        "avg_ticket": float(avg_ticket),
        "conversion_rate": float(conversion_rate),
        "avg_sales_cycle_days": int(avg_cycle)
    }
```

Este é apenas o **MÓDULO 1 (CRM)** com detalhamento completo! 

Vou continuar criando os outros 37 módulos no mesmo nível de detalhe...

