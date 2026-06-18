# Status

## Current Milestone

M58: Grid Geometry Depth Rows is complete for the scoped lightweight
ZCORN-derived geometry-row behavior. M39 through M58 are complete and ready for
testing.

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
  generic interpolation, fixed-day resampling, and an optional NumPy
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
- `UnitSystem` and `Phase` value objects added under `domain.units` with
  normalization helpers and public facade exports.
- `ReservoirGrid` and `PropertyExportOptions` now normalize optional unit-system
  metadata without performing unsupported unit conversion.
- Focused M15 tests added for unit/phase normalization, public units facade
  imports, grid unit metadata, and export option normalization.
- `ReportStepMatchPolicy` added to `ReportStepQuery`, preserving exact matching
  by default and enabling explicit nearest matching.
- `RestartDataset`, `SummaryDataset`, and `WellTimeline` now support typed query
  behavior with exact and nearest report step, simulation-day, and date matching.
- Focused M16 tests added for exact/nearest restart, summary, and well timeline
  queries and public match-policy exports.
- `DeckMetadata`, `FormattedDeckReader`, `DeckService`, and public
  `SimulationCase.load_deck_metadata()` implemented for scoped `.DATA` deck
  metadata extraction.
- Deck metadata loading now extracts supported `TITLE`, `START`, keyword names,
  and source path from formatted GRDECL-style deck text.
- Focused M17 tests added for deck metadata extraction, ISO and day/month/year
  start dates, public case loading, and malformed `START` errors.
- `ExportService` now exposes optional pandas DataFrame boundaries for grid cell
  rows, one property, and selected property collections.
- `SimulationCase.grid_cell_dataframe()` and `properties_dataframe()` added as
  optional pandas public workflows.
- Focused M18 tests added for service and public case DataFrame boundaries that
  pass whether pandas is installed or absent.
- `SummaryInterpolationMethod` added with `linear` and `stepwise` generic
  interpolation/resampling behavior for `SummaryVector`.
- Focused M19 tests added for linear default behavior, stepwise interpolation,
  stepwise resampling, invalid methods, out-of-range days, and public facade
  exports.
- `SourceFingerprint` now supports opt-in SHA-256 checksums, and
  `JsonIndexCache` can persist and validate checksum source fingerprints when
  `checksum_sources=True`.
- Focused M20 tests added for checksum fingerprints, JSON round-trip, and
  checksum-backed cache envelope reuse.
- `LoadCaseOptions.sniff_payload_format` added for opt-in payload format
  sniffing during discovery.
- `FileDetector.detect(...)` can now sniff obvious formatted text versus
  binary-looking payloads, apply explicit formatted overrides for ambiguous
  files, and report conflicts as detection errors.
- `FormattedKeywordReader` now rejects explicit unformatted expectations.
- Focused M21 tests added for payload sniffing, override contracts, discovery
  wiring, and formatted-reader mismatch behavior.
- `KeywordDataset.block(...)` added for occurrence-aware contiguous keyword
  block extraction.
- Focused M22 tests added for keyword block slicing, boundary handling,
  occurrence indexes, source preservation, and errors.
- `GridCell.corner_depths` and `property_value(...)` added for stored ZCORN
  corner-depth access and compatible property evaluation.
- Focused M23 grid-domain tests added for corner depths and property values.
- `SummaryService.load_summary_from_paths(...)` and public
  `load_summary_from_paths(...)` added for explicit formatted summary
  metadata/data paths, including report-step hints for non-unified files.
- Focused M24 summary tests added for explicit unified and non-unified path
  loading and report-step count validation.
- `RestartService.load_restarts_from_paths(...)` and public
  `load_restarts_from_paths(...)` added for explicit formatted restart paths,
  including report-step hints for non-unified files.
- Focused M25 restart tests added for explicit unified/non-unified paths,
  requested-report filtering, and report-step count validation.
- `PropertyCollection.has_property(...)` now recognizes lazy properties, and
  `select(...)` preserves lazy property loaders.
- Focused M26 tests added for lazy property selection and lazy name visibility.
- `WellDataset` now supports case-insensitive existence checks, wildcard name
  filtering, and selected timeline datasets.
