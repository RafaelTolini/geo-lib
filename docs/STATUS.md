# Status

## Current Milestone

M14: Public Facade Module Surface is complete for the scoped import-boundary
behavior. There is no remaining unblocked milestone in the current roadmap.

## Completed Work

- Specification read and converted into an implementation roadmap.
- Traceability matrix created with initial statuses.
- Python 3.11+ package scaffold added with `pyproject.toml`, README, `src/`
  layout, and typed package marker.
- `.gitignore` added for Python build, cache, coverage, and virtual-environment
  artifacts.
- Layered package foundation added for public API, application services, domain,
  formats, infrastructure, schemas, and exceptions.
- Explicit exception hierarchy implemented.
- `FileCategory`, `FileFormat`, `FormatDetectionResult`, and `LoadCaseOptions`
  implemented.
- Filename-based `FileDetector` implemented for primary categories and
  conservative non-unified restart/summary step patterns.
- `FileCatalog` implemented for basename, explicit-file, and unambiguous
  directory discovery.
- `CaseManifest` implemented with category queries and preferred-file selection.
- `SimulationCase.open(...)` implemented without payload parsing.
- Unsupported payload loader methods fail explicitly with `UnsupportedFormatError`
  when matching files exist, and `FileReadError` when required categories are
  absent.
- Focused M1 tests added.
- `KeywordType`, `KeywordRecord`, and `KeywordDataset` implemented.
- `KeywordQuery` and `CaseSensitivity` schemas implemented.
- `AmbiguousKeywordError` added for occurrence-ambiguous keyword queries.
- GRDECL tokenizer implemented for whitespace, comments, slash terminators,
  quoted strings, and escaped quote characters.
- GRDECL parser implemented for ordered keyword records, repeat syntax, integer,
  float, double-exponent, string, logical, empty-string, and defaulted values.
- GRDECL reader implemented for text files with `FileReadError` wrapping.
- Focused M2 tests added.
- `GridDimensions` implemented with total-cell, pillar-count, IJK/global-index
  conversion, and bounds validation behavior.
- `CellIndex` implemented with explicit IJK, global-index, and active-index
  constructors plus simulator one-based conversion.
- `ActiveCellMap` implemented with active-to-global, global-to-active,
  active-sized expansion, global-sized compression, and shape validation.
- `GridGeometry` implemented with GRDECL-compatible `COORD`/`ZCORN` storage,
  array length validation, MAPAXES validation, and lightweight depth/top/bottom/
  thickness access.
- `ReservoirGrid` and `GridCell` implemented for resolving cells by IJK, global,
  or active index and exposing activity and depth-derived cell values.
- `GrdeclGridBuilder` implemented for minimal grid construction from parsed or
  inline GRDECL text using `SPECGRID`, `COORD`, `ZCORN`, and optional `ACTNUM`.
- Focused M3 tests added.
- `Endianness`, `FortranRecord`, `FortranRecordReader`, and
  `detect_fortran_record_endianness` implemented under infrastructure binary
  I/O.
- Fortran-style record reader now validates leading/trailing marker agreement,
  detects truncated leading markers, payloads, and trailing markers, and rejects
  implausibly large records according to a configured maximum.
- Simple endian detection implemented by checking the first record's matching
  leading/trailing markers while preserving stream position.
- `FormattedKeywordReader` implemented for common GRDECL-style formatted text
  keyword records.
- Formatted reader rejects binary-looking input instead of pretending to parse
  unformatted payloads.
- Focused M4 tests added.
- `GridProperty`, `PropertyLayout`, and `PropertyCollection` implemented for
  typed grid-associated property values.
- `GridReader` implemented for minimal formatted GRDECL-style GRID/EGRID keyword
  files containing `SPECGRID`, `COORD`, `ZCORN`, and optional `ACTNUM`.
- `InitReader` implemented for selected formatted INIT/property keyword loading.
- `GridPropertyService` implemented to coordinate grid and property loading from
  a `CaseManifest`.
