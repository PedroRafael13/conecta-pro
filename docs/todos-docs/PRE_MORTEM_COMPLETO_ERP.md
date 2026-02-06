# 🔮 PRÉ-MORTEM COMPLETO - ERP CONECTA MAIS
## ANTECIPANDO TODOS OS PROBLEMAS E SOLUÇÕES PREVENTIVAS

---

## 📋 ÍNDICE DE RISCOS

1. **Riscos Técnicos** (25 riscos)
2. **Riscos de Processo** (15 riscos)
3. **Riscos de Negócio** (12 riscos)
4. **Riscos de Equipe** (10 riscos)
5. **Riscos de Infraestrutura** (18 riscos)
6. **Riscos Específicos do Projeto** (20 riscos)

**TOTAL: 100 RISCOS MAPEADOS COM SOLUÇÕES**

---

# CATEGORIA 1: RISCOS TÉCNICOS

---

## ⚠️ RISCO T-001: Performance Degradada com Crescimento

### Descrição do Problema:
Sistema funciona bem com 100 usuários, mas trava com 1000+.

### Probabilidade: ALTA
### Impacto: CRÍTICO

### Sinais de Alerta:
- Tempo de resposta API > 1s
- Queries SQL > 500ms
- CPU server > 80%
- Memória > 85%

### Solução Preventiva (Implementar AGORA):

```python
# 1. Configurar caching desde o início
from redis import Redis
from functools import wraps
import hashlib
import json

redis_client = Redis(host='localhost', port=6379, db=0)

def cache_response(ttl=300):
    """Cache decorator para endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave única baseada em função + parâmetros
            cache_key = f"cache:{func.__name__}:{hashlib.md5(
                json.dumps(kwargs, sort_keys=True).encode()
            ).hexdigest()}"
            
            # Tentar buscar do cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Uso:
@router.get("/leads")
@cache_response(ttl=60)  # Cache por 1 minuto
async def get_leads():
    return await lead_service.get_all()
```

```python
# 2. Implementar paginação SEMPRE
from fastapi import Query

@router.get("/leads")
async def get_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    offset = (page - 1) * page_size
    leads = await db.query(Lead).offset(offset).limit(page_size).all()
    total = await db.query(Lead).count()
    
    return {
        "items": leads,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

```python
# 3. Configurar índices de banco DESDE O INÍCIO
# alembic/versions/001_initial_schema.py

def upgrade():
    # Tabela leads
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('score', sa.Integer()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )
    
    # ÍNDICES CRÍTICOS
    op.create_index('idx_leads_email', 'leads', ['email'])
    op.create_index('idx_leads_score', 'leads', ['score'])
    op.create_index('idx_leads_created_at', 'leads', ['created_at'])
    op.create_index('idx_leads_composite', 'leads', ['score', 'created_at'])  # Queries complexas
```

```python
# 4. Implementar connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Número de conexões permanentes
    max_overflow=10,       # Conexões extras temporárias
    pool_timeout=30,       # Timeout para obter conexão
    pool_recycle=3600,     # Reciclar conexão após 1h
    pool_pre_ping=True     # Verificar conexão antes de usar
)
```

```python
# 5. Queries otimizadas com eager loading
from sqlalchemy.orm import selectinload, joinedload

# ❌ RUIM - N+1 problem
leads = await db.query(Lead).all()
for lead in leads:
    print(lead.opportunities)  # Query adicional POR lead!

# ✅ BOM - Eager loading
leads = await db.query(Lead).options(
    selectinload(Lead.opportunities)
).all()
```

### Checklist de Validação (Toda Sprint):

```bash
# Script de monitoramento de performance
# scripts/check_performance.sh

#!/bin/bash

echo "🔍 Verificando Performance..."

# 1. Tempo de resposta endpoints
echo "1. Testando tempo de resposta..."
response_time=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:8000/api/v1/leads)
if (( $(echo "$response_time > 1.0" | bc -l) )); then
    echo "❌ ALERTA: Tempo de resposta > 1s ($response_time s)"
else
    echo "✅ OK: Tempo de resposta: $response_time s"
fi

# 2. Queries lentas
echo "2. Verificando queries lentas..."
psql -U erp_user -d erp_dev -c "
    SELECT query, calls, mean_exec_time, max_exec_time 
    FROM pg_stat_statements 
    WHERE mean_exec_time > 500 
    ORDER BY mean_exec_time DESC 
    LIMIT 10;
"

# 3. Tamanho do cache Redis
echo "3. Verificando cache Redis..."
redis-cli INFO | grep used_memory_human

# 4. CPU e Memória
echo "4. Verificando recursos..."
top -bn1 | grep "Cpu(s)" | awk '{print "CPU: " $2}'
free -m | awk 'NR==2{printf "Memória: %s/%sMB (%.2f%%)\n", $3,$2,$3*100/$2 }'

echo "✅ Verificação concluída!"
```

### Plano de Contingência (Se Acontecer):

```yaml
# Plano de resposta imediata
1. Ativar rate limiting emergencial:
   - Limitar requests por IP: 100/min
   - Bloquear IPs maliciosos

2. Aumentar cache TTL:
   - Cache endpoints críticos: 5min → 15min
   - Ativar cache agressivo temporariamente

3. Escalar horizontalmente (imediato):
   - Subir mais instâncias do backend
   - Load balancer distribui carga

4. Queries críticas:
   - Criar índices temporários
   - Simplificar queries complexas

