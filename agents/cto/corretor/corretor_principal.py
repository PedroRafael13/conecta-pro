"""
CorretorPrincipal — Orquestra o fluxo completo.

Fluxo:
1. Recebe bug (do CTO, Jordan ou agentes)
2. Analisa e propõe correção (Analisador)
3. Apresenta para Jordan com risco medido
4. Aguarda aprovação no Telegram
5. Aplica se aprovado (Aplicador)
6. Reverte se falhar
7. Registra na MemóriaLonga
"""
import json
import sys
from datetime import datetime
from pathlib import Path

CTO_DIR = Path("/opt/conecta-pro/agents/cto")
CORRETOR_DIR = CTO_DIR / "corretor"
AGUARDANDO_FILE = CORRETOR_DIR / "aguardando_aprovacao.json"

sys.path.insert(0, str(CORRETOR_DIR))
sys.path.insert(0, str(CTO_DIR))

from analisador import Analisador, telegram
from aplicador import Aplicador


class CorretorPrincipal:
    """Orquestra o fluxo completo de correção."""

    def __init__(self):
        self.analisador = Analisador()
        self.aplicador = Aplicador()
        self.aguardando = self._carregar_aguardando()

    def _carregar_aguardando(self) -> dict:
        if AGUARDANDO_FILE.exists():
            try:
                return json.loads(AGUARDANDO_FILE.read_text())
            except Exception:
                pass
        return {}

    def _salvar_aguardando(self):
        AGUARDANDO_FILE.write_text(
            json.dumps(
                self.aguardando, indent=2,
                ensure_ascii=False, default=str,
            )
        )

    def propor_correcao(
        self,
        descricao: str,
        arquivo: str = None,
        codigo_errado: str = None,
        codigo_correto: str = None,
        origem: str = "CTO",
    ) -> dict:
        """
        Analisa bug e propõe correção para Jordan.
        Retorna análise com ID para aprovação.
        """
        print(f"[Corretor] Propondo correção: {descricao[:50]}")

        analise = self.analisador.analisar_bug(
            descricao=descricao,
            arquivo=arquivo,
            codigo_errado=codigo_errado,
            codigo_correto=codigo_correto,
        )

        if analise.get("erro"):
            telegram(
                f"⚠️ *Corretor — Análise falhou*\n\n"
                f"_{analise['erro']}_\n\n"
                f"Forneça mais detalhes para tentar novamente."
            )
            return analise

        # Registrar como aguardando aprovação
        self.aguardando[analise["id"]] = {
            "analise_id": analise["id"],
            "descricao": descricao,
            "arquivo": analise.get("arquivo"),
            "risco": analise.get("risco", {}),
            "origem": origem,
            "timestamp": datetime.now().isoformat(),
        }
        self._salvar_aguardando()

        # Enviar proposta para Jordan
        proposta = self.analisador.formatar_proposta_telegram(analise)
        telegram(proposta)

        print(f"  Proposta enviada: {analise['id']} — aguardando Jordan")
        return analise

    def processar_aprovacao(self, analise_id: str, aprovado: bool) -> dict:
        """
        Processa resposta de Jordan.
        Chamado pelo MonitorBot quando Jordan responde.
        """
        if analise_id not in self.aguardando:
            return {"ok": False, "msg": f"{analise_id} não encontrado"}

        if not aprovado:
            del self.aguardando[analise_id]
            self._salvar_aguardando()
            telegram(
                f"↩️ *Correção {analise_id} cancelada*\n"
                f"Nenhuma alteração foi feita."
            )
            return {"ok": True, "msg": "Cancelado"}

        # Aplicar correção
        print(f"[Corretor] Aplicando {analise_id}...")
        resultado = self.aplicador.aplicar(analise_id)

        # Remover da fila de aguardando
        entrada = self.aguardando.pop(analise_id, {})
        self._salvar_aguardando()

        # Registrar na MemóriaLonga se resolvido
        if resultado.get("sucesso"):
            try:
                from memoria_longa import MemóriaLonga
                mem = MemóriaLonga()
                mem.registrar_solucao(
                    problema=entrada.get("descricao", analise_id),
                    solucao=(
                        f"Correção automática em "
                        f"{resultado.get('arquivo', '?')}"
                    ),
                    funcionou=True,
                    ticket=analise_id,
                )
            except Exception:
                pass

        return resultado

    def listar_aguardando(self) -> list:
        """Lista correções aguardando aprovação."""
        return list(self.aguardando.values())

    def resumo(self) -> dict:
        """Resumo do corretor."""
        hist_dir = CORRETOR_DIR / "historico"
        resultados = list(hist_dir.glob("*_resultado.json"))
        total = len(resultados)
        sucesso = 0
        for f in resultados:
            try:
                if json.loads(f.read_text()).get("sucesso", False):
                    sucesso += 1
            except Exception:
                pass
        return {
            "total_correcoes": total,
            "sucesso": sucesso,
            "falhas": total - sucesso,
            "taxa_sucesso": round(sucesso / total * 100, 1) if total else 0,
            "aguardando_aprovacao": len(self.aguardando),
        }
