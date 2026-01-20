"""
Pattern Analyzer Service - Sprint 45

Servico para analise de padroes comportamentais e deteccao de anomalias.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from collections import defaultdict
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from modules.ai.fraud_detection.models.fraud_pattern import (
    FraudPattern,
    PatternType,
    PatternStatus,
)
from modules.ai.fraud_detection.models.risk_profile import RiskProfile, EntityType

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analisador de padroes comportamentais."""

    # Limiares padrao
    DEFAULT_VELOCITY_THRESHOLD = 5  # transacoes por periodo
    DEFAULT_VELOCITY_PERIOD_MINUTES = 60
    DEFAULT_AMOUNT_DEVIATION_THRESHOLD = 3.0  # desvios padrao
    DEFAULT_TIME_ANOMALY_HOURS = [0, 1, 2, 3, 4, 5]  # horarios suspeitos

    def __init__(self, db: Session):
        """Inicializa o analisador."""
        self.db = db

    async def analyze_transaction_patterns(
        self,
        entity_type: str,
        entity_id: UUID,
        transaction_data: Dict[str, Any],
        historical_transactions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analisa padroes de transacao para detectar anomalias.

        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade
            transaction_data: Dados da transacao atual
            historical_transactions: Historico de transacoes

        Returns:
            Resultado da analise com padroes detectados
        """
        result = {
            "patterns_detected": [],
            "anomalies": [],
            "risk_indicators": [],
            "confidence_scores": {},
            "total_risk_score": 0.0,
        }

        try:
            # Obter perfil de risco
            profile = await self._get_or_create_profile(entity_type, entity_id)

            # Analises
            velocity_result = await self._analyze_velocity(
                entity_id, transaction_data, profile
            )
            amount_result = await self._analyze_amount_pattern(
                transaction_data, historical_transactions, profile
            )
            time_result = await self._analyze_time_pattern(transaction_data, profile)
            location_result = await self._analyze_location_pattern(
                transaction_data, profile
            )
            recipient_result = await self._analyze_recipient_pattern(
                transaction_data, historical_transactions
            )

            # Consolidar resultados
            all_results = [
                velocity_result,
                amount_result,
                time_result,
                location_result,
                recipient_result,
            ]

            for analysis in all_results:
                if analysis.get("anomaly_detected"):
                    result["anomalies"].append(analysis.get("anomaly_type"))
                    result["patterns_detected"].extend(
                        analysis.get("matched_patterns", [])
                    )
                    result["risk_indicators"].extend(
                        analysis.get("risk_indicators", [])
                    )
                    result["confidence_scores"][analysis.get("analysis_type")] = (
                        analysis.get("confidence", 0)
                    )

            # Calcular score total
            result["total_risk_score"] = self._calculate_combined_score(all_results)

            # Verificar padroes conhecidos
            known_patterns = await self._match_known_patterns(
                transaction_data, result["anomalies"]
            )
            result["patterns_detected"].extend(known_patterns)

            logger.info(
                f"Analise de padroes concluida para {entity_type}:{entity_id} - "
                f"Score: {result['total_risk_score']:.2f}"
            )

        except Exception as e:
            logger.error(f"Erro na analise de padroes: {e}")
            result["error"] = str(e)

        return result

    async def analyze_access_patterns(
        self,
        user_id: UUID,
        access_data: Dict[str, Any],
        historical_accesses: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analisa padroes de acesso para detectar comportamento anomalo.

        Args:
            user_id: ID do usuario
            access_data: Dados do acesso atual
            historical_accesses: Historico de acessos

        Returns:
            Resultado da analise
        """
        result = {
            "patterns_detected": [],
            "anomalies": [],
            "risk_indicators": [],
            "is_new_device": False,
            "is_new_location": False,
            "is_unusual_time": False,
            "total_risk_score": 0.0,
        }

        try:
            profile = await self._get_or_create_profile("user", user_id)

            # Verificar dispositivo
            device_id = access_data.get("device_id")
            if device_id:
                known_devices = profile.known_devices or []
                if device_id not in known_devices:
                    result["is_new_device"] = True
                    result["anomalies"].append("new_device")
                    result["risk_indicators"].append(
                        f"Novo dispositivo: {device_id[:8]}..."
                    )

            # Verificar IP
            ip_address = access_data.get("ip_address")
            if ip_address:
                known_ips = profile.known_ips or []
                if ip_address not in known_ips:
                    result["anomalies"].append("new_ip")
                    result["risk_indicators"].append(f"Novo IP: {ip_address}")

            # Verificar localizacao
            location = access_data.get("location")
            if location:
                known_locations = profile.known_locations or []
                if location not in known_locations:
                    result["is_new_location"] = True
                    result["anomalies"].append("new_location")
                    result["risk_indicators"].append(f"Nova localizacao: {location}")

            # Verificar horario
            access_hour = datetime.now().hour
            typical_hours = profile.typical_hours or list(range(6, 23))
            if access_hour not in typical_hours:
                result["is_unusual_time"] = True
                result["anomalies"].append("unusual_time")
                result["risk_indicators"].append(f"Horario incomum: {access_hour}h")

            # Verificar velocidade de login
            login_velocity = await self._check_login_velocity(user_id)
            if login_velocity.get("exceeded"):
                result["anomalies"].append("excessive_logins")
                result["patterns_detected"].append("credential_stuffing")
                result["risk_indicators"].append(
                    f"Muitos logins: {login_velocity.get('count')} em "
                    f"{login_velocity.get('period_minutes')} min"
                )

            # Verificar viagem impossivel
            if historical_accesses:
                impossible_travel = await self._check_impossible_travel(
                    access_data, historical_accesses
                )
                if impossible_travel.get("detected"):
                    result["anomalies"].append("impossible_travel")
                    result["patterns_detected"].append("account_takeover")
                    result["risk_indicators"].append(
                        f"Viagem impossivel: {impossible_travel.get('distance_km')}km "
                        f"em {impossible_travel.get('time_minutes')} min"
                    )

            # Calcular score
            result["total_risk_score"] = self._calculate_access_risk_score(result)

        except Exception as e:
            logger.error(f"Erro na analise de acesso: {e}")
            result["error"] = str(e)

        return result

    async def detect_fraud_pattern(
        self,
        pattern_type: PatternType,
        data: Dict[str, Any],
        indicators: List[str],
    ) -> Dict[str, Any]:
        """
        Detecta um padrao de fraude especifico.

        Args:
            pattern_type: Tipo de padrao a detectar
            data: Dados para analise
            indicators: Indicadores presentes

        Returns:
            Resultado da deteccao
        """
        result = {
            "matched": False,
            "pattern_type": pattern_type.value,
            "confidence": 0.0,
            "indicators_found": [],
            "risk_score": 0.0,
        }

        try:
            # Buscar padrao ativo do tipo
            pattern = (
                self.db.query(FraudPattern)
                .filter(
                    FraudPattern.pattern_type == pattern_type,
                    FraudPattern.is_active == True,
                    FraudPattern.status == PatternStatus.ACTIVE,
                )
                .first()
            )

            if not pattern:
                return result

            # Verificar match
            match_result = pattern.match(data, indicators)

            if match_result["matched"]:
                result["matched"] = True
                result["pattern_id"] = str(pattern.id)
                result["pattern_name"] = pattern.name
                result["confidence"] = match_result["confidence"]
                result["indicators_found"] = match_result["matched_indicators"]
                result["risk_score"] = (
                    pattern.risk_score * match_result["confidence"]
                )

                # Registrar deteccao
                pattern.record_detection(is_confirmed=False)
                self.db.commit()

        except Exception as e:
            logger.error(f"Erro na deteccao de padrao {pattern_type}: {e}")
            self.db.rollback()

        return result

    async def _analyze_velocity(
        self,
        entity_id: UUID,
        transaction_data: Dict[str, Any],
        profile: RiskProfile,
    ) -> Dict[str, Any]:
        """Analisa velocidade de transacoes."""
        result = {
            "analysis_type": "velocity",
            "anomaly_detected": False,
            "anomaly_type": None,
            "confidence": 0.0,
            "risk_indicators": [],
            "matched_patterns": [],
        }

        try:
            # Contar transacoes recentes
            period_minutes = self.DEFAULT_VELOCITY_PERIOD_MINUTES
            threshold = self.DEFAULT_VELOCITY_THRESHOLD

            # Usar historico do perfil
            recent_count = profile.transactions_today or 0

            if recent_count >= threshold:
                result["anomaly_detected"] = True
                result["anomaly_type"] = "high_velocity"
                result["confidence"] = min(1.0, recent_count / (threshold * 2))
                result["risk_indicators"].append(
                    f"Alta velocidade: {recent_count} transacoes em {period_minutes}min"
                )
                result["matched_patterns"].append("velocity_abuse")

        except Exception as e:
            logger.error(f"Erro na analise de velocidade: {e}")

        return result

    async def _analyze_amount_pattern(
        self,
        transaction_data: Dict[str, Any],
        historical: Optional[List[Dict[str, Any]]],
        profile: RiskProfile,
    ) -> Dict[str, Any]:
        """Analisa padrao de valores."""
        result = {
            "analysis_type": "amount",
            "anomaly_detected": False,
            "anomaly_type": None,
            "confidence": 0.0,
            "risk_indicators": [],
            "matched_patterns": [],
        }

        try:
            current_amount = transaction_data.get("amount", 0)

            if historical and len(historical) >= 5:
                amounts = [t.get("amount", 0) for t in historical if t.get("amount")]
                if amounts:
                    avg = statistics.mean(amounts)
                    std = statistics.stdev(amounts) if len(amounts) > 1 else avg * 0.2

                    if std > 0:
                        z_score = abs(current_amount - avg) / std
                        if z_score > self.DEFAULT_AMOUNT_DEVIATION_THRESHOLD:
                            result["anomaly_detected"] = True
                            result["anomaly_type"] = "unusual_amount"
                            result["confidence"] = min(1.0, z_score / 5)
                            result["risk_indicators"].append(
                                f"Valor atipico: R${current_amount:.2f} "
                                f"(media: R${avg:.2f}, desvio: {z_score:.1f}σ)"
                            )
            else:
                # Usar perfil
                avg = profile.avg_transaction_value or 0
                if avg > 0 and current_amount > avg * 3:
                    result["anomaly_detected"] = True
                    result["anomaly_type"] = "unusual_amount"
                    result["confidence"] = 0.6
                    result["risk_indicators"].append(
                        f"Valor 3x acima da media: R${current_amount:.2f}"
                    )

        except Exception as e:
            logger.error(f"Erro na analise de valor: {e}")

        return result

    async def _analyze_time_pattern(
        self,
        transaction_data: Dict[str, Any],
        profile: RiskProfile,
    ) -> Dict[str, Any]:
        """Analisa padrao temporal."""
        result = {
            "analysis_type": "time",
            "anomaly_detected": False,
            "anomaly_type": None,
            "confidence": 0.0,
            "risk_indicators": [],
            "matched_patterns": [],
        }

        try:
            current_hour = datetime.now().hour
            typical_hours = profile.typical_hours or list(range(6, 23))

            if current_hour in self.DEFAULT_TIME_ANOMALY_HOURS:
                if current_hour not in typical_hours:
                    result["anomaly_detected"] = True
                    result["anomaly_type"] = "unusual_time"
                    result["confidence"] = 0.5
                    result["risk_indicators"].append(
                        f"Transacao em horario incomum: {current_hour}h"
                    )

        except Exception as e:
            logger.error(f"Erro na analise temporal: {e}")

        return result

    async def _analyze_location_pattern(
        self,
        transaction_data: Dict[str, Any],
        profile: RiskProfile,
    ) -> Dict[str, Any]:
        """Analisa padrao de localizacao."""
        result = {
            "analysis_type": "location",
            "anomaly_detected": False,
            "anomaly_type": None,
            "confidence": 0.0,
            "risk_indicators": [],
            "matched_patterns": [],
        }

        try:
            location = transaction_data.get("location")
            ip_address = transaction_data.get("ip_address")

            if location:
                known_locations = profile.known_locations or []
                if location not in known_locations and known_locations:
                    result["anomaly_detected"] = True
                    result["anomaly_type"] = "new_location"
                    result["confidence"] = 0.4
                    result["risk_indicators"].append(f"Nova localizacao: {location}")

            if ip_address:
                known_ips = profile.known_ips or []
                if ip_address not in known_ips and known_ips:
                    result["risk_indicators"].append(f"Novo IP: {ip_address}")

        except Exception as e:
            logger.error(f"Erro na analise de localizacao: {e}")

        return result

    async def _analyze_recipient_pattern(
        self,
        transaction_data: Dict[str, Any],
        historical: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Analisa padrao de destinatarios."""
        result = {
            "analysis_type": "recipient",
            "anomaly_detected": False,
            "anomaly_type": None,
            "confidence": 0.0,
            "risk_indicators": [],
            "matched_patterns": [],
        }

        try:
            payee_id = transaction_data.get("payee_id")

            if payee_id and historical:
                known_payees = {t.get("payee_id") for t in historical if t.get("payee_id")}
                if payee_id not in known_payees and len(known_payees) >= 3:
                    result["anomaly_detected"] = True
                    result["anomaly_type"] = "new_recipient"
                    result["confidence"] = 0.3
                    result["risk_indicators"].append("Novo destinatario")

        except Exception as e:
            logger.error(f"Erro na analise de destinatario: {e}")

        return result

    async def _check_login_velocity(self, user_id: UUID) -> Dict[str, Any]:
        """Verifica velocidade de tentativas de login."""
        # Simplificado - em producao, consultar logs de auth
        return {
            "exceeded": False,
            "count": 0,
            "period_minutes": 15,
            "threshold": 10,
        }

    async def _check_impossible_travel(
        self,
        current_access: Dict[str, Any],
        historical: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Verifica viagem impossivel (localizacoes distantes em pouco tempo)."""
        result = {
            "detected": False,
            "distance_km": 0,
            "time_minutes": 0,
        }

        try:
            current_coords = current_access.get("geo_coordinates")
            if not current_coords or not historical:
                return result

            # Pegar ultimo acesso
            last_access = historical[-1] if historical else None
            if not last_access:
                return result

            last_coords = last_access.get("geo_coordinates")
            last_time = last_access.get("timestamp")

            if not last_coords or not last_time:
                return result

            # Calcular distancia (formula de Haversine simplificada)
            from math import radians, sin, cos, sqrt, atan2

            lat1 = radians(current_coords.get("lat", 0))
            lon1 = radians(current_coords.get("lon", 0))
            lat2 = radians(last_coords.get("lat", 0))
            lon2 = radians(last_coords.get("lon", 0))

            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance_km = 6371 * c  # Raio da Terra

            # Calcular tempo
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time)
            time_diff = datetime.now() - last_time
            time_minutes = time_diff.total_seconds() / 60

            # Velocidade maxima razoavel: ~900 km/h (aviao)
            max_distance = (time_minutes / 60) * 900

            if distance_km > max_distance and distance_km > 100:
                result["detected"] = True
                result["distance_km"] = round(distance_km, 1)
                result["time_minutes"] = round(time_minutes, 1)

        except Exception as e:
            logger.error(f"Erro ao verificar viagem impossivel: {e}")

        return result

    async def _match_known_patterns(
        self,
        transaction_data: Dict[str, Any],
        anomalies: List[str],
    ) -> List[str]:
        """Verifica se as anomalias correspondem a padroes conhecidos."""
        matched = []

        # Mapeamento de anomalias para padroes
        anomaly_patterns = {
            "high_velocity": ["velocity_abuse", "split_transaction"],
            "unusual_amount": ["amount_manipulation", "structuring"],
            "unusual_time": ["after_hours_access"],
            "new_location": ["geo_anomaly"],
            "new_device": ["device_spoofing"],
            "impossible_travel": ["account_takeover", "credential_theft"],
        }

        for anomaly in anomalies:
            patterns = anomaly_patterns.get(anomaly, [])
            matched.extend(patterns)

        return list(set(matched))

    def _calculate_combined_score(self, results: List[Dict[str, Any]]) -> float:
        """Calcula score combinado das analises."""
        total_score = 0.0
        weights = {
            "velocity": 0.25,
            "amount": 0.25,
            "time": 0.15,
            "location": 0.20,
            "recipient": 0.15,
        }

        for r in results:
            analysis_type = r.get("analysis_type", "")
            weight = weights.get(analysis_type, 0.1)
            if r.get("anomaly_detected"):
                confidence = r.get("confidence", 0.5)
                total_score += weight * confidence * 100

        return min(100.0, total_score)

    def _calculate_access_risk_score(self, result: Dict[str, Any]) -> float:
        """Calcula score de risco de acesso."""
        score = 0.0

        if result.get("is_new_device"):
            score += 20
        if result.get("is_new_location"):
            score += 15
        if result.get("is_unusual_time"):
            score += 10

        anomaly_scores = {
            "new_ip": 10,
            "excessive_logins": 30,
            "impossible_travel": 50,
            "credential_stuffing": 40,
            "account_takeover": 60,
        }

        for anomaly in result.get("anomalies", []):
            score += anomaly_scores.get(anomaly, 5)

        return min(100.0, score)

    async def _get_or_create_profile(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> RiskProfile:
        """Obtem ou cria perfil de risco."""
        try:
            entity_type_enum = EntityType(entity_type)
        except ValueError:
            entity_type_enum = EntityType.USUARIO

        profile = (
            self.db.query(RiskProfile)
            .filter(
                RiskProfile.entity_type == entity_type_enum,
                RiskProfile.entity_id == entity_id,
            )
            .first()
        )

        if not profile:
            profile = RiskProfile(
                entity_type=entity_type_enum,
                entity_id=entity_id,
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        return profile