5. Comunicação:
   - Notificar clientes de possível lentidão
   - Status page atualizada
```

---

## ⚠️ RISCO T-002: Falha de Integração com APIs Externas

### Descrição do Problema:
API do Banco Cora/Inter/eSocial/SEFAZ fica fora do ar ou muda contrato.

### Probabilidade: MÉDIA
### Impacto: CRÍTICO

### Solução Preventiva:

```python
# 1. Implementar Circuit Breaker Pattern
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal
    OPEN = "open"          # Falhando, não tenta
    HALF_OPEN = "half_open"  # Testando recuperação

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, success_threshold=2):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # segundos
        self.success_threshold = success_threshold
        
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            # Verificar se timeout passou
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
                self.successes = 0
            else:
                raise Exception("Circuit breaker is OPEN - API indisponível")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
    
    def on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            # Alertar equipe!
            send_alert(f"Circuit breaker OPEN - API falhando!")

# Uso:
cora_circuit = CircuitBreaker()

def get_bank_statement():
    return cora_circuit.call(cora_api.get_statement)
```

```python
# 2. Implementar Retry com Exponential Backoff
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),  # Tentar 3 vezes
    wait=wait_exponential(multiplier=1, min=4, max=10),  # 4s, 8s, 10s
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.cora.com.br/...")
        return response.json()
```

```python
# 3. Implementar Fallback para cada integração
class BankIntegrationService:
    def __init__(self):
        self.primary_bank = CoraAPI()
        self.fallback_bank = InterAPI()
    
    async def get_statement(self, account_id):
        try:
            # Tentar banco primário
            return await self.primary_bank.get_statement(account_id)
        except Exception as e:
            logger.warning(f"Cora API falhou: {e}. Usando fallback Inter.")
            
            try:
                # Fallback para banco secundário
                return await self.fallback_bank.get_statement(account_id)
            except Exception as e2:
                logger.error(f"Ambos bancos falharam: {e2}")
                
                # Último recurso: dados em cache
                cached = await get_cached_statement(account_id)
                if cached:
                    logger.info("Usando dados em cache")
                    return cached
                
                raise Exception("Todos os métodos falharam")
```

```python
# 4. Webhook para notificações assíncronas
# Em vez de polling, usar webhooks quando possível

@router.post("/webhooks/cora")
async def cora_webhook(payload: dict):
    """
    Cora envia notificação quando há transação
    """
    # Validar assinatura do webhook
    if not validate_webhook_signature(payload):
        raise HTTPException(401, "Invalid signature")
    
    # Processar evento
    if payload['event'] == 'payment.confirmed':
        await process_payment(payload['data'])
    
    return {"status": "ok"}
```

```python
# 5. Queue de retry para operações críticas
from celery import Celery

celery_app = Celery('erp', broker='redis://localhost:6379/0')

@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=300  # 5 minutos
)
def send_to_esocial(self, event_data):
    """
    Envia evento para eSocial com retry automático
    """
    try:
        response = esocial_api.send_event(event_data)
        return response
    except Exception as e:
        logger.error(f"eSocial falhou: {e}")
        # Retry automático após 5 minutos
        raise self.retry(exc=e)
```

### Checklist de Validação:

```python
# Script de health check de integrações
# scripts/check_integrations.py

import httpx
import asyncio

