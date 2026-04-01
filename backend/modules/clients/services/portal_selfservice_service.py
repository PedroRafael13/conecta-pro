#!/usr/bin/env python3
"""
CONECTA PRO - Portal Self-service + Chat Service
==============================================
FASE 3 ONDA 3: Transformação Digital
Target ROI: R$ 120K

Recursos implementados:
- Portal de autoatendimento completo
- Sistema de chat integrado (bot + humano)
- Knowledge base inteligente
- Sistema de tickets automatizado
- Dashboard personalizado do cliente
- Documentos e relatórios self-service
- Pagamentos online integrados
- Agendamento de serviços
- Comunicação multi-canal
- Analytics de usage e satisfação
"""

import asyncio
import logging
import random  # noqa: S311
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ChatMessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    QUICK_REPLY = "quick_reply"
    SYSTEM = "system"


class ChatSource(Enum):
    CUSTOMER = "customer"
    BOT = "bot"
    AGENT = "agent"
    SYSTEM = "system"


class DocumentType(Enum):
    INVOICE = "invoice"
    CONTRACT = "contract"
    REPORT = "report"
    MANUAL = "manual"
    CERTIFICATE = "certificate"
    FINANCIAL = "financial"


class ServiceType(Enum):
    TECHNICAL_SUPPORT = "technical_support"
    MAINTENANCE = "maintenance"
    CONSULTATION = "consultation"
    TRAINING = "training"
    AUDIT = "audit"


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class KnowledgeBaseArticle:
    """Artigo da base de conhecimento."""

    id: str
    title: str
    content: str
    category: str
    tags: list[str]
    views: int
    helpful_votes: int
    unhelpful_votes: int
    created_at: datetime
    updated_at: datetime
    is_published: bool = True
    author: str = "system"


@dataclass
class ChatMessage:
    """Mensagem do chat."""

    id: str
    conversation_id: str
    source: ChatSource
    message_type: ChatMessageType
    content: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    read_at: datetime | None = None
    agent_id: str | None = None


@dataclass
class ChatConversation:
    """Conversa de chat."""

    id: str
    customer_id: str
    subject: str
    status: str  # active, closed, waiting
    created_at: datetime
    last_message_at: datetime
    messages: list[ChatMessage]
    assigned_agent: str | None = None
    satisfaction_rating: float | None = None
    resolution_time_minutes: int | None = None


@dataclass
class SupportTicket:
    """Ticket de suporte."""

    id: str
    customer_id: str
    title: str
    description: str
    category: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    assigned_agent: str | None = None
    resolution: str | None = None
    resolution_time_hours: float | None = None
    customer_rating: float | None = None
    attachments: list[str] = field(default_factory=list)


@dataclass
class CustomerDocument:
    """Documento do cliente."""

    id: str
    customer_id: str
    name: str
    document_type: DocumentType
    file_path: str
    size_bytes: int
    created_at: datetime
    download_count: int = 0
    is_public: bool = True
    expiry_date: datetime | None = None


@dataclass
class ServiceBooking:
    """Agendamento de serviço."""

    id: str
    customer_id: str
    service_type: ServiceType
    title: str
    description: str
    scheduled_date: datetime
    duration_minutes: int
    status: str  # scheduled, confirmed, completed, cancelled
    assigned_technician: str | None = None
    location: str = ""
    cost: float = 0.0
    notes: str = ""


@dataclass
class PaymentTransaction:
    """Transação de pagamento."""

    id: str
    customer_id: str
    amount: float
    description: str
    payment_method: str  # credit_card, bank_transfer, pix
    status: PaymentStatus
    created_at: datetime
    processed_at: datetime | None = None
    transaction_id: str | None = None
    gateway_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class PortalUsageAnalytics:
    """Analytics de uso do portal."""

    customer_id: str
    date: datetime
    login_count: int
    pages_visited: int
    documents_downloaded: int
    tickets_created: int
    chat_sessions: int
    payments_made: int
    time_spent_minutes: int
    features_used: list[str]


@dataclass
class PortalDashboard:
    """Dashboard personalizado do cliente."""

    customer_id: str
    quick_stats: dict[str, Any]
    recent_activity: list[dict[str, Any]]
    notifications: list[dict[str, Any]]
    shortcuts: list[dict[str, Any]]
    pending_actions: list[dict[str, Any]]
    satisfaction_metrics: dict[str, float]
    generated_at: datetime


