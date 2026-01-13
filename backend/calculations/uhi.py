"""
UHI (Urban Heat Island) Analysis Module

This module provides functions for analyzing Urban Heat Island effects
using Land Surface Temperature (LST) and land cover classification.

The Urban Heat Island effect is quantified by comparing temperatures
between urban and rural (vegetated) areas.

Key Metrics:
- UHI Intensity: Difference between urban and rural mean temperatures
- Hotspots: Areas significantly warmer than the mean (> mean + 2*std)
- Affected Area: Total area of hotspot regions

References:
- Oke, T.R. (1982). The energetic basis of the urban heat island
- Voogt, J.A., & Oke, T.R. (2003). Thermal remote sensing of urban climates
"""

import numpy as np
from numpy.typing import NDArray
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import IntEnum

# Import land cover classes
from .land_cover import LandCoverClass


@dataclass(frozen=True)
class UHIThresholds:
    """Thresholds for UHI analysis."""
    # Standard deviations above mean for hotspot detection
    HOTSPOT_STD_THRESHOLD: float = 2.0
    
    # Minimum cluster size (pixels) to be considered a significant hotspot
    MIN_CLUSTER_SIZE: int = 10
    
    # Landsat pixel resolution in meters
    PIXEL_RESOLUTION_M: float = 30.0


class UHICategory(IntEnum):
    """UHI intensity categories."""
    NONE = 0
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


# UHI intensity thresholds (°C)
UHI_INTENSITY_THRESHOLDS = {
    UHICategory.NONE: 0.0,
    UHICategory.WEAK: 2.0,
    UHICategory.MODERATE: 4.0,
    UHICategory.STRONG: 6.0,
    UHICategory.VERY_STRONG: 8.0,
}

UHI_CATEGORY_NAMES = {
    UHICategory.NONE: "No UHI Effect",
    UHICategory.WEAK: "Weak",
    UHICategory.MODERATE: "Moderate",
    UHICategory.STRONG: "Strong",
    UHICategory.VERY_STRONG: "Very Strong",
}


THRESHOLDS = UHIThresholds()


def calculate_zone_temperature(
    lst: NDArray[np.floating],
    mask: NDArray[np.bool_],
    nodata_value: float = -9999.0,
) -> Dict[str, Optional[float]]:
    """
    Calculate temperature statistics for a specific zone.
    
    Args:
        lst: LST array in Celsius
        mask: Boolean mask for the zone of interest
        nodata_value: Value indicating no-data pixels
    
    Returns:
        Dictionary with min, max, mean, std, and pixel count
    """
    # Combine mask with valid LST data
    valid_mask = mask & (lst != nodata_value) & np.isfinite(lst)
    valid_temps = lst[valid_mask]
    
    if len(valid_temps) == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "pixel_count": 0,
        }
    
    return {
        "min": float(np.min(valid_temps)),
        "max": float(np.max(valid_temps)),
        "mean": float(np.mean(valid_temps)),
        "std": float(np.std(valid_temps)),
        "pixel_count": int(len(valid_temps)),
    }


def identify_hotspots(
    lst: NDArray[np.floating],
    std_threshold: float = THRESHOLDS.HOTSPOT_STD_THRESHOLD,
    nodata_value: float = -9999.0,
    mean_temp: Optional[float] = None,
    std_temp: Optional[float] = None,
) -> Tuple[NDArray[np.bool_], Dict[str, float]]:
    """
    Identify thermal hotspots in LST data.
    
    Hotspots are defined as pixels where:
    temperature > mean + (std_threshold * std)
    
    Args:
        lst: LST array in Celsius
        std_threshold: Number of standard deviations above mean (default: 2.0)
        nodata_value: Value indicating no-data pixels
        mean_temp: Optional pre-calculated mean temperature
        std_temp: Optional pre-calculated standard deviation
    
    Returns:
        Tuple of:
        - Boolean mask of hotspot pixels
        - Dictionary with threshold info (mean, std, threshold_temp)
    """
    # Create valid data mask
    valid_mask = (lst != nodata_value) & np.isfinite(lst)
    valid_temps = lst[valid_mask]
    
    if len(valid_temps) == 0:
        return np.zeros(lst.shape, dtype=bool), {
            "mean": None,
            "std": None,
            "threshold_temp": None,
        }
    
    # Calculate stats if not provided
    if mean_temp is None:
        mean_temp = float(np.mean(valid_temps))
    if std_temp is None:
        std_temp = float(np.std(valid_temps))
    
    # Calculate threshold temperature
    threshold_temp = mean_temp + (std_threshold * std_temp)
    
    # Create hotspot mask
    hotspot_mask = valid_mask & (lst > threshold_temp)
    
    return hotspot_mask, {
        "mean": mean_temp,
        "std": std_temp,
        "threshold_temp": threshold_temp,
        "std_threshold": std_threshold,
    }


