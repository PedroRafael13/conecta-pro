import re

# Ler o arquivo
with open('/opt/conecta-pro/backend/modules/scheduler/services/intelligent_scheduler_service.py.bak', 'r') as f:
    content = f.read()

# Padrão para encontrar e substituir a seção problemática
old_pattern = '''                if "forbidden_hours" in conditions:
                    forbidden_start, forbidden_end = conditions["forbidden_hours"]
                    event_start_hour = start_time.hour + start_time.minute / 60
                    event_end_hour = end_time.hour + end_time.minute / 60
                    
                    # Verifica overlap com horário proibido
                    if not (event_end_hour <= forbidden_start or event_start_hour >= forbidden_end):'''

new_pattern = '''                if "forbidden_hours" in conditions:
                    forbidden_period = conditions["forbidden_hours"]
                    # Converter tuplas (hora, minuto) para float
                    forbidden_start = forbidden_period[0][0] + forbidden_period[0][1] / 60
                    forbidden_end = forbidden_period[1][0] + forbidden_period[1][1] / 60
                    event_start_hour = start_time.hour + start_time.minute / 60
                    event_end_hour = end_time.hour + end_time.minute / 60
                    
                    # Verifica overlap com horário proibido
                    if not (event_end_hour <= forbidden_start or event_start_hour >= forbidden_end):'''

# Substituir
content = content.replace(old_pattern, new_pattern)

# Escrever o arquivo corrigido
with open('/opt/conecta-pro/backend/modules/scheduler/services/intelligent_scheduler_service.py', 'w') as f:
    f.write(content)

print("Arquivo corrigido com sucesso!")