- `SimulationCase.load_grid()` now loads supported formatted GRID/EGRID files.
- `SimulationCase.load_properties()` now loads supported formatted INIT files
  and associates properties with the case grid when a supported grid file exists.
- Focused M5 tests added.
- `RestartHeader`, `RestartReport`, and `RestartDataset` implemented with
  report metadata, sequence/step/day/date lookup, and lazy keyword payload access.
- `ReportStepQuery` implemented for typed report lookup.
- `FormattedRestartReader` implemented for formatted GRDECL-style restart files
  using `REPORT` blocks.
- Formatted unified restart files can expose multiple report steps without
  loading report payload keywords.
- Formatted non-unified restart report-step files can be grouped by detected
  filename report step.
- Restart report payload keywords can be mapped to `GridProperty` values when a
  grid is supplied.
- `RestartService` implemented to coordinate formatted restart loading from a
  `CaseManifest`.
- `SimulationCase.load_restarts()` now loads supported formatted restart files,
  with optional grid association.
- Focused M6 tests added.
- `SummaryKey`, `SummaryVectorMetadata`, `SummaryMetadata`, `SummaryVector`, and
  `SummaryDataset` implemented for formatted summary metadata, time axes, vector
  lookup, filtering, exact time lookup, and lazy value loading.
- `SummaryVector` implements first/last value access, report-step lookup,
  generic linear interpolation, fixed-day resampling, and an optional NumPy
  export boundary.
- `SummaryDataset` implements wildcard/qualifier filtering, optional NumPy and
  pandas export boundaries, and CSV export with the standard library.
- `FormattedSummaryReader` implemented for scoped GRDECL-style formatted summary
  fixtures using `VECTOR`, `TIME`, `DATES`, `REPORTS`, and `VALUES` records.
- Formatted unified summary files can expose multiple report steps without
  loading vector values until requested.
- Formatted non-unified summary report-step files can be grouped by detected
  filename report step when `REPORTS` is absent.
- `SummaryService` implemented to coordinate formatted summary loading from a
  `CaseManifest`.
- `SimulationCase.load_summary()` now loads supported formatted summary files.
- Focused M7 tests added.
- `WellConnection`, `WellSegment`, `WellSnapshot`, `WellTimeline`, and
  `WellDataset` implemented for well names, timeline navigation, snapshot state,
  rates, connections, and optional segments.
- `FormattedWellReader` implemented for scoped formatted restart payload records
  `WELL`, `WCONN`, `WRATE`, and `WSEG`.
- `WellService` implemented to build well timelines from supported restart data.
- `SimulationCase.load_wells(load_segments=...)` now loads supported formatted
  restart well timelines and validates connection cells when a supported grid is
  present.
- `RftCellMeasurement`, `RftRecord`, and `RftDataset` implemented for RFT/PLT
  well/date/type queries, lazy measurement loading, pressures, depths,
  saturations, and phase rates.
- `FormattedRftReader` implemented for scoped formatted RFT/PLT text fixtures
  using `RFTREC`, `RFTCELL`, and `PLTCELL` records.
- `RftService` implemented to coordinate formatted RFT/PLT loading from a
  `CaseManifest`.
- `SimulationCase.load_rft()` now loads supported formatted RFT/PLT files.
- Focused M8 tests added.
- `PropertyCollection` now supports lazy property loaders and exposes
  `is_property_loaded(...)`.
- `InitReader` can index formatted INIT keyword records lazily, and public
  `SimulationCase.load_properties(...)` honors `LoadCaseOptions.lazy_loading`.
- `SourceFingerprint` implemented for cache invalidation using resolved path,
  file size, and `mtime_ns`.
- `JsonIndexCache` implemented for optional JSON reader indexes with hit, miss,
  and write counters.
- `FormattedSummaryReader` can persist and reuse formatted summary
  metadata/time-axis/vector-key indexes while keeping vector values lazy.
