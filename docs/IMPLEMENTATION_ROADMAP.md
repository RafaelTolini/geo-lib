# Implementation Roadmap

This roadmap is the control document for implementing `reservoir_data` against the independent specification. No milestone may be marked complete unless it has implemented behavior plus validation through tests, executable examples, or a documented independent validation path. Discovery-only support must not be described as parser support.

## Major Capability Areas

- Project scaffold and package organization
- Explicit exception model
- Schemas, DTOs, and value objects
- Public API/facades
- Case discovery and manifest management
- File type detection, formatted/unformatted flags, unified/non-unified grouping
- Text I/O and GRDECL token/keyword parsing
- Keyword records and keyword datasets
- Grid domain model, geometry, cell indexing, and active/global mapping
- GRID/EGRID reading
- INIT/property loading
- Binary record infrastructure, endian/header detection, and formatted/unformatted keyword files
- Restart datasets, reports, headers, lazy payload loading, and unified/non-unified handling
- Summary metadata, vectors, interpolation/resampling, NumPy/pandas/CSV export
- RFT/PLT datasets and measurement records
- Well timelines, snapshots, connections, segments, and rates
- Lazy loading, large-file behavior, cache/index support
- Optional writers and exports where explicitly supported
- Black-box tests and independent verification items

## Milestone Plan

### M0: Governance and Planning

Dependencies: none.

Reason: The specification requires visible tracking before implementation so capabilities are not skipped silently.

Acceptance Criteria:

- `docs/IMPLEMENTATION_ROADMAP.md` exists and lists the major capability areas.
- `docs/SPEC_TRACEABILITY.md` exists and maps specification areas to statuses.
- `docs/STATUS.md` exists and records milestone, blockers, deferred items, validation, limitations, and assumptions.

Test Requirements:

- Documentation review for required sections.

Out of Scope:

- Runtime package behavior.
- Format parsing.

### M1: Project Foundation and Case Discovery

Dependencies: M0.

Reason: Every later reader and facade depends on a stable package layout, exception taxonomy, typed loading/detection contracts, and a manifest of discovered case files.

Acceptance Criteria:

- Python 3.11+ package `reservoir_data` is importable from `src/`.
- Layer directories exist without claiming unsupported parser behavior.
- The exception model is implemented as typed exception classes.
- `LoadCaseOptions` and `FormatDetectionResult` are implemented.
- File detection recognizes known first-class extensions and conservative non-unified report-step patterns.
- `FileCatalog` discovers files by case basename without loading file contents.
- `CaseManifest` reports available categories, preserves diagnostics, and resolves preferred files.
- `SimulationCase.open()` returns a case object without loading grid, restart, summary, well, RFT, or property payloads.
- Heavy `load_*` methods raise explicit errors until real parsers exist.

Test Requirements:

- Unit tests for extension detection, formatted/unformatted flags where implemented, unified/non-unified flags, and report-step inference.
- Unit tests for case discovery by basename.
- Unit tests for strict discovery and unsupported load errors.
- Import smoke test for public API and exception exports.

Out of Scope:

- GRDECL parsing.
- Binary parsing.
- Grid/property/restart/summary/well/RFT data loading.
- pandas, CSV, and NumPy array exports.
- Cache/index behavior.

### M2: Grid Indexing, Active Mapping, and Property Core

Dependencies: M1.

Reason: Grid readers, INIT properties, restart cell properties, wells, and RFT records need shared index and active/global mapping behavior before parsing formats into domain objects.

Acceptance Criteria:

- `GridDimensions`, `CellIndex`, `ActiveCellMap`, `GridProperty`, and `PropertyCollection` are implemented with bounds and shape validation.
- Active-to-global and global-to-active conversion works for Python zero-based indexing.
- Property lookup by cell index is implemented for active and global layouts.
- NumPy is isolated at array boundaries or replaced by compatible sequence behavior until NumPy support is introduced.

Test Requirements:

