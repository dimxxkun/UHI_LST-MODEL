"""
API endpoint tests for UHI-LST Analysis Backend.

Run with: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "UHI-LST Analysis API"
    assert "version" in data


def test_health_endpoint(client):
    """Test API health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"


def test_legend_endpoint(client):
    """Test legend endpoint."""
    response = client.get("/api/legend")
    assert response.status_code == 200
    
    data = response.json()
    assert "land_cover" in data
    assert "uhi_categories" in data
    assert "thermal_zones" in data
    
    # Check land cover has expected classes
    lc = data["land_cover"]
    assert "Water" in lc
    assert "Urban/Built-up" in lc
    assert "Vegetation" in lc


def test_analyze_endpoint_validation(client):
    """Test analyze endpoint validates file types."""
    # Test with no files
    response = client.post("/api/analyze")
    assert response.status_code == 422  # Validation error
    
    # Test with wrong file type
    response = client.post(
        "/api/analyze",
        files={
            "band_2": ("test.txt", b"not a tiff", "text/plain"),
            "band_3": ("test.txt", b"not a tiff", "text/plain"),
            "band_4": ("test.txt", b"not a tiff", "text/plain"),
            "band_5": ("test.txt", b"not a tiff", "text/plain"),
            "band_6": ("test.txt", b"not a tiff", "text/plain"),
            "band_7": ("test.txt", b"not a tiff", "text/plain"),
            "band_10": ("test.txt", b"not a tiff", "text/plain"),
        }
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]


def test_job_status_endpoint(client):
    """Test job status endpoint (placeholder)."""
    response = client.get("/api/jobs/test-job-id")
    assert response.status_code == 200
    
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
