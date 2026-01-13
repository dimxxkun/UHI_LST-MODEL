"""
LST (Land Surface Temperature) Calculation Module

This module provides functions for calculating Land Surface Temperature
from Landsat 8/9 Band 10 (Thermal Infrared) imagery.

The LST calculation follows the Single-Channel Algorithm:
1. Convert Digital Numbers (DN) to Top-of-Atmosphere Radiance
2. Convert Radiance to Brightness Temperature
3. Estimate Land Surface Emissivity from NDVI
4. Calculate Land Surface Temperature using emissivity correction

References:
- USGS Landsat 8/9 Data Users Handbook
- Artis, D.A., & Carnahan, W.H. (1982). Survey of emissivity variability
- Sobrino, J.A., et al. (2004). Land surface temperature retrieval methods
"""

import numpy as np
from numpy.typing import NDArray
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


# Landsat 8/9 Band 10 Thermal Constants
@dataclass(frozen=True)
class ThermalConstants:
    """Constants for Landsat 8/9 Band 10 thermal calculations."""
    # Thermal conversion constants
    K1: float = 774.89    # Watts/(m² * sr * μm)
    K2: float = 1321.08   # Kelvin
    
    # Band 10 wavelength
    WAVELENGTH: float = 10.9e-6  # meters (10.9 μm)
    
    # Planck's radiation constant
    RHO: float = 1.438e-2  # m·K (h*c/σ = 0.01438 m·K)
    
    # Conversion
    KELVIN_TO_CELSIUS: float = 273.15


# Default metadata coefficients for Landsat 8/9 Band 10
# These should be extracted from the MTL file in practice
@dataclass
class RadianceCoefficients:
    """Radiometric rescaling coefficients from MTL metadata."""
    ML: float = 3.342e-4   # Multiplicative rescaling factor (RADIANCE_MULT_BAND_10)
    AL: float = 0.1        # Additive rescaling factor (RADIANCE_ADD_BAND_10)


# Emissivity estimation constants
@dataclass(frozen=True)
class EmissivityConstants:
    """Constants for NDVI-based emissivity estimation."""
    # NDVI thresholds for vegetation proportion
    NDVI_SOIL: float = 0.2    # Bare soil threshold
    NDVI_VEG: float = 0.5     # Full vegetation threshold
    
    # Emissivity values
    EMISSIVITY_SOIL: float = 0.97
    EMISSIVITY_VEG: float = 0.99
    
    # Simplified emissivity model coefficients
    # ε = 0.004 * Pv + 0.986
    COEFF_PV: float = 0.004
    COEFF_BASE: float = 0.986


THERMAL = ThermalConstants()
EMISSIVITY = EmissivityConstants()


