# 🏙️ UHI-LST Analysis Platform

[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-%2361DAFB)](./frontend)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python-%23009688)](./backend)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

An advanced, AI-powered platform for **Urban Heat Island (UHI)** assessment and **Land Surface Temperature (LST)** inversion using Landsat 8/9 satellite imagery.

---

## 🌟 Key Features

- 🌡️ **LST Inversion**: Real-time conversion of Landsat thermal bands to high-resolution surface temperature maps.
- 🎨 **True Color Visualization**: Interactive RGB composite rendering (Bands 4, 3, 2) with automatic image enhancement.
- 🏙️ **UHI Analytics**: Scientific derivation of UHI intensity, hotspots, and affected municipal areas.
- 🌱 **Environmental Insights**: NDVI analysis and land cover classification (Water, Urban, Vegetation, Bare Soil).
- 💡 **AI-Driven Recommendations**: Contextual strategy generation for urban heat mitigation.
- 🗺️ **High-Performance Map**: Smooth visualization of multi-gigabyte raster data directly in the browser.

---

## 🏗️ Architecture

The platform follows a modern decoupled architecture:

- **Frontend**: React + TypeScript + Vite + TailwindCSS. Uses Leaflet for mapping and GeoTIFF.js for client-side raster processing.
- **Backend**: FastAPI (Python). Leverages `rasterio`, `numpy`, and `pyproj` for heavy geospatial processing and scientific calculations.
- **Data Source**: Optimized for Landsat 8/9 Level 1/2 GeoTIFF products.

---

## 🚀 Quick Start (Windows)

The easiest way to get the entire platform running is using the provided management scripts.

### 1. Initial Setup
Run the installation script to set up both Frontend (npm) and Backend (Python venv).
```bash
.\scripts\install.bat
```

### 2. Start the Platform
Launch both servers simultaneously in a single command.
```bash
.\scripts\start.bat
```

- **Application**: [http://localhost:5173](http://localhost:5173)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Stop the Platform
```bash
.\scripts\stop.bat
```

---

## 📂 Project Structure

```bash
UHI_LST/
├── 📁 frontend/     # React application & Map components
├── 📁 backend/      # FastAPI server & Geospatial engine
├── 📁 scripts/      # Automation & Management utilities
└── 📁 data/         # Sample Landsat data directory (ignored)
```

For detailed information on each component, please refer to their respective README files:
- 📖 [Frontend Documentation](./frontend/README.md)
- 📖 [Backend Documentation](./backend/README.md)
- 📖 [Scripts Reference](./scripts/README.md)

---

## 🛠️ Requirements

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Browser**: Modern browser with WebGL support (Chrome, Edge, Firefox, Safari)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