- Focused M27 tests added in the formatted well workflow.
- `RftDataset` now exposes record types, filtered record lists, and selected
  sub-datasets by well/date/type without loading measurements.
- Focused M28 tests added in the formatted RFT/PLT workflow.
- `GridPropertyService.load_grid_from_path(...)`,
  `load_properties_from_path(...)`, and public grid/property facade helpers now
  load supported formatted grid and INIT/property files from explicit paths.
- Focused M29 tests added for explicit grid/INIT path loading and public root
  facade exports.
- `SummaryDataset.rows(...)` added as the public row API used by summary CSV and
  optional pandas export.
- Focused M30 assertions added for summary row schemas.
- `RestartDataset.timeline_rows()` and `to_csv(...)` added for restart report
  metadata timelines without loading keyword payloads.
- Focused M31 tests added for restart timeline rows and CSV.
- `WellDataset.rows()` and `to_csv(...)` added for flattened well snapshot
  metadata, counts, and rate columns.
- Focused M32 tests added for well snapshot rows and CSV.
- `RftDataset.header_rows()` and `to_csv(...)` added for RFT/PLT record metadata
  while preserving lazy measurement loading.
- Focused M33 tests added for RFT/PLT header rows, CSV, and measurement-loaded
  state.
- `PropertyCollection.materialize(...)` added for explicit eager materialization
  of all or selected lazy properties.
- Focused M34 tests added for selected lazy property materialization.
- `DeckMetadata.keyword_count(...)` and `unique_keyword_names()` added for
  syntactic deck keyword occurrence inspection.
- Focused M35 tests added for duplicate keyword counts and unique-name order.
- `FormatDetectionResult.format_label`, `diagnostic_summary()`, and
  `require_formatted(...)` added for reusable detection diagnostics and
  formatted-only guard checks.
- Focused M36 tests added for detection diagnostics and formatted requirement
  errors.
- `SummaryVector.value_at_time_index(...)`, `value_at_simulation_days(...)`,
  and `value_at_date(...)` added for exact value lookup over stored axes.
- Focused M37 assertions added for exact summary vector value lookup.
- `RestartReport.keyword_names()`, `has_keyword(...)`, and `properties(...)`
  added for report keyword availability and selected keyword-backed property
  collections.
- Focused M38 tests added for restart keyword listing, existence checks, and
  report property collections.
- `WellDataset.connection_rows()` and `connections_to_csv(...)` added for
  supported formatted well connection metadata exports.
- Focused M39 tests added for connection rows and CSV headers.
- `WellDataset.segment_rows()` and `segments_to_csv(...)` added for supported
  formatted well segment metadata exports.
- Focused M40 tests added for segment rows and CSV headers.
- `RftRecord.measurement_rows()` and `measurements_to_csv(...)` added for
  record-level RFT/PLT measurement exports.
- Focused M41 tests added for record measurement rows.
- `RftDataset.measurement_rows(...)` and `measurements_to_csv(...)` added for
  filtered dataset-level RFT/PLT measurement exports.
- Focused M42 tests added for dataset measurement rows and CSV headers.
- `SummaryDataset.time_axis_rows()` and `time_axis_to_csv(...)` added for
  summary time-axis metadata export without loading vectors.
- Focused M43 tests added for time-axis rows and CSV.
- `SummaryDataset.vector_metadata_rows()` and `vector_metadata_to_csv(...)`
  added for summary vector metadata and loaded-state export.
- Focused M44 tests added for vector metadata rows and CSV.
- `SummaryVector.rows()`, `to_csv(...)`, and `statistics()` added for
  per-vector long-form export and basic numeric statistics.
- Focused M45 summary-vector tests added for rows, CSV, and statistics.
- `SummaryDataset.select_by_filter(...)` added to combine existing key filtering
  with lazy dataset selection.
- Focused M46 tests added for filtered summary dataset selection.
- `RestartDataset.select_report_steps(...)` added for selecting report subsets
  after load.
- Focused M47 tests added for restart report-step selection.
- `RestartReport.keyword_rows()` and `keywords_to_csv(...)` added for report
  payload keyword metadata export.
- Focused M48 tests added for restart keyword rows and CSV.
- `KeywordDataset.unique_names()` and `keyword_count(...)` added for syntactic
  keyword occurrence inspection.
