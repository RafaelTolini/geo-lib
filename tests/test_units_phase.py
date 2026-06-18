import pytest

from reservoir_data.domain.grid import ActiveCellMap, GridDimensions, GridGeometry
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.units import Phase, UnitSystem
from reservoir_data.public.units_facade import Phase as PublicPhase
from reservoir_data.public.units_facade import UnitSystem as PublicUnitSystem
from reservoir_data.schemas.export import PropertyExportOptions


def test_unit_system_normalizes_common_labels() -> None:
    assert UnitSystem.from_label("METRIC") is UnitSystem.METRIC
    assert UnitSystem.from_label("field-units") is UnitSystem.FIELD
    assert UnitSystem.optional(None) is None
    assert UnitSystem.UNKNOWN.is_known is False


def test_phase_normalizes_common_labels() -> None:
    assert Phase.from_label("wat") is Phase.WATER
    assert Phase.from_label("VAPOUR") is Phase.VAPOR
    assert Phase.optional(None) is None
    assert Phase.GAS.is_known is True


def test_invalid_unit_and_phase_labels_raise_clear_errors() -> None:
    with pytest.raises(ValueError, match="Unknown unit system"):
        UnitSystem.from_label("martian")
    with pytest.raises(ValueError, match="phase label must not be empty"):
        Phase.from_label(" ")


def test_grid_and_export_options_normalize_unit_system_values() -> None:
    dimensions = GridDimensions(nx=1, ny=1, nz=1)
    geometry = GridGeometry(
        dimensions=dimensions,
        coord=(0.0,) * 24,
        zcorn=(1.0,) * 8,
    )
    grid = ReservoirGrid(
        dimensions=dimensions,
        geometry=geometry,
        active_cell_map=ActiveCellMap((1,)),
        unit_system="FIELD",
    )

    options = PropertyExportOptions(output_unit_system="metric")

    assert grid.unit_system is UnitSystem.FIELD
    assert options.output_unit_system is UnitSystem.METRIC


def test_public_units_facade_exports_domain_classes() -> None:
    assert PublicPhase is Phase
    assert PublicUnitSystem is UnitSystem
