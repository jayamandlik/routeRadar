"""RouteRadar: synthetic global incident intelligence reference API."""
from datetime import datetime, timezone
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title='RouteRadar', version='1.0.0', description='Synthetic demonstration; not live navigation')

class Report(BaseModel):
    id: str
    city: str
    source_type: str
    text: str
    event_time: str
    expires_at: str | None = None
    verified: bool = False
    geometry_validated: bool = False
    affected_modes: list[str] = Field(default_factory=lambda: ['driving'])
    synthetic: bool = True

def classify(r: Report, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    if not r.synthetic:
        return {'id': r.id, 'status': 'UNSUPPORTED_LIVE', 'action': 'REQUIRE_LIVE_ADAPTER', 'block_route': False}
    try:
        when = datetime.fromisoformat(r.event_time.replace('Z', '+00:00'))
        until = datetime.fromisoformat(r.expires_at.replace('Z', '+00:00')) if r.expires_at else None
        if when.tzinfo is None or (until is not None and until.tzinfo is None):
            raise ValueError('Timezone offset required')
    except ValueError:
        return {'id': r.id, 'status': 'INVALID', 'action': 'REVIEW', 'block_route': False}
    if until and until <= now:
        return {'id': r.id, 'status': 'EXPIRED', 'action': 'IGNORE', 'block_route': False}
    if when > now:
        return {'id': r.id, 'status': 'SCHEDULED', 'action': 'DISPLAY_PLANNED', 'block_route': False}
    official = r.source_type.upper() in {'OFFICIAL', 'TRANSPORT_AUTHORITY'}
    confirmed = official and r.verified
    status = 'CONFIRMED' if confirmed else 'UNVERIFIED'
    block = confirmed and r.geometry_validated and any(w in r.text.lower() for w in ('closed', 'closure', 'blocked', 'cerrada', 'fermé', 'gesperrt', '通行止め', 'बंद'))
    return {'id': r.id, 'status': status, 'action': 'APPLY_RESTRICTION' if block else 'DISPLAY_ONLY', 'block_route': block}

@app.get('/health')
def health():
    return {'status': 'ok', 'project': 'RouteRadar', 'mode': 'synthetic'}

@app.post('/analyze')
def analyze(report: Report):
    return classify(report)

@app.get('/cities')
def cities():
    p = ROOT / 'data' / 'cities.json'
    return json.loads(p.read_text(encoding='utf-8'))

@app.get('/scenarios')
def scenarios(city: str | None = None):
    records = [json.loads(line) for line in (ROOT/'data'/'scenarios.jsonl').read_text(encoding='utf-8').splitlines() if line]
    return [x for x in records if city is None or x['city'] == city]

@app.post('/route/check')
def route_check(payload: dict):
    """Toy graph route check, not real-world street routing."""
    graph = payload.get('graph', {})
    start, end = payload.get('start'), payload.get('end')
    blocked = {tuple(x) for x in payload.get('blocked_edges', [])}
    if not start or not end or start not in graph or end not in graph:
        raise HTTPException(422, 'start/end must exist in graph')
    from collections import deque
    queue = deque([(start, [start])]); seen = {start}
    while queue:
        node, path = queue.popleft()
        if node == end:
            return {'path': path, 'reachable': True, 'synthetic_graph': True}
        for neighbor in graph.get(node, []):
            if (node, neighbor) not in blocked and neighbor not in seen:
                seen.add(neighbor); queue.append((neighbor, path + [neighbor]))
    return {'path': [], 'reachable': False, 'synthetic_graph': True}
