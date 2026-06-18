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
- Unit-system and phase value objects as metadata boundaries.
- Exact and nearest report/time query policies.
- Scoped `.DATA` deck metadata extraction.
- Optional pandas DataFrame export for grid/property tabular data.
- Configurable generic summary interpolation/resampling methods.
- Optional checksum-backed cache source fingerprints.
- Opt-in payload format sniffing and explicit formatted/unformatted contracts.
- Keyword dataset contiguous block extraction.
- Grid cell corner-depth access and property evaluation convenience.
- Explicit formatted summary and restart path loading.
- Explicit formatted grid and INIT/property path loading.
- Lazy property collection selection.
- Lazy property collection materialization.
- Well and RFT/PLT dataset filtering and sub-selection helpers.
- Public row/CSV helpers for summary, restart, well, and RFT/PLT datasets.
- Deck keyword occurrence/count helpers.
- Format detection diagnostic helpers and formatted-file requirement checks.
- Exact summary vector value lookup by time index, simulation day, and date.
- Restart report keyword listing and property collection helpers.
- Well connection and segment row/CSV exports.
- RFT/PLT measurement row/CSV exports.
- Summary time-axis, vector metadata, and per-vector row/CSV exports.
- Restart report-step selection and report keyword metadata exports.
- Keyword, property, manifest, and case file metadata row/CSV helpers.
- Lightweight grid cell iteration, cell rows, and depth-range helpers.

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
value loading, generic interpolation/resampling, CSV export, and optional
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

### M15: Unit and Phase Domain Value Objects

Dependencies: M3, M10, and M14.

Reason: the specification includes unit-system and phase concepts as domain
value objects. They are unblocked after the grid/property/export objects and
public facade surface exist, and they can be implemented honestly as metadata
normalization without claiming unit conversion.

Status: complete for the scoped M15 behavior. `UnitSystem` and `Phase` exist
under `domain.units`, normalize common labels, expose known/unknown checks, and
are re-exported through a public units facade. `ReservoirGrid` and
`PropertyExportOptions` normalize optional unit-system metadata. Unit conversion
and phase-specific simulator semantics remain out of scope.

Acceptance criteria:

- `UnitSystem` and `Phase` are importable domain value objects.
- Common labels and aliases normalize to canonical enum values.
- Optional fields can normalize `None` without fabricating metadata.
- Public units facade exports the implemented domain classes.

Test requirements:

- Unit-system and phase normalization tests.
- Invalid label tests.
- Grid/export option unit-system normalization tests.
- Public facade import tests.

Out of scope:

- Unit conversion.
- Phase-dependent rate interpretation.
- Simulator-specific unit keyword decoding.

### M16: Exact and Nearest Report-Time Queries

Dependencies: M6, M7, M8, and M14.

Reason: `ReportStepQuery` is specified as a common typed query for restart,
summary, and well timelines, including nearest/exact policy. Exact lookup
already existed, so nearest behavior can be added as a coherent domain slice.

Status: complete for the scoped M16 behavior. `ReportStepMatchPolicy` now
controls exact or nearest matching, with exact as the default. `RestartDataset`,
`SummaryDataset`, and `WellTimeline` support typed query methods for report
step, simulation day, report date, and exact sequence index. Nearest matching
uses generic absolute distance and breaks ties by earliest sequence/time-axis
index.

Acceptance criteria:

- `ReportStepQuery` exposes an exact/nearest match policy.
- Exact matching remains default behavior.
- Restart reports can be queried by exact or nearest report step, simulation
  day, and date.
- Summary datasets can resolve exact or nearest time-axis indexes.
- Well timelines can resolve exact or nearest snapshots.

Test requirements:

- Exact and nearest restart query tests.
- Exact and nearest summary time-index tests.
- Exact and nearest well timeline tests.
- Public facade export tests for the match policy.

Out of scope:

- Datetime precision beyond stored `date` values.
- Simulator-specific tolerance rules.
- Nearest sequence-index semantics beyond exact sequence lookup.

### M17: Scoped DATA Deck Metadata

Dependencies: M2, M4, M14, and existing discovery.

Reason: the specification calls for `.DATA` deck-level metadata where externally
useful, but full deck semantic validation is explicitly out of scope. A narrow
metadata reader can reuse the formatted keyword reader and expose only validated
metadata.

Status: complete for the scoped M17 behavior. `DeckMetadata`,
`FormattedDeckReader`, `DeckService`, and
`SimulationCase.load_deck_metadata()` extract supported deck `TITLE`, `START`,
keyword names, and source path from formatted GRDECL-style `.DATA` files.

