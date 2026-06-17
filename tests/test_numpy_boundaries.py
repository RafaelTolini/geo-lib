from pathlib import Path

import pytest

from reservoir_data.domain.keyword.keyword_record import KeywordRecord
from reservoir_data.domain.property.grid_property import PropertyLayout
from reservoir_data.exceptions.errors import UnsupportedFormatError
from reservoir_data.formats.grid.grid_reader import GridReader
from reservoir_data.formats.init.init_reader import InitReader


def _minimal_grid_text() -> str:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    return f"""
    SPECGRID 2 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM 1 0 /
    """


def test_keyword_record_numeric_values_and_numpy_boundary() -> None:
    record = KeywordRecord.from_values("NUM", (1, 2.5, None))

    assert record.numeric_values(default_value=0.0) == (1, 2.5, 0.0)
    with pytest.raises(UnsupportedFormatError, match="defaulted"):
        record.numeric_values()
    with pytest.raises(UnsupportedFormatError, match="not numeric"):
        KeywordRecord.from_values("TEXT", ("A",)).numeric_values()
    with pytest.raises(UnsupportedFormatError, match="not numeric"):
        KeywordRecord.from_values("LOGIC", (True,)).numeric_values()

    try:
        array = record.to_numpy(default_value=0.0)
    except UnsupportedFormatError as error:
        assert "NumPy is not installed" in str(error)
    else:
        assert array.tolist() == [1.0, 2.5, 0.0]


def test_grid_property_numeric_values_and_numpy_boundary(tmp_path: Path) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    init_path = tmp_path / "CASE.INIT"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text(
        """
        PORO 0.25 /
        PRESSURE 100 200 /
        """,
        encoding="utf-8",
    )
    grid = GridReader().read(grid_path)
    properties = InitReader().read(
        init_path,
        grid=grid,
        names=("PORO", "PRESSURE"),
    )

    poro = properties.property("PORO")
    pressure = properties.property("PRESSURE")
    assert poro.numeric_values(
        layout=PropertyLayout.GLOBAL,
        default_value=0.0,
    ) == (0.25, 0.0)
    assert pressure.numeric_values(layout=PropertyLayout.ACTIVE) == (100,)
    assert pressure.numeric_values() == (100, 200)

    try:
        array = poro.to_numpy(layout=PropertyLayout.GLOBAL, default_value=0.0)
    except UnsupportedFormatError as error:
        assert "NumPy is not installed" in str(error)
    else:
        assert array.tolist() == [0.25, 0.0]
