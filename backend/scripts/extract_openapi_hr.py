#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo HR
Gera hr.openapi.json com todos os 236 endpoints dos 6 submódulos
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Import HR routers
# Analytics Dashboard
from modules.hr.analytics_dashboard.controllers import (
    dashboard_router as analytics_dashboard_router,
    kpi_router as analytics_kpi_router,
    report_router as analytics_report_router,
)

# Employee Portal
from modules.hr.employee_portal.controllers import (
    router as employee_portal_router,
)

# Mobile Time Clock
from modules.hr.mobile_time_clock.controllers import (
    device_router as mobile_device_router,
    checkin_router as mobile_checkin_router,
    geofence_router as mobile_geofence_router,
    offline_router as mobile_offline_router,
)

# Payroll Integration
from modules.hr.payroll_integration.controllers import (
    router as payroll_router,
)

# REP Integration
from modules.hr.rep_integration.controllers import (
    router as rep_router,
)

# Time Tracking
from modules.hr.time_tracking.controllers import (
    router as time_tracking_router,
)


def extract_hr_openapi():
    """Extrai OpenAPI spec completo do módulo HR."""

    # Create temporary FastAPI app
    app = FastAPI(
        title="Conecta PRO - HR API",
        description="API completa do módulo HR - Recursos Humanos (6 submódulos: Analytics Dashboard, Employee Portal, Mobile Time Clock, Payroll Integration, REP Integration, Time Tracking)",
        version="2.0.0",
    )

    # Include all HR routers with proper prefixes
    routers = [
        # Analytics Dashboard
        (analytics_dashboard_router, "/api/v1/hr/analytics/dashboards", ["HR Analytics - Dashboards"]),
        (analytics_kpi_router, "/api/v1/hr/analytics/kpis", ["HR Analytics - KPIs"]),
        (analytics_report_router, "/api/v1/hr/analytics/reports", ["HR Analytics - Reports"]),

        # Employee Portal
        (employee_portal_router, "/api/v1/hr/portal", ["HR Portal - Employee Portal"]),

        # Mobile Time Clock
        (mobile_device_router, "/api/v1/hr/mobile/devices", ["HR Mobile - Devices"]),
        (mobile_checkin_router, "/api/v1/hr/mobile/checkins", ["HR Mobile - Check-ins"]),
        (mobile_geofence_router, "/api/v1/hr/mobile/geofences", ["HR Mobile - Geofencing"]),
        (mobile_offline_router, "/api/v1/hr/mobile/offline", ["HR Mobile - Offline Sync"]),

        # Payroll Integration
        (payroll_router, "/api/v1/hr/payroll", ["HR Payroll - Integration"]),

        # REP Integration
        (rep_router, "/api/v1/hr/rep", ["HR REP - Integration"]),

        # Time Tracking
        (time_tracking_router, "/api/v1/hr/time-tracking", ["HR Time Tracking"]),
    ]

    for router, prefix, tags in routers:
        app.include_router(router, prefix=prefix, tags=tags)

    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add servers
    openapi_schema["servers"] = [
        {"url": "https://api.conectapro.com.br", "description": "Produção"},
        {"url": "https://staging-api.conectapro.com.br", "description": "Staging"},
        {"url": "http://localhost:8000", "description": "Desenvolvimento"},
    ]

    # Count endpoints
    total_endpoints = sum(len(methods) for methods in openapi_schema.get("paths", {}).values())
    print(f"✅ OpenAPI spec HR gerado com sucesso!")
    print(f"📊 Total de paths: {len(openapi_schema.get('paths', {}))}")
    print(f"📊 Total de endpoints: {total_endpoints}")

    # Count by submódulo
    submods = {
        "Analytics Dashboard": 0,
        "Employee Portal": 0,
        "Mobile Time Clock": 0,
        "Payroll Integration": 0,
        "REP Integration": 0,
        "Time Tracking": 0,
    }

    for path in openapi_schema.get("paths", {}).keys():
        if "/analytics/" in path:
            submods["Analytics Dashboard"] += 1
        elif "/portal/" in path:
            submods["Employee Portal"] += 1
        elif "/mobile/" in path:
            submods["Mobile Time Clock"] += 1
        elif "/payroll/" in path:
            submods["Payroll Integration"] += 1
        elif "/rep/" in path:
            submods["REP Integration"] += 1
        elif "/time-tracking/" in path:
            submods["Time Tracking"] += 1

    print("\n📋 Distribuição por submódulo:")
    for submod, count in submods.items():
        print(f"   • {submod}: {count} paths")

    # Write to file
    output_file = Path(__file__).parent.parent / "hr.openapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Arquivo salvo: {output_file}")
    print(f"📦 Tamanho: {output_file.stat().st_size / 1024:.1f} KB")

    return openapi_schema


if __name__ == "__main__":
    try:
        extract_hr_openapi()
        print("\n✨ Extração concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao extrair OpenAPI spec: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