Acceptance criteria:

- `.DATA` deck metadata can be loaded through the public case facade.
- `TITLE` is exposed as normalized text when present.
- `START` supports ISO date strings and common day/month/year forms.
- Keyword names and source path are preserved for diagnostics.
- Malformed supported metadata raises a clear parse error.

Test requirements:

- Formatted deck metadata extraction tests.
- ISO and day/month/year start-date tests.
- Public case deck metadata load test.
- Malformed `START` test.

Out of scope:

- Full deck semantic validation.
- Include-file expansion.
- Schedule editing or full deck writing.
- Binary or proprietary deck variants.

### M18: Grid and Property pandas DataFrame Boundaries

Dependencies: M11 and M14.

Reason: standard-library rows and CSV for grid/property tables already exist.
The specification also calls for pandas at optional export boundaries, so the
same validated row schema can be exposed as DataFrames without adding pandas as
a core dependency.

Status: complete for the scoped M18 behavior. `ExportService` can return
optional pandas DataFrames for grid cell rows, one property, and selected
property collections. `SimulationCase.grid_cell_dataframe()` and
`properties_dataframe()` expose these public workflows. pandas remains optional
and absent dependency errors are explicit.

Acceptance criteria:

- Grid cell table rows can be returned as a pandas DataFrame when pandas exists.
- Property table rows can be returned as a pandas DataFrame when pandas exists.
- Public case methods expose supported DataFrame workflows.
- Missing pandas raises `UnsupportedFormatError`.

Test requirements:

- Optional pandas service-boundary tests.
- Optional pandas public-case tests.
- Existing CSV/export tests remain green.

Out of scope:

- pandas as a required dependency.
- Wide/pivoted property table schemas.
- Unit conversion or simulator-specific tabular schemas.

### M19: Configurable Generic Summary Interpolation

Dependencies: M7 and M14.

Reason: the specification identifies interpolation/resampling behavior as a
required summary feature while noting that simulator-specific rate/cumulative
rules need independent verification. Generic linear and stepwise methods can be
implemented now with clear scope.

Status: complete for the scoped M19 behavior. `SummaryInterpolationMethod`
provides `linear` and `stepwise` methods. `SummaryVector.interpolate_at(...)`
and `resample(...)` accept the method while preserving linear behavior by
default.

Acceptance criteria:

- Linear interpolation remains default and backward compatible.
- Stepwise interpolation returns the previous known value between samples.
- Resampling supports both generic methods.
- Unknown methods and out-of-range days raise clear errors.
- Public summary facade exports the method enum.

Test requirements:

- Linear default interpolation/resampling tests.
- Stepwise interpolation/resampling tests.
- Invalid method and out-of-range tests.
- Public facade export tests.

Out of scope:

- Simulator-specific rate/cumulative interpolation guarantees.
- Calendar-frequency resampling beyond fixed simulation-day intervals.
- Summary binary payload decoding.

### M20: Stronger Cache Fingerprint Boundary

Dependencies: M9.

Reason: cache invalidation initially used resolved path, size, and `mtime_ns`.
The specification allows stronger source identity where available, and opt-in
checksums can harden cache workflows without changing default performance or
correctness assumptions.

Status: complete for the scoped M20 behavior. `SourceFingerprint.from_path(...)`
can include SHA-256 checksums, JSON round-tripping preserves checksum values, and
`JsonIndexCache(checksum_sources=True)` persists and validates checksum-backed
source fingerprints.

Acceptance criteria:

- Source fingerprints remain backward compatible when checksums are disabled.
- SHA-256 checksums can be requested explicitly.
- JSON cache envelopes can persist checksum fingerprints.
- Cache loading validates checksum fingerprints when enabled.

Test requirements:

- Checksum fingerprint tests.
- JSON round-trip tests.
- Checksum-backed cache save/load tests.
- Existing summary cache tests remain green.

Out of scope:

- Mandatory checksums for every cache.
- Cache support for every reader.
- Concurrent cache mutation guarantees.

### M21: Payload Sniffing and Format Override Contracts

Dependencies: M1, M4, and M20.

Reason: discovery initially relied on filenames only, while the specification
calls for formatted/unformatted handling and explicit mismatch errors. This can
be improved with opt-in payload sniffing without claiming binary payload
decoding.

