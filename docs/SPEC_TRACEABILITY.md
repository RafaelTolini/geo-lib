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
| Project scaffold | implemented | `pyproject.toml`, README, `.gitignore`, `src/` package, typed package marker, and test configuration exist. | `python -m pytest`: latest run 128 passed, 1 skipped. |
| Package structure | partially_implemented | Layered folders exist for public, application, domain, formats, infrastructure, binary I/O, text I/O, caching, schemas, exceptions, keyword, grid, property, restart, summary, well, RFT/PLT, units, deck metadata, and export workflows. Public facade modules now exist for grid, property, restart, summary, well, RFT/PLT, deck, and units workflows. Deeper binary adapters and broad simulator-specific packages are not all created yet. | Import, facade, infrastructure, reader, restart, summary, well, RFT, deck, units, cache, and export tests passed. |
| Exceptions | implemented | Explicit exception hierarchy exists in `reservoir_data.exceptions.errors`. | Error-path tests passed for discovery, missing files, and unsupported workflows. |
| Schemas/value objects | partially_implemented | `LoadCaseOptions` now includes opt-in payload sniffing, and `GridLoadOptions`, `RestartLoadOptions`, `SummaryLoadOptions`, `FormatDetectionResult`, `FileCategory`, `FileFormat`, `KeywordQuery`, `ReportStepQuery`, `ReportStepMatchPolicy`, `SummaryKey`, `SummaryInterpolationMethod`, `UnitSystem`, `Phase`, `PropertyExportOptions`, `GridTableExportOptions`, `PropertyTableExportOptions`, `GridDimensions`, and `CellIndex` exist. `FormatDetectionResult` also exposes diagnostic labels/summaries, formatted-file requirement checks, and row conversion for discovery tables. Some advanced option fields intentionally raise unsupported errors until their underlying behaviors exist. | Detection, payload sniffing, category-filter, keyword query, exact/nearest report query, summary query/filter, grid index, units/phase, load option, and export option tests passed. |
| Public API/facade | partially_implemented | `SimulationCase.open`, discovery helpers, file rows/CSV, `load_deck_metadata`, `load_grid`, `load_properties`, `load_restarts`, `load_summary`, `load_wells`, `load_rft`, `export_grid_grdecl`, `export_grid_cell_csv`, `export_properties_grdecl`, `export_properties_csv`, `grid_cell_dataframe`, and `properties_dataframe` are implemented for supported formatted keyword files and optional pandas boundaries. Public grid/property/summary/restart facades expose explicit formatted path-loading helpers. Thin public facade modules expose implemented deck, grid, property, restart, summary, well, RFT/PLT, and units domain objects and option schemas. Broad binary/vendor-specific workflows still raise explicit unsupported errors. | Facade import, explicit path loading, deck metadata, load option, DataFrame boundary, discovery row, and export tests passed. |
| DATA deck metadata | partially_implemented | `DeckMetadata`, `FormattedDeckReader`, `DeckService`, and `SimulationCase.load_deck_metadata()` extract supported `TITLE`, `START`, keyword names, keyword counts, unique keyword names, and source path from formatted GRDECL-style `.DATA` decks. Full deck semantic validation, include expansion, schedule editing, and deck writing remain out of scope. | Deck metadata tests passed. |
| Case discovery | partially_implemented | Basename, explicit-file, and unambiguous-directory discovery are implemented. Manifest and public case file rows/CSV expose discovered files and detection diagnostics without payload loading. Deeper naming policy configuration and exact simulator convention coverage remain later work. | Discovery and file-row tests passed. |
| File type detection | partially_implemented | Extension-based detection exists for main categories plus conservative non-unified step patterns. Opt-in payload sniffing can refine obvious formatted text versus binary-looking payloads for ambiguous files and report conflicts for known formatted/unformatted extensions. Detection results expose format labels, diagnostic summaries, formatted-only guard checks, and tabular rows. | Detection and payload sniffing tests passed. |
| GRDECL parser | implemented | Text tokenizer, parser, and reader handle comments, whitespace, slash terminators, quoted strings, logicals, numeric values, repeat syntax, and strict unterminated-record errors. | GRDECL tests passed. |
| Keyword records/datasets | implemented | `KeywordRecord`, `KeywordDataset`, `KeywordType`, and `KeywordQuery` provide occurrence-aware retrieval, syntactic block extraction, type/size validation, numeric tuple conversion, optional NumPy conversion, missing errors, ambiguous-query errors, occurrence counts, unique names, metadata rows, and CSV export. | Keyword dataset and NumPy boundary tests passed. |
| Grid domain model | partially_implemented | Core structured-grid dimensions, cell indexes, grid cells, reservoir grid access, all/active/inactive cell iteration, optional unit-system metadata, geometry array validation, stored corner-depth access, grid-cell property evaluation, lightweight depth/top/bottom/thickness behavior, depth/thickness ranges, and geometry depth rows are implemented. `ExportService` can export supported grid cell metadata to tabular rows/CSV and optional pandas DataFrames. Full corner-point reconstruction, volume, spatial lookup, local grids, dual grids, and NNC remain later work. | Grid domain, units, grid table CSV, lightweight geometry, and optional DataFrame export tests passed. |
| GRID/EGRID reader | partially_implemented | `GridReader` loads minimal formatted GRDECL-style GRID/EGRID keyword files into `ReservoirGrid`, and `ExportService` can write the supported geometry subset back to GRDECL text. Binary simulator GRID/EGRID keyword payload decoding, full geometry reconstruction, local grids, dual grids, and NNC remain pending. | Minimal grid reader and grid export round-trip tests passed. |
| INIT/property loading | partially_implemented | `InitReader`, `GridProperty`, and `PropertyCollection` load selected formatted INIT/property keywords and classify active/global layout when a compatible grid is provided. Public case loading and explicit path facades can index selected formatted INIT properties lazily, materialize one property on demand, select lazy subsets, explicitly materialize selected lazy collections, and export property metadata rows without forcing lazy loads. `GridProperty` exposes numeric tuple and optional NumPy boundaries for native, active, and global layouts. `ExportService` can export selected properties in native, active, or global GRDECL layout plus long-form CSV/table rows and optional pandas DataFrames. Binary INIT decoding, byte-offset indexing, unit conversion, and broad writer behavior remain pending. | INIT reader/property, explicit path loading, lazy property selection/materialization, property metadata rows, NumPy boundary, and property export/DataFrame tests passed. |
| Active/global mapping | implemented | `ActiveCellMap` converts active-sized sequences to global-sized values, compresses global-sized sequences, validates shapes, and includes optional NumPy-array paths. | Sequence tests passed; NumPy-specific test skipped because NumPy is not installed. |
| Binary record infrastructure | implemented | `FortranRecordReader` reads length-prefixed records with configurable endian order, validates leading/trailing markers, reports truncation, and provides simple endian detection. | Binary I/O tests passed. |
| Formatted/unformatted keyword files | partially_implemented | Common formatted text keyword reader is implemented for GRDECL-style records and now backs minimal GRID/EGRID/INIT readers. Unformatted low-level record framing is implemented, but simulator-specific binary keyword payload decoding is not implemented yet. | Formatted reader, grid/init reader, and formatted/unformatted mismatch tests passed. |
| Unified/non-unified handling | partially_implemented | Detection records unified flags and report steps for supported filename patterns. Formatted restart and summary reader/services now index formatted unified files and formatted non-unified report-step files. Binary restart/summary grouping remains pending. | Detection, manifest, restart grouping, and summary grouping tests passed. |
| Restart dataset/reports | partially_implemented | `RestartHeader`, `RestartReport`, `RestartDataset`, `FormattedRestartReader`, and `RestartService` support formatted restart report indexing from case discovery or explicit paths, lazy payload loading, exact and nearest report lookup, report-step subset selection, timeline rows/CSV, keyword listing/existence checks, keyword metadata rows/CSV, grid property mapping, selected keyword property collections, requested-report filtering, and eager payload materialization when requested. Binary restart keyword decoding, complete metadata semantics, well extraction through restart load options, and writing remain pending. | Restart, explicit restart path, report query, timeline/keyword CSV, and restart load option tests passed. |
| Summary dataset/vectors | partially_implemented | `SummaryKey`, `SummaryMetadata`, `SummaryVector`, `SummaryDataset`, `FormattedSummaryReader`, and `SummaryService` support formatted summary metadata from case discovery or explicit metadata/data paths, time axes, time-axis rows/CSV, vector metadata rows/CSV, lazy/eager vector loading, vector-filtered datasets, filter-based selection, filtering, exact/nearest time-axis lookup, exact vector values by report step/time index/day/date, generic linear/stepwise interpolation and resampling, vector statistics, row/CSV export, and optional NumPy/pandas export boundaries. Binary `SMSPEC`/`UNSMRY` decoding, complete vector classification guarantees, alternate key/time policies, simulator-specific rate/cumulative rules, and summary writing remain pending. | Summary, explicit summary path, summary resampling, report query, row/CSV, metadata CSV, and summary load option tests passed. |
| RFT/PLT data | partially_implemented | `RftDataset`, `RftRecord`, `RftCellMeasurement`, `FormattedRftReader`, and `RftService` support formatted GRDECL-style RFT/PLT records, well/date/type query, record-type listing, header-level filtering/selection, header rows/CSV, lazy measurement loading, measurement rows/CSV, pressures, depths, saturations, and phase rates. Binary/unformatted RFT/PLT and vendor-specific record variants remain pending. | RFT/PLT tests passed. |
| Well timelines/states/connections/segments | partially_implemented | `WellDataset`, `WellTimeline`, `WellSnapshot`, `WellConnection`, `WellSegment`, `FormattedWellReader`, and `WellService` support well timelines from scoped formatted restart records, exact/nearest typed timeline queries, well existence checks, wildcard filtering, selected timeline datasets, flattened snapshot rows/CSV, connection rows/CSV, segment rows/CSV, open state, type, rates, grid cell connections, grid validation, and optional segment loading. Complete restart well record extraction and multi-segment semantics remain pending. | Well timeline, filtering, rows/CSV, and report query tests passed. |
| Lazy loading | partially_implemented | Case open still avoids payload parsing, formatted restart report payloads are parsed lazily after header indexing, formatted summary vectors are loaded lazily after metadata/time-axis indexing, formatted INIT properties can be materialized one property at a time, selected without eager loading, and explicitly materialized as an eager collection, and formatted RFT/PLT measurements are loaded lazily after record headers. Binary restart payloads, memory-mapped/chunked readers, and broad cache-backed lazy loading remain later work. | Restart, summary, INIT property selection/materialization, and RFT lazy payload tests passed. |
| NumPy integration | partially_implemented | `ActiveCellMap` has optional NumPy array expansion/compression when NumPy is available. `KeywordRecord.to_numpy()`, `GridProperty.to_numpy()`, `SummaryVector.to_numpy()`, and `SummaryDataset.to_numpy()` provide optional NumPy export boundaries. Mutable shared-view semantics, memory-mapped arrays, and broader binary numeric buffers remain later work. | NumPy active-map test is present but skipped in this environment because NumPy is not installed; keyword/property/summary NumPy boundary tests pass by exercising optional conversion when available or explicit missing-dependency errors when absent. |
| pandas/CSV export | partially_implemented | `SummaryDataset.rows()`/`to_csv()`, summary time-axis/vector metadata CSV, and `SummaryVector.to_csv()` are implemented with the standard library, and `to_pandas()` provides an optional pandas boundary with explicit missing-dependency errors. `RestartDataset`, `RestartReport`, `WellDataset`, `RftRecord`, `RftDataset`, `KeywordDataset`, `PropertyCollection`, `CaseManifest`, and `SimulationCase` expose scoped row/CSV exports. `ExportService` writes supported grid cell metadata and selected grid properties as CSV and can expose the same grid/property row schemas as optional pandas DataFrames. | Summary CSV, restart/well/RFT/keyword/property/discovery CSV, optional pandas boundary, grid/property CSV, and grid/property DataFrame export tests passed. |
| Selective writers/export | partially_implemented | `GrdeclWriter` and `ExportService` support tested GRDECL text export for supported grid geometry and selected properties. `ExportService` also supports tabular grid/property rows and CSV. Public case methods expose grid/property GRDECL and CSV export. Full deck writing, restart/summary rewriting, binary writers, and broad simulator-format writing remain pending/deferred. | GRDECL formatting, grid/property round-trip export, and grid/property CSV tests passed. |
| Error handling | partially_implemented | Discovery, facade, keyword query, GRDECL parse/read, grid index, grid geometry, active-map shape, property shape, missing property, invalid report step, restart parse, summary metadata/data, well data, RFT/PLT data, binary record, endian detection, formatted keyword mismatch, and unsupported advanced load-option errors are implemented; later parser/domain errors remain pending. | Error and load option tests passed. |
| Large-file behavior | partially_implemented | Opening a case uses filenames only and avoids payload loading. Summary index caches can avoid repeated metadata/time-axis parsing, formatted INIT properties can defer value materialization, and existing restart/summary/RFT objects keep payloads lazy. Cache source fingerprints can opt into SHA-256 checksums. Memory mapping and chunked binary/text readers remain pending. | Discovery, lazy property, lazy payload, checksum fingerprint, and cache invalidation tests passed. |
| Cache/index support | partially_implemented | `SourceFingerprint` and `JsonIndexCache` provide optional JSON index cache files invalidated by resolved path, size, modification time, and opt-in SHA-256 checksums. Formatted summary loading can persist and reuse metadata/time-axis/vector-key indexes via `LoadCaseOptions.cache_policy`. Cache support for restart, INIT byte offsets, RFT, and binary payload readers remains pending. | Cache hit/miss, checksum source fingerprint, and source invalidation tests passed. |
| Tests | partially_implemented | M1 through M58 tests exist for foundation, keyword, GRDECL, grid, active-map, binary I/O, formatted keyword, GRID/EGRID, INIT, property, formatted restart, formatted summary, well timeline, formatted RFT/PLT, lazy property loading/selection/materialization, summary cache behavior, GRDECL export behavior, tabular grid/property export/DataFrame behavior, scoped load option behavior, keyword/property NumPy boundaries, public facade imports, units/phase, exact/nearest report queries, deck metadata, summary resampling methods, checksum cache fingerprints, payload sniffing, keyword blocks, grid-cell property evaluation, explicit grid/INIT/summary/restart path loading, dataset row/CSV exports, summary exact value lookup, restart report helpers, well/RFT filtering, connection/segment/measurement exports, discovery rows, keyword/property metadata rows, and lightweight grid cell/depth helpers. Full black-box test plan remains pending. | `python -m pytest`: 128 passed, 1 skipped. |

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
- M5 GRID/EGRID and INIT readers intentionally support formatted GRDECL-style
  keyword content only. Binary simulator keyword payload decoding remains pending
  until independently validated fixtures or documentation are available.
