# UHI-LST Platform Scripts

This folder contains scripts to manage the UHI-LST platform.

## Scripts

| Script | Description |
|--------|-------------|
| `install.bat` | Installs all dependencies (Python venv + pip, npm packages) |
| `start.bat` | Starts both backend and frontend servers |
| `stop.bat` | Stops all running servers |

## Quick Start

1. **First time setup:**
   ```
   install.bat
   ```

2. **Start the platform:**
   ```
   start.bat
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Stop the platform:**
   ```
   stop.bat
   ```

## Requirements

- Python 3.10+
- Node.js 18+