Status: complete for the scoped M21 behavior. `LoadCaseOptions` now exposes
`sniff_payload_format`, `FileDetector.detect(...)` can sniff obvious formatted
text versus binary-looking payloads, ambiguous extensions can receive an
explicit formatted override, and `FormattedKeywordReader` rejects an explicit
unformatted expectation.

Acceptance criteria:

- Payload sniffing is opt-in and leaves default discovery behavior unchanged.
- Ambiguous extensions can be refined to formatted or unformatted by sniffing.
- Conflicts between known formatted extensions and sniffed binary-looking
  payloads raise `FileDetectionError`.
- Formatted keyword reader entry points reject explicit unformatted contracts.

Test requirements:

- Sniff text and binary-looking ambiguous files.
- Sniff conflict tests for formatted filename versus binary-looking payload.
- Explicit format override tests.
- Public case discovery sniffing test.

Out of scope:

- Simulator-specific binary keyword decoding.
- Mandatory payload sniffing for every discovery run.
- Heuristic guarantees for every possible binary/text payload variant.

### M22: Keyword Dataset Block Extraction

Dependencies: M2.

Reason: the specification says keyword datasets should return blocks or filtered
datasets. Name filtering existed; contiguous block extraction was missing and is
independent of format compatibility.

Status: complete for the scoped M22 behavior. `KeywordDataset.block(...)`
returns contiguous keyword subsets with start/end keyword names, occurrence
indexes, boundary inclusion, source preservation, and clear errors.

Acceptance criteria:

- Start keyword is required and occurrence-aware.
- End keyword is optional and occurrence-aware.
- Boundary inclusion can be controlled.
- Missing or reversed boundaries raise clear errors.

Test requirements:

- Basic block extraction tests.
- Source preservation tests.
- Occurrence and error-path tests.

Out of scope:

- Semantic deck section validation.
- Parser recovery from malformed partial decks.

### M23: Grid Cell Access Convenience

Dependencies: M3 and M5.

Reason: `GridCell` should expose cell-local geometry and evaluate compatible
properties. The current lightweight geometry can expose stored corner depths
and delegate property evaluation without full corner-point reconstruction.

Status: complete for the scoped M23 behavior. `GridCell.corner_depths` exposes
the eight stored ZCORN depths for the cell, and `GridCell.property_value(...)`
returns a compatible `GridProperty` value at that cell.

Acceptance criteria:

- Grid cells expose stored corner depths.
- Grid cells evaluate global-sized and active-sized compatible properties.
- Existing unsupported volume behavior remains explicit.

Test requirements:

- Corner-depth tests.
- Grid-cell property evaluation tests.
- Existing grid geometry tests remain green.

Out of scope:

- Full XYZ corner reconstruction.
- Cell volume calculation.
- Spatial point location.

### M24: Explicit Formatted Summary Path Loading

Dependencies: M7 and M12.

Reason: the specification calls for both case-basename loading and explicit
metadata/data path loading. The formatted summary reader already supports
explicit files internally, so a public facade can expose that behavior.

Status: complete for the scoped M24 behavior. `SummaryService` and
`reservoir_data.public.summary_facade.load_summary_from_paths(...)` load
formatted summary metadata and data files directly, including non-unified data
when report-step hints are supplied.

Acceptance criteria:

- Public facade can load formatted summary data from explicit paths.
- Unified files with `REPORTS` axes work without report-step hints.
- Non-unified files without `REPORTS` work with explicit report-step hints.
- Vector filters/eager options still apply.

Test requirements:

- Explicit unified summary path tests.
- Explicit non-unified path tests.
- Report-step count validation tests.

Out of scope:

- Binary SMSPEC/UNSMRY decoding.
- Automatic convention discovery for arbitrary explicit paths.
- Restart metadata fusion.

### M25: Explicit Formatted Restart Path Loading

Dependencies: M6 and M12.

Reason: restart workflows should support explicit file paths in addition to
case discovery. This is unblocked for the existing formatted restart slice.

Status: complete for the scoped M25 behavior. `RestartService` and
`reservoir_data.public.restart_facade.load_restarts_from_paths(...)` load
formatted restart data directly, including non-unified files with explicit
report-step hints and existing restart load options.

Acceptance criteria:

- Public facade can load formatted unified restart data from explicit paths.
- Non-unified formatted restart files can be grouped with report-step hints.
- Requested-report filtering and eager/lazy payload options still apply.
- Report-step hint count mismatches raise clear errors.

Test requirements:

- Explicit unified restart path tests.
- Explicit non-unified restart path tests.
- Requested report-step option tests.
- Report-step count validation tests.

Out of scope:

