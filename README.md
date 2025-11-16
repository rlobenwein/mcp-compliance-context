# MCP Compliance Context Server

An MCP server that provides data protection regulations (GDPR, HIPAA, CCPA, LGPD, etc.) to LLMs, enabling AI assistants to help developers create compliant applications through real-time regulatory context during code review and analysis.

## Overview

This server loads regulatory data from JSON files stored in a configurable directory (set via `.env` file) and provides three main tools:

1. **get_regulation** - Retrieve full regulation details by ID
2. **get_region** - Get region information with associated regulations
3. **search_regulations** - Search across all regulations for matching keywords

## Requirements

- Python 3.10 or higher
- MCP Python SDK
- pytest and pytest-asyncio (for testing)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the regulation data directory:

   Create a `.env` file in the project root to specify where your regulation data will be stored:
   
   ```bash
   # Copy the example file
   copy .env.example .env
   # On Linux/Mac: cp .env.example .env
   ```
   
   Then edit `.env` and set your desired regulation data directory path:
   ```env
   REGULATION_DATA_DIR=C:\regulation-data
   ```
   
   **Path format:**
   - Windows: Use double backslashes (`C:\\regulation-data`) or forward slashes (`C:/regulation-data`)
   - Linux/Mac: Use standard paths (`/path/to/regulation-data`)
   
   **Note:** Both the setup script and the server will read this path from the `.env` file.

4. Set up the regulation data directory:

   **Option A: Use the setup script (recommended)**
   
   Run the provided setup script to automatically create the directory and copy sample data:
   ```bash
   python setup_data.py
   ```
   
   This will:
   - Read the `REGULATION_DATA_DIR` from your `.env` file
   - Create the regulation data directory at the specified path
   - Copy all sample data files from `sample_data/` to the target directory
   - Create the required subdirectories (`eu/`, `usa/`, `brazil/`)
   
   **Option B: Manual setup**
   
   If you prefer to set it up manually:
   - Create the directory at the path specified in your `.env` file
   - Copy the sample data structure from `sample_data/` to that directory
   - Ensure the directory structure matches:
     ```
     <your-regulation-data-dir>/
     ├── regions.json
     ├── eu/
     │   ├── gdpr.json
     │   └── dora.json
     ├── usa/
     │   ├── hipaa.json
     │   ├── ccpa.json
     │   └── glba.json
     └── brazil/
         └── lgpd.json
     ```

## Running the Server

To run the server directly, use the entry point script:

```bash
python run_server.py
```

Alternatively, you can run it as a module (requires the project root to be in PYTHONPATH):

```bash
python -m server.main
```

The server will start and communicate via stdio (standard input/output), which is the standard transport for MCP servers in Cursor.

## Data Format

### Regulation JSON Schema

Each regulation file must follow this structure:

```json
{
  "id": "gdpr",
  "name": "General Data Protection Regulation",
  "region": "EU",
  "risk_category": "high",
  "summary": "Overall summary of the regulation",
  "articles": [
    {
      "article": "32",
      "title": "Security of Processing",
      "summary": "Article summary text",
      "notes": "Additional notes about the article"
    }
  ],
  "developer_guidance": [
    "Encrypt sensitive data at rest and in transit",
    "Implement role-based access control"
  ]
}
```

### Regions JSON Schema

The `regions.json` file should contain:

```json
[
  {
    "id": "eu",
    "name": "European Union",
    "regulations": ["gdpr", "dora"],
    "notes": "Optional notes about the region"
  },
  {
    "id": "brazil",
    "name": "Brazil",
    "regulations": ["lgpd"],
    "notes": "Optional notes about the region"
  }
]
```

## Tools

### 1. get_regulation

Retrieves the full regulation JSON by its ID.

**Input:**
- `regulation_id` (string): The ID of the regulation (e.g., "gdpr", "hipaa")

**Output:**
- Full regulation dictionary with all fields, or an error message if not found

**Example:**
```python
get_regulation("gdpr")
# Returns: {
#   "id": "gdpr",
#   "name": "General Data Protection Regulation",
#   "region": "EU",
#   "risk_category": "high",
#   "articles": [...],
#   "developer_guidance": [...],
#   "summary": "..."
# }
```

**Notes:**
- Input is normalized (case-insensitive), so "GDPR", "gdpr", and "GdPr" all work
- Returns a structured error message if the regulation is not found

### 2. get_region

Retrieves information about a region and its associated regulations.

**Input:**
- `region_id` (string): The ID of the region (e.g., "eu", "usa", "brazil")

**Output:**
- Region dictionary with regulations list populated, or an error message if not found

**Example:**
```python
get_region("eu")
# Returns: {
#   "id": "eu",
#   "name": "European Union",
#   "regulations": [
#     {"id": "gdpr", "name": "...", ...},
#     {"id": "dora", "name": "...", ...}
#   ],
#   "notes": "..."
# }
```

**Notes:**
- Input is normalized (case-insensitive)
- Automatically loads and aggregates all regulations belonging to the region
- Returns regulations as full objects, not just IDs

### 3. search_regulations

Searches across all regulations for matching keywords.

**Input:**
- `keywords` (string): Search keywords (case-insensitive)

