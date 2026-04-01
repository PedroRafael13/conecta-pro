"""
Email Responder Service - Sprint 54.

Servico para geracao automatica de respostas de email.
"""

import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class EmailResponder:
    """
    Gerador de respostas de email.

    Gera respostas automaticas baseadas em:
    - Templates pre-definidos
    - Analise do conteudo do email
    - Contexto do remetente
    - Historico de interacoes
    """

    def __init__(self):
        """Inicializa o gerador de respostas."""
        self._templates = self._load_default_templates()
        self._greetings = self._load_greetings()
        self._signatures = self._load_signatures()
        self._phrases = self._load_common_phrases()

    def _load_default_templates(self) -> dict[str, dict[str, Any]]:
        """Carrega templates padrao."""
        return {
            # Suporte
            "support_acknowledgment": {
                "category": "support",
                "intent": "request",
                "subject": "Re: {original_subject}",
                "body": """Prezado(a) {sender_name},

Recebemos sua solicitacao e ela foi registrada em nosso sistema com o numero #{ticket_id}.

Nossa equipe de suporte analisara seu caso e retornara em ate {response_time}.

{action_items}

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "ticket_id", "response_time", "action_items", "signature"],
            },
            "support_resolution": {
                "category": "support",
                "intent": "resolution",
                "subject": "Re: {original_subject} - Resolvido",
                "body": """Prezado(a) {sender_name},

Informamos que sua solicitacao #{ticket_id} foi resolvida.

{resolution_details}

Caso tenha alguma duvida adicional, estamos a disposicao.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "ticket_id", "resolution_details", "signature"],
            },
            # Vendas
            "sales_inquiry": {
                "category": "sales",
                "intent": "inquiry",
                "subject": "Re: {original_subject}",
                "body": """Prezado(a) {sender_name},

Agradecemos seu interesse em nossos servicos!

{product_info}

Para mais informacoes ou para agendar uma demonstracao, entre em contato conosco.

{contact_info}

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "product_info", "contact_info", "signature"],
            },
            "sales_quote": {
                "category": "sales",
                "intent": "quote",
                "subject": "Re: {original_subject} - Proposta Comercial",
                "body": """Prezado(a) {sender_name},

Conforme solicitado, segue nossa proposta comercial:

{quote_details}

Esta proposta e valida ate {valid_until}.

Estamos a disposicao para esclarecer qualquer duvida.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "quote_details", "valid_until", "signature"],
            },
            # Cobranca
            "billing_reminder": {
                "category": "billing",
                "intent": "reminder",
                "subject": "Lembrete de Pagamento - {reference}",
                "body": """Prezado(a) {sender_name},

Identificamos que a fatura #{invoice_id} no valor de {amount} venceu em {due_date}.

Para sua comodidade, segue o codigo de barras para pagamento:
{barcode}

Caso ja tenha efetuado o pagamento, por favor desconsidere esta mensagem.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "invoice_id", "amount", "due_date", "barcode", "reference", "signature"],
            },
            "billing_confirmation": {
                "category": "billing",
                "intent": "confirmation",
                "subject": "Re: {original_subject} - Pagamento Confirmado",
                "body": """Prezado(a) {sender_name},

Confirmamos o recebimento do pagamento referente a fatura #{invoice_id}.

Detalhes:
- Valor: {amount}
- Data: {payment_date}
- Forma: {payment_method}

Agradecemos pela preferencia!

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "invoice_id", "amount", "payment_date", "payment_method", "signature"],
            },
            # Reclamacao
            "complaint_acknowledgment": {
                "category": "complaint",
                "intent": "acknowledgment",
                "subject": "Re: {original_subject}",
                "body": """Prezado(a) {sender_name},

Lamentamos pelo inconveniente relatado e agradecemos por nos comunicar.

Sua reclamacao foi registrada sob o protocolo #{protocol_id} e sera tratada com prioridade.

{next_steps}

Pedimos desculpas pelo transtorno e estamos trabalhando para resolver a situacao.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "protocol_id", "next_steps", "signature"],
            },
            # Informacao
            "information_response": {
                "category": "information",
                "intent": "response",
                "subject": "Re: {original_subject}",
                "body": """Prezado(a) {sender_name},

Em resposta a sua solicitacao de informacoes:

{information}

Caso precise de mais detalhes, estamos a disposicao.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "information", "signature"],
            },
            # Agendamento
            "scheduling_confirmation": {
                "category": "scheduling",
                "intent": "confirmation",
                "subject": "Confirmacao de Agendamento - {event_type}",
                "body": """Prezado(a) {sender_name},

Confirmamos seu agendamento conforme solicitado:

- Data: {date}
- Horario: {time}
- Local: {location}
- Tipo: {event_type}

{additional_info}

Por favor, confirme sua presenca respondendo este email.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "date", "time", "location", "event_type", "additional_info", "signature"],
            },
            "scheduling_reschedule": {
                "category": "scheduling",
                "intent": "reschedule",
                "subject": "Re: {original_subject} - Reagendamento",
                "body": """Prezado(a) {sender_name},

Conforme solicitado, seu agendamento foi alterado:

De: {old_date} as {old_time}
Para: {new_date} as {new_time}

{reason}

Por favor, confirme a alteracao.

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "old_date", "old_time", "new_date", "new_time", "reason", "signature"],
            },
            # Feedback
            "feedback_thanks": {
                "category": "feedback",
                "intent": "thanks",
                "subject": "Re: {original_subject}",
                "body": """Prezado(a) {sender_name},

Agradecemos por compartilhar sua opiniao conosco!

Seu feedback e muito importante para melhorarmos nossos servicos.

{response_to_feedback}

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "response_to_feedback", "signature"],
            },
            # Interno
            "internal_acknowledgment": {
                "category": "internal",
                "intent": "acknowledgment",
                "subject": "Re: {original_subject}",
                "body": """Ola {sender_name},

Recebi sua mensagem e {response}.

{details}

Qualquer duvida, estou a disposicao.

{signature}""",
                "variables": ["sender_name", "response", "details", "signature"],
            },
            # Auto-resposta generica
            "auto_reply_generic": {
                "category": "other",
                "intent": "auto_reply",
                "subject": "Re: {original_subject}",
                "body": """Prezado(a) {sender_name},

Recebemos sua mensagem e em breve retornaremos.

{additional_message}

Atenciosamente,
{signature}""",
                "variables": ["sender_name", "additional_message", "signature"],
            },
        }

    def _load_greetings(self) -> dict[str, list[str]]:
        """Carrega saudacoes por tom."""
        return {
            "formal": [
                "Prezado(a) {name}",
                "Caro(a) {name}",
                "Exmo(a). Sr(a). {name}",
            ],
            "professional": [
                "Prezado(a) {name}",
                "Caro(a) {name}",
                "Ola, {name}",
            ],
            "friendly": [
                "Ola {name}",
                "Ola, {name}!",
                "Oi {name}",
            ],
            "casual": [
                "Oi {name}!",
                "E ai {name}",
                "{name},",
            ],
        }

    def _load_signatures(self) -> dict[str, str]:
        """Carrega assinaturas padrao."""
        return {
            "formal": """Atenciosamente,

{company_name}
{department}
{contact_email}
{contact_phone}""",
            "professional": """Atenciosamente,

{sender_name}
{sender_role}
{company_name}
{contact_email}""",
            "friendly": """Abracos,

{sender_name}
{company_name}""",
            "casual": """{sender_name}""",
        }

    def _load_common_phrases(self) -> dict[str, list[str]]:
        """Carrega frases comuns por contexto."""
        return {
            "thanks": [
                "Agradecemos seu contato.",
                "Obrigado por entrar em contato conosco.",
                "Agradecemos pela mensagem.",
            ],
            "apology": [
                "Pedimos desculpas pelo inconveniente.",
                "Lamentamos pelo ocorrido.",
                "Sentimos muito pelo transtorno.",
            ],
            "availability": [
                "Estamos a disposicao para esclarecer duvidas.",
                "Caso precise de mais informacoes, estamos a disposicao.",
                "Nao hesite em nos contatar novamente.",
            ],
            "urgency": [
                "Trataremos seu caso com prioridade.",
                "Sua solicitacao sera tratada com urgencia.",
                "Daremos prioridade ao seu caso.",
            ],
            "confirmation": [
                "Confirmamos o recebimento da sua mensagem.",
                "Sua solicitacao foi registrada com sucesso.",
                "Recebemos sua mensagem e ela esta sendo processada.",
            ],
        }

    def generate_reply(
        self,
        email_data: dict[str, Any],
        classification: dict[str, Any],
        tone: str = "professional",
        max_length: int = 500,
        include_greeting: bool = True,
        include_signature: bool = True,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Gera resposta para um email.

        Args:
            email_data: Dados do email original
            classification: Resultado da classificacao
            tone: Tom da resposta (formal, professional, friendly, casual)
            max_length: Tamanho maximo da resposta
            include_greeting: Incluir saudacao
            include_signature: Incluir assinatura
            context: Contexto adicional

        Returns:
            Dict com resposta gerada e metadados
        """
        start_time = datetime.utcnow()
        context = context or {}

        try:
            # Extrai informacoes
            category = classification.get("category", "other")
            intent = classification.get("intent", "general")
            sentiment = classification.get("sentiment", "neutral")
            sender_name = self._extract_sender_name(email_data)
            original_subject = email_data.get("subject", "")

            # Seleciona template
            template = self._select_template(category, intent, context)
            template_used = template.get("name") if template else None

            # Gera componentes
            greeting = ""
            if include_greeting:
                greeting = self._generate_greeting(sender_name, tone)

            signature = ""
            if include_signature:
                signature = self._generate_signature(tone, context)

            # Gera corpo da resposta
            body = self._generate_body(
                template=template,
                email_data=email_data,
                classification=classification,
                context=context,
                sender_name=sender_name,
            )

            # Ajusta tom baseado no sentimento
            body = self._adjust_tone(body, sentiment, tone)

            # Monta resposta completa
            full_reply = self._compose_reply(
                greeting=greeting,
                body=body,
                signature=signature,
                max_length=max_length,
            )

            # Gera versao HTML
            html_reply = self._convert_to_html(full_reply)

            # Gera sugestoes alternativas
            suggestions = self._generate_suggestions(
                category=category,
                intent=intent,
                email_data=email_data,
            )

            # Calcula confianca
            confidence = self._calculate_confidence(
                template_used=template_used is not None,
                has_context=bool(context),
                classification_confidence=classification.get("category_confidence", 0.5),
            )

            # Identifica variaveis preenchidas
            variables_filled = self._get_filled_variables(body, context)

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                "reply_text": full_reply,
                "reply_html": html_reply,
                "confidence": confidence,
                "tone_used": tone,
                "template_used": template_used,
                "variables_filled": variables_filled,
                "suggestions": suggestions,
                "processing_time_ms": processing_time,
                "subject": f"Re: {original_subject}" if original_subject else "Re: Sua mensagem",
            }

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return {
                "reply_text": self._generate_fallback_reply(email_data, tone),
                "reply_html": None,
                "confidence": 0.3,
                "tone_used": tone,
                "template_used": None,
                "variables_filled": {},
                "suggestions": [],
                "processing_time_ms": processing_time,
                "subject": f"Re: {email_data.get('subject', 'Sua mensagem')}",
            }

    def _extract_sender_name(self, email_data: dict[str, Any]) -> str:
        """Extrai nome do remetente."""
        # Tenta from_name primeiro
        if email_data.get("from_name"):
            name = email_data["from_name"]
            # Remove titulos comuns
            for title in ["Dr.", "Dra.", "Sr.", "Sra.", "Prof.", "Profa."]:
                name = name.replace(title, "").strip()
            return name.split()[0] if name else "Cliente"

        # Extrai do email
        if email_data.get("from_address"):
            email = email_data["from_address"]
            local_part = email.split("@")[0]
            # Remove numeros e caracteres especiais
            name = re.sub(r"[0-9._-]+", " ", local_part).strip()
            if name:
                return name.title().split()[0]

        return "Cliente"

    def _select_template(
        self,
        category: str,
        intent: str,
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Seleciona template apropriado."""
        # Procura template especifico
        template_key = f"{category}_{intent}"
        if template_key in self._templates:
            template = self._templates[template_key].copy()
            template["name"] = template_key
            return template

        # Procura por categoria
        for key, template in self._templates.items():
            if template.get("category") == category:
                result = template.copy()
                result["name"] = key
                return result

        # Template generico
        if "auto_reply_generic" in self._templates:
            template = self._templates["auto_reply_generic"].copy()
            template["name"] = "auto_reply_generic"
            return template

        return None

    def _generate_greeting(self, name: str, tone: str) -> str:
        """Gera saudacao."""
        greetings = self._greetings.get(tone, self._greetings["professional"])
        greeting = greetings[0]  # Usa primeiro como padrao
        return greeting.format(name=name)

    def _generate_signature(self, tone: str, context: dict[str, Any]) -> str:
        """Gera assinatura."""
        signature_template = self._signatures.get(tone, self._signatures["professional"])

        defaults = {
            "company_name": context.get("company_name", "Conecta Plus"),
            "department": context.get("department", "Atendimento ao Cliente"),
            "sender_name": context.get("sender_name", "Equipe Conecta Plus"),
            "sender_role": context.get("sender_role", ""),
            "contact_email": context.get("contact_email", "contato@conectaplus.com.br"),
            "contact_phone": context.get("contact_phone", ""),
        }

        try:
            return signature_template.format(**defaults)
        except KeyError:
            return defaults["sender_name"]

    def _generate_body(
        self,
        template: dict[str, Any] | None,
        email_data: dict[str, Any],
        classification: dict[str, Any],
        context: dict[str, Any],
        sender_name: str,
    ) -> str:
        """Gera corpo da resposta."""
        if not template:
            return self._generate_dynamic_body(email_data, classification, context)

        body_template = template.get("body", "")

        # Prepara variaveis
        variables = {
            "sender_name": sender_name,
            "original_subject": email_data.get("subject", "sua mensagem"),
            "ticket_id": context.get("ticket_id", "000001"),
            "protocol_id": context.get("protocol_id", "000001"),
            "response_time": context.get("response_time", "24 horas"),
            "signature": "",  # Sera adicionada depois
            "action_items": self._format_action_items(classification.get("action_items", [])),
            "resolution_details": context.get("resolution_details", ""),
            "product_info": context.get("product_info", ""),
            "contact_info": context.get("contact_info", ""),
            "quote_details": context.get("quote_details", ""),
            "valid_until": context.get("valid_until", "30 dias"),
            "invoice_id": context.get("invoice_id", ""),
            "amount": context.get("amount", ""),
            "due_date": context.get("due_date", ""),
            "barcode": context.get("barcode", ""),
            "reference": context.get("reference", ""),
            "payment_date": context.get("payment_date", ""),
            "payment_method": context.get("payment_method", ""),
            "next_steps": context.get("next_steps", "Nossa equipe entrara em contato em breve."),
            "information": context.get("information", ""),
            "date": context.get("date", ""),
            "time": context.get("time", ""),
            "location": context.get("location", ""),
            "event_type": context.get("event_type", ""),
            "additional_info": context.get("additional_info", ""),
            "old_date": context.get("old_date", ""),
            "old_time": context.get("old_time", ""),
            "new_date": context.get("new_date", ""),
            "new_time": context.get("new_time", ""),
            "reason": context.get("reason", ""),
            "response_to_feedback": context.get("response_to_feedback", "Seu feedback foi registrado."),
            "response": context.get("response", "estou verificando"),
            "details": context.get("details", ""),
            "additional_message": context.get("additional_message", ""),
        }

        # Atualiza com contexto
        variables.update(context)

        try:
            return body_template.format(**variables)
        except KeyError as e:
            logger.warning(f"Variavel de template nao encontrada: {e}")
            # Tenta substituir o que conseguir
            for key, value in variables.items():
                body_template = body_template.replace("{" + key + "}", str(value))
            return body_template

    def _generate_dynamic_body(
        self,
        email_data: dict[str, Any],
        classification: dict[str, Any],
        context: dict[str, Any],
    ) -> str:
        """Gera corpo dinamico quando nao ha template."""
        parts = []

        # Confirmacao de recebimento
        parts.append(self._phrases["confirmation"][0])
        parts.append("")

        # Resposta baseada na categoria
        category = classification.get("category", "other")

        if category == "support":
            parts.append("Nossa equipe de suporte analisara sua solicitacao e retornara em breve.")
        elif category == "sales":
            parts.append("Um de nossos consultores entrara em contato para atende-lo.")
        elif category == "billing":
            parts.append("Nosso departamento financeiro verificara sua solicitacao.")
        elif category == "complaint":
            parts.append(self._phrases["apology"][0])
            parts.append("Trataremos seu caso com prioridade.")
        elif category == "scheduling":
            parts.append("Verificaremos as disponibilidades e confirmaremos em breve.")
        else:
            parts.append("Em breve retornaremos com uma resposta.")

        parts.append("")
        parts.append(self._phrases["availability"][0])

        return "\n".join(parts)

    def _format_action_items(self, action_items: list[dict[str, Any]]) -> str:
        """Formata itens de acao."""
        if not action_items:
            return ""

        lines = ["Itens identificados em sua mensagem:"]
        for item in action_items[:5]:  # Limita a 5 itens
            action = item.get("action", "Item")
            deadline = item.get("deadline")
            if deadline:
                lines.append(f"- {action} (prazo: {deadline})")
            else:
                lines.append(f"- {action}")

        return "\n".join(lines)

    def _adjust_tone(self, body: str, sentiment: str, tone: str) -> str:
        """Ajusta tom baseado no sentimento do email original."""
        # Se email negativo, adiciona empatia
        if sentiment in ["very_negative", "negative"]:
            if "Lamentamos" not in body and "desculpas" not in body.lower():
                empathy = "Entendemos sua preocupacao e estamos aqui para ajudar.\n\n"
                # Insere apos primeira linha
                lines = body.split("\n", 1)
                if len(lines) > 1:
                    body = lines[0] + "\n\n" + empathy + lines[1]
                else:
                    body = empathy + body

        return body

    def _compose_reply(
        self,
        greeting: str,
        body: str,
        signature: str,
        max_length: int,
    ) -> str:
        """Compoe resposta final."""
        parts = []

        if greeting:
            parts.append(greeting)
            parts.append("")

        parts.append(body)

        if signature:
            parts.append("")
            parts.append(signature)

        reply = "\n".join(parts)

        # Trunca se necessario
        if len(reply) > max_length:
            # Tenta manter estrutura
            if signature:
                available = max_length - len(signature) - len(greeting) - 50
                if available > 100:
                    body_lines = body.split("\n")
                    truncated_body = []
                    current_length = 0
                    for line in body_lines:
                        if current_length + len(line) < available:
                            truncated_body.append(line)
                            current_length += len(line) + 1
                        else:
                            break
                    truncated_body.append("...")
                    body = "\n".join(truncated_body)

                    parts = [greeting, "", body, "", signature] if greeting else [body, "", signature]
                    reply = "\n".join(parts)

        return reply

    def _convert_to_html(self, text: str) -> str:
        """Converte texto para HTML."""
        # Escapa HTML
        html = text.replace("&", "&amp;")
        html = html.replace("<", "&lt;")
        html = html.replace(">", "&gt;")

        # Converte quebras de linha
        html = html.replace("\n\n", "</p><p>")
        html = html.replace("\n", "<br>")

        # Converte listas
        html = re.sub(r"<br>- ([^<]+)", r"<li>\1</li>", html)
        html = re.sub(r"(<li>.*?</li>)+", r"<ul>\g<0></ul>", html)

        # Wrap em paragrafos
        html = f"<div style='font-family: Arial, sans-serif; font-size: 14px;'><p>{html}</p></div>"

        return html

    def _generate_suggestions(
        self,
        category: str,
        intent: str,
        email_data: dict[str, Any],
    ) -> list[str]:
        """Gera sugestoes alternativas."""
        suggestions = []

        if category == "support":
            suggestions.extend(
                [
                    "Posso ajudar com mais alguma coisa?",
                    "Caso o problema persista, entre em contato novamente.",
                    "Gostaria de abrir um chamado formal?",
                ]
            )
        elif category == "sales":
            suggestions.extend(
                [
                    "Gostaria de agendar uma demonstracao?",
                    "Posso enviar mais informacoes sobre nossos planos?",
                    "Quer conhecer nossos casos de sucesso?",
                ]
            )
        elif category == "billing":
            suggestions.extend(
                [
                    "Deseja parcelar o valor?",
                    "Posso verificar outras formas de pagamento?",
                    "Gostaria de receber um extrato detalhado?",
                ]
            )
        elif category == "complaint":
            suggestions.extend(
                [
                    "Gostaria de falar com um supervisor?",
                    "Posso registrar uma reclamacao formal?",
                    "Como podemos compensar o transtorno?",
                ]
            )

        return suggestions[:3]

    def _calculate_confidence(
        self,
        template_used: bool,
        has_context: bool,
        classification_confidence: float,
    ) -> float:
        """Calcula confianca da resposta."""
        confidence = 0.5

        if template_used:
            confidence += 0.2
        if has_context:
            confidence += 0.15
        confidence += classification_confidence * 0.15

        return min(0.95, confidence)

    def _get_filled_variables(
        self,
        body: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Identifica variaveis preenchidas."""
        filled = {}
        for key, value in context.items():
            if value and str(value) in body:
                filled[key] = value
        return filled

    def _generate_fallback_reply(
        self,
        email_data: dict[str, Any],
        tone: str,
    ) -> str:
        """Gera resposta de fallback."""
        sender_name = self._extract_sender_name(email_data)
        greeting = self._generate_greeting(sender_name, tone)

        return f"""{greeting},

Recebemos sua mensagem e em breve retornaremos com uma resposta.

Agradecemos seu contato.

Atenciosamente,
Equipe Conecta Plus"""

    def apply_template(
        self,
        template_code: str,
        variables: dict[str, Any],
    ) -> str | None:
        """
        Aplica um template especifico.

        Args:
            template_code: Codigo do template
            variables: Variaveis para substituicao

        Returns:
            Texto gerado ou None se template nao encontrado
        """
        template = self._templates.get(template_code)
        if not template:
            return None

        body = template.get("body", "")

        try:
            return body.format(**variables)
        except KeyError as e:
            logger.warning(f"Variavel de template nao encontrada: {e}")
            for key, value in variables.items():
                body = body.replace("{" + key + "}", str(value))
            return body

    def get_available_templates(
        self,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Lista templates disponiveis.

        Args:
            category: Filtrar por categoria

        Returns:
            Lista de templates
        """
        templates = []

        for code, template in self._templates.items():
            if category and template.get("category") != category:
                continue

            templates.append(
                {
                    "code": code,
                    "category": template.get("category"),
                    "intent": template.get("intent"),
                    "subject": template.get("subject"),
                    "variables": template.get("variables", []),
                }
            )

        return templates
