"""
File Handler Utility Module

This module provides utilities for handling uploaded GeoTIFF files:
- File validation (format, dimensions, CRS)
- Temporary file storage and cleanup
- Band data loading with metadata
- Error handling for corrupt files

Features:
- Validates GeoTIFF format and structure
- Ensures all bands have matching dimensions and CRS
- Automatic cleanup of temporary files
- Context manager support for safe resource handling
"""

import os
import tempfile
import shutil
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from contextlib import contextmanager
import atexit

import numpy as np
from numpy.typing import NDArray

# Rasterio for GeoTIFF handling
try:
    import rasterio
    from rasterio.transform import Affine
    from rasterio.crs import CRS
    from rasterio.errors import RasterioIOError
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    RasterioIOError = Exception

# Configure logging
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".tif", ".tiff", ".geotiff"}

# Default nodata value
DEFAULT_NODATA = -9999.0


class FileValidationError(Exception):
    """Raised when file validation fails."""
    pass


class BandMismatchError(Exception):
    """Raised when band dimensions or CRS don't match."""
    pass


class CorruptFileError(Exception):
    """Raised when a file is corrupt or unreadable."""
    pass


@dataclass
class BandMetadata:
    """Metadata for a loaded band."""
    width: int
    height: int
    crs: str
    transform: Any  # rasterio.Affine
    bounds: Tuple[float, float, float, float]  # (left, bottom, right, top)
    nodata: Optional[float]
    dtype: str
    band_name: str


@dataclass
class BandData:
    """Complete band data with array and metadata."""
    array: NDArray[np.floating]
    metadata: BandMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes array for JSON)."""
        return {
            "band_name": self.metadata.band_name,
            "width": self.metadata.width,
            "height": self.metadata.height,
            "crs": self.metadata.crs,
            "bounds": {
                "left": self.metadata.bounds[0],
                "bottom": self.metadata.bounds[1],
                "right": self.metadata.bounds[2],
                "top": self.metadata.bounds[3],
            },
            "dtype": self.metadata.dtype,
            "nodata": self.metadata.nodata,
        }


@dataclass
class LoadedBands:
    """Collection of loaded bands with shared metadata."""
    bands: Dict[str, NDArray[np.floating]]
    transform: Any  # rasterio.Affine
    crs: str
    bounds: Tuple[float, float, float, float]
    width: int
    height: int
    nodata_value: float


class TempFileManager:
    """
    Manages temporary files with automatic cleanup.
    
    Usage:
        manager = TempFileManager()
        path = manager.save_file(file_content, "band.tif")
        # ... use file ...
        manager.cleanup()  # or use context manager
    """
    
    def __init__(self, prefix: str = "uhi_lst_"):
        """Initialize with optional prefix for temp directory."""
        self.temp_dir: Optional[str] = None
        self.prefix = prefix
        self._files: List[str] = []
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def _ensure_temp_dir(self) -> str:
        """Ensure temp directory exists."""
        if self.temp_dir is None or not os.path.exists(self.temp_dir):
            self.temp_dir = tempfile.mkdtemp(prefix=self.prefix)
            logger.debug(f"Created temp directory: {self.temp_dir}")
        return self.temp_dir
    
    def save_file(self, content: bytes, filename: str) -> str:
        """
        Save file content to temp directory.
        
        Args:
            content: File content as bytes
            filename: Name for the saved file
        
        Returns:
            Absolute path to the saved file
        """
        temp_dir = self._ensure_temp_dir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        self._files.append(file_path)
        logger.debug(f"Saved file: {file_path} ({len(content)} bytes)")
        
        return file_path
    
    async def save_upload(self, upload_file, filename: Optional[str] = None) -> str:
        """
        Save an FastAPI UploadFile to temp directory.
        
        Args:
            upload_file: FastAPI UploadFile object
            filename: Optional filename (uses upload name if not provided)
        
        Returns:
            Absolute path to the saved file
        """
        if filename is None:
            filename = upload_file.filename or "upload.tif"
        
        content = await upload_file.read()
        await upload_file.seek(0)  # Reset for potential re-read
        
        return self.save_file(content, filename)
    
    def cleanup(self):
        """Remove temp directory and all files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")
            finally:
                self.temp_dir = None
                self._files = []
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.cleanup()
        return False


