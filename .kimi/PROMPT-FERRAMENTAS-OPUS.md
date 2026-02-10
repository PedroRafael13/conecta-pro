# PROMPT EXECUÇÃO — Ferramentas de Produtividade para Kimi K2.5

**Objetivo:** Criar 6 scripts de automação que eliminem falsos positivos e tornem o Kimi 100% assertivo.

**Contexto:** Kimi tem cometido erros recorrentes:
1. Usa enums em inglês quando o código usa português (ACTIVE→ATIVO)
2. Cria objetos nos testes sem campos obrigatórios
3. Não verifica impacto cruzado antes de renomear
4. Não detecta regressões imediatamente
5. Reports sem comandos exatos

---

## FERRAMENTA 1: pre-flight.sh (PRIORIDADE MÁXIMA)

**Propósito:** Antes de modificar QUALQUER arquivo, verificar impacto cruzado automaticamente.

**Local:** `/opt/conecta-pro/scripts/pre-flight.sh`

**Uso:**
```bash
./scripts/pre-flight.sh modules/mobile/models/push_notification.py
```

**Comportamento:**
1. Recebe path do arquivo como argumento
2. Extrai nome da classe (ex: MobilePushNotification)
3. Executa:
   ```bash
   grep -r "MobilePushNotification" /opt/conecta-pro/backend/ --include="*.py" -l
   ```
4. Lista todos os arquivos que serão afetados
5. Pergunta: "Confirma modificação? Isso afeta N arquivos. [s/N]"
6. Só permite continuar com 's'

**Output exemplo:**
```
═══════════════════════════════════════════
PRE-FLIGHT CHECK: MobilePushNotification
═══════════════════════════════════════════

Arquivos que serão AFETADOS (3):
  1. modules/mobile/models/__init__.py
  2. modules/mobile/services/push_notification_service.py
  3. tests/modules/mobile/test_notification_service.py

⚠️  AÇÃO: Renomear classe afeta todas as importações acima.

Confirma modificação? [s/N]: 
```

**Critério de sucesso:**
- [ ] Script executa sem erros
- [ ] Detecta corretamente todas as referências
- [ ] Mostra lista numerada de arquivos afetados
- [ ] Pede confirmação antes de continuar
- [ ] Retorna exit code 0 (confirmou) ou 1 (cancelou)

---

## FERRAMENTA 2: validate-enums.py (PRIORIDADE MÁXIMA)

**Propósito:** Detectar automaticamente todos os enums usados incorretamente nos testes (EN vs PT).

**Local:** `/opt/conecta-pro/scripts/validate-enums.py`

**Comportamento:**
1. Varre todos os arquivos em `tests/` que usam enums
2. Para cada enum encontrado, verifica se o valor existe no model
3. Lista apenas ERROS (uso de valor que não existe)

**Lógica:**
```python
# 1. Descobrir todos os enums definidos em modules/
# 2. Para cada teste que usa Enum.VALOR:
#    - Verificar se VALOR existe na definição do enum
#    - Se não existe → reportar erro
```

**Output exemplo:**
```
═══════════════════════════════════════════
VALIDAÇÃO DE ENUMS — 12 erros encontrados
═══════════════════════════════════════════

❌ tests/test_config_model.py:555
   Enum: TenantStatus.ACTIVE
   Erro: 'ACTIVE' não existe. Use: 'ATIVO'

❌ tests/test_config_model.py:170  
   Enum: SettingCategory.NOTIFICATIONS
   Erro: 'NOTIFICATIONS' não existe. Use: 'NOTIFICACAO'

❌ tests/test_config_service.py:82
   Enum: FlagStatus.INACTIVE
   Erro: 'INACTIVE' não existe. Use: 'INATIVO'

═══════════════════════════════════════════
CORREÇÃO AUTOMÁTICA disponível:
./scripts/validate-enums.py --fix
═══════════════════════════════════════════
```

**Modo --fix:**
- Substitui automaticamente todos os valores incorretos pelos corretos
- Cria commit com as alterações

**Critério de sucesso:**
- [ ] Detecta TenantStatus.ACTIVE → deveria ser ATIVO
- [ ] Detecta SettingCategory.NOTIFICATIONS → deveria ser NOTIFICACAO
- [ ] Detecta FlagStatus.INACTIVE → deveria ser INATIVO
- [ ] Modo --fix funciona e cria commit

---

## FERRAMENTA 3: required-fields.py (PRIORIDADE ALTA)

**Propósito:** Mostrar campos obrigatórios de qualquer model Pydantic/SQLAlchemy.

