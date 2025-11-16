"""MCP server for providing regulatory context to LLMs."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from .region_store import RegionStore
from .regulation_store import RegulationStore


def get_regulation_data_dir() -> str:
    """
    Get the regulation data directory from environment variable.
    
    Returns:
        Path to the regulation data directory as a string
        
    Raises:
        ValueError: If REGULATION_DATA_DIR is not set
    """
    # Load .env file if it exists
    load_dotenv()
    
    data_dir = os.getenv("REGULATION_DATA_DIR")
    if not data_dir:
        raise ValueError(
            "REGULATION_DATA_DIR environment variable is not set. "
            "Please create a .env file in the project root with: "
            "REGULATION_DATA_DIR=C:\\regulation-data"
        )
    
    return data_dir


# Get data directory from environment variable
DATA_DIR = get_regulation_data_dir()


@dataclass
class AppContext:
    """Application context with typed dependencies."""
    
    regulation_store: RegulationStore
    region_store: RegionStore


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manage application lifecycle with type-safe context.
    
    Initializes RegulationStore and RegionStore on startup,
    and ensures proper cleanup on shutdown.
    """
    # Initialize stores on startup
    regulation_store = RegulationStore(DATA_DIR)
    region_store = RegionStore(DATA_DIR, regulation_store)
    
    try:
        yield AppContext(
            regulation_store=regulation_store,
            region_store=region_store
        )
    finally:
        # Cleanup on shutdown (if needed in the future)
        pass


# Create FastMCP server with lifespan management
mcp = FastMCP("Regulatory Context Server", lifespan=app_lifespan)


@mcp.tool()
def get_regulation(
    regulation_id: str,
    ctx: Context[ServerSession, AppContext]
) -> dict[str, Any]:
    """
    Retrieve the full regulation JSON by its ID.
    
    Returns the complete regulation including articles, summaries, notes,
    developer_guidance, and risk_category. The input is normalized
    (case-insensitive).
    
    Args:
        regulation_id: The ID of the regulation to retrieve (e.g., "gdpr", "hipaa")
        ctx: Server context with access to regulation store
        
    Returns:
        Full regulation dictionary with all fields, or error dict if not found
        
    Example:
        get_regulation("gdpr") -> {
            "id": "gdpr",
            "name": "General Data Protection Regulation",
            "region": "EU",
            "risk_category": "high",
            "articles": [...],
            "developer_guidance": [...],
            "summary": "..."
        }
    """
    app_ctx = ctx.request_context.lifespan_context
    regulation = app_ctx.regulation_store.get_regulation(regulation_id)
    
    if regulation is None:
        return {
            "error": f"Regulation '{regulation_id}' not found. "
                     "Please check the regulation ID and try again."
        }
    
    return regulation


@mcp.tool()
def get_region(
    region_id: str,
    ctx: Context[ServerSession, AppContext]
) -> dict[str, Any]:
    """
    Retrieve information about a region and its associated regulations.
    
    Returns the region information plus a list of all regulations
    belonging to that region. The input is normalized (case-insensitive).
    Regulations are loaded from their respective JSON files and aggregated.
    
    Args:
        region_id: The ID of the region to retrieve (e.g., "eu", "usa")
        ctx: Server context with access to region and regulation stores
        
    Returns:
        Region dictionary with regulations list populated, or error dict if not found
        
    Example:
        get_region("eu") -> {
            "id": "eu",
            "name": "European Union",
            "regulations": [
                {"id": "gdpr", "name": "...", ...},
                {"id": "dora", "name": "...", ...}
            ],
            "notes": "..."
        }
    """
    app_ctx = ctx.request_context.lifespan_context
    region = app_ctx.region_store.get_region(
        region_id,
        app_ctx.regulation_store
    )
    
    if region is None:
        return {
            "error": f"Region '{region_id}' not found. "
                     "Please check the region ID and try again."
        }
    
    return region


@mcp.tool()
def search_regulations(
    keywords: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict[str, Any]]:
    """
    Search across all regulations for matching keywords.
    
    Searches in the following fields:
    - name: Regulation name
    - summary: Overall regulation summary
    - articles[].title: Article titles
    - articles[].summary: Article summaries
    - developer_guidance: Developer guidance items
    
    Returns a ranked list of regulation IDs with snippets showing why they matched.
    Results are ranked by relevance (name matches first, then summary, then articles).
    
    Args:
        keywords: Search keywords (case-insensitive)
        ctx: Server context with access to regulation store
        
    Returns:
        List of search results, each containing:
        - id: Regulation ID
        - name: Regulation name
        - snippet: Text snippet showing the match
        - match_type: Type of match (name, summary, article_title, etc.)
        - all_matches: Count of total matches found
        
    Example:
        search_regulations("data protection") -> [
            {
                "id": "gdpr",
                "name": "General Data Protection Regulation",
                "snippet": "...data protection...",
                "match_type": "summary",
                "all_matches": 3
            },
            ...
        ]
    """
    app_ctx = ctx.request_context.lifespan_context
    results = app_ctx.regulation_store.search_regulations(keywords)
    
    if not results:
        return [
            {
                "message": f"No regulations found matching '{keywords}'. "
                           "Try different keywords or check spelling."
            }
        ]
    
    return results


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

