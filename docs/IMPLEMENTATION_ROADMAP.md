# Implementation Roadmap

This roadmap is derived from the independent reservoir simulation data library
specification. It is the source of implementation sequencing for this repository.

No milestone may be marked complete unless it has implemented behavior and a
validation path. Validation means focused automated tests, independently checked
fixtures, or a documented reason why the behavior cannot be validated yet. Broad
stubs, fake parsers, and unsupported format claims do not count as completion.

## Major Capabilities

- Repository and package scaffold for `reservoir_data`.
- Explicit exception model.
- Typed schemas, DTOs, and value objects.
- Public facade for opening cases and discovering available data.
- Thin public facade modules for grid, property, restart, summary, well, and
  RFT/PLT domain workflows.
- Case discovery and file type detection.
- GRDECL text tokenization and parsing.
- Keyword records and keyword datasets.
- Grid domain model, indexing, geometry, and active/global cell mapping.
- GRID/EGRID readers.
- INIT and property loading.
- Binary record infrastructure.
- Formatted and unformatted keyword file support.
- Unified and non-unified restart and summary handling.
- Restart datasets, reports, headers, and lazy payload access.
- Summary metadata, vectors, filtering, interpolation, and export.
- RFT/PLT records and cell measurements.
- Well timelines, snapshots, connections, segments, and rates.
- Lazy loading, large-file behavior, and optional cache/index support.
- Typed grid, restart, and summary load option schemas.
- NumPy integration at array boundaries.
- Numeric tuple and optional NumPy export boundaries for keyword/property data.
- Optional pandas and CSV export boundaries.
- Selective writer/export support where explicitly implemented.
- Tabular grid cell and property CSV export for supported loaded data.

## Milestones

### M1: Project Foundation and Case Discovery

Dependencies: none.

Reason: later parsers and domain services need a package layout, shared exception
model, typed discovery contracts, and a reliable way to locate case files.

Acceptance criteria:

- Python 3.11+ package scaffold exists under `src/reservoir_data`.
- Layer folders exist for public API, application services, domain, formats,
  infrastructure, schemas, and exceptions.
- Core exception classes exist and are importable.
- `LoadCaseOptions`, `FormatDetectionResult`, `FileFormat`, and `FileCategory`
  exist with validation where needed.
- `FileDetector` detects recognized extensions and conservative non-unified
  report-step naming patterns.
- `FileCatalog` discovers files for an explicit case basename, file path, or
  unambiguous case directory.
- `SimulationCase.open(...)` returns a case object without parsing file payloads.
- Unsupported load workflows fail explicitly with `UnsupportedFormatError`.
- Planning and traceability docs are updated.

Test requirements:

- Extension and non-unified naming detection tests.
- Case discovery by basename and directory tests.
- Strict ambiguity and missing-case error tests.
- Public facade unsupported-workflow error tests.

Out of scope:

- Parsing deck, GRDECL, GRID/EGRID, INIT, restart, summary, RFT, or PLT payloads.
- Loading numeric arrays.
- NumPy/pandas export.
- Caching and lazy binary payload loading beyond preserving the option contract.

### M2: Keyword Records and GRDECL Text Parser

Dependencies: M1.

Reason: GRDECL, properties, INIT-like text payloads, and some exports depend on
neutral keyword records and datasets.

Status: complete for the scoped M2 behavior. Keyword records/datasets,
`KeywordQuery`, the GRDECL tokenizer, the GRDECL parser, and the GRDECL reader
have implemented behavior and tests. This does not include binary keyword
records, full deck semantic validation, or grid/property construction.

Acceptance criteria:

- `KeywordRecord`, `KeywordDataset`, `KeywordType`, and `KeywordQuery` have real
  query behavior.
- GRDECL tokenizer handles comments, whitespace, slash terminators, strings, and
  repeat syntax.
- Parser returns ordered keyword datasets with clear errors for malformed input.
- Element type inference is conservative and documented.

