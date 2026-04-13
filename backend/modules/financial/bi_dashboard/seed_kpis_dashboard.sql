-- Seed: BI Dashboard + KPIs iniciais Conecta Mais
-- Executado manualmente em 2026-04-13 (fix auditoria)
-- Corrige nomes dos KPIs conforme especificação original

UPDATE financial_kpis SET nome = 'Saldo Inter', descricao = 'Saldo conta Inter'
WHERE codigo = 'KPI-002';

UPDATE financial_kpis SET nome = 'Inadimplência', descricao = 'Taxa inadimplência',
    formula = 'overdue_rate', unidade = '%', valor_atual = 0
WHERE codigo = 'KPI-004';
