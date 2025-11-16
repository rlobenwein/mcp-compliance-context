"""RegulationStore class for loading and managing regulation data."""

import json
import os
from pathlib import Path
from typing import Any

from .utils import load_json_file, normalize_string


class RegulationStore:
    """Stores and manages regulation data loaded from JSON files."""
    
    def __init__(self, data_dir: str = r"C:\regulation-data"):
        """
        Initialize the RegulationStore and load all regulation files.
        
        Args:
            data_dir: Path to the regulation data directory
        """
        self.data_dir = Path(data_dir)
        self.regulations: dict[str, dict[str, Any]] = {}
        self._load_regulations()
    
    def _load_regulations(self) -> None:
        """Load all regulation JSON files from the data directory."""
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Regulation data directory not found: {self.data_dir}. "
                "Please ensure the directory exists and contains regulation JSON files."
            )
        
        # Walk through all subdirectories to find regulation JSON files
        for root, dirs, files in os.walk(self.data_dir):
            # Skip the root directory itself if it contains regions.json
            for file in files:
                if file.endswith(".json") and file != "regions.json":
                    file_path = Path(root) / file
                    try:
                        data = load_json_file(file_path)
                        if "id" in data:
                            reg_id = normalize_string(data["id"])
                            self.regulations[reg_id] = data
                    except (json.JSONDecodeError, KeyError) as e:
                        # Skip invalid files but continue loading others
                        print(f"Warning: Skipping invalid regulation file {file_path}: {e}")
                        continue
    
    def get_regulation(self, regulation_id: str) -> dict[str, Any] | None:
        """
        Get a regulation by its ID (case-insensitive).
        
        Args:
            regulation_id: The regulation ID to look up
            
        Returns:
            The full regulation dictionary, or None if not found
        """
        normalized_id = normalize_string(regulation_id)
        return self.regulations.get(normalized_id)
    
    def search_regulations(
        self, keywords: str
    ) -> list[dict[str, Any]]:
        """
        Search regulations for matching keywords.
        
        Searches across:
        - name
        - summary
        - articles[].title
        - articles[].summary
        - developer_guidance
        
        Args:
            keywords: Search keywords (case-insensitive)
            
        Returns:
            List of ranked results, each containing:
            - id: Regulation ID
            - name: Regulation name
            - snippet: Text snippet showing why it matched
            - match_type: Type of match (name, summary, article, guidance)
        """
        normalized_keywords = normalize_string(keywords)
        results: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        
        for reg_id, reg in self.regulations.items():
            if reg_id in seen_ids:
                continue
            
            matches: list[tuple[str, str]] = []  # (match_type, snippet)
            
            # Search in name
            name = reg.get("name", "")
            if normalized_keywords in normalize_string(name):
                matches.append(("name", name))
            
            # Search in summary
            summary = reg.get("summary", "")
            if normalized_keywords in normalize_string(summary):
                # Extract a snippet around the match
                snippet = self._extract_snippet(summary, normalized_keywords)
                matches.append(("summary", snippet))
            
            # Search in articles
            for article in reg.get("articles", []):
                title = article.get("title", "")
                article_summary = article.get("summary", "")
                
                if normalized_keywords in normalize_string(title):
                    matches.append(("article_title", f"Article {article.get('article', 'N/A')}: {title}"))
                
                if normalized_keywords in normalize_string(article_summary):
                    snippet = self._extract_snippet(article_summary, normalized_keywords)
                    matches.append(("article_summary", f"Article {article.get('article', 'N/A')}: {snippet}"))
            
            # Search in developer_guidance
            for guidance in reg.get("developer_guidance", []):
                if normalized_keywords in normalize_string(guidance):
                    matches.append(("developer_guidance", guidance))
            
            # If we found matches, add to results
            if matches:
                seen_ids.add(reg_id)
                # Use the first match as the primary snippet
                primary_match_type, primary_snippet = matches[0]
                
                results.append({
                    "id": reg_id,
                    "name": reg.get("name", ""),
                    "snippet": primary_snippet,
                    "match_type": primary_match_type,
                    "all_matches": len(matches),  # Count of total matches
                })
        
        # Simple ranking: prioritize name matches, then summary, then others
        def rank_key(result: dict[str, Any]) -> int:
            match_type = result.get("match_type", "")
            if match_type == "name":
                return 0
            elif match_type == "summary":
                return 1
            elif match_type.startswith("article"):
                return 2
            else:
                return 3
        
        results.sort(key=rank_key)
        return results
    
    def _extract_snippet(self, text: str, keywords: str, context_chars: int = 100) -> str:
        """
        Extract a snippet of text around matching keywords.
        
        Args:
            text: The full text to search
            keywords: The keywords to find
            context_chars: Number of characters to include before/after match
            
        Returns:
            Snippet with context around the match
        """
        text_lower = normalize_string(text)
        keywords_lower = normalize_string(keywords)
        
        idx = text_lower.find(keywords_lower)
        if idx == -1:
            return text[:context_chars * 2] if len(text) > context_chars * 2 else text
        
        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keywords) + context_chars)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet

