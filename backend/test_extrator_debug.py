#!/usr/bin/env python3
"""
Debug do extrator NF-e - simula o fluxo completo.
"""

import asyncio
import sys

# Adicionar path do módulo
sys.path.insert(0, "/app")

from uuid import UUID


async def test_comutador():
    """Testa obtenção de URL via comutador."""
    print("\n=== Teste do Comutador ===")

    from modules.government_integrations.core.contingency import ComutadorEndpoints, MatrizContingencia

    comutador = ComutadorEndpoints()

    # Testar URL para AN
    print("\nTestando obter_endpoint('AN', 'nfe', 'NFeDistribuicaoDFe'):")
    try:
        url, contingencia = await comutador.obter_endpoint("AN", "nfe", "NFeDistribuicaoDFe")
        print(f"  URL: {url}")
        print(f"  Contingência: {contingencia}")
    except Exception as e:
        print(f"  ERRO: {e}")

    # Resolver URL diretamente
    print("\nTestando MatrizContingencia.resolver_url('AN', 'NFeDistribuicaoDFe'):")
    try:
        url = MatrizContingencia.resolver_url("AN", "NFeDistribuicaoDFe")
        print(f"  URL: {url}")
    except Exception as e:
        print(f"  ERRO: {e}")


async def test_credenciais():
    """Testa obtenção de credenciais."""
    print("\n=== Teste de Credenciais ===")

    from modules.government_integrations.core.credentials import TipoCredencial
    from modules.government_integrations.core.credentials.file_credential_provider import get_file_credential_provider

    try:
        provider = get_file_credential_provider()
        print("FileCredentialProvider criado")

        # Testar SSL context
        ssl_ctx = provider.get_ssl_context()
        print(f"SSL Context: protocol={ssl_ctx.protocol}")

        # Testar credencial
        tenant_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        credencial = await provider.obter_credencial(tenant_id, TipoCredencial.SEFAZ_NFE)
        print(f"Credencial válida: {credencial.valida}")
        print(f"Certificado CNPJ: {credencial.certificado_info.cnpj_cpf if credencial.certificado_info else 'N/A'}")

    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


async def test_session():
    """Testa criação de sessão HTTP."""
    print("\n=== Teste de Sessão HTTP ===")

    import aiohttp

    from modules.government_integrations.core.credentials.file_credential_provider import get_file_credential_provider

    try:
        provider = get_file_credential_provider()
        ssl_ctx = provider.get_ssl_context()

        print(f"SSL Context criado: {ssl_ctx}")

        # URL de teste
        url = "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx"

        connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        print(f"Connector criado: {connector}")

        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"Session criada: {session}")

            # Fazer requisição simples
            async with session.get(f"{url}?wsdl", timeout=aiohttp.ClientTimeout(total=30)) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    text = await resp.text()
                    print(f"Resposta OK (len={len(text)})")
                else:
                    text = await resp.text()
                    print(f"Resposta: {text[:500]}")

    except aiohttp.ClientError as e:
        print(f"CLIENT ERROR: {type(e).__name__}: {e}")
        print(f"  args: {e.args}")
        import traceback

        traceback.print_exc()
    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


async def test_extracao():
    """Testa extração completa."""
    print("\n=== Teste de Extração Completa ===")

    from modules.government_integrations.core.credentials.file_credential_provider import get_file_credential_provider
    from modules.government_integrations.extractors.sefaz.nfe_extractor import ExtratorNFe

    try:
        # Criar provedor adaptado
        file_provider = get_file_credential_provider()

        # O ExtratorNFe espera um ProvedorCredenciais
        # Vamos criar um wrapper simples
        class FileProviderAdapter:
            def __init__(self, file_provider):
                self._fp = file_provider

            async def obter_credencial(self, tenant_id, tipo_credencial, **kwargs):
                return await self._fp.obter_credencial(str(tenant_id), tipo_credencial, **kwargs)

        adapter = FileProviderAdapter(file_provider)

        extrator = ExtratorNFe(credentials=adapter)
        print("Extrator criado")

        # Tentar extrair
        tenant_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

        print(f"\nIniciando extração para tenant: {tenant_id}")
        resultado = await extrator.extrair(tenant_id)

        print("\nResultado:")
        print(f"  Status: {resultado.status}")
        print(f"  Documentos: {resultado.documentos_processados}")
        print(f"  Novos: {resultado.documentos_novos}")
        print(f"  Erros: {len(resultado.erros)}")
        for erro in resultado.erros[:5]:
            print(f"    - {erro}")

    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("DEBUG Extrator NF-e - Fluxo Completo")
    print("=" * 60)

    await test_comutador()
    await test_credenciais()
    await test_session()
    await test_extracao()


if __name__ == "__main__":
    asyncio.run(main())