**Output:**
- Ranked list of search results, each containing:
  - `id`: Regulation ID
  - `name`: Regulation name
  - `snippet`: Text snippet showing why it matched
  - `match_type`: Type of match (name, summary, article_title, article_summary, developer_guidance)
  - `all_matches`: Count of total matches found

**Example:**
```python
search_regulations("data protection")
# Returns: [
#   {
#     "id": "gdpr",
#     "name": "General Data Protection Regulation",
#     "snippet": "...data protection...",
#     "match_type": "summary",
#     "all_matches": 3
#   },
#   ...
# ]
```

**Search Fields:**
- Regulation name
- Regulation summary
- Article titles
- Article summaries
- Developer guidance items

**Ranking:**
Results are ranked by relevance:
1. Name matches (highest priority)
2. Summary matches
3. Article matches
4. Developer guidance matches

## Configuring on Cursor

To use this MCP server in Cursor, follow these steps:

1. Open the MCP settings JSON file in Cursor
2. Add the configuration JSON to the `mcpServers` object:

**Option 1: Using the entry point script (Recommended)**

```json
{
  "mcpServers": {
    "regulatory-context": {
      "command": "python",
      "args": ["run_server.py"],
      "cwd": "D:/Projects/mcp",
      "env": {}
    }
  }
}
```

**Option 2: Using module syntax with PYTHONPATH**

```json
{
  "mcpServers": {
    "regulatory-context": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "D:/Projects/mcp",
      "env": {
        "PYTHONPATH": "D:/Projects/mcp"
      }
    }
  }
}
```

3. Update the `cwd` field (and `PYTHONPATH` in Option 2) with the path to your project root directory (where this README is located)
4. Restart Cursor or reload the MCP servers

The server will now be available to Cursor's AI assistant, and you can use the tools during code review or analysis tasks.

## How Cursor Should Interact with the Server

When Cursor's AI assistant needs regulatory context:

1. **During Code Review**: If reviewing code that handles personal data, the AI can call `get_regulation("gdpr")` or `search_regulations("data protection")` to retrieve relevant requirements.

2. **Compliance Analysis**: When analyzing code for compliance, the AI can:
   - Use `get_region("eu")` to get all EU regulations
   - Use `search_regulations("encryption")` to find regulations mentioning encryption
   - Use `get_regulation("hipaa")` to get specific HIPAA requirements

3. **Developer Guidance**: The AI can retrieve `developer_guidance` from regulations to provide specific implementation recommendations.

4. **Article Lookup**: When specific regulatory articles are mentioned, the AI can retrieve full article details from the regulation data.

**Example Interaction:**
```
Prompt: "Does this code comply with GDPR requirements for data encryption?"

Response: [Calls get_regulation("gdpr")]
    [Reviews Article 32 and developer_guidance]
    "Based on GDPR Article 32 (Security of Processing), you need to implement 
     appropriate technical measures including encryption. The developer guidance 
     recommends encrypting sensitive data at rest and in transit using AES-256 
     and TLS 1.3+. Your current implementation..."
```

## Testing

Run the test suite:

```bash
pytest tests/
```

To run with verbose output:

```bash
pytest tests/ -v
```

The tests include:
- Unit tests for `RegulationStore` (loading, normalization, search)
- Unit tests for `RegionStore` (loading, aggregation)
- Integration tests for the MCP server tools

**Note**: Tests use temporary directories and sample data, so they don't require the actual regulation data directory to exist.

## Project Structure

```
mcp/
├── server/
│   ├── __init__.py
│   ├── main.py              # FastMCP server entry point
│   ├── regulation_store.py  # RegulationStore class
│   ├── region_store.py      # RegionStore class
│   └── utils.py             # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_regulation_store.py
│   ├── test_region_store.py
│   └── test_server.py
├── sample_data/             # Sample JSON files for reference
│   ├── regions.json
│   ├── eu/
│   │   ├── gdpr.json
│   │   └── dora.json
│   ├── usa/
│   │   ├── hipaa.json
│   │   ├── ccpa.json
│   │   └── glba.json
│   └── brazil/
│       └── lgpd.json
├── README.md
└── requirements.txt
```

## Key Features

- **In-Memory Caching**: All regulation data is loaded into memory on server startup for fast access
- **Case-Insensitive Matching**: All ID lookups are normalized for user-friendly interaction
- **Comprehensive Search**: Searches across multiple fields with relevance ranking
- **Structured Output**: All tools return predictable, structured objects that LLMs can safely consume
- **Error Handling**: Meaningful error messages when regulations or regions are not found
- **Type Safety**: Full type hints throughout the codebase
- **Modular Design**: Clean separation of concerns for easy extension

## Extending the Server

To add new regulations:

1. Create a new JSON file following the regulation schema
2. Place it in the appropriate region subdirectory within your regulation data directory (configured in `.env`)
   - Example: `<your-regulation-data-dir>/eu/new-regulation.json`
3. Add the regulation ID to the region's `regulations` list in `regions.json`
4. Restart the server (it will automatically load the new file)

To add new regions:

1. Add a new entry to `regions.json` with the region's ID, name, and regulation list
2. Create a subdirectory for the region in your regulation data directory
   - Example: `<your-regulation-data-dir>/new-region/`
3. Place regulation files in that subdirectory
4. Restart the server

## License

This project is provided as-is for use with MCP and Cursor.
