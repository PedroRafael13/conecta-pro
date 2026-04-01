"""
Testes E2E — Fiscal Fases 3, 6, 7, 8
DominioExporterAgent, BookkeeperAutoAgent, FinancialStatementsAgent + endpoints HTTP
"""

import pytest
from httpx import ASGITransport, AsyncClient

# ── Unit tests: DominioExporterAgent ─────────────────────────────────────────


class TestDominioExporterAgent:
    def setup_method(self):
        from modules.empresas.agents.dominio_exporter import DominioExporterAgent

        self.agent = DominioExporterAgent()

    def test_gerar_plano_contas(self):
        r = self.agent.gerar_plano_contas("conecta_eletronica")
        assert r["sucesso"] is True
        assert r["empresa"] == "conecta_eletronica"
        assert r["total_contas"] > 0
        assert r["nome_arquivo"] == "PLANO_CONTAS_CONECTA_ELETRONICA.TXT"
        assert "CODIGO|DESCRICAO" in r["conteudo"]
        assert r["formato"] == "DOMINIO_TOTVS_PLANO_CONTAS_V12"

    def test_exportar_lancamentos_vazio(self):
        r = self.agent.exportar_lancamentos("conecta_eletronica", "2026-03", [])
        assert r["sucesso"] is True
        assert r["total_lancamentos"] == 0
        assert r["balanceado"] is True
        assert "CAB|DOMINIO|V12|CONECTA_ELETRONICA|03/2026" in r["conteudo"]

    def test_exportar_lancamentos_com_dados(self):
        lancamentos = [
            {
                "data": "01/03/2026",
                "historico": "Receita de Serviços",
                "conta_debito": "1.1.2.01",
                "conta_credito": "3.1.1.03",
                "valor": 100000,
                "tipo": "D",
                "complemento": "NF-001",
            }
        ]
        r = self.agent.exportar_lancamentos("conecta_eletronica", "2026-03", lancamentos)
        assert r["sucesso"] is True
        assert r["total_lancamentos"] == 1
        assert r["total_debitos"] == 100000.0
        assert "LAN|01/03/2026" in r["conteudo"]
        assert r["nome_arquivo"] == "LANCAMENTOS_CONECTA_ELETRONICA_202603.TXT"

    def test_exportar_clientes(self):
        clientes = [
            {
                "id": 1,
                "nome": "Cliente Teste Ltda",
                "cnpj": "12345678000195",
                "municipio": "Manaus",
                "uf": "AM",
                "cep": "69000000",
                "email": "cliente@teste.com",
            }
        ]
        r = self.agent.exportar_clientes("conecta_eletronica", clientes)
        assert r["sucesso"] is True
        assert r["total_clientes"] == 1
        assert "CLI|000001|Cliente Teste Ltda" in r["conteudo"]
        assert r["nome_arquivo"] == "CLIENTES_CONECTA_ELETRONICA.TXT"

    def test_exportar_nfse_para_dominio(self):
        notas = [
            {
                "numero": "NF-001",
                "tomador": "Empresa ABC Ltda",
                "tipo_servico": "eletronica",
                "valor_servico": 50000,
                "iss": 2500,
                "pis": 825,
                "cofins": 3800,
                "data_emissao": "05/03/2026",
            }
        ]
        r = self.agent.exportar_nfse_para_dominio("conecta_eletronica", "2026-03", notas)
        assert r["sucesso"] is True
        # Deve gerar: 1 lançamento receita + 1 ISS + 1 PIS + 1 COFINS = 4
        assert r["total_lancamentos"] == 4
        assert r["total_debitos"] > 0

    def test_formatacao_cnpj(self):
        r = self.agent.exportar_clientes("empresa", [{"id": 1, "nome": "Teste", "cnpj": "35710481000103"}])
        assert "35.710.481/0001-03" in r["conteudo"]

    def test_formatacao_cep(self):
        r = self.agent.exportar_clientes("empresa", [{"id": 1, "nome": "Teste", "cep": "69050000"}])
        assert "69050-000" in r["conteudo"]

    def test_plano_contas_natureza_correta(self):
        r = self.agent.gerar_plano_contas("empresa")
        linhas = r["conteudo"].split("\r\n")
        # Linha de ativo deve ter natureza D
        ativo = next(line for line in linhas if line.startswith("1.1.1.01"))
        assert "|D|" in ativo
        # Linha de passivo deve ter natureza C
        passivo = next(line for line in linhas if line.startswith("2.1.1.01"))
        assert "|C|" in passivo