- M6 restart support intentionally covers formatted GRDECL-style restart
  fixtures only. A `REPORT` keyword starts each formatted unified report block;
  formatted non-unified files may use the filename report step when `REPORT` is
  absent.
- M7 summary support intentionally covers formatted GRDECL-style summary
  fixtures only. Metadata uses `VECTOR` records, data uses `TIME`, `DATES`,
  optional `REPORTS`, and lazy `VALUES` records. Generic vector resampling is
  configurable between linear and stepwise behavior, while simulator-specific
  rate/cumulative behavior remains independently verified future work.
- M8 well support intentionally covers formatted restart payload fixtures with
  `WELL`, `WCONN`, `WRATE`, and `WSEG` records. RFT/PLT support intentionally
  covers formatted text fixtures with `RFTREC`, `RFTCELL`, and `PLTCELL`
  records. These are scoped validation contracts, not simulator compatibility
  guarantees for binary or vendor-specific output.
- M9 cache support starts with formatted summary indexes. Cache invalidation is
  based on resolved path, file size, and `mtime_ns`. Formatted INIT lazy loading
  indexes keyword records and defers `GridProperty` materialization, but does
  not yet provide byte-offset streaming for huge text arrays.
- M10 writer support intentionally covers only GRDECL-style text exports for
  the grid geometry/property subset already supported by readers. It is not a
  full deck writer, restart writer, summary writer, or binary writer.
