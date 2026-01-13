"""
Heatmap Data Generator Module

This module provides utilities for converting raster data (LST arrays)
into JSON-serializable heatmap data for frontend visualization.

Features:
- Converts pixel coordinates to geographic coordinates (lat/lon)
- Intelligent sampling to reduce data size
- Filters invalid values (NoData, NaN, Inf)
- Supports coordinate system reprojection
- Optimized for performance with large rasters
"""

import numpy as np
from numpy.typing import NDArray
from typing import Dict, List, Optional, Tuple, TypedDict, Union
from dataclasses import dataclass, field
import math

# Try to import rasterio and pyproj for coordinate transformation
try:
    import rasterio
    from rasterio.transform import xy, Affine
    from rasterio.crs import CRS
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


class HeatmapPoint(TypedDict):
    """Type definition for a heatmap data point."""
    lat: float
    lon: float
    temp: float


@dataclass
class HeatmapConfig:
    """Configuration for heatmap generation."""
    max_points: int = 5000
    sample_step: Optional[int] = None  # Auto-calculated if None
    default_sample_step: int = 10      # Default sampling every 10th pixel
    nodata_value: float = -9999.0
    min_valid_temp: float = -50.0      # Minimum valid temperature (Celsius)
    max_valid_temp: float = 80.0       # Maximum valid temperature (Celsius)
    decimal_places_latlon: int = 6     # Precision for lat/lon
    decimal_places_temp: int = 2       # Precision for temperature
    target_crs: str = "EPSG:4326"      # Output coordinate system (WGS84)


def is_valid_temperature(
    temp: float,
    nodata_value: float = -9999.0,
    min_temp: float = -50.0,
    max_temp: float = 80.0,
) -> bool:
    """
    Check if a temperature value is valid.
    
    Args:
        temp: Temperature value to check
        nodata_value: NoData value to filter
        min_temp: Minimum valid temperature
        max_temp: Maximum valid temperature
    
    Returns:
        True if temperature is valid, False otherwise
    """
    if temp == nodata_value:
        return False
    if not np.isfinite(temp):
        return False
    if temp < min_temp or temp > max_temp:
        return False
    return True


def calculate_optimal_sample_step(
    height: int,
    width: int,
    max_points: int,
) -> int:
    """
    Calculate optimal sampling step to achieve approximately max_points.
    
    Args:
        height: Raster height in pixels
        width: Raster width in pixels
        max_points: Maximum number of output points
    
    Returns:
        Sampling step (e.g., 10 means every 10th pixel)
    """
    total_pixels = height * width
    
    if total_pixels <= max_points:
        return 1
    
    # Calculate step based on desired density
    # We want: (height / step) * (width / step) ≈ max_points
    # Therefore: step ≈ sqrt(total_pixels / max_points)
    step = int(math.ceil(math.sqrt(total_pixels / max_points)))
    
    return max(1, step)


