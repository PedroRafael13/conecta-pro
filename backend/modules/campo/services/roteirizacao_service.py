"""
Serviço de Roteirização Inteligente para Campo.

Fornece funcionalidades para:
- Otimização de rotas para múltiplas OS do dia
- Integração com Google Maps API
- Cálculo de distâncias e tempos
- Janelas de atendimento
- Reotimização em tempo real
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
import logging
import math
import json

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TipoOtimizacao(str, Enum):
    """Tipos de otimização de rota."""
    MENOR_DISTANCIA = "menor_distancia"
    MENOR_TEMPO = "menor_tempo"
    BALANCEADA = "balanceada"
    PRIORIDADE = "prioridade"


class StatusRoteiro(str, Enum):
    """Status do roteiro."""
    PLANEJADO = "planejado"
    EM_EXECUCAO = "em_execucao"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class PontoRota(BaseModel):
    """Ponto de uma rota."""
    ordem_servico_id: Optional[UUID] = None
    visita_id: Optional[UUID] = None
    endereco: str
    latitude: float
    longitude: float
    tipo: str  # 'os', 'visita', 'base'
    nome_cliente: Optional[str] = None
    janela_inicio: Optional[time] = None
    janela_fim: Optional[time] = None
    duracao_estimada_minutos: int = 60
    prioridade: int = 1  # 1=baixa, 5=urgente


class TrechoRota(BaseModel):
    """Trecho entre dois pontos."""
    origem: PontoRota
    destino: PontoRota
    distancia_km: float
    duracao_minutos: int
    instrucoes: Optional[str] = None


class RoteiroOtimizado(BaseModel):
    """Roteiro otimizado completo."""
    tecnico_id: UUID
    tecnico_nome: str
    data: date
    pontos: List[PontoRota]
    trechos: List[TrechoRota]
    distancia_total_km: float
    duracao_total_minutos: int
    hora_inicio_sugerida: time
    hora_fim_estimada: time
    economia_km: Optional[float] = None  # Comparado com ordem original
    economia_tempo_minutos: Optional[int] = None


class RoteirizacaoService:
    """Serviço de roteirização inteligente."""

    def __init__(self, db: Session, google_maps_api_key: Optional[str] = None):
        self.db = db
        self.google_maps_api_key = google_maps_api_key
        self._cache_distancias: Dict[str, Dict] = {}

    # =========================================================================
    # OTIMIZAÇÃO DE ROTAS
    # =========================================================================

    def otimizar_rota_tecnico(
        self,
        tecnico_id: UUID,
        data: date,
        tipo_otimizacao: TipoOtimizacao = TipoOtimizacao.BALANCEADA,
        ponto_partida: Optional[Dict[str, Any]] = None,
        ponto_retorno: Optional[Dict[str, Any]] = None,
    ) -> RoteiroOtimizado:
        """
        Otimiza a rota de um técnico para um dia específico.

        Args:
            tecnico_id: ID do técnico
            data: Data do roteiro
            tipo_otimizacao: Tipo de otimização desejada
            ponto_partida: Ponto de partida (default: base do técnico)
            ponto_retorno: Ponto de retorno (default: mesmo da partida)

        Returns:
            RoteiroOtimizado com a melhor rota
        """
        from modules.campo.models.ordem_servico import OrdemServico, StatusOS
        from modules.campo.models.visita import Visita, StatusVisita

        # Buscar dados do técnico
        from modules.campo.models.campo_tecnico import CampoTecnico

        tecnico = self.db.query(CampoTecnico).filter(
            CampoTecnico.id == tecnico_id
        ).first()

        if not tecnico:
            raise ValueError(f"Técnico {tecnico_id} não encontrado")

        # Definir ponto de partida
        if not ponto_partida:
            ponto_partida = {
                "endereco": tecnico.base_address if hasattr(tecnico, 'base_address') else "Base",
                "latitude": float(tecnico.base_latitude) if hasattr(tecnico, 'base_latitude') and tecnico.base_latitude else -23.5505,
                "longitude": float(tecnico.base_longitude) if hasattr(tecnico, 'base_longitude') and tecnico.base_longitude else -46.6333,
            }

        # Buscar OS agendadas para o dia
        ordens_servico = self.db.query(OrdemServico).filter(
            OrdemServico.tecnico_id == tecnico_id,
            OrdemServico.data_agendada == data,
            OrdemServico.status.in_([StatusOS.AGENDADA, StatusOS.EM_ANDAMENTO]),
        ).all()

        # Buscar visitas agendadas para o dia
        visitas = self.db.query(Visita).filter(
            Visita.responsavel_id == tecnico_id,
            Visita.data_visita == data,
            Visita.status.in_([StatusVisita.AGENDADA, StatusVisita.CONFIRMADA]),
        ).all()

        # Converter para pontos de rota
        pontos = []

        # Adicionar ponto de partida
        ponto_base = PontoRota(
            endereco=ponto_partida["endereco"],
            latitude=ponto_partida["latitude"],
            longitude=ponto_partida["longitude"],
            tipo="base",
            nome_cliente="Base",
            duracao_estimada_minutos=0,
            prioridade=0,
        )
        pontos.append(ponto_base)

        # Adicionar OS
        for os_item in ordens_servico:
            ponto = PontoRota(
                ordem_servico_id=os_item.id,
                endereco=os_item.endereco_servico or "Endereço não informado",
                latitude=float(os_item.latitude) if os_item.latitude else -23.5505,
                longitude=float(os_item.longitude) if os_item.longitude else -46.6333,
                tipo="os",
                nome_cliente=os_item.cliente_nome if hasattr(os_item, 'cliente_nome') else "Cliente",
                janela_inicio=os_item.horario_inicio_previsto,
                janela_fim=os_item.horario_fim_previsto,
                duracao_estimada_minutos=os_item.duracao_estimada_minutos or 60,
                prioridade=self._prioridade_para_int(os_item.prioridade),
            )
            pontos.append(ponto)

        # Adicionar visitas
        for visita in visitas:
            ponto = PontoRota(
                visita_id=visita.id,
                endereco=visita.endereco or "Endereço não informado",
                latitude=float(visita.latitude) if visita.latitude else -23.5505,
                longitude=float(visita.longitude) if visita.longitude else -46.6333,
                tipo="visita",
                nome_cliente=visita.cliente_nome if hasattr(visita, 'cliente_nome') else visita.prospect_nome or "Cliente",
                janela_inicio=visita.horario_inicio,
                janela_fim=visita.horario_fim,
                duracao_estimada_minutos=30,  # Visitas geralmente são mais curtas
                prioridade=2,
            )
            pontos.append(ponto)

        if len(pontos) <= 1:
            # Nenhum serviço agendado
            return RoteiroOtimizado(
                tecnico_id=tecnico_id,
                tecnico_nome=tecnico.full_name if hasattr(tecnico, 'full_name') else str(tecnico_id),
                data=data,
                pontos=[ponto_base],
                trechos=[],
                distancia_total_km=0,
                duracao_total_minutos=0,
                hora_inicio_sugerida=time(8, 0),
                hora_fim_estimada=time(8, 0),
            )

        # Otimizar ordem dos pontos
        pontos_otimizados = self._otimizar_ordem_pontos(
            pontos, tipo_otimizacao
        )

        # Adicionar ponto de retorno se especificado
        if ponto_retorno:
            ponto_fim = PontoRota(
                endereco=ponto_retorno["endereco"],
                latitude=ponto_retorno["latitude"],
                longitude=ponto_retorno["longitude"],
                tipo="base",
                nome_cliente="Retorno",
                duracao_estimada_minutos=0,
                prioridade=0,
            )
            pontos_otimizados.append(ponto_fim)

        # Calcular trechos entre pontos
        trechos = self._calcular_trechos(pontos_otimizados)

        # Calcular totais
        distancia_total = sum(t.distancia_km for t in trechos)
        duracao_deslocamento = sum(t.duracao_minutos for t in trechos)
        duracao_servicos = sum(p.duracao_estimada_minutos for p in pontos_otimizados if p.tipo != "base")
        duracao_total = duracao_deslocamento + duracao_servicos

        # Calcular horários
        hora_inicio = time(8, 0)  # Início padrão às 8h
        if pontos_otimizados[1].janela_inicio:
            hora_inicio = pontos_otimizados[1].janela_inicio

        minutos_fim = hora_inicio.hour * 60 + hora_inicio.minute + duracao_total
        hora_fim = time(minutos_fim // 60, minutos_fim % 60)

        # Calcular economia (comparar com ordem original)
        economia_km, economia_tempo = self._calcular_economia(
            pontos, pontos_otimizados
        )

        return RoteiroOtimizado(
            tecnico_id=tecnico_id,
            tecnico_nome=tecnico.full_name if hasattr(tecnico, 'full_name') else str(tecnico_id),
            data=data,
            pontos=pontos_otimizados,
            trechos=trechos,
            distancia_total_km=round(distancia_total, 2),
            duracao_total_minutos=duracao_total,
            hora_inicio_sugerida=hora_inicio,
            hora_fim_estimada=hora_fim,
            economia_km=round(economia_km, 2) if economia_km else None,
            economia_tempo_minutos=economia_tempo,
        )

    def _otimizar_ordem_pontos(
        self,
        pontos: List[PontoRota],
        tipo_otimizacao: TipoOtimizacao,
    ) -> List[PontoRota]:
        """
        Otimiza a ordem dos pontos usando algoritmo adequado.

        Implementa uma versão simplificada do Problema do Caixeiro Viajante (TSP).
        """
        if len(pontos) <= 2:
            return pontos

        # Separar ponto de partida (base)
        ponto_partida = pontos[0]
        pontos_servico = pontos[1:]

        # Se houver janelas de tempo, ordenar respeitando-as
        pontos_com_janela = [p for p in pontos_servico if p.janela_inicio]
        pontos_sem_janela = [p for p in pontos_servico if not p.janela_inicio]

        # Ordenar por janela de início
        pontos_com_janela.sort(key=lambda p: (p.janela_inicio.hour * 60 + p.janela_inicio.minute) if p.janela_inicio else 999)

        # Se otimização por prioridade, colocar urgentes primeiro
        if tipo_otimizacao == TipoOtimizacao.PRIORIDADE:
            pontos_sem_janela.sort(key=lambda p: -p.prioridade)

        # Usar algoritmo do vizinho mais próximo para pontos sem janela
        if pontos_sem_janela and tipo_otimizacao in [TipoOtimizacao.MENOR_DISTANCIA, TipoOtimizacao.BALANCEADA]:
            pontos_sem_janela = self._nearest_neighbor(ponto_partida, pontos_sem_janela)

        # Intercalar pontos com janela e sem janela
        resultado = [ponto_partida]

        idx_com_janela = 0
        idx_sem_janela = 0
        hora_atual = 8 * 60  # 8:00 em minutos

        while idx_com_janela < len(pontos_com_janela) or idx_sem_janela < len(pontos_sem_janela):
            proximo = None

            if idx_com_janela < len(pontos_com_janela):
                ponto_janela = pontos_com_janela[idx_com_janela]
                janela_minutos = ponto_janela.janela_inicio.hour * 60 + ponto_janela.janela_inicio.minute if ponto_janela.janela_inicio else 999

                # Se já está na hora da janela ou passou
                if hora_atual >= janela_minutos - 30:  # 30 min de margem
                    proximo = ponto_janela
                    idx_com_janela += 1

            if not proximo and idx_sem_janela < len(pontos_sem_janela):
                proximo = pontos_sem_janela[idx_sem_janela]
                idx_sem_janela += 1
            elif not proximo and idx_com_janela < len(pontos_com_janela):
                proximo = pontos_com_janela[idx_com_janela]
                idx_com_janela += 1

            if proximo:
                resultado.append(proximo)
                # Atualizar hora atual (simplificado)
                hora_atual += proximo.duracao_estimada_minutos + 20  # 20 min deslocamento médio

        return resultado

    def _nearest_neighbor(
        self,
        origem: PontoRota,
        pontos: List[PontoRota],
    ) -> List[PontoRota]:
        """
        Algoritmo do vizinho mais próximo para ordenar pontos.
        """
        if not pontos:
            return []

        resultado = []
        restantes = pontos.copy()
        atual = origem

        while restantes:
            # Encontrar ponto mais próximo
            mais_proximo = min(
                restantes,
                key=lambda p: self._calcular_distancia(atual, p)
            )
            resultado.append(mais_proximo)
            restantes.remove(mais_proximo)
            atual = mais_proximo

        return resultado

    def _calcular_distancia(
        self,
        p1: PontoRota,
        p2: PontoRota,
    ) -> float:
        """
        Calcula distância entre dois pontos usando fórmula de Haversine.
        """
        # Fórmula de Haversine para distância em km
        R = 6371  # Raio da Terra em km

        lat1 = math.radians(p1.latitude)
        lat2 = math.radians(p2.latitude)
        dlat = math.radians(p2.latitude - p1.latitude)
        dlon = math.radians(p2.longitude - p1.longitude)

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _calcular_trechos(
        self,
        pontos: List[PontoRota],
    ) -> List[TrechoRota]:
        """Calcula os trechos entre pontos consecutivos."""
        trechos = []

        for i in range(len(pontos) - 1):
            origem = pontos[i]
            destino = pontos[i + 1]

            distancia = self._calcular_distancia(origem, destino)

            # Estimar tempo: 30 km/h em área urbana (média)
            duracao = int(distancia / 30 * 60)  # minutos

            # Se tiver API do Google Maps, usar dados reais
            if self.google_maps_api_key:
                dados_google = self._consultar_google_maps(origem, destino)
                if dados_google:
                    distancia = dados_google.get("distancia_km", distancia)
                    duracao = dados_google.get("duracao_minutos", duracao)

            trecho = TrechoRota(
                origem=origem,
                destino=destino,
                distancia_km=round(distancia, 2),
                duracao_minutos=duracao,
            )
            trechos.append(trecho)

        return trechos

    def _calcular_economia(
        self,
        ordem_original: List[PontoRota],
        ordem_otimizada: List[PontoRota],
    ) -> Tuple[Optional[float], Optional[int]]:
        """Calcula economia comparando ordem original com otimizada."""
        if len(ordem_original) <= 2:
            return None, None

        # Calcular distância total da ordem original
        distancia_original = 0
        for i in range(len(ordem_original) - 1):
            distancia_original += self._calcular_distancia(
                ordem_original[i], ordem_original[i + 1]
            )

        # Calcular distância total da ordem otimizada
        distancia_otimizada = 0
        for i in range(len(ordem_otimizada) - 1):
            distancia_otimizada += self._calcular_distancia(
                ordem_otimizada[i], ordem_otimizada[i + 1]
            )

        economia_km = distancia_original - distancia_otimizada

        # Estimar economia de tempo (30 km/h médio)
        economia_tempo = int(economia_km / 30 * 60) if economia_km > 0 else 0

        return economia_km, economia_tempo

    def _prioridade_para_int(self, prioridade: Any) -> int:
        """Converte enum de prioridade para inteiro."""
        if hasattr(prioridade, 'value'):
            prioridade = prioridade.value

        mapa = {
            'BAIXA': 1,
            'NORMAL': 2,
            'ALTA': 3,
            'URGENTE': 5,
            'baixa': 1,
            'normal': 2,
            'alta': 3,
            'urgente': 5,
        }
        return mapa.get(str(prioridade), 2)

    # =========================================================================
    # INTEGRAÇÃO GOOGLE MAPS
    # =========================================================================

    def _consultar_google_maps(
        self,
        origem: PontoRota,
        destino: PontoRota,
    ) -> Optional[Dict[str, Any]]:
        """
        Consulta a API do Google Maps para obter distância e tempo reais.
        """
        if not self.google_maps_api_key:
            return None

        # Verificar cache
        cache_key = f"{origem.latitude},{origem.longitude}|{destino.latitude},{destino.longitude}"
        if cache_key in self._cache_distancias:
            return self._cache_distancias[cache_key]

        try:
            # TODO: Implementar chamada real à API do Google Maps
            # Exemplo de implementação:
            #
            # import httpx
            # url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            # params = {
            #     "origins": f"{origem.latitude},{origem.longitude}",
            #     "destinations": f"{destino.latitude},{destino.longitude}",
            #     "mode": "driving",
            #     "key": self.google_maps_api_key,
            # }
            # response = httpx.get(url, params=params)
            # data = response.json()
            #
            # if data["status"] == "OK":
            #     element = data["rows"][0]["elements"][0]
            #     resultado = {
            #         "distancia_km": element["distance"]["value"] / 1000,
            #         "duracao_minutos": element["duration"]["value"] // 60,
            #     }
            #     self._cache_distancias[cache_key] = resultado
            #     return resultado

            logger.debug(f"Google Maps API não configurada, usando cálculo local")
            return None

        except Exception as e:
            logger.error(f"Erro ao consultar Google Maps: {e}")
            return None

    # =========================================================================
    # REOTIMIZAÇÃO EM TEMPO REAL
    # =========================================================================

    def reotimizar_rota(
        self,
        tecnico_id: UUID,
        data: date,
        ponto_atual_latitude: float,
        ponto_atual_longitude: float,
        os_concluidas: Optional[List[UUID]] = None,
    ) -> RoteiroOtimizado:
        """
        Reotimiza a rota considerando posição atual e OS já concluídas.

        Args:
            tecnico_id: ID do técnico
            data: Data do roteiro
            ponto_atual_latitude: Latitude atual do técnico
            ponto_atual_longitude: Longitude atual do técnico
            os_concluidas: Lista de IDs de OS já concluídas

        Returns:
            RoteiroOtimizado atualizado
        """
        os_concluidas = os_concluidas or []

        # Criar ponto de partida atual
        ponto_partida = {
            "endereco": "Posição Atual",
            "latitude": ponto_atual_latitude,
            "longitude": ponto_atual_longitude,
        }

        # Otimizar excluindo OS concluídas
        roteiro = self.otimizar_rota_tecnico(
            tecnico_id=tecnico_id,
            data=data,
            ponto_partida=ponto_partida,
        )

        # Filtrar OS já concluídas
        roteiro.pontos = [
            p for p in roteiro.pontos
            if p.ordem_servico_id not in os_concluidas
        ]

        # Recalcular trechos
        roteiro.trechos = self._calcular_trechos(roteiro.pontos)

        # Recalcular totais
        roteiro.distancia_total_km = sum(t.distancia_km for t in roteiro.trechos)
        duracao_deslocamento = sum(t.duracao_minutos for t in roteiro.trechos)
        duracao_servicos = sum(p.duracao_estimada_minutos for p in roteiro.pontos if p.tipo != "base")
        roteiro.duracao_total_minutos = duracao_deslocamento + duracao_servicos

        return roteiro

    # =========================================================================
    # ANÁLISE E ESTATÍSTICAS
    # =========================================================================

    def analisar_rotas_equipe(
        self,
        data: date,
        tecnico_ids: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Analisa rotas de toda a equipe para um dia.

        Args:
            data: Data de análise
            tecnico_ids: Lista de técnicos (default: todos)

        Returns:
            Dict com análise consolidada
        """
        from modules.campo.models.campo_tecnico import CampoTecnico

        # Buscar técnicos
        query = self.db.query(CampoTecnico).filter(CampoTecnico.is_active == True)
        if tecnico_ids:
            query = query.filter(CampoTecnico.id.in_(tecnico_ids))

        tecnicos = query.all()

        resultados = {
            "data": data.isoformat(),
            "tecnicos_analisados": len(tecnicos),
            "rotas": [],
            "totais": {
                "total_os": 0,
                "total_visitas": 0,
                "distancia_total_km": 0,
                "duracao_total_minutos": 0,
                "economia_estimada_km": 0,
            },
        }

        for tecnico in tecnicos:
            try:
                roteiro = self.otimizar_rota_tecnico(
                    tecnico_id=tecnico.id,
                    data=data,
                )

                qtd_os = len([p for p in roteiro.pontos if p.tipo == "os"])
                qtd_visitas = len([p for p in roteiro.pontos if p.tipo == "visita"])

                resultados["rotas"].append({
                    "tecnico_id": str(tecnico.id),
                    "tecnico_nome": roteiro.tecnico_nome,
                    "qtd_os": qtd_os,
                    "qtd_visitas": qtd_visitas,
                    "distancia_km": roteiro.distancia_total_km,
                    "duracao_minutos": roteiro.duracao_total_minutos,
                    "hora_inicio": roteiro.hora_inicio_sugerida.isoformat(),
                    "hora_fim": roteiro.hora_fim_estimada.isoformat(),
                    "economia_km": roteiro.economia_km,
                })

                resultados["totais"]["total_os"] += qtd_os
                resultados["totais"]["total_visitas"] += qtd_visitas
                resultados["totais"]["distancia_total_km"] += roteiro.distancia_total_km
                resultados["totais"]["duracao_total_minutos"] += roteiro.duracao_total_minutos
                if roteiro.economia_km:
                    resultados["totais"]["economia_estimada_km"] += roteiro.economia_km

            except Exception as e:
                logger.error(f"Erro ao analisar rota do técnico {tecnico.id}: {e}")
                resultados["rotas"].append({
                    "tecnico_id": str(tecnico.id),
                    "erro": str(e),
                })

        return resultados

    def sugerir_redistribuicao(
        self,
        data: date,
        tecnico_ids: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Sugere redistribuição de OS entre técnicos para balancear carga.

        Args:
            data: Data de análise
            tecnico_ids: Lista de técnicos

        Returns:
            Dict com sugestões de redistribuição
        """
        analise = self.analisar_rotas_equipe(data, tecnico_ids)

        rotas_validas = [r for r in analise["rotas"] if "erro" not in r]

        if len(rotas_validas) < 2:
            return {
                "redistribuicao_necessaria": False,
                "motivo": "Poucos técnicos para redistribuir",
            }

        # Calcular média de carga
        media_os = analise["totais"]["total_os"] / len(rotas_validas)
        media_distancia = analise["totais"]["distancia_total_km"] / len(rotas_validas)

        # Identificar técnicos sobrecarregados e subutilizados
        sobrecarregados = [
            r for r in rotas_validas
            if r["qtd_os"] > media_os * 1.3 or r["distancia_km"] > media_distancia * 1.3
        ]

        subutilizados = [
            r for r in rotas_validas
            if r["qtd_os"] < media_os * 0.7 and r["distancia_km"] < media_distancia * 0.7
        ]

        sugestoes = []

        for sobre in sobrecarregados:
            for sub in subutilizados:
                if sobre["qtd_os"] > sub["qtd_os"] + 2:
                    sugestoes.append({
                        "de_tecnico": sobre["tecnico_nome"],
                        "para_tecnico": sub["tecnico_nome"],
                        "motivo": f"Balancear carga ({sobre['qtd_os']} OS vs {sub['qtd_os']} OS)",
                        "economia_potencial_km": round(
                            (sobre["distancia_km"] - media_distancia) * 0.3, 2
                        ),
                    })

        return {
            "redistribuicao_necessaria": len(sugestoes) > 0,
            "media_os_por_tecnico": round(media_os, 1),
            "media_distancia_km": round(media_distancia, 2),
            "tecnicos_sobrecarregados": len(sobrecarregados),
            "tecnicos_subutilizados": len(subutilizados),
            "sugestoes": sugestoes,
        }


# Singleton
def get_roteirizacao_service(db: Session, google_maps_api_key: Optional[str] = None) -> RoteirizacaoService:
    """Factory function para obter instância do serviço."""
    return RoteirizacaoService(db, google_maps_api_key)
