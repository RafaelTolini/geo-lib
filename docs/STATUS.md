# Status

## Current Milestone

M2: Keyword Records and GRDECL Text Parser is complete for the scoped behavior.
The next automatic milestone is M3: Grid Domain Model and Active/Global Mapping.

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

## Work In Progress

- None for M2.

## Next Planned Task

Implement M3: grid dimensions, cell indexes, reservoir grid skeleton,
grid cells, grid geometry placeholders with real validation behavior, and
active/global cell mapping.

## Blockers

- None for M3 foundation behavior.

## Deferred Specification Items

- GRID/EGRID parsing.
- INIT/property loading.
- Binary record infrastructure.
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

## Known Limitations

- Only GRDECL text keyword payloads are parsed.
- Discovery will be filename-based until format readers and binary/text sniffing
  are implemented.
- Exact formatted and non-unified extension conventions are conservative and
  require independent verification before being advertised as complete support.
- Public loaders for grid, properties, restart, summary, wells, and RFT/PLT are
  intentionally unsupported beyond discovery until their parser milestones.
- GRDECL parsing does not perform deck semantics, grid construction, property
  shape validation, or binary/formatted simulator keyword parsing.
- GRDECL bare default repeats such as `3*` are represented as `None`; later
  domain validators decide whether defaults are legal for a given keyword.

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
