"""
tests/load/locustfile.py
Testes de carga com Locust para endpoints criticos do Conecta PRO.

Executar:
    cd /opt/conecta-pro/backend
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --headless \
           -u 50 -r 5 -t 60s --csv=../reports/locust

Ou com UI:
    locust -f tests/load/locustfile.py --host=http://localhost:8000
    # Acessar http://localhost:8089
"""

from locust import HttpUser, between, tag, task


class ConectaProUser(HttpUser):
    """Simula um usuario do Conecta PRO."""

    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Login ao iniciar."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@conectaplus.com.br",
                "password": "admin123",
            },
            name="/api/v1/auth/login",
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
        else:
            self.token = ""

    @property
    def headers(self):
        """Headers com autenticacao."""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    @tag("health")
    def health_check(self):
        """Endpoint de health check."""
        self.client.get("/health", name="/health")

    @task(5)
    @tag("operacional")
    def listar_escalas(self):
        """Lista escalas do modulo operacional."""
        self.client.get(
            "/api/v1/operacional/escalas",
            headers=self.headers,
            name="/api/v1/operacional/escalas",
        )

    @task(5)
    @tag("financial")
    def dashboard_financeiro(self):
        """Dashboard financeiro."""
        self.client.get(
            "/api/v1/financial/dashboard",
            headers=self.headers,
            name="/api/v1/financial/dashboard",
        )

    @task(3)
    @tag("clients")
    def listar_clientes(self):
        """Lista clientes."""
        self.client.get(
            "/api/v1/clients",
            headers=self.headers,
            name="/api/v1/clients",
        )

    @task(2)
    @tag("operacional")
    def listar_postos(self):
        """Lista postos de servico."""
        self.client.get(
            "/api/v1/operacional/postos",
            headers=self.headers,
            name="/api/v1/operacional/postos",
        )

    @task(2)
    @tag("hr")
    def listar_funcionarios(self):
        """Lista funcionarios."""
        self.client.get(
            "/api/v1/hr/employees",
            headers=self.headers,
            name="/api/v1/hr/employees",
        )

    @task(1)
    @tag("government")
    def esocial_status(self):
        """Verifica status eSocial."""
        self.client.get(
            "/api/v1/government/esocial/status",
            headers=self.headers,
            name="/api/v1/government/esocial/status",
        )


class ConectaProReadHeavy(HttpUser):
    """Usuario com foco em leitura pesada (relatorios)."""

    wait_time = between(3, 8)
    token = None
    weight = 1  # Menos frequente

    def on_start(self):
        """Login ao iniciar."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@conectaplus.com.br",
                "password": "admin123",
            },
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token", "")

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(1)
    @tag("reports")
    def relatorio_financeiro(self):
        """Gera relatorio financeiro (pesado)."""
        self.client.get(
            "/api/v1/financial/reports/monthly",
            headers=self.headers,
            name="/api/v1/financial/reports/monthly",
        )

    @task(1)
    @tag("reports")
    def relatorio_operacional(self):
        """Gera relatorio operacional."""
        self.client.get(
            "/api/v1/operacional/reports/summary",
            headers=self.headers,
            name="/api/v1/operacional/reports/summary",
        )
