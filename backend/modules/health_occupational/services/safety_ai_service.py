"""
Safety AI Service - Saúde Ocupacional Preditiva
===============================================
Sistema de IA para previsão e prevenção de acidentes de trabalho.
Target: Zero acidentes através de análise preditiva.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Simulação de imports ML (será instalado depois)
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
except ImportError:
    # Fallback para desenvolvimento
    RandomForestClassifier = None
    GradientBoostingRegressor = None
    StandardScaler = None

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Níveis de risco de segurança."""
    MUITO_BAIXO = "muito_baixo"
    BAIXO = "baixo" 
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class AccidentType(Enum):
    """Tipos de acidentes previsíveis."""
    QUEDA = "queda"
    CORTE = "corte"
    QUEIMADURA = "queimadura"
    LESAO_REPETITIVA = "lesao_repetitiva"
    IMPACTO = "impacto"
    EXPOSICAO_QUIMICA = "exposicao_quimica"


@dataclass
class SafetyRiskAssessment:
    """Resultado da avaliação de risco."""
    employee_id: str
    risk_level: RiskLevel
    risk_score: float  # 0-100
    predicted_accidents: List[AccidentType]
    recommendations: List[str]
    urgent_actions: List[str]
    confidence: float
    assessment_date: datetime


@dataclass
class AccidentPrediction:
    """Previsão específica de acidente."""
    accident_type: AccidentType
    probability: float  # 0-1
    predicted_date_range: Tuple[datetime, datetime]
    contributing_factors: List[str]
    prevention_measures: List[str]