Test requirements:

- Integer, float, string, logical, repeat syntax, comments, and irregular
  whitespace tests.
- Missing keyword and ambiguous occurrence tests.
- Unterminated record tests.

Out of scope:

- Binary keyword records.
- Full deck semantic validation.
- GRID/EGRID or INIT binary parsing.

### M3: Grid Domain Model and Active/Global Mapping

Dependencies: M2 for keyword-backed grid construction, M1 for shared contracts.

Reason: properties, wells, RFT measurements, and restart grid properties need
stable cell addressing and active/global mapping semantics.

Status: complete for the scoped M3 behavior. `GridDimensions`, `CellIndex`,
`ReservoirGrid`, `GridCell`, `GridGeometry`, and `ActiveCellMap` implement core
indexing, activity, shape validation, and lightweight depth-derived geometry.
`GrdeclGridBuilder` constructs a minimal grid from `SPECGRID`, `COORD`, `ZCORN`,
and optional `ACTNUM`. Full corner-point coordinate reconstruction, volume
calculation, local grids, dual grids, NNC, and binary GRID/EGRID readers remain
out of scope for this milestone.

Acceptance criteria:

- `GridDimensions`, `CellIndex`, `ReservoirGrid`, `GridCell`, `GridGeometry`,
  and `ActiveCellMap` implement core index and shape behavior.
- Zero-based and simulator one-based index conversion is explicit.
- Active-to-global and global-to-active conversion works for plain sequences and
  NumPy arrays when NumPy is available.
- Minimal GRDECL grid construction is supported for `SPECGRID`, `COORD`,
  `ZCORN`, and `ACTNUM` when sufficient records exist.

Test requirements:

- Index conversion and bounds tests.
- Active/global mapping tests.
- Minimal grid construction tests.
- Invalid dimension and shape error tests.

Out of scope:

- Complete corner-point geometry volume calculations.
- Local grid refinement, dual-grid, NNC, and map-axis edge cases.
- Binary GRID/EGRID reading.

### M4: Binary and Formatted Keyword Infrastructure

Dependencies: M2 and M3.

Reason: GRID/EGRID, INIT, restart, summary, and RFT readers require reliable
record I/O before domain-specific parsing can be honest.

Status: complete for the scoped M4 behavior. `FortranRecordReader`,
`FortranRecord`, `Endianness`, and `detect_fortran_record_endianness` implement
low-level Fortran-style record reading, marker mismatch detection, truncation
errors, configurable endian order, and simple endian detection. A common
`FormattedKeywordReader` reads GRDECL-style text keyword records and rejects
binary-looking input. Simulator-specific unformatted keyword decoding remains
out of scope for this milestone.

Acceptance criteria:

- Fortran-style record marker reader detects record-size mismatches and EOF.
- Endianness can be configured and simple marker detection is available.
- Formatted keyword reader reads documented text-style keyword records.
- Infrastructure APIs are internal to format readers, not public facades.

Test requirements:

- Valid and corrupt record tests.
- Truncated record tests.
- Endian detection tests with independent fixtures.
- Formatted/unformatted mismatch tests.

Out of scope:

- Complete simulator-specific binary keyword variants.
- Public exposure of low-level binary records.

### M5: GRID/EGRID and INIT Readers

Dependencies: M3 and M4.

Reason: grid geometry and initialization properties need both domain mapping and
keyword file infrastructure.

Status: complete for the scoped M5 behavior. `GridReader` loads minimal
formatted GRDECL-style GRID/EGRID keyword files using `SPECGRID`, `COORD`,
`ZCORN`, and optional `ACTNUM`. `InitReader`, `GridProperty`, and
`PropertyCollection` load selected formatted INIT/property keywords and associate
them with a compatible grid as active-sized or global-sized properties. Public
`SimulationCase.load_grid()` and `load_properties()` now use these readers for
supported formatted keyword files. Simulator-specific unformatted binary
GRID/EGRID/INIT keyword payload decoding remains out of scope.

