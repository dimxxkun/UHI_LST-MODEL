"""
Land Cover Classification Module

This module provides functions for classifying Landsat 8/9 imagery into
land cover categories based on spectral indices.

Classification uses a decision tree approach with:
- NDVI (Normalized Difference Vegetation Index) for vegetation
- NDWI (Normalized Difference Water Index) for water bodies
- Urban Index (Band 6 / Band 5 ratio) for built-up areas

Land Cover Classes:
1. Water
2. Urban/Built-up
3. Vegetation
4. Bare soil

References:
- McFeeters, S.K. (1996). The use of NDWI for water body delineation
- Zha, Y., et al. (2003). Use of normalized difference built-up index
"""

import numpy as np
from numpy.typing import NDArray
from typing import Dict, Tuple, Optional
from enum import IntEnum
from dataclasses import dataclass


class LandCoverClass(IntEnum):
    """Land cover classification categories."""
    NODATA = 0
    WATER = 1
    URBAN = 2
    VEGETATION = 3
    BARE_SOIL = 4


# Color map for visualization (RGB)
LAND_COVER_COLORS = {
    LandCoverClass.NODATA: (0, 0, 0),          # Black
    LandCoverClass.WATER: (0, 100, 255),       # Blue
    LandCoverClass.URBAN: (255, 100, 100),     # Red/Pink
    LandCoverClass.VEGETATION: (34, 139, 34),  # Forest Green
    LandCoverClass.BARE_SOIL: (210, 180, 140), # Tan
}

LAND_COVER_NAMES = {
    LandCoverClass.NODATA: "No Data",
    LandCoverClass.WATER: "Water",
    LandCoverClass.URBAN: "Urban/Built-up",
    LandCoverClass.VEGETATION: "Vegetation",
    LandCoverClass.BARE_SOIL: "Bare Soil",
}


@dataclass(frozen=True)
class ClassificationThresholds:
    """Thresholds for land cover classification."""
    # NDWI threshold for water detection
    NDWI_WATER: float = 0.0
    
    # NDVI thresholds
    NDVI_VEGETATION: float = 0.2  # Above this = vegetation
    NDVI_SPARSE: float = 0.1      # Below this = non-vegetated
    
    # Urban index threshold (B6/B5 ratio)
    URBAN_RATIO_MIN: float = 1.0   # Urban typically > 1.0
    
    # NDBI threshold for urban
    NDBI_URBAN: float = 0.0        # Above this = potentially urban


THRESHOLDS = ClassificationThresholds()