- M11 tabular export intentionally covers standard-library CSV/row output and
  optional pandas DataFrame boundaries for supported loaded grid cells and
  properties. It uses existing lightweight ZCORN-derived top/bottom/depth/
  thickness values and does not claim full corner-point XYZ reconstruction,
  volume calculations, unit conversion, local-grid/NNC tables, or
  simulator-specific table schemas.
- M12 load options intentionally provide typed contracts and enforcement for the
  supported formatted-reader workflows. Options whose underlying behavior is not
  implemented raise `UnsupportedFormatError` rather than being silently ignored.
- M13 NumPy boundary support intentionally keeps NumPy optional. Tuple-backed
  keyword and property values produce copied arrays when NumPy is available and
  raise explicit missing-dependency errors when it is absent.
- M14 public facade modules intentionally re-export implemented domain/result
  objects and DTOs only. They do not add compatibility aliases or expose
  low-level parser/binary internals.
- M15 unit-system and phase support intentionally normalizes metadata labels
  only. Unit conversion and phase-dependent simulator semantics remain deferred.
- M16 nearest report/time matching is a generic absolute-distance policy over
  stored report steps, simulation days, or report dates, with ties resolved by
  earliest sequence/time-axis index.
- M17 `.DATA` deck metadata support intentionally parses formatted keyword text
  only and extracts externally useful metadata without full deck semantics.
