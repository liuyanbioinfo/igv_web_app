import pytest
import os,sys
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"IGV Viewer" in response.data

def test_update_igv_valid_bam(client):
    """Test the /api/check-bam endpoint with valid BAM file"""
    response = client.post('/api/check-bam', json={"bam_path": app.root_path + "/static/testdata/test.cons.bam"})
    assert response.status_code == 200
    data = response.get_json()
    assert "bam_url" in data
    assert "bam_index_url" in data

def test_update_igv_invalid_bam(client):
    """Test the /api/check-bam endpoint with invalid BAM file"""
    response = client.post('/api/check-bam', json={"bam_path": app.root_path +"/static/dynamic_bam/data/invalid.bam"})
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    print(data["error"])
    assert data["error"] == "File not found or not allowed."
