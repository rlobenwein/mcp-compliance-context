"""Integration tests for the MCP server."""

import json
import tempfile
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session

from server.main import mcp


@pytest.fixture
def anyio_backend():
    """Set anyio backend to asyncio."""
    return "asyncio"


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
        
        # Create regions.json
        regions_data = [
            {
                "id": "eu",
                "name": "European Union",
                "regulations": ["gdpr"],
                "notes": "EU regulations"
            }
        ]
        
        with open(data_dir / "regions.json", "w", encoding="utf-8") as f:
            json.dump(regions_data, f)
        
        # Create sample regulation file
        gdpr_data = {
            "id": "gdpr",
            "name": "General Data Protection Regulation",
            "region": "EU",
            "risk_category": "high",
            "summary": "GDPR is a data protection regulation in the EU",
            "articles": [
                {
                    "article": "32",
                    "title": "Security of Processing",
                    "summary": "Implement appropriate security measures for data processing",
                    "notes": "Security requirement"
                }
            ],
            "developer_guidance": [
                "Encrypt sensitive data at rest and in transit",
                "Implement role-based access control"
            ]
        }
        
        with open(eu_dir / "gdpr.json", "w", encoding="utf-8") as f:
            json.dump(gdpr_data, f)
        
        yield data_dir


@pytest.fixture
async def client_session(temp_data_dir, monkeypatch):
    """Create a client session connected to the server with test data."""
    # Patch the DATA_DIR to use our temporary directory
    import server.main
    original_data_dir = server.main.DATA_DIR
    server.main.DATA_DIR = str(temp_data_dir)
    
    try:
        async with create_connected_server_and_client_session(
            mcp, raise_exceptions=True
        ) as session:
            yield session
    finally:
        server.main.DATA_DIR = original_data_dir


@pytest.mark.anyio
async def test_get_regulation_tool(client_session: ClientSession):
    """Test the get_regulation tool."""
    result = await client_session.call_tool("get_regulation", {"regulation_id": "gdpr"})
    
    assert result is not None
    content = result.content
    assert len(content) > 0
    
    # Check if we got structured content or text content
    if hasattr(result, "structuredContent") and result.structuredContent:
        regulation = result.structuredContent
    else:
        # Parse text content if structured not available
        import json
        text = content[0].text if hasattr(content[0], "text") else str(content[0])
        regulation = json.loads(text)
    
    assert regulation.get("id") == "gdpr"
    assert "name" in regulation
    assert "articles" in regulation


@pytest.mark.anyio
async def test_get_regulation_tool_invalid_id(client_session: ClientSession):
    """Test the get_regulation tool with an invalid ID."""
    result = await client_session.call_tool("get_regulation", {"regulation_id": "nonexistent"})
    
    assert result is not None
    content = result.content
    assert len(content) > 0
    
    # Should return an error message
    if hasattr(result, "structuredContent") and result.structuredContent:
        response = result.structuredContent
    else:
        import json
        text = content[0].text if hasattr(content[0], "text") else str(content[0])
        response = json.loads(text)
    
    assert "error" in response


@pytest.mark.anyio
async def test_get_region_tool(client_session: ClientSession):
    """Test the get_region tool."""
    result = await client_session.call_tool("get_region", {"region_id": "eu"})
    
    assert result is not None
    content = result.content
    assert len(content) > 0
    
    if hasattr(result, "structuredContent") and result.structuredContent:
        region = result.structuredContent
    else:
        import json
        text = content[0].text if hasattr(content[0], "text") else str(content[0])
        region = json.loads(text)
    
    assert region.get("id") == "eu"
    assert "regulations" in region
    assert len(region["regulations"]) > 0


@pytest.mark.anyio
async def test_search_regulations_tool(client_session: ClientSession):
    """Test the search_regulations tool."""
    result = await client_session.call_tool("search_regulations", {"keywords": "data protection"})
    
    assert result is not None
    content = result.content
    assert len(content) > 0
    
    if hasattr(result, "structuredContent") and result.structuredContent:
        results = result.structuredContent
    else:
        import json
        text = content[0].text if hasattr(content[0], "text") else str(content[0])
        results = json.loads(text)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert "id" in results[0]
    assert "snippet" in results[0]


@pytest.mark.anyio
async def test_list_tools(client_session: ClientSession):
    """Test that all three tools are available."""
    tools_response = await client_session.list_tools()
    
    tool_names = [tool.name for tool in tools_response.tools]
    
    assert "get_regulation" in tool_names
    assert "get_region" in tool_names
    assert "search_regulations" in tool_names