- Binary restart decoding.
- Automatic filename convention detection for arbitrary explicit paths.
- Restart writing.

### M26: Lazy Property Collection Selection

Dependencies: M5 and M9.

Reason: property collections should support selected property workflows while
preserving lazy loading. Existing lazy property names were not visible through
`has_property(...)`.

Status: complete for the scoped M26 behavior. `PropertyCollection.has_property`
now recognizes lazy properties, and `PropertyCollection.select(...)` returns a
subset collection while preserving lazy loaders.

Acceptance criteria:

- Lazy property names are visible before materialization.
- Selected lazy collections do not materialize values eagerly.
- Missing selected properties raise `MissingKeywordError`.

Test requirements:

- Lazy `has_property(...)` tests.
- Lazy selection tests.
- Existing eager/lazy property equivalence tests remain green.

Out of scope:

- Byte-offset streaming for huge INIT text payloads.
- Binary INIT payload lazy loading.

### M27: Well Dataset Filtering and Selection

Dependencies: M8 and M16.

Reason: users need ergonomic access to well names and timelines. The formatted
well timeline model already exists, so dataset-level selection helpers are
unblocked.

Status: complete for the scoped M27 behavior. `WellDataset` now supports
`has_well(...)`, wildcard name filtering, and selected timeline datasets.

Acceptance criteria:

- Well existence checks are case-insensitive.
- Wildcard filtering returns matching normalized well names.
- Selected datasets preserve sources and timeline behavior.

Test requirements:

- Well existence/filter/select tests in the formatted well workflow.

Out of scope:

- Additional restart well record variants.
- Multi-segment topology interpretation beyond existing scoped fields.

### M28: RFT/PLT Dataset Filtering and Selection

Dependencies: M8.

Reason: RFT/PLT datasets should expose record availability without loading
measurements. Record headers are already indexed eagerly, so filtering can be
implemented without changing lazy measurement behavior.

Status: complete for the scoped M28 behavior. `RftDataset` now exposes
available record types, filtered records by well/date/type, and selected
sub-datasets.

Acceptance criteria:

- Available RFT/PLT record types are exposed.
- Records can be filtered by optional well, date, and record type.
- Selection returns a new dataset without loading measurements.

Test requirements:

- Record type tests.
- Filter/select tests in the formatted RFT/PLT workflow.

Out of scope:

- Binary/unformatted RFT/PLT decoding.
- Vendor-specific measurement variants.

### M29: Explicit Formatted Grid and INIT Path Loading

Dependencies: M5, M12, and M14.

Reason: summary and restart workflows already support explicit formatted paths.
Grid and INIT/property workflows should offer the same convenience while staying
within the validated formatted keyword reader scope.

Status: complete for the scoped M29 behavior. `GridPropertyService`,
`reservoir_data.public.grid_facade.load_grid_from_path(...)`, and
`reservoir_data.public.property_facade.load_properties_from_path(...)` now load
supported formatted grid and INIT/property files from explicit paths.

Acceptance criteria:

- Public facades load supported formatted grid paths without case discovery.
- Public facades load selected formatted INIT/property paths with optional grid
  association and lazy/eager behavior.
- Existing grid load options are validated for explicit path loading.

Test requirements:

- Explicit grid path loading tests.
- Explicit INIT/property path loading tests.
- Root public facade export tests.

Out of scope:

- Binary GRID/EGRID/INIT decoding.
- Automatic discovery for arbitrary explicit-path groups.

### M30: Summary Dataset Public Row API

Dependencies: M7 and M24.

Reason: summary CSV/pandas export already builds row dictionaries internally.
Exposing those rows makes the standard-library export boundary useful without
forcing users to write temporary files.

Status: complete for the scoped M30 behavior. `SummaryDataset.rows(...)`
returns selected vector rows using the same schema as CSV/pandas export.

Acceptance criteria:

- Rows include date, report step, simulation days, and selected vector values.
- `to_csv(...)` and `to_pandas(...)` use the public row API.

Test requirements:

- Row-schema tests for selected vectors.
- Existing summary CSV and pandas-optional tests remain green.

Out of scope:

- Wide/pivot variants beyond the existing row schema.
- Summary writing or binary vector decoding.

### M31: Restart Dataset Timeline Rows and CSV

Dependencies: M6, M16, and M25.

Reason: restart report headers are already indexed lazily; users need a simple
metadata timeline export without materializing restart keyword payloads.

Status: complete for the scoped M31 behavior. `RestartDataset.timeline_rows()`
and `to_csv(...)` expose report step, sequence index, simulation days, date, and
source metadata.