def validate_file_extension(filename: str) -> bool:
    """
    Check if filename has a valid GeoTIFF extension.
    
    Args:
        filename: Name of the file to validate
    
    Returns:
        True if extension is valid
    """
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_geotiff(file_path: str) -> BandMetadata:
    """
    Validate that a file is a valid GeoTIFF and return metadata.
    
    Args:
        file_path: Path to the file to validate
    
    Returns:
        BandMetadata object with file information
    
    Raises:
        FileValidationError: If file is not a valid GeoTIFF
        CorruptFileError: If file is corrupt or unreadable
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for GeoTIFF validation")
    
    if not os.path.exists(file_path):
        raise FileValidationError(f"File not found: {file_path}")
    
    try:
        with rasterio.open(file_path) as src:
            # Check if it has at least one band
            if src.count < 1:
                raise FileValidationError(f"File has no bands: {file_path}")
            
            # Check for valid dimensions
            if src.width < 1 or src.height < 1:
                raise FileValidationError(f"Invalid dimensions: {src.width}x{src.height}")
            
            # Check for valid CRS
            if src.crs is None:
                logger.warning(f"No CRS defined in {file_path}, assuming EPSG:4326")
            
            # Get bounds
            bounds = (src.bounds.left, src.bounds.bottom, 
                     src.bounds.right, src.bounds.top)
            
            return BandMetadata(
                width=src.width,
                height=src.height,
                crs=str(src.crs) if src.crs else "EPSG:4326",
                transform=src.transform,
                bounds=bounds,
                nodata=src.nodata,
                dtype=str(src.dtypes[0]),
                band_name=os.path.basename(file_path),
            )
            
    except RasterioIOError as e:
        raise CorruptFileError(f"Cannot read file (corrupt or invalid): {file_path}. Error: {e}")
    except Exception as e:
        raise FileValidationError(f"Validation failed for {file_path}: {e}")


def validate_bands_match(
    band_files: Dict[str, str],
    tolerance_pixels: int = 0,
) -> Dict[str, BandMetadata]:
    """
    Validate that all band files have matching dimensions and CRS.
    
    Args:
        band_files: Dictionary of {band_name: file_path}
        tolerance_pixels: Allowed difference in dimensions (default: 0)
    
    Returns:
        Dictionary of {band_name: BandMetadata}
    
    Raises:
        BandMismatchError: If bands don't match
        FileValidationError: If validation fails
    """
    if not band_files:
        raise FileValidationError("No band files provided")
    
    metadata_dict = {}
    reference_meta: Optional[BandMetadata] = None
    reference_band: Optional[str] = None
    
    for band_name, file_path in band_files.items():
        meta = validate_geotiff(file_path)
        meta.band_name = band_name
        metadata_dict[band_name] = meta
        
        if reference_meta is None:
            reference_meta = meta
            reference_band = band_name
        else:
            # Check dimensions
            width_diff = abs(meta.width - reference_meta.width)
            height_diff = abs(meta.height - reference_meta.height)
            
            if width_diff > tolerance_pixels or height_diff > tolerance_pixels:
                raise BandMismatchError(
                    f"Dimension mismatch: {reference_band} is {reference_meta.width}x{reference_meta.height}, "
                    f"but {band_name} is {meta.width}x{meta.height}"
                )
            
            # Check CRS
            if meta.crs != reference_meta.crs:
                # Log warning but don't fail (some bands may have slightly different CRS strings)
                logger.warning(
                    f"CRS mismatch: {reference_band} has {reference_meta.crs}, "
                    f"but {band_name} has {meta.crs}"
                )
    
    logger.info(f"Validated {len(band_files)} bands: all match ({reference_meta.width}x{reference_meta.height})")
    return metadata_dict


def load_band(
    file_path: str,
    nodata_value: float = DEFAULT_NODATA,
    band_index: int = 1,
) -> BandData:
    """
    Load a GeoTIFF band as numpy array with metadata.
    
    Args:
        file_path: Path to the GeoTIFF file
        nodata_value: Value to use for nodata pixels
        band_index: Band index to read (1-based, default: 1)
    
    Returns:
        BandData object with array and metadata
    
    Raises:
        CorruptFileError: If file cannot be read
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required for loading bands")
    
    try:
        with rasterio.open(file_path) as src:
            # Read band data
            data = src.read(band_index).astype(np.float64)
            
            # Replace nodata values
            if src.nodata is not None:
                data[data == src.nodata] = nodata_value
            
            # Replace invalid values (zeros, negatives)
            data[data <= 0] = nodata_value
            data[~np.isfinite(data)] = nodata_value
            
            # Get bounds
            bounds = (src.bounds.left, src.bounds.bottom,
                     src.bounds.right, src.bounds.top)
            
            metadata = BandMetadata(
                width=src.width,
                height=src.height,
                crs=str(src.crs) if src.crs else "EPSG:4326",
                transform=src.transform,
                bounds=bounds,
                nodata=nodata_value,
                dtype=str(data.dtype),
                band_name=os.path.basename(file_path),
            )
            
            return BandData(array=data, metadata=metadata)
            
    except RasterioIOError as e:
        raise CorruptFileError(f"Failed to load band from {file_path}: {e}")


