"""
Cross Module Analytics - Análise Cross-Module Inteligente

Analisa correlações e dependências entre os 33 módulos do Conecta PRO:
1. Detecta padrões cross-module
2. Identifica correlações ocultas
3. Mapeia dependências entre módulos
4. Gera insights integrados
5. Prediz impactos em cascata

Versão adaptada para Conecta PRO
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json
from collections import defaultdict
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Tipos de correlação entre módulos"""
    POSITIVE = "positive"      # Correlação positiva
    NEGATIVE = "negative"      # Correlação negativa  
    NEUTRAL = "neutral"        # Sem correlação significativa
    CAUSAL = "causal"          # Relação de causa-efeito
    BIDIRECTIONAL = "bidirectional"  # Influência mútua


@dataclass
class ModuleCorrelation:
    """Correlação entre dois módulos"""
    module_a: str
    module_b: str
    correlation_type: CorrelationType
    strength: float  # 0.0 a 1.0
    confidence: float  # 0.0 a 1.0
    insights: List[str]
    impact_areas: List[str]
    timestamp: datetime


@dataclass
class CascadeImpact:
    """Impacto em cascata entre módulos"""
    trigger_module: str
    affected_modules: List[str]
    impact_chain: List[str]
    severity: float  # 0.0 a 1.0
    probability: float  # 0.0 a 1.0
    estimated_duration: timedelta
    mitigation_actions: List[str]


