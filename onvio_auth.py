#!/usr/bin/env python3
"""
GEDEON Fase 3 — Onvio Headless Auth via HTTP (sem Playwright)

Fluxo OIDC completo:
  1. POST /api/security/v1/oidc/login  → URL Auth0 (auth.thomsonreuters.com)
  2. GET  identifier page              → form com state
  3. POST email (username step)        → redireciona para password
  4. POST senha (password step)        → redireciona para MFA
  5. POST MFA via email OTP            → IMAP lê código do inbox
  6. Salva cookies no Redis (TTL 16h)

Config:
  IMAP_PASSWORD: senha do inbox de ONVIO_EMAIL no imap.titan.email
  Se vazio, entra em modo interativo (pede código na stdin).

Seletores e endpoints confirmados por inspeção real (2026-04-17):
  - POST body: {"type":"clientcenter","sp":"clientcenter","lang":"pt-BR",
                "redirectUri":"https://onvio.com.br/clientcenter/pt/"}
  - MFA email trigger: POST mfa-login-options com action=email::1
  - OTP input name: code
"""
import json, sys, time, imaplib, email, re, ssl
from datetime import datetime

import redis
import requests
from bs4 import BeautifulSoup

# ── Configuração ─────────────────────────────────────────────────────────────

ONVIO_URL    = "https://onvio.com.br/clientcenter/pt/auth"
ONVIO_EMAIL  = "administracao@conectamaistech.com.br"
ONVIO_PASS   = "Jordan0612*"

# IMAP para leitura automática do código MFA via e-mail
IMAP_SERVER   = "imap.titan.email"
IMAP_PORT     = 993
IMAP_PASSWORD = ""  # TODO: preencher com a senha do inbox IMAP

REDIS_KEY  = "onvio:session"
REDIS_TTL  = 57600  # 16 horas
REDIS_URL  = "redis://:15e1eeedc382272306a6aeef092dbd92c9b1ea73eb99067567a144812094da1b4db0ce7b7654a31584e4a2d3fc1a43f4@172.18.0.4:6379/1"

# ── HTTP Session ──────────────────────────────────────────────────────────────

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _soup(r: requests.Response) -> BeautifulSoup:
    return BeautifulSoup(r.text, "html.parser")


def _state(soup: BeautifulSoup) -> str:
    inp = soup.find("input", {"name": "state"})
    if not inp:
        raise RuntimeError("State input não encontrado na página")
    return inp["value"]