Acceptance criteria:

- Timeline rows are emitted in sequence order.
- CSV export uses the standard library and does not load report payloads.

Test requirements:

- Restart timeline row tests.
- Restart timeline CSV tests.

Out of scope:

- Restart payload table export.
- Binary restart decoding.

### M32: Well Dataset Snapshot Rows and CSV

Dependencies: M8, M16, and M27.

Reason: well timelines are loaded into snapshot objects, but common inspection
workflows need flattened rows for report-step state, counts, and rates.

Status: complete for the scoped M32 behavior. `WellDataset.rows()` and
`to_csv(...)` return flattened snapshot rows with well name, report metadata,
well type/open state, connection and segment counts, and available rate columns.

Acceptance criteria:

- Rows preserve normalized well names and report metadata.
- Rate columns are generated from available snapshot rates.
- CSV export uses a stable base schema plus discovered rate columns.

Test requirements:

- Well snapshot row tests.
- Well CSV export tests.

Out of scope:

- Connection-level or segment-level table exports.
- Additional restart well record semantics.

### M33: RFT/PLT Header Rows and CSV

Dependencies: M8 and M28.

Reason: RFT/PLT headers are indexed eagerly while measurements remain lazy.
Header export should not force measurement materialization.

Status: complete for the scoped M33 behavior. `RftDataset.header_rows()` and
`to_csv(...)` expose well, date, record type, source, and measurement-loaded
state.

Acceptance criteria:

- Header rows can be exported before measurements are loaded.
- Measurement-loaded state reflects lazy payload access.
- CSV export uses the standard library.

Test requirements:

- RFT/PLT header row tests.
- RFT/PLT header CSV tests.
- Existing lazy measurement tests remain green.

Out of scope:

- RFT/PLT measurement table export.
- Binary/unformatted RFT/PLT decoding.

### M34: Lazy Property Collection Materialization

Dependencies: M5, M9, and M26.

Reason: selection preserved lazy loaders, but callers also need an explicit way
to convert selected lazy properties into an eager collection.

Status: complete for the scoped M34 behavior. `PropertyCollection.materialize(...)`
returns a new eager collection for all or selected properties while using the
existing lazy loaders and missing-property errors.

Acceptance criteria:

- Selected lazy properties can be materialized explicitly.
- Materialized collections expose eager loaded properties only.
- Missing names use the existing `MissingKeywordError` behavior.

Test requirements:

- Lazy selected materialization tests.
- Existing lazy selection tests remain green.

Out of scope:

- Byte-offset streaming indexes.
- Binary INIT lazy loading.

### M35: Deck Keyword Count Helpers

Dependencies: M17.

Reason: deck metadata already preserves keyword names. Users need simple
occurrence and unique-name helpers without full deck semantic validation.

Status: complete for the scoped M35 behavior. `DeckMetadata.keyword_count(...)`
and `unique_keyword_names()` report total/filtered keyword counts and
first-occurrence unique keyword names.

Acceptance criteria:

- Total keyword count is available.
- Case-insensitive keyword occurrence counts are available.
- Unique keyword names preserve first occurrence order.

Test requirements:

- Deck keyword count tests.
- Duplicate keyword unique-name tests.

Out of scope:

- Deck section semantics.
- Include expansion.

### M36: Detection Diagnostics and Formatted Requirement Helper

Dependencies: M21.

Reason: payload sniffing introduced richer detection state. Callers need
consistent diagnostic text and a reusable formatted-file guard.

Status: complete for the scoped M36 behavior. `FormatDetectionResult` now
exposes `format_label`, `diagnostic_summary()`, and
`require_formatted(...)`.

Acceptance criteria:

- Formatted, unformatted, and unknown states have stable labels.
- Diagnostics can be rendered as one compact summary string.
- Formatted-only workflows can raise `UnsupportedFormatError` from a detection
  result.

Test requirements:

- Detection label and summary tests.
- Formatted requirement success/error tests.

Out of scope:

- Binary decoding.
- Probabilistic payload classification guarantees.

### M37: Exact Summary Vector Value Lookup Helpers

Dependencies: M7 and M19.

Reason: `SummaryVector` supported report-step lookup and interpolation by
simulation day. Exact lookup by stored time index, simulation day, and date
rounds out the basic vector query surface.

Status: complete for the scoped M37 behavior. `SummaryVector` now supports
`value_at_time_index(...)`, `value_at_simulation_days(...)`, and
`value_at_date(...)`.

