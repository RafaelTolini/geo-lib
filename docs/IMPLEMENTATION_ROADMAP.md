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
- NumPy integration at array boundaries.
- Optional pandas and CSV export boundaries.
- Selective writer/export support where explicitly implemented.

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
