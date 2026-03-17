"""
Servico de Autenticacao do Portal do Cliente.

Gerencia login, validacao de token JWT, refresh e logout
para clientes externos que acessam o portal de kits documentais.
"""

import logging
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.client_portal.models.session import ClientPortalSession
from modules.client_portal.schemas.auth import PortalLoginResponse
from modules.people_management.ged.models.client import GedClient

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("PORTAL_SECRET_KEY", "conecta-portal-secret-key-change-me")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PortalAuthService:
    """Servico de autenticacao para o portal do cliente.

    Gerencia o ciclo completo de autenticacao: login com username/password,
    emissao de JWT, validacao, refresh e invalidacao (logout).
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def login(
        self,
        username: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> PortalLoginResponse:
        """Autentica um cliente pelo username e senha do portal.

        Args:
            username: Login do portal do cliente.
            password: Senha em texto plano para verificacao.
            ip_address: IP do cliente para registro na sessao.
            user_agent: User-Agent do navegador do cliente.

        Returns:
            PortalLoginResponse com token JWT e dados do cliente.

        Raises:
            ValueError: Se credenciais invalidas ou acesso desabilitado.
        """
        result = await self.db.execute(select(GedClient).where(GedClient.portal_username == username))
        client = result.scalar_one_or_none()

        if not client:
            logger.warning("Tentativa de login com username inexistente: %s", username)
            raise ValueError("Credenciais invalidas")

        if not client.portal_access_enabled:
            logger.warning(
                "Tentativa de login com acesso desabilitado: %s (client_id=%s)",
                username,
                client.id,
            )
            raise ValueError("Acesso ao portal desabilitado para este cliente")

        if not client.portal_password_hash:
            logger.warning(
                "Cliente sem senha configurada: %s (client_id=%s)",
                username,
                client.id,
            )
            raise ValueError("Credenciais invalidas")

        if not self.verify_password(password, client.portal_password_hash):
            logger.warning(
                "Senha incorreta para username: %s (client_id=%s)",
                username,
                client.id,
            )
            raise ValueError("Credenciais invalidas")

        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=TOKEN_EXPIRY_HOURS)

        token_payload = {
            "sub": str(client.id),
            "username": username,
            "type": "portal",
            "iat": now.timestamp(),
            "exp": expires_at.timestamp(),
            "jti": str(uuid4()),
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

        session = ClientPortalSession(
            client_id=str(client.id),
            token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True,
        )
        self.db.add(session)
        await self.db.flush()

        logger.info(
            "Login portal bem-sucedido: %s (client_id=%s, session_id=%s)",
            username,
            client.id,
            session.id,
        )

        return PortalLoginResponse(
            access_token=token,
            token_type="bearer",
            expires_at=expires_at,
            client_id=str(client.id),
            client_name=client.name,
        )

    async def validate_token(self, token: str) -> str:
        """Valida um token JWT e retorna o client_id.

        Args:
            token: Token JWT a ser validado.

        Returns:
            client_id (str) do cliente autenticado.

        Raises:
            ValueError: Se token invalido, expirado ou sessao inativa.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token invalido")

        if payload.get("type") != "portal":
            raise ValueError("Token invalido para o portal")

        client_id = payload.get("sub")
        if not client_id:
            raise ValueError("Token invalido: sem identificacao do cliente")

        result = await self.db.execute(
            select(ClientPortalSession).where(
                ClientPortalSession.token == token,
                ClientPortalSession.is_active.is_(True),
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("Sessao nao encontrada ou inativa")

        now = datetime.now(UTC)
        if session.expires_at.replace(tzinfo=UTC) < now:
            session.is_active = False
            await self.db.flush()
            raise ValueError("Sessao expirada")

        return client_id

    async def refresh_token(
        self,
        current_token: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> PortalLoginResponse:
        """Renova um token JWT gerando uma nova sessao.

        Invalida a sessao atual e cria uma nova com novo token.

        Args:
            current_token: Token JWT atual para renovacao.
            ip_address: IP do cliente.
            user_agent: User-Agent do navegador.

        Returns:
            PortalLoginResponse com novo token JWT.

        Raises:
            ValueError: Se token atual invalido.
        """
        client_id = await self.validate_token(current_token)

        await self.db.execute(
            update(ClientPortalSession).where(ClientPortalSession.token == current_token).values(is_active=False)
        )

        result = await self.db.execute(select(GedClient).where(GedClient.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise ValueError("Cliente nao encontrado")

        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=TOKEN_EXPIRY_HOURS)

        token_payload = {
            "sub": str(client.id),
            "username": client.portal_username,
            "type": "portal",
            "iat": now.timestamp(),
            "exp": expires_at.timestamp(),
            "jti": str(uuid4()),
        }
        new_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

        session = ClientPortalSession(
            client_id=str(client.id),
            token=new_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True,
        )
        self.db.add(session)
        await self.db.flush()

        logger.info(
            "Token portal renovado: client_id=%s, session_id=%s",
            client.id,
            session.id,
        )

        return PortalLoginResponse(
            access_token=new_token,
            token_type="bearer",
            expires_at=expires_at,
            client_id=str(client.id),
            client_name=client.name,
        )

    async def logout(self, token: str) -> dict:
        """Invalida a sessao atual do cliente.

        Args:
            token: Token JWT a ser invalidado.

        Returns:
            Confirmacao do logout.
        """
        result = await self.db.execute(
            update(ClientPortalSession)
            .where(
                ClientPortalSession.token == token,
                ClientPortalSession.is_active.is_(True),
            )
            .values(is_active=False)
        )

        if result.rowcount == 0:
            logger.warning("Tentativa de logout com token invalido ou ja inativo")
            return {"message": "Sessao ja estava inativa"}

        logger.info("Logout portal realizado com sucesso")
        return {"message": "Logout realizado com sucesso"}

    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash bcrypt de uma senha.

        Args:
            password: Senha em texto plano.

        Returns:
            Hash bcrypt da senha.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se uma senha corresponde ao hash armazenado.

        Args:
            plain_password: Senha em texto plano.
            hashed_password: Hash bcrypt armazenado.

        Returns:
            True se a senha corresponde, False caso contrario.
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            logger.warning("Erro ao verificar senha — hash possivelmente corrompido")
            return False