Acceptance criteria:

- Exact time-index lookup validates range.
- Exact simulation-day lookup uses stored time-axis values.
- Exact date lookup uses stored report dates.

Test requirements:

- Exact time-index/day/date value tests.
- Existing interpolation/resampling tests remain green.

Out of scope:

- Tolerance-based matching.
- Calendar-frequency resampling.

### M38: Restart Report Keyword and Property Helpers

Dependencies: M6, M13, and M31.

Reason: restart reports could map one keyword to a grid property, but users
also need to inspect available keyword names and convert selected report
keywords into a property collection.

Status: complete for the scoped M38 behavior. `RestartReport.keyword_names()`,
`has_keyword(...)`, and `properties(...)` expose report keyword availability and
selected property collections.

Acceptance criteria:

- Report keyword names are exposed in payload order.
- Keyword existence checks are case-insensitive through the keyword dataset.
- Selected restart keywords can be returned as a `PropertyCollection`.

Test requirements:

- Restart keyword listing and existence tests.
- Restart property collection tests.

Out of scope:

- Restart property table export.
- Binary restart payload decoding.

### M39: Well Connection Row Export

Dependencies: M8, M27, and M32.

Reason: well snapshots already expose connection objects. Users need
connection-level table rows without adding new restart well record semantics.

Status: complete for the scoped M39 behavior. `WellDataset.connection_rows()`
and `connections_to_csv(...)` export connection metadata for supported formatted
well snapshots.

Acceptance criteria:

- Rows include well/report metadata, connection index, zero-based and simulator
  one-based cell indexes, open state, direction, connection factor, and
  classification.
- CSV export uses the standard library.

Test requirements:

- Connection row tests.
- Connection CSV header tests.

Out of scope:

- New restart well record variants.
- Connection geometry beyond stored cell indexes.

### M40: Well Segment Row Export

Dependencies: M8, M27, and M32.

Reason: segment objects already exist for scoped formatted well snapshots.
Segment-level table rows are unblocked and keep segment loading optional.

Status: complete for the scoped M40 behavior. `WellDataset.segment_rows()` and
`segments_to_csv(...)` export segment id, parent id, depth, and length metadata.

Acceptance criteria:

- Rows preserve well/report metadata and segment fields.
- CSV export uses the standard library.

Test requirements:

- Segment row tests.
- Segment CSV header tests.

Out of scope:

- Full multi-segment topology interpretation.
- Segment geometry beyond scoped fields.

### M41: RFT/PLT Record Measurement Rows

Dependencies: M8 and M33.

Reason: record headers can be exported lazily, but cell-level RFT/PLT inspection
also needs explicit measurement rows that intentionally materialize one record.

Status: complete for the scoped M41 behavior. `RftRecord.measurement_rows()` and
`measurements_to_csv(...)` export one record's measurements with cell indexes,
depth, pressure, saturation columns, and rate columns.

Acceptance criteria:

- Measurement rows include well/date/type metadata and cell indexes.
- Saturation and rate keys become stable column names.
- CSV export uses the standard library.

Test requirements:

- RFT measurement row tests.
- Record measurement CSV tests.

Out of scope:

- Binary/unformatted RFT/PLT decoding.
- Vendor-specific measurement variants.

### M42: RFT/PLT Dataset Measurement Rows

Dependencies: M28, M33, and M41.

Reason: after record-level measurement rows exist, dataset-level filtered
measurement exports are a straightforward query/export surface.

Status: complete for the scoped M42 behavior. `RftDataset.measurement_rows(...)`
and `measurements_to_csv(...)` export measurement rows across optionally
filtered records.

Acceptance criteria:

- Dataset measurement rows honor existing well/date/type filters.
- CSV export handles discovered saturation and rate columns.

Test requirements:

- Dataset measurement row tests.
- Dataset measurement CSV tests.

Out of scope:

- Measurement lazy index caches.
- Binary/vendor-specific measurement payloads.

### M43: Summary Time-Axis Row Export

Dependencies: M7 and M30.

Reason: summary datasets already preserve dates, report steps, and simulation
days. Time-axis export should not load vector values.

Status: complete for the scoped M43 behavior. `SummaryDataset.time_axis_rows()`
and `time_axis_to_csv(...)` export time index, date, report step, and simulation
days.

Acceptance criteria:

- Rows are emitted in time-axis order.
- Export does not load vector values.

Test requirements:

- Time-axis row tests.
- Time-axis CSV tests.

Out of scope:

- Calendar-frequency resampling.
- Binary summary decoding.

