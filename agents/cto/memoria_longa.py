"""
MemóriaLonga — Memória persistente de longo prazo do CTO.
Diferente da memória de curto prazo (patterns, snapshots),
a memória longa registra aprendizados definitivos sobre
o sistema — o que funciona, o que sempre quebra, como resolver.

Estrutura:
- Soluções validadas: "quando X acontece, Y resolve"
- Componentes frágeis: "Redis cai 5x/mês por volta das 2h"
- Histórico de deploys: "deploy de sexta sempre causa problema"
- Conhecimento acumulado: fatos permanentes sobre o sistema
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


MEMORIA_FILE = Path(
    "/opt/conecta-pro/agents/cto/memory/memoria_longa.json"
)


class MemóriaLonga:
    """Memória de longo prazo do CTO."""

    def __init__(self):
        MEMORIA_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.dados = self._carregar()

    def _carregar(self) -> dict:
        if MEMORIA_FILE.exists():
            try:
                return json.loads(MEMORIA_FILE.read_text())
            except Exception:
                pass
        return {
            "versao": "1.0",
            "criado_em": datetime.now().isoformat(),
            "solucoes_validadas": {},
            "componentes_frageis": {},
            "padroes_temporais": {},
            "fatos_sistema": [],
            "licoes_aprendidas": [],
            "historico_resolucoes": [],
        }

    def _salvar(self):
        MEMORIA_FILE.write_text(
            json.dumps(
                self.dados, indent=2,
                ensure_ascii=False, default=str
            )
        )

    def registrar_solucao(
        self,
        problema: str,
        solucao: str,
        funcionou: bool,
        tempo_resolucao_s: float = 0,
        ticket: str = None,
    ):
        """
        Registra solução validada.
        "Quando Redis cai → restart resolve em 5s"
        """
        chave = problema.lower()[:50]

        if chave not in self.dados["solucoes_validadas"]:
            self.dados["solucoes_validadas"][chave] = {
                "problema": problema,
                "tentativas": [],
                "melhor_solucao": None,
                "taxa_sucesso": 0,
            }

        entry = self.dados["solucoes_validadas"][chave]
        entry["tentativas"].append({
            "solucao": solucao,
            "funcionou": funcionou,
            "tempo_s": tempo_resolucao_s,
            "ticket": ticket,
            "timestamp": datetime.now().isoformat(),
        })

        # Atualizar melhor solução (mais rápida que funcionou)
        sucessos = [t for t in entry["tentativas"] if t["funcionou"]]
        if sucessos:
            melhor = min(sucessos, key=lambda t: t["tempo_s"])
            entry["melhor_solucao"] = melhor["solucao"]
            entry["taxa_sucesso"] = round(
                len(sucessos) / len(entry["tentativas"]) * 100
            )

        self._salvar()
        print(
            f"[MemóriaLonga] Solução registrada: "
            f"{problema[:40]} → {'✅' if funcionou else '❌'}"
        )

    def registrar_componente_fragil(
        self,
        componente: str,
        tipo_falha: str,
        horario_tipico: str = None,
        frequencia: str = None,
    ):
        """
        Registra componente que falha com frequência.
        "Redis falha às 2h quando swap > 80%"
        """
        if componente not in self.dados["componentes_frageis"]:
            self.dados["componentes_frageis"][componente] = {
                "falhas": [],
                "total": 0,
                "ultimo_incidente": None,
            }

        c = self.dados["componentes_frageis"][componente]
        c["falhas"].append({
            "tipo": tipo_falha,
            "horario": horario_tipico,
            "frequencia": frequencia,
            "registrado_em": datetime.now().isoformat(),
        })
        c["total"] += 1
        c["ultimo_incidente"] = datetime.now().isoformat()
        c["falhas"] = c["falhas"][-20:]  # Manter últimas 20

        self._salvar()

    def registrar_licao(
        self,
        licao: str,
        contexto: str = "",
        ticket: str = None,
    ):
        """
        Registra lição aprendida permanentemente.
        "kill -HUP 1 não recarrega uvicorn — usar docker restart"
        """
        self.dados["licoes_aprendidas"].append({
            "licao": licao,
            "contexto": contexto,
            "ticket": ticket,
            "registrado_em": datetime.now().isoformat(),
        })
        # Manter apenas 100 mais recentes
        self.dados["licoes_aprendidas"] = (
            self.dados["licoes_aprendidas"][-100:]
        )
        self._salvar()
        print(f"[MemóriaLonga] Lição: {licao[:60]}")

    def registrar_fato(self, fato: str, categoria: str = "geral"):
        """
        Registra fato permanente sobre o sistema.
        "Next.js standalone não recarrega com hot-copy"
        """
        self.dados["fatos_sistema"].append({
            "fato": fato,
            "categoria": categoria,
            "registrado_em": datetime.now().isoformat(),
        })
        self._salvar()

    def consultar_solucao(self, problema: str) -> Optional[str]:
        """Consulta melhor solução conhecida para um problema."""
        chave = problema.lower()[:50]

        # Busca exata
        if chave in self.dados["solucoes_validadas"]:
            return self.dados["solucoes_validadas"][chave].get(
                "melhor_solucao"
            )

        # Busca por similaridade (palavras-chave)
        palavras = set(chave.split())
        melhor_match = None
        melhor_score = 0

        for k, v in self.dados["solucoes_validadas"].items():
            palavras_k = set(k.split())
            score = len(palavras & palavras_k)
            if score > melhor_score and v.get("melhor_solucao"):
                melhor_score = score
                melhor_match = v["melhor_solucao"]

        return melhor_match if melhor_score >= 2 else None

    def componentes_mais_frageis(self, top: int = 5) -> list:
        """Retorna componentes que mais falham."""
        return sorted(
            [
                {
                    "componente": k,
                    "total_falhas": v["total"],
                    "ultimo": v["ultimo_incidente"],
                }
                for k, v in self.dados["componentes_frageis"].items()
            ],
            key=lambda x: x["total_falhas"],
            reverse=True,
        )[:top]

    def popular_com_historico(self):
        """
        Popula memória com lições desta sessão.
        Conhecimento acumulado que o CTO deve lembrar sempre.
        """
        licoes = [
            (
                "kill -HUP 1 não recarrega módulos Python "
                "em uvicorn — usar docker stop + start",
                "deploy",
            ),
            (
                "docker cp modules/ não sobrescreve arquivos "
                "existentes — copiar individualmente",
                "deploy",
            ),
            (
                "Next.js standalone compila rewrites() no "
                "server.js — mudanças exigem rebuild completo",
                "frontend",
            ),
            (
                "main_production.py é ZONA PROIBIDA — "
                "injetar via cadeia de imports",
                "arquitetura",
            ),
            (
                "SearchService não indexava employees — "
                "corrigido em 01/04/2026 via monitoring router",
                "busca",
            ),
            (
                "4 sistemas de monitoramento rodavam em "
                "paralelo causando contradições — "
                "unificado em orchestrator_unificado.py",
                "monitoramento",
            ),
            (
                "OpenClaw webhook exige endpoint público "
                "sem JWT — Alertmanager não envia token",
                "integracao",
            ),
            (
                "Swap 100% causa condição de corrida no "
                "token JWT — logout inesperado no frontend",
                "infraestrutura",
            ),
            (
                "INSS 2026: faixas 1412/2666/4000/7786 — "
                "não 1518/2793/4190/8157 (era tabela 2025)",
                "folha",
            ),
            (
                "celery-integrations usa imagem própria — "
                "hot copy no backend não atualiza o Celery",
                "deploy",
            ),
        ]

        fatos = [
            ("Redis falha por swap saturado", "infraestrutura"),
            ("PM2ExcessiveRestarts confiança 95% (6x histórico)", "monitoramento"),
            ("483 tabelas no banco da Conecta Mais", "banco"),
            ("13 clientes | 41 funcionários | 12 postos", "negocio_tecnico"),
            ("VPS KV4: 32GB RAM | 386GB disco | 4GB swap", "infraestrutura"),
            ("Frontend em Docker porta 3001", "infraestrutura"),
            ("Backend FastAPI porta 8080", "infraestrutura"),
        ]

        for licao, ctx in licoes:
            self.registrar_licao(licao, ctx)

        for fato, cat in fatos:
            self.registrar_fato(fato, cat)

        # Componentes frágeis conhecidos
        self.registrar_componente_fragil(
            "redis", "OOM/swap saturado", "02:00-04:00 UTC", "5x/mês"
        )
        self.registrar_componente_fragil(
            "celery-integrations",
            "TypeError em hot-copy",
            None,
            "em cada deploy",
        )

        print(
            f"✅ Memória populada: "
            f"{len(licoes)} lições + {len(fatos)} fatos"
        )

    def resumo(self) -> dict:
        return {
            "solucoes": len(self.dados["solucoes_validadas"]),
            "componentes_frageis": len(self.dados["componentes_frageis"]),
            "licoes": len(self.dados["licoes_aprendidas"]),
            "fatos": len(self.dados["fatos_sistema"]),
            "top_frageis": self.componentes_mais_frageis(3),
        }
