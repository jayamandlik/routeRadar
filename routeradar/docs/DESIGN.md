# RouteRadar Global Design

## Interfaces

Source adapters (official / transit / social / public) -> normalization -> AI extraction -> provenance and deduplication -> verification -> geocoding and map matching -> deterministic routing -> API / notifications.

## Global requirements

- Per-city configuration: IANA timezone, languages, local authority sources, road rules, coordinate reference, available travel modes, accessibility and licensing.
- Global city fixtures must not imply universal live data coverage.
- Route engine must respect directed edges, closures by mode, effective intervals, accessibility, and disconnected networks.
- Geospatial data must be validated before restricting any network segment.
- Separate unit tests, integration tests with real routing graphs, and live provider contract tests.
- All timestamps must be offset-aware and event ordering based on event time plus source revision.
- Maintain source provenance, privacy protections, rate limits, cache freshness, and failure-mode disclosures.

## Test coverage

50 cities x 8 synthetic incidents = 400 incident cases, plus graph route tests. Scenarios exercise multilingual content and expected conservative verification behavior. These are deterministic reference tests, not proof of model quality or comprehensive global coverage.
