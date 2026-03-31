"""
BaseAgent — Classe base para todos os agentes do Conecta PRO.

Cada agente especializado herda desta classe e implementa:
  - MODULO: nome do módulo
  - SUBMODULO: nome do submódulo
  - ENDPOINTS: lista de endpoints para testar
  - CONHECE_BUGS: bugs conhecidos das auditorias
  - auditar(): lógica específica de auditoria
  - corrigir(): lógica específica de correção

Ciclo permanente 24h:
  1. Testar endpoints do submódulo
  2. Identificar bugs novos vs conhecidos
  3. Aplicar correções automáticas seguras
  4. Reportar resultado ao orquestrador pai
"""
import json
import logging
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

BACKEND_URL = "http://127.0.0.1:8080"
REPORTS_DIR = Path("/opt/conecta-pro/reports/modules")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class BaseAgent:
    """Classe base para todos os agentes especializados."""

    # Sobrescrever nas subclasses
    MODULO: str = "base"
    SUBMODULO: str = "base"
    ENDPOINTS: list = []

    # Bugs conhecidos das auditorias (skills 01-10)
    # Formato: {"descricao": str, "corrigido": bool,
    #           "auto_corrigivel": bool}
    CONHECE_BUGS: list = []

    def __init__(self):
        self.token: Optional[str] = None
        self.container: Optional[str] = None
        self.resultados: list = []
        self.correcoes_aplicadas: list = []
        self.bugs_novos: list = []
        self.score: float = 0.0
        self.timestamp = datetime.now()

    # ─── AUTH ───────────────────────────────────────

    def obter_token(self) -> str:
        """Obter JWT token do backend."""
        try:
            r = subprocess.run([
                'curl', '-sf', '-X', 'POST',
                f'{BACKEND_URL}/api/v1/auth/login',
                '-H',
                'Content-Type: '
                'application/x-www-form-urlencoded',
                '-d',
                'username=jjesus@conectamais.pro'
                '&password=Jordan0612'
            ], capture_output=True, text=True,
               timeout=15)
            self.token = json.loads(
                r.stdout).get('access_token', '')
            return self.token
        except Exception as e:
            logger.error(f"Token error: {e}")
            return ''

    def obter_container(self) -> str:
        """Obter nome do container backend."""
        try:
            r = subprocess.run([
                'docker', 'ps',
                '--filter',
                'ancestor=conecta-pro-backend',
                '--format', '{{.Names}}'
            ], capture_output=True, text=True)
            self.container = \
                r.stdout.strip().split('\n')[0]
            return self.container
        except Exception as e:
            logger.error(f"Container error: {e}")
            return ''

    # ─── TESTE DE ENDPOINTS ─────────────────────────

    def testar_endpoint(
            self,
            path: str,
            method: str = 'GET',
            esperado: int = 200,
            payload: dict = None) -> dict:
        """Testar um endpoint e retornar resultado."""
        try:
            cmd = [
                'curl', '-sf',
                '-o', '/dev/null',
                '-w', '%{http_code}',
                '-X', method,
                f'{BACKEND_URL}{path}',
                '-H',
                f'Authorization: Bearer {self.token}',
                '--max-time', '10'
            ]
            if payload:
                cmd += [
                    '-H',
                    'Content-Type: application/json',
                    '-d', json.dumps(payload)
                ]

            r = subprocess.run(
                cmd, capture_output=True,
                text=True, timeout=15)
            status = int(r.stdout.strip() or '0')
            ok = status == esperado

            return {
                'path': path,
                'method': method,
                'status': status,
                'esperado': esperado,
                'ok': ok,
                'ts': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'path': path,
                'method': method,
                'status': 0,
                'esperado': esperado,
                'ok': False,
                'erro': str(e),
                'ts': datetime.now().isoformat()
            }

    def testar_sem_token(self, path: str) -> dict:
        """Testar endpoint sem token — deve retornar 401/403."""
        try:
            r = subprocess.run([
                'curl', '-sf',
                '-o', '/dev/null',
                '-w', '%{http_code}',
                '-X', 'GET',
                f'{BACKEND_URL}{path}',
                '--max-time', '10'
            ], capture_output=True, text=True,
               timeout=15)
            status = int(r.stdout.strip() or '0')
            protegido = status in [401, 403]
            return {
                'path': path,
                'status_sem_token': status,
                'protegido': protegido
            }
        except Exception as e:
            return {
                'path': path,
                'status_sem_token': 0,
                'protegido': False,
                'erro': str(e)
            }

    def db_query(self, sql: str) -> str:
        """Executar query no banco."""
        try:
            r = subprocess.run([
                'docker', 'exec',
                self.container,
                'psql', '-U', 'postgres',
                '-d', 'conecta_pro',
                '-t', '-c', sql
            ], capture_output=True, text=True,
               timeout=15)
            return r.stdout.strip()
        except Exception as e:
            logger.error(f"DB query error: {e}")
            return ''

    def hot_copy(self, local_path: str,
                 container_path: str) -> bool:
        """Copiar arquivo para o container."""
        try:
            r = subprocess.run([
                'docker', 'cp',
                local_path,
                f'{self.container}:{container_path}'
            ], capture_output=True, text=True,
               timeout=30)
            return r.returncode == 0
        except Exception as e:
            logger.error(f"Hot copy error: {e}")
            return False

    def restart_container(self) -> bool:
        """Reiniciar o container backend."""
        try:
            subprocess.run([
                'docker', 'restart',
                self.container
            ], capture_output=True, timeout=45)
            import time
            time.sleep(10)
            return True
        except Exception as e:
            logger.error(f"Restart error: {e}")
            return False

    # ─── AUDITORIA ──────────────────────────────────

    def auditar_todos_endpoints(self) -> list:
        """Testar todos os endpoints do submódulo."""
        self.resultados = []
        for ep in self.ENDPOINTS:
            if isinstance(ep, str):
                r = self.testar_endpoint(ep)
            elif isinstance(ep, dict):
                r = self.testar_endpoint(
                    ep['path'],
                    ep.get('method', 'GET'),
                    ep.get('esperado', 200),
                    ep.get('payload')
                )
            self.resultados.append(r)
        return self.resultados

    def calcular_score(self) -> float:
        """Calcular score do submódulo."""
        if not self.resultados:
            return 0.0
        total = len(self.resultados)
        ok = sum(1 for r in self.resultados if r['ok'])
        self.score = round((ok / total) * 10, 1) \
            if total > 0 else 0.0
        return self.score

    def identificar_bugs(self) -> list:
        """Identificar endpoints com falha."""
        self.bugs_novos = [
            r for r in self.resultados
            if not r['ok']
        ]
        return self.bugs_novos

    # ─── CORREÇÕES ──────────────────────────────────

    def aplicar_correcao_simples(
            self,
            arquivo: str,
            buscar: str,
            substituir: str,
            descricao: str) -> bool:
        """
        Aplicar correção simples por find/replace.
        Seguro para: imports, tipos, constantes.
        NUNCA usar em: alembic/versions/, .env,
        main_production.py, docker-compose*.yml
        """
        # Zonas proibidas
        zonas_proibidas = [
            'alembic/versions',
            'main_production.py',
            'docker-compose',
            '.env',
            'credentials/'
        ]
        for zona in zonas_proibidas:
            if zona in arquivo:
                logger.warning(
                    f"ZONA PROIBIDA: {arquivo}")
                return False

        caminho = f"/opt/conecta-pro/backend/{arquivo}"
        if not os.path.exists(caminho):
            logger.error(f"Arquivo não encontrado: "
                         f"{caminho}")
            return False

        try:
            content = open(caminho).read()
            if buscar not in content:
                return False

            novo = content.replace(buscar, substituir)
            open(caminho, 'w').write(novo)

            # Hot copy para o container
            container_path = f"/app/{arquivo}"
            if self.hot_copy(caminho, container_path):
                self.correcoes_aplicadas.append({
                    'descricao': descricao,
                    'arquivo': arquivo,
                    'status': 'aplicada',
                    'ts': datetime.now().isoformat()
                })
                logger.info(
                    f"Correção aplicada: {descricao}")
                return True
            return False
        except Exception as e:
            logger.error(
                f"Erro na correção {descricao}: {e}")
            return False

    # ─── RELATÓRIO ──────────────────────────────────

    def gerar_relatorio(self) -> dict:
        """Gerar relatório completo do ciclo."""
        total = len(self.resultados)
        ok = sum(1 for r in self.resultados if r['ok'])

        return {
            'modulo': self.MODULO,
            'submodulo': self.SUBMODULO,
            'timestamp': self.timestamp.isoformat(),
            'score': self.score,
            'endpoints': {
                'total': total,
                'ok': ok,
                'falha': total - ok
            },
            'bugs_novos': len(self.bugs_novos),
            'bugs_detalhes': self.bugs_novos[:5],
            'correcoes_aplicadas':
                self.correcoes_aplicadas,
            'resultados': self.resultados
        }

    def salvar_relatorio(self, relatorio: dict):
        """Salvar relatório em disco."""
        nome = (f"{self.MODULO}_{self.SUBMODULO}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M')}"
                f".json")
        path = REPORTS_DIR / nome
        path.write_text(
            json.dumps(relatorio, indent=2,
                       ensure_ascii=False,
                       default=str))

    # ─── CICLO PRINCIPAL ────────────────────────────

    def executar(self) -> dict:
        """
        Executar ciclo completo do agente.
        1. Obter credenciais
        2. Auditar endpoints
        3. Identificar bugs
        4. Aplicar correções automáticas
        5. Gerar relatório
        """
        # Setup
        self.obter_token()
        self.obter_container()

        if not self.token:
            return {
                'modulo': self.MODULO,
                'submodulo': self.SUBMODULO,
                'erro': 'token_falhou',
                'score': 0.0
            }

        # Auditoria
        self.auditar_todos_endpoints()
        self.calcular_score()
        self.identificar_bugs()

        # Correções específicas do submódulo
        self.corrigir()

        # Relatório
        relatorio = self.gerar_relatorio()
        self.salvar_relatorio(relatorio)
        return relatorio

    def corrigir(self):
        """
        Implementar nas subclasses com
        correções específicas do submódulo.
        """
        pass

    def auditar(self):
        """
        Implementar nas subclasses com
        auditorias específicas do submódulo.
        """
        pass
