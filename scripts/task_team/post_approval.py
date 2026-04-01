#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/opt/conecta-pro/.comms/task-team/approvals.ndjson')

p = argparse.ArgumentParser()
p.add_argument('--reviewer', required=True)
p.add_argument('--task-id', required=True)
p.add_argument('--decision', choices=['approved', 'rejected'], required=True)
p.add_argument('--reason', default='')
a = p.parse_args()

obj = {
    'ts': datetime.now(timezone.utc).isoformat(),
    'reviewer': a.reviewer,
    'task_id': a.task_id,
    'decision': a.decision,
    'reason': a.reason,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('a', encoding='utf-8') as f:
    f.write(json.dumps(obj, ensure_ascii=True) + '\n')

print('OK')
