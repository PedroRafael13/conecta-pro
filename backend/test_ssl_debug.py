#!/usr/bin/env python3
"""
Script de debug para conexão SSL com SEFAZ.
"""

import asyncio
import ssl
import traceback

import aiohttp

# Paths dos certificados
CERT_PEM = "/opt/conecta-pro/credentials/certificates/a1_cert.pem"
KEY_PEM = "/opt/conecta-pro/credentials/certificates/a1_key.pem"

# URL de teste
URL_SEFAZ = "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx?wsdl"


async def test_without_cert():
    """Testa conexão sem certificado cliente."""
    print("\n=== Teste SEM certificado cliente ===")
    try:
        ssl_ctx = ssl.create_default_context()
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)

        async with (
            aiohttp.ClientSession(connector=connector) as session,
            session.get(URL_SEFAZ, timeout=aiohttp.ClientTimeout(total=30)) as resp,
        ):
            print(f"Status: {resp.status}")
            text = await resp.text()
            print(f"Resposta (primeiros 200 chars): {text[:200]}")
    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        traceback.print_exc()


async def test_with_cert():
    """Testa conexão COM certificado cliente."""
    print("\n=== Teste COM certificado cliente ===")
    try:
        # Criar contexto SSL
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Carregar certificado e chave
        print(f"Carregando cert: {CERT_PEM}")
        print(f"Carregando key: {KEY_PEM}")
        ssl_ctx.load_cert_chain(certfile=CERT_PEM, keyfile=KEY_PEM)

        # Configurações de verificação
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        print(f"SSL Context criado: protocol={ssl_ctx.protocol}")

        # Criar connector
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        print("Connector criado")

        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"Session criada, fazendo request para: {URL_SEFAZ}")
            async with session.get(URL_SEFAZ, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                print(f"Resposta (primeiros 500 chars): {text[:500]}")

    except ssl.SSLError as e:
        print(f"SSL ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
    except aiohttp.ClientError as e:
        print(f"CLIENT ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"GENERIC ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()


async def test_with_cert_and_ca():
    """Testa conexão COM certificado cliente E verificação do servidor."""
    print("\n=== Teste COM certificado cliente E CA ===")
    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.load_cert_chain(certfile=CERT_PEM, keyfile=KEY_PEM)

        print("SSL Context com CA padrão criado")

        connector = aiohttp.TCPConnector(ssl=ssl_ctx)

        async with (
            aiohttp.ClientSession(connector=connector) as session,
            session.get(URL_SEFAZ, timeout=aiohttp.ClientTimeout(total=30)) as resp,
        ):
            print(f"Status: {resp.status}")
            text = await resp.text()
            print(f"Resposta (primeiros 500 chars): {text[:500]}")

    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        traceback.print_exc()


async def test_soap_request():
    """Testa requisição SOAP real."""
    print("\n=== Teste SOAP Request ===")

    soap_url = "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx"
    cnpj = "35710481000103"

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
    <soap12:Body>
        <nfeDistDFeInteresse xmlns="http://www.portalfiscal.inf.br/nfe">
            <nfeDadosMsg>
                <distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
                    <tpAmb>1</tpAmb>
                    <cUFAutor>13</cUFAutor>
                    <CNPJ>{cnpj}</CNPJ>
                    <distNSU>
                        <NSU>000000000000000</NSU>
                    </distNSU>
                </distDFeInt>
            </nfeDadosMsg>
        </nfeDistDFeInteresse>
    </soap12:Body>
</soap12:Envelope>"""

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
        "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse",
    }

    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.load_cert_chain(certfile=CERT_PEM, keyfile=KEY_PEM)

        connector = aiohttp.TCPConnector(ssl=ssl_ctx)

        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"Enviando SOAP para: {soap_url}")
            async with session.post(
                soap_url, data=envelope, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                print(f"Resposta:\n{text[:2000]}")

    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        traceback.print_exc()


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("DEBUG SSL/mTLS - Conexão SEFAZ")
    print("=" * 60)

    # Verificar arquivos
    import os

    print(f"\nCert existe: {os.path.exists(CERT_PEM)}")
    print(f"Key existe: {os.path.exists(KEY_PEM)}")

    await test_without_cert()
    await test_with_cert()
    await test_with_cert_and_ca()
    await test_soap_request()


if __name__ == "__main__":
    asyncio.run(main())
