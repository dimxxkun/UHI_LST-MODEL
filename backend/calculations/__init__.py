"""
Calculations module for UHI-LST Analysis.

This module contains functions for calculating various vegetation and 
urban heat indices from Landsat 8/9 imagery.
"""

from .ndvi import (
    calculate_ndvi, 
    classify_ndvi, 
    NDVICategory,
    get_ndvi_statistics,
    get_classification_percentages,
)
from .lst import (
    dn_to_radiance,
    radiance_to_brightness_temperature,
    estimate_emissivity_from_ndvi,
    calculate_lst,
    calculate_lst_from_band10,
    get_lst_statistics,
    classify_lst_thermal_zones,
    ThermalConstants,
    RadianceCoefficients,
)
from .land_cover import (
    LandCoverClass,
    calculate_ndwi,
    calculate_urban_index,
    calculate_ndbi,
    classify_land_cover,
    get_land_cover_statistics,
    create_color_visualization,
    export_classification_legend,
    calculate_all_indices,
)
from .uhi import (
    UHICategory,
    analyze_uhi,
    identify_hotspots,
    count_hotspot_clusters,
    calculate_affected_area,
    classify_uhi_intensity,
    create_uhi_map,
    create_hotspot_visualization,
    get_uhi_summary,
)

__all__ = [
    # NDVI
    "calculate_ndvi",
    "classify_ndvi", 
    "NDVICategory",
    "get_ndvi_statistics",
    "get_classification_percentages",
    # LST
    "dn_to_radiance",
    "radiance_to_brightness_temperature",
    "estimate_emissivity_from_ndvi",
    "calculate_lst",
    "calculate_lst_from_band10",
    "get_lst_statistics",
    "classify_lst_thermal_zones",
    "ThermalConstants",
    "RadianceCoefficients",
    # Land Cover
    "LandCoverClass",
    "calculate_ndwi",
    "calculate_urban_index",
    "calculate_ndbi",
    "classify_land_cover",
    "get_land_cover_statistics",
    "create_color_visualization",
    "export_classification_legend",
    "calculate_all_indices",
    # UHI
    "UHICategory",
    "analyze_uhi",
    "identify_hotspots",
    "count_hotspot_clusters",
    "calculate_affected_area",
    "classify_uhi_intensity",
    "create_uhi_map",
    "create_hotspot_visualization",
    "get_uhi_summary",
]