# ── Unit tests: BookkeeperAutoAgent ──────────────────────────────────────────


class TestBookkeeperAutoAgent:
    def setup_method(self):
        from modules.empresas.agents.bookkeeper_auto import BookkeeperAutoAgent

        self.agent = BookkeeperAutoAgent()

    def test_lancamentos_folha_basico(self):
        funcionarios = [
            {"salario_bruto": 3000, "inss_patronal": 660, "fgts": 240},
            {"salario_bruto": 2500, "inss_patronal": 550, "fgts": 200},
        ]
        r = self.agent.gerar_lancamentos_folha("conecta_patrimonial", "2026-03", funcionarios)
        assert r["sucesso"] is True
        assert r["total_funcionarios"] == 2
        assert r["totais"]["salarios"] == 5500.0
        assert r["totais"]["inss_patronal"] == 1210.0
        assert r["totais"]["fgts"] == 440.0
        assert r["total_lancamentos"] == 5  # salarios + inss + fgts + ferias + decimo
        assert r["totais"]["custo_total"] > 5500

    def test_lancamentos_folha_vazia(self):
        r = self.agent.gerar_lancamentos_folha("empresa", "2026-03", [])
        assert r["sucesso"] is True
        assert r["total_funcionarios"] == 0
        # Mesmo sem funcionários, provisões são geradas (zero)
        assert r["total_lancamentos"] == 2  # provisão férias e decimo com valor 0

    def test_lancamentos_impostos_lucro_real(self):
        impostos = {"irpj": 15000, "csll": 9000, "pis": 3300, "cofins": 15200}
        r = self.agent.gerar_lancamentos_impostos("conecta_eletronica", "2026-03", impostos, "lucro_real")
        assert r["sucesso"] is True
        assert r["regime"] == "lucro_real"
        assert r["total_lancamentos"] == 4
        assert r["total_impostos"] == 42500.0

    def test_lancamentos_impostos_simples(self):
        impostos = {"das": 28000}
        r = self.agent.gerar_lancamentos_impostos("conecta_patrimonial", "2026-03", impostos, "simples_nacional")
        assert r["sucesso"] is True
        assert r["regime"] == "simples_nacional"
        assert r["total_lancamentos"] == 1
        assert r["total_impostos"] == 28000.0

    def test_resumo_contabil_mensal(self):
        r = self.agent.resumo_contabil_mensal(
            empresa_slug="conecta_eletronica",
            periodo="2026-03",
            receitas=350000,
            custos_folha=250000,
            impostos=42000,
            despesas_admin=20000,
        )
        assert r["sucesso"] is True
        assert r["dre_resumido"]["receita_bruta"] == 350000
        assert r["dre_resumido"]["lucro_bruto"] == 100000
        assert r["dre_resumido"]["lucro_operacional"] == 80000
        assert r["dre_resumido"]["lucro_liquido"] == 38000
        assert r["dre_resumido"]["margem_bruta_pct"] == pytest.approx(28.57, abs=0.1)
        assert r["classificacao"] in ["EXCELENTE", "BOM", "REGULAR", "CRÍTICO", "PREJUÍZO"]

    def test_resumo_classificacao_excelente(self):
        r = self.agent.resumo_contabil_mensal(
            "emp", "2026-03", receitas=100000, custos_folha=10000, impostos=5000, despesas_admin=5000
        )
        assert r["classificacao"] == "EXCELENTE"

    def test_resumo_classificacao_prejuizo(self):
        r = self.agent.resumo_contabil_mensal(
            "emp", "2026-03", receitas=100000, custos_folha=120000, impostos=5000, despesas_admin=5000
        )
        assert r["classificacao"] == "PREJUÍZO"
        assert len(r["alertas"]) > 0

    def test_alertas_custo_elevado(self):
        r = self.agent.resumo_contabil_mensal(
            "emp", "2026-03", receitas=100000, custos_folha=85000, impostos=5000, despesas_admin=5000
        )
        alertas = r["alertas"]
        assert any("mão de obra" in a.lower() for a in alertas)