Acceptance criteria:

- Minimal GRID/EGRID reader loads dimensions and activity for validated sample
  files.
- INIT/property reader loads selected properties without reading unrelated
  payloads where an index is available.
- Properties can be associated with a compatible grid.

Test requirements:

- Minimal grid fixture tests.
- Inactive cell mapping tests.
- Selected property loading tests.
- Shape mismatch and missing property tests.

Out of scope:

- Writing GRID/EGRID.
- Vendor-specific grid extensions without independent fixtures.

### M6: Restart Dataset and Reports

Dependencies: M4 and M5.

Reason: restart payloads depend on binary keyword infrastructure and grid
property mapping.

Status: complete for the scoped M6 behavior. `RestartHeader`, `RestartReport`,
and `RestartDataset` implement report metadata, sequence/step/day/date lookup,
and lazy report payload access. `FormattedRestartReader` indexes formatted
GRDECL-style restart fixtures using `REPORT` blocks, supports formatted unified
files and formatted non-unified report-step files, and maps loaded report
keywords to `GridProperty` objects when a grid is supplied. Public
`SimulationCase.load_restarts()` now loads supported formatted restart files.
Simulator-specific binary restart keyword payload decoding, full restart header
semantics, well extraction, and restart writing remain out of scope.

Acceptance criteria:

- Unified and non-unified restart files can be indexed.
- Report headers load without loading all payload arrays.
- Reports can be retrieved by step and sequence index.
- One report payload can be loaded on demand and mapped to grid-sized properties.

Test requirements:

- Unified and non-unified grouping tests.
- Header-only lazy behavior tests.
- Invalid report-step tests.
- Corrupt report block tests.

Out of scope:

- Complete well extraction.
- Restart writing.

### M7: Summary Dataset, Vectors, and Exports

Dependencies: M4.

Reason: summary metadata and vector files require binary/formatted keyword
infrastructure, but do not require a loaded grid.

Status: complete for the scoped M7 behavior. `SummaryKey`, `SummaryMetadata`,
`SummaryVector`, and `SummaryDataset` implement vector metadata, time axes,
exact report/date/day lookup, wildcard and qualifier filtering, lazy vector
value loading, generic linear interpolation/resampling, CSV export, and optional
NumPy/pandas export boundaries. `FormattedSummaryReader` and `SummaryService`
load formatted GRDECL-style summary fixtures using `VECTOR`, `TIME`, `DATES`,
`REPORTS`, and `VALUES` records, including formatted unified and formatted
non-unified report-step files. Simulator-specific binary `SMSPEC`/`UNSMRY`
payload decoding, complete vector classification guarantees, and summary
writing remain out of scope.

Acceptance criteria:

- SMSPEC/UNSMRY metadata and values load from independent fixtures.
- Vector keys, units, dates, simulation days, and report steps are exposed.
- Vector filtering and missing-vector errors work.
- NumPy, pandas, and CSV export boundaries are implemented with pandas optional.
- Resampling and interpolation behavior is documented and validated.

Test requirements:

- Metadata and vector retrieval tests.
- Filtering tests.
- Missing vector and truncated data tests.
- NumPy, pandas-optional, and CSV export tests.

Out of scope:

- Full vector classification guarantees until independently verified.
- Summary writing unless explicitly added later.

### M8: Well and RFT/PLT Data

Dependencies: M5, M6, and M7 where timeline alignment is needed.

Reason: well state and RFT/PLT records reference report steps, cells, rates, and
grid locations.

