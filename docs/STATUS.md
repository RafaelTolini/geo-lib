# Status

## Current Milestone

M4: Binary and Formatted Keyword Infrastructure is complete for the scoped
behavior. The next automatic milestone is M5: GRID/EGRID and INIT Readers.

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

## Work In Progress

- None for M4.

## Next Planned Task

Implement M5: minimal GRID/EGRID and INIT/property readers using the validated
grid domain model and keyword I/O infrastructure.

## Blockers

- None identified for an M5 foundation slice, but production-quality binary
  GRID/EGRID/INIT coverage still requires independent public fixtures or
  documentation.

## Deferred Specification Items

- GRID/EGRID parsing.
- INIT/property loading.
- Restart, summary, well, and RFT/PLT payload parsing.
- NumPy, pandas, CSV, and simulator-format export.
- Cache/index support.
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

## Known Limitations

- Only GRDECL text keyword payloads are parsed.
- Discovery will be filename-based until format readers and binary/text sniffing
  are implemented.
- Exact formatted and non-unified extension conventions are conservative and
  require independent verification before being advertised as complete support.
- Public loaders for grid, properties, restart, summary, wells, and RFT/PLT are
  intentionally unsupported beyond discovery until their parser milestones.
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
