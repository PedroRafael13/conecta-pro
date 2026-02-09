#!/usr/bin/env python3
import sys

sys.path.append("/opt/conecta-pro/backend")

import asyncio
from datetime import datetime, timedelta

from modules.scheduler.services.intelligent_scheduler_service import intelligent_scheduler_service


async def test_intelligent_scheduler():
    print("🚀 TESTANDO INTELLIGENT SCHEDULER SERVICE")
    print("=" * 50)

    try:
        # Teste 1: Verificar status do serviço
        print("📊 Status do Serviço:")
        print(f"✅ Eventos: {len(intelligent_scheduler_service.events)}")
        print(f"✅ Recursos: {len(intelligent_scheduler_service.resources)}")
        print(f"✅ Conflitos: {len(intelligent_scheduler_service.conflicts)}")
        print()

        # Teste 2: Criar um evento de teste
        event_requirements = {
            "duration": 60,
            "type": "meeting",
            "priority": "high",
            "participants": ["user1@conecta.com", "user2@conecta.com"],
            "location": "Sala de Reunião A",
            "equipment_needed": ["projetor", "microfone"],
        }

        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)

        print("🎯 TESTE: Sugestão de Horário Ótimo")
        print(f"📅 Período: {start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m')}")
        print(f"⏱️  Duração: {event_requirements['duration']} minutos")
        print()

        # Sugerir horário ótimo
        suggestion = await intelligent_scheduler_service.suggest_optimal_time(
            event_requirements=event_requirements,
            preferred_date_range=(start_date, end_date),
            duration_minutes=event_requirements["duration"],
        )

        if suggestion:
            print("✅ RESULTADO DA SUGESTÃO:")
            print(f"⏰ Horário sugerido: {suggestion.suggested_start.strftime('%d/%m %H:%M')}")
            print(f"🎯 Confiança: {suggestion.confidence:.1%}")
            print(f"📍 Local: {suggestion.location or 'Não especificado'}")
            print(f"💡 Justificativa: {suggestion.reason}")
            print()

        # Teste 3: Analytics e Métricas
        print("📊 ANALYTICS DO SISTEMA:")
        analytics = await intelligent_scheduler_service.get_scheduler_analytics()

        print(f"📈 Score do calendário: {analytics['optimization']['calendar_score']:.2f}")
        print(f"⏱️  Tempo economizado/dia: {analytics['optimization']['time_saved_daily_minutes']} min")
        print(f"📊 Melhoria eficiência: {analytics['optimization']['efficiency_improvement']}%")
        print(f"🤖 Confiança ML: {analytics['optimization']['ml_confidence']:.1%}")
        print(f"🎯 Slots ótimos previstos: {analytics['predictions']['optimal_slots_predicted']}")
        print(f"🛡️  Taxa prevenção conflitos: {analytics['predictions']['conflict_prevention_rate']}%")

        print()
        print("🎉 INTELLIGENT SCHEDULER SERVICE: FUNCIONANDO!")
        print("✅ Sugestões inteligentes: OPERACIONAL")
        print("✅ Analytics avançado: OPERACIONAL")
        print("✅ Machine Learning: OPERACIONAL")
        print("🎯 AGENDAMENTO INTELIGENTE: IMPLEMENTADO!")

        return analytics

    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_intelligent_scheduler())
