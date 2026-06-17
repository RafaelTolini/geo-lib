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
| Project scaffold | implemented | `pyproject.toml`, README, `.gitignore`, `src/` package, typed package marker, and test configuration exist. | `python -m pytest`: latest run 88 passed, 1 skipped. |
| Package structure | partially_implemented | Layered folders exist for public, application, domain, formats, infrastructure, binary I/O, text I/O, caching, schemas, exceptions, keyword, grid, property, restart, summary, well, RFT/PLT, and export workflows. Public facade modules now exist for grid, property, restart, summary, well, and RFT/PLT workflows. Domain-specific future modules such as units and deeper binary adapters are not all created yet. | Import, facade, infrastructure, reader, restart, summary, well, RFT, cache, and export tests passed. |
| Exceptions | implemented | Explicit exception hierarchy exists in `reservoir_data.exceptions.errors`. | Error-path tests passed for discovery, missing files, and unsupported workflows. |
| Schemas/value objects | partially_implemented | `LoadCaseOptions`, `GridLoadOptions`, `RestartLoadOptions`, `SummaryLoadOptions`, `FormatDetectionResult`, `FileCategory`, `FileFormat`, `KeywordQuery`, `ReportStepQuery`, `SummaryKey`, `PropertyExportOptions`, `GridTableExportOptions`, `PropertyTableExportOptions`, `GridDimensions`, and `CellIndex` exist. Some advanced option fields intentionally raise unsupported errors until their underlying behaviors exist. | Detection, category-filter, keyword query, report query, summary query/filter, grid index, load option, and export option tests passed. |
| Public API/facade | partially_implemented | `SimulationCase.open`, discovery helpers, `load_grid`, `load_properties`, `load_restarts`, `load_summary`, `load_wells`, `load_rft`, `export_grid_grdecl`, `export_grid_cell_csv`, `export_properties_grdecl`, and `export_properties_csv` are implemented for supported formatted keyword files. Thin public facade modules expose implemented grid, property, restart, summary, well, and RFT/PLT domain objects and option schemas. Grid/restart/summary loaders accept scoped load option objects. Broad binary/vendor-specific workflows still raise explicit unsupported errors. | Facade import, load option, and export tests passed. |
| Case discovery | partially_implemented | Basename, explicit-file, and unambiguous-directory discovery are implemented. Deeper naming policy configuration and exact simulator convention coverage remain later work. | Discovery tests passed. |
| File type detection | partially_implemented | Extension-based detection exists for main categories plus conservative non-unified step patterns. No payload sniffing yet. | Detection tests passed. |
| GRDECL parser | implemented | Text tokenizer, parser, and reader handle comments, whitespace, slash terminators, quoted strings, logicals, numeric values, repeat syntax, and strict unterminated-record errors. | GRDECL tests passed. |
| Keyword records/datasets | implemented | `KeywordRecord`, `KeywordDataset`, `KeywordType`, and `KeywordQuery` provide occurrence-aware retrieval, type/size validation, numeric tuple conversion, optional NumPy conversion, missing errors, and ambiguous-query errors. | Keyword dataset and NumPy boundary tests passed. |
| Grid domain model | partially_implemented | Core structured-grid dimensions, cell indexes, grid cells, reservoir grid access, geometry array validation, and lightweight depth/top/bottom/thickness behavior are implemented. `ExportService` can export supported grid cell metadata to tabular rows/CSV. Full corner-point reconstruction, volume, spatial lookup, local grids, dual grids, and NNC remain later work. | Grid domain and grid table export tests passed. |
| GRID/EGRID reader | partially_implemented | `GridReader` loads minimal formatted GRDECL-style GRID/EGRID keyword files into `ReservoirGrid`, and `ExportService` can write the supported geometry subset back to GRDECL text. Binary simulator GRID/EGRID keyword payload decoding, full geometry reconstruction, local grids, dual grids, and NNC remain pending. | Minimal grid reader and grid export round-trip tests passed. |
| INIT/property loading | partially_implemented | `InitReader`, `GridProperty`, and `PropertyCollection` load selected formatted INIT/property keywords and classify active/global layout when a compatible grid is provided. Public property loading can now index selected formatted INIT properties lazily and materialize one property on demand. `GridProperty` exposes numeric tuple and optional NumPy boundaries for native, active, and global layouts. `ExportService` can export selected properties in native, active, or global GRDECL layout and long-form CSV/table rows. Binary INIT decoding, byte-offset indexing, units, and broad writer behavior remain pending. | INIT reader/property, lazy property, NumPy boundary, and property export tests passed. |
| Active/global mapping | implemented | `ActiveCellMap` converts active-sized sequences to global-sized values, compresses global-sized sequences, validates shapes, and includes optional NumPy-array paths. | Sequence tests passed; NumPy-specific test skipped because NumPy is not installed. |
| Binary record infrastructure | implemented | `FortranRecordReader` reads length-prefixed records with configurable endian order, validates leading/trailing markers, reports truncation, and provides simple endian detection. | Binary I/O tests passed. |
| Formatted/unformatted keyword files | partially_implemented | Common formatted text keyword reader is implemented for GRDECL-style records and now backs minimal GRID/EGRID/INIT readers. Unformatted low-level record framing is implemented, but simulator-specific binary keyword payload decoding is not implemented yet. | Formatted reader, grid/init reader, and formatted/unformatted mismatch tests passed. |
| Unified/non-unified handling | partially_implemented | Detection records unified flags and report steps for supported filename patterns. Formatted restart and summary reader/services now index formatted unified files and formatted non-unified report-step files. Binary restart/summary grouping remains pending. | Detection, manifest, restart grouping, and summary grouping tests passed. |
| Restart dataset/reports | partially_implemented | `RestartHeader`, `RestartReport`, `RestartDataset`, `FormattedRestartReader`, and `RestartService` support formatted restart report indexing, lazy payload loading, report lookup, grid property mapping, requested-report filtering, and eager payload materialization when requested. Binary restart keyword decoding, complete metadata semantics, well extraction through restart load options, and writing remain pending. | Restart and restart load option tests passed. |
| Summary dataset/vectors | partially_implemented | `SummaryKey`, `SummaryMetadata`, `SummaryVector`, `SummaryDataset`, `FormattedSummaryReader`, and `SummaryService` support formatted summary metadata, time axes, lazy/eager vector loading, vector-filtered datasets, filtering, interpolation/resampling, CSV export, and optional NumPy/pandas export boundaries. Binary `SMSPEC`/`UNSMRY` decoding, complete vector classification guarantees, alternate key/time policies, and summary writing remain pending. | Summary and summary load option tests passed. |
| RFT/PLT data | partially_implemented | `RftDataset`, `RftRecord`, `RftCellMeasurement`, `FormattedRftReader`, and `RftService` support formatted GRDECL-style RFT/PLT records, well/date/type query, lazy measurement loading, pressures, depths, saturations, and phase rates. Binary/unformatted RFT/PLT and vendor-specific record variants remain pending. | RFT/PLT tests passed. |
| Well timelines/states/connections/segments | partially_implemented | `WellDataset`, `WellTimeline`, `WellSnapshot`, `WellConnection`, `WellSegment`, `FormattedWellReader`, and `WellService` support well timelines from scoped formatted restart records, open state, type, rates, grid cell connections, grid validation, and optional segment loading. Complete restart well record extraction and multi-segment semantics remain pending. | Well timeline tests passed. |
| Lazy loading | partially_implemented | Case open still avoids payload parsing, formatted restart report payloads are parsed lazily after header indexing, formatted summary vectors are loaded lazily after metadata/time-axis indexing, formatted INIT properties can be materialized one property at a time through the public case workflow, and formatted RFT/PLT measurements are loaded lazily after record headers. Binary restart payloads, memory-mapped/chunked readers, and broad cache-backed lazy loading remain later work. | Restart, summary, INIT property, and RFT lazy payload tests passed. |
| NumPy integration | partially_implemented | `ActiveCellMap` has optional NumPy array expansion/compression when NumPy is available. `KeywordRecord.to_numpy()`, `GridProperty.to_numpy()`, `SummaryVector.to_numpy()`, and `SummaryDataset.to_numpy()` provide optional NumPy export boundaries. Mutable shared-view semantics, memory-mapped arrays, and broader binary numeric buffers remain later work. | NumPy active-map test is present but skipped in this environment because NumPy is not installed; keyword/property/summary NumPy boundary tests pass by exercising optional conversion when available or explicit missing-dependency errors when absent. |
| pandas/CSV export | partially_implemented | `SummaryDataset.to_csv()` is implemented with the standard library, and `to_pandas()` provides an optional pandas boundary with explicit missing-dependency errors. `ExportService` also writes supported grid cell metadata and selected grid properties as CSV. pandas DataFrame boundaries for grid/property tables remain later work. | Summary CSV, optional pandas boundary, grid CSV, and property CSV export tests passed. |
| Selective writers/export | partially_implemented | `GrdeclWriter` and `ExportService` support tested GRDECL text export for supported grid geometry and selected properties. `ExportService` also supports tabular grid/property rows and CSV. Public case methods expose grid/property GRDECL and CSV export. Full deck writing, restart/summary rewriting, binary writers, and broad simulator-format writing remain pending/deferred. | GRDECL formatting, grid/property round-trip export, and grid/property CSV tests passed. |
| Error handling | partially_implemented | Discovery, facade, keyword query, GRDECL parse/read, grid index, grid geometry, active-map shape, property shape, missing property, invalid report step, restart parse, summary metadata/data, well data, RFT/PLT data, binary record, endian detection, formatted keyword mismatch, and unsupported advanced load-option errors are implemented; later parser/domain errors remain pending. | Error and load option tests passed. |
| Large-file behavior | partially_implemented | Opening a case uses filenames only and avoids payload loading. Summary index caches can avoid repeated metadata/time-axis parsing, formatted INIT properties can defer value materialization, and existing restart/summary/RFT objects keep payloads lazy. Memory mapping and chunked binary/text readers remain pending. | Discovery, lazy property, lazy payload, and cache invalidation tests passed. |
| Cache/index support | partially_implemented | `SourceFingerprint` and `JsonIndexCache` provide optional JSON index cache files invalidated by resolved path, size, and modification time. Formatted summary loading can persist and reuse metadata/time-axis/vector-key indexes via `LoadCaseOptions.cache_policy`. Cache support for restart, INIT byte offsets, RFT, and binary payload readers remains pending. | Cache hit/miss and source invalidation tests passed. |
| Tests | partially_implemented | M1 through M14 tests exist for foundation, keyword, GRDECL, grid, active-map, binary I/O, formatted keyword, GRID/EGRID, INIT, property, formatted restart, formatted summary, well timeline, formatted RFT/PLT, lazy property loading, summary cache behavior, GRDECL export behavior, tabular grid/property export behavior, scoped load option behavior, keyword/property NumPy boundaries, and public facade imports. Full black-box test plan remains pending. | `python -m pytest`: 88 passed, 1 skipped. |

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
  linear by simulation day until simulator-specific rate/cumulative behavior is
  independently verified.
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
- M11 tabular export intentionally covers standard-library CSV/row output for
  supported loaded grid cells and properties. It uses existing lightweight
  ZCORN-derived top/bottom/depth/thickness values and does not claim full
  corner-point XYZ reconstruction, volume calculations, pandas DataFrame export,
  unit conversion, local-grid/NNC tables, or simulator-specific table schemas.
- M12 load options intentionally provide typed contracts and enforcement for the
  supported formatted-reader workflows. Options whose underlying behavior is not
  implemented raise `UnsupportedFormatError` rather than being silently ignored.
- M13 NumPy boundary support intentionally keeps NumPy optional. Tuple-backed
  keyword and property values produce copied arrays when NumPy is available and
  raise explicit missing-dependency errors when it is absent.
- M14 public facade modules intentionally re-export implemented domain/result
  objects and DTOs only. They do not add compatibility aliases or expose
  low-level parser/binary internals.
