"""
Test suite for UHI-LST calculation modules.

This script verifies that all calculation modules work correctly
with synthetic test data.

Run with: pytest tests/test_calculations.py -v
Or directly: python tests/test_calculations.py
"""

import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ndvi_calculation():
    """Test NDVI calculation with known values."""
    print("\n📊 Testing NDVI Calculation...")
    
    from calculations.ndvi import calculate_ndvi, classify_ndvi, get_ndvi_statistics
    
    # Create test data
    # NIR = 0.5, Red = 0.1 -> NDVI = (0.5 - 0.1) / (0.5 + 0.1) = 0.667
    nir = np.array([[0.5, 0.3, 0.6],
                    [0.4, 0.2, 0.8],
                    [0.1, 0.5, 0.7]], dtype=np.float64)
    
    red = np.array([[0.1, 0.2, 0.1],
                    [0.3, 0.4, 0.1],
                    [0.2, 0.1, 0.2]], dtype=np.float64)
    
    # Calculate NDVI
    ndvi = calculate_ndvi(nir, red, nodata_value=-9999.0)
    
    # Expected: (0.5-0.1)/(0.5+0.1) = 0.667 for first pixel
    expected_first = (0.5 - 0.1) / (0.5 + 0.1)
    assert abs(ndvi[0, 0] - expected_first) < 0.001, f"Expected {expected_first}, got {ndvi[0, 0]}"
    
    # Test classification
    classified = classify_ndvi(ndvi)
    assert classified.shape == ndvi.shape
    
    # Test statistics
    stats = get_ndvi_statistics(ndvi)
    assert stats["min"] is not None
    assert stats["max"] is not None
    assert -1 <= stats["min"] <= stats["max"] <= 1
    
    print(f"  ✅ NDVI range: {stats['min']:.3f} to {stats['max']:.3f}")
    print(f"  ✅ NDVI mean: {stats['mean']:.3f}")
    print("  ✅ NDVI calculation passed!")
    return True


def test_lst_calculation():
    """Test LST calculation pipeline."""
    print("\n🌡️ Testing LST Calculation...")
    
    from calculations.lst import (
        dn_to_radiance,
        radiance_to_brightness_temperature,
        estimate_emissivity_from_ndvi,
        calculate_lst,
        get_lst_statistics
    )
    
    # Create test thermal band data (DN values typical for Landsat)
    # DN values around 20000-30000 are typical for Band 10
    band_10 = np.array([[25000, 26000, 27000],
                        [28000, 29000, 30000],
                        [31000, 32000, 33000]], dtype=np.float64)
    
    # Create test NDVI (for emissivity calculation)
    ndvi = np.array([[0.3, 0.4, 0.5],
                     [0.2, 0.3, 0.4],
                     [0.1, 0.2, 0.3]], dtype=np.float64)
    
    # Step 1: DN to Radiance
    radiance = dn_to_radiance(band_10, ml=3.342e-4, al=0.1)
    assert np.all(radiance > 0), "Radiance should be positive"
    print(f"  ✅ Radiance range: {np.min(radiance):.2f} to {np.max(radiance):.2f}")
    
    # Step 2: Radiance to Brightness Temperature
    bt = radiance_to_brightness_temperature(radiance)
    assert np.all(bt > 200), "Brightness temp should be > 200K"
    assert np.all(bt < 400), "Brightness temp should be < 400K"
    print(f"  ✅ Brightness Temp range: {np.min(bt):.1f}K to {np.max(bt):.1f}K")
    
    # Step 3: Estimate Emissivity
    emissivity = estimate_emissivity_from_ndvi(ndvi)
    assert np.all(emissivity >= 0.95), "Emissivity should be >= 0.95"
    assert np.all(emissivity <= 1.0), "Emissivity should be <= 1.0"
    print(f"  ✅ Emissivity range: {np.min(emissivity):.4f} to {np.max(emissivity):.4f}")
    
    # Step 4: Calculate LST
    lst = calculate_lst(bt, emissivity, output_celsius=True)
    
    # LST should be reasonable temperatures
    stats = get_lst_statistics(lst)
    assert stats["min"] is not None
    assert stats["min"] > -50, "LST should be > -50°C"
    assert stats["max"] < 80, "LST should be < 80°C"
    
    print(f"  ✅ LST range: {stats['min']:.1f}°C to {stats['max']:.1f}°C")
    print(f"  ✅ LST mean: {stats['mean']:.1f}°C")
    print("  ✅ LST calculation passed!")
    return True


