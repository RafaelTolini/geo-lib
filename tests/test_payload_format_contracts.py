from pathlib import Path
import struct

import pytest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileDetectionError, UnsupportedFormatError
from reservoir_data.formats.common.file_detector import FileDetector
from reservoir_data.formats.common.formatted_keyword_reader import FormattedKeywordReader
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.loading import LoadCaseOptions


def _fortran_record(payload: bytes) -> bytes:
    marker = struct.pack("<I", len(payload))
    return marker + payload + marker


def test_file_detector_can_sniff_ambiguous_grid_payload_format(tmp_path: Path) -> None:
    text_path = tmp_path / "CASE.EGRID"
    binary_path = tmp_path / "CASE.GRID"
    text_path.write_text("SPECGRID 1 1 1 1 F /", encoding="utf-8")
    binary_path.write_bytes(_fortran_record(b"GRID"))

    text_result = FileDetector().detect(text_path, sniff_payload=True)
    binary_result = FileDetector().detect(binary_path, sniff_payload=True)

    assert text_result.formatted is True
    assert binary_result.formatted is False
    assert any("Payload sniffing" in item for item in text_result.diagnostics)


def test_file_detector_reports_payload_conflict_when_sniffing(tmp_path: Path) -> None:
    path = tmp_path / "CASE.FUNRST"
    path.write_bytes(_fortran_record(b"RESTART"))

    with pytest.raises(FileDetectionError, match="conflicts"):
        FileDetector().detect(path, sniff_payload=True)


def test_file_detector_supports_explicit_format_override_for_ambiguous_files(
    tmp_path: Path,
) -> None:
    path = tmp_path / "CASE.EGRID"
    path.write_text("SPECGRID 1 1 1 1 F /", encoding="utf-8")

    result = FileDetector().detect(path, formatted_override=True)

    assert result.formatted is True
    assert result.file_category is FileCategory.GRID
    assert result.confidence == 1.0
    assert result.format_label == "formatted"
    assert result.diagnostic_summary()
    result.require_formatted("grid loading")


def test_detection_result_requires_formatted_payloads(tmp_path: Path) -> None:
    path = tmp_path / "CASE.GRID"
    path.write_bytes(_fortran_record(b"GRID"))
    result = FileDetector().detect(path, sniff_payload=True)

    assert result.format_label == "unformatted"
    with pytest.raises(UnsupportedFormatError, match="requires a formatted file"):
        result.require_formatted("formatted reader")


def test_simulation_case_discovery_can_opt_into_payload_sniffing(tmp_path: Path) -> None:
    (tmp_path / "CASE.EGRID").write_text(
        "SPECGRID 1 1 1 1 F / COORD 24*0 / ZCORN 8*0 /",
        encoding="utf-8",
    )

    case = SimulationCase.open(
        tmp_path / "CASE",
        LoadCaseOptions(sniff_payload_format=True),
    )

    detection = case.manifest.preferred_file(FileCategory.GRID)
    assert detection is not None
    assert detection.formatted is True


def test_formatted_keyword_reader_rejects_explicit_unformatted_expectation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "CASE.FINIT"
    path.write_text("PORO 1 /", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError, match="unformatted"):
        FormattedKeywordReader().read(path, expect_formatted=False)