class SafetyAIService:
    """Serviço de IA para Saúde Ocupacional Preditiva."""

    def __init__(self):
        """Inicializa o serviço de IA de segurança."""
        self.risk_model: Optional[RandomForestClassifier] = None
        self.accident_prediction_model: Optional[GradientBoostingRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        
        # Cache de análises
        self._risk_cache: Dict[str, SafetyRiskAssessment] = {}
        self._prediction_cache: Dict[str, List[AccidentPrediction]] = {}
        
        logger.info("Safety AI Service inicializado")

    # ========================================
    # 1. RISK ASSESSMENT ENGINE
    # ========================================

    async def assess_employee_risk(
        self,
        employee_id: str,
        work_conditions: Dict[str, Any],
        health_data: Dict[str, Any],
        historical_incidents: List[Dict[str, Any]] = None
    ) -> SafetyRiskAssessment:
        """
        Avalia risco de segurança de um funcionário.
        Target: Prevenção proativa de acidentes.
        """
        try:
            logger.info(f"Avaliando risco de segurança: {employee_id}")
            
            # Verificar cache
            cache_key = f"{employee_id}_{datetime.now().date()}"
            if cache_key in self._risk_cache:
                return self._risk_cache[cache_key]
            
            # Extrair features para análise
            features = self._extract_safety_features(
                work_conditions, health_data, historical_incidents or []
            )
            
            # Calcular score de risco
            risk_score = self._calculate_risk_score(features)
            
            # Determinar nível de risco
            risk_level = self._determine_risk_level(risk_score)
            
            # Prever tipos de acidentes prováveis
            predicted_accidents = self._predict_accident_types(features)
            
            # Gerar recomendações
            recommendations = self._generate_safety_recommendations(
                risk_level, predicted_accidents, features
            )
            
            # Ações urgentes se necessário
            urgent_actions = self._identify_urgent_actions(risk_level, features)
            
            # Calcular confiança
            confidence = self._calculate_assessment_confidence(features)
            
            assessment = SafetyRiskAssessment(
                employee_id=employee_id,
                risk_level=risk_level,
                risk_score=risk_score,
                predicted_accidents=predicted_accidents,
                recommendations=recommendations,
                urgent_actions=urgent_actions,
                confidence=confidence,
                assessment_date=datetime.now()
            )
            
            # Cache do resultado
            self._risk_cache[cache_key] = assessment
            
            logger.info(f"Avaliação concluída: {risk_level.value} ({risk_score:.1f})")
            return assessment
            
        except Exception as e:
            logger.error(f"Erro na avaliação de risco: {e}")
            # Retornar avaliação de segurança básica
            return SafetyRiskAssessment(
                employee_id=employee_id,
                risk_level=RiskLevel.MEDIO,
                risk_score=50.0,
                predicted_accidents=[],
                recommendations=["Realizar avaliação manual detalhada"],
                urgent_actions=[],
                confidence=0.3,
                assessment_date=datetime.now()
            )

    def _extract_safety_features(
        self,
        work_conditions: Dict[str, Any],
        health_data: Dict[str, Any], 
        historical_incidents: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extrai features para análise de segurança."""
        try:
            features = {}
            
            # Features de condições de trabalho
            features["work_height"] = float(work_conditions.get("height_meters", 0))
            features["noise_level"] = float(work_conditions.get("noise_db", 50))
            features["temperature"] = float(work_conditions.get("temperature_c", 25))
            features["chemical_exposure"] = float(work_conditions.get("chemical_exposure_level", 0))
            features["machinery_risk"] = float(work_conditions.get("machinery_risk_score", 0))
            features["work_hours_per_day"] = float(work_conditions.get("daily_hours", 8))
            
            # Features de saúde
            features["age"] = float(health_data.get("age", 35))
            features["experience_years"] = float(health_data.get("experience_years", 5))
            features["health_score"] = float(health_data.get("overall_health_score", 80))
            features["vision_score"] = float(health_data.get("vision_score", 100))
            features["hearing_score"] = float(health_data.get("hearing_score", 100))
            features["fatigue_level"] = float(health_data.get("fatigue_level", 20))
            
            # Features de histórico
            features["incidents_last_year"] = float(len(historical_incidents))
            features["days_since_last_incident"] = float(
                (datetime.now() - datetime.fromisoformat(
                    historical_incidents[0].get("date", datetime.now().isoformat())
                )).days if historical_incidents else 365
            )
            
            # Features calculadas
            features["risk_multiplier"] = (
                features["work_height"] * 0.1 +
                features["chemical_exposure"] * 0.2 +
                features["machinery_risk"] * 0.15
            )
            
            features["fatigue_risk"] = min(100, 
                features["fatigue_level"] * 
                (features["work_hours_per_day"] / 8)
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Erro na extração de features: {e}")
            # Features padrão seguras
            return {
                "work_height": 0, "noise_level": 50, "temperature": 25,
                "age": 35, "experience_years": 5, "health_score": 80,
                "incidents_last_year": 0, "risk_multiplier": 0, "fatigue_risk": 20
            }

    def _calculate_risk_score(self, features: Dict[str, float]) -> float:
        """Calcula score de risco (0-100)."""
        try:
            if self.risk_model and RandomForestClassifier:
                # Usar modelo ML treinado
                feature_vector = np.array(list(features.values())).reshape(1, -1)
                if self.scaler:
                    feature_vector = self.scaler.transform(feature_vector)
                risk_proba = self.risk_model.predict_proba(feature_vector)[0]
                return float(risk_proba[1]) * 100  # Probabilidade de risco alto
            else:
                # Algoritmo baseado em regras
                return self._rule_based_risk_calculation(features)
                
        except Exception as e:
            logger.error(f"Erro no cálculo de risco: {e}")
            return 50.0  # Risco médio por segurança

    def _rule_based_risk_calculation(self, features: Dict[str, float]) -> float:
        """Cálculo de risco baseado em regras de negócio."""
        score = 30.0  # Base score
        
        # Fatores de aumento de risco
        if features.get("work_height", 0) > 2:
            score += min(20, features["work_height"] * 3)
        
        if features.get("chemical_exposure", 0) > 5:
            score += min(25, features["chemical_exposure"] * 2)
        
        if features.get("machinery_risk", 0) > 3:
            score += min(20, features["machinery_risk"] * 4)
        
        if features.get("fatigue_level", 0) > 70:
            score += min(15, (features["fatigue_level"] - 70) * 0.5)
        
        # Fatores de redução de risco
        experience = features.get("experience_years", 0)
        if experience > 5:
            score -= min(10, (experience - 5) * 1.5)
        
        health_score = features.get("health_score", 80)
        if health_score > 90:
            score -= 5
        
        # Histórico de incidentes
        incidents = features.get("incidents_last_year", 0)
        if incidents > 0:
            score += min(20, incidents * 8)
        
        return max(0.0, min(100.0, score))

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determina nível de risco baseado no score."""
        if risk_score >= 80:
            return RiskLevel.CRITICO
        elif risk_score >= 65:
            return RiskLevel.ALTO
        elif risk_score >= 45:
            return RiskLevel.MEDIO
        elif risk_score >= 25:
            return RiskLevel.BAIXO
        else:
            return RiskLevel.MUITO_BAIXO

    def _predict_accident_types(self, features: Dict[str, float]) -> List[AccidentType]:
        """Prediz tipos de acidentes mais prováveis."""
        predictions = []
        
        # Regras baseadas em features
        if features.get("work_height", 0) > 1.5:
            predictions.append(AccidentType.QUEDA)
        
        if features.get("machinery_risk", 0) > 2:
            predictions.extend([AccidentType.CORTE, AccidentType.IMPACTO])
        
        if features.get("chemical_exposure", 0) > 3:
            predictions.extend([AccidentType.QUEIMADURA, AccidentType.EXPOSICAO_QUIMICA])
        
        if features.get("fatigue_level", 0) > 60:
            predictions.append(AccidentType.LESAO_REPETITIVA)
        
        return list(set(predictions))  # Remove duplicatas

    # ========================================
    # 2. ACCIDENT PREDICTION ENGINE
    # ========================================

    async def predict_accidents(
        self,
        workplace_data: Dict[str, Any],
        employee_data: List[Dict[str, Any]],
        prediction_horizon_days: int = 30
    ) -> List[AccidentPrediction]:
        """
        Prediz acidentes potenciais no ambiente de trabalho.
        """
        try:
            logger.info(f"Predizendo acidentes para {prediction_horizon_days} dias")
            
            predictions = []
            
            # Analisar cada tipo de acidente potencial
            for accident_type in AccidentType:
                prediction = self._predict_specific_accident(
                    accident_type, workplace_data, employee_data, prediction_horizon_days
                )
                if prediction and prediction.probability > 0.1:  # > 10% probabilidade
                    predictions.append(prediction)
            
            # Ordenar por probabilidade
            predictions.sort(key=lambda x: x.probability, reverse=True)
            
            logger.info(f"Identificadas {len(predictions)} previsões de acidentes")
            return predictions
            
        except Exception as e:
            logger.error(f"Erro na previsão de acidentes: {e}")
            return []

    def _predict_specific_accident(
        self,
        accident_type: AccidentType,
        workplace_data: Dict[str, Any],
        employee_data: List[Dict[str, Any]],
        horizon_days: int
    ) -> Optional[AccidentPrediction]:
        """Prediz acidente específico."""
        try:
            # Calcular probabilidade baseada no tipo de acidente
            probability = self._calculate_accident_probability(
                accident_type, workplace_data, employee_data
            )
            
            if probability < 0.1:  # Muito baixa
                return None
            
            # Estimar janela temporal
            start_date = datetime.now()
            end_date = start_date + timedelta(days=horizon_days)
            
            # Identificar fatores contribuintes
            factors = self._identify_contributing_factors(accident_type, workplace_data)
            
            # Gerar medidas preventivas
            prevention_measures = self._generate_prevention_measures(accident_type, factors)
            
            return AccidentPrediction(
                accident_type=accident_type,
                probability=probability,
                predicted_date_range=(start_date, end_date),
                contributing_factors=factors,
                prevention_measures=prevention_measures
            )
            
        except Exception as e:
            logger.error(f"Erro na previsão específica: {e}")
            return None

    def _calculate_accident_probability(
        self,
        accident_type: AccidentType,
        workplace_data: Dict[str, Any],
        employee_data: List[Dict[str, Any]]
    ) -> float:
        """Calcula probabilidade de acidente específico."""
        base_probabilities = {
            AccidentType.QUEDA: 0.05,
            AccidentType.CORTE: 0.08,
            AccidentType.QUEIMADURA: 0.03,
            AccidentType.LESAO_REPETITIVA: 0.12,
            AccidentType.IMPACTO: 0.06,
            AccidentType.EXPOSICAO_QUIMICA: 0.02
        }
        
        base_prob = base_probabilities.get(accident_type, 0.05)
        
        # Multiplicadores baseados em condições
        multiplier = 1.0
        
        if accident_type == AccidentType.QUEDA:
            height_risk = workplace_data.get("average_work_height", 0)
            multiplier *= (1 + height_risk * 0.3)
        
        elif accident_type == AccidentType.CORTE:
            machinery_risk = workplace_data.get("machinery_complexity", 0)
            multiplier *= (1 + machinery_risk * 0.25)
        
        elif accident_type == AccidentType.LESAO_REPETITIVA:
            avg_fatigue = np.mean([emp.get("fatigue_level", 30) for emp in employee_data])
            multiplier *= (1 + max(0, avg_fatigue - 50) * 0.02)
        
        return min(0.9, base_prob * multiplier)

    # ========================================
    # 3. SAFETY RECOMMENDATIONS
    # ========================================

    def _generate_safety_recommendations(
        self,
        risk_level: RiskLevel,
        predicted_accidents: List[AccidentType],
        features: Dict[str, float]
    ) -> List[str]:
        """Gera recomendações de segurança específicas."""
        recommendations = []
        
        # Recomendações por nível de risco
        if risk_level in [RiskLevel.CRITICO, RiskLevel.ALTO]:
            recommendations.extend([
                "🚨 Implementar supervisão intensiva",
                "📋 Revisar procedimentos de segurança imediatamente",
                "🛡️ Verificar EPIs e equipamentos de proteção"
            ])
        
        # Recomendações por tipo de acidente previsto
        for accident_type in predicted_accidents:
            if accident_type == AccidentType.QUEDA:
                recommendations.extend([
                    "🪜 Instalar proteções contra quedas",
                    "👷 Treinamento específico para trabalho em altura"
                ])
            elif accident_type == AccidentType.CORTE:
                recommendations.extend([
                    "🧤 EPIs de proteção para mãos reforçados",
                    "⚙️ Manutenção preventiva em equipamentos cortantes"
                ])
            elif accident_type == AccidentType.LESAO_REPETITIVA:
                recommendations.extend([
                    "💪 Programa de ginástica laboral",
                    "⏰ Pausas regulares para descanso"
                ])
        
        # Recomendações baseadas em features específicas
        if features.get("fatigue_level", 0) > 60:
            recommendations.append("😴 Reduzir carga de trabalho ou aumentar pausas")
        
        if features.get("chemical_exposure", 0) > 5:
            recommendations.append("🧪 Melhorar ventilação e proteção química")
        
        return list(set(recommendations))  # Remove duplicatas

    def _identify_urgent_actions(
        self,
        risk_level: RiskLevel,
        features: Dict[str, float]
    ) -> List[str]:
        """Identifica ações urgentes necessárias."""
        urgent_actions = []
        
        if risk_level == RiskLevel.CRITICO:
            urgent_actions.extend([
                "🚨 PARAR ATIVIDADE IMEDIATAMENTE",
                "📞 Notificar supervisão de segurança",
                "🔍 Investigação detalhada obrigatória"
            ])
        
        elif risk_level == RiskLevel.ALTO:
            urgent_actions.extend([
                "⚠️ Supervisão adicional nas próximas 24h",
                "📋 Checklist de segurança obrigatório",
                "👨‍⚕️ Avaliação médica se necessário"
            ])
        
        # Ações específicas por features críticas
        if features.get("chemical_exposure", 0) > 8:
            urgent_actions.append("☠️ Evacuar área e verificar vazamentos")
        
        if features.get("fatigue_level", 0) > 80:
            urgent_actions.append("😴 Afastamento imediato para descanso")
        
        return urgent_actions

    def _identify_contributing_factors(
        self,
        accident_type: AccidentType,
        workplace_data: Dict[str, Any]
    ) -> List[str]:
        """Identifica fatores contribuintes para acidentes."""
        factors = []
        
        if accident_type == AccidentType.QUEDA:
            if workplace_data.get("wet_floors", False):
                factors.append("Pisos molhados ou escorregadios")
            if workplace_data.get("poor_lighting", False):
                factors.append("Iluminação inadequada")
        
        elif accident_type == AccidentType.LESAO_REPETITIVA:
            if workplace_data.get("repetitive_tasks", 0) > 6:
                factors.append("Alto volume de tarefas repetitivas")
            if workplace_data.get("poor_ergonomics", False):
                factors.append("Ergonomia inadequada do posto de trabalho")
        
        return factors

    def _generate_prevention_measures(
        self,
        accident_type: AccidentType,
        factors: List[str]
    ) -> List[str]:
        """Gera medidas preventivas específicas."""
        measures = []
        
        prevention_map = {
            AccidentType.QUEDA: [
                "Instalar corrimãos e proteções",
                "Manter pisos secos e sinalizados",
                "Melhorar iluminação"
            ],
            AccidentType.CORTE: [
                "Manutenção regular de equipamentos",
                "Treinamento em manuseio seguro",
                "EPIs adequados para mãos"
            ],
            AccidentType.LESAO_REPETITIVA: [
                "Implementar pausas programadas",
                "Rodízio de atividades",
                "Melhoria ergonômica"
            ]
        }
        
        return prevention_map.get(accident_type, ["Avaliação específica necessária"])

    # ========================================
    # 4. ANALYTICS & REPORTING
    # ========================================

    async def generate_safety_analytics(
        self,
        workplace_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Gera analytics de segurança para o ambiente de trabalho."""
        try:
            logger.info(f"Gerando analytics de segurança: {workplace_id}")
            
            # Simular dados analytics
            analytics = {
                "period": {
                    "start_date": (datetime.now() - timedelta(days=period_days)).isoformat(),
                    "end_date": datetime.now().isoformat(),
                    "days": period_days
                },
                "risk_distribution": {
                    "critico": 2,
                    "alto": 5,
                    "medio": 15,
                    "baixo": 25,
                    "muito_baixo": 53
                },
                "predicted_accidents": {
                    "total_predictions": 8,
                    "high_probability": 3,
                    "prevented_actions": 6
                },
                "safety_score": 78.5,  # Score geral de segurança
                "improvement_trend": +12.3,  # Melhoria em %
                "top_risks": [
                    "Trabalho em altura sem proteção adequada",
                    "Fadiga excessiva em turnos longos", 
                    "Exposição química acima do limite"
                ],
                "prevention_effectiveness": 85.2,  # % de acidentes prevenidos
                "recommendations_implemented": 67.8,  # % de recomendações seguidas
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erro na geração de analytics: {e}")
            return {"error": str(e)}

    def _calculate_assessment_confidence(self, features: Dict[str, float]) -> float:
        """Calcula confiança da avaliação."""
        # Confiança baseada na completude dos dados
        required_features = [
            "work_height", "age", "experience_years", 
            "health_score", "incidents_last_year"
        ]
        
        available_features = sum(1 for feat in required_features if feat in features)
        completeness = available_features / len(required_features)
        
        # Confiança base + ajuste por completude
        base_confidence = 0.7
        return min(0.95, base_confidence + (completeness * 0.25))

    # ========================================
    # 5. MODEL TRAINING & OPTIMIZATION
    # ========================================

    async def train_models(self, training_data: List[Dict[str, Any]]) -> bool:
        """Treina modelos ML com dados históricos."""
        try:
            if not RandomForestClassifier:
                logger.warning("scikit-learn não disponível, usando modelos baseados em regras")
                return True
            
            logger.info("Treinando modelos de segurança...")
            
            # Preparar dados de treinamento
            X, y = self._prepare_training_data(training_data)
            
            if len(X) < 10:  # Dados insuficientes
                logger.warning("Dados insuficientes para treinamento ML")
                return False
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Treinar scaler
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo de risco
            self.risk_model = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.risk_model.fit(X_train_scaled, y_train)
            
            # Avaliar performance
            train_score = self.risk_model.score(X_train_scaled, y_train)
            test_score = self.risk_model.score(X_test_scaled, y_test)
            
            logger.info(f"Modelo treinado - Train: {train_score:.3f}, Test: {test_score:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return False

    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados para treinamento."""
        X = []
        y = []
        
        for record in training_data:
            features = self._extract_safety_features(
                record.get("work_conditions", {}),
                record.get("health_data", {}),
                record.get("historical_incidents", [])
            )
            
            X.append(list(features.values()))
            # Label: 1 se houve acidente, 0 caso contrário
            y.append(1 if record.get("had_accident", False) else 0)
        
        return np.array(X), np.array(y)


# ========================================
# FACTORY & UTILITIES
# ========================================

def create_safety_ai_service() -> SafetyAIService:
    """Factory para criar instância do SafetyAIService."""
    return SafetyAIService()


async def quick_safety_check(
    employee_id: str,
    work_conditions: Dict[str, Any]
) -> str:
    """Check rápido de segurança."""
    service = create_safety_ai_service()
    
    assessment = await service.assess_employee_risk(
        employee_id=employee_id,
        work_conditions=work_conditions,
        health_data={"age": 30, "experience_years": 2, "health_score": 85}
    )
    
    if assessment.risk_level == RiskLevel.CRITICO:
        return "🚨 RISCO CRÍTICO - AÇÃO IMEDIATA NECESSÁRIA"
    elif assessment.risk_level == RiskLevel.ALTO:
        return "⚠️ RISCO ALTO - SUPERVISÃO ADICIONAL"
    elif assessment.risk_level == RiskLevel.MEDIO:
        return "⚠️ RISCO MODERADO - MONITORAR"
    else:
        return "✅ SEGURO - CONDIÇÕES ADEQUADAS"

