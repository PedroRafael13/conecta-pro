"""Serviço de segurança mobile."""

import hashlib
import hmac
import logging
import re
import time
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.mobile.models.device_token import DeviceToken
from modules.mobile.models.mobile_session import MobileSession

logger = logging.getLogger(__name__)


class RateLimitExceededError(Exception):
    """Exceção para rate limit excedido."""

    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class MobileSecurity:
    """
    Serviço de segurança para API mobile.

    Funcionalidades:
    - Rate limiting por dispositivo/usuário
    - Validação de API key mobile
    - Certificate pinning validation
    - Device fingerprint verification
    - Detecção de dispositivo root/jailbreak
    - Anti-tampering checks
    """

    # Rate limits por tipo de operação
    RATE_LIMITS = {
        "default": {"requests": 100, "window": 60},  # 100 req/min
        "sync": {"requests": 10, "window": 60},  # 10 sync/min
        "notification": {"requests": 50, "window": 60},  # 50/min
        "auth": {"requests": 5, "window": 300},  # 5 tentativas/5min
        "batch": {"requests": 20, "window": 60},  # 20 batch/min
    }

    # Padrões suspeitos em user agents
    SUSPICIOUS_UA_PATTERNS = [
        r"python-requests",
        r"curl",
        r"wget",
        r"postman",
        r"insomnia",
        r"httpie",
        r"scrapy",
    ]

    def __init__(
        self,
        api_key_secret: str,
        enable_strict_mode: bool = False,
        allow_rooted_devices: bool = True,
    ) -> None:
        """
        Inicializa o serviço de segurança.

        Args:
            api_key_secret: Segredo para validação de API key
            enable_strict_mode: Modo estrito (bloqueia suspeitos)
            allow_rooted_devices: Permitir dispositivos root/jailbreak
        """
        self.api_key_secret = api_key_secret
        self.strict_mode = enable_strict_mode
        self.allow_rooted = allow_rooted_devices

        # Cache de rate limits (em produção usar Redis)
        self._rate_limit_cache: dict[str, dict] = {}

        # Compilar patterns
        self._suspicious_ua_re = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_UA_PATTERNS]

    async def validate_request(
        self,
        request: Request,
        db: AsyncSession,
        operation_type: str = "default",
    ) -> dict[str, Any]:
        """
        Valida requisição mobile.

        Args:
            request: Requisição HTTP
            db: Sessão do banco
            operation_type: Tipo de operação para rate limit

        Returns:
            Dict com informações de segurança

        Raises:
            HTTPException: Se validação falhar
        """
        # Extrair headers de segurança
        security_headers = self._extract_security_headers(request)

        # Validar API key mobile
        if not await self._validate_api_key(security_headers.get("api_key")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid mobile API key",
            )

        # Verificar rate limit
        rate_key = self._get_rate_limit_key(request, security_headers)
        if not await self._check_rate_limit(rate_key, operation_type):
            limit_config = self.RATE_LIMITS.get(operation_type, self.RATE_LIMITS["default"])
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(limit_config["window"])},
            )

        # Verificar user agent suspeito
        if self.strict_mode and self._is_suspicious_ua(request):
            logger.warning(f"Suspicious UA detected: {request.headers.get('user-agent')}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Verificar dispositivo root/jailbreak
        if not self.allow_rooted and security_headers.get("is_rooted"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rooted/jailbroken devices not allowed",
            )

        # Verificar integridade do app
        if not await self._verify_app_integrity(security_headers):
            logger.warning(f"App integrity check failed for device {security_headers.get('device_id')}")
            if self.strict_mode:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="App integrity verification failed",
                )

        # Verificar device fingerprint se disponível
        device_id = security_headers.get("device_id")
        if device_id:
            await self._verify_device_fingerprint(db, device_id, security_headers)

        return {
            "device_id": device_id,
            "platform": security_headers.get("platform"),
            "app_version": security_headers.get("app_version"),
            "is_trusted": True,
            "security_level": self._calculate_security_level(security_headers),
        }

    def _extract_security_headers(self, request: Request) -> dict[str, Any]:
        """Extrai headers de segurança da requisição."""
        headers = dict(request.headers)

        return {
            "api_key": headers.get("x-mobile-api-key"),
            "device_id": headers.get("x-device-id"),
            "platform": headers.get("x-platform"),
            "app_version": headers.get("x-app-version"),
            "app_signature": headers.get("x-app-signature"),
            "device_fingerprint": headers.get("x-device-fingerprint"),
            "is_rooted": headers.get("x-is-rooted") == "true",
            "is_emulator": headers.get("x-is-emulator") == "true",
            "install_source": headers.get("x-install-source"),
            "timestamp": headers.get("x-request-timestamp"),
            "nonce": headers.get("x-request-nonce"),
            "signature": headers.get("x-request-signature"),
        }

    async def _validate_api_key(self, api_key: str | None) -> bool:
        """Valida API key mobile."""
        if not api_key:
            return False

        # Validar formato (minimo 10 chars para key_id.signature)
        if len(api_key) < 10:
            return False

        # Verificar assinatura HMAC
        try:
            parts = api_key.split(".")
            if len(parts) != 2:
                return False

            key_id, signature = parts
            expected = hmac.new(
                self.api_key_secret.encode(),
                key_id.encode(),
                hashlib.sha256,
            ).hexdigest()[:16]

            return hmac.compare_digest(signature, expected)

        except Exception:
            return False

    def _get_rate_limit_key(
        self,
        request: Request,
        security_headers: dict,
    ) -> str:
        """Gera chave para rate limiting."""
        # Priorizar device_id, depois IP
        device_id = security_headers.get("device_id")
        if device_id:
            return f"device:{device_id}"

        # Fallback para IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def _check_rate_limit(
        self,
        key: str,
        operation_type: str,
    ) -> bool:
        """Verifica rate limit para chave/operação."""
        config = self.RATE_LIMITS.get(operation_type, self.RATE_LIMITS["default"])
        max_requests = config["requests"]
        window = config["window"]

        full_key = f"{key}:{operation_type}"
        now = time.time()

        # Obter ou criar entry no cache
        if full_key not in self._rate_limit_cache:
            self._rate_limit_cache[full_key] = {
                "count": 0,
                "window_start": now,
            }

        entry = self._rate_limit_cache[full_key]

        # Resetar janela se expirou
        if now - entry["window_start"] > window:
            entry["count"] = 0
            entry["window_start"] = now

        # Verificar limite
        if entry["count"] >= max_requests:
            return False

        # Incrementar contador
        entry["count"] += 1
        return True

    def _is_suspicious_ua(self, request: Request) -> bool:
        """Verifica se user agent é suspeito."""
        ua = request.headers.get("user-agent", "")

        for pattern in self._suspicious_ua_re:
            if pattern.search(ua):
                return True

        # Verificar se é app oficial
        if not any(x in ua for x in ["ConectaPRO-Android", "ConectaPRO-iOS"]):
            return True

        return False

    async def _verify_app_integrity(self, security_headers: dict) -> bool:
        """Verifica integridade do app."""
        # Verificar assinatura do app
        app_signature = security_headers.get("app_signature")
        if not app_signature:
            return True  # Não obrigatório por enquanto

        platform = security_headers.get("platform", "").lower()

        # Assinaturas válidas do app (em produção, carregar de config)
        valid_signatures = {
            "android": [
                "SHA256:XX:XX:XX...",  # Assinatura de release
                "SHA256:YY:YY:YY...",  # Assinatura de debug
            ],
            "ios": [
                "TEAM_ID.com.conectapro.app",
            ],
        }

        platform_signatures = valid_signatures.get(platform, [])

        # Em desenvolvimento, aceitar qualquer assinatura
        if not platform_signatures:
            return True

        return app_signature in platform_signatures

    async def _verify_device_fingerprint(
        self,
        db: AsyncSession,
        device_id: str,
        security_headers: dict,
    ) -> bool:
        """Verifica fingerprint do dispositivo."""
        fingerprint = security_headers.get("device_fingerprint")
        if not fingerprint:
            return True

        # Buscar tokens do dispositivo
        query = select(DeviceToken).where(
            DeviceToken.device_id == device_id,
            DeviceToken.is_active,
        )
        result = await db.execute(query)
        token = result.scalar_one_or_none()

        if not token:
            return True  # Dispositivo novo, ok

        # Verificar se fingerprint mudou significativamente
        # (implementar lógica de similaridade se necessário)

        return True

    def _calculate_security_level(self, security_headers: dict) -> str:
        """Calcula nível de segurança do dispositivo."""
        score = 100

        # Penalidades
        if security_headers.get("is_rooted"):
            score -= 30

        if security_headers.get("is_emulator"):
            score -= 20

        if not security_headers.get("app_signature"):
            score -= 10

        if not security_headers.get("device_fingerprint"):
            score -= 10

        # Install source
        install_source = security_headers.get("install_source", "")
        if install_source not in ["play_store", "app_store"]:
            score -= 15

        # Determinar nível
        if score >= 90:
            return "high"
        elif score >= 70:
            return "medium"
        elif score >= 50:
            return "low"
        else:
            return "critical"

    def generate_mobile_api_key(self, key_id: str) -> str:
        """
        Gera API key para app mobile.

        Args:
            key_id: Identificador único da chave

        Returns:
            API key no formato "key_id.signature"
        """
        signature = hmac.new(
            self.api_key_secret.encode(),
            key_id.encode(),
            hashlib.sha256,
        ).hexdigest()[:16]

        return f"{key_id}.{signature}"

    def generate_request_signature(
        self,
        method: str,
        path: str,
        timestamp: str,
        nonce: str,
        body: str | None = None,
    ) -> str:
        """
        Gera assinatura de requisição para validação.

        Args:
            method: Método HTTP
            path: Path da requisição
            timestamp: Timestamp da requisição
            nonce: Nonce único
            body: Corpo da requisição (opcional)

        Returns:
            Assinatura HMAC
        """
        data = f"{method}|{path}|{timestamp}|{nonce}"
        if body:
            data += f"|{hashlib.sha256(body.encode()).hexdigest()}"

        return hmac.new(
            self.api_key_secret.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()

    def validate_request_signature(
        self,
        request: Request,
        security_headers: dict,
        max_age_seconds: int = 300,
    ) -> bool:
        """
        Valida assinatura da requisição.

        Args:
            request: Requisição HTTP
            security_headers: Headers de segurança
            max_age_seconds: Idade máxima da requisição

        Returns:
            True se válida
        """
        timestamp = security_headers.get("timestamp")
        nonce = security_headers.get("nonce")
        signature = security_headers.get("signature")

        if not all([timestamp, nonce, signature]):
            return False

        # Verificar idade
        try:
            req_time = float(timestamp)
            if abs(time.time() - req_time) > max_age_seconds:
                return False
        except ValueError:
            return False

        # TODO: Verificar nonce não foi usado (requer Redis)

        # Calcular assinatura esperada
        # (simplificado, em produção incluir body)
        expected = self.generate_request_signature(
            request.method,
            str(request.url.path),
            timestamp,
            nonce,
        )

        return hmac.compare_digest(signature, expected)

    async def log_security_event(
        self,
        db: AsyncSession,
        event_type: str,
        device_id: str | None,
        user_id: int | None,
        details: dict,
        severity: str = "info",
    ) -> None:
        """
        Registra evento de segurança.

        Args:
            db: Sessão do banco
            event_type: Tipo do evento
            device_id: ID do dispositivo
            user_id: ID do usuário
            details: Detalhes do evento
            severity: Severidade (info, warning, error, critical)
        """
        logger.log(
            logging.INFO if severity == "info" else logging.WARNING if severity == "warning" else logging.ERROR,
            f"Security event: {event_type} | device={device_id} | user={user_id} | details={details}",
        )

        # TODO: Persistir em tabela de audit log

    async def revoke_device(
        self,
        db: AsyncSession,
        device_id: str,
        reason: str,
    ) -> bool:
        """
        Revoga acesso de um dispositivo.

        Args:
            db: Sessão do banco
            device_id: ID do dispositivo
            reason: Motivo da revogação

        Returns:
            True se dispositivo foi revogado
        """
        # Desativar tokens
        query = (
            update(DeviceToken)
            .where(DeviceToken.device_id == device_id)
            .values(
                is_active=False,
                push_enabled=False,
            )
        )
        result = await db.execute(query)

        # Invalidar sessões
        session_query = update(MobileSession).where(MobileSession.device_id == device_id).values(is_active=False)
        await db.execute(session_query)

        await db.commit()

        logger.warning(f"Device revoked: {device_id} | reason: {reason}")

        return result.rowcount > 0

    def get_security_recommendations(
        self,
        security_level: str,
        security_headers: dict,
    ) -> list[str]:
        """
        Gera recomendações de segurança para o dispositivo.

        Args:
            security_level: Nível de segurança atual
            security_headers: Headers de segurança

        Returns:
            Lista de recomendações
        """
        recommendations = []

        if security_headers.get("is_rooted"):
            recommendations.append("Your device is rooted/jailbroken. This may expose your data to security risks.")

        if security_headers.get("is_emulator"):
            recommendations.append("Running on emulator detected. For best security, use a physical device.")

        if not security_headers.get("app_signature"):
            recommendations.append("App signature verification not available. Please update to the latest version.")

        install_source = security_headers.get("install_source", "")
        if install_source not in ["play_store", "app_store"]:
            recommendations.append(
                "App was not installed from official store. "
                "Download from Google Play or App Store for updates and security."
            )

        if security_level in ["low", "critical"]:
            recommendations.append("Your security level is low. Please review and update your device settings.")

        return recommendations
