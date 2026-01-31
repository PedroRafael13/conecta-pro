#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo HR completo.
Módulo HR: 6 submódulos, 25 controllers, maior módulo do sistema.
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Import all HR routers from submodules
from modules.hr.analytics_dashboard.controllers import (
    dashboard_controller,
    kpi_controller,
    report_controller
)
from modules.hr.employee_portal.controllers import (
    document_controller,
    notification_controller,
    payslip_controller,
    preferences_controller,
    vacation_controller
)
from modules.hr.mobile_time_clock.controllers import (
    checkin_controller,
    device_controller as mtc_device_controller,
    geofence_controller,
    offline_controller
)
from modules.hr.payroll_integration.controllers import (
    esocial_controller,
    payroll_event_controller,
    payroll_export_controller,
    payroll_period_controller
)
from modules.hr.rep_integration.controllers import (
    afd_controller,
    device_controller as rep_device_controller,
    event_controller,
    sync_controller,
    webhook_controller
)
from modules.hr.time_tracking.controllers import (
    justification_controller,
    overtime_controller,
    time_entry_controller,
    time_sheet_controller
)

def create_hr_app() -> FastAPI:
    """Cria app FastAPI com todos os routers do módulo HR."""
    app = FastAPI(
        title="Conecta Pro - HR Module API",
        description="API completa do módulo de Recursos Humanos (HR) - 25 controllers em 6 submódulos",
        version="1.0.0"
    )

    # Analytics Dashboard (3 controllers)
    app.include_router(
        dashboard_controller.router,
        prefix="/api/v1/hr/analytics/dashboard",
        tags=["HR Analytics - Dashboard"]
    )
    app.include_router(
        kpi_controller.router,
        prefix="/api/v1/hr/analytics/kpi",
        tags=["HR Analytics - KPI"]
    )
    app.include_router(
        report_controller.router,
        prefix="/api/v1/hr/analytics/reports",
        tags=["HR Analytics - Reports"]
    )

    # Employee Portal (5 controllers)
    app.include_router(
        document_controller.router,
        prefix="/api/v1/hr/portal/documents",
        tags=["HR Portal - Documents"]
    )
    app.include_router(
        notification_controller.router,
        prefix="/api/v1/hr/portal/notifications",
        tags=["HR Portal - Notifications"]
    )
    app.include_router(
        payslip_controller.router,
        prefix="/api/v1/hr/portal/payslips",
        tags=["HR Portal - Payslips"]
    )
    app.include_router(
        preferences_controller.router,
        prefix="/api/v1/hr/portal/preferences",
        tags=["HR Portal - Preferences"]
    )
    app.include_router(
        vacation_controller.router,
        prefix="/api/v1/hr/portal/vacation",
        tags=["HR Portal - Vacation"]
    )

    # Mobile Time Clock (4 controllers)
    app.include_router(
        checkin_controller.router,
        prefix="/api/v1/hr/mobile/checkin",
        tags=["HR Mobile - Check-in"]
    )
    app.include_router(
        mtc_device_controller.router,
        prefix="/api/v1/hr/mobile/devices",
        tags=["HR Mobile - Devices"]
    )
    app.include_router(
        geofence_controller.router,
        prefix="/api/v1/hr/mobile/geofence",
        tags=["HR Mobile - Geofence"]
    )
    app.include_router(
        offline_controller.router,
        prefix="/api/v1/hr/mobile/offline",
        tags=["HR Mobile - Offline"]
    )

    # Payroll Integration (4 controllers)
    app.include_router(
        esocial_controller.router,
        prefix="/api/v1/hr/payroll/esocial",
        tags=["HR Payroll - eSocial"]
    )
    app.include_router(
        payroll_event_controller.router,
        prefix="/api/v1/hr/payroll/events",
        tags=["HR Payroll - Events"]
    )
    app.include_router(
        payroll_export_controller.router,
        prefix="/api/v1/hr/payroll/export",
        tags=["HR Payroll - Export"]
    )
    app.include_router(
        payroll_period_controller.router,
        prefix="/api/v1/hr/payroll/periods",
        tags=["HR Payroll - Periods"]
    )

    # REP Integration (5 controllers)
    app.include_router(
        afd_controller.router,
        prefix="/api/v1/hr/rep/afd",
        tags=["HR REP - AFD"]
    )
    app.include_router(
        rep_device_controller.router,
        prefix="/api/v1/hr/rep/devices",
        tags=["HR REP - Devices"]
    )
    app.include_router(
        event_controller.router,
        prefix="/api/v1/hr/rep/events",
        tags=["HR REP - Events"]
    )
    app.include_router(
        sync_controller.router,
        prefix="/api/v1/hr/rep/sync",
        tags=["HR REP - Sync"]
    )
    app.include_router(
        webhook_controller.router,
        prefix="/api/v1/hr/rep/webhooks",
        tags=["HR REP - Webhooks"]
    )

    # Time Tracking (4 controllers)
    app.include_router(
        justification_controller.router,
        prefix="/api/v1/hr/timetracking/justifications",
        tags=["HR TimeTracking - Justifications"]
    )
    app.include_router(
        overtime_controller.router,
        prefix="/api/v1/hr/timetracking/overtime",
        tags=["HR TimeTracking - Overtime"]
    )
    app.include_router(
        time_entry_controller.router,
        prefix="/api/v1/hr/timetracking/entries",
        tags=["HR TimeTracking - Entries"]
    )
    app.include_router(
        time_sheet_controller.router,
        prefix="/api/v1/hr/timetracking/timesheets",
        tags=["HR TimeTracking - TimeSheets"]
    )

    return app

def extract_openapi():
    """Extrai OpenAPI spec e salva em arquivo."""
    print("🚀 Iniciando extração OpenAPI do módulo HR...")
    print("📊 Módulo HR: 6 submódulos, 25 controllers")
    print()

    app = create_hr_app()

    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Count endpoints
    total_endpoints = len(openapi_schema.get("paths", {}))
    total_schemas = len(openapi_schema.get("components", {}).get("schemas", {}))

    print(f"✅ OpenAPI gerado com sucesso!")
    print(f"📍 Total de endpoints: {total_endpoints}")
    print(f"📦 Total de schemas: {total_schemas}")
    print()

    # Save to file
    output_file = backend_path / "openapi_hr.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    file_size = output_file.stat().st_size
    file_size_kb = file_size / 1024

    print(f"💾 Arquivo salvo: {output_file}")
    print(f"📏 Tamanho: {file_size_kb:.1f} KB ({file_size:,} bytes)")
    print()

    # Stats por submódulo
    print("📊 Estatísticas por submódulo:")
    tags = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "patch", "delete"]:
                for tag in details.get("tags", []):
                    tags[tag] = tags.get(tag, 0) + 1

    for tag in sorted(tags.keys()):
        print(f"   • {tag}: {tags[tag]} endpoints")

    print()
    print("✅ Extração concluída!")

if __name__ == "__main__":
    try:
        extract_openapi()
    except Exception as e:
        print(f"❌ Erro durante extração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
