---
title: Módulo Operacional
description: 14 controllers de gestão operacional para vigilância
controllers: 14
---

# Módulo Operacional

Gestão operacional de equipes, postos e atividades de vigilância.

## Controllers

```
PostosController          # Gestão de postos de vigilância
EscalasController         # Escalação de equipes
OrdensServicoController   # O.S. de atendimento
RondasController          # Rondas virtuais/físicas
OcorrenciasController     # Registro de ocorrências
EquipamentosController    # Controle de equipamentos
ClientesController        # Cadastro de clientes
ContratosController       # Gestão contratual
FuncionariosController    # Equipe de vigilância
VeiculosController        # Frota de viaturas
ArmamentosController      # Controle de armas
AlarmesController         # Central de alarmes
RelatoriosController      # Relatórios operacionais
DashboardController       # KPIs operacionais
```

## Estrutura Operacional

```
Cliente
  └── Contrato
        └── Posto(s)
              ├── Escala (funcionários)
              ├── Rondas (checkpoints)
              ├── Equipamentos
              └── Ocorrências
```

## Comandos

```bash
# Testes operacionais
pytest tests/operacional/ -v -k "escala or ronda"

# Seed de dados operacionais
python scripts/seed_operacional.py --env staging

# Relatório mensal
python scripts/relatorio_operacional.py --mes 2024-01
```

## Regras de Negócio

### Escalas
- Jornada máxima: 12h (Lei 13.467/2017)
- Intervalo mínimo: 1h para jornada > 6h
- Descanso semanal: 24h consecutivos

### Rondas
- QR Code / NFC / GPS para checkpoints
- Tolerância de tempo: ± 5 minutos
- Registro de desvios obrigatório

### Ocorrências
- Classificação: Crítica, Alta, Média, Baixa
- SLA de resposta: Crítica = 15 min
- Evidências fotográficas obrigatórias

## Checklist de Features

- [ ] Cálculo automático de escala
- [ ] Notificações de ronda perdida
- [ ] Geolocalização de postos
- [ ] QR Code/NFC para checkpoints
- [ ] Alertas de jornada excessiva
- [ ] Integração com app mobile