def pixel_to_latlon(
    row: int,
    col: int,
    transform: "Affine",
    source_crs: Optional[str] = None,
    target_crs: str = "EPSG:4326",
) -> Tuple[float, float]:
    """
    Convert pixel coordinates to latitude/longitude.
    
    Args:
        row: Row index (y)
        col: Column index (x)
        transform: Rasterio affine transform
        source_crs: Source coordinate reference system
        target_crs: Target CRS (default: WGS84)
    
    Returns:
        Tuple of (latitude, longitude)
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for coordinate transformation")
    
    # Get coordinates in source CRS
    x, y = xy(transform, row, col, offset="center")
    
    # If source CRS is different from target, reproject
    if source_crs and source_crs != target_crs:
        from pyproj import Transformer
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        x, y = transformer.transform(x, y)
    
    # Return as (lat, lon) - note y is lat, x is lon
    return (y, x)



def generate_heatmap_data(
    lst: NDArray[np.floating],
    transform: "Affine",
    source_crs: Optional[str] = None,
    config: Optional[HeatmapConfig] = None,
) -> List[HeatmapPoint]:
    """
    Generate heatmap data from LST array with geospatial transform.
    
    This is the main function for creating frontend-ready heatmap data.
    
    Args:
        lst: 2D NumPy array with Land Surface Temperature values (Celsius)
        transform: Rasterio affine transform for coordinate conversion
        source_crs: Source coordinate reference system (e.g., "EPSG:32632")
        config: HeatmapConfig object with generation parameters
    
    Returns:
        List of HeatmapPoint dictionaries with lat, lon, temp
    
    Example:
        >>> with rasterio.open("lst.tif") as src:
        ...     data = src.read(1)
        ...     heatmap = generate_heatmap_data(
        ...         data, src.transform, str(src.crs)
        ...     )
        >>> print(len(heatmap))
        4500
        >>> print(heatmap[0])
        {'lat': 9.0821, 'lon': 8.6754, 'temp': 35.2}
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for heatmap generation")
    
    # Use default config if not provided
    if config is None:
        config = HeatmapConfig()
    
    height, width = lst.shape
    
    # Calculate optimal sampling step
    if config.sample_step is None:
        sample_step = calculate_optimal_sample_step(
            height, width, config.max_points
        )
    else:
        sample_step = config.sample_step
    
    # Ensure minimum step of 1
    sample_step = max(1, sample_step)
    
    heatmap_data: List[HeatmapPoint] = []
    
    # Iterate with sampling
    for row in range(0, height, sample_step):
        for col in range(0, width, sample_step):
            temp = float(lst[row, col])
            
            # Validate temperature
            if not is_valid_temperature(
                temp,
                config.nodata_value,
                config.min_valid_temp,
                config.max_valid_temp,
            ):
                continue
            
            # Convert pixel to lat/lon
            try:
                lat, lon = pixel_to_latlon(
                    row, col, transform, source_crs, config.target_crs
                )
            except Exception:
                # Skip if coordinate conversion fails
                continue
            
            # Create point with rounded values
            point: HeatmapPoint = {
                "lat": round(lat, config.decimal_places_latlon),
                "lon": round(lon, config.decimal_places_latlon),
                "temp": round(temp, config.decimal_places_temp),
            }
            
            heatmap_data.append(point)
            
            # Check max points limit
            if len(heatmap_data) >= config.max_points:
                return heatmap_data
    
    return heatmap_data


def generate_heatmap_from_array(
    lst: NDArray[np.floating],
    bounds: Tuple[float, float, float, float],
    config: Optional[HeatmapConfig] = None,
) -> List[HeatmapPoint]:
    """
    Generate heatmap data from LST array using bounding box.
    
    Alternative to generate_heatmap_data when only bounds are available
    (no rasterio transform).
    
    Args:
        lst: 2D NumPy array with LST values
        bounds: Tuple of (min_lon, min_lat, max_lon, max_lat) in WGS84
        config: HeatmapConfig object
    
    Returns:
        List of HeatmapPoint dictionaries
    
    Example:
        >>> bounds = (8.0, 9.0, 9.0, 10.0)  # (min_lon, min_lat, max_lon, max_lat)
        >>> heatmap = generate_heatmap_from_array(lst, bounds)
    """
    if config is None:
        config = HeatmapConfig()
    
    height, width = lst.shape
    min_lon, min_lat, max_lon, max_lat = bounds
    
    # Calculate pixel size in degrees
    pixel_width = (max_lon - min_lon) / width
    pixel_height = (max_lat - min_lat) / height
    
    # Calculate sampling step
    if config.sample_step is None:
        sample_step = calculate_optimal_sample_step(
            height, width, config.max_points
        )
    else:
        sample_step = config.sample_step
    
    sample_step = max(1, sample_step)
    
    heatmap_data: List[HeatmapPoint] = []
    
    for row in range(0, height, sample_step):
        for col in range(0, width, sample_step):
            temp = float(lst[row, col])
            
            if not is_valid_temperature(
                temp,
                config.nodata_value,
                config.min_valid_temp,
                config.max_valid_temp,
            ):
                continue
            
            # Calculate coordinates
            # Note: row 0 is at max_lat (top of image)
            lat = max_lat - (row + 0.5) * pixel_height
            lon = min_lon + (col + 0.5) * pixel_width
            
            point: HeatmapPoint = {
                "lat": round(lat, config.decimal_places_latlon),
                "lon": round(lon, config.decimal_places_latlon),
                "temp": round(temp, config.decimal_places_temp),
            }
            
            heatmap_data.append(point)
            
            if len(heatmap_data) >= config.max_points:
                return heatmap_data
    
    return heatmap_data