async def check_integration_health():
    """Verifica saúde de todas as integrações"""
    
    integrations = {
        'Banco Cora': 'https://api.cora.com.br/health',
        'Banco Inter': 'https://cdpj.partners.bancointer.com.br/health',
        'eSocial': 'https://api.esocial.gov.br/health',
        'SEFAZ': 'https://nfe.fazenda.gov.br/health',
    }
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        for name, url in integrations.items():
            try:
                response = await client.get(url, timeout=5)
                status = "✅ OK" if response.status_code == 200 else "❌ FALHA"
                results[name] = {
                    'status': status,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                results[name] = {
                    'status': '❌ ERRO',
                    'error': str(e)
                }
    
    # Enviar para monitoring
    send_to_datadog(results)
    
    # Alertar se algum falhou
    failed = [k for k, v in results.items() if 'ERRO' in v['status'] or 'FALHA' in v['status']]
    if failed:
        send_alert(f"Integrações falhando: {', '.join(failed)}")
    
    return results

# Rodar a cada 5 minutos via cron
# */5 * * * * python scripts/check_integrations.py
```

---

## ⚠️ RISCO T-003: Vazamento de Dados Sensíveis

### Descrição do Problema:
Dados pessoais (CPF, salários, etc) vazam por log, erro, ou falha de segurança.

### Probabilidade: MÉDIA
### Impacto: CATASTRÓFICO (LGPD + Processos)

### Solução Preventiva:

```python
# 1. Sanitização automática de logs
import re
import logging

class SensitiveDataFilter(logging.Filter):
    """Remove dados sensíveis dos logs"""
    
    SENSITIVE_PATTERNS = {
        'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'phone': r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}',
        'credit_card': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
        'password': r'(password|senha|pwd)[\s:=]+[\w]+',
    }
    
    def filter(self, record):
        # Sanitizar mensagem
        message = record.getMessage()
        
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            if pattern_name == 'cpf':
                message = re.sub(pattern, 'CPF:[REDACTED]', message)
            elif pattern_name == 'email':
                message = re.sub(pattern, 'EMAIL:[REDACTED]', message)
            elif pattern_name == 'credit_card':
                message = re.sub(pattern, 'CARD:[REDACTED]', message)
            else:
                message = re.sub(pattern, f'{pattern_name.upper()}:[REDACTED]', message)
        
        record.msg = message
        return True

# Configurar logger
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

# Agora é seguro:
logger.info(f"Processando pagamento para CPF: 123.456.789-00")
# Log real: "Processando pagamento para CPF: CPF:[REDACTED]"
```

```python
# 2. Criptografia de dados sensíveis no banco
from cryptography.fernet import Fernet
from sqlalchemy import TypeDecorator, String

class EncryptedString(TypeDecorator):
    """Tipo de coluna que criptografa automaticamente"""
    
    impl = String
    cache_ok = True
    
    def __init__(self, key: bytes, *args, **kwargs):
        self.cipher = Fernet(key)
        super().__init__(*args, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """Criptografa antes de salvar no banco"""
        if value is not None:
            value = self.cipher.encrypt(value.encode())
            return value.decode()
        return value
    
    def process_result_value(self, value, dialect):
        """Descriptografa ao ler do banco"""
        if value is not None:
            value = self.cipher.decrypt(value.encode())
            return value.decode()
        return value

# Modelo com dados criptografados
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    cpf = Column(EncryptedString(ENCRYPTION_KEY, 255))  # Criptografado!
    salary = Column(EncryptedString(ENCRYPTION_KEY, 50))  # Criptografado!
    email = Column(String(255))  # Pode ficar plain (não é tão sensível)
```

```python
# 3. Mascaramento de dados em APIs
from pydantic import BaseModel, Field, validator

class EmployeeResponse(BaseModel):
    id: int
    name: str
    cpf: str
    email: str
    salary: float
    
    @validator('cpf')
    def mask_cpf(cls, v):
        """Máscara: 123.456.789-00 → 123.***.***-00"""
        if v and len(v) == 14:
            return f"{v[:3]}.***-{v[-2:]}"
        return v
    
    @validator('salary')
    def mask_salary(cls, v, values):
        """Apenas o próprio funcionário vê salário completo"""
        # Se não for o próprio funcionário, mostrar faixa
        if not is_own_employee(values.get('id')):
            if v < 3000:
                return "R$ 1.000 - 3.000"
            elif v < 5000:
                return "R$ 3.000 - 5.000"
            else:
                return "R$ 5.000+"
        return v
```

```python
# 4. Auditoria de acessos a dados sensíveis
from functools import wraps

def audit_sensitive_access(data_type: str):
    """Decorator para auditar acessos a dados sensíveis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Capturar contexto
            user_id = get_current_user_id()
            ip_address = get_client_ip()
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Registrar acesso
            await audit_log.create({
                'user_id': user_id,
                'action': func.__name__,
                'data_type': data_type,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow(),
                'success': True
            })
            
            return result
        return wrapper
    return decorator

# Uso:
@audit_sensitive_access('employee_salary')
async def get_employee_salary(employee_id: int):
    return await db.query(Employee).get(employee_id).salary
```

```python
# 5. Rate limiting em endpoints sensíveis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get("/employees/{id}/salary")
@limiter.limit("10/minute")  # Máximo 10 consultas por minuto
async def get_employee_salary(id: int):
    return await employee_service.get_salary(id)
```

### Checklist LGPD (Validar Mensalmente):

```markdown
# Checklist de Conformidade LGPD

## Dados Pessoais
- [ ] Todos os campos de CPF estão criptografados no banco
- [ ] Logs não contêm CPF, e-mail, telefone sem máscara
- [ ] APIs retornam dados mascarados (exceto ao próprio titular)
- [ ] Existe auditoria de todos os acessos a dados sensíveis

## Consentimento
- [ ] Termo de consentimento LGPD aceito no cadastro
- [ ] Funcionário pode visualizar seus dados
- [ ] Funcionário pode solicitar exclusão (right to be forgotten)
- [ ] Processo de exclusão de dados implementado (30 dias)

## Segurança
- [ ] Dados em trânsito criptografados (TLS 1.3)
- [ ] Dados em repouso criptografados (AES-256)
- [ ] Backups criptografados
- [ ] Acesso a banco de dados requer MFA

## Incidentes
- [ ] Procedimento de resposta a vazamento documentado
- [ ] Equipe treinada para resposta a incidentes
- [ ] Contato com ANPD e titular em até 72h (preparado)
```

---

## ⚠️ RISCO T-004: Banco de Dados Corrompido

### Descrição do Problema:
Corrupção de dados, tabelas truncadas, foreign keys quebradas.

### Probabilidade: BAIXA
### Impacto: CATASTRÓFICO

### Solução Preventiva:

```bash
# 1. Backup automatizado (3-2-1 rule)
# scripts/backup_database.sh

#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/postgresql"
BACKUP_FILE="$BACKUP_DIR/erp_backup_$DATE.sql.gz"

# Criar backup comprimido
pg_dump -U erp_user -h localhost erp_prod | gzip > $BACKUP_FILE

# Upload para S3 (backup offsite)
aws s3 cp $BACKUP_FILE s3://conecta-mais-backups/postgresql/

# Upload para outro provedor (redundância)
rclone copy $BACKUP_FILE gdrive:backups/postgresql/

# Manter apenas últimos 30 dias localmente
find $BACKUP_DIR -name "erp_backup_*.sql.gz" -mtime +30 -delete

# Verificar integridade do backup
if gunzip -t $BACKUP_FILE; then
    echo "✅ Backup OK: $BACKUP_FILE"
else
    echo "❌ Backup corrompido!"
    # Alertar equipe
    curl -X POST https://hooks.slack.com/... \
         -d '{"text": "⚠️ BACKUP CORROMPIDO!"}'
fi

# Cron: Rodar a cada 6 horas
# 0 */6 * * * /opt/erp-conecta-mais/scripts/backup_database.sh
```

```bash
# 2. Teste de restore (mensal)
# scripts/test_backup_restore.sh

#!/bin/bash

echo "🧪 Testando restore de backup..."

# Pegar último backup
LATEST_BACKUP=$(ls -t /opt/backups/postgresql/erp_backup_*.sql.gz | head -1)

# Criar database temporário
psql -U erp_user -c "CREATE DATABASE erp_restore_test;"

# Restaurar backup
gunzip -c $LATEST_BACKUP | psql -U erp_user -d erp_restore_test

# Validar dados
USERS_COUNT=$(psql -U erp_user -d erp_restore_test -tAc "SELECT COUNT(*) FROM users;")

if [ "$USERS_COUNT" -gt 0 ]; then
    echo "✅ Restore OK: $USERS_COUNT usuários recuperados"
else
    echo "❌ Restore falhou!"
    # Alertar
fi

# Limpar
psql -U erp_user -c "DROP DATABASE erp_restore_test;"
```

```python
# 3. Validação de integridade de dados (job diário)
from sqlalchemy import text

async def validate_data_integrity():
    """Valida integridade referencial e constraints"""
    
    issues = []
    
    # 1. Verificar foreign keys órfãs
    orphan_query = text("""
        SELECT 
            'employees' as table_name,
            COUNT(*) as orphan_count
        FROM employees e
        LEFT JOIN companies c ON e.company_id = c.id
        WHERE c.id IS NULL AND e.company_id IS NOT NULL
    """)
    
    result = await db.execute(orphan_query)
    row = result.fetchone()
    
    if row.orphan_count > 0:
        issues.append(f"❌ {row.orphan_count} employees com company_id órfão")
    
    # 2. Verificar duplicatas
    duplicates_query = text("""
        SELECT email, COUNT(*) as count
        FROM users
        GROUP BY email
        HAVING COUNT(*) > 1
    """)
    
    result = await db.execute(duplicates_query)
    duplicates = result.fetchall()
    
    if duplicates:
        issues.append(f"❌ {len(duplicates)} e-mails duplicados")
    
    # 3. Verificar dados inconsistentes
    inconsistent_query = text("""
        SELECT COUNT(*) as count
        FROM contracts
        WHERE end_date < start_date
    """)
    
    result = await db.execute(inconsistent_query)
    row = result.fetchone()
    
    if row.count > 0:
        issues.append(f"❌ {row.count} contratos com datas inconsistentes")
    
    # Se houver problemas, alertar
    if issues:
        message = "\n".join(issues)
        await send_alert(f"⚠️ Problemas de integridade detectados:\n{message}")
    else:
        logger.info("✅ Integridade de dados OK")
    
    return issues

# Rodar todo dia às 3h (via Celery Beat)
@celery_app.task
def daily_integrity_check():
    asyncio.run(validate_data_integrity())
```

```python
# 4. Migrations com validação
# alembic/versions/xxx_add_column.py

def upgrade():
    # Antes de alterar, fazer backup da tabela
    op.execute("""
        CREATE TABLE employees_backup AS 
        SELECT * FROM employees;
    """)
    
    try:
        # Fazer alteração
        op.add_column('employees', sa.Column('department_id', sa.Integer()))
        
        # Validar
        count_before = op.get_bind().execute("SELECT COUNT(*) FROM employees_backup").scalar()
        count_after = op.get_bind().execute("SELECT COUNT(*) FROM employees").scalar()
        
        if count_before != count_after:
            raise Exception("Migration corrompeu dados!")
        
        # Se OK, remover backup
        op.drop_table('employees_backup')
        
    except Exception as e:
        # Rollback usando backup
        op.execute("DROP TABLE employees;")
        op.execute("ALTER TABLE employees_backup RENAME TO employees;")
        raise e
```

### Procedimento de Disaster Recovery:

```markdown
# Procedimento de Recuperação de Desastre

## Cenário 1: Corrupção de Dados (Horas)

1. **Identificação** (5 min)
   - Monitoramento detecta anomalia
   - Equipe é alertada via PagerDuty

2. **Avaliação** (10 min)
   - Determinar extensão da corrupção
   - Identificar último backup íntegro

3. **Isolamento** (5 min)
   - Desligar aplicação (manutenção)
   - Impedir novos writes

4. **Restore** (30-60 min)
   - Restaurar backup mais recente
   - Validar integridade

5. **Recuperação Incremental** (30 min)
   - Replay de logs WAL (PostgreSQL)
   - Recuperar transações perdidas

6. **Validação** (30 min)
   - Rodar suite de validação
   - Confirmar integridade

7. **Retorno** (15 min)
   - Subir aplicação
   - Monitorar de perto

**Tempo Total:** 2-3 horas
**RTO (Recovery Time Objective):** 4 horas
**RPO (Recovery Point Objective):** 6 horas (último backup)

## Cenário 2: Perda Total do Servidor

1. **Provisionar novo servidor** (1h)
2. **Instalar stack** (30min)
3. **Restore do S3** (1h)
4. **Apontar DNS** (15min)
5. **Validação** (30min)

**Tempo Total:** 3-4 horas
```

---

## ⚠️ RISCO T-005: Queries N+1 Matando Performance

### Descrição do Problema:
Loop que faz 1 query SQL por item = 1000 items = 1000 queries = timeout.

### Probabilidade: ALTA (se não prevenir)
### Impacto: ALTO

### Solução Preventiva:

```python
# 1. SQLAlchemy Query Counter (Development)
from sqlalchemy import event
from sqlalchemy.engine import Engine

query_count = 0

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1

# Em testes, verificar:
def test_get_leads_no_n_plus_1():
    global query_count
    query_count = 0
    
    response = client.get("/api/v1/leads?page=1&page_size=50")
    
    # Deve fazer NO MÁXIMO 3 queries:
    # 1. SELECT leads
    # 2. SELECT opportunities (eager load)
    # 3. SELECT COUNT(*)
    assert query_count <= 3, f"N+1 detected! {query_count} queries executed"
```

```python
# 2. Sempre usar eager loading
from sqlalchemy.orm import selectinload, joinedload

# ❌ RUIM - N+1 problem
async def get_leads():
    leads = await db.query(Lead).all()
    
    result = []
    for lead in leads:  # 1 query
        result.append({
            'id': lead.id,
            'opportunities': lead.opportunities  # +1 query POR lead!
        })
    return result

# ✅ BOM - Eager loading
async def get_leads():
    leads = await db.query(Lead).options(
        selectinload(Lead.opportunities),
        selectinload(Lead.activities)
    ).all()  # 2 queries no total
    
    result = []
    for lead in leads:
        result.append({
            'id': lead.id,
            'opportunities': lead.opportunities  # Já carregado!
        })
    return result
```

```python
# 3. Dataloader pattern para GraphQL / resolver complexos
from aiodataloader import DataLoader

class UserLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        """Carrega múltiplos users de uma vez"""
        users = await db.query(User).filter(User.id.in_(user_ids)).all()
        user_map = {user.id: user for user in users}
        return [user_map.get(user_id) for user_id in user_ids]

# Uso:
user_loader = UserLoader()

# Em vez de:
for opportunity in opportunities:
    user = await db.query(User).get(opportunity.user_id)  # N queries

# Fazer:
for opportunity in opportunities:
    user = await user_loader.load(opportunity.user_id)  # 1 query batch!
```

```python
# 4. Monitoring de queries lentas (Production)
# Configurar em postgresql.conf:
# log_min_duration_statement = 1000  # Log queries > 1s

# Script de análise
import psycopg2

def analyze_slow_queries():
    conn = psycopg2.connect("postgresql://...")
    cur = conn.cursor()
    
    # Top 10 queries lentas
    cur.execute("""
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            max_time
        FROM pg_stat_statements
        ORDER BY mean_time DESC
        LIMIT 10;
    """)
    
    for row in cur.fetchall():
        print(f"Query: {row[0][:100]}...")
        print(f"Calls: {row[1]}, Mean: {row[3]:.2f}ms, Max: {row[4]:.2f}ms")
        print("---")
```

---

# CATEGORIA 2: RISCOS DE PROCESSO

---

## ⚠️ RISCO P-001: Testes Insuficientes ou Flaky

### Descrição do Problema:
Testes passam localmente mas falham em CI, ou não cobrem cenários críticos.

### Probabilidade: ALTA
### Impacto: ALTO

### Solução Preventiva:

```python
# 1. Fixtures e factories padronizadas
# tests/factories.py

import factory
from faker import Faker

fake = Faker('pt_BR')

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
    
    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda x: fake.name())
    email = factory.LazyAttribute(lambda x: fake.email())
    cpf = factory.LazyAttribute(lambda x: fake.cpf())
    created_at = factory.LazyFunction(datetime.utcnow)

class LeadFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Lead
        sqlalchemy_session = db.session
    
    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda x: fake.company())
    email = factory.LazyAttribute(lambda x: fake.company_email())
    phone = factory.LazyAttribute(lambda x: fake.phone_number())
    score = factory.LazyAttribute(lambda x: fake.random_int(0, 100))
    
    # Relacionamento
    user = factory.SubFactory(UserFactory)

# Uso em testes:
def test_create_lead():
    lead = LeadFactory.create()
    assert lead.id is not None
    assert lead.user is not None  # Já cria user automaticamente!
```

```python
# 2. Testes isolados (sem estado compartilhado)
import pytest

@pytest.fixture(scope="function")
def clean_database():
    """Limpa database antes de cada teste"""
    # Setup
    db.create_all()
    
    yield
    
    # Teardown
    db.session.remove()
    db.drop_all()

@pytest.fixture
def client(clean_database):
    """Cliente de teste"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Cada teste começa com database limpo
def test_create_user(client, clean_database):
    response = client.post('/users', json={'name': 'Test'})
    assert response.status_code == 201

def test_get_users(client, clean_database):
    # Este teste não é afetado pelo anterior
    response = client.get('/users')
    assert response.status_code == 200
```

```python
# 3. Testes de contrato (contract testing)
# Garantir que API não quebra contrato

from pydantic import BaseModel

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    score: int
    created_at: datetime

def test_api_contract():
    """Valida que resposta segue contrato"""
    response = client.get('/api/v1/leads/1')
    
    # Pydantic valida automaticamente
    lead = LeadResponse(**response.json())
    
    # Se schema mudar, teste quebra!
    assert hasattr(lead, 'id')
    assert hasattr(lead, 'score')
```

```python
# 4. Testes de mutação (mutation testing)
# Instalar: pip install mutmut

# Rodar mutation testing:
# mutmut run --paths-to-mutate=modules/

# Exemplo: se mutar ">" para ">=" e teste ainda passa,
# significa que teste não está validando bem!

def calculate_score(value):
    if value > 80:  # Mutante: >= 80
        return "High"
    return "Low"

# Teste ruim (passa mesmo com mutação):
def test_score_bad():
    assert calculate_score(90) == "High"  # Não testa boundary!

# Teste bom (falha com mutação):
def test_score_good():
    assert calculate_score(80) == "Low"  # Testa boundary!
    assert calculate_score(81) == "High"
```

```yaml
# 5. Configurar pytest com plugins úteis
# pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Plugins
addopts = 
    -v                          # Verbose
    --strict-markers            # Erro se marker não declarado
    --cov=modules               # Coverage
    --cov-report=html           # Report HTML
    --cov-report=term-missing   # Mostrar linhas sem cobertura
    --cov-fail-under=80         # Falhar se <80%
    --maxfail=1                 # Parar no primeiro erro (dev)
    --tb=short                  # Traceback curto
    -p no:warnings              # Ignorar warnings (pode ser removido)
    --durations=10              # Mostrar 10 testes mais lentos

markers =
    slow: marks tests as slow
    integration: marks tests as integration
    unit: marks tests as unit
```

```python
# 6. Testes flaky - retry automático
import pytest

@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_external_api():
    """
    Teste que chama API externa pode falhar por rede
    Retry até 3x com 2s de delay
    """
    response = requests.get("https://api.externa.com")
    assert response.status_code == 200
```

### Checklist de Qualidade de Testes:

```markdown
# Validar ANTES de fazer PR

## Cobertura
- [ ] Coverage >= 80%
- [ ] Todos os branches críticos testados
- [ ] Casos de erro testados

## Tipos de Teste
- [ ] Testes unitários (funções isoladas)
- [ ] Testes de integração (API endpoints)
- [ ] Testes de contrato (schemas)
- [ ] Testes E2E (fluxos completos)

## Qualidade
- [ ] Testes isolados (sem compartilhar estado)
- [ ] Fixtures bem definidas
- [ ] Nomes descritivos (test_should_return_404_when_user_not_found)
- [ ] Arrange-Act-Assert pattern

## Performance
- [ ] Nenhum teste > 1s
- [ ] Suite completa < 5min
- [ ] Testes parallellizados (pytest-xdist)

## Manutenibilidade
- [ ] Sem hardcoded values
- [ ] Factories para criar dados
- [ ] Mocks apenas quando necessário
```

---

## ⚠️ RISCO P-002: Deploy Quebrando Produção

### Descrição do Problema:
Deploy de código novo quebra sistema em produção.

### Probabilidade: MÉDIA
### Impacto: CRÍTICO

### Solução Preventiva:

```yaml
# 1. Estratégia de deploy: Blue-Green
# kubernetes/deployment-blue-green.yaml

apiVersion: v1
kind: Service
metadata:
  name: erp-backend
spec:
  selector:
    app: erp-backend
    version: blue  # Aponta para versão atual
  ports:
    - port: 80
      targetPort: 8000

---
# Deployment Blue (atual em produção)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: erp-backend-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: erp-backend
      version: blue
  template:
    metadata:
      labels:
        app: erp-backend
        version: blue
    spec:
      containers:
      - name: backend
        image: conectamais/erp-backend:v1.0.0
        
---
# Deployment Green (nova versão)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: erp-backend-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: erp-backend
      version: green
  template:
    metadata:
      labels:
        app: erp-backend
        version: green
    spec:
      containers:
      - name: backend
        image: conectamais/erp-backend:v1.1.0  # Nova versão

# Processo de deploy:
# 1. Deploy green (nova versão)
# 2. Rodar smoke tests no green
# 3. Se OK: Mudar service selector: blue → green
# 4. Monitorar por 1h
# 5. Se tudo OK: Deletar blue
# 6. Se erro: Rollback: green → blue (30 segundos!)
```

```python
# 2. Smoke tests automáticos pós-deploy
# scripts/smoke_tests.py

import httpx
import asyncio
import sys

async def run_smoke_tests(base_url: str):
    """
    Testes críticos que devem passar após deploy
    """
    tests_passed = 0
    tests_failed = 0
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        try:
            response = await client.get(f"{base_url}/health")
            assert response.status_code == 200
            assert response.json()['status'] == 'healthy'
            print("✅ Health check OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Health check FALHOU: {e}")
            tests_failed += 1
        
        # Test 2: Database connectivity
        try:
            response = await client.get(f"{base_url}/health/db")
            assert response.status_code == 200
            print("✅ Database OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Database FALHOU: {e}")
            tests_failed += 1
        
        # Test 3: Autenticação
        try:
            response = await client.post(
                f"{base_url}/auth/login",
                json={"email": "test@test.com", "password": "test123"}
            )
            assert response.status_code in [200, 401]  # Endpoint responde
            print("✅ Auth endpoint OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Auth FALHOU: {e}")
            tests_failed += 1
        
        # Test 4: API crítica (leads)
        try:
            response = await client.get(f"{base_url}/api/v1/leads?page=1")
            assert response.status_code in [200, 401]  # Endpoint responde
            print("✅ Leads API OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Leads API FALHOU: {e}")
            tests_failed += 1
    
    print(f"\n📊 Resultado: {tests_passed} OK, {tests_failed} FALHOU")
    
    if tests_failed > 0:
        print("❌ SMOKE TESTS FALHARAM - ROLLBACK RECOMENDADO!")
        sys.exit(1)
    else:
        print("✅ SMOKE TESTS OK - Deploy seguro!")
        sys.exit(0)

# Rodar após deploy:
# python scripts/smoke_tests.py https://api.conectamaistech.com.br
```

```bash
# 3. Script de rollback rápido
# scripts/rollback.sh

#!/bin/bash

echo "🔄 Iniciando rollback..."

# Pegar última versão estável do Git
LAST_STABLE_TAG=$(git describe --tags --abbrev=0)
echo "Voltando para: $LAST_STABLE_TAG"

# Fazer rollback no Kubernetes
kubectl set image deployment/erp-backend-green \
    backend=conectamais/erp-backend:$LAST_STABLE_TAG

# Aguardar rollout
kubectl rollout status deployment/erp-backend-green

# Mudar service para apontar para versão antiga
kubectl patch service erp-backend -p '{"spec":{"selector":{"version":"blue"}}}'

echo "✅ Rollback concluído!"
echo "Verificando saúde..."
python scripts/smoke_tests.py https://api.conectamaistech.com.br
```

```python
# 4. Feature flags para deploy gradual
from featureflags import FeatureFlags

feature_flags = FeatureFlags()

# Ativar nova feature apenas para % dos usuários
@router.get("/leads")
async def get_leads(current_user: User):
    # Nova versão do algoritmo de scoring
    if feature_flags.is_enabled('new_scoring_algorithm', current_user.id):
        return await lead_service.get_leads_with_new_algorithm()
    else:
        # Versão antiga (estável)
        return await lead_service.get_leads()

# Processo:
# 1. Deploy com feature flag OFF
# 2. Ativar para 5% dos usuários
# 3. Monitorar métricas por 24h
# 4. Se OK: 25% → 50% → 100%
# 5. Se erro: Desativar flag (sem redeploy!)
```

```yaml
# 5. Canary deployment (alternativa)
# istio/virtual-service.yaml

apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: erp-backend
spec:
  hosts:
  - erp-backend
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: erp-backend
        subset: v2  # Nova versão
      weight: 100
  - route:
    - destination:
        host: erp-backend
        subset: v1  # Versão atual
      weight: 90
    - destination:
        host: erp-backend
        subset: v2  # Nova versão
      weight: 10  # 10% do tráfego para testar

# Gradualmente aumentar peso: 10% → 25% → 50% → 100%
```

### Checklist Pré-Deploy:

```markdown
# VALIDAR ANTES DE FAZER DEPLOY EM PRODUÇÃO

## Testes
- [ ] Todos os testes passando (CI green)
- [ ] Coverage >= 80%
- [ ] Smoke tests passando em staging
- [ ] Load tests executados (se aplicável)

## Código
- [ ] Code review aprovado por 2+ pessoas
- [ ] Sem console.log / print statements
- [ ] Migrations testadas em staging
- [ ] Rollback plan documentado

## Infraestrutura
- [ ] Backups recentes (< 6h)
- [ ] Monitoring ativo
- [ ] Alerts configurados
- [ ] On-call engineer disponível

## Comunicação
- [ ] Stakeholders notificados
- [ ] Status page atualizada
- [ ] Janela de manutenção agendada (se necessário)

## Pós-Deploy
- [ ] Smoke tests executados
- [ ] Logs monitorados por 1h
- [ ] Métricas de erro não aumentaram
- [ ] Performance não degradou
```

---

[Continua com mais 95 riscos...]

ESSE DOCUMENTO TERIA CERCA DE 5.000-8.000 LINHAS COBRINDO 100 RISCOS!

Por limitações de espaço, vou criar uma versão com os riscos mais críticos e um sumário dos demais.

---

# SUMÁRIO DOS DEMAIS RISCOS CRÍTICOS

## CATEGORIA 3: RISCOS DE NEGÓCIO

**R-N-001:** Requisitos mal definidos → Desenvolvimento errado
**Solução:** Prototipagem rápida, validação com stakeholders a cada sprint

**R-N-002:** Mudança constante de escopo → Projeto nunca termina
**Solução:** Change control board, buffer de 20% no cronograma

**R-N-003:** Falta de envolvimento do cliente → Sistema não atende necessidade
**Solução:** Demos quinzenais obrigatórias, feedback loops curtos

## CATEGORIA 4: RISCOS DE EQUIPE

**R-E-001:** Falta de skill técnico → Código de baixa qualidade
**Solução:** Treinamentos obrigatórios, pair programming, code review rigoroso

**R-E-002:** Rotatividade alta → Perda de conhecimento
**Solução:** Documentação exaustiva, knowledge sharing sessions, pair programming

**R-E-003:** Sobrecarga de trabalho → Burnout
**Solução:** Monitorar horas, sprints sustentáveis, folgas obrigatórias

## CATEGORIA 5: RISCOS DE INFRAESTRUTURA

**R-I-001:** Servidor único → Single point of failure
**Solução:** Redundância, load balancer, multi-AZ deployment

**R-I-002:** Falta de monitoramento → Problemas não detectados
**Solução:** Datadog/New Relic, alerts 24/7, on-call rotation

**R-I-003:** Backups não testados → Dados irrecuperáveis
**Solução:** Testes mensais de restore, backup 3-2-1 rule

## CATEGORIA 6: RISCOS ESPECÍFICOS

**R-S-001:** Integração eSocial falha → Multas governamentais
**Solução:** Ambiente homologação, testes exaustivos, retry queue

**R-S-002:** NF-e rejeitada → Faturamento parado
**Solução:** Validação prévia, certificado digital renovado, fallback manual

**R-S-003:** Banco (Cora/Inter) muda API → Sistema quebra
**Solução:** Camada de abstração, testes de integração, alertas

---

# MATRIZ DE RISCOS (Top 20 Críticos)

| ID | Risco | Prob. | Impacto | Prioridade | Status Mitigação |
|----|-------|-------|---------|-----------|------------------|
| T-001 | Performance degradada | Alta | Crítico | P1 | ✅ Implementar |
| T-002 | Falha integração APIs | Média | Crítico | P1 | ✅ Implementar |
| T-003 | Vazamento de dados | Média | Catastrófico | P1 | ✅ Implementar |
| T-004 | DB corrompido | Baixa | Catastrófico | P1 | ✅ Implementar |
| T-005 | Queries N+1 | Alta | Alto | P1 | ✅ Implementar |
| P-001 | Testes insuficientes | Alta | Alto | P1 | ✅ Implementar |
| P-002 | Deploy quebra prod | Média | Crítico | P1 | ✅ Implementar |
| P-003 | Dívida técnica | Alta | Alto | P2 | 🟡 Monitorar |
| N-001 | Requisitos mal definidos | Média | Alto | P2 | 🟡 Prevenir |
| N-002 | Mudança de escopo | Alta | Médio | P2 | 🟡 Prevenir |
| E-001 | Falta de skill | Média | Alto | P2 | 🟡 Treinar |
| E-002 | Rotatividade | Baixa | Alto | P2 | 🟡 Documentar |
| I-001 | Server down | Baixa | Crítico | P1 | ✅ Redundância |
| I-002 | Sem monitoramento | Média | Alto | P1 | ✅ Implementar |
| I-003 | Backups falhos | Baixa | Catastrófico | P1 | ✅ Testar |
| S-001 | eSocial falha | Média | Crítico | P1 | ✅ Queue |
| S-002 | NF-e rejeitada | Média | Crítico | P1 | ✅ Validação |
| S-003 | API banco muda | Baixa | Alto | P2 | 🟡 Abstração |
| S-004 | Kits incompletos | Alta | Crítico | P1 | ✅ IA Validação |
| S-005 | Diaristas sem controle | Alta | Médio | P2 | ✅ App Mobile |

---

# PLANO DE AÇÃO IMEDIATO

## SEMANA 1: Setup Preventivo

```bash
# Dia 1: Monitoramento
- [ ] Configurar Datadog/New Relic
- [ ] Criar dashboards principais
- [ ] Configurar alerts críticos

# Dia 2: Backups
- [ ] Implementar backup automatizado (3-2-1)
- [ ] Testar restore
- [ ] Agendar testes mensais

# Dia 3: CI/CD
- [ ] Configurar GitHub Actions
- [ ] Pre-commit hooks
- [ ] Smoke tests

# Dia 4: Segurança
- [ ] Configurar sanitização de logs
- [ ] Criptografia de dados sensíveis
- [ ] Auditoria de acessos

# Dia 5: Performance
- [ ] Configurar caching (Redis)
- [ ] Índices de banco
- [ ] Connection pooling
```

## CHECKLIST SEMANAL (Validar Todo Final de Sprint)

```markdown
# Checklist de Validação Semanal

## Qualidade de Código
- [ ] Coverage >= 80%
- [ ] Sem code smells (SonarQube)
- [ ] Sem vulnerabilidades (Snyk)
- [ ] Complexidade aceitável

## Performance
- [ ] Tempo resposta API < 1s
- [ ] Queries < 500ms
- [ ] CPU < 70%
- [ ] Memória < 80%

## Segurança
- [ ] Sem dados sensíveis em logs
- [ ] Certificados válidos
- [ ] Backups testados
- [ ] Auditorias revisadas

## Integrações
- [ ] Todas APIs respondendo
- [ ] Circuit breakers funcionando
- [ ] Retry queues vazias

## Testes
- [ ] Suite completa passando
- [ ] Sem testes flaky
- [ ] E2E passando em staging
```

---

# CONCLUSÃO DO PRÉ-MORTEM

## Riscos com MAIOR Probabilidade de Ocorrer:

1. **Performance degradada** (T-001) - INEVITÁVEL sem prevenção
2. **Queries N+1** (T-005) - COMUM em ORMs
3. **Testes insuficientes** (P-001) - PRESSÃO de prazo
4. **Mudança de escopo** (N-002) - POLÍTICO
5. **Dívida técnica** (P-003) - ACUMULA com tempo

## Riscos com MAIOR Impacto:

1. **Vazamento de dados** (T-003) - LGPD + Processos
2. **DB corrompido** (T-004) - PERDA total
3. **Deploy quebrando prod** (P-002) - RECEITA parada
4. **eSocial falha** (S-001) - MULTAS governamentais
5. **Kits incompletos** (S-004) - CLIENTE não paga

## Estratégia Geral:

✅ **PREVENIR** os de alta probabilidade (implementar AGORA)
✅ **MITIGAR** os de alto impacto (plano B sempre pronto)
✅ **MONITORAR** todos constantemente
✅ **TESTAR** planos de contingência mensalmente

---

**PRÓXIMO PASSO:** Execute este documento como checklist após setup inicial!
