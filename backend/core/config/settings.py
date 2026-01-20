"""
Configurações centralizadas do ERP Conecta Mais.
Usa pydantic-settings para validação e carregamento de variáveis de ambiente.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # App
    app_name: str = Field(default="ERP Conecta Mais")
    app_version: str = Field(default="2.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # Server
    host: str = Field(default="127.0.0.1")  # Use HOST=0.0.0.0 em produção via env
    port: int = Field(default=8080)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/erp_conecta_mais"
    )
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/1")
    redis_ttl: int = Field(default=3600)

    # JWT
    jwt_secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)

    # CORS - usa string para evitar problemas de parsing
    cors_origins_str: str = Field(default="http://localhost:3000", alias="cors_origins")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = Field(default="https://erp.conectamais.pro/api/v1/auth/google/callback")
    FRONTEND_URL: str = Field(default="https://erp.conectamais.pro")

    @property
    def cors_origins(self) -> List[str]:
        """Retorna lista de CORS origins parseada."""
        if isinstance(self.cors_origins_str, str):
            return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
        return ["http://localhost:3000"]

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v, info):
        """Valida que JWT secret tem tamanho adequado em produção."""
        if info.data.get("environment") == "production" and len(v) < 32:
            raise ValueError("JWT secret deve ter pelo menos 32 caracteres em produção")
        return v


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


settings = get_settings()