Status: complete for the scoped M8 behavior. `WellDataset`, `WellTimeline`,
`WellSnapshot`, `WellConnection`, and `WellSegment` implement well names,
timeline navigation, snapshot state, rates, connections, optional segment data,
and grid-backed connection validation from supported formatted restart records.
`RftDataset`, `RftRecord`, and `RftCellMeasurement` implement formatted RFT/PLT
record indexing, well/date/type queries, lazy measurement loading, pressures,
depths, saturations, and phase rates. `FormattedWellReader`,
`FormattedRftReader`, `WellService`, `RftService`, and public
`SimulationCase.load_wells()`/`load_rft()` wire these workflows for scoped
GRDECL-style text fixtures. Binary/vendor-specific well records, complete
restart well extraction, and unformatted RFT/PLT decoding remain out of scope.

Acceptance criteria:

- Well names and timelines can be built from supported restart records.
- Snapshots expose open state, type, connections, rates, and optional segments.
- RFT/PLT records can be queried by well and date from supported sample files.

Test requirements:

- Timeline and snapshot retrieval tests.
- Connection cell index validation tests.
- Segment-disabled behavior tests.
- RFT/PLT query and malformed record tests.

Out of scope:

- Writing well or RFT/PLT files.
- Unsupported proprietary well record variants.

### M9: Lazy Loading, Cache, and Large-File Hardening

Dependencies: M4 through M8.

Reason: lazy loading and caches need real payload readers before memory behavior
can be validated honestly.

Status: complete for the scoped M9 behavior. `PropertyCollection` now supports
lazy `GridProperty` loaders, and public property loading honors
`LoadCaseOptions.lazy_loading` so selected formatted INIT properties are indexed
without materializing values until requested. `SourceFingerprint` and
`JsonIndexCache` implement optional source-identity cache/index files with
resolved path, size, and modification time invalidation. Formatted summary
loading can use `LoadCaseOptions.cache_policy` to persist and reuse metadata/time
axis/vector-key indexes while keeping vector values lazy. Eager/lazy equivalence,
cache hit/miss, and cache invalidation are validated. Binary payload lazy loading,
memory mapping/chunked reading, cache support for every reader, and hard
thread-safety guarantees remain out of scope.

Acceptance criteria:

- Opening a case avoids loading unrelated files.
- Summary vectors, restart report payloads, and large property arrays load on
  demand.
- Optional cache/index files improve repeated access without changing results.
- Cache invalidation uses source identity, size, and timestamp at minimum.

Test requirements:

- Lazy loader call-count or memory-bounded behavior tests.
- Cache hit/miss and invalidation tests.
- Eager/lazy result equivalence tests.

Out of scope:

- Hard thread-safety guarantees unless explicitly designed.
- Mandatory cache files.

### M10: Selective Writers and Export Hardening

Dependencies: M2 through M9, depending on target.

Reason: writers must preserve simulator-compatible organization and should only
be added after readers and domain objects are validated.

Status: complete for the scoped M10 behavior. `PropertyExportOptions`,
`PropertyExportLayout`, and `ExportFormat` define typed export boundaries.
`GrdeclWriter` writes the GRDECL-style text subset supported by the current
parser, including strings, logicals, numerics, and defaulted values.
`ExportService` exports supported grid geometry (`SPECGRID`, `COORD`, `ZCORN`,
and optional `ACTNUM`) and selected grid properties in native, active, or global
layout. Public `SimulationCase.export_grid_grdecl(...)` and
`export_properties_grdecl(...)` expose these workflows. Exported grid/property
text round-trips through existing readers in tests. Full deck writing,
arbitrary restart/summary rewriting, binary writers, and broad simulator-format
writers remain out of scope.

Acceptance criteria:

- GRDECL geometry/property export is implemented and tested.
- CSV and pandas export remain isolated at boundaries.
- Any simulator-format writer documents limitations and round-trips against
  independent fixtures.

Test requirements:

- GRDECL output formatting tests.
- CSV header/date/value tests.
- Writer round-trip tests only for supported writer targets.

Out of scope:

- Full deck schedule editing.
- Arbitrary restart or summary rewriting unless independently required and
  validated.