def calculate_ndwi(
    green: NDArray[np.floating],
    nir: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Calculate NDWI (Normalized Difference Water Index).
    
    Formula: NDWI = (Green - NIR) / (Green + NIR)
             NDWI = (Band 3 - Band 5) / (Band 3 + Band 5)
    
    NDWI > 0 typically indicates water bodies.
    
    Args:
        green: Band 3 (Green) array
        nir: Band 5 (NIR) array
        nodata_value: Value for no-data pixels
    
    Returns:
        NDWI array with values between -1 and 1
    """
    if green.shape != nir.shape:
        raise ValueError(
            f"Input arrays must have same shape. "
            f"Green: {green.shape}, NIR: {nir.shape}"
        )
    
    green = green.astype(np.float64)
    nir = nir.astype(np.float64)
    
    # Initialize with nodata
    ndwi = np.full(green.shape, nodata_value, dtype=np.float64)
    
    # Calculate denominator
    denominator = green + nir
    
    # Valid pixel mask
    valid_mask = (
        np.isfinite(green) & 
        np.isfinite(nir) & 
        (green != nodata_value) & 
        (nir != nodata_value) &
        (denominator != 0)
    )
    
    # Calculate NDWI
    ndwi[valid_mask] = (green[valid_mask] - nir[valid_mask]) / denominator[valid_mask]
    
    # Clip to valid range
    ndwi[valid_mask] = np.clip(ndwi[valid_mask], -1.0, 1.0)
    
    return ndwi


def calculate_urban_index(
    swir1: NDArray[np.floating],
    nir: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Calculate Urban Index (SWIR1/NIR ratio).
    
    Formula: UI = Band 6 / Band 5
    
    Urban areas typically have UI > 1.0 due to:
    - High SWIR reflectance from impervious surfaces
    - Lower NIR reflectance compared to vegetation
    
    Args:
        swir1: Band 6 (SWIR1) array
        nir: Band 5 (NIR) array
        nodata_value: Value for no-data pixels
    
    Returns:
        Urban Index array (unbounded ratio)
    """
    if swir1.shape != nir.shape:
        raise ValueError(
            f"Input arrays must have same shape. "
            f"SWIR1: {swir1.shape}, NIR: {nir.shape}"
        )
    
    swir1 = swir1.astype(np.float64)
    nir = nir.astype(np.float64)
    
    # Initialize with nodata
    ui = np.full(swir1.shape, nodata_value, dtype=np.float64)
    
    # Valid pixel mask (avoid division by zero)
    valid_mask = (
        np.isfinite(swir1) & 
        np.isfinite(nir) & 
        (swir1 != nodata_value) & 
        (nir != nodata_value) &
        (nir != 0)
    )
    
    # Calculate ratio
    ui[valid_mask] = swir1[valid_mask] / nir[valid_mask]
    
    return ui


def calculate_ndbi(
    swir1: NDArray[np.floating],
    nir: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Calculate NDBI (Normalized Difference Built-up Index).
    
    Formula: NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
             NDBI = (Band 6 - Band 5) / (Band 6 + Band 5)
    
    NDBI > 0 typically indicates built-up/urban areas.
    
    Args:
        swir1: Band 6 (SWIR1) array
        nir: Band 5 (NIR) array
        nodata_value: Value for no-data pixels
    
    Returns:
        NDBI array with values between -1 and 1
    """
    if swir1.shape != nir.shape:
        raise ValueError(
            f"Input arrays must have same shape. "
            f"SWIR1: {swir1.shape}, NIR: {nir.shape}"
        )
    
    swir1 = swir1.astype(np.float64)
    nir = nir.astype(np.float64)
    
    # Initialize with nodata
    ndbi = np.full(swir1.shape, nodata_value, dtype=np.float64)
    
    # Calculate denominator
    denominator = swir1 + nir
    
    # Valid pixel mask
    valid_mask = (
        np.isfinite(swir1) & 
        np.isfinite(nir) & 
        (swir1 != nodata_value) & 
        (nir != nodata_value) &
        (denominator != 0)
    )
    
    # Calculate NDBI
    ndbi[valid_mask] = (swir1[valid_mask] - nir[valid_mask]) / denominator[valid_mask]
    
    # Clip to valid range
    ndbi[valid_mask] = np.clip(ndbi[valid_mask], -1.0, 1.0)
    
    return ndbi


def classify_land_cover(
    band_2: NDArray[np.floating],  # Blue
    band_3: NDArray[np.floating],  # Green
    band_4: NDArray[np.floating],  # Red
    band_5: NDArray[np.floating],  # NIR
    band_6: NDArray[np.floating],  # SWIR1
    band_7: NDArray[np.floating],  # SWIR2
    nodata_value: float = -9999.0,
    ndvi: Optional[NDArray[np.floating]] = None,
) -> Tuple[NDArray[np.int8], Dict[str, NDArray[np.floating]]]:
    """
    Classify land cover using spectral indices.
    
    Classification decision tree:
    1. If NDWI > 0 → Water
    2. If NDVI > 0.2 → Vegetation
    3. If Urban Index (B6/B5) > 1.0 OR NDBI > 0 → Urban
    4. Otherwise → Bare Soil
    
    Args:
        band_2: Band 2 (Blue) array
        band_3: Band 3 (Green) array
        band_4: Band 4 (Red) array
        band_5: Band 5 (NIR) array
        band_6: Band 6 (SWIR1) array
        band_7: Band 7 (SWIR2) array
        nodata_value: Value for no-data pixels
        ndvi: Optional pre-calculated NDVI array
    
    Returns:
        Tuple of:
        - Classification array (values 0-4)
        - Dictionary with calculated indices (ndvi, ndwi, ndbi, urban_index)
    """
    # Validate shapes
    shapes = [band_2.shape, band_3.shape, band_4.shape, 
              band_5.shape, band_6.shape, band_7.shape]
    if not all(s == shapes[0] for s in shapes):
        raise ValueError("All input bands must have the same shape")
    
    # Calculate indices
    # NDVI: (NIR - Red) / (NIR + Red)
    if ndvi is None:
        from .ndvi import calculate_ndvi
        ndvi = calculate_ndvi(band_5, band_4, nodata_value)
    
    # NDWI: (Green - NIR) / (Green + NIR)
    ndwi = calculate_ndwi(band_3, band_5, nodata_value)
    
    # NDBI: (SWIR1 - NIR) / (SWIR1 + NIR)
    ndbi = calculate_ndbi(band_6, band_5, nodata_value)
    
    # Urban Index: SWIR1 / NIR
    urban_index = calculate_urban_index(band_6, band_5, nodata_value)
    
    # Initialize classification with NODATA
    classification = np.full(band_2.shape, LandCoverClass.NODATA, dtype=np.int8)
    
    # Create valid data mask (all bands must have valid data)
    valid_mask = (
        (ndvi != nodata_value) & 
        (ndwi != nodata_value) &
        np.isfinite(ndvi) & 
        np.isfinite(ndwi)
    )
    
    # Apply decision tree classification
    # Priority order: Water > Vegetation > Urban > Bare Soil
    
    # Step 1: Water (NDWI > 0)
    water_mask = valid_mask & (ndwi > THRESHOLDS.NDWI_WATER)
    classification[water_mask] = LandCoverClass.WATER
    
    # Step 2: Vegetation (NDVI > 0.2, not already classified)
    remaining = valid_mask & (classification == LandCoverClass.NODATA)
    vegetation_mask = remaining & (ndvi > THRESHOLDS.NDVI_VEGETATION)
    classification[vegetation_mask] = LandCoverClass.VEGETATION
    
    # Step 3: Urban (Urban Index > 1.0 OR NDBI > 0, not already classified)
    remaining = valid_mask & (classification == LandCoverClass.NODATA)
    urban_mask = remaining & (
        (urban_index > THRESHOLDS.URBAN_RATIO_MIN) | 
        (ndbi > THRESHOLDS.NDBI_URBAN)
    )
    classification[urban_mask] = LandCoverClass.URBAN
    
    # Step 4: Bare Soil (everything else that's valid)
    remaining = valid_mask & (classification == LandCoverClass.NODATA)
    classification[remaining] = LandCoverClass.BARE_SOIL
    
    # Store indices
    indices = {
        "ndvi": ndvi,
        "ndwi": ndwi,
        "ndbi": ndbi,
        "urban_index": urban_index,
    }
    
    return classification, indices


def get_land_cover_statistics(
    classification: NDArray[np.int8],
) -> Dict[str, any]:
    """
    Calculate statistics for land cover classification.
    
    Args:
        classification: Classification array from classify_land_cover()
    
    Returns:
        Dictionary containing:
        - class_counts: Pixel count per class
        - class_percentages: Percentage per class
        - total_valid: Total valid pixels
        - total_pixels: Total pixels including nodata
    """
    total_pixels = classification.size
    valid_mask = classification != LandCoverClass.NODATA
    total_valid = int(np.sum(valid_mask))
    
    class_counts = {}
    class_percentages = {}
    
    for cls in LandCoverClass:
        count = int(np.sum(classification == cls))
        class_counts[LAND_COVER_NAMES[cls]] = count
        
        if total_valid > 0:
            percentage = (count / total_valid * 100) if cls != LandCoverClass.NODATA else 0
        else:
            percentage = 0.0
        class_percentages[LAND_COVER_NAMES[cls]] = round(percentage, 2)
    
    return {
        "class_counts": class_counts,
        "class_percentages": class_percentages,
        "total_valid_pixels": total_valid,
        "total_pixels": total_pixels,
        "nodata_pixels": total_pixels - total_valid,
    }


def create_color_visualization(
    classification: NDArray[np.int8],
    alpha: bool = True,
) -> NDArray[np.uint8]:
    """
    Create a color-coded RGB(A) visualization of land cover classification.
    
    Args:
        classification: Classification array from classify_land_cover()
        alpha: If True, include alpha channel (transparent nodata)
    
    Returns:
        NumPy array with shape (height, width, 3) or (height, width, 4)
        Values are uint8 (0-255) suitable for image export
    """
    height, width = classification.shape
    channels = 4 if alpha else 3
    
    # Initialize output (black/transparent for nodata)
    rgb = np.zeros((height, width, channels), dtype=np.uint8)
    
    # Apply colors for each class
    for cls, color in LAND_COVER_COLORS.items():
        mask = classification == cls
        rgb[mask, 0] = color[0]  # R
        rgb[mask, 1] = color[1]  # G
        rgb[mask, 2] = color[2]  # B
        
        if alpha:
            # Set alpha to 255 (opaque) for valid data, 0 for nodata
            if cls != LandCoverClass.NODATA:
                rgb[mask, 3] = 255
    
    return rgb


def export_classification_legend() -> Dict[str, Dict]:
    """
    Export the classification legend for visualization.
    
    Returns:
        Dictionary with class names, values, and RGB colors.
    """
    legend = {}
    for cls in LandCoverClass:
        legend[LAND_COVER_NAMES[cls]] = {
            "value": int(cls),
            "color_rgb": LAND_COVER_COLORS[cls],
            "color_hex": "#{:02x}{:02x}{:02x}".format(*LAND_COVER_COLORS[cls]),
        }
    return legend


def calculate_all_indices(
    band_2: NDArray[np.floating],
    band_3: NDArray[np.floating],
    band_4: NDArray[np.floating],
    band_5: NDArray[np.floating],
    band_6: NDArray[np.floating],
    band_7: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> Dict[str, NDArray[np.floating]]:
    """
    Calculate all spectral indices for analysis.
    
    Indices calculated:
    - NDVI: Vegetation index
    - NDWI: Water index
    - NDBI: Built-up index
    - Urban Index: SWIR1/NIR ratio
    - MNDWI: Modified NDWI using SWIR
    
    Args:
        band_2 through band_7: Landsat bands
        nodata_value: Value for no-data pixels
    
    Returns:
        Dictionary with all calculated indices
    """
    from .ndvi import calculate_ndvi
    
    # NDVI: vegetation
    ndvi = calculate_ndvi(band_5, band_4, nodata_value)
    
    # NDWI: water (McFeeters)
    ndwi = calculate_ndwi(band_3, band_5, nodata_value)
    
    # NDBI: built-up
    ndbi = calculate_ndbi(band_6, band_5, nodata_value)
    
    # Urban Index: B6/B5 ratio
    urban_index = calculate_urban_index(band_6, band_5, nodata_value)
    
    # MNDWI: Modified NDWI (Green - SWIR1) / (Green + SWIR1)
    # Better for water in urban areas
    mndwi = np.full(band_3.shape, nodata_value, dtype=np.float64)
    denominator = band_3.astype(np.float64) + band_6.astype(np.float64)
    valid_mask = (
        np.isfinite(band_3) & np.isfinite(band_6) &
        (band_3 != nodata_value) & (band_6 != nodata_value) &
        (denominator != 0)
    )
    mndwi[valid_mask] = (band_3[valid_mask] - band_6[valid_mask]) / denominator[valid_mask]
    mndwi[valid_mask] = np.clip(mndwi[valid_mask], -1.0, 1.0)
    
    return {
        "ndvi": ndvi,
        "ndwi": ndwi,
        "ndbi": ndbi,
        "urban_index": urban_index,
        "mndwi": mndwi,
    }
