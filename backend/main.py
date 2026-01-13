"""
FastAPI Backend for Landsat 8/9 UHI and LST Analysis

This API processes Landsat 8/9 imagery to calculate:
- Land Surface Temperature (LST)
- Normalized Difference Vegetation Index (NDVI)
- Urban Heat Island (UHI) intensity
- Land Cover Classification
- Actionable recommendations for heat mitigation
"""

import os
import time
import uuid
import logging
import tempfile
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Rasterio for GeoTIFF processing
import rasterio
from rasterio.transform import xy

# Import calculation modules
from calculations import (
    # NDVI
    calculate_ndvi,
    classify_ndvi,
    get_ndvi_statistics,
    get_classification_percentages,
    # LST
    dn_to_radiance,
    radiance_to_brightness_temperature,
    estimate_emissivity_from_ndvi,
    calculate_lst,
    get_lst_statistics,
    classify_lst_thermal_zones,
    RadianceCoefficients,
    # Land Cover
    classify_land_cover,
    get_land_cover_statistics,
    # UHI
    analyze_uhi,
    create_uhi_map,
)

# Import analysis modules
from analysis import generate_insights

# Import utility modules
from utils.heatmap import (
    generate_heatmap_data as gen_heatmap,
    HeatmapConfig,
    get_heatmap_statistics,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="UHI-LST Analysis API",
    description="API for processing Landsat 8/9 imagery to calculate Land Surface Temperature (LST) and Urban Heat Island (UHI) indices",
    version="1.0.0"
)

# CORS configuration - allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development to avoid CORS issues
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".tif", ".tiff"}

# Band configuration for Landsat 8/9
REQUIRED_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7", "B10"]

# Default nodata value
NODATA_VALUE = -9999.0

# Maximum heatmap points to return (for performance)
MAX_HEATMAP_POINTS = 5000

# Heatmap configuration
HEATMAP_CONFIG = HeatmapConfig(
    max_points=MAX_HEATMAP_POINTS,
    sample_step=10,  # Sample every 10th pixel
    nodata_value=NODATA_VALUE,
)


def validate_tiff_file(file: UploadFile) -> bool:
    """Validate that the uploaded file is a TIFF file."""
    if not file.filename:
        return False
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def load_band_as_array(file_path: str) -> Tuple[np.ndarray, dict]:
    """
    Load a GeoTIFF band file and return the data array and metadata.
    
    Args:
        file_path: Path to the GeoTIFF file
    
    Returns:
        Tuple of (data array, metadata dict with transform, crs, bounds)
    """
    with rasterio.open(file_path) as src:
        data = src.read(1).astype(np.float64)
        
        # Replace nodata with our standard nodata value
        if src.nodata is not None:
            data[data == src.nodata] = NODATA_VALUE
        
        # Replace zeros and negative values (common nodata indicators)
        data[data <= 0] = NODATA_VALUE
        
        metadata = {
            "transform": src.transform,
            "crs": str(src.crs),
            "bounds": src.bounds,
            "width": src.width,
            "height": src.height,
            "nodata": src.nodata,
        }
        
        return data, metadata