- M18 pandas DataFrame export intentionally reuses the same row schema as the
  validated grid/property CSV exports and keeps pandas optional.
- M19 summary interpolation methods are generic numeric policies. Rate versus
  cumulative resampling remains independently verified future work.
- M20 SHA-256 fingerprints are opt-in cache hardening; path, size, and
  `mtime_ns` remain the default cache source identity contract.
- M21 payload sniffing is opt-in and only detects obvious formatted text versus
  binary-looking payloads; it is not a binary decoder.
- M22 keyword block extraction is syntactic and occurrence-based, not simulator
  deck section validation.
- M23 grid cell corner-depth access exposes stored ZCORN depth values only;
  full XYZ corners and volumes remain deferred.
- M24 explicit summary path loading assumes formatted keyword text and requires
  report-step hints for non-unified files that omit a `REPORTS` axis.
- M25 explicit restart path loading assumes formatted keyword text and requires
  report-step hints for non-unified files that omit `REPORT`.
- M26 property collection selection preserves lazy loaders rather than forcing
  materialization.
- M27 well filtering operates on normalized timeline names only and adds no new
  restart well record semantics.
- M28 RFT/PLT filtering operates on eager record headers and does not load cell
  measurements.
- M29 explicit grid/INIT path loading assumes formatted keyword text and reuses
  the existing validated `GridReader` and `InitReader` only.
