#!/usr/bin/env python3
"""Diagnóstico rápido do backend Conecta PRO"""
import requests
from datetime import datetime
import json

def run_diagnostic():
    print("🔍 CONECTA PRO - DIAGNOSTIC TEST")
    print("=" * 40)
    print(f"Timestamp: {datetime.now()}")
    print(f"Servidor: MacBook-Air-de-Jordan.local")

    server = "localhost:8080"

    try:
        # Teste básico
        response = requests.get(f"http://{server}/", timeout=3)
        print(f"✅ Root endpoint: {response.status_code}")

        # Health check
        response = requests.get(f"http://{server}/health", timeout=3)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data}")
        else:
            print(f"⚠️ Health check: {response.status_code}")

        print("\n✅ Backend funcionando!")

    except Exception as e:
        print(f"❌ Erro: {e}")
        print("⚠️ Verifique se o backend está rodando na porta 8080")

if __name__ == "__main__":
    run_diagnostic()
