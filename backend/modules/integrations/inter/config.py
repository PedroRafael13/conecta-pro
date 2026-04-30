"""D6 — Configurações e constantes do módulo Inter."""

import os

# URLs produção (confirmadas 30/04/2026)
INTER_TOKEN_URL = "https://cdpj.partners.bancointer.com.br/oauth/v2/token"
INTER_BANKING_URL = "https://cdpj.partners.bancointer.com.br/banking/v2"
INTER_COBRANCA_URL = "https://cdpj.partners.bancointer.com.br/cobranca/v3"
INTER_PIX_URL = "https://cdpj.partners.bancointer.com.br/pix/v2"

# Cache Redis
INTER_REDIS_TOKEN_KEY = "inter:token"
INTER_REDIS_TOKEN_TTL = 50 * 60  # 50 min (token vale 1h)
INTER_REDIS_SALDO_LOCK_KEY = "inter:saldo:lock"
INTER_REDIS_SALDO_LOCK_TTL = 5  # 5 segundos

# Credenciais (via .env)
INTER_CLIENT_ID = os.getenv("INTER_CLIENT_ID", "")
INTER_CLIENT_SECRET = os.getenv("INTER_CLIENT_SECRET", "")
INTER_CERT_PATH = os.getenv("INTER_CERT_PATH", "/app/credentials/inter/certificate.crt")
INTER_KEY_PATH = os.getenv("INTER_KEY_PATH", "/app/credentials/inter/private.key")
INTER_AGENCY = os.getenv("INTER_AGENCY", "")
INTER_ACCOUNT = os.getenv("INTER_ACCOUNT", "")
INTER_ENVIRONMENT = os.getenv("INTER_ENVIRONMENT", "production")

# Scopes habilitados
INTER_SCOPES = [
    "extrato.read",
    "boleto-cobranca.read",
    "boleto-cobranca.write",
    "pagamento-pix.read",
    "pagamento-boleto.read",
    "cob.read",
    "cob.write",
]