- Focused M49 tests added for keyword counts and unique names.
- `KeywordDataset.rows()` and `to_csv(...)` added for keyword metadata row
  exports.
- Focused M50 tests added for keyword rows and CSV.
- `PropertyCollection.metadata_rows()` and `metadata_to_csv(...)` added for
  property metadata export without forcing lazy property loading.
- Focused M51 tests added for lazy property metadata rows and CSV.
- `CaseManifest.file_rows()` and `files_to_csv(...)` added for discovery file
  rows and CSV export.
- `FormatDetectionResult.to_row()` added as the per-detection row contract.
- `SimulationCase.file_rows()` and `files_to_csv(...)` added as public discovery
  row exports.
- Focused M52-M54 tests added for detection, manifest, and public case file
  rows/CSV.
- `ReservoirGrid.cells()`, `active_cells()`, and `inactive_cells()` added for
  stable cell iteration.
- `ReservoirGrid.cell_rows()` added for lightweight domain-level cell metadata
  rows.
- `GridGeometry.depth_range()`, `thickness_range()`, and `cell_depth_rows()`
  added for lightweight ZCORN-derived geometry inspection.
- Focused M55-M58 grid-domain tests added for cell iteration, cell rows, depth
  ranges, and geometry depth rows.

## Work In Progress

- None for M58.

## Next Planned Task

M59: Optional pandas DataFrame boundaries for the newly added summary metadata,
well connection/segment, RFT measurement, keyword/property metadata, discovery,
and lightweight grid row helpers, keeping pandas optional and isolated.

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
- Broad cache/index support beyond formatted summary indexes and opt-in
  checksum fingerprints.
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
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_units_phase.py tests/test_public_facades.py`
  succeeded: 7 passed in 0.62s during M15 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_report_queries.py tests/test_restart_reader.py tests/test_summary_reader.py tests/test_well_rft_reader.py tests/test_public_facades.py`
  succeeded: 23 passed in 0.72s during M16 validation after correcting a test
  fixture constructor.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_deck_metadata.py tests/test_file_detection.py tests/test_case_discovery.py`
  succeeded: 28 passed in 0.64s during M17 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_export_service.py tests/test_public_facades.py`
  succeeded: 10 passed in 0.45s during M18 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_summary_resampling.py tests/test_summary_reader.py tests/test_public_facades.py`
  succeeded: 11 passed in 0.51s during M19 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_lazy_cache_hardening.py`
  succeeded: 6 passed in 0.55s during M20 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 108 passed and
  1 skipped in 1.30s after M20. The skipped test remains the optional NumPy
  array conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_payload_format_contracts.py tests/test_file_detection.py tests/test_case_discovery.py tests/test_formatted_keyword_reader.py`
  succeeded: 32 passed in 0.54s during M21 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_keyword_dataset.py`
  succeeded: 5 passed in 0.17s during M22 validation after correcting the
  occurrence-index expectation in the new test.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_grid_domain.py`
  succeeded: 6 passed and 1 skipped in 0.22s during M23 validation after
  making test property layouts explicit.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_summary_reader.py tests/test_public_facades.py`
  succeeded: 10 passed in 0.44s during M24 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_restart_reader.py tests/test_public_facades.py`
  succeeded: 11 passed in 0.47s during M25 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_lazy_cache_hardening.py tests/test_grid_init_readers.py`
  succeeded: 12 passed in 0.44s during M26 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_well_rft_reader.py`
  succeeded: 7 passed in 0.34s during M27 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_well_rft_reader.py`
  succeeded: 7 passed in 0.30s during M28 validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 123 passed and
  1 skipped in 1.28s after M28. The skipped test remains the optional NumPy
  array conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_grid_init_readers.py tests/test_summary_reader.py tests/test_restart_reader.py tests/test_well_rft_reader.py tests/test_deck_metadata.py tests/test_payload_format_contracts.py tests/test_summary_resampling.py`
  succeeded: 46 passed in 1.18s during M29-M38 focused validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 127 passed and
  1 skipped in 1.53s after M38. The skipped test remains the optional NumPy
  array conversion path because NumPy is not installed in this environment.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_well_rft_reader.py tests/test_summary_reader.py tests/test_restart_reader.py tests/test_keyword_dataset.py tests/test_lazy_cache_hardening.py tests/test_file_detection.py tests/test_case_discovery.py tests/test_grid_domain.py`
  failed initially: 1 failed, 66 passed, 1 skipped because a test expected a
  field summary vector to carry a qualifier kind.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/test_well_rft_reader.py tests/test_summary_reader.py tests/test_restart_reader.py tests/test_keyword_dataset.py tests/test_lazy_cache_hardening.py tests/test_file_detection.py tests/test_case_discovery.py tests/test_grid_domain.py`
  succeeded: 67 passed and 1 skipped in 1.04s during M39-M58 focused validation.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest` succeeded: 128 passed and
  1 skipped in 1.56s after M58. The skipped test remains the optional NumPy
  array conversion path because NumPy is not installed in this environment.

