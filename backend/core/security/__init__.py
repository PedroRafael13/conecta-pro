"""Security module - Rate limiting e seguranca."""

# PATCH 04: Log Masking
from core.security.log_masking import LogMasker, SecureLogFilter, mask_sensitive_data
from core.security.rate_limiter import RateLimiter, RateLimitMiddleware, rate_limiter

# PATCH 02: SQL Injection Validator
from core.security.sql_validator import InvalidTableError, SQLTableValidator, validate_table_name

__all__ = [
    "RateLimiter",
    "RateLimitMiddleware",
    "rate_limiter",
    # SQL Injection Protection
    "SQLTableValidator",
    "validate_table_name",
    "InvalidTableError",
    # Log Masking
    "LogMasker",
    "SecureLogFilter",
    "mask_sensitive_data",
]