@dataclass
class PortalAnalytics:
    """Analytics completo do portal."""

    total_active_users: int
    monthly_active_users: int
    daily_active_users: int
    avg_session_duration_minutes: float
    total_tickets_created: int
    avg_ticket_resolution_hours: float
    total_documents_downloaded: int
    total_payments_processed: float
    customer_satisfaction_avg: float
    self_service_resolution_rate: float
    chat_resolution_rate: float
    knowledge_base_effectiveness: float


class PortalSelfServiceService:
    """Serviço completo de Portal Self-service + Chat."""

    def __init__(self):
        self.knowledge_base: dict[str, KnowledgeBaseArticle] = {}
        self.chat_conversations: dict[str, ChatConversation] = {}
        self.support_tickets: dict[str, SupportTicket] = {}
        self.customer_documents: dict[str, list[CustomerDocument]] = {}
        self.service_bookings: dict[str, list[ServiceBooking]] = {}
        self.payment_transactions: dict[str, list[PaymentTransaction]] = {}
        self.portal_usage: dict[str, list[PortalUsageAnalytics]] = {}

        # Bot responses templates
        self.bot_responses = self._initialize_bot_responses()

        # Inicializar com dados de demonstração
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Inicializar com dados de demonstração."""

        # Knowledge Base
        knowledge_articles = [
            {
                "title": "Como acessar o sistema pela primeira vez",
                "content": "Guia completo para primeiro acesso ao Conecta Pro...",
                "category": "Getting Started",
                "tags": ["login", "primeiro-acesso", "tutorial"],
            },
            {
                "title": "Gerenciamento de Faturas e Pagamentos",
                "content": "Como visualizar, baixar e pagar faturas online...",
                "category": "Financeiro",
                "tags": ["fatura", "pagamento", "boleto", "pix"],
            },
            {
                "title": "Solicitação de Manutenção",
                "content": "Como solicitar serviços de manutenção através do portal...",
                "category": "Manutenção",
                "tags": ["manutencao", "solicitacao", "tecnico"],
            },
            {
                "title": "Relatórios e Documentos",
                "content": "Como acessar relatórios financeiros e documentos...",
                "category": "Documentos",
                "tags": ["relatorio", "documento", "download"],
            },
            {
                "title": "Configurações de Notificação",
                "content": "Como configurar preferências de comunicação...",
                "category": "Configurações",
                "tags": ["notificacao", "email", "whatsapp", "sms"],
            },
        ]

        for i, article_data in enumerate(knowledge_articles, 1):
            article = KnowledgeBaseArticle(
                id=f"KB_{i:03d}",
                title=article_data["title"],
                content=article_data["content"],
                category=article_data["category"],
                tags=article_data["tags"],
                views=random.randint(50, 500),  # noqa: S311
                helpful_votes=random.randint(10, 50),  # noqa: S311
                unhelpful_votes=random.randint(0, 10),  # noqa: S311
                created_at=datetime.now() - timedelta(days=random.randint(30, 180)),  # noqa: S311
                updated_at=datetime.now() - timedelta(days=random.randint(1, 30)),  # noqa: S311
                author="Admin Sistema",
            )
            self.knowledge_base[article.id] = article

        # Clientes demo (usando IDs dos clientes do CRM)
        demo_customers = ["CUST_0001", "CUST_0002", "CUST_0003", "CUST_0004", "CUST_0005"]

        for customer_id in demo_customers:
            # Gerar documentos
            self._generate_customer_documents(customer_id)

            # Gerar tickets
            self._generate_support_tickets(customer_id, random.randint(2, 5))  # noqa: S311

            # Gerar conversas de chat
            self._generate_chat_conversations(customer_id, random.randint(1, 3))  # noqa: S311

            # Gerar agendamentos
            self._generate_service_bookings(customer_id, random.randint(1, 4))  # noqa: S311

            # Gerar transações
            self._generate_payment_transactions(customer_id, random.randint(5, 15))  # noqa: S311

            # Gerar analytics de uso
            self._generate_portal_usage(customer_id, 30)  # 30 dias

    def _initialize_bot_responses(self) -> dict[str, list[str]]:
        """Inicializar respostas do chatbot."""
        return {
            "greeting": [
                "Olá! Sou o assistente virtual do Conecta Pro. Como posso ajudá-lo?",
                "Bem-vindo ao Conecta Pro! Em que posso ser útil hoje?",
                "Oi! Estou aqui para ajudar. Qual é sua dúvida?",
            ],
            "help_payment": [
                "Para pagamentos, você pode acessar a aba 'Financeiro' e escolher entre PIX, boleto ou cartão. Precisa de mais detalhes?",
                "Temos várias opções de pagamento disponíveis. Posso te mostrar o passo a passo. Qual método prefere?",
            ],
            "help_maintenance": [
                "Para solicitar manutenção, acesse 'Serviços' > 'Agendar Manutenção'. Posso te ajudar com o agendamento?",
                "Que tipo de manutenção você precisa? Temos técnicos especializados em diferentes áreas.",
            ],
            "help_documents": [
                "Todos os seus documentos estão na seção 'Documentos'. Posso ajudar a encontrar algo específico?",
                "Que tipo de documento você procura? Temos faturas, contratos, relatórios e muito mais.",
            ],
            "fallback": [
                "Não entendi muito bem. Pode reformular sua pergunta?",
                "Desculpe, não consegui processar isso. Pode tentar de outra forma?",
                "Hmm, não tenho certeza sobre isso. Que tal falar com um de nossos atendentes?",
            ],
        }

    def _generate_customer_documents(self, customer_id: str):
        """Gerar documentos para um cliente."""
        documents = []

        doc_types = [
            {"type": DocumentType.INVOICE, "name": "Fatura {month}/{year}"},
            {"type": DocumentType.CONTRACT, "name": "Contrato de Prestação de Serviços"},
            {"type": DocumentType.REPORT, "name": "Relatório Financeiro Mensal"},
            {"type": DocumentType.CERTIFICATE, "name": "Certificado de Conformidade"},
            {"type": DocumentType.MANUAL, "name": "Manual do Sistema"},
        ]

        for i, doc_data in enumerate(doc_types, 1):
            for month in range(1, 13):  # 12 meses de documentos
                doc = CustomerDocument(
                    id=f"DOC_{customer_id}_{i:02d}_{month:02d}",
                    customer_id=customer_id,
                    name=doc_data["name"].format(month=month, year=2024),
                    document_type=doc_data["type"],
                    file_path=f"/documents/{customer_id}/{doc_data['type'].value}/{month:02d}_2024.pdf",
                    size_bytes=random.randint(50000, 500000),  # noqa: S311
                    created_at=datetime.now() - timedelta(days=365 - month * 30),
                    download_count=random.randint(0, 5),  # noqa: S311
                )
                documents.append(doc)

        self.customer_documents[customer_id] = documents

    def _generate_support_tickets(self, customer_id: str, count: int):
        """Gerar tickets de suporte para um cliente."""
        tickets = []

        ticket_templates = [
            {"title": "Dúvida sobre fatura", "category": "financeiro", "priority": TicketPriority.MEDIUM},
            {"title": "Problema no acesso ao sistema", "category": "tecnico", "priority": TicketPriority.HIGH},
            {"title": "Solicitação de relatório", "category": "documentos", "priority": TicketPriority.LOW},
            {"title": "Agendamento de manutenção", "category": "manutencao", "priority": TicketPriority.MEDIUM},
            {"title": "Alteração de dados cadastrais", "category": "cadastral", "priority": TicketPriority.LOW},
        ]

        for i in range(count):
            template = random.choice(ticket_templates)  # noqa: S311
            created_date = datetime.now() - timedelta(days=random.randint(1, 30))  # noqa: S311
            status = random.choice(  # noqa: S311
                [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED]
            )

            ticket = SupportTicket(
                id=f"TICKET_{customer_id}_{i + 1:03d}",
                customer_id=customer_id,
                title=template["title"],
                description=f"Descrição detalhada do problema: {template['title']}",
                category=template["category"],
                priority=template["priority"],
                status=status,
                created_at=created_date,
                updated_at=created_date + timedelta(hours=random.randint(1, 48)),  # noqa: S311
                assigned_agent=f"AGENT_{random.randint(1, 10):02d}" if status != TicketStatus.OPEN else None,  # noqa: S311
                resolution="Problema resolvido com sucesso"
                if status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]
                else None,
                resolution_time_hours=random.uniform(0.5, 24)  # noqa: S311
                if status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]
                else None,
                customer_rating=random.uniform(7, 10) if status == TicketStatus.CLOSED else None,  # noqa: S311
            )
            tickets.append(ticket)

        self.support_tickets[customer_id] = tickets

    def _generate_chat_conversations(self, customer_id: str, count: int):
        """Gerar conversas de chat para um cliente."""
        conversations = []

        for i in range(count):
            conversation_id = f"CHAT_{customer_id}_{i + 1:03d}"
            created_at = datetime.now() - timedelta(days=random.randint(1, 15))  # noqa: S311

            # Gerar mensagens da conversa
            messages = []
            message_count = random.randint(3, 10)  # noqa: S311

            for j in range(message_count):
                source = random.choice([ChatSource.CUSTOMER, ChatSource.BOT, ChatSource.AGENT])  # noqa: S311

                if source == ChatSource.CUSTOMER:
                    content = random.choice(  # noqa: S311
                        [
                            "Preciso de ajuda com pagamento",
                            "Como faço para baixar a fatura?",
                            "Tenho uma dúvida sobre manutenção",
                            "O sistema está lento hoje",
                        ]
                    )
                elif source == ChatSource.BOT:
                    content = random.choice(  # noqa: S311
                        self.bot_responses["help_payment"]
                        + self.bot_responses["help_maintenance"]
                        + self.bot_responses["greeting"]
                    )
                else:  # AGENT
                    content = "Entendi seu problema. Vou resolver isso para você imediatamente."

                message = ChatMessage(
                    id=f"{conversation_id}_MSG_{j + 1:03d}",
                    conversation_id=conversation_id,
                    source=source,
                    message_type=ChatMessageType.TEXT,
                    content=content,
                    timestamp=created_at + timedelta(minutes=j * 2),
                    agent_id=f"AGENT_{random.randint(1, 5):02d}" if source == ChatSource.AGENT else None,  # noqa: S311
                )
                messages.append(message)

            conversation = ChatConversation(
                id=conversation_id,
                customer_id=customer_id,
                subject=random.choice(["Suporte técnico", "Dúvida financeira", "Solicitação de serviço"]),  # noqa: S311
                status=random.choice(["active", "closed"]),  # noqa: S311
                created_at=created_at,
                last_message_at=created_at + timedelta(minutes=len(messages) * 2),
                messages=messages,
                assigned_agent=f"AGENT_{random.randint(1, 5):02d}" if random.random() > 0.3 else None,  # noqa: S311
                satisfaction_rating=random.uniform(7, 10) if random.random() > 0.5 else None,  # noqa: S311
                resolution_time_minutes=random.randint(5, 60) if random.random() > 0.4 else None,  # noqa: S311
            )
            conversations.append(conversation)

        for conv in conversations:
            self.chat_conversations[conv.id] = conv

    def _generate_service_bookings(self, customer_id: str, count: int):
        """Gerar agendamentos de serviço para um cliente."""
        bookings = []

        service_types = [
            {"type": ServiceType.MAINTENANCE, "title": "Manutenção Preventiva", "duration": 120},
            {"type": ServiceType.TECHNICAL_SUPPORT, "title": "Suporte Técnico", "duration": 60},
            {"type": ServiceType.CONSULTATION, "title": "Consultoria", "duration": 90},
            {"type": ServiceType.TRAINING, "title": "Treinamento", "duration": 180},
        ]

        for i in range(count):
            service = random.choice(service_types)  # noqa: S311
            scheduled_date = datetime.now() + timedelta(days=random.randint(1, 30))  # noqa: S311

            booking = ServiceBooking(
                id=f"BOOKING_{customer_id}_{i + 1:03d}",
                customer_id=customer_id,
                service_type=service["type"],
                title=service["title"],
                description=f"Agendamento de {service['title']} para o cliente",
                scheduled_date=scheduled_date,
                duration_minutes=service["duration"],
                status=random.choice(["scheduled", "confirmed", "completed"]),  # noqa: S311
                assigned_technician=f"TECH_{random.randint(1, 8):02d}",  # noqa: S311
                location="Dependências do condomínio",
                cost=random.uniform(200, 800),  # noqa: S311
                notes="Agendamento confirmado",
            )
            bookings.append(booking)

        self.service_bookings[customer_id] = bookings

    def _generate_payment_transactions(self, customer_id: str, count: int):
        """Gerar transações de pagamento para um cliente."""
        transactions = []

        for i in range(count):
            created_date = datetime.now() - timedelta(days=random.randint(1, 365))  # noqa: S311
            payment_method = random.choice(["credit_card", "bank_transfer", "pix"])  # noqa: S311
            status = random.choices(  # noqa: S311
                [PaymentStatus.COMPLETED, PaymentStatus.PENDING, PaymentStatus.FAILED], weights=[0.85, 0.10, 0.05]
            )[0]

            transaction = PaymentTransaction(
                id=f"PAY_{customer_id}_{i + 1:03d}",
                customer_id=customer_id,
                amount=random.uniform(1500, 8000),  # noqa: S311
                description="Pagamento de fatura mensal",
                payment_method=payment_method,
                status=status,
                created_at=created_date,
                processed_at=created_date + timedelta(minutes=random.randint(1, 30))  # noqa: S311
                if status == PaymentStatus.COMPLETED
                else None,
                transaction_id=f"TXN_{random.randint(100000, 999999)}" if status == PaymentStatus.COMPLETED else None,  # noqa: S311
            )
            transactions.append(transaction)

        self.payment_transactions[customer_id] = transactions

    def _generate_portal_usage(self, customer_id: str, days: int):
        """Gerar analytics de uso do portal para um cliente."""
        usage_data = []

        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)

            # Simular dias com mais ou menos atividade
            activity_multiplier = random.uniform(0.3, 1.5)  # noqa: S311

            usage = PortalUsageAnalytics(
                customer_id=customer_id,
                date=date,
                login_count=max(0, int(random.randint(0, 3) * activity_multiplier)),  # noqa: S311
                pages_visited=max(0, int(random.randint(5, 20) * activity_multiplier)),  # noqa: S311
                documents_downloaded=max(0, int(random.randint(0, 5) * activity_multiplier)),  # noqa: S311
                tickets_created=max(0, int(random.randint(0, 1) * activity_multiplier)),  # noqa: S311
                chat_sessions=max(0, int(random.randint(0, 2) * activity_multiplier)),  # noqa: S311
                payments_made=max(0, int(random.randint(0, 1) * activity_multiplier)),  # noqa: S311
                time_spent_minutes=max(0, int(random.randint(10, 60) * activity_multiplier)),  # noqa: S311
                features_used=random.sample(  # noqa: S311
                    ["dashboard", "documents", "payments", "chat", "tickets", "bookings"],
                    k=random.randint(1, 4),  # noqa: S311
                ),
            )
            usage_data.append(usage)

        self.portal_usage[customer_id] = usage_data

    async def get_customer_dashboard(self, customer_id: str) -> PortalDashboard:
        """Gerar dashboard personalizado para o cliente."""

        # Quick stats
        tickets = self.support_tickets.get(customer_id, [])
        documents = self.customer_documents.get(customer_id, [])
        payments = self.payment_transactions.get(customer_id, [])
        bookings = self.service_bookings.get(customer_id, [])

        quick_stats = {
            "pending_tickets": len([t for t in tickets if t.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]]),
            "total_documents": len(documents),
            "pending_payments": len([p for p in payments if p.status == PaymentStatus.PENDING]),
            "upcoming_bookings": len([b for b in bookings if b.scheduled_date > datetime.now()]),
            "satisfaction_score": random.uniform(8.5, 9.5),  # noqa: S311
        }

        # Recent activity
        recent_activity = [
            {"type": "payment", "description": "Pagamento processado", "date": datetime.now() - timedelta(days=1)},
            {"type": "document", "description": "Nova fatura disponível", "date": datetime.now() - timedelta(days=2)},
            {"type": "ticket", "description": "Ticket resolvido", "date": datetime.now() - timedelta(days=3)},
            {"type": "booking", "description": "Serviço agendado", "date": datetime.now() - timedelta(days=4)},
        ]

        # Notifications
        notifications = [
            {"type": "info", "message": "Nova versão do sistema disponível", "priority": "low"},
            {"type": "warning", "message": "Fatura vence em 5 dias", "priority": "medium"},
            {"type": "success", "message": "Pagamento confirmado", "priority": "low"},
        ]

        # Shortcuts
        shortcuts = [
            {"name": "Pagar Fatura", "icon": "payment", "url": "/payments"},
            {"name": "Baixar Documentos", "icon": "download", "url": "/documents"},
            {"name": "Agendar Serviço", "icon": "calendar", "url": "/bookings"},
            {"name": "Abrir Ticket", "icon": "support", "url": "/tickets"},
        ]

        # Pending actions
        pending_actions = [
            {"action": "Confirmar agendamento", "due_date": datetime.now() + timedelta(days=2)},
            {"action": "Atualizar dados cadastrais", "due_date": datetime.now() + timedelta(days=7)},
        ]

        return PortalDashboard(
            customer_id=customer_id,
            quick_stats=quick_stats,
            recent_activity=recent_activity,
            notifications=notifications,
            shortcuts=shortcuts,
            pending_actions=pending_actions,
            satisfaction_metrics={
                "overall_satisfaction": random.uniform(8.0, 9.5),  # noqa: S311
                "portal_usability": random.uniform(8.5, 9.2),  # noqa: S311
                "support_quality": random.uniform(8.2, 9.3),  # noqa: S311
            },
            generated_at=datetime.now(),
        )

    async def search_knowledge_base(self, query: str, category: str = None) -> list[KnowledgeBaseArticle]:
        """Buscar na base de conhecimento."""
        results = []
        query_lower = query.lower()

        for article in self.knowledge_base.values():
            # Busca por título, conteúdo e tags
            if (
                query_lower in article.title.lower()
                or query_lower in article.content.lower()
                or any(query_lower in tag.lower() for tag in article.tags)
            ):
                # Filtrar por categoria se especificada
                if category and article.category.lower() != category.lower():
                    continue

                results.append(article)

        # Ordenar por relevância (views + helpful votes)
        return sorted(results, key=lambda x: x.views + x.helpful_votes, reverse=True)

    async def create_support_ticket(
        self, customer_id: str, title: str, description: str, category: str, priority: TicketPriority
    ) -> SupportTicket:
        """Criar novo ticket de suporte."""
        ticket_id = f"TICKET_{customer_id}_{len(self.support_tickets.get(customer_id, [])) + 1:03d}"

        ticket = SupportTicket(
            id=ticket_id,
            customer_id=customer_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=TicketStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        if customer_id not in self.support_tickets:
            self.support_tickets[customer_id] = []

        self.support_tickets[customer_id].append(ticket)

        logger.info(f"Ticket criado: {ticket_id} para cliente {customer_id}")
        return ticket

    async def start_chat_conversation(self, customer_id: str, subject: str) -> ChatConversation:
        """Iniciar nova conversa de chat."""
        conversation_id = f"CHAT_{customer_id}_{len(self.chat_conversations) + 1:03d}"

        # Mensagem inicial do bot
        welcome_message = ChatMessage(
            id=f"{conversation_id}_MSG_001",
            conversation_id=conversation_id,
            source=ChatSource.BOT,
            message_type=ChatMessageType.TEXT,
            content=random.choice(self.bot_responses["greeting"]),  # noqa: S311
            timestamp=datetime.now(),
        )

        conversation = ChatConversation(
            id=conversation_id,
            customer_id=customer_id,
            subject=subject,
            status="active",
            created_at=datetime.now(),
            last_message_at=datetime.now(),
            messages=[welcome_message],
        )

        self.chat_conversations[conversation_id] = conversation
        return conversation

    async def send_chat_message(
        self,
        conversation_id: str,
        source: ChatSource,
        content: str,
        message_type: ChatMessageType = ChatMessageType.TEXT,
    ) -> ChatMessage:
        """Enviar mensagem no chat."""
        conversation = self.chat_conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversa {conversation_id} não encontrada")

        message_id = f"{conversation_id}_MSG_{len(conversation.messages) + 1:03d}"

        message = ChatMessage(
            id=message_id,
            conversation_id=conversation_id,
            source=source,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
        )

        conversation.messages.append(message)
        conversation.last_message_at = datetime.now()

        # Se for mensagem do cliente, gerar resposta automática do bot
        if source == ChatSource.CUSTOMER:
            bot_response = await self._generate_bot_response(content)
            if bot_response:
                await asyncio.sleep(0.5)  # Simular delay
                await self.send_chat_message(conversation_id, ChatSource.BOT, bot_response)

        return message

    async def _generate_bot_response(self, customer_message: str) -> str | None:
        """Gerar resposta automática do chatbot."""
        message_lower = customer_message.lower()

        # Palavras-chave para diferentes tipos de ajuda
        if any(word in message_lower for word in ["pagamento", "pagar", "fatura", "boleto", "pix"]):
            return random.choice(self.bot_responses["help_payment"])  # noqa: S311
        elif any(word in message_lower for word in ["manutenção", "manutencao", "tecnico", "reparo"]):
            return random.choice(self.bot_responses["help_maintenance"])  # noqa: S311
        elif any(word in message_lower for word in ["documento", "relatório", "relatorio", "baixar"]):
            return random.choice(self.bot_responses["help_documents"])  # noqa: S311
        else:
            return random.choice(self.bot_responses["fallback"])  # noqa: S311

    async def process_payment(
        self, customer_id: str, amount: float, payment_method: str, description: str = ""
    ) -> PaymentTransaction:
        """Processar pagamento online."""
        transaction_id = f"PAY_{customer_id}_{len(self.payment_transactions.get(customer_id, [])) + 1:03d}"

        # Simular processamento (95% de sucesso)
        success = random.random() > 0.05  # noqa: S311

        transaction = PaymentTransaction(
            id=transaction_id,
            customer_id=customer_id,
            amount=amount,
            description=description or "Pagamento via portal",
            payment_method=payment_method,
            status=PaymentStatus.COMPLETED if success else PaymentStatus.FAILED,
            created_at=datetime.now(),
            processed_at=datetime.now() if success else None,
            transaction_id=f"TXN_{random.randint(100000, 999999)}" if success else None,  # noqa: S311
        )

        if customer_id not in self.payment_transactions:
            self.payment_transactions[customer_id] = []

        self.payment_transactions[customer_id].append(transaction)

        logger.info(f"Pagamento processado: {transaction_id} - {transaction.status.value}")
        return transaction

    async def book_service(
        self, customer_id: str, service_type: ServiceType, title: str, scheduled_date: datetime, description: str = ""
    ) -> ServiceBooking:
        """Agendar serviço através do portal."""
        booking_id = f"BOOKING_{customer_id}_{len(self.service_bookings.get(customer_id, [])) + 1:03d}"

        # Duração padrão por tipo de serviço
        duration_map = {
            ServiceType.TECHNICAL_SUPPORT: 60,
            ServiceType.MAINTENANCE: 120,
            ServiceType.CONSULTATION: 90,
            ServiceType.TRAINING: 180,
            ServiceType.AUDIT: 240,
        }

        booking = ServiceBooking(
            id=booking_id,
            customer_id=customer_id,
            service_type=service_type,
            title=title,
            description=description or f"Agendamento de {service_type.value}",
            scheduled_date=scheduled_date,
            duration_minutes=duration_map.get(service_type, 90),
            status="scheduled",
            location="A definir",
            cost=random.uniform(200, 800),  # noqa: S311
        )

        if customer_id not in self.service_bookings:
            self.service_bookings[customer_id] = []

        self.service_bookings[customer_id].append(booking)

        logger.info(f"Serviço agendado: {booking_id} para {scheduled_date}")
        return booking

    async def download_document(self, customer_id: str, document_id: str) -> CustomerDocument | None:
        """Fazer download de documento."""
        documents = self.customer_documents.get(customer_id, [])

        for document in documents:
            if document.id == document_id:
                document.download_count += 1
                logger.info(f"Download realizado: {document_id} ({document.download_count}x)")
                return document

        return None

    async def get_portal_analytics(self) -> PortalAnalytics:
        """Obter analytics completo do portal."""

        # Calcular métricas agregadas
        all_usage = []
        for usage_list in self.portal_usage.values():
            all_usage.extend(usage_list)

        total_active_users = len(self.portal_usage)

        # Usuários ativos no mês
        thirty_days_ago = datetime.now() - timedelta(days=30)
        monthly_active = len(
            [
                customer_id
                for customer_id, usage_list in self.portal_usage.items()
                if any(usage.date >= thirty_days_ago and usage.login_count > 0 for usage in usage_list)
            ]
        )

        # Usuários ativos hoje
        today = datetime.now().date()
        daily_active = len(
            [
                customer_id
                for customer_id, usage_list in self.portal_usage.items()
                if any(usage.date.date() == today and usage.login_count > 0 for usage in usage_list)
            ]
        )

        # Duração média de sessão
        avg_session_duration = sum(usage.time_spent_minutes for usage in all_usage) / len(all_usage) if all_usage else 0

        # Tickets e resoluções
        all_tickets = []
        for ticket_list in self.support_tickets.values():
            all_tickets.extend(ticket_list)

        resolved_tickets = [t for t in all_tickets if t.resolution_time_hours is not None]
        avg_resolution_hours = (
            sum(t.resolution_time_hours for t in resolved_tickets) / len(resolved_tickets) if resolved_tickets else 0
        )

        # Downloads de documentos
        total_downloads = sum(
            sum(doc.download_count for doc in doc_list) for doc_list in self.customer_documents.values()
        )

        # Pagamentos processados
        total_payments = sum(
            sum(t.amount for t in payment_list if t.status == PaymentStatus.COMPLETED)
            for payment_list in self.payment_transactions.values()
        )

        # Satisfação do cliente
        all_ratings = []
        for ticket_list in self.support_tickets.values():
            all_ratings.extend([t.customer_rating for t in ticket_list if t.customer_rating])

        for conv_list in self.chat_conversations.values():
            if isinstance(conv_list, ChatConversation) and conv_list.satisfaction_rating:
                all_ratings.append(conv_list.satisfaction_rating)

        avg_satisfaction = sum(all_ratings) / len(all_ratings) if all_ratings else 8.5

        # Taxa de auto-resolução
        self_service_tickets = len(
            [t for t in all_tickets if t.assigned_agent is None and t.status == TicketStatus.RESOLVED]
        )
        self_service_rate = self_service_tickets / len(all_tickets) if all_tickets else 0

        # Taxa de resolução de chat
        chat_conversations = [conv for conv in self.chat_conversations.values() if isinstance(conv, ChatConversation)]
        resolved_chats = len([c for c in chat_conversations if c.satisfaction_rating and c.satisfaction_rating >= 8])
        chat_resolution_rate = resolved_chats / len(chat_conversations) if chat_conversations else 0

        # Eficácia da knowledge base
        kb_effectiveness = sum(
            article.helpful_votes / max(1, article.helpful_votes + article.unhelpful_votes)
            for article in self.knowledge_base.values()
        ) / len(self.knowledge_base)

        return PortalAnalytics(
            total_active_users=total_active_users,
            monthly_active_users=monthly_active,
            daily_active_users=daily_active,
            avg_session_duration_minutes=avg_session_duration,
            total_tickets_created=len(all_tickets),
            avg_ticket_resolution_hours=avg_resolution_hours,
            total_documents_downloaded=total_downloads,
            total_payments_processed=total_payments,
            customer_satisfaction_avg=avg_satisfaction,
            self_service_resolution_rate=self_service_rate,
            chat_resolution_rate=chat_resolution_rate,
            knowledge_base_effectiveness=kb_effectiveness,
        )

    async def get_customer_portal_usage(self, customer_id: str, days: int = 30) -> list[PortalUsageAnalytics]:
        """Obter dados de uso do portal para um cliente."""
        usage_data = self.portal_usage.get(customer_id, [])

        # Filtrar pelos últimos N dias
        cutoff_date = datetime.now() - timedelta(days=days)
        return [usage for usage in usage_data if usage.date >= cutoff_date]

    async def get_customer_tickets(self, customer_id: str, status: TicketStatus = None) -> list[SupportTicket]:
        """Obter tickets de um cliente."""
        tickets = self.support_tickets.get(customer_id, [])

        if status:
            tickets = [t for t in tickets if t.status == status]

        return sorted(tickets, key=lambda x: x.created_at, reverse=True)

    async def get_customer_documents(
        self, customer_id: str, document_type: DocumentType = None
    ) -> list[CustomerDocument]:
        """Obter documentos de um cliente."""
        documents = self.customer_documents.get(customer_id, [])

        if document_type:
            documents = [d for d in documents if d.document_type == document_type]

        return sorted(documents, key=lambda x: x.created_at, reverse=True)


# Instância singleton do serviço
portal_selfservice_service = PortalSelfServiceService()


if __name__ == "__main__":
    # Teste básico
    async def test_portal_service():
        service = PortalSelfServiceService()

        # Obter analytics
        analytics = await service.get_portal_analytics()
        print(f"Active Users: {analytics.total_active_users}")
        print(f"Customer Satisfaction: {analytics.customer_satisfaction_avg:.2f}")

        # Obter dashboard de cliente
        dashboard = await service.get_customer_dashboard("CUST_0001")
        print(f"Pending Tickets: {dashboard.quick_stats['pending_tickets']}")

    asyncio.run(test_portal_service())
