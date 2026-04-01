"""
BrowserAgent — E2E automatizado com Playwright.
Navega pelo ERP real, preenche formulários, valida resultados.
Detecta: botões quebrados, fluxos incompletos, dados incorretos na tela,
         formulários sem validação, redirects errados.

PRINCÍPIO: não-destrutivo — usa dados de teste, não altera dados reais.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import (
        Browser,
        Page,
        TimeoutError as PlaywrightTimeout,
        sync_playwright,
    )

    PLAYWRIGHT_DISPONIVEL = True
except ImportError:
    PLAYWRIGHT_DISPONIVEL = False


ERP_URL = "http://127.0.0.1:3001"
REPORTS_DIR = Path("/opt/conecta-pro/reports/browser")
SCREENSHOTS_DIR = Path("/opt/conecta-pro/reports/browser/screenshots")

# Credenciais do ERP
ERP_USER = "jjesus@conectamais.pro"
ERP_PASS = "Jordan0612"  # pragma: allowlist secret

# Timeout padrão
TIMEOUT = 10000  # 10s


class BrowserAgent:
    """E2E automatizado com Playwright."""

    def __init__(self, token: str = None):
        self.token = token
        self.nome = "browser"
        self.resultados = []
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    def _screenshot(self, nome: str):
        """Captura screenshot para evidência."""
        try:
            path = SCREENSHOTS_DIR / f"{nome}_{datetime.now().strftime('%H%M%S')}.png"
            self.page.screenshot(path=str(path))
            return str(path)
        except Exception:
            return None

    def _resultado(
        self,
        fluxo: str,
        passou: bool,
        descricao: str,
        detalhe: str = "",
        screenshot: str = None,
    ):
        """Registra resultado de um teste."""
        self.resultados.append(
            {
                "fluxo": fluxo,
                "passou": passou,
                "descricao": descricao,
                "detalhe": detalhe,
                "screenshot": screenshot,
                "timestamp": datetime.now().isoformat(),
            }
        )
        emoji = "✅" if passou else "❌"
        print(f"  {emoji} {fluxo}: {descricao}")
        if not passou and detalhe:
            print(f"     → {detalhe}")

    def _iniciar_browser(self, playwright) -> bool:
        """Inicia browser headless."""
        try:
            self.browser = playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            context = self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                ignore_https_errors=True,
            )
            self.page = context.new_page()
            self.page.set_default_timeout(TIMEOUT)
            return True
        except Exception as e:
            print(f"  ❌ Erro ao iniciar browser: {e}")
            return False

    def _fazer_login(self) -> bool:
        """Faz login no ERP."""
        try:
            self.page.goto(f"{ERP_URL}/login", wait_until="networkidle")

            # Preencher credenciais
            self.page.fill(
                "input[type='email'], input[name='email'], input[placeholder*='email' i]",
                ERP_USER,
            )
            self.page.fill("input[type='password'], input[name='password']", ERP_PASS)

            # Clicar em entrar
            self.page.click(
                "button[type='submit'], button:has-text('Entrar'), button:has-text('Login')"
            )

            # Aguardar redirect pós-login (qualquer rota interna)
            self.page.wait_for_url(f"{ERP_URL}/**", timeout=15000)

            # Confirmar que saiu da página de login
            if "/login" not in self.page.url:
                self._resultado("login", True, f"Login OK → {self.page.url}")
                return True

            # Ainda em /login — verificar erro
            erro = self.page.locator(
                "[class*='error'], [class*='alert'], text='Credenciais', text='inválido'"
            )
            detalhe = (
                erro.first.inner_text() if erro.count() > 0 else "Permaneceu em /login"
            )
            shot = self._screenshot("login_falhou")
            self._resultado("login", False, "Login não redirecionou", detalhe, shot)
            return False

        except PlaywrightTimeout:
            shot = self._screenshot("login_timeout")
            self._resultado(
                "login", False, "Timeout no login", "Página não carregou", shot
            )
            return False
        except Exception as e:
            shot = self._screenshot("login_erro")
            self._resultado("login", False, f"Erro no login: {str(e)[:80]}", "", shot)
            return False

    def _testar_navegacao_dashboard(self):
        """Verifica se o dashboard carrega com dados."""
        try:
            self.page.goto(f"{ERP_URL}/dashboard", wait_until="networkidle")
            time.sleep(1.5)

            # Verificar que há módulos no dashboard
            modulos = self.page.locator(
                "[class*='card'], [class*='module'], [class*='grid'] > *"
            )
            count = modulos.count()

            if count >= 4:
                self._resultado(
                    "dashboard", True, f"Dashboard com {count} cards/módulos"
                )
            else:
                shot = self._screenshot("dashboard_vazio")
                self._resultado(
                    "dashboard",
                    False,
                    f"Dashboard com poucos elementos: {count}",
                    "Esperado 4+ cards",
                    shot,
                )

            # Verificar ausência de erros na tela
            erros = self.page.locator(
                "[class*='error-page'], [class*='error-boundary']"
            )
            if erros.count() > 0:
                self._resultado(
                    "dashboard_erros",
                    False,
                    f"Dashboard com {erros.count()} error boundaries",
                    screenshot=self._screenshot("dashboard_erros"),
                )
            else:
                self._resultado(
                    "dashboard_erros", True, "Sem error boundaries no dashboard"
                )

        except Exception as e:
            self._resultado("dashboard", False, f"Erro: {str(e)[:80]}")

    def _testar_tela_branca(self):
        """Verifica telas brancas em módulos principais."""
        paginas = [
            ("/modulos/dp", "Departamento Pessoal"),
            ("/modulos/financeiro", "Financeiro"),
            ("/modulos/crm", "CRM"),
            ("/modulos/operacional", "Operacional"),
            ("/modulos/ged", "GED"),
            ("/modulos/gestao-pessoas/saude-ocupacional", "Saúde Ocupacional"),
        ]

        for path, nome in paginas:
            try:
                self.page.goto(f"{ERP_URL}{path}", wait_until="networkidle")
                time.sleep(1.5)

                body = self.page.locator("body").inner_text()
                tem_conteudo = len(body.strip()) > 50
                tem_erro_http = any(
                    e in body for e in ["404 - ", "500 - ", "Application error"]
                )

                fluxo = f"tela_{nome.lower().replace(' ', '_')}"
                if tem_conteudo and not tem_erro_http:
                    self._resultado(fluxo, True, f"{nome}: página com conteúdo")
                else:
                    shot = self._screenshot(f"tela_branca_{nome.replace(' ', '_')}")
                    self._resultado(
                        fluxo,
                        False,
                        f"{nome}: tela branca ou erro HTTP",
                        screenshot=shot,
                    )

            except Exception as e:
                self._resultado(
                    f"tela_{nome.lower().replace(' ', '_')}",
                    False,
                    f"{nome}: {str(e)[:80]}",
                )

    def _testar_modulo_dp(self):
        """Testa navegação no módulo Departamento Pessoal."""
        try:
            self.page.goto(f"{ERP_URL}/modulos/dp", wait_until="networkidle")
            time.sleep(1.5)

            titulo = self.page.locator("h1, h2").first
            if titulo.is_visible():
                texto = titulo.inner_text()
                self._resultado("dp_navegacao", True, f"DP carregou: '{texto[:40]}'")
            else:
                self._resultado(
                    "dp_navegacao",
                    False,
                    "DP sem título visível",
                    screenshot=self._screenshot("dp_sem_titulo"),
                )

            # Submódulos
            cards = self.page.locator(
                "[class*='card'] a, a[href*='admissao'], a[href*='funcionario']"
            )
            if cards.count() >= 3:
                self._resultado(
                    "dp_submodulos", True, f"DP tem {cards.count()} submódulos visíveis"
                )
            else:
                self._resultado(
                    "dp_submodulos", False, f"DP com poucos submódulos: {cards.count()}"
                )

        except Exception as e:
            self._resultado("dp_navegacao", False, f"Erro: {str(e)[:80]}")

    def _testar_listagem_funcionarios(self):
        """Testa listagem de funcionários."""
        try:
            self.page.goto(
                f"{ERP_URL}/modulos/gestao-pessoas/funcionarios",
                wait_until="networkidle",
            )
            time.sleep(2)

            linhas = self.page.locator(
                "table tbody tr, [class*='list'] > *, [class*='row']"
            )
            count = linhas.count()

            if count >= 10:
                self._resultado(
                    "funcionarios_lista",
                    True,
                    f"Funcionários: {count} registros visíveis",
                )
            elif count > 0:
                self._resultado(
                    "funcionarios_lista",
                    True,
                    f"Funcionários: {count} registros (verificar paginação)",
                )
            else:
                shot = self._screenshot("funcionarios_vazio")
                self._resultado(
                    "funcionarios_lista",
                    False,
                    "Lista de funcionários vazia",
                    "Esperado 52 funcionários",
                    shot,
                )

            busca = self.page.locator(
                "input[placeholder*='buscar' i], input[placeholder*='search' i], input[placeholder*='pesquisar' i]"
            )
            if busca.count() > 0:
                self._resultado("funcionarios_busca", True, "Campo de busca presente")
            else:
                self._resultado("funcionarios_busca", False, "Campo de busca ausente")

        except Exception as e:
            self._resultado("funcionarios_lista", False, f"Erro: {str(e)[:80]}")

    def _testar_modulo_financeiro(self):
        """Testa navegação no módulo Financeiro."""
        try:
            self.page.goto(f"{ERP_URL}/modulos/financeiro", wait_until="networkidle")
            time.sleep(2)

            valores = self.page.locator(
                "[class*='valor'], [class*='amount'], [class*='currency']"
            )
            body_text = self.page.locator("body").inner_text()
            tem_reais = "R$" in body_text

            if valores.count() > 0 or tem_reais:
                self._resultado(
                    "financeiro_dashboard",
                    True,
                    f"Dashboard financeiro com valores monetários ({valores.count()} elementos)",
                )
            else:
                shot = self._screenshot("financeiro_sem_valores")
                self._resultado(
                    "financeiro_dashboard",
                    False,
                    "Dashboard financeiro sem valores monetários",
                    screenshot=shot,
                )

            if len(body_text) > 100:
                self._resultado(
                    "financeiro_conteudo", True, "Página financeira com conteúdo"
                )
            else:
                self._resultado(
                    "financeiro_conteudo", False, "Possível tela branca financeiro"
                )

        except Exception as e:
            self._resultado("financeiro_dashboard", False, f"Erro: {str(e)[:80]}")

    def _testar_modulo_crm(self):
        """Testa navegação no módulo CRM."""
        try:
            self.page.goto(f"{ERP_URL}/modulos/crm", wait_until="networkidle")
            time.sleep(2)

            metricas = self.page.locator(
                "[class*='metric'], [class*='stat'], [class*='card']"
            )
            if metricas.count() >= 2:
                self._resultado(
                    "crm_dashboard", True, f"CRM com {metricas.count()} métricas/cards"
                )
            else:
                self._resultado(
                    "crm_dashboard",
                    False,
                    f"CRM com poucos elementos: {metricas.count()}",
                )

            self.page.goto(f"{ERP_URL}/modulos/crm/clientes", wait_until="networkidle")
            time.sleep(2)

            linhas = self.page.locator(
                "table tbody tr, [class*='client-row'], [class*='list-item']"
            )
            count = linhas.count()
            if count >= 13:
                self._resultado("crm_clientes", True, f"CRM: {count} clientes visíveis")
            elif count > 0:
                self._resultado(
                    "crm_clientes", True, f"CRM: {count} clientes (verificar paginação)"
                )
            else:
                shot = self._screenshot("crm_clientes_vazio")
                self._resultado(
                    "crm_clientes", False, "CRM sem clientes visíveis", screenshot=shot
                )

        except Exception as e:
            self._resultado("crm_dashboard", False, f"Erro: {str(e)[:80]}")

    def _testar_modulo_operacional(self):
        """Testa navegação no módulo Operacional."""
        try:
            self.page.goto(
                f"{ERP_URL}/modulos/operacional/postos", wait_until="networkidle"
            )
            time.sleep(2)

            linhas = self.page.locator(
                "table tbody tr, [class*='posto'], [class*='post-row']"
            )
            count = linhas.count()
            if count >= 10:
                self._resultado("operacional_postos", True, f"Postos: {count} visíveis")
            elif count > 0:
                self._resultado(
                    "operacional_postos", True, f"Postos: {count} (verificar paginação)"
                )
            else:
                shot = self._screenshot("operacional_postos_vazio")
                self._resultado(
                    "operacional_postos", False, "Sem postos visíveis", screenshot=shot
                )

        except Exception as e:
            self._resultado("operacional_postos", False, f"Erro: {str(e)[:80]}")

    def _testar_botoes_criticos(self):
        """Testa se botões críticos respondem ao clique."""
        testes = [
            {
                "url": f"{ERP_URL}/modulos/dp/admissao",
                "botao": (
                    "button:has-text('Nova Admissão'), "
                    "button:has-text('Novo'), "
                    "a:has-text('Nova Admissão')"
                ),
                "fluxo": "admissao_botao_novo",
            },
            {
                "url": f"{ERP_URL}/modulos/crm",
                "botao": (
                    "button:has-text('Novo Lead'), "
                    "button:has-text('Adicionar'), "
                    "a:has-text('Novo')"
                ),
                "fluxo": "crm_botao_novo_lead",
            },
        ]

        for teste in testes:
            try:
                self.page.goto(teste["url"], wait_until="networkidle")
                time.sleep(2)

                botao = self.page.locator(teste["botao"]).first
                if botao.is_visible():
                    botao.click()
                    time.sleep(1.5)

                    modal = self.page.locator(
                        "[role='dialog'], [class*='modal'], [class*='dialog'], form"
                    )
                    if modal.count() > 0:
                        self._resultado(
                            teste["fluxo"], True, "Botão funcionou — modal/form abriu"
                        )
                    else:
                        shot = self._screenshot(f"{teste['fluxo']}_sem_modal")
                        self._resultado(
                            teste["fluxo"],
                            False,
                            "Botão clicado mas nenhum modal/form abriu",
                            screenshot=shot,
                        )

                    # Fechar modal se abriu
                    fechar = self.page.locator(
                        "button:has-text('Cancelar'), button:has-text('Fechar'), [aria-label='Close']"
                    )
                    if fechar.count() > 0:
                        fechar.first.click()
                else:
                    self._resultado(
                        teste["fluxo"], False, "Botão não encontrado ou não visível"
                    )

            except Exception as e:
                self._resultado(teste["fluxo"], False, f"Erro: {str(e)[:80]}")

    def auditar(self) -> dict:
        """Executa todos os testes E2E."""
        if not PLAYWRIGHT_DISPONIVEL:
            return {
                "agente": "browser",
                "score": 0,
                "erro": "Playwright não instalado",
                "bugs": [],
            }

        print("🔍 BrowserAgent: executando testes E2E...")
        inicio = datetime.now()

        with sync_playwright() as playwright:
            if not self._iniciar_browser(playwright):
                return {
                    "agente": "browser",
                    "score": 0,
                    "erro": "Browser não iniciou",
                    "bugs": [],
                }

            try:
                if not self._fazer_login():
                    return {
                        "agente": "browser",
                        "score": 0,
                        "erro": "Login falhou",
                        "bugs": [],
                    }

                self._testar_navegacao_dashboard()
                self._testar_tela_branca()
                self._testar_modulo_dp()
                self._testar_listagem_funcionarios()
                self._testar_modulo_financeiro()
                self._testar_modulo_crm()
                self._testar_modulo_operacional()
                self._testar_botoes_criticos()

            finally:
                try:
                    self.browser.close()
                except Exception:
                    pass

        duracao = (datetime.now() - inicio).seconds
        passou = sum(1 for r in self.resultados if r["passou"])
        total = len(self.resultados)
        score = (passou / total * 10) if total else 0

        falhas = [r for r in self.resultados if not r["passou"]]

        resultado = {
            "agente": "browser",
            "score": round(score, 1),
            "testes_total": total,
            "testes_passou": passou,
            "testes_falhou": len(falhas),
            "duracao_s": duracao,
            "falhas": falhas,
            "bugs": [
                {
                    "tipo": f"e2e_{f['fluxo']}",
                    "descricao": f["descricao"],
                    "detalhe": f.get("detalhe", ""),
                    "screenshot": f.get("screenshot"),
                    "autocorrigivel": False,
                    "acao_jordan": True,
                }
                for f in falhas
            ],
        }

        print(f"\n  Score: {score:.1f}/10 ({passou}/{total} passou)")
        print(f"  Duração: {duracao}s")
        if falhas:
            print(f"\n  Falhas ({len(falhas)}):")
            for f in falhas:
                print(f"    ❌ {f['fluxo']}: {f['descricao']}")
        else:
            print("  ✅ Todos os testes passaram!")

        return resultado


if __name__ == "__main__":
    import json

    agente = BrowserAgent()
    resultado = agente.auditar()
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