def get_heatmap_statistics(heatmap_data: List[HeatmapPoint]) -> Dict[str, any]:
    """
    Calculate statistics for heatmap data.
    
    Args:
        heatmap_data: List of heatmap points
    
    Returns:
        Dictionary with min, max, mean, std of temperatures
    """
    if not heatmap_data:
        return {
            "count": 0,
            "min_temp": None,
            "max_temp": None,
            "mean_temp": None,
            "std_temp": None,
            "min_lat": None,
            "max_lat": None,
            "min_lon": None,
            "max_lon": None,
        }
    
    temps = [p["temp"] for p in heatmap_data]
    lats = [p["lat"] for p in heatmap_data]
    lons = [p["lon"] for p in heatmap_data]
    
    return {
        "count": len(heatmap_data),
        "min_temp": min(temps),
        "max_temp": max(temps),
        "mean_temp": round(sum(temps) / len(temps), 2),
        "std_temp": round(float(np.std(temps)), 2),
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lon": min(lons),
        "max_lon": max(lons),
    }


def filter_heatmap_by_bounds(
    heatmap_data: List[HeatmapPoint],
    bounds: Tuple[float, float, float, float],
) -> List[HeatmapPoint]:
    """
    Filter heatmap points to only include those within bounds.
    
    Args:
        heatmap_data: List of heatmap points
        bounds: Tuple of (min_lon, min_lat, max_lon, max_lat)
    
    Returns:
        Filtered list of heatmap points
    """
    min_lon, min_lat, max_lon, max_lat = bounds
    
    return [
        point for point in heatmap_data
        if (min_lat <= point["lat"] <= max_lat and
            min_lon <= point["lon"] <= max_lon)
    ]


def filter_heatmap_by_temperature(
    heatmap_data: List[HeatmapPoint],
    min_temp: Optional[float] = None,
    max_temp: Optional[float] = None,
) -> List[HeatmapPoint]:
    """
    Filter heatmap points by temperature range.
    
    Args:
        heatmap_data: List of heatmap points
        min_temp: Minimum temperature (inclusive)
        max_temp: Maximum temperature (inclusive)
    
    Returns:
        Filtered list of heatmap points
    """
    result = heatmap_data
    
    if min_temp is not None:
        result = [p for p in result if p["temp"] >= min_temp]
    
    if max_temp is not None:
        result = [p for p in result if p["temp"] <= max_temp]
    
    return result


def create_temperature_bins(
    heatmap_data: List[HeatmapPoint],
    num_bins: int = 10,
) -> Dict[str, List[HeatmapPoint]]:
    """
    Bin heatmap points by temperature for graduated visualization.
    
    Args:
        heatmap_data: List of heatmap points
        num_bins: Number of temperature bins
    
    Returns:
        Dictionary with bin labels as keys and points as values
    """
    if not heatmap_data:
        return {}
    
    temps = [p["temp"] for p in heatmap_data]
    min_temp = min(temps)
    max_temp = max(temps)
    bin_size = (max_temp - min_temp) / num_bins
    
    bins: Dict[str, List[HeatmapPoint]] = {}
    
    for i in range(num_bins):
        bin_min = min_temp + i * bin_size
        bin_max = min_temp + (i + 1) * bin_size
        bin_label = f"{bin_min:.1f}-{bin_max:.1f}"
        bins[bin_label] = []
    
    for point in heatmap_data:
        bin_index = min(int((point["temp"] - min_temp) / bin_size), num_bins - 1)
        bin_min = min_temp + bin_index * bin_size
        bin_max = min_temp + (bin_index + 1) * bin_size
        bin_label = f"{bin_min:.1f}-{bin_max:.1f}"
        bins[bin_label].append(point)
    
    return bins