def load_all_bands(
    band_files: Dict[str, str],
    nodata_value: float = DEFAULT_NODATA,
    validate: bool = True,
) -> LoadedBands:
    """
    Load all band files and return as a structured object.
    
    Args:
        band_files: Dictionary of {band_name: file_path}
        nodata_value: Value to use for nodata pixels
        validate: Whether to validate bands match before loading
    
    Returns:
        LoadedBands object with all arrays and shared metadata
    
    Raises:
        BandMismatchError: If bands don't match (when validate=True)
        CorruptFileError: If any file cannot be read
    """
    if validate:
        validate_bands_match(band_files)
    
    bands = {}
    reference_data: Optional[BandData] = None
    
    for band_name, file_path in band_files.items():
        band_data = load_band(file_path, nodata_value)
        bands[band_name] = band_data.array
        
        if reference_data is None:
            reference_data = band_data
    
    if reference_data is None:
        raise FileValidationError("No bands loaded")
    
    return LoadedBands(
        bands=bands,
        transform=reference_data.metadata.transform,
        crs=reference_data.metadata.crs,
        bounds=reference_data.metadata.bounds,
        width=reference_data.metadata.width,
        height=reference_data.metadata.height,
        nodata_value=nodata_value,
    )


@contextmanager
def temp_band_files(
    band_uploads: Dict[str, Any],
    nodata_value: float = DEFAULT_NODATA,
):
    """
    Context manager for handling uploaded band files.
    
    Saves uploads to temp directory, loads them, and cleans up on exit.
    
    Args:
        band_uploads: Dictionary of {band_name: UploadFile or bytes}
        nodata_value: Value to use for nodata pixels
    
    Yields:
        LoadedBands object with all data
    
    Example:
        async with temp_band_files({"B4": band4_upload, "B5": band5_upload}) as bands:
            ndvi = calculate_ndvi(bands.bands["B5"], bands.bands["B4"])
    """
    manager = TempFileManager()
    
    try:
        # This is a sync context manager; for async uploads, use save_upload separately
        band_files = {}
        
        for band_name, upload in band_uploads.items():
            if isinstance(upload, bytes):
                file_path = manager.save_file(upload, f"{band_name}.tif")
            else:
                # Assume it's already a file path string
                file_path = str(upload)
            
            band_files[band_name] = file_path
        
        # Load all bands
        loaded = load_all_bands(band_files, nodata_value)
        
        yield loaded
        
    finally:
        manager.cleanup()


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get detailed information about a GeoTIFF file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with file information
    """
    if not HAS_RASTERIO:
        raise ImportError("rasterio is required")
    
    try:
        with rasterio.open(file_path) as src:
            return {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size_bytes": os.path.getsize(file_path),
                "size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
                "width": src.width,
                "height": src.height,
                "count": src.count,
                "crs": str(src.crs) if src.crs else None,
                "dtype": str(src.dtypes[0]),
                "nodata": src.nodata,
                "bounds": {
                    "left": src.bounds.left,
                    "bottom": src.bounds.bottom,
                    "right": src.bounds.right,
                    "top": src.bounds.top,
                },
                "transform": list(src.transform)[:6],
                "driver": src.driver,
            }
    except Exception as e:
        raise CorruptFileError(f"Cannot read file info: {e}")
