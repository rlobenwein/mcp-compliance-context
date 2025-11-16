"""Utility functions for the regulatory context server."""

import json
from pathlib import Path
from typing import Any


def normalize_string(s: str) -> str:
    """
    Normalize a string to lowercase and strip whitespace.
    
    Args:
        s: Input string to normalize
        
    Returns:
        Normalized string (lowercase, stripped)
    """
    return s.strip().lower()


def load_json_file(file_path: str | Path) -> dict[str, Any]:
    """
    Safely load a JSON file with error handling.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