# ── Unit tests: FinancialStatementsAgent ─────────────────────────────────────


class TestFinancialStatementsAgent:
    def setup_method(self):
        from modules.empresas.agents.financial_statements import FinancialStatementsAgent

        self.agent = FinancialStatementsAgent()

    def test_gerar_dre_lucro_real(self):
        dados = {
            "receita_bruta": 350000,
            "deducoes": 31500,
            "custos": {"folha": 200000, "encargos": 60000},
            "despesas": {"admin": 20000, "aluguel": 5000},
            "outros": {"receitas_financeiras": 0, "despesas_financeiras": 2000},
        }
        r = self.agent.gerar_dre("conecta_eletronica", "2026-03", dados, "lucro_real")
        assert r["sucesso"] is True
        assert r["dre"]["receita_bruta"] == 350000
        assert r["dre"]["receita_liquida"] == 318500
        assert r["dre"]["lucro_bruto"] == 58500
        assert r["dre"]["total_custos"] == 260000
        assert r["dre"]["impostos_sobre_lucro"] > 0
        assert r["dre"]["lucro_liquido"] < r["dre"]["lair"]
        assert r["indicadores"]["classificacao"] in ["EXCELENTE", "BOM", "REGULAR", "CRÍTICO", "PREJUÍZO"]

    def test_gerar_dre_simples_nacional(self):
        dados = {
            "receita_bruta": 150000,
            "deducoes": 0,
            "custos": {"folha": 100000},
            "despesas": {"admin": 10000},
            "outros": {},
            "das": 12000,
        }
        r = self.agent.gerar_dre("conecta_patrimonial", "2026-03", dados, "simples_nacional")
        assert r["sucesso"] is True
        assert r["regime"] == "simples_nacional"
        assert r["dre"]["impostos_sobre_lucro"] == 12000

    def test_gerar_balanco_sintetico(self):
        dados = {
            "ativo_circulante": {"caixa": 50000, "clientes": 120000},
            "ativo_nao_circulante": {"imobilizado": 80000},
            "passivo_circulante": {"fornecedores": 30000, "obrigacoes_trab": 45000, "obrigacoes_trib": 20000},
            "passivo_nao_circulante": {},
            "patrimonio_liquido": {"capital": 155000},
        }
        r = self.agent.gerar_balanco_sintetico("conecta_eletronica", "2026-03-31", dados)
        assert r["sucesso"] is True
        assert r["balanco"]["ativo"]["total_ativo"] == 250000
        assert r["balanco"]["passivo"]["total_passivo"] == 250000
        assert r["balanceado"] is True
        assert r["indicadores"]["liquidez_corrente"] == pytest.approx(1.789, abs=0.01)

    def test_balanco_desbalanceado(self):
        dados = {
            "ativo_circulante": {"caixa": 100000},
            "ativo_nao_circulante": {},
            "passivo_circulante": {"fornecedores": 50000},
            "passivo_nao_circulante": {},
            "patrimonio_liquido": {"capital": 40000},  # 50+40 = 90 != 100
        }
        r = self.agent.gerar_balanco_sintetico("empresa", "2026-03-31", dados)
        assert r["sucesso"] is True
        assert r["balanceado"] is False

    def test_gerar_dfc_indireto(self):
        dados = {
            "lucro_liquido": 38000,
            "depreciacao": 3000,
            "amortizacao": 0,
            "variacao_contas_receber": 10000,
            "variacao_fornecedores": 5000,
            "variacao_obrigacoes_trabalhistas": 2000,
            "variacao_impostos": 1500,
            "aquisicao_imobilizado": 0,
            "emprestimos_obtidos": 0,
            "amortizacao_emprestimos": 0,
            "distribuicao_lucros": 0,
            "saldo_caixa_inicial": 80000,
        }
        r = self.agent.gerar_dfc_indireto("conecta_eletronica", "2026-03", dados)
        assert r["sucesso"] is True
        assert r["dfc"]["saldo_inicial"] == 80000
        assert r["dfc"]["variacao_caixa"] != 0
        assert r["dfc"]["saldo_final"] == r["dfc"]["saldo_inicial"] + r["dfc"]["variacao_caixa"]
        assert r["saude_caixa"] in ["POSITIVO", "NEGATIVO"]

    def test_gerar_consolidado_grupo(self):
        empresas = [
            {
                "empresa": "Conecta Eletrônica",
                "receita_bruta": 200000,
                "total_custos": 130000,
                "total_despesas": 20000,
                "impostos": 25000,
                "lucro_liquido": 25000,
            },
            {
                "empresa": "Conecta Patrimonial",
                "receita_bruta": 150000,
                "total_custos": 110000,
                "total_despesas": 15000,
                "impostos": 8000,
                "lucro_liquido": 17000,
            },
        ]
        r = self.agent.gerar_consolidado_grupo("2026-03", empresas)
        assert r["sucesso"] is True
        assert r["empresas"] == 2
        assert r["consolidado"]["receita_total"] == 350000
        assert r["consolidado"]["lucro_liquido_total"] == 42000
        assert r["maior_contribuidor"] == "Conecta Eletrônica"
        assert r["consolidado"]["margem_liquida_grupo_pct"] == pytest.approx(12.0, abs=0.1)

    def test_consolidado_vazio(self):
        r = self.agent.gerar_consolidado_grupo("2026-03", [])
        assert r["sucesso"] is True
        assert r["consolidado"]["receita_total"] == 0
        assert r["maior_contribuidor"] == ""