def test_land_cover_classification():
    """Test land cover classification."""
    print("\n🏞️ Testing Land Cover Classification...")
    
    from calculations.land_cover import (
        classify_land_cover,
        get_land_cover_statistics,
        LandCoverClass
    )
    
    # Create synthetic band data
    # Simulate water (high green, low NIR)
    # Simulate vegetation (high NIR, low red)
    # Simulate urban (high SWIR, moderate NIR)
    
    size = (10, 10)
    
    # Water pixels (top-left quadrant)
    # Urban pixels (top-right quadrant)
    # Vegetation (bottom-left quadrant)
    # Bare soil (bottom-right quadrant)
    
    band_2 = np.random.uniform(0.1, 0.3, size).astype(np.float64)
    band_3 = np.random.uniform(0.1, 0.3, size).astype(np.float64)
    band_4 = np.random.uniform(0.1, 0.3, size).astype(np.float64)
    band_5 = np.random.uniform(0.1, 0.5, size).astype(np.float64)
    band_6 = np.random.uniform(0.1, 0.3, size).astype(np.float64)
    band_7 = np.random.uniform(0.1, 0.3, size).astype(np.float64)
    
    # Set up water pixels (high green, low NIR -> NDWI > 0)
    band_3[:5, :5] = 0.4  # High green
    band_5[:5, :5] = 0.1  # Low NIR
    
    # Set up vegetation pixels (high NIR, low red -> NDVI > 0.2)
    band_5[5:, :5] = 0.6  # High NIR
    band_4[5:, :5] = 0.1  # Low red
    
    # Set up urban pixels (high SWIR/NIR ratio)
    band_6[:5, 5:] = 0.5  # High SWIR1
    band_5[:5, 5:] = 0.2  # Low NIR
    
    # Classify
    classification, indices = classify_land_cover(
        band_2, band_3, band_4, band_5, band_6, band_7
    )
    
    # Check classification results
    stats = get_land_cover_statistics(classification)
    
    assert stats["total_valid_pixels"] > 0
    print(f"  ✅ Total pixels classified: {stats['total_valid_pixels']}")
    
    for class_name, pct in stats["class_percentages"].items():
        print(f"  ✅ {class_name}: {pct:.1f}%")
    
    # Verify we have multiple classes
    unique_classes = np.unique(classification)
    assert len(unique_classes) >= 2, "Should have at least 2 land cover classes"
    
    print("  ✅ Land cover classification passed!")
    return True


def test_uhi_analysis():
    """Test UHI analysis."""
    print("\n🔥 Testing UHI Analysis...")
    
    from calculations.uhi import analyze_uhi, UHICategory
    from calculations.land_cover import LandCoverClass
    
    # Create synthetic LST data (temperatures in Celsius)
    size = (20, 20)
    
    # Base temperature
    lst = np.random.uniform(30, 35, size).astype(np.float64)
    
    # Urban areas are hotter
    lst[:10, :10] = np.random.uniform(38, 45, (10, 10))
    
    # Vegetation areas are cooler
    lst[10:, 10:] = np.random.uniform(28, 32, (10, 10))
    
    # Create land cover classification
    land_cover = np.full(size, LandCoverClass.BARE_SOIL, dtype=np.int8)
    land_cover[:10, :10] = LandCoverClass.URBAN
    land_cover[10:, 10:] = LandCoverClass.VEGETATION
    land_cover[:5, 15:] = LandCoverClass.WATER
    
    # Analyze UHI
    result = analyze_uhi(lst, land_cover)
    
    # Check results
    assert result["uhi_intensity"] is not None
    assert result["urban_mean_temp"] is not None
    assert result["rural_mean_temp"] is not None
    
    print(f"  ✅ UHI Intensity: {result['uhi_intensity']:.2f}°C")
    print(f"  ✅ Urban Mean Temp: {result['urban_mean_temp']:.2f}°C")
    print(f"  ✅ Rural Mean Temp: {result['rural_mean_temp']:.2f}°C")
    print(f"  ✅ UHI Category: {result['uhi_category']}")
    print(f"  ✅ Hotspot Count: {result['hotspot_count']}")
    print(f"  ✅ Affected Area: {result['affected_area_km2']:.4f} km²")
    
    # Urban should be hotter than rural
    assert result["urban_mean_temp"] > result["rural_mean_temp"], \
        "Urban areas should be hotter than rural"
    
    print("  ✅ UHI analysis passed!")
    return True