### M11: Tabular Grid and Property Export

Dependencies: M3, M5, and M10.

Reason: the specification calls for users to inspect and export grid geometry,
cell indexes, and grid property values as tabular data. This is unblocked by the
validated grid/property domain model and the selective export service, and it can
be implemented without claiming unsupported binary or vendor-format behavior.

Status: complete for the scoped M11 behavior. `GridTableExportOptions` and
`PropertyTableExportOptions` define typed CSV/table export boundaries.
`ExportService` now returns tabular grid cell rows and writes grid cell CSV with
zero-based indexes, simulator one-based indexes, activity, active/global mapping,
and lightweight top/bottom/depth/thickness values. It also returns and writes
long-form property rows for selected properties in native, active, or global
layout with inactive defaults where applicable. Public
`SimulationCase.export_grid_cell_csv(...)` and `export_properties_csv(...)`
expose these workflows. Full pandas DataFrame exports for grid/properties,
corner-point XYZ coordinate tables, volumes, units, local grids, NNC, binary
writers, and vendor-specific tabular semantics remain out of scope.

Acceptance criteria:

- Grid cell rows and CSV include stable index, activity, and lightweight
  geometry columns for supported grids.
- Property table rows and CSV support selected properties and native, active, or
  global layout export.
- Inactive defaults are respected when active-sized properties are expanded to
  global rows.
- Public facade methods expose the supported CSV export workflows.

Test requirements:

- Grid cell row and CSV tests.
- Property table row and CSV tests for active/global layout conversion.
- Public facade CSV export tests.

Out of scope:

- pandas DataFrame export for grid/property tables.
- Full corner-point XYZ reconstruction, cell volumes, local grids, dual grids,
  and NNC table export.
- Unit conversion and simulator-specific table schemas.
- Binary or broad simulator-format writers.

### M12: Typed Load Options and Service Enforcement

Dependencies: M5, M6, M7, and M9.

Reason: the specification defines `GridLoadOptions`, `RestartLoadOptions`, and
`SummaryLoadOptions` as user-facing contracts for loader behavior. These options
should exist only once the corresponding loaders have real behavior, so the
library can honor supported options and reject unsupported advanced requests
without silently ignoring them.

Status: complete for the scoped M12 behavior. `GridLoadOptions`,
`RestartLoadOptions`, and `SummaryLoadOptions` are implemented with supporting
enums for geometry validation, restart grid association, summary key separator,
and summary time units. `SimulationCase.load_grid(...)`,
`load_restarts(...)`, and `load_summary(...)` accept these option objects.
Grid loading validates supported basic/no geometry validation and rejects local
grids, NNC metadata, coordinate-transform application, lazy geometry arrays, and
full corner-point validation. Restart loading honors requested report-step
filters and eager keyword payload loading, preserves header-only lazy behavior,
and rejects restart well-data extraction through this path. Summary loading
honors vector filtering and eager vector value loading, while rejecting
unsupported restart metadata inclusion, non-colon key policies, non-day time
policies, and relaxed metadata validation.

Acceptance criteria:

- Load option DTOs exist with normalized enum and iterable fields.
- Public facade methods accept the scoped option objects.
- Supported options alter returned datasets or loading behavior in tests.
- Unsupported advanced options raise explicit `UnsupportedFormatError`.

Test requirements:

- Grid load option acceptance and unsupported-option tests.
- Restart requested-report filtering and eager payload tests.
- Summary vector-filter and eager value tests.
- Unsupported advanced option tests.

Out of scope:

- Full local-grid, dual-grid, NNC, and full geometry validation support.
- Restart well extraction through `RestartLoadOptions`.
- Summary restart metadata fusion, alternate key separators, alternate time
  units, and relaxed metadata validation.
- Binary/unformatted option behavior beyond existing explicit unsupported
  errors.

### M13: Keyword and Property NumPy Boundary Hardening

