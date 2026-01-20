"""
Testes para módulo ETL (normalização, mapeamento, deduplicação).
"""

import pytest
from datetime import datetime
from uuid import uuid4

# Importar módulos a testar
import sys
sys.path.insert(0, '/opt/conecta-pro/backend/modules/government_integrations')

from core.etl.normalizer import (
    normalizar_cpf,
    normalizar_cnpj,
    normalizar_data,
    normalizar_valor,
    normalizar_ie,
    NormalizadorDados,
)
from core.etl.field_mapper import (
    MapeadorCampos,
    MAPEAMENTO_NFE,
)
from core.etl.deduplicator import (
    DeduplicadorDocumentos,
    REGRAS_DEDUP,
)


class TestNormalizadorCPF:
    """Testes para normalização de CPF."""

    def test_cpf_com_formatacao(self):
        """Deve normalizar CPF formatado."""
        assert normalizar_cpf("123.456.789-00") == "12345678900"

    def test_cpf_sem_formatacao(self):
        """Deve manter CPF já normalizado."""
        assert normalizar_cpf("12345678900") == "12345678900"

    def test_cpf_com_espacos(self):
        """Deve remover espaços."""
        assert normalizar_cpf("  123.456.789-00  ") == "12345678900"

    def test_cpf_vazio(self):
        """Deve retornar None para CPF vazio."""
        assert normalizar_cpf("") is None
        assert normalizar_cpf(None) is None

    def test_cpf_invalido(self):
        """Deve retornar None para CPF inválido."""
        assert normalizar_cpf("123") is None
        assert normalizar_cpf("abc") is None


class TestNormalizadorCNPJ:
    """Testes para normalização de CNPJ."""

    def test_cnpj_com_formatacao(self):
        """Deve normalizar CNPJ formatado."""
        assert normalizar_cnpj("12.345.678/0001-90") == "12345678000190"

    def test_cnpj_sem_formatacao(self):
        """Deve manter CNPJ já normalizado."""
        assert normalizar_cnpj("12345678000190") == "12345678000190"

    def test_cnpj_vazio(self):
        """Deve retornar None para CNPJ vazio."""
        assert normalizar_cnpj("") is None


class TestNormalizadorData:
    """Testes para normalização de datas."""

    def test_data_iso(self):
        """Deve parsear data ISO."""
        result = normalizar_data("2026-01-15")
        assert result is not None
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_data_br(self):
        """Deve parsear data brasileira."""
        result = normalizar_data("15/01/2026")
        assert result is not None
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_data_iso_com_hora(self):
        """Deve parsear data ISO com hora."""
        result = normalizar_data("2026-01-15T14:30:00")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30

    def test_data_invalida(self):
        """Deve retornar None para data inválida."""
        assert normalizar_data("data-invalida") is None
        assert normalizar_data("") is None


class TestNormalizadorValor:
    """Testes para normalização de valores monetários."""

    def test_valor_decimal_ponto(self):
        """Deve parsear valor com ponto decimal."""
        assert normalizar_valor("1234.56") == 1234.56

    def test_valor_decimal_virgula(self):
        """Deve parsear valor brasileiro com vírgula."""
        assert normalizar_valor("1.234,56") == 1234.56

    def test_valor_inteiro(self):
        """Deve parsear valor inteiro."""
        assert normalizar_valor("1000") == 1000.0

    def test_valor_negativo(self):
        """Deve parsear valor negativo."""
        assert normalizar_valor("-100,50") == -100.50

    def test_valor_invalido(self):
        """Deve retornar 0 para valor inválido."""
        assert normalizar_valor("abc") == 0.0


class TestNormalizadorIE:
    """Testes para normalização de Inscrição Estadual."""

    def test_ie_isento(self):
        """Deve retornar ISENTO para valores indicando isenção."""
        assert normalizar_ie("ISENTO") == "ISENTO"
        assert normalizar_ie("isento") == "ISENTO"
        assert normalizar_ie("ISENTA") == "ISENTO"

    def test_ie_com_formatacao(self):
        """Deve remover caracteres não numéricos."""
        assert normalizar_ie("123.456.789.001") == "123456789001"

    def test_ie_vazia(self):
        """Deve retornar ISENTO para IE vazia."""
        assert normalizar_ie("") == "ISENTO"