def count_hotspot_clusters(
    hotspot_mask: NDArray[np.bool_],
    min_cluster_size: int = THRESHOLDS.MIN_CLUSTER_SIZE,
) -> Tuple[int, NDArray[np.int32]]:
    """
    Count connected hotspot clusters using connected component labeling.
    
    Uses a simple 4-connectivity flood fill algorithm.
    For production use, consider scipy.ndimage.label for better performance.
    
    Args:
        hotspot_mask: Boolean mask of hotspot pixels
        min_cluster_size: Minimum pixels for a valid cluster
    
    Returns:
        Tuple of:
        - Number of clusters meeting minimum size
        - Labeled array where each cluster has a unique ID
    """
    # Initialize labels
    labels = np.zeros(hotspot_mask.shape, dtype=np.int32)
    current_label = 0
    
    # Get hotspot coordinates
    hotspot_coords = np.argwhere(hotspot_mask)
    
    if len(hotspot_coords) == 0:
        return 0, labels
    
    # Create a set of unvisited hotspot pixels
    unvisited = set(map(tuple, hotspot_coords))
    
    cluster_sizes = []
    
    while unvisited:
        # Start new cluster
        current_label += 1
        start = unvisited.pop()
        
        # BFS to find connected pixels
        queue = [start]
        cluster_size = 0
        
        while queue:
            pixel = queue.pop(0)
            row, col = pixel
            
            if labels[row, col] != 0:
                continue
            
            labels[row, col] = current_label
            cluster_size += 1
            
            # Check 4-connected neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                
                if 0 <= nr < hotspot_mask.shape[0] and 0 <= nc < hotspot_mask.shape[1]:
                    if hotspot_mask[nr, nc] and (nr, nc) in unvisited:
                        queue.append((nr, nc))
                        unvisited.discard((nr, nc))
        
        cluster_sizes.append(cluster_size)
    
    # Count clusters meeting minimum size
    significant_clusters = sum(1 for size in cluster_sizes if size >= min_cluster_size)
    
    return significant_clusters, labels


def calculate_affected_area(
    hotspot_mask: NDArray[np.bool_],
    pixel_resolution_m: float = THRESHOLDS.PIXEL_RESOLUTION_M,
) -> Dict[str, float]:
    """
    Calculate the total area affected by hotspots.
    
    Args:
        hotspot_mask: Boolean mask of hotspot pixels
        pixel_resolution_m: Pixel size in meters (default: 30m for Landsat)
    
    Returns:
        Dictionary with area in various units
    """
    hotspot_count = int(np.sum(hotspot_mask))
    
    # Calculate area
    pixel_area_m2 = pixel_resolution_m ** 2  # 900 m² for 30m pixels
    total_area_m2 = hotspot_count * pixel_area_m2
    total_area_km2 = total_area_m2 / 1_000_000  # Convert to km²
    total_area_ha = total_area_m2 / 10_000  # Convert to hectares
    
    return {
        "pixel_count": hotspot_count,
        "pixel_resolution_m": pixel_resolution_m,
        "area_m2": total_area_m2,
        "area_km2": round(total_area_km2, 4),
        "area_ha": round(total_area_ha, 2),
    }


def classify_uhi_intensity(intensity: float) -> UHICategory:
    """
    Classify UHI intensity into categories.
    
    Categories:
    - None: < 2°C
    - Weak: 2-4°C
    - Moderate: 4-6°C
    - Strong: 6-8°C
    - Very Strong: > 8°C
    
    Args:
        intensity: UHI intensity in Celsius
    
    Returns:
        UHICategory enum value
    """
    if intensity < UHI_INTENSITY_THRESHOLDS[UHICategory.WEAK]:
        return UHICategory.NONE
    elif intensity < UHI_INTENSITY_THRESHOLDS[UHICategory.MODERATE]:
        return UHICategory.WEAK
    elif intensity < UHI_INTENSITY_THRESHOLDS[UHICategory.STRONG]:
        return UHICategory.MODERATE
    elif intensity < UHI_INTENSITY_THRESHOLDS[UHICategory.VERY_STRONG]:
        return UHICategory.STRONG
    else:
        return UHICategory.VERY_STRONG


