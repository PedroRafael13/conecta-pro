"""
Service para e-CAC - Centro Virtual de Atendimento ao Contribuinte.

Camada de servico para operacoes do e-CAC.
"""

import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any

from ..core.certificate_manager import CertificateManager
from ..core.ecac import (
    EcacManager,
    TipoDeclaracaoConsulta,
)

logger = logging.getLogger(__name__)


class EcacService:
    """Service para operacoes do e-CAC."""

    def __init__(self):
        """Inicializa o service."""
        self.cpf_cnpj = os.getenv("ECAC_CPF_CNPJ", os.getenv("EMPRESA_CNPJ", "35710481000103"))
        self.cert_path = os.getenv("CERTIFICATE_PATH", "")
        self.cert_password = os.getenv("CERTIFICATE_PASSWORD", "")

        # Certificado eh opcional
        self.cert_manager = None
        if self.cert_path and os.path.exists(self.cert_path):
            try:
                self.cert_manager = CertificateManager(certificate_path=self.cert_path, password=self.cert_password)
                logger.info("Certificado digital carregado para e-CAC")
            except Exception as e:
                logger.warning(f"Certificado nao carregado: {e}")

        self.manager = EcacManager(
            cnpj_cpf=self.cpf_cnpj,
            certificado_path=self.cert_path,
            certificado_senha=self.cert_password,
        )

        logger.info(f"e-CAC Service inicializado - CPF/CNPJ: {self.cpf_cnpj}, Tipo: {self.manager.tipo_documento}")

    def consultar_situacao_fiscal(
        self,
        cpf_cnpj: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta situacao fiscal do contribuinte.

        Args:
            cpf_cnpj: CPF ou CNPJ (opcional, usa o configurado)

        Returns:
            Dict com resultado da consulta
        """
        documento = cpf_cnpj or self.cpf_cnpj

        # Se foi passado um documento diferente, cria um novo manager
        if cpf_cnpj and cpf_cnpj != self.cpf_cnpj:
            manager = EcacManager(
                cnpj_cpf=cpf_cnpj,
                certificado_path=self.cert_path,
                certificado_senha=self.cert_password,
            )
        else:
            manager = self.manager

        resultado = manager.consultar_situacao_fiscal()

        logger.info(f"Situacao fiscal consultada para {documento}")

        # Converte pendencias
        pendencias = []
        for p in resultado.pendencias:
            pendencias.append(
                {
                    "tipo": p.tipo.value,
                    "descricao": p.descricao,
                    "valor": str(p.valor) if p.valor else None,
                    "data_vencimento": p.data_vencimento.isoformat() if p.data_vencimento else None,
                    "numero_processo": p.numero_processo,
                    "exercicio": p.exercicio,
                    "periodo_apuracao": p.periodo_apuracao,
                }
            )

        # Converte debitos
        debitos = []
        for d in resultado.debitos:
            debitos.append(
                {
                    "codigo_receita": d.codigo_receita,
                    "descricao": d.descricao,
                    "competencia": d.competencia,
                    "valor_principal": str(d.valor_principal),
                    "valor_multa": str(d.valor_multa),
                    "valor_juros": str(d.valor_juros),
                    "valor_total": str(d.valor_total),
                    "data_vencimento": d.data_vencimento.isoformat() if d.data_vencimento else None,
                    "situacao": d.situacao,
                    "numero_processo": d.numero_processo,
                }
            )

        return {
            "cpf_cnpj": resultado.cpf_cnpj,
            "nome": resultado.nome,
            "situacao": resultado.situacao.value,
            "data_consulta": resultado.data_consulta.isoformat(),
            "pendencias": pendencias,
            "debitos": debitos,
            "declaracoes_omissas": resultado.declaracoes_omissas,
            "certidao_disponivel": resultado.certidao_disponivel,
            "tipo_certidao_disponivel": (
                resultado.tipo_certidao_disponivel.value if resultado.tipo_certidao_disponivel else None
            ),
        }

    def consultar_debitos(
        self,
        situacao: str | None = None,
        competencia_inicio: str | None = None,
        competencia_fim: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta debitos do contribuinte.

        Args:
            situacao: Filtro de situacao ('aberto', 'suspenso', 'parcelado')
            competencia_inicio: Competencia inicial (YYYY-MM)
            competencia_fim: Competencia final (YYYY-MM)

        Returns:
            Dict com lista de debitos
        """
        debitos_raw = self.manager.consultar_debitos(situacao=situacao)

        debitos = []
        valor_total = Decimal("0")

        for d in debitos_raw:
            debito = {
                "codigo_receita": d.codigo_receita,
                "descricao": d.descricao,
                "competencia": d.competencia,
                "valor_principal": str(d.valor_principal),
                "valor_multa": str(d.valor_multa),
                "valor_juros": str(d.valor_juros),
                "valor_total": str(d.valor_total),
                "data_vencimento": d.data_vencimento.isoformat() if d.data_vencimento else None,
                "situacao": d.situacao,
                "numero_processo": d.numero_processo,
            }

            # Filtro por competencia
            if competencia_inicio and d.competencia < competencia_inicio:
                continue
            if competencia_fim and d.competencia > competencia_fim:
                continue

            debitos.append(debito)
            valor_total += d.valor_total

        logger.info(f"Debitos consultados: {len(debitos)} encontrados")

        return {
            "cpf_cnpj": self.cpf_cnpj,
            "data_consulta": datetime.now().isoformat(),
            "quantidade": len(debitos),
            "valor_total": str(valor_total),
            "filtros": {
                "situacao": situacao,
                "competencia_inicio": competencia_inicio,
                "competencia_fim": competencia_fim,
            },
            "debitos": debitos,
        }

    def emitir_certidao(
        self,
        finalidade: str | None = None,
        cpf_cnpj: str | None = None,
    ) -> dict[str, Any]:
        """
        Emite certidao fiscal (CND/CPEN).

        Args:
            finalidade: Finalidade da certidao
            cpf_cnpj: CPF ou CNPJ (opcional)

        Returns:
            Dict com dados da certidao
        """
        documento = cpf_cnpj or self.cpf_cnpj

        if cpf_cnpj and cpf_cnpj != self.cpf_cnpj:
            manager = EcacManager(
                cnpj_cpf=cpf_cnpj,
                certificado_path=self.cert_path,
                certificado_senha=self.cert_password,
            )
        else:
            manager = self.manager

        certidao = manager.emitir_certidao(finalidade=finalidade)

        logger.info(f"Certidao emitida para {documento}: {certidao.tipo.value}")

        return {
            "tipo": certidao.tipo.value,
            "numero": certidao.numero,
            "data_emissao": certidao.data_emissao.isoformat(),
            "data_validade": certidao.data_validade.isoformat(),
            "codigo_controle": certidao.codigo_controle,
            "contribuinte_cpf_cnpj": certidao.contribuinte_cpf_cnpj,
            "contribuinte_nome": certidao.contribuinte_nome,
            "finalidade": certidao.finalidade,
            "observacoes": certidao.observacoes,
        }

    def validar_certidao(
        self,
        numero: str,
        codigo_controle: str,
    ) -> dict[str, Any]:
        """
        Valida autenticidade de uma certidao.

        Args:
            numero: Numero da certidao
            codigo_controle: Codigo de controle

        Returns:
            Dict com resultado da validacao
        """
        resultado = self.manager.validar_certidao(
            numero=numero,
            codigo_controle=codigo_controle,
        )

        logger.info(f"Certidao validada: {numero} - Valida: {resultado.get('valida')}")

        return {
            "numero": resultado["numero"],
            "codigo_controle": resultado["codigo_controle"],
            "valida": resultado["valida"],
            "data_validacao": resultado["data_validacao"],
            "tipo_certidao": resultado.get("tipo_certidao"),
            "data_emissao": resultado.get("data_emissao"),
            "data_validade": resultado.get("data_validade"),
            "contribuinte": resultado.get("contribuinte"),
            "mensagem": resultado["mensagem"],
        }

    def consultar_declaracoes(
        self,
        tipo: str,
        exercicio_inicio: int,
        exercicio_fim: int | None = None,
    ) -> dict[str, Any]:
        """
        Consulta declaracoes transmitidas.

        Args:
            tipo: Tipo de declaracao
            exercicio_inicio: Exercicio inicial
            exercicio_fim: Exercicio final

        Returns:
            Dict com lista de declaracoes
        """
        try:
            tipo_enum = TipoDeclaracaoConsulta(tipo)
        except ValueError:
            tipo_enum = TipoDeclaracaoConsulta.DCTFWEB

        exercicio_fim = exercicio_fim or exercicio_inicio

        declaracoes_raw = self.manager.consultar_declaracoes(
            tipo=tipo_enum,
            exercicio_inicio=exercicio_inicio,
            exercicio_fim=exercicio_fim,
        )

        declaracoes = []
        for d in declaracoes_raw:
            declaracoes.append(
                {
                    "tipo": d.tipo.value,
                    "exercicio": d.exercicio,
                    "numero_recibo": d.numero_recibo,
                    "data_transmissao": d.data_transmissao.isoformat(),
                    "situacao": d.situacao,
                    "retificadora": d.retificadora,
                    "numero_recibo_anterior": d.numero_recibo_anterior,
                }
            )

        logger.info(
            f"Declaracoes consultadas: {len(declaracoes)} encontradas ({tipo} {exercicio_inicio}-{exercicio_fim})"
        )

        return {
            "cpf_cnpj": self.cpf_cnpj,
            "tipo": tipo,
            "exercicio_inicio": exercicio_inicio,
            "exercicio_fim": exercicio_fim,
            "quantidade": len(declaracoes),
            "declaracoes": declaracoes,
        }

    def consultar_parcelamentos(
        self,
        situacao: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta parcelamentos ativos.

        Args:
            situacao: Filtro de situacao

        Returns:
            Dict com lista de parcelamentos
        """
        parcelamentos = self.manager.consultar_parcelamentos()

        # Filtra por situacao se especificado
        if situacao:
            parcelamentos = [p for p in parcelamentos if p.get("situacao") == situacao]

        logger.info(f"Parcelamentos consultados: {len(parcelamentos)} encontrados")

        return {
            "cpf_cnpj": self.cpf_cnpj,
            "data_consulta": datetime.now().isoformat(),
            "quantidade": len(parcelamentos),
            "parcelamentos": parcelamentos,
        }

    def simular_parcelamento(
        self,
        debitos: list[str],
        quantidade_parcelas: int,
    ) -> dict[str, Any]:
        """
        Simula parcelamento de debitos.

        Args:
            debitos: Lista de codigos de debitos
            quantidade_parcelas: Numero de parcelas

        Returns:
            Dict com simulacao do parcelamento
        """
        resultado = self.manager.simular_parcelamento(
            debitos=debitos,
            quantidade_parcelas=quantidade_parcelas,
        )

        logger.info(f"Parcelamento simulado: {len(debitos)} debitos em {quantidade_parcelas}x")

        return {
            "cpf_cnpj": self.cpf_cnpj,
            "debitos": resultado["debitos"],
            "quantidade_debitos": len(debitos),
            "valor_total_debitos": resultado.get("valor_total_debitos", "0.00"),
            "quantidade_parcelas": resultado["quantidade_parcelas"],
            "valor_primeira_parcela": resultado.get("valor_primeira_parcela", "0.00"),
            "valor_demais_parcelas": resultado.get("valor_demais_parcelas", "0.00"),
            "taxa_juros": resultado.get("taxa_juros", "SELIC"),
            "data_primeira_parcela": resultado.get("data_primeira_parcela", ""),
            "status": resultado["status"],
            "observacoes": resultado.get("observacoes"),
            "mensagem": resultado["mensagem"],
        }

    def consultar_processos(
        self,
        situacao: str | None = None,
        numero_processo: str | None = None,
    ) -> dict[str, Any]:
        """
        Consulta processos digitais (e-Processo).

        Args:
            situacao: Filtro de situacao
            numero_processo: Numero especifico do processo

        Returns:
            Dict com lista de processos
        """
        processos = self.manager.consultar_processos(situacao=situacao)

        # Filtra por numero se especificado
        if numero_processo:
            processos = [p for p in processos if p.get("numero") == numero_processo]

        logger.info(f"Processos consultados: {len(processos)} encontrados")

        return {
            "cpf_cnpj": self.cpf_cnpj,
            "data_consulta": datetime.now().isoformat(),
            "quantidade": len(processos),
            "filtros": {
                "situacao": situacao,
                "numero_processo": numero_processo,
            },
            "processos": processos,
        }

    def validar_status(self) -> dict[str, Any]:
        """
        Valida status da configuracao e-CAC.

        Returns:
            Dict com status da configuracao
        """
        return {
            "ambiente": "producao",
            "url": self.manager.URL_PRODUCAO,
            "cpf_cnpj": self.cpf_cnpj,
            "tipo_documento": self.manager.tipo_documento,
            "certificado_configurado": self.cert_manager is not None,
            "certificado_valido": (self.cert_manager._loaded if self.cert_manager else False),
            "servicos_disponiveis": [
                "Consulta de Situacao Fiscal",
                "Consulta de Debitos",
                "Emissao de Certidoes (CND/CPEN)",
                "Validacao de Certidoes",
                "Consulta de Declaracoes",
                "Parcelamentos",
                "Processos Digitais (e-Processo)",
            ],
        }


# Singleton
_ecac_service: EcacService | None = None


def get_ecac_service() -> EcacService:
    """Retorna instancia singleton do service."""
    global _ecac_service
    if _ecac_service is None:
        _ecac_service = EcacService()
    return _ecac_service