class TestNormalizadorDados:
    """Testes para a classe NormalizadorDados."""

    def setup_method(self):
        """Setup para cada teste."""
        self.normalizador = NormalizadorDados()

    def test_normalizar_cep(self):
        """Deve normalizar CEP."""
        assert self.normalizador.normalizar_cep("12345-678") == "12345678"
        assert self.normalizador.normalizar_cep("12345678") == "12345678"

    def test_normalizar_telefone(self):
        """Deve normalizar telefone."""
        assert self.normalizador.normalizar_telefone("(11) 99999-8888") == "11999998888"
        assert self.normalizador.normalizar_telefone("11999998888") == "11999998888"

    def test_normalizar_ncm(self):
        """Deve normalizar NCM."""
        assert self.normalizador.normalizar_ncm("1234.56.78") == "12345678"

    def test_normalizar_chave_acesso(self):
        """Deve normalizar chave de acesso."""
        chave = "1234 5678 9012 3456 7890 1234 5678 9012 3456 7890 1234"
        resultado = self.normalizador.normalizar_chave_acesso(chave)
        assert len(resultado) == 44
        assert resultado.isdigit()


class TestMapeadorCampos:
    """Testes para mapeamento de campos."""

    def setup_method(self):
        """Setup para cada teste."""
        self.mapeador = MapeadorCampos()

    def test_mapear_dict_nfe(self):
        """Deve mapear campos de NF-e."""
        dados_xml = {
            "nNF": "123",
            "serie": "1",
            "dhEmi": "2026-01-15T10:00:00",
            "vNF": "1000.00",
            "CNPJ": "12345678000190",
            "xNome": "Empresa Teste",
        }

        resultado = self.mapeador.mapear_dict(dados_xml, "nfe")

        assert resultado["numero"] == "123"
        assert resultado["serie"] == "1"
        assert resultado["data_emissao"] == "2026-01-15T10:00:00"
        assert resultado["valor_total"] == "1000.00"

    def test_mapear_dict_com_defaults(self):
        """Deve usar valores default para campos ausentes."""
        dados_xml = {
            "nNF": "123",
        }

        resultado = self.mapeador.mapear_dict(dados_xml, "nfe")

        assert resultado["numero"] == "123"
        # Campos não mapeados não devem existir
        assert "serie" not in resultado


class TestRegrasDedup:
    """Testes para regras de deduplicação."""

    def test_regra_nfe_existe(self):
        """Deve existir regra para NF-e."""
        assert "nfe" in REGRAS_DEDUP

    def test_regra_nfe_campos_chave(self):
        """Regra NF-e deve ter chave_acesso como campo chave."""
        regra = REGRAS_DEDUP["nfe"]
        assert "chave_acesso" in regra.campos_chave

    def test_regra_esocial_existe(self):
        """Deve existir regra para eSocial."""
        assert "esocial" in REGRAS_DEDUP

    def test_regra_esocial_campos_chave(self):
        """Regra eSocial deve ter id_evento como campo chave."""
        regra = REGRAS_DEDUP["esocial"]
        assert "id_evento" in regra.campos_chave


class TestDeduplicador:
    """Testes para o deduplicador."""

    def test_obter_regra_existente(self):
        """Deve retornar regra existente."""
        regra = DeduplicadorDocumentos._obter_regra("nfe")
        assert regra is not None
        assert "chave_acesso" in regra.campos_chave

    def test_obter_regra_inexistente(self):
        """Deve retornar regra default para tipo inexistente."""
        regra = DeduplicadorDocumentos._obter_regra("tipo_inexistente")
        assert regra is not None
        # Deve usar regra default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
