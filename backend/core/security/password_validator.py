"""
Validador de força de senha.

Implementa regras robustas de validação de senha incluindo:
- Comprimento mínimo de 12 caracteres
- Requisito de maiúsculas, minúsculas, números e caracteres especiais
- Verificação contra lista de senhas comuns (PT-BR + EN)
"""

import re

SPECIAL_CHARACTERS = set("!@#$%^&*()_+-=[]{}|;:,.<>?/~`")

# Top 100 senhas comuns (EN + PT-BR) - não expor em logs
COMMON_PASSWORDS: frozenset[str] = frozenset(
    {
        # EN top passwords
        "password",
        "123456",
        "12345678",
        "qwerty",
        "abc123",
        "monkey",
        "1234567",
        "letmein",
        "trustno1",
        "dragon",
        "baseball",
        "iloveyou",
        "master",
        "sunshine",
        "ashley",
        "bailey",
        "shadow",
        "123123",
        "654321",
        "superman",
        "qazwsx",
        "michael",
        "football",
        "password1",
        "password123",
        "batman",
        "login",
        "welcome",
        "admin",
        "princess",
        "starwars",
        "passw0rd",
        "hello",
        "charlie",
        "donald",
        "access",
        "thunderbird",
        "mustang",
        "cheese",
        "robert",
        "jordan",
        "summer",
        "taylor",
        "thomas",
        "andrew",
        "harley",
        "daniel",
        "hannah",
        "george",
        "william",
        # PT-BR top passwords
        "senha",
        "senha123",
        "senha1234",
        "mudar123",
        "mudar",
        "brasil",
        "flamengo",
        "palmeiras",
        "corinthians",
        "santos",
        "amor",
        "amorzinho",
        "familia",
        "deus",
        "jesus",
        "felicidade",
        "saudade",
        "liberdade",
        "sucesso",
        "vitoria",
        "gabriel",
        "lucas",
        "mateus",
        "pedro",
        "maria",
        "joao",
        "ana",
        "julia",
        "rafael",
        "fernando",
        "carlos",
        "marcos",
        "paulo",
        "andre",
        "felipe",
        "campeao",
        "futebol",
        "gremio",
        "vasco",
        "cruzeiro",
        "botafogo",
        "atletico",
        "bahia",
        "sport",
        "inter",
        "conecta",
        "admin123",
        "sistema",
        "teste",
        "teste123",
    }
)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Valida a força de uma senha.

    Args:
        password: Senha a ser validada.

    Returns:
        Tupla (is_valid, errors) onde errors é uma lista de mensagens
        descrevendo os problemas encontrados. Lista vazia = senha válida.
    """
    errors: list[str] = []

    if len(password) < 12:
        errors.append("Senha deve ter pelo menos 12 caracteres")

    if not any(c.isupper() for c in password):
        errors.append("Senha deve conter pelo menos uma letra maiúscula")

    if not any(c.islower() for c in password):
        errors.append("Senha deve conter pelo menos uma letra minúscula")

    if not any(c.isdigit() for c in password):
        errors.append("Senha deve conter pelo menos um número")

    if not any(c in SPECIAL_CHARACTERS for c in password):
        errors.append("Senha deve conter pelo menos um caractere especial (!@#$%^&*()_+-=[]{}|;:,.<>?/~`)")

    if password.lower() in COMMON_PASSWORDS:
        errors.append("Senha está na lista de senhas comuns e não pode ser utilizada")

    # Detectar sequências repetidas (ex: aaaa, 1111)
    if re.search(r"(.)\1{3,}", password):
        errors.append("Senha não pode conter 4 ou mais caracteres repetidos consecutivos")

    return (len(errors) == 0, errors)
