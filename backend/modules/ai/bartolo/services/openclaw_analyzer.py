"""
Analyzer para OpenClaw - Usa LLM para analisar falhas e sugerir correções.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import json
import logging

from modules.ai.conversation.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenClawAnalyzer:
    """Analisa falhas do OpenClaw usando LLM e sugere correções."""

    def __init__(self):
        self.llm = LLMProvider()

    async def analyze_failures(self, report: dict) -> str:
        """
        Analisa falhas e sugere correções usando IA.

        Args:
            report: Relatório OpenClaw completo

        Returns:
            Análise formatada em Markdown
        """
        # Filtra checks com problemas
        problems = [c for c in report["checks"] if c["status"] in ["fail", "error", "warn"]]

        if not problems:
            return self._format_no_problems_response(report)

        # Monta prompt para LLM
        prompt = self._build_analysis_prompt(report, problems)

        try:
            # Envia para LLM com timeout
            llm_response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=None,
                max_tokens=1500,
                temperature=0.3,  # Mais determinístico para análise técnica
            )

            return self._format_analysis_response(report, problems, llm_response.content)

        except Exception as e:
            logger.error(f"Erro na análise IA: {e}")
            return self._format_fallback_response(report, problems)

    def _build_analysis_prompt(self, report: dict, problems: list[dict]) -> str:
        """Constrói prompt para análise do LLM."""

        problems_text = "\n\n".join(
            [
                f"**{i + 1}. {p['name']}** (Status: {p['status'].upper()})\n"
                f"   • Duração: {p['duration_seconds']:.1f}s\n"
                f"   • Mensagem: {p['message']}\n"
                f"   • Details: {json.dumps(p.get('details', {}), indent=2)}"
                for i, p in enumerate(problems)
            ]
        )

        prompt = f"""Você é um especialista DevOps sênior do sistema Conecta PRO.

**CONTEXTO DO SISTEMA:**
- Stack: Python 3.12 FastAPI + Next.js 16 React + PostgreSQL 16 + Redis 7
- Ambiente: VPS Ubuntu 24.04 via Docker Compose
- Projeto: ERP para gestão de segurança patrimonial

**RELATÓRIO OPENCLAW:**
- Ciclo: {report["cycle_id"]}
- Status Geral: {report["overall_status"].upper()}
- Duração: {report["duration_seconds"]:.1f}s
- Health Score: {report.get("health_score", "N/A")}/100

**PROBLEMAS DETECTADOS ({len(problems)}):**
{problems_text}

---

**SUA TAREFA:**
Para CADA problema acima, forneça análise em formato Markdown:

### [Número]. [Nome do Check]

**🔍 Causa Raiz:**
[Explicação técnica do que causou o problema]

**✅ Solução Imediata:**
```bash
# Comandos específicos para resolver AGORA
```

**🛡️ Prevenção:**
[Como evitar que aconteça novamente]

**📊 Prioridade:** 🔴 CRÍTICO | 🟡 MÉDIO | 🟢 BAIXO

---

**IMPORTANTE:**
- Seja específico e prático
- Use comandos reais (docker, pytest, ruff, etc)
- Forneça paths exatos de arquivos quando relevante
- Priorize soluções rápidas
- Se o problema for timeout, sugira otimizações
"""

        return prompt

    def _format_no_problems_response(self, report: dict) -> str:
        """Formata resposta quando não há problemas."""

        return f"""**✅ Sistema Operando Perfeitamente!**

**Ciclo:** {report["cycle_id"]}
**Duração:** {report["duration_seconds"]:.1f}s
**Health Score:** {report.get("health_score", 100)}/100

**Resumo:**
- ✅ Pass: {report["summary"]["status_counts"]["pass"]}
- ⏭️ Skip: {report["summary"]["status_counts"]["skip"]}

Todos os checks críticos passaram. Sistema está estável e seguro.

💡 **Recomendação:** Execute `/openclaw ciclo` regularmente para manter qualidade.
"""

    def _format_analysis_response(self, report: dict, problems: list[dict], llm_response: str) -> str:
        """Formata resposta com análise do LLM."""

        header = f"""**🤖 Análise IA do OpenClaw**

**Ciclo:** {report["cycle_id"]}
**Status:** {report["overall_status"].upper()}
**Problemas:** {len(problems)}
**Duração:** {report["duration_seconds"]:.1f}s

---

"""

        footer = f"""

---

💡 **Próximos Passos:**
1. Execute os comandos sugeridos na ordem apresentada
2. Use `/openclaw status` para verificar se problemas foram resolvidos
3. Se persistir, rode `/openclaw ciclo` para revalidar tudo

📊 **Health Score Atual:** {report.get("health_score", 0)}/100
"""

        return header + llm_response + footer

    def _format_fallback_response(self, report: dict, problems: list[dict]) -> str:
        """Formata resposta fallback quando LLM falha."""

        problems_text = "\n".join([f"- **{p['check']}** ({p['status'].upper()}): {p['message']}" for p in problems[:5]])

        return f"""**⚠️ Análise Básica (LLM indisponível)**

**Ciclo:** {report["cycle_id"]}
**Status:** {report["overall_status"].upper()}
**Problemas Detectados:** {len(problems)}

{problems_text}

---

**💡 Recomendações Gerais:**

**Para erros de timeout:**
```bash
# Aumentar timeout no runner ou executar checks individualmente
python3 scripts/openclaw/runner.py --only tests
```

**Para falhas de lint:**
```bash
# Corrigir automaticamente
ruff check backend/ --fix
cd frontend && npm run lint:fix
```

**Para falhas de security:**
```bash
# Revisar relatório detalhado
cat reports/openclaw/bandit_report.json
```

**Para falhas de health:**
```bash
# Verificar containers
docker ps
docker logs conecta-pro-backend --tail 50
```

---

📊 Tente novamente `/openclaw analyze` em alguns minutos quando LLM estiver disponível.
"""

    async def analyze_specific_check(self, check_name: str, check_result: dict) -> str:
        """Analisa um check específico."""

        if check_result["status"] == "pass":
            return f"✅ **{check_name}** passou sem problemas."

        prompt = f"""Analise este problema específico do OpenClaw:

**Check:** {check_name}
**Status:** {check_result["status"].upper()}
**Duração:** {check_result["duration_seconds"]:.1f}s
**Mensagem:** {check_result["message"]}
**Details:** {json.dumps(check_result.get("details", {}), indent=2)}

Forneça:
1. Causa raiz provável
2. Comando para resolver (bash)
3. Como prevenir

Seja conciso (máx 200 palavras).
"""

        try:
            llm_response = await self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=None,
                max_tokens=500,
                temperature=0.3,
            )
            return f"**🔍 Análise: {check_name}**\n\n{llm_response.content}"
        except Exception as e:
            logger.error(f"Erro ao analisar check específico: {e}")
            return f"❌ Erro ao analisar {check_name}: {str(e)}"