**Local:** `/opt/conecta-pro/scripts/required-fields.py`

**Uso:**
```bash
./scripts/required-fields.py modules/config/models/tenant.py Tenant
./scripts/required-fields.py modules/config/models/tenant.py TenantSettings
```

**Comportamento:**
1. Parseia o arquivo do model
2. Identifica:
   - Campos com `nullable=False` (SQLAlchemy) = obrigatório
   - Campos sem `default` e sem `Optional` (Pydantic) = obrigatório
   - Campos com `default` ou `nullable=True` = opcional

**Output exemplo:**
```
═══════════════════════════════════════════
Tenant — Campos Obrigatórios
═══════════════════════════════════════════

OBRIGATÓRIOS (3):
  nome          str                    não tem default
  slug          str                    não tem default
  status        TenantStatus           default: ATIVO

OPCIONAIS (8):
  documento     str | None             nullable=True
  logo_url      str | None             nullable=True
  endereco      str | None             nullable=True
  ...

═══════════════════════════════════════════
Uso correto no teste:
  Tenant(nome="Test", slug="test", status=TenantStatus.ATIVO)
═══════════════════════════════════════════
```

**Critério de sucesso:**
- [ ] Parseia SQLAlchemy models corretamente
- [ ] Detecta nullable=False como obrigatório
- [ ] Mostra default quando existe
- [ ] Mostra exemplo de uso correto

---

## FERRAMENTA 4: safe-edit.sh (PRIORIDADE ALTA)

**Propósito:** Wrapper que verifica regressão após CADA modificação.

**Local:** `/opt/conecta-pro/scripts/safe-edit.sh`

**Uso:**
```bash
# Ao invés de editar diretamente:
sed -i 's/OLD/NEW/g' arquivo.py

# Usar:
./scripts/safe-edit.sh "sed -i 's/OLD/NEW/g' arquivo.py"
```

**Comportamento:**
1. Roda verify-all.sh ANTES → salva baseline
2. Executa o comando de edição
3. Roda verify-all.sh DEPOIS → compara
4. Se piorou qualquer métrica:
   - Reverte automaticamente: `git checkout -- arquivo.py`
   - Mostra diff do que piorou
   - Pergunta: "Revertido. Quer investigar antes de tentar novamente?"
   - Exit code 1
5. Se melhorou ou manteve:
   - Exit code 0

**Output exemplo (regressão):**
```
═══════════════════════════════════════════
SAFE-EDIT: modules/teste.py
═══════════════════════════════════════════

[ANTES] Collection: 6288 testes
[ANTES] Passed: 5315

Executando: sed -i 's/MobilePushNotification/MobileNotificationLog/g' ...

[DEPOIS] Collection: 6288 testes
[DEPOIS] Passed: 5290 ⚠️ -25

❌ REGRESSÃO DETECTADA: -25 testes passando
🔄 REVERTENDO alteração...
✅ Arquivo restaurado

Investigue antes de tentar novamente.
Use: ./scripts/pre-flight.sh arquivo.py
```

**Critério de sucesso:**
- [ ] Detecta regressão imediatamente
- [ ] Reverte automaticamente
- [ ] Mostra delta claro (ANTES vs DEPOIS)
- [ ] Não permite commitar com regressão

---

## FERRAMENTA 5: verify-instant.sh (PRIORIDADE MÉDIA)

**Propósito:** Verificação REALMENTE rápida (~8s) para checks durante desenvolvimento.

**Local:** `/opt/conecta-pro/scripts/verify-instant.sh`

**Diferença do verify-quick.sh atual:**
- verify-quick.sh: 90s+ (ainda roda pytest amostra)
- verify-instant.sh: ~8s (só collection, não roda testes)

**O que verifica:**
1. Ruff linting (~2s)
2. Pytest COLLECTION apenas (~5s) — verifica se não quebrou imports
3. Alembic heads (~1s)

**O que NÃO verifica:**
- Pytest RUN (demora)
- Bandit (demora)
- TypeScript/ESLint (frontend separado)

**Output:**
```
═══════════════════════════════════════════
VERIFY-INSTANT (~8s)
═══════════════════════════════════════════

✓ Ruff: 0 erros (2.1s)
✓ Collection: 6288 testes, 0 erros (5.3s)
✓ Alembic: 1 head (0.8s)

═══════════════════════════════════════════
Total: 8.2s
═══════════════════════════════════════════
```

