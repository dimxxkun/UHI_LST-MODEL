"""
Utility modules for UHI-LST Analysis.
"""

from .heatmap import (
    generate_heatmap_data,
    generate_heatmap_from_array,
    HeatmapConfig,
    HeatmapPoint,
    get_heatmap_statistics,
    filter_heatmap_by_bounds,
    filter_heatmap_by_temperature,
)

from .file_handler import (
    TempFileManager,
    BandData,
    BandMetadata,
    LoadedBands,
    validate_file_extension,
    validate_geotiff,
    validate_bands_match,
    load_band,
    load_all_bands,
    temp_band_files,
    get_file_info,
    FileValidationError,
    BandMismatchError,
    CorruptFileError,
)

__all__ = [
    # Heatmap
    "generate_heatmap_data",
    "generate_heatmap_from_array",
    "HeatmapConfig",
    "HeatmapPoint",
    "get_heatmap_statistics",
    "filter_heatmap_by_bounds",
    "filter_heatmap_by_temperature",
    # File Handler
    "TempFileManager",
    "BandData",
    "BandMetadata",
    "LoadedBands",
    "validate_file_extension",
    "validate_geotiff",
    "validate_bands_match",
    "load_band",
    "load_all_bands",
    "temp_band_files",
    "get_file_info",
    "FileValidationError",
    "BandMismatchError",
    "CorruptFileError",
]