### M44: Summary Vector Metadata Row Export

Dependencies: M7, M30, and M43.

Reason: vector metadata is available without loading values. Users need a
metadata table for keys, qualifiers, units, classifications, and loaded state.

Status: complete for the scoped M44 behavior.
`SummaryDataset.vector_metadata_rows()` and `vector_metadata_to_csv(...)` export
summary vector metadata without loading vector values.

Acceptance criteria:

- Rows include key, keyword, qualifier, qualifier kind, unit, classification,
  and loaded state.
- CSV export uses the standard library.

Test requirements:

- Vector metadata row tests.
- Vector metadata CSV tests.

Out of scope:

- Independently verified full vector classification semantics.
- Binary SMSPEC decoding.

### M45: Summary Vector Row Export

Dependencies: M7, M30, and M37.

Reason: `SummaryDataset.rows(...)` exports wide rows. Individual vectors also
need long-form rows for workflows that inspect or export one vector.

Status: complete for the scoped M45 behavior. `SummaryVector.rows()` and
`to_csv(...)` export one vector as key/date/report-step/simulation-day/value
rows.

Acceptance criteria:

- Rows include vector key, unit, time axes, and value.
- CSV export uses the standard library.

Test requirements:

- Summary vector row tests.
- Summary vector CSV tests.

Out of scope:

- Summary writing.
- Binary vector payload decoding.

### M46: Summary Filtered Dataset Selection

Dependencies: M7 and M30.

Reason: filtering keys and selecting explicit keys already existed separately.
A direct filtered-selection helper improves the public query surface without new
format assumptions.

Status: complete for the scoped M46 behavior. `SummaryDataset.select_by_filter(...)`
returns a dataset matching the existing wildcard/keyword/qualifier filters.

Acceptance criteria:

- Filtered selection reuses existing metadata filtering.
- The returned dataset preserves lazy loaders for selected vectors.

Test requirements:

- Filtered selection tests.

Out of scope:

- New semantic vector-classification rules.

### M47: Restart Report-Step Selection

Dependencies: M6, M16, and M31.

Reason: requested report-step filtering exists at load time. Users also need to
select report subsets from an already loaded restart dataset.

Status: complete for the scoped M47 behavior. `RestartDataset.select_report_steps(...)`
returns report subsets in the requested order.

Acceptance criteria:

- Selected datasets preserve source/unified/grid metadata.
- Missing report steps reuse existing `InvalidReportStepError` behavior.

Test requirements:

- Restart report-step selection tests.

Out of scope:

- Binary restart decoding.

### M48: Restart Report Keyword Metadata Export

Dependencies: M38.

Reason: restart reports expose keyword names. Payload keyword metadata rows make
the loaded report inspectable without converting every keyword to a property.

Status: complete for the scoped M48 behavior. `RestartReport.keyword_rows()` and
`keywords_to_csv(...)` export report keyword metadata rows.

Acceptance criteria:

- Rows include report step, sequence index, keyword, occurrence, type, value
  count, and source.
- CSV export uses the standard library.

Test requirements:

- Restart keyword row tests.
- Restart keyword CSV tests.

Out of scope:

- Restart payload value table export.
- Binary restart payload decoding.

### M49: Keyword Dataset Count Helpers

Dependencies: M2 and M22.

Reason: keyword names are already ordered; users need occurrence counts and
first-occurrence unique names for diagnostics.

Status: complete for the scoped M49 behavior. `KeywordDataset.unique_names()` and
`keyword_count(...)` expose syntactic keyword counts.

Acceptance criteria:

- Total record count is available.
- Case-insensitive single-keyword occurrence count is available.
- Unique names preserve first occurrence order.

Test requirements:

- Keyword count and unique-name tests.

Out of scope:

- Semantic deck section validation.

### M50: Keyword Dataset Metadata Row Export

Dependencies: M2, M22, and M49.

Reason: keyword datasets should be inspectable without expanding values into a
wide table.

Status: complete for the scoped M50 behavior. `KeywordDataset.rows()` and
`to_csv(...)` export keyword metadata rows with indexes, occurrences, type, and
value count.

Acceptance criteria:

- Rows preserve keyword order and occurrence indexes.
- CSV export uses the standard library.

Test requirements:

- Keyword metadata row tests.
- Keyword metadata CSV tests.

Out of scope:

- Full keyword value table export.

### M51: Property Collection Metadata Row Export

Dependencies: M5, M26, and M34.

Reason: property collections may be lazy. Metadata export should show loaded
state without forcing lazy property materialization.