**Uso ideal:**
- A cada modificação de código
- Antes de commitar quick fixes
- Verificação rápida durante desenvolvimento

**Critério de sucesso:**
- [ ] Completa em < 10s
- [ ] Detecta collection errors
- [ ] Detecta ruff errors
- [ ] Mostra tempo de cada etapa

---

## FERRAMENTA 6: schema-validator.py (PRIORIDADE MÉDIA)

**Propósito:** Comparar Pydantic schemas vs uso real nos testes.

**Local:** `/opt/conecta-pro/scripts/schema-validator.py`

**Uso:**
```bash
./scripts/schema-validator.py --model TenantCreate
./scripts/schema-validator.py --all  # Valida todos os schemas
```

**Comportamento:**
1. Parseia o Pydantic model
2. Lista campos obrigatórios
3. Busca nos testes onde o model é instanciado
4. Verifica se todos os campos obrigatórios estão sendo passados

**Output exemplo:**
```
═══════════════════════════════════════════
Schema Validator: TenantCreate
═══════════════════════════════════════════

Campos obrigatórios (4):
  ✓ nome      presente em todos os testes
  ✓ slug      presente em todos os testes
  ⚠️ status    FALTANDO em:
      - tests/test_config_model.py:60
      - tests/test_config_model.py:103

═══════════════════════════════════════════
CORREÇÃO SUGERIDA:
  TenantCreate(nome="X", slug="y", status=TenantStatus.ATIVO)
═══════════════════════════════════════════
```

**Critério de sucesso:**
- [ ] Parseia Pydantic BaseModel corretamente
- [ ] Detecta campos obrigatórios (sem default)
- [ ] Encontra uso nos testes
- [ ] Reporta onde faltam campos obrigatórios

---

## ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

### Fase 1 (Impacto Imediato)
1. `verify-instant.sh` — Mais simples, resolve timeout
2. `required-fields.py` — Resolve TypeError nos testes

### Fase 2 (Prevenção de Erros)
3. `validate-enums.py` — Resolve EN vs PT
4. `pre-flight.sh` — Previne impacto cruzado

### Fase 3 (Segurança)
5. `safe-edit.sh` — Previne regressões
6. `schema-validator.py` — Validação completa

---

## CHECKLIST DE ENTREGA

Para cada ferramenta, verificar:
- [ ] Script executável (`chmod +x`)
- [ ] Local correto (`/opt/conecta-pro/scripts/`)
- [ ] Testado com exemplo real do projeto
- [ ] Documentado com `--help`
- [ ] Atualiza ENVIRONMENT.md com novo comando

---

## ATUALIZAÇÕES NO ENVIRONMENT.md

Adicionar seção:
```markdown
### Novas Ferramentas de Produtividade

```bash
# Verificação instantânea (~8s)
verify-instant          # alias para ./scripts/verify-instant.sh

# Pre-flight antes de editar
pre-flight arquivo.py   # verifica impacto cruzado

# Validar enums
validate-enums          # lista erros EN vs PT
validate-enums --fix    # corrige automaticamente

# Campos obrigatórios
required-fields.py modules/x/models/y.py ModelName

# Edição segura
safe-edit.sh "comando de edição"  # reverte se piorar
```
```

---

## MENSAGEM PARA KIMI

Após implementar, adicionar a `/opt/conecta-pro/.kimi/ERROS-PASSADOS.md`:

```markdown
## Erro 13: Não usar as novas ferramentas

**Regra:** ANTES de qualquer modificação:
1. Rodar: `pre-flight arquivo.py`
2. Durante: `safe-edit.sh "comando"`
3. Depois: `verify-instant` (rápido) ou `verify-all.sh` (completo)

**Se encontrar enum errado:**
- Rodar: `validate-enums --fix`

**Se TypeError em teste:**
- Rodar: `required-fields.py caminho/do/model.py NomeModel`
```

---

## MÉTRICA DE SUCESSO FINAL

Após implementar todas as ferramentas:
- Kimi deve conseguir fazer Tarefa 3 (Enums) sem erros
- Kimi deve detectar regressão antes de reportar conclusão
- Tempo de verificação: 8s (instant) vs 90s+ (atual)
- Falsos positivos: 0 (com uso obrigatório das ferramentas)

---

**Quando terminar:**
1. Atualizar `/opt/conecta-pro/.kimi/ENVIRONMENT.md` com todos os comandos
2. Criar mensagem em `/opt/conecta-pro/.comms/messages/claude-out.jsonl` avisando Kimi
3. Kimi vai testar cada ferramenta antes de usar em produção