Dependencies: M2, M3, and M5.

Reason: the specification calls for keyword records and grid properties to
provide typed array access and optional NumPy conversion at boundaries. This can
be implemented safely after keyword parsing and grid/property layout conversion
exist, without adding NumPy as a core dependency or claiming mutable shared-array
semantics for tuple-backed data.

Status: complete for the scoped M13 behavior. `KeywordRecord.numeric_values(...)`
returns validated numeric tuples, supports explicit replacement of defaulted
values, and rejects logical/string values instead of coercing them.
`KeywordRecord.to_numpy(...)` provides an optional NumPy conversion boundary with
an explicit missing-dependency error. `GridProperty.numeric_values(...)` and
`to_numpy(...)` provide the same behavior for native, active, and global
property layouts, reusing existing active/global shape conversion and inactive
defaults. NumPy remains optional, and tuple-backed records/properties return
copied arrays when NumPy is available.

Acceptance criteria:

- Keyword records expose numeric tuple conversion with clear errors for
  defaulted, logical, and string values.
- Keyword records expose an optional NumPy array boundary with explicit missing
  dependency behavior.
- Grid properties expose numeric tuple and optional NumPy conversion for native,
  active, and global layouts.
- Property conversion honors active/global mapping and inactive defaults.

Test requirements:

- Keyword numeric/default/non-numeric conversion tests.
- Property native/active/global numeric conversion tests.
- Optional NumPy boundary tests that pass whether NumPy is installed or absent.

Out of scope:

- NumPy as a required dependency.
- Mutable shared-view semantics for tuple-backed keyword/property values.
- Memory mapping, chunked binary arrays, or binary keyword numeric buffers.
- Unit conversion while exporting numeric arrays.

### M14: Public Facade Module Surface

Dependencies: M5 through M13, depending on exposed domain object.

Reason: the specification proposes thin public facade modules for grid,
restart, summary, and well workflows, and the public API should expose stable
user-facing imports without requiring users to know internal domain module paths.
These modules should be added only after the underlying domain objects and option
schemas have real behavior, so public imports do not advertise unsupported
workflows.

Status: complete for the scoped M14 behavior. Public facade modules now exist
for grid, property, restart, summary, well, and RFT/PLT workflows. They re-export
the already implemented domain/result objects and relevant option/query/export
schemas without duplicating loader logic. `reservoir_data.public` also exposes
the same stable surface alongside `SimulationCase`. These facades are import
boundaries only; binary/vendor support and unsupported advanced workflow options
remain governed by the underlying services and domain objects.

Acceptance criteria:

- Public grid, property, restart, summary, well, and RFT/PLT facade modules are
  importable.
- Facades expose the implemented domain objects and relevant DTOs through
  explicit `__all__` lists.
- `reservoir_data.public` exposes the same stable facade classes.
- Tests validate public facade imports resolve to the implemented domain/schema
  classes.

Test requirements:

- Import tests for each public facade module.
- Constructibility tests for exported option DTOs.
- Identity tests proving public exports refer to implemented domain/schema
  classes.

Out of scope:

- New loader behavior beyond existing `SimulationCase` methods.
- Compatibility aliases for external APIs.
- Public exposure of low-level binary/parser internals.
- Claiming support for binary/vendor-specific workflows through facade names.

## Deferred Independent Verification

These topics must remain `blocked` or `deferred` until verified with public
documentation, domain experts, or independent sample files:

- Exact formatted-file extension conventions across simulators.
- Exact non-unified summary filename conventions.
- Complete summary vector classification rules.
- Rate versus cumulative interpolation/resampling rules.
- Optional restart well record variants.
- Endianness behavior across target platforms.
- Binary string padding and variable-length string behavior.
- Local grid refinement, dual-grid, and NNC edge cases.
- One-based indexing conventions for completions and NNC records.
- Whether restart or summary writing is required for the first production scope.
