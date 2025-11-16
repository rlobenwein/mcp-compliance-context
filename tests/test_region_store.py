"""Tests for RegionStore class."""

import json
import tempfile
from pathlib import Path

import pytest

from server.region_store import RegionStore
from server.regulation_store import RegulationStore


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory with sample region and regulation data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        
        # Create subdirectories
        eu_dir = data_dir / "eu"
        usa_dir = data_dir / "usa"
        eu_dir.mkdir()
        usa_dir.mkdir()
        
        # Create regions.json
        regions_data = [
            {
                "id": "eu",
                "name": "European Union",
                "regulations": ["gdpr"],
                "notes": "EU regulations"
            },
            {
                "id": "usa",
                "name": "United States of America",
                "regulations": ["hipaa"],
                "notes": "US regulations"
            }
        ]
        
        with open(data_dir / "regions.json", "w", encoding="utf-8") as f:
            json.dump(regions_data, f)
        
        # Create sample regulation files
        gdpr_data = {
            "id": "gdpr",
            "name": "General Data Protection Regulation",
            "region": "EU",
            "risk_category": "high",
            "summary": "GDPR regulation",
            "articles": [],
            "developer_guidance": []
        }
        
        hipaa_data = {
            "id": "hipaa",
            "name": "Health Insurance Portability and Accountability Act",
            "region": "USA",
            "risk_category": "high",
            "summary": "HIPAA regulation",
            "articles": [],
            "developer_guidance": []
        }
        
        with open(eu_dir / "gdpr.json", "w", encoding="utf-8") as f:
            json.dump(gdpr_data, f)
        
        with open(usa_dir / "hipaa.json", "w", encoding="utf-8") as f:
            json.dump(hipaa_data, f)
        
        yield data_dir


def test_region_store_loads_regions(temp_data_dir):
    """Test that RegionStore loads regions.json."""
    regulation_store = RegulationStore(str(temp_data_dir))
    region_store = RegionStore(str(temp_data_dir), regulation_store)
    
    assert len(region_store.regions) == 2
    assert "eu" in region_store.regions
    assert "usa" in region_store.regions


def test_get_region_valid_id(temp_data_dir):
    """Test getting a region with a valid ID."""
    regulation_store = RegulationStore(str(temp_data_dir))
    region_store = RegionStore(str(temp_data_dir), regulation_store)
    
    region = region_store.get_region("eu", regulation_store)
    assert region is not None
    assert region["id"] == "eu"
    assert region["name"] == "European Union"
    assert "regulations" in region
    assert len(region["regulations"]) > 0


def test_get_region_case_insensitive(temp_data_dir):
    """Test that get_region is case-insensitive."""
    regulation_store = RegulationStore(str(temp_data_dir))
    region_store = RegionStore(str(temp_data_dir), regulation_store)
    
    region1 = region_store.get_region("EU", regulation_store)
    region2 = region_store.get_region("eu", regulation_store)
    region3 = region_store.get_region("Eu", regulation_store)
    
    assert region1 == region2 == region3
    assert region1 is not None


def test_get_region_invalid_id(temp_data_dir):
    """Test getting a region with an invalid ID."""
    regulation_store = RegulationStore(str(temp_data_dir))
    region_store = RegionStore(str(temp_data_dir), regulation_store)
    
    region = region_store.get_region("nonexistent", regulation_store)
    assert region is None


def test_get_region_aggregates_regulations(temp_data_dir):
    """Test that get_region aggregates regulations correctly."""
    regulation_store = RegulationStore(str(temp_data_dir))
    region_store = RegionStore(str(temp_data_dir), regulation_store)
    
    region = region_store.get_region("eu", regulation_store)
    assert region is not None
    assert len(region["regulations"]) == 1
    assert region["regulations"][0]["id"] == "gdpr"


def test_get_region_without_regulation_store(temp_data_dir):
    """Test that get_region works without a regulation store (returns empty regulations)."""
    region_store = RegionStore(str(temp_data_dir))
    
    region = region_store.get_region("eu")
    assert region is not None
    assert region["id"] == "eu"
    assert region["regulations"] == []