# ── HTTP Endpoint tests (sync via live server on port 8080) ───────────────────
# Using httpx.Client against live server avoids pytest-asyncio source inspection issues

import httpx as _httpx  # noqa: E402

BASE = "http://localhost:8080/api/v1"


class TestHTTPEndpoints:
    """Testes HTTP contra o servidor ao vivo na porta 8080"""

    def test_http_plano_contas(self):
        r = _httpx.get(f"{BASE}/empresas/dominio/plano-contas/conecta_eletronica")
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["total_contas"] > 0
        assert data["empresa"] == "conecta_eletronica"

    def test_http_exportar_lancamentos(self):
        r = _httpx.post(
            f"{BASE}/empresas/dominio/lancamentos",
            json={
                "empresa_slug": "conecta_eletronica",
                "periodo": "2026-03",
                "lancamentos": [
                    {
                        "data": "01/03/2026",
                        "historico": "Receita Teste",
                        "conta_debito": "1.1.2.01",
                        "conta_credito": "3.1.1.03",
                        "valor": 50000,
                        "tipo": "D",
                    }
                ],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["total_lancamentos"] == 1

    def test_http_exportar_clientes(self):
        r = _httpx.post(
            f"{BASE}/empresas/dominio/clientes",
            json={
                "empresa_slug": "conecta_eletronica",
                "clientes": [{"id": 1, "nome": "Cliente HTTP Ltda", "cnpj": "12345678000195", "uf": "AM"}],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["total_clientes"] == 1

    def test_http_exportar_nfse(self):
        r = _httpx.post(
            f"{BASE}/empresas/dominio/nfse",
            json={
                "empresa_slug": "conecta_eletronica",
                "periodo": "2026-03",
                "notas": [
                    {
                        "numero": "NF-001",
                        "tomador": "Empresa XYZ",
                        "tipo_servico": "eletronica",
                        "valor_servico": 30000,
                        "iss": 1500,
                        "pis": 495,
                        "cofins": 2280,
                        "data_emissao": "01/03/2026",
                    }
                ],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["total_lancamentos"] == 4  # receita + iss + pis + cofins

    def test_http_lancamentos_folha(self):
        r = _httpx.post(
            f"{BASE}/empresas/contabilidade/lancamentos/folha",
            json={
                "empresa_slug": "conecta_patrimonial",
                "competencia": "2026-03",
                "funcionarios": [
                    {"salario_bruto": 4000, "inss_patronal": 880, "fgts": 320},
                ],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["totais"]["salarios"] == 4000

    def test_http_lancamentos_impostos(self):
        r = _httpx.post(
            f"{BASE}/empresas/contabilidade/lancamentos/impostos",
            json={
                "empresa_slug": "conecta_eletronica",
                "competencia": "2026-03",
                "impostos": {"irpj": 15000, "csll": 9000},
                "regime": "lucro_real",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["total_impostos"] == 24000

    def test_http_resumo_mensal(self):
        r = _httpx.post(
            f"{BASE}/empresas/contabilidade/resumo-mensal",
            json={
                "empresa_slug": "conecta_eletronica",
                "periodo": "2026-03",
                "receitas": 350000,
                "custos_folha": 250000,
                "impostos": 42000,
                "despesas_admin": 20000,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["dre_resumido"]["receita_bruta"] == 350000

    def test_http_dre(self):
        r = _httpx.post(
            f"{BASE}/empresas/demonstrativos/dre",
            json={
                "empresa_slug": "conecta_eletronica",
                "periodo": "2026-03",
                "dados": {
                    "receita_bruta": 350000,
                    "deducoes": 31500,
                    "custos": {"folha": 200000, "encargos": 60000},
                    "despesas": {"admin": 20000},
                    "outros": {},
                },
                "regime": "lucro_real",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["dre"]["receita_bruta"] == 350000
        assert "classificacao" in data["indicadores"]

    def test_http_balanco(self):
        r = _httpx.post(
            f"{BASE}/empresas/demonstrativos/balanco",
            json={
                "empresa_slug": "conecta_eletronica",
                "data_base": "2026-03-31",
                "dados": {
                    "ativo_circulante": {"caixa": 80000},
                    "ativo_nao_circulante": {"imob": 70000},
                    "passivo_circulante": {"fornec": 50000},
                    "passivo_nao_circulante": {},
                    "patrimonio_liquido": {"capital": 100000},
                },
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["balanco"]["ativo"]["total_ativo"] == 150000

    def test_http_dfc(self):
        r = _httpx.post(
            f"{BASE}/empresas/demonstrativos/dfc",
            json={
                "empresa_slug": "conecta_eletronica",
                "periodo": "2026-03",
                "dados": {
                    "lucro_liquido": 38000,
                    "depreciacao": 3000,
                    "variacao_contas_receber": 5000,
                    "saldo_caixa_inicial": 80000,
                },
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert "dfc" in data
        assert data["dfc"]["saldo_inicial"] == 80000

    def test_http_consolidado_grupo(self):
        r = _httpx.post(
            f"{BASE}/empresas/demonstrativos/consolidado-grupo",
            json={
                "periodo": "2026-03",
                "empresas": [
                    {
                        "empresa": "Eletrônica",
                        "receita_bruta": 200000,
                        "total_custos": 130000,
                        "total_despesas": 20000,
                        "impostos": 25000,
                        "lucro_liquido": 25000,
                    },
                    {
                        "empresa": "Patrimonial",
                        "receita_bruta": 150000,
                        "total_custos": 110000,
                        "total_despesas": 15000,
                        "impostos": 8000,
                        "lucro_liquido": 17000,
                    },
                ],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["sucesso"] is True
        assert data["consolidado"]["receita_total"] == 350000
        assert data["maior_contribuidor"] == "Eletrônica"

    def test_http_download_plano_contas(self):
        r = _httpx.get(f"{BASE}/empresas/dominio/download/plano-contas/conecta_eletronica")
        assert r.status_code == 200
        assert "attachment" in r.headers.get("content-disposition", "")
        assert "PLANO_CONTAS_CONECTA_ELETRONICA.TXT" in r.headers.get("content-disposition", "")
        assert len(r.text) > 0
