#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

EV = Path('/opt/conecta-pro/.comms/task-team/events.ndjson')
MSG = Path('/opt/conecta-pro/.comms/task-team/to_chief.md')

required_agents = {
    'Program-Manager', 'Security-Lead', 'Backend-Lead', 'Frontend-Lead',
    'Data-Lead', 'SRE-Lead', 'QA-Lead', 'Release-Lead', 'Audit-Lead'
}

events = []
if EV.exists():
    for line in EV.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue

print('=== CHIEF REVIEW ===')
if not events:
    print('status: NO_ACTIVITY')
    raise SystemExit(0)

by_agent = defaultdict(list)
for e in events:
    by_agent[e.get('agent', '?')].append(e)

viol_model = [e for e in events if e.get('model') != 'claude-opus-4.6']
off_plan = [e for e in events if e.get('on_plan') is False]
missing_agents = sorted(required_agents - set(by_agent.keys()))
status_count = Counter(e.get('status', '?') for e in events)
phase_count = Counter(str(e.get('phase', '?')) for e in events)

print(f"events_total: {len(events)}")
print('status_count: ' + ', '.join(f"{k}={v}" for k,v in sorted(status_count.items())))
print('phase_count: ' + ', '.join(f"{k}={v}" for k,v in sorted(phase_count.items(), key=lambda x: x[0])))
print(f"viol_model: {len(viol_model)}")
print(f"off_plan: {len(off_plan)}")
print(f"agents_reporting: {len(by_agent)}")

has_progress = any(e.get('status') in {'progress', 'done', 'blocked'} for e in events)
last_ts = None
for e in events:
    ts = e.get('ts')
    if not ts:
        continue
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except ValueError:
        continue
    if last_ts is None or dt > last_ts:
        last_ts = dt

stalled = False
if not has_progress and status_count.get('started', 0) >= 3 and last_ts is not None:
    age_min = (datetime.now(timezone.utc) - last_ts).total_seconds() / 60
    if age_min >= 5:
        stalled = True
        print(f"stalled_minutes_since_last_event: {age_min:.1f}")

if missing_agents:
    print('missing_agents: ' + ', '.join(missing_agents))
else:
    print('missing_agents: none')

print('latest_by_agent:')
for agent in sorted(by_agent.keys()):
    e = by_agent[agent][-1]
    print(f"- {agent}: phase={e.get('phase')} status={e.get('status')} task={e.get('task_id')} action={e.get('action')}")

if off_plan:
    print('off_plan_last10:')
    for e in off_plan[-10:]:
        print(f"- {e.get('ts')} {e.get('agent')} task={e.get('task_id')} notes={e.get('notes','')}")

if viol_model:
    print('viol_model_last10:')
    for e in viol_model[-10:]:
        print(f"- {e.get('ts')} {e.get('agent')} model={e.get('model')} task={e.get('task_id')}")

msg_lines = MSG.read_text(encoding='utf-8').splitlines() if MSG.exists() else []
updates = sum(1 for ln in msg_lines if ln.strip().startswith('Tipo: UPDATE'))
blockers = sum(1 for ln in msg_lines if ln.strip().startswith('Tipo: BLOCKER'))
decisions = sum(1 for ln in msg_lines if ln.strip().startswith('Tipo: DECISION_REQUEST'))
deliveries = sum(1 for ln in msg_lines if ln.strip().startswith('Tipo: DELIVERY'))
print(f"msg_updates={updates} msg_blockers={blockers} msg_decisions={decisions} msg_deliveries={deliveries}")

verdict = 'OK'
reasons = []
if viol_model:
    verdict = 'REJECT'
    reasons.append('modelo fora de claude-opus-4.6')
if missing_agents:
    verdict = 'WARN' if verdict == 'OK' else verdict
    reasons.append('nem todos os agentes reportaram')
if off_plan:
    verdict = 'WARN' if verdict == 'OK' else verdict
    reasons.append('ha atividades fora do plano')
if stalled:
    verdict = 'WARN' if verdict == 'OK' else verdict
    reasons.append('time parado sem eventos de progresso')

print('verdict: ' + verdict)
if reasons:
    print('reasons: ' + ' | '.join(reasons))
if stalled:
    print('alert: TEAM_STALLED_WITHOUT_PROGRESS')
