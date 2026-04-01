"""
BaseOrchestrator — Classe base para orquestradores
de módulo.

Cada orquestrador de módulo:
  1. Instancia e executa todos os agentes
     do seu módulo em sequência
  2. Consolida o score do módulo
  3. Determina se há bugs críticos
  4. Retorna resultado consolidado ao
     Orquestrador Geral
"""
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/opt/conecta-pro/agents/core')

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(
    "/opt/conecta-pro/reports/modules")


class BaseOrchestrator:
    """Classe base para orquestradores de módulo."""

    MODULO: str = "base"
    DESCRICAO: str = ""

    # Lista de classes de agentes do módulo
    # Preencher nas subclasses:
    # AGENTES = [AgenteColaboradores,
    #            AgenteAdmissao, ...]
    AGENTES: list = []

    def __init__(self):
        self.resultados_agentes = []
        self.score_modulo = 0.0
        self.correcoes_totais = []
        self.bugs_totais = []
        self.timestamp = datetime.now()

    def _obter_token_compartilhado(self) -> str:
        """Obtém token JWT único — compartilhado com todos os agentes do módulo."""
        try:
            r = subprocess.run([
                'curl', '-sf', '-X', 'POST',
                'http://127.0.0.1:8080/api/v1/auth/login',
                '-H',
                'Content-Type: application/x-www-form-urlencoded',
                '-d',
                'username=jjesus@conectamais.pro&password=Jordan0612'
            ], capture_output=True, text=True, timeout=15)
            token = json.loads(r.stdout).get('access_token', '')
            if token:
                logger.info(f"[{self.MODULO}] Token compartilhado obtido")
            return token
        except Exception as e:
            logger.error(f"[{self.MODULO}] Erro ao obter token: {e}")
            return ''

    def executar(self) -> dict:
        """
        Executar todos os agentes do módulo
        e consolidar resultado.
        """
        # Token único obtido UMA VEZ — injetado em todos os agentes
        token_compartilhado = self._obter_token_compartilhado()

        logger.info(
            f"[{self.MODULO}] Iniciando "
            f"{len(self.AGENTES)} agentes...")

        scores = []
        for AgenteClass in self.AGENTES:
            try:
                agente = AgenteClass(token=token_compartilhado)
                resultado = agente.executar()
                scores.append(
                    resultado.get('score', 0.0))
                self.resultados_agentes.append(
                    resultado)
                self.correcoes_totais.extend(
                    resultado.get(
                        'correcoes_aplicadas', []))
                self.bugs_totais.extend(
                    resultado.get(
                        'bugs_detalhes', []))

                sub = resultado.get('submodulo', '?')
                sc = resultado.get('score', 0.0)
                logger.info(
                    f"  [{self.MODULO}] "
                    f"{sub}: {sc}/10")
            except Exception as e:
                logger.error(
                    f"  [{self.MODULO}] "
                    f"Erro em agente: {e}")

        self.score_modulo = round(
            sum(scores) / len(scores), 1) \
            if scores else 0.0

        relatorio = {
            'modulo': self.MODULO,
            'descricao': self.DESCRICAO,
            'timestamp': self.timestamp.isoformat(),
            'score': self.score_modulo,
            'agentes_executados': len(self.AGENTES),
            'submodulos': self.resultados_agentes,
            'correcoes_aplicadas':
                self.correcoes_totais,
            'bugs_totais': len(self.bugs_totais),
            'bugs_criticos': [
                b for b in self.bugs_totais
                if b.get('status', 200) in
                [500, 0, 404]
            ]
        }

        # Salvar relatório do módulo
        nome = (f"{self.MODULO}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M')}"
                f".json")
        REPORTS_DIR.mkdir(
            parents=True, exist_ok=True)
        (REPORTS_DIR / nome).write_text(
            json.dumps(relatorio, indent=2,
                       ensure_ascii=False,
                       default=str))

        logger.info(
            f"[{self.MODULO}] Score: "
            f"{self.score_modulo}/10 | "
            f"Correções: {len(self.correcoes_totais)}")

        return relatorio
