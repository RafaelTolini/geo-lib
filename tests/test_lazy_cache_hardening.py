import json
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.formats.init.init_reader import InitReader
from reservoir_data.formats.summary.formatted_summary_reader import (
    FormattedSummaryReader,
)
from reservoir_data.infrastructure.caching.json_index_cache import JsonIndexCache
from reservoir_data.infrastructure.caching.source_fingerprint import SourceFingerprint
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import CachePolicy, LoadCaseOptions


def _grid_text() -> str:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    return f"""
    SPECGRID 2 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM 1 0 /
    """


def _summary_detection(path: Path) -> FormatDetectionResult:
    return FormatDetectionResult(
        path=path,
        file_category=FileCategory.SUMMARY_DATA,
        formatted=True,
        unified=True,
        report_step=None,
        confidence=1.0,
        diagnostics=("test fixture",),
    )


def _summary_metadata() -> str:
    return """
    VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /
    VECTOR 'FOPT' 'SM3' 'FIELD' /
    """


def _summary_data(fopr_last: float = 20.0) -> str:
    return f"""
    TIME 0 10 /
    DATES '2026-01-01' '2026-01-11' /
    REPORTS 0 1 /
    VALUES 'FOPR' 10 {fopr_last} /
    VALUES 'FOPT' 100 300 /
    """


def test_public_case_lazy_properties_load_only_when_requested(tmp_path: Path) -> None:
    (tmp_path / "CASE.FEGRID").write_text(_grid_text(), encoding="utf-8")
    (tmp_path / "CASE.FINIT").write_text(
        """
        PORO 0.25 /
        PRESSURE 100 200 /
        """,
        encoding="utf-8",
    )

    case = SimulationCase.open(
        tmp_path / "CASE",
        LoadCaseOptions(lazy_loading=True),
    )
    properties = case.load_properties(names=["PORO", "PRESSURE"])

    assert properties.names() == ("PORO", "PRESSURE")
    assert properties.has_property("pressure")
    assert not properties.is_property_loaded("PORO")
    assert not properties.is_property_loaded("PRESSURE")
    metadata_rows = properties.metadata_rows()
    assert metadata_rows[0]["PROPERTY"] == "PORO"
    assert metadata_rows[0]["LOADED"] is False

    poro = properties.property("PORO")

    assert poro is not None
    assert properties.is_property_loaded("PORO")
    assert not properties.is_property_loaded("PRESSURE")
    assert poro.to_global_array(default_value=0.0) == (0.25, 0.0)
    metadata_csv_path = tmp_path / "properties.csv"
    properties.metadata_to_csv(metadata_csv_path)
    assert "INDEX,PROPERTY,LOADED,LAYOUT,VALUE_COUNT,UNIT,SOURCE" in (
        metadata_csv_path.read_text(encoding="utf-8")
    )


def test_lazy_property_collection_selection_preserves_lazy_loaders(
    tmp_path: Path,
) -> None:
    path = tmp_path / "CASE.FINIT"
    path.write_text("PORO 0.25 / PRESSURE 100 200 /", encoding="utf-8")
    properties = InitReader().read(
        path,
        names=("PORO", "PRESSURE"),
        lazy=True,
    )

    selected = properties.select(["PRESSURE"])

    assert selected.names() == ("PRESSURE",)
    assert selected.has_property("PRESSURE")
    assert not selected.is_property_loaded("PRESSURE")
    assert selected.property("PRESSURE").values == (100, 200)
    assert selected.is_property_loaded("PRESSURE")


def test_lazy_init_property_results_match_eager_results(tmp_path: Path) -> None:
    path = tmp_path / "CASE.FINIT"
    path.write_text("PORO 0.25 / PRESSURE 100 200 /", encoding="utf-8")
    reader = InitReader()

    eager = reader.read(path, names=["PORO"], lazy=False)
    lazy = reader.read(path, names=["PORO"], lazy=True)

    assert not lazy.is_property_loaded("PORO")
    assert lazy.property("PORO") == eager.property("PORO")


def test_summary_index_cache_hits_and_invalidates_by_source_identity(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "CASE.FSMSPEC"
    data_path = tmp_path / "CASE.FUNSMRY"
    cache_dir = tmp_path / ".reservoir_data_cache"
    metadata_path.write_text(_summary_metadata(), encoding="utf-8")
    data_path.write_text(_summary_data(), encoding="utf-8")

    reader = FormattedSummaryReader()
    first_cache = JsonIndexCache(cache_dir=cache_dir, writable=True)
    first = reader.read(metadata_path, (_summary_detection(data_path),), cache=first_cache)

    assert first_cache.misses == 1
    assert first_cache.writes == 1
    assert first.vector("FOPR").values == (10.0, 20.0)

    second_cache = JsonIndexCache(cache_dir=cache_dir, writable=True)
    second = reader.read(
        metadata_path,
        (_summary_detection(data_path),),
        cache=second_cache,
    )

    assert second_cache.hits == 1
    assert not second.is_vector_loaded("FOPR")
    assert second.vector("FOPR").values == first.vector("FOPR").values

    data_path.write_text(_summary_data(fopr_last=25.0), encoding="utf-8")
    invalidated_cache = JsonIndexCache(cache_dir=cache_dir, writable=True)
    changed = reader.read(
        metadata_path,
        (_summary_detection(data_path),),
        cache=invalidated_cache,
    )

    assert invalidated_cache.misses == 1
    assert invalidated_cache.writes == 1
    assert changed.vector("FOPR").values == (10.0, 25.0)


def test_source_fingerprint_can_include_stronger_sha256_checksum(
    tmp_path: Path,
) -> None:
    path = tmp_path / "source.txt"
    path.write_text("abc", encoding="utf-8")

    weak = SourceFingerprint.from_path(path)
    strong = SourceFingerprint.from_path(path, include_checksum=True)
    restored = SourceFingerprint.from_json(strong.to_json())

    assert weak.sha256 is None
    assert strong.sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert restored == strong


def test_json_index_cache_can_persist_checksum_fingerprints(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    cache_dir = tmp_path / ".reservoir_data_cache"
    source.write_text("payload", encoding="utf-8")

    cache = JsonIndexCache(cache_dir=cache_dir, writable=True, checksum_sources=True)
    cache.save("test", "case", (source,), {"ok": True})
    cache_file = next(cache_dir.glob("*.json"))
    envelope = json.loads(cache_file.read_text(encoding="utf-8"))

    reloaded_cache = JsonIndexCache(
        cache_dir=cache_dir,
        writable=True,
        checksum_sources=True,
    )
    payload = reloaded_cache.load("test", "case", (source,))

    assert envelope["sources"][0]["sha256"]
    assert payload == {"ok": True}
    assert reloaded_cache.hits == 1


def test_public_summary_cache_policy_creates_optional_index(tmp_path: Path) -> None:
    (tmp_path / "CASE.FSMSPEC").write_text(_summary_metadata(), encoding="utf-8")
    (tmp_path / "CASE.FUNSMRY").write_text(_summary_data(), encoding="utf-8")

    case = SimulationCase.open(
        tmp_path / "CASE",
        LoadCaseOptions(cache_policy=CachePolicy.READ_WRITE),
    )
    summary = case.load_summary()

    assert summary.keys() == ("FOPR", "FOPT")
    assert (tmp_path / ".reservoir_data_cache").is_dir()
