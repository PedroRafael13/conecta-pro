# Patch específico para o método _calculate_constraint_penalty

with open("/opt/conecta-pro/backend/modules/scheduler/services/intelligent_scheduler_service.py") as f:
    lines = f.readlines()

# Encontrar e substituir apenas a linha problemática
for i, line in enumerate(lines):
    if 'forbidden_start, forbidden_end = conditions["forbidden_hours"]' in line:
        # Substituir a linha problemática com o código correto
        lines[i] = '                    forbidden_period = conditions["forbidden_hours"]\n'
        # Inserir as linhas de conversão
        lines.insert(i + 1, "                    # Converter tuplas (hora, minuto) para float\n")
        lines.insert(
            i + 2, "                    forbidden_start = forbidden_period[0][0] + forbidden_period[0][1] / 60\n"
        )
        lines.insert(
            i + 3, "                    forbidden_end = forbidden_period[1][0] + forbidden_period[1][1] / 60\n"
        )
        break

# Salvar
with open("/opt/conecta-pro/backend/modules/scheduler/services/intelligent_scheduler_service.py", "w") as f:
    f.writelines(lines)

print("Método patcheado com sucesso!")
