import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app, classify, Report

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]

def test_health():
    assert client.get('/health').json()['project'] == 'RouteRadar'

def test_every_scenario():
    cases = [json.loads(x) for x in (ROOT/'data'/'scenarios.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(cases) >= 100
    for case in cases:
        got = classify(Report(**case['input']))
        assert got['status'] == case['expected']['status'], case['test_id']
        assert got['block_route'] == case['expected']['block_route'], case['test_id']

def test_route_detour():
    graph={'A':['B','C'],'B':['D'],'C':['D'],'D':[]}
    r=client.post('/route/check',json={'graph':graph,'start':'A','end':'D','blocked_edges':[['A','B']]})
    assert r.json()['path']==['A','C','D']

def test_no_route():
    r=client.post('/route/check',json={'graph':{'A':['B'],'B':[]},'start':'A','end':'B','blocked_edges':[['A','B']]})
    assert r.json()['reachable'] is False

def test_multilingual_and_adversarial():
    cases = [json.loads(x) for x in (ROOT/'data'/'edge_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    for case in cases:
        got = classify(Report(**case['input']))
        assert got['status'] == case['expected']['status'], case['test_id']
        assert got['block_route'] == case['expected']['block_route'], case['test_id']
