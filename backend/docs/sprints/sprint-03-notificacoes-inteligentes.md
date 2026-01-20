# Sprint 03: Notificações Inteligentes

## 🎯 OBJETIVO
Implementar sistema avançado de notificações inteligentes com IA para personalização, timing otimizado, multi-canal e análise comportamental, maximizando engajamento e reduzindo spam.

## 🔧 ESPECIFICAÇÕES TÉCNICAS

### Arquitetura de Notificações Inteligentes
```
┌─────────────────────────────────────────────────────────┐
│                NOTIFICAÇÕES INTELIGENTES                 │
├─────────────────────────────────────────────────────────┤
│  IA Engine                                               │
│  ├── Personalization Engine                              │
│  ├── Timing Optimizer                                    │
│  ├── Content Generator                                   │
│  ├── Channel Selector                                    │
│  └── Behavioral Analyzer                                 │
├─────────────────────────────────────────────────────────┤
│  Notification Hub                                        │
│  ├── Multi-Channel Dispatcher                           │
│  ├── Template Manager                                    │
│  ├── A/B Testing Engine                                  │
│  ├── Delivery Scheduler                                  │
│  └── Analytics Collector                                 │
├─────────────────────────────────────────────────────────┤
│  Delivery Channels                                       │
│  ├── Push Notifications (Mobile/Web)                    │
│  ├── Email (Rich HTML/Plain Text)                       │
│  ├── SMS/WhatsApp                                        │
│  ├── In-App Notifications                               │
│  └── Slack/Teams Integration                            │
├─────────────────────────────────────────────────────────┤
│  Data Layer                                              │
│  ├── User Preferences (Redis)                           │
│  ├── Delivery Logs (PostgreSQL)                         │
│  ├── Templates (MongoDB)                                │
│  └── Analytics (InfluxDB)                               │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### 1. Personalization Engine
```python
# core/notifications/personalization_engine.py
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class PersonalizationEngine:
    """Motor de personalização de notificações."""

    def __init__(self):
        self.engagement_model = RandomForestClassifier()
        self.timing_model = RandomForestClassifier()
        self.content_model = None  # LLM para geração de conteúdo
        self.load_models()

    async def personalize_notification(
        self,
        user_id: int,
        notification_type: str,
        base_content: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Personaliza notificação para usuário específico.

        Args:
            user_id: ID do usuário
            notification_type: Tipo da notificação
            base_content: Conteúdo base
            context: Contexto adicional

        Returns:
            Notificação personalizada
        """
        
        # 1. Obter perfil do usuário
        user_profile = await self.get_user_profile(user_id)
        
        # 2. Analisar histórico de engajamento
        engagement_history = await self.get_engagement_history(user_id)
        
        # 3. Determinar timing ótimo
        optimal_time = await self.calculate_optimal_timing(
            user_profile, engagement_history
        )
        
        # 4. Selecionar canal preferido
        preferred_channel = await self.select_optimal_channel(
            user_profile, notification_type
        )
        
        # 5. Personalizar conteúdo
        personalized_content = await self.personalize_content(
            base_content, user_profile, context
        )
        
        # 6. Calcular probabilidade de engajamento
        engagement_score = await self.predict_engagement(
            user_profile, notification_type, optimal_time, preferred_channel
        )
        
        return {
            "user_id": user_id,
            "content": personalized_content,
            "optimal_time": optimal_time,
            "preferred_channel": preferred_channel,
            "engagement_score": engagement_score,
            "personalization_factors": self.get_personalization_factors(user_profile)
        }

    async def get_user_profile(self, user_id: int) -> Dict:
        """Obter perfil completo do usuário."""
        
        profile = await get_user_basic_profile(user_id)
        
        # Enriquecer com dados comportamentais
        profile.update({
            "activity_patterns": await self.analyze_activity_patterns(user_id),
            "preferences": await get_notification_preferences(user_id),
            "engagement_metrics": await calculate_engagement_metrics(user_id),
            "device_info": await get_user_devices(user_id),
            "timezone": await get_user_timezone(user_id)
        })
        
        return profile

    async def analyze_activity_patterns(self, user_id: int) -> Dict:
        """Analisa padrões de atividade do usuário."""
        
        # Buscar atividades dos últimos 30 dias
        activities = await get_user_activities(user_id, days=30)
        
        patterns = {
            "peak_hours": self.calculate_peak_hours(activities),
            "active_days": self.calculate_active_days(activities),
            "session_duration": self.calculate_avg_session_duration(activities),
            "feature_usage": self.analyze_feature_usage(activities),
            "response_patterns": self.analyze_notification_responses(user_id)
        }
        
        return patterns

    def calculate_peak_hours(self, activities: List[Dict]) -> List[int]:
        """Calcula horários de pico de atividade."""
        hour_counts = [0] * 24
        
        for activity in activities:
            hour = activity["timestamp"].hour
            hour_counts[hour] += 1
        
        # Retornar top 3 horários
        sorted_hours = sorted(
            enumerate(hour_counts), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [hour for hour, _ in sorted_hours[:3]]

    async def calculate_optimal_timing(
        self, user_profile: Dict, engagement_history: List[Dict]
    ) -> datetime:
        """Calcula timing ótimo para envio."""
        
        # Features para o modelo
        features = self.extract_timing_features(user_profile, engagement_history)
        
        # Prever horário ótimo usando modelo ML
        optimal_hour = self.timing_model.predict([features])[0]
        
        # Ajustar para timezone do usuário
        user_tz = user_profile.get("timezone", "UTC")
        optimal_time = self.adjust_for_timezone(optimal_hour, user_tz)
        
        return optimal_time

    async def select_optimal_channel(
        self, user_profile: Dict, notification_type: str
    ) -> str:
        """Seleciona canal ótimo baseado no perfil e tipo."""
        
        # Preferências explícitas do usuário
        preferences = user_profile.get("preferences", {})
        
        # Performance histórica por canal
        channel_performance = await self.get_channel_performance(
            user_profile["user_id"], notification_type
        )
        
        # Contexto atual (online, offline, device ativo)
        current_context = await self.get_current_context(user_profile["user_id"])
        
        # Score cada canal
        channel_scores = {}
        for channel in ["push", "email", "sms", "in_app"]:
            score = self.calculate_channel_score(
                channel, preferences, channel_performance, current_context
            )
            channel_scores[channel] = score
        
        # Retornar canal com maior score
        best_channel = max(channel_scores, key=channel_scores.get)
        
        return best_channel

    async def personalize_content(
        self, base_content: Dict, user_profile: Dict, context: Dict
    ) -> Dict:
        """Personaliza conteúdo da notificação."""
        
        # Substituir variáveis dinâmicas
        personalized = base_content.copy()
        
        # Nome personalizado
        user_name = user_profile.get("first_name", "")        if user_name:
            personalized["title"] = personalized["title"].replace("{name}", user_name)
            personalized["body"] = personalized["body"].replace("{name}", user_name)
        
        # Dados contextuais
        if context:
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in personalized["title"]:
                    personalized["title"] = personalized["title"].replace(placeholder, str(value))
                if placeholder in personalized["body"]:
                    personalized["body"] = personalized["body"].replace(placeholder, str(value))
        
        # Ajustar tom baseado no perfil
        tone = self.determine_communication_tone(user_profile)
        personalized = self.adjust_content_tone(personalized, tone)
        
        # Adicionar CTA personalizada
        personalized["cta"] = self.generate_personalized_cta(
            base_content, user_profile
        )
        
        return personalized

    def determine_communication_tone(self, user_profile: Dict) -> str:
        """Determina tom de comunicação baseado no perfil."""
        
        # Analisar histórico de interações
        engagement_style = user_profile.get("engagement_style", "professional")
        
        # Faixa etária
        age_group = user_profile.get("age_group", "adult")
        
        # Setor/área
        business_sector = user_profile.get("business_sector", "general")
        
        # Mapear para tom
        tone_mapping = {
            ("professional", "adult"): "formal",
            ("casual", "young"): "informal",
            ("tech", "adult"): "technical",
            ("creative", "any"): "creative"
        }
        
        for (style, age), tone in tone_mapping.items():
            if engagement_style == style and (age == "any" or age_group == age):
                return tone
        
        return "neutral"

    async def predict_engagement(
        self,
        user_profile: Dict,
        notification_type: str,
        timing: datetime,
        channel: str
    ) -> float:
        """Prediz probabilidade de engajamento."""
        
        # Extrair features
        features = self.extract_engagement_features(
            user_profile, notification_type, timing, channel
        )
        
        # Prever usando modelo treinado
        engagement_probability = self.engagement_model.predict_proba([features])[0][1]
        
        return float(engagement_probability)
```

#### 2. Multi-Channel Dispatcher
```python
# core/notifications/dispatcher.py
import asyncio
from typing import Dict, List, Optional
from enum import Enum

class NotificationChannel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"
    SLACK = "slack"
    TEAMS = "teams"

class MultiChannelDispatcher:
    """Despachador multi-canal de notificações."""

    def __init__(self):
        self.channel_handlers = {
            NotificationChannel.PUSH: PushNotificationHandler(),
            NotificationChannel.EMAIL: EmailNotificationHandler(),
            NotificationChannel.SMS: SMSNotificationHandler(),
            NotificationChannel.WHATSAPP: WhatsAppNotificationHandler(),
            NotificationChannel.IN_APP: InAppNotificationHandler(),
            NotificationChannel.SLACK: SlackNotificationHandler(),
            NotificationChannel.TEAMS: TeamsNotificationHandler()
        }
        
        self.delivery_queue = asyncio.Queue()
        self.retry_queue = asyncio.Queue()

    async def dispatch_notification(
        self,
        notification: Dict,
        channels: List[str],
        scheduling: Optional[Dict] = None
    ) -> Dict:
        """
        Despacha notificação para múltiplos canais.

        Args:
            notification: Dados da notificação
            channels: Lista de canais para envio
            scheduling: Configurações de agendamento

        Returns:
            Resultado do envio
        """
        
        dispatch_id = generate_dispatch_id()
        results = {
            "dispatch_id": dispatch_id,
            "channels": {},
            "overall_status": "pending",
            "sent_at": datetime.utcnow()
        }

        # Processar envio para cada canal
        tasks = []
        for channel_name in channels:
            try:
                channel = NotificationChannel(channel_name)
                task = self.send_to_channel(
                    notification, channel, dispatch_id, scheduling
                )
                tasks.append((channel_name, task))
            except ValueError:
                results["channels"][channel_name] = {
                    "status": "error",
                    "error": f"Invalid channel: {channel_name}"
                }

        # Executar envios em paralelo
        if tasks:
            completed_tasks = await asyncio.gather(
                *[task for _, task in tasks], 
                return_exceptions=True
            )
            
            for i, (channel_name, result) in enumerate(zip(
                [ch for ch, _ in tasks], completed_tasks
            )):
                if isinstance(result, Exception):
                    results["channels"][channel_name] = {
                        "status": "error",
                        "error": str(result)
                    }
                else:
                    results["channels"][channel_name] = result

        # Determinar status geral
        results["overall_status"] = self.calculate_overall_status(
            results["channels"]
        )

        # Salvar log
        await self.log_dispatch_result(results)

        return results

    async def send_to_channel(
        self,
        notification: Dict,
        channel: NotificationChannel,
        dispatch_id: str,
        scheduling: Optional[Dict]
    ) -> Dict:
        """Envia notificação para canal específico."""
        
        handler = self.channel_handlers.get(channel)
        if not handler:
            return {
                "status": "error",
                "error": f"No handler for channel {channel.value}"
            }

        try:
            # Verificar se deve ser agendada
            if scheduling and scheduling.get("send_at"):
                send_at = datetime.fromisoformat(scheduling["send_at"])
                if send_at > datetime.utcnow():
                    await self.schedule_notification(
                        notification, channel, dispatch_id, send_at
                    )
                    return {
                        "status": "scheduled",
                        "scheduled_for": send_at.isoformat()
                    }

            # Enviar imediatamente
            result = await handler.send(notification)
            
            # Adicionar à fila de retry se falhou
            if result["status"] == "failed" and result.get("retryable", False):
                await self.retry_queue.put({
                    "notification": notification,
                    "channel": channel,
                    "dispatch_id": dispatch_id,
                    "attempt": 1,
                    "next_retry": datetime.utcnow() + timedelta(minutes=5)
                })

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "retryable": True
            }

    async def schedule_notification(
        self,
        notification: Dict,
        channel: NotificationChannel,
        dispatch_id: str,
        send_at: datetime
    ):
        """Agenda notificação para envio futuro."""
        
        scheduled_notification = {
            "id": generate_scheduled_id(),
            "dispatch_id": dispatch_id,
            "notification": notification,
            "channel": channel.value,
            "send_at": send_at,
            "status": "scheduled",
            "created_at": datetime.utcnow()
        }
        
        await save_scheduled_notification(scheduled_notification)

    def calculate_overall_status(self, channel_results: Dict) -> str:
        """Calcula status geral baseado nos resultados dos canais."""
        
        statuses = [result.get("status") for result in channel_results.values()]
        
        if all(status == "success" for status in statuses):
            return "success"
        elif any(status == "success" for status in statuses):
            return "partial_success"
        elif all(status in ["failed", "error"] for status in statuses):
            return "failed"
        else:
            return "mixed"

    async def process_scheduled_notifications(self):
        """Processa notificações agendadas que chegaram no horário."""
        
        while True:
            try:
                # Buscar notificações para enviar
                due_notifications = await get_due_scheduled_notifications()
                
                for scheduled in due_notifications:
                    channel = NotificationChannel(scheduled["channel"])
                    await self.send_to_channel(
                        scheduled["notification"],
                        channel,
                        scheduled["dispatch_id"],
                        None
                    )
                    
                    # Marcar como enviada
                    await mark_scheduled_as_sent(scheduled["id"])
                
                # Aguardar antes da próxima verificação
                await asyncio.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Error processing scheduled notifications: {e}")
                await asyncio.sleep(60)

    async def process_retry_queue(self):
        """Processa fila de retry para notificações falhadas."""
        
        while True:
            try:
                retry_item = await self.retry_queue.get()
                
                # Verificar se é hora de tentar novamente
                if datetime.utcnow() >= retry_item["next_retry"]:
                    
                    # Tentar enviar novamente
                    result = await self.send_to_channel(
                        retry_item["notification"],
                        retry_item["channel"],
                        retry_item["dispatch_id"],
                        None
                    )
                    
                    # Se ainda falhou e pode tentar novamente
                    if (result["status"] == "failed" and 
                        retry_item["attempt"] < 3 and 
                        result.get("retryable", False)):
                        
                        retry_item["attempt"] += 1
                        retry_item["next_retry"] = datetime.utcnow() + timedelta(
                            minutes=5 * retry_item["attempt"]  # Backoff exponencial
                        )
                        await self.retry_queue.put(retry_item)
                    
                    else:
                        # Desistir ou sucesso
                        await self.log_final_retry_result(retry_item, result)
                
                else:
                    # Não é hora ainda, voltar para a fila
                    await self.retry_queue.put(retry_item)
                    await asyncio.sleep(30)  # Aguardar um pouco
                    
            except Exception as e:
                logger.error(f"Error processing retry queue: {e}")
```

#### 3. Channel Handlers
```python
# core/notifications/handlers/push_handler.py
from firebase_admin import messaging
import httpx

class PushNotificationHandler:
    """Handler para push notifications."""

    async def send(self, notification: Dict) -> Dict:
        """Envia push notification."""
        
        try:
            user_id = notification["user_id"]
            content = notification["content"]
            
            # Buscar tokens do usuário
            tokens = await get_user_push_tokens(user_id)
            if not tokens:
                return {"status": "failed", "error": "No push tokens"}

            # Criar mensagens
            messages = []
            for token in tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=content["title"],
                        body=content["body"],
                        image=content.get("image_url")
                    ),
                    data=content.get("data", {}),
                    token=token["token"],
                    android=self.create_android_config(content),
                    apns=self.create_apns_config(content)
                )
                messages.append(message)

            # Enviar em batch
            response = await messaging.send_all(messages)
            
            return {
                "status": "success" if response.success_count > 0 else "failed",
                "sent": response.success_count,
                "failed": response.failure_count,
                "details": response.responses
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "retryable": True}

# core/notifications/handlers/email_handler.py
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailNotificationHandler:
    """Handler para notificações por email."""

    def __init__(self):
        self.smtp_config = get_smtp_config()

    async def send(self, notification: Dict) -> Dict:
        """Envia notificação por email."""
        
        try:
            user_id = notification["user_id"]
            content = notification["content"]
            
            # Obter email do usuário
            user_email = await get_user_email(user_id)
            if not user_email:
                return {"status": "failed", "error": "No email address"}

            # Criar mensagem
            msg = MIMEMultipart("alternative")
            msg["Subject"] = content["title"]
            msg["From"] = self.smtp_config["from_email"]
            msg["To"] = user_email

            # Versão texto
            text_part = MIMEText(content["body"], "plain", "utf-8")
            msg.attach(text_part)

            # Versão HTML se disponível
            if content.get("html_body"):
                html_part = MIMEText(content["html_body"], "html", "utf-8")
                msg.attach(html_part)

            # Enviar
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_config["host"],
                port=self.smtp_config["port"],
                start_tls=True,
                username=self.smtp_config["username"],
                password=self.smtp_config["password"]
            )

            return {"status": "success", "email": user_email}

        except Exception as e:
            return {"status": "error", "error": str(e), "retryable": True}

# core/notifications/handlers/sms_handler.py
import httpx

class SMSNotificationHandler:
    """Handler para notificações SMS."""

    def __init__(self):
        self.sms_provider = get_sms_provider_config()

    async def send(self, notification: Dict) -> Dict:
        """Envia notificação SMS."""
        
        try:
            user_id = notification["user_id"]
            content = notification["content"]
            
            # Obter número do usuário
            phone_number = await get_user_phone(user_id)
            if not phone_number:
                return {"status": "failed", "error": "No phone number"}

            # Enviar via provedor (Twilio, AWS SNS, etc.)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.sms_provider["api_url"],
                    json={
                        "to": phone_number,
                        "body": content["body"],
                        "from": self.sms_provider["from_number"]
                    },
                    headers={
                        "Authorization": f"Bearer {self.sms_provider['api_key']}"
                    }
                )
                
                if response.status_code == 200:
                    return {"status": "success", "phone": phone_number}
                else:
                    return {
                        "status": "failed",
                        "error": response.text,
                        "retryable": response.status_code >= 500
                    }

        except Exception as e:
            return {"status": "error", "error": str(e), "retryable": True}
```

#### 4. A/B Testing Engine
```python
# core/notifications/ab_testing.py
from typing import Dict, List, Optional
import random

class ABTestingEngine:
    """Motor de testes A/B para notificações."""

    def __init__(self):
        self.active_tests = {}
        self.load_active_tests()

    async def create_ab_test(
        self,
        test_name: str,
        variants: List[Dict],
        target_audience: Dict,
        duration_days: int,
        success_metric: str
    ) -> str:
        """
        Cria novo teste A/B.

        Args:
            test_name: Nome do teste
            variants: Lista de variantes para testar
            target_audience: Critérios do público-alvo
            duration_days: Duração do teste em dias
            success_metric: Métrica de sucesso (click_rate, conversion_rate, etc.)

        Returns:
            ID do teste criado
        """
        
        test_id = generate_test_id()
        
        ab_test = {
            "id": test_id,
            "name": test_name,
            "variants": variants,
            "target_audience": target_audience,
            "duration_days": duration_days,
            "success_metric": success_metric,
            "status": "active",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=duration_days),
            "participants": {},
            "results": {}
        }
        
        # Salvar teste
        await save_ab_test(ab_test)
        
        # Carregar para cache
        self.active_tests[test_id] = ab_test
        
        return test_id

    async def assign_user_to_test(
        self,
        user_id: int,
        test_id: str,
        notification_context: Dict
    ) -> Optional[Dict]:
        """
        Atribui usuário a variante do teste.

        Args:
            user_id: ID do usuário
            test_id: ID do teste
            notification_context: Contexto da notificação

        Returns:
            Variante atribuída ou None se não aplicável
        """
        
        test = self.active_tests.get(test_id)
        if not test or test["status"] != "active":
            return None

        # Verificar se usuário está no público-alvo
        if not await self.user_matches_audience(user_id, test["target_audience"]):
            return None

        # Verificar se usuário já está no teste
        if str(user_id) in test["participants"]:
            variant_id = test["participants"][str(user_id)]
            return next(v for v in test["variants"] if v["id"] == variant_id)

        # Atribuir usuário a variante (distribuição igual)
        variant = random.choice(test["variants"])
        
        # Salvar atribuição
        test["participants"][str(user_id)] = variant["id"]
        await update_test_participants(test_id, test["participants"])

        return variant

    async def user_matches_audience(
        self, user_id: int, audience_criteria: Dict
    ) -> bool:
        """Verifica se usuário corresponde aos critérios do público-alvo."""
        
        user_profile = await get_user_profile(user_id)
        
        # Verificar cada critério
        for criterion, value in audience_criteria.items():
            user_value = user_profile.get(criterion)
            
            if isinstance(value, list):
                if user_value not in value:
                    return False
            elif isinstance(value, dict):
                # Range (ex: age: {"min": 18, "max": 65})
                if "min" in value and user_value < value["min"]:
                    return False
                if "max" in value and user_value > value["max"]:
                    return False
            else:
                if user_value != value:
                    return False
        
        return True

    async def track_test_event(
        self,
        user_id: int,
        test_id: str,
        variant_id: str,
        event_type: str,
        event_data: Optional[Dict] = None
    ):
        """Rastreia evento do teste A/B."""
        
        event = {
            "test_id": test_id,
            "user_id": user_id,
            "variant_id": variant_id,
            "event_type": event_type,
            "event_data": event_data or {},
            "timestamp": datetime.utcnow()
        }
        
        await save_test_event(event)

    async def analyze_test_results(self, test_id: str) -> Dict:
        """Analisa resultados do teste A/B."""
        
        test = await get_ab_test(test_id)
        if not test:
            return {"error": "Test not found"}

        # Buscar eventos do teste
        events = await get_test_events(test_id)
        
        # Calcular métricas por variante
        results = {}
        for variant in test["variants"]:
            variant_id = variant["id"]
            variant_events = [e for e in events if e["variant_id"] == variant_id]
            
            results[variant_id] = {
                "variant_name": variant["name"],
                "participants": len([p for p, v in test["participants"].items() if v == variant_id]),
                "total_events": len(variant_events),
                "metrics": self.calculate_variant_metrics(variant_events, test["success_metric"])
            }

        # Determinar variante vencedora
        winner = self.determine_winner(results, test["success_metric"])
        
        return {
            "test_id": test_id,
            "test_name": test["name"],
            "status": test["status"],
            "results": results,
            "winner": winner,
            "statistical_significance": self.calculate_significance(results)
        }

    def calculate_variant_metrics(
        self, events: List[Dict], success_metric: str
    ) -> Dict:
        """Calcula métricas para uma variante."""
        
        if not events:
            return {"click_rate": 0, "conversion_rate": 0, "engagement_rate": 0}

        sent_events = [e for e in events if e["event_type"] == "sent"]
        click_events = [e for e in events if e["event_type"] == "clicked"]
        conversion_events = [e for e in events if e["event_type"] == "converted"]

        total_sent = len(sent_events)
        
        metrics = {
            "click_rate": len(click_events) / total_sent if total_sent > 0 else 0,
            "conversion_rate": len(conversion_events) / total_sent if total_sent > 0 else 0,
            "engagement_rate": len([e for e in events if e["event_type"] in ["clicked", "opened"]]) / total_sent if total_sent > 0 else 0
        }

        return metrics

    def determine_winner(self, results: Dict, success_metric: str) -> Optional[str]:
        """Determina variante vencedora baseada na métrica de sucesso."""
        
        best_variant = None
        best_value = 0
        
        for variant_id, result in results.items():
            metric_value = result["metrics"].get(success_metric, 0)
            if metric_value > best_value:
                best_value = metric_value
                best_variant = variant_id
        
        return best_variant
```

## 🗃️ ESTRUTURAS DE DADOS

### 1. Notification Models
```python
# models/notifications/notification.py
from enum import Enum
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, Boolean, Float

class NotificationStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"

class NotificationType(Enum):
    SYSTEM = "system"
    BUSINESS = "business"
    MARKETING = "marketing"
    REMINDER = "reminder"
    URGENT = "urgent"

class Notification(Base):
    """Modelo base de notificação."""
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Integer, default=0)  # 0=baixa, 5=alta, 10=crítica
    
    # Conteúdo
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    html_body = Column(Text)
    image_url = Column(String(500))
    cta_text = Column(String(100))
    cta_url = Column(String(500))
    
    # Metadados
    data_payload = Column(JSON)
    personalization_data = Column(JSON)
    ab_test_id = Column(String, ForeignKey("ab_tests.id"))
    ab_variant_id = Column(String)
    
    # Timing e canal
    preferred_channel = Column(String(50))
    optimal_send_time = Column(DateTime)
    scheduled_for = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Status e métricas
    status = Column(Enum(NotificationStatus), default=NotificationStatus.DRAFT)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    engagement_score = Column(Float)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    deliveries = relationship("NotificationDelivery", back_populates="notification")

class NotificationDelivery(Base):
    """Log de entrega por canal."""
    __tablename__ = "notification_deliveries"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    notification_id = Column(String, ForeignKey("notifications.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    delivery_address = Column(String(500))  # email, phone, token, etc.
    
    # Status da entrega
    status = Column(Enum(NotificationStatus), nullable=False)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    failed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Métricas do canal
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    unsubscribed_at = Column(DateTime)
    
    # Metadados
    provider_id = Column(String(200))  # ID do provedor externo
    provider_response = Column(JSON)

    # Relacionamentos
    notification = relationship("Notification", back_populates="deliveries")

class NotificationTemplate(Base):
    """Templates de notificação."""
    __tablename__ = "notification_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(200), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    category = Column(String(100))
    
    # Template content
    title_template = Column(String(500), nullable=False)
    body_template = Column(Text, nullable=False)
    html_template = Column(Text)
    variables = Column(JSON)  # Lista de variáveis disponíveis
    
    # Configurações
    default_channel = Column(String(50))
    priority = Column(Integer, default=0)
    auto_personalize = Column(Boolean, default=True)
    
    # Metadados
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_engagement = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### 2. User Preferences Model
```python
# models/notifications/preferences.py
class NotificationPreferences(Base):
    """Preferências de notificação do usuário."""
    __tablename__ = "notification_preferences"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Preferências por canal
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)
    in_app_enabled = Column(Boolean, default=True)
    
    # Preferências por tipo
    system_notifications = Column(Boolean, default=True)
    business_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)
    reminder_notifications = Column(Boolean, default=True)
    urgent_notifications = Column(Boolean, default=True)
    
    # Timing preferences
    quiet_hours_start = Column(Time)  # Ex: 22:00
    quiet_hours_end = Column(Time)    # Ex: 08:00
    timezone = Column(String(50), default="UTC")
    preferred_days = Column(JSON)     # [1,2,3,4,5] = seg-sex
    
    # Frequência
    max_daily_notifications = Column(Integer, default=10)
    max_weekly_marketing = Column(Integer, default=2)
    digest_frequency = Column(String(20), default="daily")  # daily, weekly, off
    
    # Configurações avançadas
    ai_optimization = Column(Boolean, default=True)
    personalization = Column(Boolean, default=True)
    auto_unsubscribe_inactive = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="notification_preferences")

class NotificationSubscription(Base):
    """Inscrições específicas de notificação."""
    __tablename__ = "notification_subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(200), nullable=False)  # Ex: "lead_updates", "order_status"
    channel = Column(String(50), nullable=False)
    
    is_subscribed = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    unsubscribed_at = Column(DateTime)
    unsubscribe_reason = Column(String(200))
    
    # Configurações específicas
    frequency = Column(String(20), default="immediate")  # immediate, hourly, daily
    conditions = Column(JSON)  # Condições para envio
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = relationship("User")
```

## 🚀 IMPLEMENTAÇÃO

### Fase 1: Motor de Personalização (Sprint 1-2)
1. **Personalization Engine**
   - User profiling
   - Behavioral analysis
   - ML models para timing
   - Content personalization

2. **Basic Channels**
   - Push notifications
   - Email básico
   - In-app notifications
   - User preferences

### Fase 2: Multi-Channel (Sprint 3-4)
1. **Channel Expansion**
   - SMS integration
   - WhatsApp Business API
   - Slack/Teams integration
   - Rich email templates

2. **Scheduling System**
   - Optimal timing
   - Delivery scheduler
   - Retry mechanisms
   - Conflict resolution

### Fase 3: Intelligence Layer (Sprint 5)
1. **A/B Testing**
   - Test creation
   - User assignment
   - Results analysis
   - Auto-optimization

2. **Advanced Analytics**
   - Engagement tracking
   - Performance metrics
   - Predictive insights
   - ROI measurement

### Fase 4: Enterprise Features (Sprint 6)
1. **Advanced Features**
   - Workflow integration
   - Bulk operations
   - Advanced segmentation
   - Compliance tools

2. **Optimization**
   - Performance tuning
   - Cost optimization
   - Deliverability improvement
   - Mobile optimization

## 📊 MÉTRICAS E MONITORAMENTO

### Analytics Dashboard
```python
# analytics/notification_analytics.py
class NotificationAnalytics:
    """Analytics avançado de notificações."""

    def __init__(self):
        self.metrics_collector = MetricsCollector()

    async def get_engagement_metrics(
        self, 
        date_range: Tuple[datetime, datetime],
        filters: Optional[Dict] = None
    ) -> Dict:
        """Métricas de engajamento."""
        
        base_query = self.build_base_query(date_range, filters)
        
        metrics = {
            "overview": {
                "total_sent": await base_query.count(),
                "delivered_rate": await self.calculate_delivery_rate(base_query),
                "open_rate": await self.calculate_open_rate(base_query),
                "click_rate": await self.calculate_click_rate(base_query),
                "unsubscribe_rate": await self.calculate_unsubscribe_rate(base_query)
            },
            "by_channel": await self.get_channel_breakdown(base_query),
            "by_type": await self.get_type_breakdown(base_query),
            "by_hour": await self.get_hourly_breakdown(base_query),
            "personalization_impact": await self.analyze_personalization_impact(base_query)
        }
        
        return metrics

    async def analyze_user_journey(self, user_id: int) -> Dict:
        """Analisa jornada de notificações do usuário."""
        
        user_notifications = await self.get_user_notifications(user_id)
        
        journey = {
            "total_received": len(user_notifications),
            "engagement_timeline": self.build_engagement_timeline(user_notifications),
            "preferred_channels": self.analyze_channel_preferences(user_notifications),
            "optimal_timing": self.analyze_timing_patterns(user_notifications),
            "content_preferences": self.analyze_content_preferences(user_notifications),
            "engagement_score": self.calculate_user_engagement_score(user_notifications)
        }
        
        return journey

    async def generate_optimization_recommendations(self) -> List[Dict]:
        """Gera recomendações de otimização baseadas em dados."""
        
        recommendations = []
        
        # Análise de performance por canal
        channel_performance = await self.analyze_channel_performance()
        for channel, metrics in channel_performance.items():
            if metrics["click_rate"] < 0.02:  # Menos de 2%
                recommendations.append({
                    "type": "channel_optimization",
                    "priority": "high",
                    "channel": channel,
                    "issue": "Low click rate",
                    "recommendation": "Improve content relevance and CTA placement",
                    "expected_impact": "15-30% improvement in click rate"
                })
        
        # Análise de timing
        timing_analysis = await self.analyze_send_timing()
        if timing_analysis["suboptimal_percentage"] > 0.3:  # 30% fora do timing ideal
            recommendations.append({
                "type": "timing_optimization",
                "priority": "medium",
                "issue": "Suboptimal send timing",
                "recommendation": "Enable AI-powered send time optimization",
                "expected_impact": "10-20% improvement in open rates"
            })
        
        # Análise de personalização
        personalization_impact = await self.analyze_personalization_effectiveness()
        if personalization_impact["non_personalized_performance"] > personalization_impact["personalized_performance"]:
            recommendations.append({
                "type": "personalization",
                "priority": "high",
                "issue": "Personalization reducing performance",
                "recommendation": "Review personalization algorithms and data quality",
                "expected_impact": "Prevent 5-10% performance degradation"
            })
        
        return recommendations
```

### KPIs Principais
- **Delivery Rate:** > 99%
- **Open Rate:** > 25%
- **Click Rate:** > 5%
- **Unsubscribe Rate:** < 0.5%
- **Response Time:** < 30 segundos
- **Personalization Lift:** > 15%

## 🔒 COMPLIANCE E PRIVACIDADE

### LGPD/GDPR Compliance
```python
# compliance/notification_compliance.py
class NotificationComplianceManager:
    """Gerencia compliance de notificações."""

    def __init__(self):
        self.consent_manager = ConsentManager()
        self.data_processor = DataProcessor()

    async def verify_send_consent(
        self,
        user_id: int,
        notification_type: str,
        channel: str
    ) -> bool:
        """Verifica consentimento para envio."""
        
        # Verificar consentimento geral
        general_consent = await self.consent_manager.has_consent(
            user_id, "notifications"
        )
        if not general_consent:
            return False
        
        # Verificar consentimento específico do canal
        channel_consent = await self.consent_manager.has_consent(
            user_id, f"notifications_{channel}"
        )
        if not channel_consent:
            return False
        
        # Verificar consentimento do tipo (marketing requer opt-in explícito)
        if notification_type == "marketing":
            marketing_consent = await self.consent_manager.has_consent(
                user_id, "marketing_notifications"
            )
            if not marketing_consent:
                return False
        
        # Verificar se usuário não está em lista de supressão
        is_suppressed = await self.check_suppression_list(user_id, channel)
        if is_suppressed:
            return False
        
        return True

    async def process_unsubscribe_request(
        self,
        user_id: int,
        channel: Optional[str] = None,
        notification_type: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Processa solicitação de descadastro."""
        
        unsubscribe_data = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "channel": channel,
            "notification_type": notification_type,
            "reason": reason,
            "ip_address": request.client.host if request else None
        }
        
        if channel and notification_type:
            # Unsubscribe específico
            await self.consent_manager.revoke_consent(
                user_id, f"{notification_type}_{channel}"
            )
        elif channel:
            # Unsubscribe do canal
            await self.consent_manager.revoke_consent(
                user_id, f"notifications_{channel}"
            )
        else:
            # Unsubscribe geral
            await self.consent_manager.revoke_consent(
                user_id, "notifications"
            )
        
        # Adicionar à lista de supressão
        await self.add_to_suppression_list(unsubscribe_data)
        
        # Log para auditoria
        await self.log_unsubscribe_event(unsubscribe_data)

    async def generate_data_export(self, user_id: int) -> Dict:
        """Gera export de dados para LGPD/GDPR."""
        
        user_data = {
            "user_id": user_id,
            "preferences": await get_user_notification_preferences(user_id),
            "subscriptions": await get_user_subscriptions(user_id),
            "consents": await self.consent_manager.get_user_consents(user_id),
            "notification_history": await get_user_notification_history(user_id),
            "engagement_data": await get_user_engagement_data(user_id),
            "suppression_records": await get_user_suppression_records(user_id)
        }
        
        return user_data

    async def anonymize_user_data(self, user_id: int):
        """Anonimiza dados do usuário conforme LGPD."""
        
        # Anonimizar preferências
        await anonymize_notification_preferences(user_id)
        
        # Anonimizar histórico (manter métricas agregadas)
        await anonymize_notification_history(user_id)
        
        # Anonimizar logs de engajamento
        await anonymize_engagement_data(user_id)
        
        # Manter dados necessários para compliance
        await mark_user_as_anonymized(user_id)