## Known Limitations

- Only GRDECL text keyword payloads are parsed.
- Discovery is filename-based by default. Opt-in payload sniffing can refine
  obvious formatted text versus binary-looking files but does not decode
  simulator-specific binary payloads.
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
- Summary vector resampling supports generic linear and stepwise interpolation
  by simulation day. Simulator-specific rate/cumulative resampling rules remain
  deferred.
- pandas and NumPy are optional. Summary and grid/property DataFrame export
  methods raise explicit `UnsupportedFormatError` messages when the optional
  dependency is absent.
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
- Cache invalidation uses resolved source path, size, and `mtime_ns` by default;
  opt-in SHA-256 source checksums are available for stronger cache fingerprints.
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
- Property CSV/DataFrame export is long-form row output for supported loaded
  properties. It does not yet provide unit conversion, wide pivoted property
  tables, or simulator-specific table schemas.
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
- Unit-system and phase value objects normalize labels only. Unit conversion and
  phase-specific simulator semantics remain deferred.
- Deck metadata support is limited to formatted GRDECL-style `.DATA` text and
  extracts only `TITLE`, `START`, keyword names, and source path. Full deck
  semantic validation, schedule editing, includes, and broad deck writing remain
  out of scope.
- Nearest report/time query behavior breaks ties by earliest sequence/time-axis
  index and does not infer simulator-specific date/time precision beyond stored
  `date` values.
- Explicit summary and restart path-loading helpers assume formatted keyword
  text. Non-unified explicit paths require caller-provided report-step hints
  when the files omit report-step metadata.
- Explicit grid and INIT/property path-loading helpers assume formatted keyword
  text and reuse the existing validated readers only.
- Summary, restart, well, and RFT/PLT row/CSV helpers expose scoped metadata or
  already-supported values only; they do not add simulator-specific table
  schemas.
- Restart timeline CSV does not materialize keyword payloads.
- Well snapshot CSV does not export connection-level or segment-level child
  rows yet.
- RFT/PLT header CSV does not export cell measurement rows yet.
- Property collection materialization is explicit eager loading through the
  existing lazy loaders; it is not byte-offset streaming or memory mapping.
- Deck keyword count helpers are syntactic over parsed keyword names and do not
  infer deck section semantics.
- Detection diagnostic helpers summarize existing detection state and enforce
  formatted-only contracts; they do not decode binary payloads.
- Summary vector day/date lookup helpers require exact stored axis values.
- Restart report property collections wrap selected keywords as properties and
  do not add restart payload table export.
- Well connection and segment row exports flatten existing scoped formatted well
  objects only; they do not add new restart well record semantics.
- RFT/PLT measurement rows intentionally materialize matching lazy measurements
  and do not add measurement indexes or binary decoding.
- Summary time-axis and vector metadata rows expose stored formatted summary
  metadata only; complete vector-classification guarantees remain deferred.
- Restart keyword metadata rows intentionally load the selected report payload
  and do not export full keyword values.
- Keyword and property metadata CSV exports are metadata-only; property metadata
  rows do not force lazy property loading.
- Manifest and public case file rows expose discovery metadata only and do not
  parse payloads.
- Grid cell iteration and cell/depth rows use the existing lightweight
  ZCORN-derived geometry metrics and do not expose full XYZ corners, volumes,
  spatial lookup, local grids, dual grids, or NNC metadata.