def analyze_uhi(
    lst: NDArray[np.floating],
    land_cover: NDArray[np.int8],
    nodata_value: float = -9999.0,
    pixel_resolution_m: float = THRESHOLDS.PIXEL_RESOLUTION_M,
    hotspot_std_threshold: float = THRESHOLDS.HOTSPOT_STD_THRESHOLD,
) -> Dict[str, Any]:
    """
    Comprehensive Urban Heat Island analysis.
    
    Calculates:
    1. Urban mean temperature (from urban/built-up pixels)
    2. Rural mean temperature (from vegetation pixels)
    3. UHI intensity (urban - rural)
    4. Hotspot identification and counting
    5. Affected area estimation
    
    Args:
        lst: LST array in Celsius
        land_cover: Land cover classification array
        nodata_value: Value indicating no-data pixels
        pixel_resolution_m: Pixel size in meters
        hotspot_std_threshold: Std devs above mean for hotspots
    
    Returns:
        Dictionary containing all UHI analysis results
    """
    # Validate input shapes
    if lst.shape != land_cover.shape:
        raise ValueError(
            f"LST and land cover arrays must have same shape. "
            f"LST: {lst.shape}, Land cover: {land_cover.shape}"
        )
    
    # Create masks for urban and vegetation (rural reference)
    urban_mask = land_cover == LandCoverClass.URBAN
    vegetation_mask = land_cover == LandCoverClass.VEGETATION
    
    # Calculate zone temperatures
    urban_stats = calculate_zone_temperature(lst, urban_mask, nodata_value)
    rural_stats = calculate_zone_temperature(lst, vegetation_mask, nodata_value)
    
    # Calculate UHI intensity
    uhi_intensity = None
    uhi_category = UHICategory.NONE
    
    if urban_stats["mean"] is not None and rural_stats["mean"] is not None:
        uhi_intensity = urban_stats["mean"] - rural_stats["mean"]
        uhi_category = classify_uhi_intensity(uhi_intensity)
    
    # Identify hotspots
    hotspot_mask, hotspot_info = identify_hotspots(
        lst, 
        std_threshold=hotspot_std_threshold,
        nodata_value=nodata_value
    )
    
    # Count hotspot clusters
    cluster_count, cluster_labels = count_hotspot_clusters(hotspot_mask)
    
    # Calculate affected area
    area_stats = calculate_affected_area(hotspot_mask, pixel_resolution_m)
    
    # Calculate overall LST statistics
    valid_mask = (lst != nodata_value) & np.isfinite(lst)
    overall_stats = {
        "min": float(np.min(lst[valid_mask])) if np.any(valid_mask) else None,
        "max": float(np.max(lst[valid_mask])) if np.any(valid_mask) else None,
        "mean": float(np.mean(lst[valid_mask])) if np.any(valid_mask) else None,
        "std": float(np.std(lst[valid_mask])) if np.any(valid_mask) else None,
    }
    
    return {
        # Primary UHI metrics
        "uhi_intensity": round(uhi_intensity, 2) if uhi_intensity is not None else None,
        "uhi_category": UHI_CATEGORY_NAMES[uhi_category],
        "uhi_category_value": int(uhi_category),
        
        # Temperature statistics
        "urban_mean_temp": round(urban_stats["mean"], 2) if urban_stats["mean"] else None,
        "rural_mean_temp": round(rural_stats["mean"], 2) if rural_stats["mean"] else None,
        "urban_stats": urban_stats,
        "rural_stats": rural_stats,
        "overall_stats": overall_stats,
        
        # Hotspot analysis
        "hotspot_count": int(np.sum(hotspot_mask)),
        "hotspot_cluster_count": cluster_count,
        "hotspot_threshold_temp": round(hotspot_info["threshold_temp"], 2) if hotspot_info["threshold_temp"] else None,
        
        # Area statistics
        "affected_area_km2": area_stats["area_km2"],
        "affected_area_ha": area_stats["area_ha"],
        "affected_pixels": area_stats["pixel_count"],
        
        # Masks for visualization
        "hotspot_mask": hotspot_mask,
        "cluster_labels": cluster_labels,
        
        # Metadata
        "pixel_resolution_m": pixel_resolution_m,
        "unit": "Celsius",
    }


