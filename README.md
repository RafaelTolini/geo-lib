# reservoir_data

`reservoir_data` is an object-oriented Python library for discovering and
loading reservoir simulation data as domain objects.

Current implementation status is tracked in:

- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/SPEC_TRACEABILITY.md`
- `docs/STATUS.md`

The first milestone implements project scaffolding, typed discovery contracts,
case file detection, case manifests, and the public `SimulationCase.open(...)`
entry point. Payload readers are intentionally not claimed as supported yet.
