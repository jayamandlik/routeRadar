# RouteRadar

**Global urban disruption intelligence — synthetic reference implementation**

RouteRadar accepts reports from official and public sources, classifies whether a restriction may be applied, and demonstrates alternate paths on a toy directed graph. The bundled global dataset is **entirely synthetic** and is not a real-time map or safe-navigation product.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

```bash
curl http://127.0.0.1:8000/cities
curl http://127.0.0.1:8000/scenarios?city=London
pytest -q
```

POST `/analyze` with an `input` object from `data/scenarios.jsonl`. `POST /route/check` accepts a synthetic directed graph, start, end, and blocked edges.

## Data

- `data/cities.json`: 50 major cities, coordinates and IANA timezone identifiers.
- `data/scenarios.jsonl`: 8 scenarios per city, including official verified closures, unverified rumors, planned closures, expired closures, conflicting public reports, missing timezone, transit notices, and multilingual posts.
- `data/test_matrix.csv`: spreadsheet-friendly test cases with expected results.

## Design constraints

- An official report only blocks a graph edge when verified, geometry-validated, active, and explicitly describing a closure.
- Social reports never automatically close a road.
- City names and coordinates in the dataset are reference fixtures, not precise closure geometry.
- The route endpoint uses a **toy graph**, not OpenStreetMap, MTA, or live routing. Do not use for navigation.
- Production requires city-specific authoritative feeds, licenses, geocoding, map matching, real routing, data freshness, accessibility support, authentication, observability, and human review.

See `docs/AGENT_PROMPT.md` and `docs/DESIGN.md`.

- `data/edge_cases.jsonl`: 6 additional multilingual and adversarial cases.