- Keyword block extraction is syntactic and does not validate deck section
  semantics.
- Grid cell corner access exposes stored ZCORN depths only; full XYZ corners and
  volume calculations remain unsupported.

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
- M15 treats unit systems and phases as normalized metadata labels only; no unit
  conversion or phase-dependent interpretation is inferred.
- M16 treats nearest report/time matching as a generic absolute-distance policy
  over stored report steps, simulation days, or report dates.
- M17 treats `.DATA` decks as formatted keyword text and extracts only metadata
  that can be validated without full deck semantic interpretation.
- M18 treats pandas DataFrame export as an optional boundary over the same row
  schema already validated for grid/property CSV export.
- M19 treats linear and stepwise summary interpolation as generic numeric
  methods until simulator-specific rate/cumulative rules are independently
  verified.
- M20 keeps path/size/mtime cache invalidation as the default fast contract and
  makes SHA-256 checksums explicit opt-in hardening.
- M21 keeps payload sniffing opt-in because discovery should remain cheap and
  because sniffing only detects obvious text/binary-looking payloads.
- M22 treats keyword blocks as ordered syntactic slices, not semantic deck
  sections.
- M23 exposes stored ZCORN corner depths and property delegation while keeping
  full corner-point geometry out of scope.
- M24 treats explicit summary paths as formatted keyword text and uses
  caller-provided report-step hints for non-unified data without `REPORTS`.
- M25 treats explicit restart paths as formatted keyword text and uses
  caller-provided report-step hints for non-unified files without `REPORT`.
- M26 preserves lazy property loaders when selecting property subsets.
- M27 keeps well filtering at the dataset/timeline name layer and does not add
  new restart well record semantics.
- M28 filters RFT/PLT record headers only and does not materialize measurement
  payloads during selection.
- M29 treats explicit grid/INIT paths as formatted keyword text and does not
  infer arbitrary multi-file case context from those paths.
- M30 treats summary rows as the same row schema used by summary CSV/pandas
  export.
- M31 treats restart timeline export as report metadata only.
- M32 treats well rows as snapshot-level exports with discovered rate columns.
- M33 treats RFT/PLT rows as record-header exports and keeps measurements lazy.
- M34 treats property materialization as an explicit conversion from lazy
  loaders to an eager collection.
- M35 treats deck keyword counts as syntactic occurrence counts.
- M36 treats detection diagnostics as convenience helpers over existing
  detection state, not stronger payload compatibility guarantees.
- M37 treats summary vector date/day lookup as exact matching over stored axes.
- M38 treats restart report property collections as keyword-backed convenience
  wrappers, not a new restart table/export subsystem.
- M39 treats well connection rows as flattened existing `WellConnection`
  objects, not a broader restart well parser.
- M40 treats well segment rows as flattened existing `WellSegment` objects and
  does not infer full segment topology.
- M41 treats RFT record measurement rows as an explicit payload materialization
  operation.
- M42 treats RFT dataset measurement rows as filtered aggregation over record
  measurement rows.
- M43 treats summary time-axis rows as stored date/report-step/day metadata.
- M44 treats summary vector metadata rows as stored metadata and loaded-state
  diagnostics.
- M45 treats summary vector rows as long-form exports for one vector.
- M46 treats summary filtered selection as a wrapper around existing key filters.
- M47 treats restart report-step selection as an in-memory subset operation.
- M48 treats restart keyword metadata rows as a report-payload inspection helper.
- M49 treats keyword counts as syntactic occurrence counts.
- M50 treats keyword dataset rows as metadata-only rows.
- M51 treats property metadata rows as lazy-state diagnostics.
- M52 treats manifest file rows as discovery diagnostics.
- M53 treats detection result rows as a stable tabular representation of
  existing detection state.
- M54 treats public case file rows as manifest rows exposed through the case
  facade.
- M55 treats grid cell iteration as materialized lightweight cell views.
- M56 treats grid cell rows as lightweight domain rows, not full geometry tables.
- M57 treats depth and thickness ranges as ZCORN-derived metrics.
- M58 treats geometry depth rows as top/bottom/depth/thickness summaries only.