- `SummaryService` now honors `LoadCaseOptions.cache_policy` for formatted
  summary index cache use.
- `.reservoir_data_cache/` added to `.gitignore`.
- Focused M9 tests added for lazy INIT property loading, eager/lazy property
  equivalence, summary cache hit/miss behavior, cache invalidation, and public
  cache policy wiring.
- `ExportFormat`, `PropertyExportLayout`, and `PropertyExportOptions` added for
  typed export boundaries.
- `GrdeclWriter` implemented for the GRDECL-style text subset supported by the
  current parser, including string escaping, logical values, numeric values, and
  defaulted values.
- `ExportService` implemented for supported grid geometry export and selected
  property export in native, active, or global layout.
- `SimulationCase.export_grid_grdecl(...)` and
  `SimulationCase.export_properties_grdecl(...)` added as public export
  workflows.
- Focused M10 tests added for GRDECL formatting, grid export round-trip,
  property export layout conversion, and public case export workflows.
- `GridTableExportOptions` and `PropertyTableExportOptions` added for typed
  tabular export boundaries.
- `ExportService.grid_cell_rows(...)` and `write_grid_cell_csv(...)` implemented
  for supported grid cell metadata, including zero-based indexes, simulator
  one-based indexes, activity, active/global mapping, and lightweight
  top/bottom/depth/thickness values.
- `ExportService.property_rows(...)`, `properties_to_table_rows(...)`,
  `write_property_csv(...)`, and `write_properties_csv(...)` implemented for
  selected supported properties in native, active, or global layout.
- `SimulationCase.export_grid_cell_csv(...)` and
  `SimulationCase.export_properties_csv(...)` added as public CSV export
  workflows.
- Focused M11 tests added for grid cell rows/CSV, property table rows/CSV,
  active/global layout conversion, inactive defaults, and public case CSV export
  workflows.
- `GridLoadOptions`, `RestartLoadOptions`, and `SummaryLoadOptions` added with
  supporting enums for geometry validation, restart grid association, summary
  key separator policy, and summary time unit policy.
- `SimulationCase.load_grid(...)`, `load_restarts(...)`, and `load_summary(...)`
  now accept the scoped load option objects.
- Grid loading now accepts basic/no geometry validation options and rejects
  unsupported local grids, NNC metadata, coordinate-transform application, lazy
  geometry arrays, and full corner-point validation requests.
- Restart loading now honors requested report-step filters and eager keyword
  payload materialization, while preserving header-only lazy behavior.
- Summary loading now honors vector-filtered datasets and eager vector value
  materialization.
- Unsupported advanced restart and summary options now raise explicit
  `UnsupportedFormatError` instead of being ignored.
- Focused M12 tests added for grid load options, restart report filtering/eager
  payload loading, summary vector filtering/eager loading, and unsupported
  advanced option errors.
- `KeywordRecord.numeric_values(...)` added for validated numeric tuple access,
  including explicit default replacement for defaulted values.
- `KeywordRecord.to_numpy(...)` added as an optional NumPy conversion boundary
  with explicit missing-dependency errors.
- `GridProperty.numeric_values(...)` and `to_numpy(...)` added for native,
  active, and global layout conversion using existing active/global mapping.
- Focused M13 tests added for keyword numeric/default/non-numeric conversion,
  property native/active/global numeric conversion, and optional NumPy boundary
  behavior.
- Public facade modules added for grid, property, restart, summary, well, and
  RFT/PLT workflows.
- `reservoir_data.public` now re-exports implemented public domain/result
  objects and relevant option/query/export DTOs alongside `SimulationCase`.
- Focused M14 tests added to validate facade imports, exported option DTO
  construction, and identity with implemented domain/schema classes.

## Work In Progress

- None for M14.

## Next Planned Task

