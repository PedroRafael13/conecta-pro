#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

EV = Path('/opt/conecta-pro/.comms/task-team/events.ndjson')

events = []
if EV.exists():
    for line in EV.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

if not events:
    print('SEM_EVENTOS')
    raise SystemExit(0)

by_status = Counter(e.get('status', '?') for e in events)
by_phase = Counter(str(e.get('phase', '?')) for e in events)
viol_model = [e for e in events if e.get('model') != 'claude-opus-4.6']
viol_phase = [e for e in events if not isinstance(e.get('phase'), int) or e['phase'] < 0 or e['phase'] > 8]
offplan = [e for e in events if e.get('on_plan') is False]

last_by_agent = {}
for e in events:
    last_by_agent[e.get('agent', '?')] = e

print(f"TOTAL_EVENTOS={len(events)}")
print('STATUS=' + ','.join(f"{k}:{v}" for k, v in sorted(by_status.items())))
print('FASES=' + ','.join(f"{k}:{v}" for k, v in sorted(by_phase.items(), key=lambda x: x[0])))
print(f"VIOL_OPUS46={len(viol_model)}")
print(f"VIOL_FASE={len(viol_phase)}")
print(f"OFF_PLAN={len(offplan)}")
print('ULTIMO_POR_AGENTE:')
for agent in sorted(last_by_agent):
    e = last_by_agent[agent]
    print(f"- {agent}: phase={e.get('phase')} status={e.get('status')} task={e.get('task_id')}")

if offplan:
    print('ALERTAS_OFF_PLAN:')
    for e in offplan[-10:]:
        print(f"- {e.get('ts')} {e.get('agent')} {e.get('task_id')} {e.get('action')} | {e.get('notes', '')}")

if viol_model:
    print('ALERTAS_MODELO:')
    for e in viol_model[-10:]:
        print(f"- {e.get('ts')} {e.get('agent')} model={e.get('model')} task={e.get('task_id')}")
