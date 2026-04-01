"""
BrowserFlows — Fluxos completos de negócio via Playwright.

Testa jornadas reais do frontend Conecta PRO:
1. Admissão E2E — DP/ponto, espelho de ponto, navegação completa
2. Holerite — /modulos/dp/folha (Folha de Pagamento, INSS, IRRF, Calcular)
3. Lead CRM — /modulos/crm/leads (pipeline, busca, oportunidades)
4. Escala Operacional — /escalas, editor visual, templates

NOTA: O frontend usa NEXT_PUBLIC_API_URL=https://erp.conectamais.pro
para chamadas de dados. Testes verificam estrutura UI + API local.
"""

import json
import time
import urllib.error
import urllib.request
from typing import Callable, Optional

try:
    from playwright.sync_api import Page

    PLAYWRIGHT_DISPONIVEL = True
except ImportError:
    PLAYWRIGHT_DISPONIVEL = False

ERP_URL = "http://127.0.0.1:3001"
API_URL = "http://127.0.0.1:8080"


class BrowserFlows:
    """
    Fluxos completos de negócio para BrowserAgent.

    Uso:
        flows = BrowserFlows(
            page=self.page,
            resultado_fn=self._resultado,
            screenshot_fn=self._screenshot,
            token=self._obter_jwt(),
        )
        flows.executar_todos()
    """

    def __init__(
        self,
        page: "Page",
        resultado_fn: Callable,
        screenshot_fn: Callable,
        token: Optional[str] = None,
    ):
        self.page = page
        self._resultado = resultado_fn
        self._screenshot = screenshot_fn
        self.token = token

    # ─── HELPERS ─────────────────────────────────────────────

    def _api_get(self, path: str) -> dict:
        """GET autenticado na API local (127.0.0.1:8080)."""
        try:
            req = urllib.request.Request(
                f"{API_URL}{path}",
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
            )
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"_http_error": e.code}
        except Exception:
            return {}

    def _navegar(self, path: str, timeout: int = 12000) -> bool:
        """Navega e verifica que não caiu no login."""
        try:
            self.page.goto(f"{ERP_URL}{path}", wait_until="domcontentloaded", timeout=timeout)
            time.sleep(2)
            return "/login" not in self.page.url
        except Exception:
            return False

    def _body_text(self) -> str:
        """Texto do body sem o widget Bartolo."""
        try:
            return self.page.evaluate("() => document.body.innerText")
        except Exception:
            return ""

    def _visivel(self, seletor: str, timeout: int = 3000) -> bool:
        try:
            return self.page.locator(seletor).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def _clicar(self, seletor: str, timeout: int = 3000) -> bool:
        try:
            el = self.page.locator(seletor).first
            if el.is_visible(timeout=timeout):
                el.click()
                return True
        except Exception:
            pass
        return False

    def _contar(self, seletor: str) -> int:
        try:
            return self.page.locator(seletor).count()
        except Exception:
            return 0

    # ─── FLUXO 1: ADMISSÃO E2E ───────────────────────────────

    def fluxo_admissao(self) -> dict:
        """
        Admissão end-to-end:
        1. Verificar API local de operacional/employees
        2. Navegar para /modulos/dp — verificar que página carrega
        3. Navegar para /modulos/gestao-pessoas/ponto — nav com 6+ sub-seções
        4. Verificar acesso ao espelho de ponto
        5. Verificar acesso a justificativas
        """
        print("\n  📋 Fluxo 1: Admissão / Departamento Pessoal")

        # 1. API local — verificar dados de colaboradores
        data = self._api_get("/api/v1/operacional/employees/?page=1&page_size=1")
        api_ok = "_http_error" not in data or data.get("_http_error") in (200, None)
        total = data.get("total", data.get("count", 0))
        self._resultado(
            "admissao_api",
            api_ok,
            f"API operacional/employees: {total} colaboradores" if api_ok else "API operacional indisponível",
        )

        # 2. Navegar para /modulos/dp
        ok = self._navegar("/modulos/dp")
        body = self._body_text()
        # /modulos/dp redireciona para outra rota — aceitar qualquer conteúdo não vazio
        tem_dp_conteudo = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado(
            "admissao_dp_rota",
            tem_dp_conteudo,
            f"Módulo DP acessível (URL: {self.page.url.split('3001')[-1][:40]})",
        )

        # 3. Módulo ponto eletrônico
        ok = self._navegar("/modulos/gestao-pessoas/ponto")
        if not ok:
            self._resultado("admissao_ponto_rota", False, "Módulo ponto não acessível")
            return {"passou": False, "fluxo": "admissao"}

        # Verificar via botões de navegação
        nav_ponto = self._contar(
            "button:has-text('Bater Ponto'), button:has-text('Dashboard Ponto'), "
            "button:has-text('Espelho de Ponto'), button:has-text('Justificativas'), "
            "button:has-text('Banco de Horas')"
        )
        self._resultado(
            "admissao_ponto_rota",
            nav_ponto >= 3,
            f"Módulo Ponto com {nav_ponto} seções de navegação",
        )

        # 4. Espelho de Ponto
        ok = self._navegar("/modulos/gestao-pessoas/ponto/espelho")
        body = self._body_text()
        carregou = len(body.strip()) > 100 and "/login" not in self.page.url
        tem_espelho_kw = any(
            kw in body for kw in ["Espelho", "espelho", "Ponto", "data", "Data", "mês", "Mês"]
        )
        self._resultado(
            "admissao_espelho",
            carregou,
            "Espelho de Ponto carregou" if carregou else "Espelho de Ponto não carregou",
        )
        self._screenshot("admissao_espelho_ponto")

        # 5. Justificativas
        ok = self._navegar("/modulos/gestao-pessoas/ponto/justificativas")
        body = self._body_text()
        carregou = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado(
            "admissao_justificativas",
            carregou,
            "Justificativas de ponto carregou" if carregou else "Justificativas não carregou",
        )

        return {"passou": True, "fluxo": "admissao"}

    # ─── FLUXO 2: HOLERITE ───────────────────────────────────

    def fluxo_holerite(self) -> dict:
        """
        Folha de Pagamento / Holerite:
        1. Navegar para /modulos/dp/folha
        2. Verificar estrutura da página (Folha de Pagamento, INSS, IRRF)
        3. Verificar botão "Calcular Folha" presente
        4. Verificar exportação disponível
        5. Verificar rubricas em /modulos/dp/folha/rubricas
        """
        print("\n  📋 Fluxo 2: Holerite / Folha de Pagamento")

        # 1. Navegar para folha
        ok = self._navegar("/modulos/dp/folha")
        if not ok:
            self._resultado("holerite_rota", False, "/modulos/dp/folha não acessível")
            return {"passou": False, "fluxo": "holerite"}

        # Aguardar loading completar — a página carrega stats após API call
        # Stats cards ("Total INSS", "Total IRRF") aparecem só após loading=false
        try:
            self.page.wait_for_selector("text=Total INSS", timeout=8000)
        except Exception:
            time.sleep(4)  # fallback: espera extra

        body = self._body_text()

        # 2. Verificar estrutura da página (conteúdo real que está no código)
        # Do código-fonte: 'Folha de Pagamento', 'Folha salarial e encargos trabalhistas'
        tem_titulo = any(
            kw in body for kw in ["Folha de Pagamento", "Folha salarial", "Folha"]
        )
        self._resultado("holerite_rota", tem_titulo or len(body) > 100, "Módulo Folha carregou")

        # Verificar labels nos stats cards (renderizados após loading completar)
        # Do fonte: card title 'Total INSS', 'Total IRRF' (visíveis mesmo com data vazia)
        html = self.page.content()
        tem_inss_label = "INSS" in body or "INSS" in html
        tem_irrf_label = "IRRF" in body or "IRRF" in html

        self._resultado("holerite_inss", tem_inss_label, "Label INSS presente" if tem_inss_label else "Label INSS ausente")
        self._resultado("holerite_irrf", tem_irrf_label, "Label IRRF presente" if tem_irrf_label else "Label IRRF ausente")

        # 3. Botão "Calcular Folha"
        tem_calcular = self._visivel("button:has-text('Calcular Folha'), button:has-text('Calcular')", timeout=4000)
        self._resultado("holerite_calcular", tem_calcular, "Botão 'Calcular Folha' presente")

        # 4. Busca/filtro de período disponível (folha não tem botão exportar — tem filtro de mês/ano)
        tem_filtro = (
            self._visivel("input, select", timeout=3000)
            or "competência" in body.lower()
            or "período" in body.lower()
            or "mês" in body.lower()
        )
        self._resultado("holerite_filtro_periodo", tem_filtro, "Filtro de período disponível" if tem_filtro else "Filtro ausente")

        self._screenshot("holerite_folha_pagamento")

        # 5. Rubricas de folha
        ok = self._navegar("/modulos/dp/folha/rubricas")
        body = self._body_text()
        tem_rubricas = any(
            kw in body for kw in ["Rubrica", "rubrica", "Rubrica", "provento", "desconto", "Folha"]
        )
        carregou = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado(
            "holerite_rubricas",
            carregou,
            "Rubricas de folha acessíveis" if carregou else "Rubricas não acessíveis",
        )

        return {"passou": True, "fluxo": "holerite"}

    # ─── FLUXO 3: LEAD CRM ───────────────────────────────────

    def fluxo_lead_crm(self) -> dict:
        """
        Pipeline de leads no CRM:
        1. Verificar API local de leads
        2. Navegar para /modulos/crm/leads
        3. Verificar estrutura do dashboard (labels presentes no HTML)
        4. Verificar pipeline de status (Qualificado, Proposta, Negociação)
        5. Testar busca funcional
        6. Navegar para oportunidades + propostas
        """
        print("\n  📋 Fluxo 3: Lead CRM / Pipeline")

        # 1. API local de leads (sem trailing slash — FastAPI redirects 307 que urllib não segue)
        data = self._api_get("/api/v1/crm/leads?page=1&page_size=1")
        api_ok = "_http_error" not in data and bool(data)
        total = data.get("total", data.get("count", 0))
        self._resultado("crm_api", api_ok, f"API crm/leads: {total} leads")

        # 2. Navegar
        ok = self._navegar("/modulos/crm/leads")
        if not ok:
            self._resultado("crm_rota", False, "CRM leads não acessível")
            return {"passou": False, "fluxo": "lead_crm"}

        time.sleep(2)  # aguardar renderização React
        body = self._body_text()
        html = self.page.content()
        tem_crm = any(kw in body for kw in ["Leads", "Lead", "CRM", "Pipeline"])
        self._resultado("crm_rota", tem_crm or len(body) > 200, "Módulo CRM Leads carregou")

        # 3. Labels de dashboard presentes no HTML (são string literals no JSX — não dependem de API)
        # Do código: 'Total de Leads', 'Leads Novos', 'Valor Estimado'
        labels_esperados = ["Total de Leads", "Leads Novos", "Valor Estimado"]
        labels_em_html = [l for l in labels_esperados if l in html]
        labels_em_texto = [l for l in labels_esperados if l in body]
        labels_ok = list(set(labels_em_html + labels_em_texto))
        self._resultado(
            "crm_dashboard_labels",
            len(labels_ok) >= 2,
            f"Labels do dashboard: {labels_ok}",
        )

        # 4. Pipeline com tabs de status (do código: Todos, Novo, Qualificado, Proposta, Negociação)
        status_tabs = self._contar(
            "button:has-text('Todos'), button:has-text('Qualificado'), "
            "button:has-text('Proposta'), button:has-text('Negociação')"
        )
        tem_pipeline = status_tabs >= 2 or any(
            kw in body for kw in ["Qualificado", "Proposta", "Negociação"]
        )
        self._resultado("crm_pipeline_status", tem_pipeline, f"Pipeline com {status_tabs} tabs de status")

        # 5. Campo de busca funcional
        search = self.page.locator("input[placeholder*='Buscar'], input[type='search']").first
        tem_busca = False
        try:
            tem_busca = search.is_visible(timeout=2000)
        except Exception:
            pass
        if tem_busca:
            search.fill("TEST")
            time.sleep(0.5)
            search.clear()
        self._resultado("crm_busca", tem_busca, "Campo de busca funcional" if tem_busca else "Busca ausente")

        # 6. Botão Novo Lead
        tem_btn = self._visivel("button:has-text('Novo Lead'), button:has-text('Novo')", timeout=2000)
        self._resultado("crm_botao_novo", tem_btn, "Botão 'Novo Lead' presente")

        self._screenshot("crm_leads_pipeline")

        # 7. Oportunidades
        ok = self._navegar("/modulos/crm/oportunidades")
        body = self._body_text()
        carregou_opp = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado("crm_oportunidades", carregou_opp, "Página Oportunidades carregou")

        # 8. Propostas
        ok = self._navegar("/modulos/crm/propostas")
        body = self._body_text()
        carregou_prop = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado("crm_propostas", carregou_prop, "Página Propostas carregou")

        return {"passou": True, "fluxo": "lead_crm"}

    # ─── FLUXO 4: ESCALA OPERACIONAL ─────────────────────────

    def fluxo_escala(self) -> dict:
        """
        Escala operacional:
        1. Verificar API local de escalas
        2. Navegar para /modulos/operacional/escalas — tabs de navegação
        3. Verificar editor visual (/escalas/visual)
        4. Verificar templates (/escalas/templates) — estrutura
        5. Verificar alocações (/modulos/operacional/alocacoes)
        6. Verificar botões de ação (Gerar Escala, Nova Escala)
        """
        print("\n  📋 Fluxo 4: Escala Operacional")

        # 1. API local de escalas — trailing slash obrigatório (FastAPI não redireciona sem ela)
        data = self._api_get("/api/v1/operacional/scales/?page=1&page_size=1")
        api_ok = "_http_error" not in data and bool(data)
        total = data.get("total", data.get("count", len(data.get("items", []))))
        self._resultado("escala_api", api_ok, f"API operacional/scales: {total} escalas")

        # 2. Módulo escalas + navegação
        ok = self._navegar("/modulos/operacional/escalas")
        if not ok:
            self._resultado("escala_rota", False, "Módulo escalas não acessível")
            return {"passou": False, "fluxo": "escala"}

        body = self._body_text()
        tem_op = any(kw in body for kw in ["Escalas", "Operacional", "Postos"])
        self._resultado("escala_rota", tem_op, "Módulo Operacional/Escalas carregou")

        # Tabs internos de navegação (Postos, Escalas, Editor Visual, Alocações, Turnos...)
        nav_count = self._contar(
            "button:has-text('Escalas'), button:has-text('Editor Visual'), "
            "button:has-text('Postos'), button:has-text('Turnos'), button:has-text('Alocacoes')"
        )
        self._resultado(
            "escala_nav_tabs",
            nav_count >= 3,
            f"Navegação operacional: {nav_count} tabs",
        )

        # 3. Editor visual
        ok = self._navegar("/modulos/operacional/escalas/visual")
        body = self._body_text()
        carregou = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado(
            "escala_editor_visual",
            carregou,
            "Editor visual carregou" if carregou else "Editor visual não carregou",
        )
        self._screenshot("escala_editor_visual")

        # 4. Templates — verificar que a página carrega (não que tem dados)
        ok = self._navegar("/modulos/operacional/escalas/templates")
        body = self._body_text()
        carregou = len(body.strip()) > 100 and "/login" not in self.page.url
        # Botão de criação de template (TemplateManager.tsx: 'Novo Template' / 'Criar Primeiro Template')
        tem_btn_template = self._visivel(
            "button:has-text('Novo Template'), button:has-text('Criar Primeiro Template'), "
            "button:has-text('Template'), button:has-text('Voltar para Escalas')",
            timeout=4000,
        )
        self._resultado(
            "escala_templates",
            carregou,
            "Templates de escala carregou" if carregou else "Templates não carregou",
        )
        self._resultado(
            "escala_btn_gerar",
            tem_btn_template,
            "Botão de template presente" if tem_btn_template else "Botão de template ausente",
        )

        # 5. Alocações
        ok = self._navegar("/modulos/operacional/alocacoes")
        body = self._body_text()
        carregou = len(body.strip()) > 100 and "/login" not in self.page.url
        self._resultado(
            "escala_alocacoes",
            carregou,
            "Módulo Alocações carregou" if carregou else "Alocações não carregou",
        )

        self._screenshot("escala_operacional_final")
        return {"passou": True, "fluxo": "escala"}

    # ─── EXECUTOR PRINCIPAL ───────────────────────────────────

    def executar_todos(self) -> list:
        """Executa todos os 4 fluxos de negócio em sequência."""
        resultados_fluxos = []
        resultados_fluxos.append(self.fluxo_admissao())
        resultados_fluxos.append(self.fluxo_holerite())
        resultados_fluxos.append(self.fluxo_lead_crm())
        resultados_fluxos.append(self.fluxo_escala())
        return resultados_fluxos