No further unblocked milestone exists in the current roadmap. Remaining work is
compatibility expansion: binary payload decoding, independently verified vendor
variants, broader cache/index support, full geometry reconstruction, and
additional writer/export targets.

## Blockers

- Production-quality binary summary support requires independently validated
  SMSPEC/UNSMRY keyword payload decoding beyond the current record-framing
  infrastructure.
- Production-quality well extraction requires independently validated restart
  well record semantics and sample files.
- Production-quality RFT/PLT support requires independently validated binary and
  vendor-specific measurement record semantics and sample files.

## Deferred Specification Items

- Binary/unformatted GRID/EGRID and INIT keyword payload decoding.
- Binary/unformatted restart payload parsing.
- Binary/unformatted summary payload parsing.
- Binary/vendor-specific well and RFT/PLT payload parsing.
- Broad simulator-format export, binary writers, full deck writing, restart/
  summary rewriting, and broader writer/export targets.
- Broad cache/index support beyond formatted summary indexes.
- Independent verification topics listed in the roadmap.

## Validation Commands Run

- `python -m pytest` failed initially because `pytest` was not installed in the
  default `C:\Python314` environment.
- `python -m pip install -e ".[test]"` succeeded, installing the declared test
  extra in editable mode.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 22 passed in
  0.12s on the final run.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 29 passed in
  0.21s on the final M2 run.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 37 passed and
  1 skipped in 0.23s on the final M3 run. The skipped test is the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 46 passed and
  1 skipped in 0.25s on the final M4 run. The skipped test remains the optional
  NumPy array conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 52 passed and
  1 skipped in 0.32s on the final M5 run. The skipped test remains the optional
  NumPy array conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 58 passed and
  1 skipped in 0.50s after M6. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 64 passed and
  1 skipped in 0.55s after M7. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 71 passed and
  1 skipped in 0.72s after M8. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 75 passed and
  1 skipped in 0.87s after M9. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 79 passed and
  1 skipped in 0.97s after M10. The skipped test remains the optional NumPy
  array conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_export_service.py`
  succeeded: 6 passed in 0.38s during M11 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 81 passed and
  1 skipped in 0.87s after M11. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_load_options.py`
  succeeded: 3 passed in 0.36s during M12 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 84 passed and
  1 skipped in 0.89s after M12. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_numpy_boundaries.py`
  succeeded: 2 passed in 0.36s during M13 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 86 passed and
  1 skipped in 0.90s after M13. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_public_facades.py`
  succeeded: 2 passed in 0.23s during M14 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 88 passed and
  1 skipped in 1.01s after M14. The skipped test remains the optional NumPy array
  conversion path because NumPy is not installed in this environment.

## Known Limitations

- Only GRDECL text keyword payloads are parsed.
- Discovery will be filename-based until format readers and binary/text sniffing
  are implemented.
- Exact formatted and non-unified extension conventions are conservative and
  require independent verification before being advertised as complete support.
- Public loaders are supported only for the scoped formatted keyword variants
  described below. Binary and vendor-specific workflows remain unsupported until
  independently validated.
- The GRDECL parser itself does not perform deck semantics, property shape
  validation, or binary/formatted simulator keyword parsing. Minimal grid
  construction is handled separately by `GrdeclGridBuilder`.
- GRDECL bare default repeats such as `3*` are represented as `None`; later
  domain validators decide whether defaults are legal for a given keyword.
- Grid construction is limited to minimal GRDECL text-derived grids. Binary
  GRID/EGRID readers are not implemented.
- `GridGeometry` stores and validates `COORD` and `ZCORN`, but does not yet
  reconstruct full corner-point XYZ coordinates, compute cell volumes, locate
  spatial points, or support local grids, dual grids, or NNC metadata.
- Active/global mapping supports optional NumPy arrays in code, but the NumPy
  validation test was skipped because NumPy is not installed.
- Binary infrastructure reads Fortran-style record frames only; it does not
  decode simulator-specific binary keyword names, types, element counts, string
  padding, or numeric payload arrays yet.