def dn_to_radiance(
    band_10: NDArray[np.floating],
    ml: float = RadianceCoefficients.ML,
    al: float = RadianceCoefficients.AL,
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Convert Digital Numbers (DN) to Top-of-Atmosphere Spectral Radiance.
    
    Formula: L = ML * DN + AL
    
    Where:
    - L = TOA Spectral Radiance (Watts/(m² * sr * μm))
    - ML = Radiance multiplicative scaling factor (from MTL)
    - AL = Radiance additive scaling factor (from MTL)
    - DN = Digital Number (quantized calibrated pixel value)
    
    Args:
        band_10: NumPy array with Band 10 DN values
        ml: Multiplicative rescaling factor (RADIANCE_MULT_BAND_10)
        al: Additive rescaling factor (RADIANCE_ADD_BAND_10)
        nodata_value: Value for no-data pixels
    
    Returns:
        NumPy array with TOA Radiance values (W/(m²·sr·μm))
    """
    # Convert to float64
    band_10 = band_10.astype(np.float64)
    
    # Initialize output with nodata
    radiance = np.full(band_10.shape, nodata_value, dtype=np.float64)
    
    # Create valid data mask
    valid_mask = (band_10 != nodata_value) & np.isfinite(band_10) & (band_10 > 0)
    
    # Apply radiometric calibration
    radiance[valid_mask] = ml * band_10[valid_mask] + al
    
    # Ensure positive radiance values
    radiance[valid_mask & (radiance <= 0)] = nodata_value
    
    return radiance


def radiance_to_brightness_temperature(
    radiance: NDArray[np.floating],
    k1: float = THERMAL.K1,
    k2: float = THERMAL.K2,
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Convert TOA Radiance to Brightness Temperature.
    
    Formula: BT = K2 / ln((K1 / L) + 1)
    
    Where:
    - BT = Brightness Temperature (Kelvin)
    - K1 = Band-specific thermal constant (774.89 for Band 10)
    - K2 = Band-specific thermal constant (1321.08 for Band 10)
    - L = TOA Spectral Radiance
    
    Args:
        radiance: NumPy array with radiance values
        k1: Thermal constant K1 (default: 774.89)
        k2: Thermal constant K2 (default: 1321.08)
        nodata_value: Value for no-data pixels
    
    Returns:
        NumPy array with Brightness Temperature in Kelvin
    """
    # Initialize output with nodata
    bt = np.full(radiance.shape, nodata_value, dtype=np.float64)
    
    # Create valid mask (radiance must be positive)
    valid_mask = (radiance != nodata_value) & np.isfinite(radiance) & (radiance > 0)
    
    # Calculate brightness temperature
    # BT = K2 / ln((K1/L) + 1)
    bt[valid_mask] = k2 / np.log((k1 / radiance[valid_mask]) + 1)
    
    return bt


def estimate_emissivity_from_ndvi(
    ndvi: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> NDArray[np.floating]:
    """
    Estimate Land Surface Emissivity from NDVI.
    
    Uses the NDVI Threshold Method:
    1. Calculate Proportion of Vegetation (Pv):
       Pv = ((NDVI - NDVImin) / (NDVImax - NDVImin))²
       
    2. Calculate Emissivity:
       ε = 0.004 * Pv + 0.986
    
    For special cases:
    - NDVI < 0.2 (bare soil): ε ≈ 0.97
    - NDVI > 0.5 (full vegetation): ε ≈ 0.99
    
    Args:
        ndvi: NumPy array with NDVI values (-1 to 1)
        nodata_value: Value for no-data pixels
    
    Returns:
        NumPy array with emissivity values (typically 0.95 to 1.0)
    """
    # Initialize output with nodata
    emissivity = np.full(ndvi.shape, nodata_value, dtype=np.float64)
    
    # Create valid mask
    valid_mask = (ndvi != nodata_value) & np.isfinite(ndvi)
    
    # Initialize valid pixels
    emissivity[valid_mask] = EMISSIVITY.EMISSIVITY_SOIL
    
    # Case 1: Bare soil (NDVI < 0.2)
    soil_mask = valid_mask & (ndvi < EMISSIVITY.NDVI_SOIL)
    emissivity[soil_mask] = EMISSIVITY.EMISSIVITY_SOIL
    
    # Case 2: Full vegetation (NDVI > 0.5)
    veg_mask = valid_mask & (ndvi > EMISSIVITY.NDVI_VEG)
    emissivity[veg_mask] = EMISSIVITY.EMISSIVITY_VEG
    
    # Case 3: Mixed (0.2 <= NDVI <= 0.5)
    mixed_mask = valid_mask & (ndvi >= EMISSIVITY.NDVI_SOIL) & (ndvi <= EMISSIVITY.NDVI_VEG)
    
    # Calculate Proportion of Vegetation (Pv)
    ndvi_range = EMISSIVITY.NDVI_VEG - EMISSIVITY.NDVI_SOIL
    pv = np.zeros(ndvi.shape, dtype=np.float64)
    pv[mixed_mask] = ((ndvi[mixed_mask] - EMISSIVITY.NDVI_SOIL) / ndvi_range) ** 2
    
    # Calculate emissivity: ε = 0.004 * Pv + 0.986
    emissivity[mixed_mask] = EMISSIVITY.COEFF_PV * pv[mixed_mask] + EMISSIVITY.COEFF_BASE
    
    return emissivity


def calculate_lst(
    brightness_temp: NDArray[np.floating],
    emissivity: NDArray[np.floating],
    wavelength: float = THERMAL.WAVELENGTH,
    rho: float = THERMAL.RHO,
    nodata_value: float = -9999.0,
    output_celsius: bool = True,
) -> NDArray[np.floating]:
    """
    Calculate Land Surface Temperature using emissivity correction.
    
    Formula: LST = BT / (1 + (λ * BT / ρ) * ln(ε))
    
    Where:
    - LST = Land Surface Temperature
    - BT = Brightness Temperature (Kelvin)
    - λ = Wavelength of emitted radiance (10.9 μm for Band 10)
    - ρ = h*c/σ = 1.438×10⁻² m·K
    - ε = Land Surface Emissivity
    
    Args:
        brightness_temp: Array with brightness temperature (Kelvin)
        emissivity: Array with emissivity values
        wavelength: Band 10 wavelength in meters (default: 10.9e-6)
        rho: Planck's constant ratio (default: 1.438e-2)
        nodata_value: Value for no-data pixels
        output_celsius: If True, convert output to Celsius (default: True)
    
    Returns:
        NumPy array with LST values in Celsius (or Kelvin if output_celsius=False)
    """
    if brightness_temp.shape != emissivity.shape:
        raise ValueError(
            f"Input arrays must have same shape. "
            f"BT: {brightness_temp.shape}, Emissivity: {emissivity.shape}"
        )
    
    # Initialize output with nodata
    lst = np.full(brightness_temp.shape, nodata_value, dtype=np.float64)
    
    # Create valid mask
    valid_mask = (
        (brightness_temp != nodata_value) & 
        (emissivity != nodata_value) & 
        np.isfinite(brightness_temp) & 
        np.isfinite(emissivity) &
        (emissivity > 0) &  # Emissivity must be positive for log
        (brightness_temp > 0)  # Temperature must be positive
    )
    
    # Calculate LST
    # LST = BT / (1 + (λ * BT / ρ) * ln(ε))
    bt = brightness_temp[valid_mask]
    eps = emissivity[valid_mask]
    
    lst[valid_mask] = bt / (1 + (wavelength * bt / rho) * np.log(eps))
    
    # Convert to Celsius if requested
    if output_celsius:
        lst[valid_mask] = lst[valid_mask] - THERMAL.KELVIN_TO_CELSIUS
    
    return lst


def calculate_lst_from_band10(
    band_10: NDArray[np.floating],
    ndvi: NDArray[np.floating],
    ml: float = RadianceCoefficients.ML,
    al: float = RadianceCoefficients.AL,
    nodata_value: float = -9999.0,
) -> Tuple[NDArray[np.floating], Dict[str, any]]:
    """
    Complete LST calculation pipeline from Band 10 DN and NDVI.
    
    This is a convenience function that chains all calculation steps:
    1. DN → Radiance
    2. Radiance → Brightness Temperature
    3. NDVI → Emissivity
    4. BT + Emissivity → LST
    
    Args:
        band_10: Band 10 Digital Number values
        ndvi: NDVI array (from calculate_ndvi)
        ml: Radiance multiplicative factor (from MTL)
        al: Radiance additive factor (from MTL)
        nodata_value: Value for no-data pixels
    
    Returns:
        Tuple of:
        - LST array in Celsius
        - Dictionary with intermediate results and statistics
    """
    # Step 1: DN to Radiance
    radiance = dn_to_radiance(band_10, ml, al, nodata_value)
    
    # Step 2: Radiance to Brightness Temperature
    bt = radiance_to_brightness_temperature(radiance, nodata_value=nodata_value)
    
    # Step 3: Estimate Emissivity from NDVI
    emissivity = estimate_emissivity_from_ndvi(ndvi, nodata_value)
    
    # Step 4: Calculate LST
    lst = calculate_lst(bt, emissivity, nodata_value=nodata_value)
    
    # Calculate statistics
    stats = get_lst_statistics(lst, nodata_value)
    
    return lst, {
        "radiance": radiance,
        "brightness_temperature": bt,
        "emissivity": emissivity,
        "statistics": stats,
    }


def get_lst_statistics(
    lst: NDArray[np.floating],
    nodata_value: float = -9999.0,
) -> Dict[str, Optional[float]]:
    """
    Calculate statistics for an LST array.
    
    Args:
        lst: NumPy array with LST values (Celsius)
        nodata_value: Value indicating no-data pixels
    
    Returns:
        Dictionary containing:
        - min: Minimum LST value
        - max: Maximum LST value
        - mean: Mean LST value
        - std: Standard deviation
        - median: Median value
        - valid_pixels: Count of valid pixels
        - total_pixels: Total pixel count
    """
    # Mask valid pixels
    valid_mask = (lst != nodata_value) & np.isfinite(lst)
    valid_values = lst[valid_mask]
    
    if len(valid_values) == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "median": None,
            "valid_pixels": 0,
            "total_pixels": int(lst.size),
            "unit": "Celsius",
        }
    
    return {
        "min": float(np.min(valid_values)),
        "max": float(np.max(valid_values)),
        "mean": float(np.mean(valid_values)),
        "std": float(np.std(valid_values)),
        "median": float(np.median(valid_values)),
        "valid_pixels": int(np.sum(valid_mask)),
        "total_pixels": int(lst.size),
        "unit": "Celsius",
    }


def classify_lst_thermal_zones(
    lst: NDArray[np.floating],
    mean_lst: Optional[float] = None,
    std_lst: Optional[float] = None,
    nodata_value: float = -9999.0,
) -> NDArray[np.int8]:
    """
    Classify LST into thermal comfort zones based on standard deviations from mean.
    
    Zones:
        0: Very Cold (< mean - 2*std)
        1: Cold (mean - 2*std to mean - 1*std)
        2: Cool (mean - 1*std to mean - 0.5*std)
        3: Comfortable (mean - 0.5*std to mean + 0.5*std)
        4: Warm (mean + 0.5*std to mean + 1*std)
        5: Hot (mean + 1*std to mean + 2*std)
        6: Very Hot (> mean + 2*std)
    
    Args:
        lst: LST array in Celsius
        mean_lst: Optional pre-calculated mean (calculated if not provided)
        std_lst: Optional pre-calculated std (calculated if not provided)
        nodata_value: Value for no-data pixels
    
    Returns:
        Classified array with zone values (0-6), -1 for nodata
    """
    # Calculate stats if not provided
    if mean_lst is None or std_lst is None:
        stats = get_lst_statistics(lst, nodata_value)
        mean_lst = stats["mean"]
        std_lst = stats["std"]
    
    if mean_lst is None or std_lst is None:
        return np.full(lst.shape, -1, dtype=np.int8)
    
    # Initialize with nodata
    zones = np.full(lst.shape, -1, dtype=np.int8)
    
    # Valid mask
    valid_mask = (lst != nodata_value) & np.isfinite(lst)
    
    # Define thresholds
    thresholds = [
        mean_lst - 2 * std_lst,
        mean_lst - 1 * std_lst,
        mean_lst - 0.5 * std_lst,
        mean_lst + 0.5 * std_lst,
        mean_lst + 1 * std_lst,
        mean_lst + 2 * std_lst,
    ]
    
    # Classify
    zones[valid_mask & (lst < thresholds[0])] = 0  # Very Cold
    zones[valid_mask & (lst >= thresholds[0]) & (lst < thresholds[1])] = 1  # Cold
    zones[valid_mask & (lst >= thresholds[1]) & (lst < thresholds[2])] = 2  # Cool
    zones[valid_mask & (lst >= thresholds[2]) & (lst < thresholds[3])] = 3  # Comfortable
    zones[valid_mask & (lst >= thresholds[3]) & (lst < thresholds[4])] = 4  # Warm
    zones[valid_mask & (lst >= thresholds[4]) & (lst < thresholds[5])] = 5  # Hot
    zones[valid_mask & (lst >= thresholds[5])] = 6  # Very Hot
    
    return zones
