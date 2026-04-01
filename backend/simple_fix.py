# Solução simples: Modificar apenas as constraints para usar formato correto

# Ler arquivo
with open("/opt/conecta-pro/backend/modules/scheduler/services/intelligent_scheduler_service.py.bak") as f:
    content = f.read()

# Mudar o formato de forbidden_hours de [(12, 0), (13, 30)] para [12.0, 13.5]
content = content.replace('"forbidden_hours": [(12, 0), (13, 30)]', '"forbidden_hours": [12.0, 13.5]')

# Salvar
with open("/opt/conecta-pro/backend/modules/scheduler/services/intelligent_scheduler_service.py", "w") as f:
    f.write(content)

print("Correção simples aplicada!")