- `FormattedKeywordReader` supports the GRDECL-style text keyword syntax already
  implemented by `GrdeclParser`; it does not claim every simulator formatted-file
  variant.
- GRID/EGRID reader support is limited to formatted GRDECL-style keyword content.
  Unformatted binary GRID/EGRID files are still unsupported.
- INIT reader support is limited to formatted GRDECL-style keyword content.
  It loads selected properties after parsing the formatted keyword file; no
  persistent large-file index or lazy binary payload loading exists yet.
- Property layout inference is shape-based. When active and global sizes are the
  same, the property is conservatively classified as global-sized.
- Restart support is limited to formatted GRDECL-style restart fixtures. Binary
  `.UNRST`/restart keyword payload decoding is not implemented.
- Formatted unified restart files require `REPORT` keywords to delimit report
  blocks. Formatted non-unified restart files may omit `REPORT` only when the
  report step is detected from the filename.
- Restart report headers currently capture report step, sequence index,
  simulation days, ISO report date, source path, and unified flag. Complete
  simulator restart header semantics remain pending.
- Well data extraction from restart files is not implemented.
- Summary support is limited to formatted GRDECL-style summary fixtures. Binary
  `.SMSPEC`/`.UNSMRY` payload decoding is not implemented.
- Formatted summary metadata requires `VECTOR` records. Formatted summary data
  requires `TIME`, `DATES`, and `VALUES` records; unified data also requires
  `REPORTS`, while formatted non-unified files may derive a single report step
  from the detected filename.
- Summary vector resampling uses generic linear interpolation by simulation day.
  Simulator-specific rate/cumulative resampling rules remain deferred.
- pandas and NumPy are optional. Summary export methods raise explicit
  `UnsupportedFormatError` messages when the optional dependency is absent.
- Well timeline support is limited to formatted restart payload fixtures with
  `WELL`, `WCONN`, `WRATE`, and `WSEG` records. Complete simulator restart well
  extraction, wellhead metadata, connection factors beyond the scoped fields,
  segment topology semantics, and vendor-specific well records remain pending.
- RFT/PLT support is limited to formatted text fixtures with `RFTREC`, `RFTCELL`,
  and `PLTCELL` records. Binary/unformatted RFT/PLT payload decoding and
  vendor-specific measurement variants remain pending.
- RFT/PLT headers are indexed eagerly, while cell measurements are loaded lazily
  when `RftRecord.measurements` is accessed.
- Formatted INIT lazy loading defers `GridProperty` materialization, but it does
  not yet implement byte-offset streaming or memory mapping for very large text
  arrays.
- Cache/index support is currently limited to formatted summary metadata/time
  axes/vector keys. Cache files are optional and correctness does not depend on
  them.
- Cache invalidation uses resolved source path, size, and `mtime_ns`; stronger
  checksum-based invalidation remains future hardening.
- GRDECL writer support is limited to the text keyword subset supported by the
  current parser. It is validated for supported grid geometry and selected grid
  property exports only.
- Grid export writes stored `COORD`/`ZCORN` arrays and `ACTNUM`, but it does not
  reconstruct full corner-point geometry, local grids, dual grids, NNC metadata,
  or simulator-specific binary GRID/EGRID records.
- Property export writes selected loaded properties in native, active, or global
  layout. Unit conversion and simulator binary INIT writing remain pending.
- Grid cell CSV export uses the existing lightweight geometry metrics derived
  from stored ZCORN values. It does not provide full corner-point XYZ coordinate
  tables, cell volumes, local grids, dual grids, or NNC metadata.
- Property CSV export is long-form row output for supported loaded properties.
  It does not yet provide pandas DataFrames, unit conversion, wide pivoted
  property tables, or simulator-specific table schemas.
- `GridLoadOptions` is a typed public contract, but local grids, NNC metadata,
  coordinate-transform application, lazy geometry arrays, and full corner-point
  validation still raise explicit unsupported errors.
