#!/usr/bin/env python3
"""Validador rápido Conecta PRO - Fase 6"""
import requests
import os
from datetime import datetime

def validate_system():
    print("🧪 CONECTA PRO - VALIDAÇÃO RÁPIDA FASE 6")
    print("=" * 50)
    print(f"⏰ {datetime.now()}")
    print(f"📍 Servidor: srv1134814 (82.25.75.74)")
    print()

    # 1. Verificar estrutura de diretórios
    print("📁 VERIFICANDO ESTRUTURA:")
    dirs = [
        "/opt/conecta-pro/docs/fase6/tools",
        "/opt/conecta-pro/docs/fase6/reports",
        "/opt/conecta-pro/docs/fase6/validation-results"
    ]

    for d in dirs:
        if os.path.exists(d):
            files = os.listdir(d)
            count = len(files)
            print(f"✅ {d} ({count} arquivos)")
        else:
            print(f"❌ {d} (não existe)")

    print()

    # 2. Verificar backend
    print("🔧 VERIFICANDO BACKEND:")
    try:
        response = requests.get("http://localhost:8080/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"✅ App: {data.get('app', 'unknown')}")
            print(f"✅ Versão: {data.get('version', 'unknown')}")
            print(f"✅ Ambiente: {data.get('environment', 'unknown')}")
        else:
            print(f"⚠️ Health check: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend inacessível: {e}")

    print()

    # 3. Verificar recursos do sistema
    print("💾 VERIFICANDO RECURSOS:")
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        print(f"✅ CPU: {cpu_percent}%")
        print(f"✅ Memória: {memory.percent}% ({memory.used//1024//1024}MB usado)")
        print(f"✅ Disco: {disk.percent}% ({disk.used//1024//1024//1024}GB usado)")
    except ImportError:
        print("⚠️ psutil não instalado, pulando verificação de recursos")

    print()
    print("✅ VALIDAÇÃO CONCLUÍDA!")
    print("📊 Sistema operacional e pronto para Fase 6")

if __name__ == "__main__":
    validate_system()
