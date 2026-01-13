# ⚙️ UHI-LST Analysis Backend

FastAPI backend for processing Landsat 8/9 imagery to calculate Land Surface Temperature (LST) and Urban Heat Island (UHI) indices.

## Features

- 🌡️ **LST Calculation**: Convert thermal band to surface temperature
- 🌱 **NDVI Analysis**: Vegetation index and classification
- 🏙️ **Land Cover Classification**: Water, Urban, Vegetation, Bare Soil
- 🔥 **UHI Detection**: Urban heat island intensity and hotspots
- 💡 **AI Insights**: Natural language explanations and recommendations
- 🗺️ **Heatmap Generation**: JSON data for frontend visualization

## Quick Start

### Prerequisites

- Python 3.10+ 
- pip or conda for package management
- GDAL libraries (required for rasterio)

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or simply:
python main.py
```

The server will be available at: **http://localhost:8000**

### API Documentation

Once running, access interactive docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```bash
GET /
GET /api/health
```

### Analyze Landsat Imagery

```bash
POST /api/analyze
```

**Parameters:**
- `band_2`: Band 2 (Blue) - .tif file
- `band_3`: Band 3 (Green) - .tif file  
- `band_4`: Band 4 (Red) - .tif file
- `band_5`: Band 5 (NIR) - .tif file
- `band_6`: Band 6 (SWIR1) - .tif file
- `band_7`: Band 7 (SWIR2) - .tif file
- `band_10`: Band 10 (Thermal) - .tif file
- `ml_coefficient`: (optional) Radiance multiplicative factor
- `al_coefficient`: (optional) Radiance additive factor

### Example cURL Request

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "accept: application/json" \
  -F "band_2=@path/to/LC08_B2.TIF" \
  -F "band_3=@path/to/LC08_B3.TIF" \
  -F "band_4=@path/to/LC08_B4.TIF" \
  -F "band_5=@path/to/LC08_B5.TIF" \
  -F "band_6=@path/to/LC08_B6.TIF" \
  -F "band_7=@path/to/LC08_B7.TIF" \
  -F "band_10=@path/to/LC08_B10.TIF"
```

### Example PowerShell Request

```powershell
$uri = "http://localhost:8000/api/analyze"
$form = @{
    band_2 = Get-Item ".\data\LC08_B2.TIF"
    band_3 = Get-Item ".\data\LC08_B3.TIF"
    band_4 = Get-Item ".\data\LC08_B4.TIF"
    band_5 = Get-Item ".\data\LC08_B5.TIF"
    band_6 = Get-Item ".\data\LC08_B6.TIF"
    band_7 = Get-Item ".\data\LC08_B7.TIF"
    band_10 = Get-Item ".\data\LC08_B10.TIF"
}
Invoke-RestMethod -Uri $uri -Method Post -Form $form
```

### Expected Response Format

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "execution_time_seconds": 12.453,
  "step_times": {
    "file_upload": 0.234,
    "load_bands": 1.523,
    "ndvi": 0.456,
    "lst": 0.892,
    "land_cover": 0.678,
    "uhi": 0.345,
    "insights": 0.012,
    "heatmap": 0.234
  },
  
  "metadata": {
    "width": 7671,
    "height": 7791,
    "crs": "EPSG:32632",
    "bounds": {
      "left": 399960.0,
      "bottom": 1000020.0,
      "right": 630030.0,
      "top": 1233750.0
    }
  },
  
  "lst": {
    "statistics": {
      "min": 22.3,
      "max": 48.5,
      "mean": 35.2,
      "std": 5.4,
      "median": 34.8,
      "valid_pixels": 59780361,
      "total_pixels": 59780361,
      "unit": "Celsius"
    },
    "unit": "Celsius"
  },
  
  "ndvi": {
    "statistics": {
      "min": -0.42,
      "max": 0.87,
      "mean": 0.28,
      "std": 0.15,
      "valid_pixels": 59780361,
      "total_pixels": 59780361
    },
    "classification_percentages": {
      "water": 5.2,
      "urban_bare_soil": 35.1,
      "sparse_vegetation": 28.4,
      "dense_vegetation": 31.3
    }
  },
  
  "land_cover": {
    "class_counts": {
      "No Data": 0,
      "Water": 3108175,
      "Urban/Built-up": 25167212,
      "Vegetation": 18690243,
      "Bare Soil": 12814731
    },
    "class_percentages": {
      "Water": 5.2,
      "Urban/Built-up": 42.1,
      "Vegetation": 31.3,
      "Bare Soil": 21.4
    },
    "total_valid_pixels": 59780361,
    "total_pixels": 59780361
  },
  
  "uhi": {
    "uhi_intensity": 4.32,
    "uhi_category": "Moderate",
    "uhi_category_value": 2,
    "urban_mean_temp": 38.5,
    "rural_mean_temp": 34.18,
    "hotspot_count": 15420,
    "hotspot_cluster_count": 23,
    "hotspot_threshold_temp": 42.3,
    "affected_area_km2": 13.88,
    "affected_area_ha": 1388.0
  },
  
  "insights": {
    "explanation": "## Urban Heat Island Analysis Summary\n\nThe analysis reveals a **moderate Urban Heat Island (UHI) effect**...",
    "recommendations": [
      {
        "title": "Expand Urban Tree Canopy Program",
        "description": "Urban areas cover 42.1% of the study area...",
        "priority": "HIGH",
        "priority_value": 3,
        "category": "Green Infrastructure",
        "timeframe": "Long-term (2-5 years)",
        "estimated_impact": "High"
      }
    ],
    "recommendation_count": 4,
    "severity": "moderate",
    "severity_value": 2
  },
  
  "heatmap": {
    "points": [
      {"lat": 9.0821, "lon": 8.6754, "temp": 35.2},
      {"lat": 9.0831, "lon": 8.6764, "temp": 36.1}
    ],
    "point_count": 4532,
    "statistics": {
      "count": 4532,
      "min_temp": 22.3,
      "max_temp": 48.5,
      "mean_temp": 35.2,
      "std_temp": 5.4
    },
    "config": {
      "max_points": 5000,
      "sample_step": 10
    }
  }
}
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application & endpoints
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration template
├── README.md               # This file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
│
├── calculations/           # Core calculation modules
│   ├── __init__.py
│   ├── ndvi.py             # NDVI calculation
│   ├── lst.py              # LST calculation
│   ├── land_cover.py       # Land cover classification
│   └── uhi.py              # UHI analysis
│
├── analysis/               # Insights generation
│   ├── __init__.py
│   └── insights.py         # AI-powered recommendations
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── heatmap.py          # Heatmap data generation
│   └── file_handler.py     # File validation & loading
│
└── tests/                  # Test suite
    ├── test_calculations.py
    └── test_api.py
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `true` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173` |
| `MAX_FILE_SIZE_MB` | Max upload size | `500` |

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_calculations.py -v
```

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t uhi-lst-backend .
docker run -p 8000:8000 uhi-lst-backend
```

## Landsat Data Sources

Download Landsat 8/9 imagery from:
- [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- [USGS GloVis](https://glovis.usgs.gov/)
- [Google Earth Engine](https://earthengine.google.com/)

Required bands for analysis:
- Band 2: Blue (0.45-0.51 µm)
- Band 3: Green (0.53-0.59 µm)
- Band 4: Red (0.64-0.67 µm)
- Band 5: NIR (0.85-0.88 µm)
- Band 6: SWIR1 (1.57-1.65 µm)
- Band 7: SWIR2 (2.11-2.29 µm)
- Band 10: Thermal (10.6-11.19 µm)

## License

MIT License - See LICENSE file for details.