```

## 📋 CHECKLIST DE ENTREGA

### ✅ Backend Core
- [ ] Personalization Engine implementado
- [ ] Multi-Channel Dispatcher
- [ ] Template Manager
- [ ] Scheduling System
- [ ] A/B Testing Engine
- [ ] Analytics Engine
- [ ] Compliance Manager
- [ ] Delivery Tracking
- [ ] Error Handling & Retry

### ✅ Channel Integration
- [ ] Push Notifications (Firebase/APNS)
- [ ] Email (SMTP/SendGrid)
- [ ] SMS (Twilio/AWS SNS)
- [ ] WhatsApp Business API
- [ ] In-App Notifications
- [ ] Slack Integration
- [ ] Teams Integration
- [ ] Rich Media Support

### ✅ Frontend Components
- [ ] Notification Center
- [ ] Preferences Dashboard
- [ ] Template Editor
- [ ] Campaign Manager
- [ ] Analytics Dashboard
- [ ] A/B Test Manager
- [ ] User Journey Visualization
- [ ] Mobile Notifications UI

### ✅ Machine Learning
- [ ] Timing Optimization Model
- [ ] Channel Selection Model
- [ ] Content Personalization
- [ ] Engagement Prediction
- [ ] Churn Prevention
- [ ] Sentiment Analysis
- [ ] Performance Forecasting
- [ ] Auto-optimization

## 🎯 CRITÉRIOS DE SUCESSO

### Performance Metrics
- Delivery rate > 99%
- Open rate > 25%
- Click rate > 5%
- Response time < 30s
- 99.9% uptime

### User Experience
- Unsubscribe rate < 0.5%
- User satisfaction > 4.2/5
- Preference adoption > 80%
- Mobile optimization score > 95

### Business Impact
- 40% increase in user engagement
- 25% increase in conversion rates
- 30% reduction in spam complaints
- 50% improvement in notification relevance
- ROI > 300%

### AI Effectiveness
- Personalization lift > 15%
- Timing optimization lift > 12%
- Channel optimization lift > 10%
- Predictive accuracy > 85%

---

**📅 Duração Estimada:** 6 sprints (12 semanas)
**👥 Equipe Necessária:** 3 desenvolvedores full-stack + 1 ML engineer + 1 mobile developer
**💰 Investimento:** R$ 200.000 - R$ 280.000
**🚀 Impacto Esperado:** Sistema de notificações inteligentes de classe mundial com IA avançada e compliance total