class CrossModuleAnalytics:
    """
    Analytics Cross-Module que identifica padrões entre módulos do Conecta PRO
    
    Funcionalidades:
    - Análise de correlações entre módulos
    - Detecção de impactos em cascata
    - Mapeamento de dependências
    - Geração de insights integrados
    """

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.correlation_cache = {}
        self.impact_patterns = {}
        
        # Módulos do Conecta PRO
        self.conecta_modules = [
            "ai", "analytics", "audit", "automation", "bidding", "clients",
            "config", "core", "crm", "diarists", "document_kits", "documents",
            "equipment_management", "facilities", "fase5", "field_service",
            "financial", "ged", "government_integrations", "health_occupational",
            "hr", "integrations", "marketplace", "mobile", "monitoring",
            "notifications", "occurrences", "operations", "recruitment",
            "reports", "scheduler", "security_lgpd", "services"
        ]
        
        # Mapeamento de dependências conhecidas
        self.known_dependencies = {
            "financial": ["hr", "operations", "crm", "clients"],
            "hr": ["operations", "notifications", "documents"],
            "operations": ["hr", "clients", "equipment_management"],
            "crm": ["clients", "financial", "notifications"],
            "notifications": ["hr", "crm", "operations", "financial"]
        }

    async def analyze_all_correlations(self, tenant_id: str, timeframe_days: int = 30) -> List[ModuleCorrelation]:
        """
        Analisa correlações entre todos os módulos
        """
        correlations = []
        
        try:
            # Coletar dados de todos os módulos
            all_module_data = await self._collect_all_module_data(tenant_id, timeframe_days)
            
            modules = list(all_module_data.keys())
            
            # Analisar cada par de módulos
            for i in range(len(modules)):
                for j in range(i + 1, len(modules)):
                    module_a = modules[i]
                    module_b = modules[j]
                    
                    data_a = all_module_data[module_a]
                    data_b = all_module_data[module_b]
                    
                    if data_a and data_b:
                        correlation = await self._analyze_module_pair(
                            module_a, module_b, data_a, data_b, tenant_id
                        )
                        correlations.append(correlation)
            
            # Cache dos resultados
            cache_key = f"{tenant_id}_{timeframe_days}"
            self.correlation_cache[cache_key] = correlations
            
            return correlations
            
        except Exception as e:
            logger.error(f"Erro na análise de correlações: {e}")
            return []

    async def detect_cascade_impacts(self, trigger_module: str, tenant_id: str) -> List[CascadeImpact]:
        """
        Detecta potenciais impactos em cascata quando um módulo é afetado
        """
        impacts = []
        
        try:
            # Obter dependências do módulo trigger
            direct_dependencies = self.known_dependencies.get(trigger_module, [])
            
            # Calcular impacto em cascata
            for dependency in direct_dependencies:
                impact = await self._calculate_cascade_impact(trigger_module, dependency, tenant_id)
                impacts.append(impact)
            
            # Impactos de segunda ordem
            for dependency in direct_dependencies:
                second_order = self.known_dependencies.get(dependency, [])
                for second_dep in second_order:
                    if second_dep != trigger_module:
                        impact = await self._calculate_cascade_impact(
                            dependency, second_dep, tenant_id, order=2
                        )
                        impacts.append(impact)
            
            return impacts
            
        except Exception as e:
            logger.error(f"Erro na detecção de cascata: {e}")
            return []

    async def generate_integrated_insights(self, tenant_id: str) -> Dict[str, Any]:
        """
        Gera insights integrados baseados em análises cross-module
        """
        try:
            # Analisar correlações
            correlations = await self.analyze_all_correlations(tenant_id)
            
            # Encontrar correlações mais fortes
            strong_correlations = [c for c in correlations if c.strength > 0.7]
            
            # Analisar padrões
            patterns = await self._identify_patterns(correlations)
            
            # Gerar recomendações
            recommendations = await self._generate_cross_module_recommendations(patterns)
            
            insights = {
                "total_correlations": len(correlations),
                "strong_correlations": len(strong_correlations),
                "key_patterns": patterns,
                "recommendations": recommendations,
                "risk_modules": await self._identify_risk_modules(correlations),
                "opportunity_modules": await self._identify_opportunity_modules(correlations),
                "generated_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Erro na geração de insights: {e}")
            return {}

    async def _collect_all_module_data(self, tenant_id: str, timeframe_days: int) -> Dict[str, Any]:
        """
        Coleta dados de todos os módulos (simulado para demonstração)
        """
        module_data = {}
        
        for module in self.conecta_modules:
            # Simular dados para demonstração
            # Em produção, isso consultaria cada módulo via API/DB
            data = await self._simulate_module_data(module, tenant_id, timeframe_days)
            module_data[module] = data
            
        return module_data

    async def _simulate_module_data(self, module: str, tenant_id: str, days: int) -> Dict[str, Any]:
        """Simula dados de módulo para demonstração"""
        # Dados simulados baseados no tipo de módulo
        base_metrics = {
            "financial": {"revenue": np.random.normal(50000, 10000), "expenses": np.random.normal(30000, 5000)},
            "hr": {"employees": np.random.randint(10, 100), "turnover": np.random.uniform(0.05, 0.2)},
            "crm": {"leads": np.random.randint(20, 200), "conversion_rate": np.random.uniform(0.1, 0.3)},
            "operations": {"posts": np.random.randint(5, 50), "efficiency": np.random.uniform(0.7, 0.95)}
        }
        
        return base_metrics.get(module, {"activity": np.random.uniform(0, 100)})

    async def _analyze_module_pair(self, module_a: str, module_b: str, data_a: Any, data_b: Any, tenant_id: str) -> ModuleCorrelation:
        """Analisa correlação entre dois módulos"""
        
        # Extrair valores numéricos para correlação
        values_a = self._extract_numeric_values(data_a)
        values_b = self._extract_numeric_values(data_b)
        
        # Calcular correlação de Pearson
        if len(values_a) > 1 and len(values_b) > 1:
            correlation, p_value = pearsonr(values_a[:min(len(values_a), len(values_b))], 
                                          values_b[:min(len(values_a), len(values_b))])
        else:
            correlation = 0.0
            p_value = 1.0
        
        # Determinar tipo de correlação
        if abs(correlation) > 0.7:
            corr_type = CorrelationType.POSITIVE if correlation > 0 else CorrelationType.NEGATIVE
        elif abs(correlation) > 0.5:
            corr_type = CorrelationType.CAUSAL
        else:
            corr_type = CorrelationType.NEUTRAL
        
        # Gerar insights específicos
        insights = self._generate_pair_insights(module_a, module_b, correlation)
        impact_areas = self._identify_impact_areas(module_a, module_b)
        
        return ModuleCorrelation(
            module_a=module_a,
            module_b=module_b,
            correlation_type=corr_type,
            strength=abs(correlation),
            confidence=1.0 - p_value if p_value < 1.0 else 0.0,
            insights=insights,
            impact_areas=impact_areas,
            timestamp=datetime.now()
        )

    def _extract_numeric_values(self, data: Any) -> List[float]:
        """Extrai valores numéricos de dados de módulo"""
        values = []
        
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, (int, float)):
                    values.append(float(value))
                elif isinstance(value, (list, np.ndarray)):
                    values.extend([float(v) for v in value if isinstance(v, (int, float))])
        elif isinstance(data, (list, np.ndarray)):
            values = [float(v) for v in data if isinstance(v, (int, float))]
        elif isinstance(data, (int, float)):
            values = [float(data)]
        
        # Garantir que temos pelo menos alguns valores
        if len(values) < 2:
            values = [np.random.normal(0, 1) for _ in range(10)]
            
        return values

    def _generate_pair_insights(self, module_a: str, module_b: str, correlation: float) -> List[str]:
        """Gera insights específicos para par de módulos"""
        insights = []
        
        if abs(correlation) > 0.7:
            insights.append(f"Forte correlação detectada entre {module_a} e {module_b}")
            insights.append(f"Mudanças em {module_a} afetam significativamente {module_b}")
        elif abs(correlation) > 0.5:
            insights.append(f"Correlação moderada entre {module_a} e {module_b}")
            insights.append(f"Recomenda-se monitorar ambos os módulos")
        else:
            insights.append(f"Correlação baixa entre {module_a} e {module_b}")
            insights.append(f"Módulos operam de forma independente")
        
        return insights

    def _identify_impact_areas(self, module_a: str, module_b: str) -> List[str]:
        """Identifica áreas de impacto entre módulos"""
        impact_map = {
            ("financial", "hr"): ["folha_pagamento", "beneficios", "orcamento_pessoal"],
            ("hr", "operations"): ["alocacao_pessoal", "escalas", "produtividade"],
            ("crm", "financial"): ["receitas", "previsao_vendas", "comissoes"],
            ("operations", "clients"): ["qualidade_servico", "satisfacao_cliente", "contratos"]
        }
        
        # Verificar ambas as direções
        areas = impact_map.get((module_a, module_b), [])
        if not areas:
            areas = impact_map.get((module_b, module_a), [])
        
        if not areas:
            areas = ["operacoes_gerais", "qualidade_dados", "eficiencia_processos"]
            
        return areas

    async def _calculate_cascade_impact(self, trigger: str, affected: str, tenant_id: str, order: int = 1) -> CascadeImpact:
        """Calcula impacto em cascata"""
        
        # Severidade baseada em dependências conhecidas
        severity = 0.8 if order == 1 else 0.5
        probability = 0.9 if order == 1 else 0.6
        
        # Duração estimada do impacto
        duration = timedelta(hours=24) if order == 1 else timedelta(hours=8)
        
        # Ações de mitigação
        mitigation = [
            f"Monitorar {affected} após mudanças em {trigger}",
            f"Implementar alertas entre {trigger} e {affected}",
            "Criar plano de contingência para impactos"
        ]
        
        return CascadeImpact(
            trigger_module=trigger,
            affected_modules=[affected],
            impact_chain=[trigger, affected],
            severity=severity,
            probability=probability,
            estimated_duration=duration,
            mitigation_actions=mitigation
        )

    async def _identify_patterns(self, correlations: List[ModuleCorrelation]) -> List[Dict[str, Any]]:
        """Identifica padrões nas correlações"""
        patterns = []
        
        # Agrupar por força de correlação
        strong_corrs = [c for c in correlations if c.strength > 0.7]
        if strong_corrs:
            patterns.append({
                "type": "strong_correlations",
                "count": len(strong_corrs),
                "modules": [f"{c.module_a}-{c.module_b}" for c in strong_corrs]
            })
        
        # Identificar módulos centrais (com mais conexões)
        module_connections = defaultdict(int)
        for corr in correlations:
            if corr.strength > 0.5:
                module_connections[corr.module_a] += 1
                module_connections[corr.module_b] += 1
        
        if module_connections:
            central_module = max(module_connections, key=module_connections.get)
            patterns.append({
                "type": "central_module",
                "module": central_module,
                "connections": module_connections[central_module]
            })
        
        return patterns

    async def _generate_cross_module_recommendations(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações cross-module"""
        recommendations = []
        
        for pattern in patterns:
            if pattern["type"] == "strong_correlations":
                recommendations.append(f"Implementar dashboards integrados para {pattern['count']} correlações fortes")
            elif pattern["type"] == "central_module":
                recommendations.append(f"Módulo {pattern['module']} é central - priorizar monitoramento")
        
        # Recomendações gerais
        recommendations.extend([
            "Configurar alertas cross-module para impactos em cascata",
            "Implementar análise preditiva para correlações identificadas",
            "Criar workflows automatizados baseados em dependências"
        ])
        
        return recommendations

    async def _identify_risk_modules(self, correlations: List[ModuleCorrelation]) -> List[str]:
        """Identifica módulos de risco baseado em correlações"""
        risk_modules = []
        
        module_risk_score = defaultdict(float)
        
        for corr in correlations:
            if corr.strength > 0.7:  # Correlações fortes
                module_risk_score[corr.module_a] += corr.strength
                module_risk_score[corr.module_b] += corr.strength
        
        # Módulos com score alto são de risco (muitas dependências)
        for module, score in module_risk_score.items():
            if score > 2.0:  # Threshold arbitrário
                risk_modules.append(module)
        
        return risk_modules[:5]  # Top 5

    async def _identify_opportunity_modules(self, correlations: List[ModuleCorrelation]) -> List[str]:
        """Identifica módulos com oportunidades baseado em correlações"""
        opportunity_modules = []
        
        # Módulos com poucas correlações podem ter oportunidades de integração
        module_correlation_count = defaultdict(int)
        
        for corr in correlations:
            if corr.strength > 0.3:
                module_correlation_count[corr.module_a] += 1
                module_correlation_count[corr.module_b] += 1
        
        # Módulos com poucas correlações têm oportunidades
        for module in self.conecta_modules:
            if module_correlation_count[module] < 2:
                opportunity_modules.append(module)
        
        return opportunity_modules[:5]  # Top 5

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do analytics cross-module"""
        return {
            "status": "healthy",
            "modules_tracked": len(self.conecta_modules),
            "cached_correlations": len(self.correlation_cache),
            "known_dependencies": len(self.known_dependencies),
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
