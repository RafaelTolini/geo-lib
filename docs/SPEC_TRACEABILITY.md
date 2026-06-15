# Specification Traceability

Statuses: `not_started`, `in_progress`, `implemented`, `partially_implemented`, `blocked`, `deferred`.

| Specification Area | Status | Implementation / Evidence | Notes |
| --- | --- | --- | --- |
| Project scaffold | implemented | `pyproject.toml`, `README.md`, `src/reservoir_data`, `tests` | Python 3.11+ package scaffold exists and imports under `PYTHONPATH=src`. |
| Package structure | partially_implemented | M1 layer packages under `public`, `application`, `domain`, `infrastructure`, `schemas`, `exceptions` | Only packages needed for M1 are present; future domain/format subpackages will be added with real behavior. |
| Exceptions | implemented | `src/reservoir_data/exceptions/errors.py`; tests in `tests/test_manifest_and_options.py` | Full specified exception taxonomy exists. |
| Schemas/value objects | partially_implemented | `LoadCaseOptions`, `FormatDetectionResult`, `FileCategory`, `FileFormat` | Remaining schemas such as grid, summary, restart, keyword, report-step, and export options are pending. |
| Public API/facade | partially_implemented | `SimulationCase.open()`, `available_data()`, `has_data()` | Heavy `load_*` methods intentionally raise explicit errors until parsers exist. |
| Case discovery | partially_implemented | `FileCatalog`, `CaseLoader`, `CaseManifest` | Basename/directory discovery works without payload loading; richer ambiguity policies and explicit manifest input are pending. |
| File type detection | partially_implemented | `FileDetector`; tests in `tests/test_file_detector.py` | Known extensions and conservative report-step suffixes are detected; exact formatted/non-unified conventions remain verification items. |
| GRDECL parser | not_started | Planned for M3 | Requires keyword domain and text I/O. |
| Keyword records/datasets | not_started | Planned for M3 | Required before text/formatted keyword parsing. |
| Grid domain model | not_started | Planned for M2/M4 | Indexing and active mapping first, geometry after GRDECL. |
| GRID/EGRID reader | not_started | Planned for M6 | Requires binary keyword infrastructure and grid domain. |
| INIT/property loading | not_started | Planned for M7 | Requires keyword and property models. |
| Active/global mapping | not_started | Planned for M2 | Dependency for grid properties, restart, wells, and RFT. |
| Binary record infrastructure | not_started | Planned for M5 | Needed before binary readers. |
| Formatted/unformatted keyword files | not_started | Planned for M3/M5 | M1 records inferred formatted flags only; no keyword parsing exists. |
| Unified/non-unified handling | partially_implemented | M1 detection metadata for unified files and non-unified report-step suffixes | Parsing/group semantics for restart and summary datasets remain pending. |
| Restart dataset/reports | not_started | Planned for M8 | Requires binary infrastructure and keyword datasets. |
| Summary dataset/vectors | not_started | Planned for M9 | Requires summary metadata/data readers. |
| RFT/PLT data | not_started | Planned for M10 | Requires RFT readers and grid/time context. |
| Well timelines/states/connections/segments | not_started | Planned for M10 | Requires restart extraction and grid indexes. |
| Lazy loading | partially_implemented | `SimulationCase.open()` and `FileCatalog` inspect names only | Real lazy providers for arrays/vectors/reports are pending. |
| NumPy integration | not_started | Planned for M2/M7/M9 | Optional boundary integration only. |
| pandas/CSV export | not_started | Planned for M9 | pandas optional and isolated. |
| Error handling | partially_implemented | Exception taxonomy plus discovery/load boundary errors | Parser/domain contextual errors will be added per milestone. |
| Large-file behavior | not_started | Planned for M8/M9/M11 | Requires real lazy payload readers. |
| Tests | partially_implemented | 19 stdlib unit tests for M1 behavior | Black-box parser and large-file tests are pending with later milestones. |

## Deferred or Blocked Items

- Proprietary simulator extensions are deferred until independently verified.
- Restart and summary writers are deferred until reader behavior and round-trip validation exist.
- Local grid refinement, dual-grid, NNC, and complex well segment edge cases are deferred until sample files or public documentation are available.