def _read_otp_from_imap(timeout_s: int = 90) -> str | None:
    """Lê o código OTP do email de MFA via IMAP. Retorna None se não encontrar."""
    if not IMAP_PASSWORD:
        return None

    deadline = time.time() + timeout_s
    print("  [IMAP] Aguardando email OTP...")

    while time.time() < deadline:
        try:
            ctx = ssl.create_default_context()
            imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ctx)
            imap.login(ONVIO_EMAIL, IMAP_PASSWORD)
            imap.select("INBOX")
            _, msgs = imap.search(None, 'UNSEEN FROM "thomsonreuters.com"')
            ids = msgs[0].split()
            if ids:
                _, data = imap.fetch(ids[-1], "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                # Procura código de 6 dígitos
                codes = re.findall(r"\b(\d{6})\b", body)
                if codes:
                    imap.logout()
                    print(f"  [IMAP] Código encontrado: {codes[0]}")
                    return codes[0]
            imap.logout()
        except Exception as e:
            print(f"  [IMAP] Erro: {e}")

        time.sleep(5)

    return None


# ── Auth Flow ─────────────────────────────────────────────────────────────────

def login_onvio() -> dict:
    s = _SESSION

    # STEP 1 — página inicial (obtém cookies de sessão)
    print("[1/6] Carregando página de auth Onvio...")
    s.headers["Accept"] = "text/html,application/xhtml+xml,*/*"
    s.get(ONVIO_URL, timeout=30)

    # STEP 2 — POST OIDC para obter URL Auth0
    print("[2/6] Iniciando OIDC login...")
    s.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://onvio.com.br",
        "Referer": ONVIO_URL,
    })
    r2 = s.post(
        "https://onvio.com.br/api/security/v1/oidc/login",
        json={
            "type": "clientcenter",
            "sp": "clientcenter",
            "lang": "pt-BR",
            "redirectUri": "https://onvio.com.br/clientcenter/pt/",
        },
        allow_redirects=False,
        timeout=30,
    )
    auth0_url = r2.headers.get("location") or r2.headers.get("Location")
    if not auth0_url:
        raise RuntimeError(f"OIDC login falhou: {r2.status_code} — {r2.text[:200]}")
    print(f"  Auth0 URL obtida ✅")

    # STEP 3 — GET página de identificador Auth0
    print("[3/6] Carregando página de login Auth0...")
    s.headers.update({"Accept": "text/html,application/xhtml+xml,*/*", "Referer": "https://onvio.com.br/"})
    r3 = s.get(auth0_url, timeout=30)
    soup3 = _soup(r3)
    state = _state(soup3)
    login_url = r3.url

    # STEP 4 — POST email
    print("[4/6] Enviando e-mail...")
    s.headers.update({
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://auth.thomsonreuters.com",
        "Referer": login_url,
    })
    r4 = s.post(
        login_url,
        data={
            "state": state,
            "username": ONVIO_EMAIL,
            "js-available": "true",
            "webauthn-available": "false",
            "is-brave": "false",
            "webauthn-platform-available": "false",
            "action": "default",
        },
        timeout=30,
    )
    soup4 = _soup(r4)
    state4 = _state(soup4)
    pwd_url = r4.url

    if "password" not in r4.url and not soup4.find("input", {"type": "password"}):
        raise RuntimeError(f"Esperado página de senha, obteve: {r4.url[:100]}")

    # STEP 5 — POST senha
    print("[5/6] Enviando senha...")
    s.headers["Referer"] = pwd_url
    r5 = s.post(
        pwd_url,
        data={"state": state4, "password": ONVIO_PASS, "action": "default"},
        timeout=30,
    )

    # Verifica se autenticou ou se está na página de MFA
    if "onvio.com.br" in r5.url and "auth" not in r5.url:
        print("  Login completo sem MFA ✅")
        return _extract_session(s, r5)

    if "mfa" in r5.url or "mfa" in r5.text.lower():
        print("[6/6] MFA requerido — disparando email OTP...")
        soup5 = _soup(r5)
        state5 = _state(soup5)
        mfa_url = r5.url

        s.headers["Referer"] = mfa_url
        r6 = s.post(
            mfa_url,
            data={"state": state5, "action": "email::1"},
            timeout=30,
        )
        otp_url = r6.url
        soup6 = _soup(r6)
        state6 = _state(soup6)

        print("  Email OTP disparado. Aguardando código...")

        # Tenta ler o código via IMAP
        otp_code = _read_otp_from_imap(timeout_s=90)

        if not otp_code:
            print("\n  ⚠️  IMAP não configurado ou código não encontrado.")
            print(f"  Verifique o inbox de {ONVIO_EMAIL} e informe o código:")
            otp_code = input("  Código OTP (6 dígitos): ").strip()

        if not otp_code:
            raise RuntimeError("Código OTP não fornecido")

        # POST código OTP
        print(f"  Submetendo OTP {otp_code}...")
        s.headers["Referer"] = otp_url
        r7 = s.post(
            otp_url,
            data={"state": state6, "code": otp_code, "action": "default"},
            allow_redirects=True,
            timeout=30,
        )

        if "onvio.com.br" in r7.url:
            print("  Login com MFA completo ✅")
            return _extract_session(s, r7)

        # Possível auto-submit form (Auth0 form_post)
        soup7 = _soup(r7)
        form = soup7.find("form")
        if form and form.get("action"):
            hidden = {i["name"]: i.get("value", "") for i in form.find_all("input", {"type": "hidden"})}
            r8 = s.post(form["action"], data=hidden, timeout=30)
            if "onvio.com.br" in r8.url:
                print("  Auth0 callback completo ✅")
                return _extract_session(s, r8)

        raise RuntimeError(f"Login falhou após MFA. URL final: {r7.url[:150]}")

    raise RuntimeError(f"Estado inesperado após senha. URL: {r5.url[:150]}")


def _extract_session(s: requests.Session, final_resp: requests.Response) -> dict:
    """Extrai cookies da sessão para armazenamento no Redis."""
    cookies = {c.name: c.value for c in s.cookies}

    # Cookies Auth0 (domínio thomsonreuters)
    auth0_cookies = {k: v for k, v in cookies.items() if k.startswith("auth0") or k == "did" or k == "did_compat"}

    # Cookies Onvio
    onvio_cookies = {k: v for k, v in cookies.items() if k not in auth0_cookies}

    return {
        "cookies": cookies,
        "auth0_cookies": auth0_cookies,
        "onvio_cookies": onvio_cookies,
        "final_url": final_resp.url,
        "extracted_at": time.time(),
        "extracted_at_iso": datetime.utcnow().isoformat() + "Z",
    }


# ── Redis ─────────────────────────────────────────────────────────────────────

def save_to_redis(session_data: dict) -> bool:
    r = redis.from_url(REDIS_URL)
    r.setex(REDIS_KEY, REDIS_TTL, json.dumps(session_data))
    print(f"\n✅ Sessão salva no Redis")
    print(f"   Key:     {REDIS_KEY}")
    print(f"   TTL:     {REDIS_TTL // 3600}h ({REDIS_TTL}s)")
    print(f"   Cookies: {list(session_data['cookies'].keys())}")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔐 GEDEON Onvio Auth — Iniciando login OIDC...\n")
    session_data = login_onvio()
    save_to_redis(session_data)
    print("\n✅ Concluído. Backend pode usar onvio:session do Redis.")
    print(f"   URL final: {session_data['final_url'][:100]}")