def test_insights_generation():
    """Test insights and recommendations generation."""
    print("\n💡 Testing Insights Generation...")
    
    from analysis.insights import generate_insights, UHISeverity
    
    # Create mock analysis results
    uhi_result = {
        "uhi_intensity": 5.5,
        "urban_mean_temp": 40.2,
        "rural_mean_temp": 34.7,
        "hotspot_count": 5000,
        "hotspot_cluster_count": 12,
        "affected_area_km2": 4.5,
        "affected_area_ha": 450,
    }
    
    land_cover_stats = {
        "class_percentages": {
            "Water": 3.2,
            "Urban/Built-up": 65.0,
            "Vegetation": 18.5,
            "Bare Soil": 13.3,
        },
        "total_valid_pixels": 100000,
    }
    
    ndvi_stats = {
        "min": -0.2,
        "max": 0.75,
        "mean": 0.22,
        "std": 0.15,
    }
    
    lst_stats = {
        "min": 25.5,
        "max": 52.3,
        "mean": 38.2,
        "std": 5.8,
    }
    
    # Generate insights
    insights = generate_insights(
        uhi_result, land_cover_stats, ndvi_stats, lst_stats
    )
    
    # Check results
    assert "explanation" in insights
    assert "recommendations" in insights
    assert "severity" in insights
    
    assert len(insights["explanation"]) > 100, "Explanation should be substantial"
    assert len(insights["recommendations"]) >= 3, "Should have at least 3 recommendations"
    
    print(f"  ✅ Severity: {insights['severity']}")
    print(f"  ✅ Recommendation count: {insights['recommendation_count']}")
    
    for rec in insights["recommendations"][:3]:
        print(f"  ✅ [{rec['priority']}] {rec['title']}")
    
    print("  ✅ Insights generation passed!")
    return True


def test_heatmap_generation():
    """Test heatmap data generation."""
    print("\n🗺️ Testing Heatmap Generation...")
    
    from utils.heatmap import (
        generate_heatmap_from_array,
        HeatmapConfig,
        get_heatmap_statistics
    )
    
    # Create synthetic LST data
    size = (100, 100)
    lst = np.random.uniform(25, 45, size).astype(np.float64)
    
    # Set some nodata values
    lst[0, :] = -9999.0
    lst[:, 0] = -9999.0
    
    # Define bounds (example for Nigeria)
    bounds = (8.0, 9.0, 9.0, 10.0)  # (min_lon, min_lat, max_lon, max_lat)
    
    # Configure
    config = HeatmapConfig(
        max_points=500,
        sample_step=5,
        nodata_value=-9999.0,
    )
    
    # Generate heatmap
    heatmap = generate_heatmap_from_array(lst, bounds, config)
    
    # Check results
    assert len(heatmap) > 0, "Should have heatmap points"
    assert len(heatmap) <= config.max_points, "Should respect max_points limit"
    
    # Check point structure
    point = heatmap[0]
    assert "lat" in point
    assert "lon" in point
    assert "temp" in point
    
    # Check coordinates are within bounds
    for p in heatmap:
        assert bounds[1] <= p["lat"] <= bounds[3], f"Lat {p['lat']} out of bounds"
        assert bounds[0] <= p["lon"] <= bounds[2], f"Lon {p['lon']} out of bounds"
        assert p["temp"] != -9999.0, "NoData values should be filtered"
    
    # Get statistics
    stats = get_heatmap_statistics(heatmap)
    
    print(f"  ✅ Heatmap points: {len(heatmap)}")
    print(f"  ✅ Temperature range: {stats['min_temp']:.1f}°C to {stats['max_temp']:.1f}°C")
    print(f"  ✅ Geographic bounds: ({stats['min_lat']:.4f}, {stats['min_lon']:.4f}) to ({stats['max_lat']:.4f}, {stats['max_lon']:.4f})")
    print("  ✅ Heatmap generation passed!")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("🧪 UHI-LST Calculation Test Suite")
    print("=" * 60)
    
    tests = [
        ("NDVI Calculation", test_ndvi_calculation),
        ("LST Calculation", test_lst_calculation),
        ("Land Cover Classification", test_land_cover_classification),
        ("UHI Analysis", test_uhi_analysis),
        ("Insights Generation", test_insights_generation),
        ("Heatmap Generation", test_heatmap_generation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"  ❌ {name} failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    for name, success, error in results:
        status = "✅ PASSED" if success else f"❌ FAILED: {error}"
        print(f"  {name}: {status}")
    
    print()
    print(f"Total: {passed}/{len(results)} tests passed")
    
    if failed > 0:
        print(f"⚠️ {failed} test(s) failed!")
        return False
    else:
        print("✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
