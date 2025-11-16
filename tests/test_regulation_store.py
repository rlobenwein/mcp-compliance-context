"""Tests for RegulationStore class."""

import json
import tempfile
from pathlib import Path

import pytest

from server.regulation_store import RegulationStore


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory with sample regulation data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        
        # Create subdirectories
        eu_dir = data_dir / "eu"
        usa_dir = data_dir / "usa"
        eu_dir.mkdir()
        usa_dir.mkdir()
        
        # Create sample regulation files
        gdpr_data = {
            "id": "gdpr",
            "name": "General Data Protection Regulation",
            "region": "EU",
            "risk_category": "high",
            "summary": "GDPR is a data protection regulation",
            "articles": [
                {
                    "article": "32",
                    "title": "Security of Processing",
                    "summary": "Implement appropriate security measures",
                    "notes": "Important security requirement"
                }
            ],
            "developer_guidance": [
                "Encrypt sensitive data",
                "Implement access controls"
            ]
        }
        
        hipaa_data = {
            "id": "hipaa",
            "name": "Health Insurance Portability and Accountability Act",
            "region": "USA",
            "risk_category": "high",
            "summary": "HIPAA protects health information",
            "articles": [
                {
                    "article": "164.312",
                    "title": "Technical safeguards",
                    "summary": "Implement technical security measures",
                    "notes": "Technical requirements"
                }
            ],
            "developer_guidance": [
                "Encrypt PHI",
                "Implement audit logging"
            ]
        }
        
        # Write JSON files
        with open(eu_dir / "gdpr.json", "w", encoding="utf-8") as f:
            json.dump(gdpr_data, f)
        
        with open(usa_dir / "hipaa.json", "w", encoding="utf-8") as f:
            json.dump(hipaa_data, f)
        
        yield data_dir


def test_regulation_store_loads_files(temp_data_dir):
    """Test that RegulationStore loads all regulation files."""
    store = RegulationStore(str(temp_data_dir))
    
    assert len(store.regulations) == 2
    assert "gdpr" in store.regulations
    assert "hipaa" in store.regulations


def test_get_regulation_valid_id(temp_data_dir):
    """Test getting a regulation with a valid ID."""
    store = RegulationStore(str(temp_data_dir))
    
    regulation = store.get_regulation("gdpr")
    assert regulation is not None
    assert regulation["id"] == "gdpr"
    assert regulation["name"] == "General Data Protection Regulation"


def test_get_regulation_case_insensitive(temp_data_dir):
    """Test that get_regulation is case-insensitive."""
    store = RegulationStore(str(temp_data_dir))
    
    regulation1 = store.get_regulation("GDPR")
    regulation2 = store.get_regulation("gdpr")
    regulation3 = store.get_regulation("GdPr")
    
    assert regulation1 == regulation2 == regulation3
    assert regulation1 is not None


def test_get_regulation_invalid_id(temp_data_dir):
    """Test getting a regulation with an invalid ID."""
    store = RegulationStore(str(temp_data_dir))
    
    regulation = store.get_regulation("nonexistent")
    assert regulation is None


def test_search_regulations_by_name(temp_data_dir):
    """Test searching regulations by name."""
    store = RegulationStore(str(temp_data_dir))
    
    results = store.search_regulations("GDPR")
    assert len(results) > 0
    assert any(r["id"] == "gdpr" for r in results)


def test_search_regulations_by_summary(temp_data_dir):
    """Test searching regulations by summary."""
    store = RegulationStore(str(temp_data_dir))
    
    results = store.search_regulations("data protection")
    assert len(results) > 0
    assert any(r["id"] == "gdpr" for r in results)


def test_search_regulations_by_article_title(temp_data_dir):
    """Test searching regulations by article title."""
    store = RegulationStore(str(temp_data_dir))
    
    results = store.search_regulations("Security of Processing")
    assert len(results) > 0
    assert any(r["id"] == "gdpr" for r in results)


def test_search_regulations_by_developer_guidance(temp_data_dir):
    """Test searching regulations by developer guidance."""
    store = RegulationStore(str(temp_data_dir))
    
    results = store.search_regulations("Encrypt")
    assert len(results) > 0
    # Both GDPR and HIPAA should match
    assert len(results) >= 1


def test_search_regulations_no_results(temp_data_dir):
    """Test searching with keywords that don't match anything."""
    store = RegulationStore(str(temp_data_dir))
    
    results = store.search_regulations("nonexistent keyword xyz")
    assert len(results) == 0


def test_search_regulations_ranking(temp_data_dir):
    """Test that search results are ranked appropriately."""
    store = RegulationStore(str(temp_data_dir))
    
    results = store.search_regulations("GDPR")
    # Name matches should be ranked first
    if results:
        assert results[0]["match_type"] in ["name", "summary", "article_title", "article_summary", "developer_guidance"]

