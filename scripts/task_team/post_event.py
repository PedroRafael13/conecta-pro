#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/opt/conecta-pro/.comms/task-team/events.ndjson')

p = argparse.ArgumentParser()
p.add_argument('--agent', required=True)
p.add_argument('--model', required=True)
p.add_argument('--phase', type=int, required=True)
p.add_argument('--task-id', required=True)
p.add_argument('--action', required=True)
p.add_argument('--status', choices=['started', 'progress', 'blocked', 'done'], required=True)
p.add_argument('--on-plan', choices=['true', 'false'], required=True)
p.add_argument('--evidence', default='')
p.add_argument('--notes', default='')
a = p.parse_args()

obj = {
    'ts': datetime.now(timezone.utc).isoformat(),
    'agent': a.agent,
    'model': a.model,
    'phase': a.phase,
    'task_id': a.task_id,
    'action': a.action,
    'status': a.status,
    'on_plan': a.on_plan == 'true',
    'evidence': [x.strip() for x in a.evidence.split(',') if x.strip()],
    'notes': a.notes,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('a', encoding='utf-8') as f:
    f.write(json.dumps(obj, ensure_ascii=True) + '\n')

print('OK')