- Bounds checks and invalid index tests.
- Active/global conversion tests.
- Property shape mismatch tests.
- Property cell lookup tests.

Out of Scope:

- Geometry calculations from COORD/ZCORN.
- Reading GRID/EGRID/INIT files.
- pandas/CSV export.

### M3: Keyword Domain and GRDECL Text Reader

Dependencies: M1 and M2.

Reason: GRDECL and later text/formatted keyword files require keyword records, datasets, query behavior, tokenization, repeat syntax, comments, and terminators.

Acceptance Criteria:

- `KeywordRecord`, `KeywordDataset`, `KeywordType`, and `KeywordQuery` are implemented.
- Text tokenization supports comments, whitespace, slash terminators, strings, logical values, and repeat syntax.
- GRDECL reader parses selected keyword records into typed keyword datasets.
- Unterminated records and unsupported type inference raise explicit errors.

Test Requirements:

- Integer, float, string, logical, and repeat syntax tests.
- Comment and irregular whitespace tests.
- Missing/ambiguous keyword query tests.
- Unterminated keyword tests.

Out of Scope:

- Binary keyword records.
- GRID/EGRID binary files.
- Full deck semantic validation.

### M4: Minimal Grid Construction from GRDECL

Dependencies: M2 and M3.

Reason: Grid domain behavior and GRDECL keyword parsing must exist before constructing a `ReservoirGrid` from `SPECGRID`, `COORD`, `ZCORN`, `ACTNUM`, and optional `MAPAXES`.

Acceptance Criteria:

- Minimal `ReservoirGrid`, `GridCell`, and `GridGeometry` are implemented for structured grids.
- GRDECL grid construction validates dimensions and geometry keyword counts.
- Active/inactive status is connected to `ActiveCellMap`.
- Grid cell index tables can be exported in a basic tabular form without pandas.

Test Requirements:

- Minimal grid fixture tests.
- Inactive cell mapping tests.
- Invalid dimension and keyword-count tests.

Out of Scope:

- Full geometric volume calculations if independent formulas/sample validation are not yet available.
- Local grid refinements, dual-grid metadata, and NNC metadata.
- Binary GRID/EGRID reading.

### M5: Binary Keyword Infrastructure

Dependencies: M1 and M3.

Reason: GRID/EGRID, INIT, restart, summary, and RFT/PLT readers need low-level record access isolated below format readers.

Acceptance Criteria:

- Fortran-style record reader detects record-size mismatches.
- Endian/header detection is implemented or explicitly configurable.
- Binary record infrastructure is not exposed through public facades.
- Formatted/unformatted keyword-file distinction has validation tests for supported cases.

Test Requirements:

- Valid binary record read tests.
- Truncated/corrupt record tests.
- Endianness selection tests for supported byte orders.

Out of Scope:

- Full simulator-specific GRID/EGRID/INIT/restart/summary parsing.
- Memory-mapped large-file optimization unless required for correctness.

### M6: GRID/EGRID Reader

Dependencies: M2, M4, and M5.

Reason: The grid reader converts binary/formatted keyword records into the grid domain model and needs both geometry/index behavior and binary infrastructure.

Acceptance Criteria:

- Supported GRID/EGRID variants load dimensions, activity, and geometry records.
- Unsupported variants raise `UnsupportedFormatError`.
- Geometry consistency errors raise `GridGeometryError`.
- Public `case.load_grid()` returns `ReservoirGrid` for validated samples.

Test Requirements:

- Minimal GRID/EGRID sample tests.
- Malformed geometry tests.
- Active/global mapping integration tests.

Out of Scope:

- Writing GRID/EGRID.
- Unverified local grid refinement and dual-grid edge cases.

### M7: INIT and Property Loading

Dependencies: M2, M3, M5, and M6 where grid association is requested.

Reason: INIT data requires keyword records, property shape validation, and optional association with a loaded grid.

Acceptance Criteria:

- Selected properties can be loaded without loading unrelated properties.
- Active-sized and global-sized property arrays are supported.
- Missing properties and shape mismatches raise specified errors.
- Public `case.load_properties(names=...)` returns a typed collection.