- M30 summary rows intentionally expose the same wide row schema already used
  by summary CSV/pandas export.
- M31 restart timeline rows intentionally include report metadata only and do
  not materialize restart keyword payloads.
- M32 well rows intentionally flatten snapshot-level state and rates only; they
  do not export connection- or segment-level child tables.
- M33 RFT/PLT header rows intentionally expose record metadata and lazy-loaded
  state without materializing measurements.
- M34 property collection materialization is explicit and still uses the
  existing lazy loaders; it is not byte-offset streaming.
- M35 deck keyword count helpers operate on the syntactic keyword-name list and
  do not infer deck section semantics.
- M36 detection diagnostics summarize existing detection results and enforce
  formatted-only contracts; they are not binary decoders.
- M37 summary vector day/date lookup is exact over stored axes; tolerance and
  calendar-frequency behavior remain deferred.
- M38 restart report property collections are keyword-backed convenience
  wrappers and do not add restart payload table export or binary decoding.
- M39 well connection rows flatten existing scoped `WellConnection` objects and
  add no new restart well record semantics.
- M40 well segment rows flatten existing scoped `WellSegment` objects and do
  not infer full multi-segment topology.
- M41 RFT/PLT record measurement rows intentionally materialize one record's
  lazy measurements.
- M42 RFT/PLT dataset measurement rows intentionally materialize matching
  record measurements and do not create measurement indexes.
- M43 summary time-axis rows operate only on stored date/report-step/day axes.
- M44 summary vector metadata rows expose stored metadata and loaded state, not
  independently verified full vector classification semantics.
- M45 summary vector rows are long-form value exports for one already loaded
  vector.
- M46 summary filtered selection reuses existing wildcard and qualifier filters.
- M47 restart report-step selection operates on already loaded report indexes.
- M48 restart report keyword rows expose payload metadata and therefore load
  that report's keyword dataset.
- M49 keyword dataset counts are syntactic occurrence counts.
- M50 keyword dataset rows are metadata rows and do not expand full values.
- M51 property metadata rows do not force lazy property loading.
- M52 manifest file rows are discovery metadata only and do not read payloads.
- M53 detection result rows summarize existing detection state.
- M54 public case file rows delegate to the manifest and do not read payloads.
- M55 grid cell iteration materializes lightweight `GridCell` views, not lazy
  geometry arrays.
- M56 grid cell rows reuse stored ZCORN-derived depth metrics only.
- M57 depth/thickness ranges use stored ZCORN-derived values, not full
  coordinate geometry.
- M58 geometry depth rows expose top/bottom/depth/thickness only and do not
  expose XYZ corners or volumes.