# Note: generate_heatmap_data is now imported from utils.heatmap


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "UHI-LST Analysis API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """API health check."""
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_landsat_imagery(
    band_2: UploadFile = File(..., description="Band 2 (Blue) - .tif file"),
    band_3: UploadFile = File(..., description="Band 3 (Green) - .tif file"),
    band_4: UploadFile = File(..., description="Band 4 (Red) - .tif file"),
    band_5: UploadFile = File(..., description="Band 5 (NIR) - .tif file"),
    band_6: UploadFile = File(..., description="Band 6 (SWIR1) - .tif file"),
    band_7: UploadFile = File(..., description="Band 7 (SWIR2) - .tif file"),
    band_10: UploadFile = File(..., description="Band 10 (Thermal) - .tif file"),
    ml_coefficient: float = 3.342e-4,
    al_coefficient: float = 0.1,
):
    """
    Process Landsat 8/9 band files to calculate LST and UHI indices.
    
    Accepts 7 band files:
    - Band 2: Blue (0.45-0.51 µm)
    - Band 3: Green (0.53-0.59 µm)
    - Band 4: Red (0.64-0.67 µm)
    - Band 5: NIR (0.85-0.88 µm)
    - Band 6: SWIR1 (1.57-1.65 µm)
    - Band 7: SWIR2 (2.11-2.29 µm)
    - Band 10: Thermal (10.6-11.19 µm)
    
    Optional parameters:
    - ml_coefficient: Radiance multiplicative factor from MTL file
    - al_coefficient: Radiance additive factor from MTL file
    
    Returns:
        JSON with complete analysis results including LST, UHI, and recommendations.
    """
    start_time = time.time()
    job_id = str(uuid.uuid4())
    
    logger.info(f"[{job_id}] Starting analysis...")
    
    # Collect all band files for validation
    band_files = {
        "B2": band_2,
        "B3": band_3,
        "B4": band_4,
        "B5": band_5,
        "B6": band_6,
        "B7": band_7,
        "B10": band_10,
    }
    
    # Validate all files are valid TIFF files
    validation_errors = []
    for band_name, file in band_files.items():
        if not validate_tiff_file(file):
            validation_errors.append(
                f"{band_name}: Invalid file format. Expected .tif or .tiff, got '{file.filename}'"
            )
    
    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File validation failed",
                "messages": validation_errors
            }
        )
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            step_times = {}
            
            # ========== Step 1: Save uploaded files ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 1: Saving uploaded files...")
            
            saved_files = {}
            for band_name, file in band_files.items():
                file_path = os.path.join(temp_dir, f"{band_name}.tif")
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                saved_files[band_name] = file_path
                await file.seek(0)
            
            step_times["file_upload"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] Files saved in {step_times['file_upload']}s")
            
            # ========== Step 2: Load band data ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 2: Loading band data with rasterio...")
            
            bands = {}
            metadata = None
            
            for band_name, file_path in saved_files.items():
                data, meta = load_band_as_array(file_path)
                bands[band_name] = data
                if metadata is None:
                    metadata = meta
            
            step_times["load_bands"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] Bands loaded in {step_times['load_bands']}s. Shape: {bands['B10'].shape}")
            
            # ========== Step 3: Calculate NDVI ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 3: Calculating NDVI...")
            
            ndvi = calculate_ndvi(
                nir=bands["B5"],
                red=bands["B4"],
                nodata_value=NODATA_VALUE
            )
            ndvi_stats = get_ndvi_statistics(ndvi, NODATA_VALUE)
            ndvi_classified = classify_ndvi(ndvi, NODATA_VALUE)
            ndvi_percentages = get_classification_percentages(ndvi_classified)
            
            step_times["ndvi"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] NDVI calculated in {step_times['ndvi']}s. Mean: {ndvi_stats['mean']:.3f}")
            
            # ========== Step 4: Calculate LST ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 4: Calculating LST...")
            
            # DN to Radiance
            radiance = dn_to_radiance(
                bands["B10"],
                ml=ml_coefficient,
                al=al_coefficient,
                nodata_value=NODATA_VALUE
            )
            
            # Radiance to Brightness Temperature
            brightness_temp = radiance_to_brightness_temperature(
                radiance,
                nodata_value=NODATA_VALUE
            )
            
            # Estimate Emissivity from NDVI
            emissivity = estimate_emissivity_from_ndvi(
                ndvi,
                nodata_value=NODATA_VALUE
            )
            
            # Calculate LST
            lst = calculate_lst(
                brightness_temp,
                emissivity,
                nodata_value=NODATA_VALUE,
                output_celsius=True
            )
            lst_stats = get_lst_statistics(lst, NODATA_VALUE)
            thermal_zones = classify_lst_thermal_zones(lst, nodata_value=NODATA_VALUE)
            
            step_times["lst"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] LST calculated in {step_times['lst']}s. Mean: {lst_stats['mean']:.1f}°C")
            
            # ========== Step 5: Classify Land Cover ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 5: Classifying land cover...")
            
            land_cover, indices = classify_land_cover(
                band_2=bands["B2"],
                band_3=bands["B3"],
                band_4=bands["B4"],
                band_5=bands["B5"],
                band_6=bands["B6"],
                band_7=bands["B7"],
                nodata_value=NODATA_VALUE,
                ndvi=ndvi
            )
            land_cover_stats = get_land_cover_statistics(land_cover)
            
            step_times["land_cover"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] Land cover classified in {step_times['land_cover']}s")
            
            # ========== Step 6: Calculate UHI ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 6: Analyzing Urban Heat Island...")
            
            uhi_result = analyze_uhi(
                lst=lst,
                land_cover=land_cover,
                nodata_value=NODATA_VALUE,
            )
            
            # Create UHI anomaly map
            uhi_map = create_uhi_map(lst, land_cover, NODATA_VALUE)
            
            step_times["uhi"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] UHI analyzed in {step_times['uhi']}s. Intensity: {uhi_result['uhi_intensity']}°C")
            
            # ========== Step 7: Generate Insights ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 7: Generating insights and recommendations...")
            
            # Prepare stats for insights
            insights_result = generate_insights(
                uhi_result=uhi_result,
                land_cover_stats=land_cover_stats,
                ndvi_stats=ndvi_stats,
                lst_stats=lst_stats,
            )
            
            step_times["insights"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] Insights generated in {step_times['insights']}s")
            
            # ========== Step 8: Generate Heatmap Data ==========
            step_start = time.time()
            logger.info(f"[{job_id}] Step 8: Generating heatmap data...")
            
            heatmap_data = gen_heatmap(
                lst=lst,
                transform=metadata["transform"],
                source_crs=metadata["crs"],
                config=HEATMAP_CONFIG,
            )
            heatmap_stats = get_heatmap_statistics(heatmap_data)
            
            step_times["heatmap"] = round(time.time() - step_start, 3)
            logger.info(f"[{job_id}] Heatmap generated with {len(heatmap_data)} points in {step_times['heatmap']}s")
            
            # ========== Prepare Response ==========
            total_time = round(time.time() - start_time, 3)
            logger.info(f"[{job_id}] Analysis complete in {total_time}s")
            
            # Remove numpy arrays from UHI result for JSON serialization
            uhi_response = {k: v for k, v in uhi_result.items() 
                          if not isinstance(v, np.ndarray)}
            
            response_data = {
                "job_id": job_id,
                "status": "completed",
                "execution_time_seconds": total_time,
                "step_times": step_times,
                
                # Image metadata
                "metadata": {
                    "width": metadata["width"],
                    "height": metadata["height"],
                    "crs": metadata["crs"],
                    "bounds": {
                        "left": metadata["bounds"].left,
                        "bottom": metadata["bounds"].bottom,
                        "right": metadata["bounds"].right,
                        "top": metadata["bounds"].top,
                    },
                },
                
                # LST results
                "lst": {
                    "statistics": lst_stats,
                    "unit": "Celsius",
                },
                
                # NDVI results
                "ndvi": {
                    "statistics": ndvi_stats,
                    "classification_percentages": ndvi_percentages,
                },
                
                # Land cover results
                "land_cover": land_cover_stats,
                
                # UHI results
                "uhi": uhi_response,
                
                # Insights and recommendations
                "insights": insights_result,
                
                # Heatmap data for visualization
                "heatmap": {
                    "points": heatmap_data,
                    "point_count": len(heatmap_data),
                    "statistics": heatmap_stats,
                    "config": {
                        "max_points": HEATMAP_CONFIG.max_points,
                        "sample_step": HEATMAP_CONFIG.sample_step,
                    },
                },
            }
            
            return JSONResponse(content=response_data)
            
    except rasterio.errors.RasterioIOError as e:
        logger.error(f"[{job_id}] Rasterio error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Failed to read GeoTIFF file",
                "message": str(e),
                "hint": "Ensure the uploaded files are valid Landsat GeoTIFF files",
                "job_id": job_id,
            }
        )
    
    except ValueError as e:
        logger.error(f"[{job_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation error",
                "message": str(e),
                "job_id": job_id,
            }
        )
    
    except Exception as e:
        logger.exception(f"[{job_id}] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing failed",
                "message": str(e),
                "job_id": job_id,
            }
        )


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a processing job.
    
    TODO: Implement job tracking with a database or cache for async processing.
    """
    return {
        "job_id": job_id,
        "status": "not_implemented",
        "message": "Job tracking not yet implemented. Analysis is synchronous."
    }


@app.get("/api/legend")
async def get_legend():
    """
    Get color legends for map visualizations.
    """
    from calculations.land_cover import export_classification_legend, LAND_COVER_COLORS
    from calculations.uhi import UHI_CATEGORY_NAMES
    
    return {
        "land_cover": export_classification_legend(),
        "uhi_categories": {
            name: {
                "value": int(cat),
            }
            for cat, name in UHI_CATEGORY_NAMES.items()
        },
        "thermal_zones": {
            "very_cold": {"value": 0, "description": "< mean - 2σ"},
            "cold": {"value": 1, "description": "mean - 2σ to mean - 1σ"},
            "cool": {"value": 2, "description": "mean - 1σ to mean - 0.5σ"},
            "comfortable": {"value": 3, "description": "mean - 0.5σ to mean + 0.5σ"},
            "warm": {"value": 4, "description": "mean + 0.5σ to mean + 1σ"},
            "hot": {"value": 5, "description": "mean + 1σ to mean + 2σ"},
            "very_hot": {"value": 6, "description": "> mean + 2σ"},
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
