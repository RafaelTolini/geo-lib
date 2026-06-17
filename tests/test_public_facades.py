import reservoir_data.public as public
from reservoir_data.domain.grid import ReservoirGrid
from reservoir_data.domain.property.grid_property import GridProperty
from reservoir_data.domain.restart import RestartDataset
from reservoir_data.domain.rft import RftDataset
from reservoir_data.domain.summary import SummaryDataset
from reservoir_data.domain.well import WellDataset
from reservoir_data.public.grid_facade import GridLoadOptions, GridTableExportOptions
from reservoir_data.public.property_facade import (
    PropertyExportOptions,
    PropertyTableExportOptions,
)
from reservoir_data.public.restart_facade import RestartLoadOptions
from reservoir_data.public.summary_facade import SummaryLoadOptions
from reservoir_data.schemas.loading import GridLoadOptions as SchemaGridLoadOptions


def test_public_facade_modules_export_domain_and_option_classes() -> None:
    assert public.ReservoirGrid is ReservoirGrid
    assert public.GridProperty is GridProperty
    assert public.RestartDataset is RestartDataset
    assert public.SummaryDataset is SummaryDataset
    assert public.WellDataset is WellDataset
    assert public.RftDataset is RftDataset
    assert GridLoadOptions is SchemaGridLoadOptions
    assert "ReservoirGrid" in public.__all__
    assert "SummaryLoadOptions" in public.__all__


def test_public_facade_option_exports_are_constructible() -> None:
    assert GridLoadOptions().load_local_grids is False
    assert RestartLoadOptions().lazy_keyword_arrays is True
    assert SummaryLoadOptions().lazy_vectors is True
    assert GridTableExportOptions().include_geometry is True
    assert PropertyExportOptions().target_layout.value == "native"
    assert PropertyTableExportOptions().target_layout.value == "global"
