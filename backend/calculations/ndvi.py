"""
NDVI (Normalized Difference Vegetation Index) Calculation Module

This module provides functions for calculating NDVI from Landsat 8/9
Band 5 (NIR) and Band 4 (Red) imagery.

NDVI = (NIR - Red) / (NIR + Red)

NDVI values range from -1 to 1:
- Negative values: Water bodies
- Values 0 to 0.2: Urban areas, bare soil, rocks
- Values 0.2 to 0.4: Sparse vegetation, grasslands
- Values > 0.4: Dense vegetation, forests
"""

import numpy as np
from numpy.typing import NDArray
from enum import IntEnum
from typing import Tuple, Dict


class NDVICategory(IntEnum):
    """NDVI classification categories."""
    WATER = 0
    URBAN_BARE_SOIL = 1
    SPARSE_VEGETATION = 2
    DENSE_VEGETATION = 3


# NDVI classification thresholds
NDVI_THRESHOLDS = {
    "water_max": 0.0,
    "urban_max": 0.2,
    "sparse_max": 0.4,
}


def calculate_ndvi(
    nir: NDArray[np.floating],
    red: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Calculate NDVI from NIR (Band 5) and Red (Band 4) arrays.
    
    NDVI = (NIR - Red) / (NIR + Red)
    
    Args:
        nir: NumPy array containing Near Infrared band values (Landsat Band 5)
        red: NumPy array containing Red band values (Landsat Band 4)
        nodata_value: Value to use for no-data pixels (default: -9999.0)
    
    Returns:
        NumPy array with NDVI values clipped between -1 and 1.
        NoData pixels are set to nodata_value.
    
    Raises:
        ValueError: If input arrays have different shapes.
    
    Example:
        >>> nir = np.array([[0.4, 0.5], [0.3, 0.6]])
        >>> red = np.array([[0.1, 0.2], [0.2, 0.1]])
        >>> ndvi = calculate_ndvi(nir, red)
        >>> print(ndvi)
        [[0.6  0.428...]
         [0.2  0.714...]]
    """
    # Validate input shapes
    if nir.shape != red.shape:
        raise ValueError(
            f"Input arrays must have the same shape. "
            f"NIR shape: {nir.shape}, Red shape: {red.shape}"
        )
    
    # Convert to float64 for precision
    nir = nir.astype(np.float64)
    red = red.astype(np.float64)
    
    # Create output array filled with nodata
    ndvi = np.full(nir.shape, nodata_value, dtype=np.float64)
    
    # Calculate sum for denominator
    denominator = nir + red
    
    # Create mask for valid pixels:
    # - Both bands have valid data (not nodata)
    # - Denominator is not zero (avoid division by zero)
    # - Values are finite
    valid_mask = (
        np.isfinite(nir) & 
        np.isfinite(red) & 
        (nir != nodata_value) & 
        (red != nodata_value) &
        (denominator != 0)
    )
    
    # Calculate NDVI only for valid pixels
    ndvi[valid_mask] = (nir[valid_mask] - red[valid_mask]) / denominator[valid_mask]
    
    # Clip values to valid NDVI range [-1, 1]
    # Only clip valid pixels to preserve nodata values
    ndvi[valid_mask] = np.clip(ndvi[valid_mask], -1.0, 1.0)
    
    return ndvi


def classify_ndvi(
    ndvi: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> NDArray[np.int8]:
    """
    Classify NDVI values into land cover categories.
    
    Categories:
        0 (WATER): NDVI < 0
        1 (URBAN_BARE_SOIL): 0 <= NDVI < 0.2
        2 (SPARSE_VEGETATION): 0.2 <= NDVI < 0.4
        3 (DENSE_VEGETATION): NDVI >= 0.4
    
    Args:
        ndvi: NumPy array with NDVI values (from calculate_ndvi)
        nodata_value: Value indicating no-data pixels (default: -9999.0)
    
    Returns:
        NumPy array with classification values (0-3).
        NoData pixels are set to -1.
    
    Example:
        >>> ndvi = np.array([[-0.2, 0.1], [0.3, 0.6]])
        >>> classified = classify_ndvi(ndvi)
        >>> print(classified)
        [[0 1]
         [2 3]]
    """
    # Initialize with -1 for nodata
    classified = np.full(ndvi.shape, -1, dtype=np.int8)
    
    # Create mask for valid NDVI values
    valid_mask = (ndvi != nodata_value) & np.isfinite(ndvi)
    
    # Classify valid pixels
    # Water: NDVI < 0
    water_mask = valid_mask & (ndvi < NDVI_THRESHOLDS["water_max"])
    classified[water_mask] = NDVICategory.WATER
    
    # Urban/Bare soil: 0 <= NDVI < 0.2
    urban_mask = valid_mask & (ndvi >= NDVI_THRESHOLDS["water_max"]) & (ndvi < NDVI_THRESHOLDS["urban_max"])
    classified[urban_mask] = NDVICategory.URBAN_BARE_SOIL
    
    # Sparse vegetation: 0.2 <= NDVI < 0.4
    sparse_mask = valid_mask & (ndvi >= NDVI_THRESHOLDS["urban_max"]) & (ndvi < NDVI_THRESHOLDS["sparse_max"])
    classified[sparse_mask] = NDVICategory.SPARSE_VEGETATION
    
    # Dense vegetation: NDVI >= 0.4
    dense_mask = valid_mask & (ndvi >= NDVI_THRESHOLDS["sparse_max"])
    classified[dense_mask] = NDVICategory.DENSE_VEGETATION
    
    return classified


def get_ndvi_statistics(
    ndvi: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> Dict[str, float]:
    """
    Calculate statistics for an NDVI array.
    
    Args:
        ndvi: NumPy array with NDVI values
        nodata_value: Value indicating no-data pixels
    
    Returns:
        Dictionary containing:
        - min: Minimum NDVI value
        - max: Maximum NDVI value
        - mean: Mean NDVI value
        - std: Standard deviation
        - valid_pixels: Count of valid pixels
        - total_pixels: Total pixel count
    """
    # Mask valid pixels
    valid_mask = (ndvi != nodata_value) & np.isfinite(ndvi)
    valid_values = ndvi[valid_mask]
    
    if len(valid_values) == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "valid_pixels": 0,
            "total_pixels": int(ndvi.size),
        }
    
    return {
        "min": float(np.min(valid_values)),
        "max": float(np.max(valid_values)),
        "mean": float(np.mean(valid_values)),
        "std": float(np.std(valid_values)),
        "valid_pixels": int(np.sum(valid_mask)),
        "total_pixels": int(ndvi.size),
    }


def get_classification_percentages(
    classified: NDArray[np.int8],
) -> Dict[str, float]:
    """
    Calculate the percentage of each land cover category.
    
    Args:
        classified: Classified NDVI array from classify_ndvi()
    
    Returns:
        Dictionary with category names and their percentages.
    """
    # Count valid pixels (not -1)
    valid_mask = classified >= 0
    total_valid = np.sum(valid_mask)
    
    if total_valid == 0:
        return {
            "water": 0.0,
            "urban_bare_soil": 0.0,
            "sparse_vegetation": 0.0,
            "dense_vegetation": 0.0,
        }
    
    return {
        "water": float(np.sum(classified == NDVICategory.WATER) / total_valid * 100),
        "urban_bare_soil": float(np.sum(classified == NDVICategory.URBAN_BARE_SOIL) / total_valid * 100),
        "sparse_vegetation": float(np.sum(classified == NDVICategory.SPARSE_VEGETATION) / total_valid * 100),
        "dense_vegetation": float(np.sum(classified == NDVICategory.DENSE_VEGETATION) / total_valid * 100),
    }