Status: complete for the scoped M51 behavior. `PropertyCollection.metadata_rows()`
and `metadata_to_csv(...)` export property names, loaded state, layout, value
count, unit, and source when available.

Acceptance criteria:

- Metadata rows do not force lazy property loading.
- Loaded properties include layout and value count.
- CSV export uses the standard library.

Test requirements:

- Lazy metadata row tests.
- Property metadata CSV tests.

Out of scope:

- Byte-offset INIT indexing.
- Binary INIT lazy loading.

### M52: Case Manifest File Row Export

Dependencies: M1 and M36.

Reason: manifests already contain detection results. File rows make discovery
diagnostics inspectable and exportable without loading payloads.

Status: complete for the scoped M52 behavior. `CaseManifest.file_rows()` and
`files_to_csv(...)` export discovered file rows.

Acceptance criteria:

- Rows expose category, formatted/unified/report-step metadata, confidence, and
  diagnostics.
- CSV export uses the standard library.

Test requirements:

- Manifest/case file row tests.
- File CSV tests.

Out of scope:

- Payload parsing.

### M53: Detection Result Row Representation

Dependencies: M21 and M36.

Reason: manifest rows should be based on a stable per-detection row contract.

Status: complete for the scoped M53 behavior. `FormatDetectionResult.to_row()`
returns path, filename, category, format label, flags, report step, confidence,
and diagnostics.

Acceptance criteria:

- Detection rows include the same fields used by manifest file exports.
- Format labels reuse the existing diagnostic helper.

Test requirements:

- Detection row tests.

Out of scope:

- Stronger binary classification.

### M54: Public Case File Row Export

Dependencies: M52.

Reason: users work through `SimulationCase`, so manifest file rows should be
available from the public case object.

Status: complete for the scoped M54 behavior. `SimulationCase.file_rows()` and
`files_to_csv(...)` expose manifest file rows through the public case object.

Acceptance criteria:

- Public case file rows do not load payloads.
- CSV export delegates to the manifest.

Test requirements:

- Public case file row and CSV tests.

Out of scope:

- New discovery policies.

### M55: Reservoir Grid Cell Iteration Helpers

Dependencies: M3 and M23.

Reason: users often need all, active, or inactive cells as domain objects.
Existing grid access could resolve one cell at a time only.

Status: complete for the scoped M55 behavior. `ReservoirGrid.cells()`,
`active_cells()`, and `inactive_cells()` return resolved `GridCell` objects in
stable order.

Acceptance criteria:

- All cells are returned in global index order.
- Active cells are returned in active index order.
- Inactive cells are returned in global index order.

Test requirements:

- Cell iteration tests.

Out of scope:

- Lazy geometry arrays.

### M56: Reservoir Grid Domain Cell Rows

Dependencies: M11, M23, and M55.

Reason: grid table export existed in the export service. A domain-level row view
improves direct inspection without adding new file formats.

Status: complete for the scoped M56 behavior. `ReservoirGrid.cell_rows()`
returns lightweight cell metadata rows using the same stored-depth conventions
as existing grid cells.

Acceptance criteria:

- Rows include indexes, activity, and lightweight top/bottom/depth/thickness.
- Rows are emitted in global cell order.

Test requirements:

- Grid cell row tests.

Out of scope:

- Full corner-point XYZ tables.
- Volume calculation.

### M57: Grid Geometry Depth and Thickness Ranges

Dependencies: M3 and M23.

Reason: stored ZCORN-derived depth metrics can expose simple ranges now without
full corner-point geometry reconstruction.

Status: complete for the scoped M57 behavior. `GridGeometry.depth_range()` and
`thickness_range()` expose stored corner-depth and lightweight cell-thickness
ranges.

Acceptance criteria:

- Depth range uses stored ZCORN values.
- Thickness range uses existing bottom-top depth differences.

Test requirements:

- Depth/thickness range tests.

Out of scope:

- Full coordinate geometry validation.
- Volume ranges.

### M58: Grid Geometry Depth Rows

Dependencies: M3, M23, and M57.

Reason: users need a geometry-only depth table independent of activity and
property export.

Status: complete for the scoped M58 behavior. `GridGeometry.cell_depth_rows()`
returns per-global-cell top, bottom, depth, and thickness rows.

Acceptance criteria:

- Rows are emitted in global index order.
- Row values reuse existing lightweight geometry methods.

Test requirements:

- Geometry depth row tests.

Out of scope:

- Full XYZ corners, centers, and volumes.

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