Test Requirements:

- Selected-property tests.
- Active/global property tests.
- Missing property and shape mismatch tests.

Out of Scope:

- Writing INIT files.
- Unit conversion unless metadata is independently validated.

### M8: Restart Dataset and Report Loading

Dependencies: M2, M3, M5, M6, and M7 for grid-property association.

Reason: Restart payloads use keyword records, report indexing, lazy loading, and grid-sized property conversion.

Acceptance Criteria:

- Unified and supported non-unified restart files are grouped.
- Report headers/index load without payload arrays.
- Reports can be retrieved by report step, date, simulation day, or sequence index where metadata is available.
- Report payload keywords load lazily.
- Invalid report queries raise `InvalidReportStepError`.

Test Requirements:

- Unified restart header tests.
- Non-unified grouping tests.
- Lazy payload loading tests.
- Invalid report-step tests.

Out of Scope:

- Restart writing.
- Well extraction unless implemented in M10.

### M9: Summary Dataset, Vectors, and Export

Dependencies: M3 and M5.

Reason: Summary metadata/data parsing uses keyword infrastructure and requires stable vector/domain behavior before export.

Acceptance Criteria:

- SMSPEC and supported summary data layouts load metadata and vector values.
- Vector keys, units, qualifiers, dates, simulation days, and report steps are exposed.
- Lazy vector loading is supported.
- Filtering and missing-vector behavior are implemented.
- CSV export and optional pandas export are implemented at boundaries.
- Interpolation/resampling behavior is documented and tested once independently validated.

Test Requirements:

- Metadata/vector tests.
- Wildcard/qualifier filter tests.
- Missing/truncated data tests.
- NumPy-compatible, pandas-optional, and CSV export tests.

Out of Scope:

- Round-trip summary writing unless explicitly added and tested.
- Unverified rate-versus-cumulative resampling semantics.

### M10: Well and RFT/PLT Workflows

Dependencies: M6, M8, and M9 where time/grid context is needed.

Reason: Wells and RFT/PLT records rely on restart data, grid indexes, time metadata, and optional segment-loading policies.

Acceptance Criteria:

- Well names and timelines are extracted where restart records include them.
- Snapshots expose open status, type, connections, segments when loaded, and available rates.
- RFT/PLT records can be queried by well/date/type.
- Missing well/RFT data raises the specified errors.

Test Requirements:

- Well timeline tests.
- Segment enable/disable tests.
- RFT/PLT query and measurement tests.
- Invalid connection cell tests.

Out of Scope:

- RFT/PLT writing.
- Unsupported vendor-specific well variants.

### M11: Large-File Behavior, Caching, and Optional Writers

Dependencies: M5 through M10.

Reason: Lazy loading and cache/index support must be validated against real readers and should not become a correctness dependency.

Acceptance Criteria:

- Opening cases avoids loading unrelated files.
- Restart and summary metadata-only workflows avoid loading payload arrays.
- Optional cache/index files are invalidated by source identity, size, timestamp, or stronger checksum.
- Optional writers are limited to explicitly supported outputs and include round-trip or black-box validation.

Test Requirements:

- Large-file or simulated lazy-loading tests.
- Cache invalidation tests.
- Writer/export round-trip tests where writing is supported.

Out of Scope:

- Guarantees for every proprietary extension.
- Simulator execution or physics validation.

## Independent Verification Backlog

- Exact formatted-file extension conventions across simulators.
- Exact non-unified summary filename conventions.
- Summary vector category classification rules.
- Rate versus cumulative interpolation/resampling rules.
- Restart files with missing optional well records.
- Malformed but partially readable keyword-file behavior.
- Endianness behavior across target platforms.
- String padding and variable-length binary string behavior.
- Dual-grid, local-grid refinement, NNC, and completion indexing edge cases.
- Whether restart or summary writing is required for an early release.
- Officially supported vendor-specific extensions.
