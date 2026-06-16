# Specification Traceability

Statuses:

- `not_started`
- `in_progress`
- `implemented`
- `partially_implemented`
- `blocked`
- `deferred`

No row may be advanced to `implemented` without real behavior and validation.

| Specification area | Status | Implementation notes | Validation |
| --- | --- | --- | --- |
| Project scaffold | implemented | `pyproject.toml`, README, `.gitignore`, `src/` package, typed package marker, and test configuration exist. | `python -m pytest`: 22 passed. |
| Package structure | partially_implemented | Layered folders exist for public, application, domain, formats, infrastructure, schemas, and exceptions. Domain-specific future modules are not all created yet. | Import and facade tests passed. |
| Exceptions | implemented | Explicit exception hierarchy exists in `reservoir_data.exceptions.errors`. | Error-path tests passed for discovery, missing files, and unsupported workflows. |
| Schemas/value objects | partially_implemented | `LoadCaseOptions`, `FormatDetectionResult`, `FileCategory`, `FileFormat`, and `KeywordQuery` exist. Export/grid/restart/summary option schemas remain later work. | Detection, category-filter, and keyword query tests passed. |
| Public API/facade | partially_implemented | `SimulationCase.open`, `available_data`, `has_data`, and `files_for` are implemented. Payload loaders raise explicit errors until parsers exist. | Facade tests passed. |
| Case discovery | partially_implemented | Basename, explicit-file, and unambiguous-directory discovery are implemented. Deeper naming policy configuration and exact simulator convention coverage remain later work. | Discovery tests passed. |
| File type detection | partially_implemented | Extension-based detection exists for main categories plus conservative non-unified step patterns. No payload sniffing yet. | Detection tests passed. |
| GRDECL parser | implemented | Text tokenizer, parser, and reader handle comments, whitespace, slash terminators, quoted strings, logicals, numeric values, repeat syntax, and strict unterminated-record errors. | GRDECL tests passed. |
| Keyword records/datasets | implemented | `KeywordRecord`, `KeywordDataset`, `KeywordType`, and `KeywordQuery` provide occurrence-aware retrieval, type/size validation, missing errors, and ambiguous-query errors. | Keyword dataset tests passed. |
| Grid domain model | not_started | Planned for M3. | Pending. |
| GRID/EGRID reader | not_started | Planned for M5 after binary/keyword infrastructure. | Pending. |
| INIT/property loading | not_started | Planned for M5. | Pending. |
| Active/global mapping | not_started | Planned for M3. | Pending. |
| Binary record infrastructure | not_started | Planned for M4. | Pending. |
| Formatted/unformatted keyword files | not_started | Planned for M4. | Pending. |
| Unified/non-unified handling | partially_implemented | Detection records unified flags and report steps for supported filename patterns. Payload grouping/indexing is later work. | Detection and manifest tests passed. |
| Restart dataset/reports | not_started | Planned for M6. | Pending. |
| Summary dataset/vectors | not_started | Planned for M7. | Pending. |
| RFT/PLT data | not_started | Planned for M8. | Pending. |
| Well timelines/states/connections/segments | not_started | Planned for M8. | Pending. |
| Lazy loading | partially_implemented | M1 preserves load option and opens cases without payload parsing. Real lazy payload providers are later work. | Facade/discovery tests passed. |
| NumPy integration | not_started | Planned for M3 and later boundaries. | Pending. |
| pandas/CSV export | not_started | Planned for M7 and M10; pandas remains optional. | Pending. |
| Error handling | partially_implemented | Discovery, facade, keyword query, and GRDECL parse/read error paths are implemented; later parser/domain errors remain pending. | Error tests passed. |
| Large-file behavior | partially_implemented | Opening a case uses filenames only and avoids payload loading. Memory-bound tests require real payload readers. | Discovery tests use empty files and do not parse contents. |
| Tests | partially_implemented | M1 and M2 tests exist for foundation, keyword, and GRDECL behavior. Full black-box test plan remains pending. | `python -m pytest`: 29 passed. |

## Assumptions Recorded

- Python 3.11+ is required because the repository has no existing version file.
- Exact formatted and non-unified extension conventions require independent
  verification before being treated as comprehensive compatibility guarantees.
- M1 file detection is based on filenames only; no payload sniffing is claimed.
- M2 GRDECL type inference is conservative: numeric mixes promote to float or
  double, unquoted non-numeric values are strings, mixed semantic records are
  `MIXED`, and bare repeat defaults such as `3*` are represented as `None`.
