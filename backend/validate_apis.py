#!/usr/bin/env python3
"""
Script para validar configurações das APIs externas.
"""
import os
import sys

def validate_whatsapp_config():
    """Valida configurações do WhatsApp."""
    print("🔍 Validando configurações WhatsApp...")
    
    configs = {
        'WHATSAPP_API_ENABLED': os.getenv('WHATSAPP_API_ENABLED', 'false'),
        'EVOLUTION_API_URL': os.getenv('EVOLUTION_API_URL', ''),
        'EVOLUTION_API_KEY': os.getenv('EVOLUTION_API_KEY', ''),
        'WHATSAPP_INSTANCE_ID': os.getenv('WHATSAPP_INSTANCE_ID', ''),
    }
    
    for key, value in configs.items():
        status = "✅" if value and value != 'your_evolution_api_key_here' else "❌"
        print(f"  {status} {key}: {value[:20]}{'...' if len(value) > 20 else ''}" if value else f"  {status} {key}: <vazio>")
    
    return all(configs.values()) and configs['EVOLUTION_API_KEY'] != 'your_evolution_api_key_here'

def validate_google_maps_config():
    """Valida configurações do Google Maps."""
    print("\n🗺️  Validando configurações Google Maps...")
    
    configs = {
        'GOOGLE_MAPS_API_KEY': os.getenv('GOOGLE_MAPS_API_KEY', ''),
        'GOOGLE_MAPS_ENABLED': os.getenv('GOOGLE_MAPS_ENABLED', 'false'),
        'MAPS_DEFAULT_CENTER_LAT': os.getenv('MAPS_DEFAULT_CENTER_LAT', ''),
        'MAPS_DEFAULT_CENTER_LNG': os.getenv('MAPS_DEFAULT_CENTER_LNG', ''),
    }
    
    for key, value in configs.items():
        status = "✅" if value and value != 'your_google_maps_api_key_here' else "❌"
        print(f"  {status} {key}: {value}")
    
    return all(configs.values()) and configs['GOOGLE_MAPS_API_KEY'] != 'your_google_maps_api_key_here'

def main():
    print("🔧 VALIDAÇÃO DE APIS EXTERNAS - CONECTA PRO")
    print("=" * 50)
    
    whatsapp_ok = validate_whatsapp_config()
    maps_ok = validate_google_maps_config()
    
    print("\n📊 RESUMO:")
    print(f"  WhatsApp: {'✅ Configurado' if whatsapp_ok else '❌ Pendente (chaves precisam ser atualizadas)'})")
    print(f"  Google Maps: {'✅ Configurado' if maps_ok else '❌ Pendente (chaves precisam ser atualizadas)'})")
    
    if whatsapp_ok and maps_ok:
        print("\n🎉 Todas as APIs estão configuradas!")
        sys.exit(0)
    else:
        print("\n⚠️  Para ativar as APIs, substitua 'your_*_api_key_here' pelas chaves reais.")
        sys.exit(1)

if __name__ == '__main__':
    main()
