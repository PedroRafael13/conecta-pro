"""Security module - Rate limiting, validação e segurança."""

# PATCH 04: Log Masking
# PATCH 06: File Validator
from core.security.file_validator import FileValidationError, FileValidator
from core.security.log_masking import LogMasker, SecureLogFilter, mask_sensitive_data

# PATCH 05: Password Validator
from core.security.password_validator import validate_password_strength
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
    # Password Validation
    "validate_password_strength",
    # File Validation
    "FileValidator",
    "FileValidationError",
]