- `RestartLoadOptions` supports requested report-step filtering, header-only
  loading, and eager keyword payload materialization. Well-data extraction
  through restart loading remains unsupported; users should use `load_wells()`
  for the scoped formatted well workflow.
- `SummaryLoadOptions` supports vector filtering and eager/lazy vector loading.
  Restart metadata fusion, alternate key separators, alternate time units, and
  relaxed metadata validation still raise explicit unsupported errors.
- Keyword and grid-property NumPy conversion is optional and raises
  `UnsupportedFormatError` when NumPy is not installed.
- Keyword and grid-property values are currently tuple-backed immutable domain
  values, so `to_numpy(...)` returns a copied boundary array rather than a shared
  mutable view into a backing numeric buffer.
- Numeric conversion rejects strings and logical values instead of coercing them;
  defaulted values require an explicit numeric replacement.
- Public facade modules are import boundaries over implemented domain objects and
  DTOs. They do not add new loader behavior, compatibility aliases for other
  APIs, or public access to low-level parser/binary internals.

## Assumptions

- The repository has no existing `pyproject.toml`, `justfile`,
  `.pre-commit-config.yaml`, `.python-version`, README, or architecture docs.
- Python 3.11+ is required; validation ran with Python 3.14.4 because it is the
  default interpreter in this environment.
- First milestone should prioritize honest discovery and shared architecture over
  unsupported parser claims.
- GRDECL type inference is conservative: numeric values promote to float or
  double only when syntax requires it; otherwise mixed semantic records are
  marked `MIXED` instead of guessed.
- M3 derives lightweight cell depth/top/bottom/thickness from eight stored
  ZCORN values per global cell. This is a conservative internal convention for
  the current minimal grid domain and is not a compatibility guarantee for full
  simulator corner-point geometry ordering.
- M4 assumes 4-byte or 8-byte unsigned Fortran record markers. Endian detection
  is intentionally simple and validates only the first record's matching marker
  pair.
- M5 treats formatted GRID/EGRID/INIT sample fixtures as GRDECL-style keyword
  text. This is a narrow implementation slice, not a guarantee for all simulator
  formatted output variants.
- M6 treats formatted restart sample fixtures as GRDECL-style keyword text with
  `REPORT` delimiters. This is a narrow implementation slice, not a guarantee
  for simulator binary or vendor-specific formatted restart variants.
- M7 treats formatted summary sample fixtures as GRDECL-style keyword text with
  `VECTOR` metadata records and `VALUES` vector records. This is a narrow
  implementation slice, not a guarantee for simulator binary or vendor-specific
  formatted summary variants.
- M8 treats formatted restart well data and RFT/PLT sample fixtures as
  GRDECL-style keyword text with scoped record names. This is a narrow
  implementation slice, not a guarantee for simulator binary or vendor-specific
  well/RFT/PLT variants.
- M9 treats optional cache files as performance indexes only. It assumes source
  path, file size, and `mtime_ns` are sufficient for the first cache
  invalidation contract.
- M10 treats GRDECL text export as the first writer target because the matching
  reader subset is already validated. Other writer targets remain deferred until
  independently required and verified.
- M11 treats standard-library CSV/row output as the first non-summary tabular
  export target because it can reuse the validated grid/property domain model
  without adding optional dependency or simulator-specific assumptions.
- M12 treats unsupported advanced load options as explicit errors until the
  underlying reader/domain behavior exists, preventing silent no-op option
  handling.
- M13 treats NumPy as an optional boundary dependency. The current tuple-backed
  keyword/property model is immutable, so shared mutable NumPy views are deferred
  until there is a real numeric buffer or memory-mapped payload implementation.
- M14 treats the public facade modules as stable import boundaries only. Actual
  workflow support remains limited to the implemented `SimulationCase` methods
  and scoped formatted readers.
