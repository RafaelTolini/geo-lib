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
| Project scaffold | implemented | `pyproject.toml`, README, `.gitignore`, `src/` package, typed package marker, and test configuration exist. | `python -m pytest`: latest run 46 passed, 1 skipped. |
| Package structure | partially_implemented | Layered folders exist for public, application, domain, formats, infrastructure, binary I/O, text I/O, schemas, exceptions, keyword, and grid. Domain-specific future modules are not all created yet. | Import, facade, and infrastructure tests passed. |
| Exceptions | implemented | Explicit exception hierarchy exists in `reservoir_data.exceptions.errors`. | Error-path tests passed for discovery, missing files, and unsupported workflows. |
| Schemas/value objects | partially_implemented | `LoadCaseOptions`, `FormatDetectionResult`, `FileCategory`, `FileFormat`, `KeywordQuery`, `GridDimensions`, and `CellIndex` exist. Export/grid load/restart/summary option schemas remain later work. | Detection, category-filter, keyword query, and grid index tests passed. |
| Public API/facade | partially_implemented | `SimulationCase.open`, `available_data`, `has_data`, and `files_for` are implemented. Payload loaders raise explicit errors until parsers exist. | Facade tests passed. |
| Case discovery | partially_implemented | Basename, explicit-file, and unambiguous-directory discovery are implemented. Deeper naming policy configuration and exact simulator convention coverage remain later work. | Discovery tests passed. |
| File type detection | partially_implemented | Extension-based detection exists for main categories plus conservative non-unified step patterns. No payload sniffing yet. | Detection tests passed. |
| GRDECL parser | implemented | Text tokenizer, parser, and reader handle comments, whitespace, slash terminators, quoted strings, logicals, numeric values, repeat syntax, and strict unterminated-record errors. | GRDECL tests passed. |
| Keyword records/datasets | implemented | `KeywordRecord`, `KeywordDataset`, `KeywordType`, and `KeywordQuery` provide occurrence-aware retrieval, type/size validation, missing errors, and ambiguous-query errors. | Keyword dataset tests passed. |
| Grid domain model | partially_implemented | Core structured-grid dimensions, cell indexes, grid cells, reservoir grid access, geometry array validation, and lightweight depth/top/bottom/thickness behavior are implemented. Full corner-point reconstruction, volume, spatial lookup, local grids, dual grids, NNC, and grid table export remain later work. | Grid domain tests passed. |
| GRID/EGRID reader | not_started | Planned for M5 after binary/keyword infrastructure. | Pending. |
| INIT/property loading | not_started | Planned for M5. | Pending. |
| Active/global mapping | implemented | `ActiveCellMap` converts active-sized sequences to global-sized values, compresses global-sized sequences, validates shapes, and includes optional NumPy-array paths. | Sequence tests passed; NumPy-specific test skipped because NumPy is not installed. |
| Binary record infrastructure | implemented | `FortranRecordReader` reads length-prefixed records with configurable endian order, validates leading/trailing markers, reports truncation, and provides simple endian detection. | Binary I/O tests passed. |
| Formatted/unformatted keyword files | partially_implemented | Common formatted text keyword reader is implemented for GRDECL-style records, and unformatted low-level record framing is implemented. Simulator-specific binary keyword payload decoding is not implemented yet. | Formatted reader and formatted/unformatted mismatch tests passed. |
| Unified/non-unified handling | partially_implemented | Detection records unified flags and report steps for supported filename patterns. Payload grouping/indexing is later work. | Detection and manifest tests passed. |
| Restart dataset/reports | not_started | Planned for M6. | Pending. |
| Summary dataset/vectors | not_started | Planned for M7. | Pending. |
| RFT/PLT data | not_started | Planned for M8. | Pending. |
| Well timelines/states/connections/segments | not_started | Planned for M8. | Pending. |
| Lazy loading | partially_implemented | M1 preserves load option and opens cases without payload parsing. Real lazy payload providers are later work. | Facade/discovery tests passed. |
| NumPy integration | partially_implemented | `ActiveCellMap` has optional NumPy array expansion/compression when NumPy is available. Broader NumPy boundaries for properties, summary vectors, and mutation semantics remain later work. | NumPy test is present but skipped in this environment because NumPy is not installed. |
| pandas/CSV export | not_started | Planned for M7 and M10; pandas remains optional. | Pending. |
| Error handling | partially_implemented | Discovery, facade, keyword query, GRDECL parse/read, grid index, grid geometry, active-map shape, binary record, endian detection, and formatted keyword mismatch errors are implemented; later parser/domain errors remain pending. | Error tests passed. |
| Large-file behavior | partially_implemented | Opening a case uses filenames only and avoids payload loading. Memory-bound tests require real payload readers. | Discovery tests use empty files and do not parse contents. |
| Tests | partially_implemented | M1 through M4 tests exist for foundation, keyword, GRDECL, grid, active-map, binary I/O, and formatted keyword behavior. Full black-box test plan remains pending. | `python -m pytest`: 46 passed, 1 skipped. |

## Assumptions Recorded

- Python 3.11+ is required because the repository has no existing version file.
- Exact formatted and non-unified extension conventions require independent
  verification before being treated as comprehensive compatibility guarantees.
- M1 file detection is based on filenames only; no payload sniffing is claimed.
- M2 GRDECL type inference is conservative: numeric mixes promote to float or
  double, unquoted non-numeric values are strings, mixed semantic records are
  `MIXED`, and bare repeat defaults such as `3*` are represented as `None`.
- M3 stores GRDECL `COORD` and `ZCORN` arrays and derives simple depth metrics
  from eight stored ZCORN values per global cell. This is sufficient for the
  current domain tests but is not a full corner-point geometry reconstruction.
- M4 binary infrastructure handles Fortran-style record framing only. It does
  not decode simulator-specific binary keyword payload layouts yet.