def create_uhi_map(
    lst: NDArray[np.floating],
    land_cover: NDArray[np.int8],
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Create a UHI intensity map (temperature anomaly from rural mean).
    
    Each pixel value represents how much warmer it is compared to
    the rural (vegetation) mean temperature.
    
    Args:
        lst: LST array in Celsius
        land_cover: Land cover classification array
        nodata_value: Value indicating no-data pixels
    
    Returns:
        Array with temperature anomaly values (positive = warmer than rural)
    """
    # Get rural reference temperature
    vegetation_mask = land_cover == LandCoverClass.VEGETATION
    rural_stats = calculate_zone_temperature(lst, vegetation_mask, nodata_value)
    
    if rural_stats["mean"] is None:
        return np.full(lst.shape, nodata_value, dtype=np.float64)
    
    rural_mean = rural_stats["mean"]
    
    # Create anomaly map
    uhi_map = np.full(lst.shape, nodata_value, dtype=np.float64)
    valid_mask = (lst != nodata_value) & np.isfinite(lst)
    uhi_map[valid_mask] = lst[valid_mask] - rural_mean
    
    return uhi_map


def create_hotspot_visualization(
    hotspot_mask: NDArray[np.bool_],
    intensity: Optional[NDArray[np.floating]] = None,
    alpha: bool = True,
) -> NDArray[np.uint8]:
    """
    Create a color-coded visualization of hotspots.
    
    If intensity is provided, uses a gradient from yellow to red.
    Otherwise, uses solid red for hotspots.
    
    Args:
        hotspot_mask: Boolean mask of hotspot pixels
        intensity: Optional array to use for color intensity
        alpha: Include alpha channel
    
    Returns:
        RGBA array for visualization (uint8)
    """
    height, width = hotspot_mask.shape
    channels = 4 if alpha else 3
    
    # Initialize transparent/black
    rgb = np.zeros((height, width, channels), dtype=np.uint8)
    
    if intensity is not None and np.any(hotspot_mask):
        # Normalize intensity for color mapping
        valid_intensity = intensity[hotspot_mask]
        min_val = np.min(valid_intensity)
        max_val = np.max(valid_intensity)
        
        if max_val > min_val:
            # Create gradient: yellow (low) to red (high)
            normalized = (intensity - min_val) / (max_val - min_val)
            
            # R channel: always 255 for hotspots
            rgb[hotspot_mask, 0] = 255
            
            # G channel: 255 (yellow) to 0 (red) based on intensity
            rgb[hotspot_mask, 1] = (255 * (1 - normalized[hotspot_mask])).astype(np.uint8)
            
            # B channel: 0
            rgb[hotspot_mask, 2] = 0
        else:
            # All same intensity, use solid orange
            rgb[hotspot_mask, 0] = 255
            rgb[hotspot_mask, 1] = 100
            rgb[hotspot_mask, 2] = 0
    else:
        # Solid red for hotspots
        rgb[hotspot_mask, 0] = 255
        rgb[hotspot_mask, 1] = 50
        rgb[hotspot_mask, 2] = 50
    
    if alpha:
        # Set alpha: opaque for hotspots, transparent otherwise
        rgb[hotspot_mask, 3] = 200  # Slightly transparent
    
    return rgb


def get_uhi_summary(analysis_result: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of UHI analysis.
    
    Args:
        analysis_result: Result dictionary from analyze_uhi()
    
    Returns:
        Formatted summary string
    """
    lines = [
        "=" * 50,
        "URBAN HEAT ISLAND ANALYSIS SUMMARY",
        "=" * 50,
        "",
        f"UHI Intensity: {analysis_result['uhi_intensity']}°C ({analysis_result['uhi_category']})",
        "",
        "Temperature Statistics:",
        f"  Urban Mean:  {analysis_result['urban_mean_temp']}°C",
        f"  Rural Mean:  {analysis_result['rural_mean_temp']}°C",
        "",
        "Hotspot Analysis:",
        f"  Total Hotspots:    {analysis_result['hotspot_count']:,} pixels",
        f"  Hotspot Clusters:  {analysis_result['hotspot_cluster_count']}",
        f"  Threshold Temp:    {analysis_result['hotspot_threshold_temp']}°C",
        "",
        "Affected Area:",
        f"  {analysis_result['affected_area_km2']} km²",
        f"  {analysis_result['affected_area_ha']} hectares",
        "",
        "=" * 50,
    ]
    
    return "\n".join(lines)
