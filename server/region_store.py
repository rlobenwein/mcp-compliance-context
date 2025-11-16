"""RegionStore class for loading and managing region data."""

import json
from pathlib import Path
from typing import Any

from .regulation_store import RegulationStore
from .utils import load_json_file, normalize_string


class RegionStore:
    """Stores and manages region data loaded from JSON files."""
    
    def __init__(
        self, 
        data_dir: str = r"C:\regulation-data",
        regulation_store: RegulationStore | None = None
    ):
        """
        Initialize the RegionStore and load regions.json.
        
        Args:
            data_dir: Path to the regulation data directory
            regulation_store: Optional RegulationStore instance for loading regulations
        """
        self.data_dir = Path(data_dir)
        self.regulation_store = regulation_store
        self.regions: dict[str, dict[str, Any]] = {}
        self._load_regions()
    
    def _load_regions(self) -> None:
        """Load regions.json from the data directory."""
        regions_path = self.data_dir / "regions.json"
        
        if not regions_path.exists():
            raise FileNotFoundError(
                f"Regions file not found: {regions_path}. "
                "Please ensure regions.json exists in the data directory."
            )
        
        try:
            data = load_json_file(regions_path)
            # Handle both list and dict formats
            if isinstance(data, list):
                regions_list = data
            elif isinstance(data, dict) and "regions" in data:
                regions_list = data["regions"]
            else:
                regions_list = [data]
            
            for region in regions_list:
                if "id" in region:
                    region_id = normalize_string(region["id"])
                    self.regions[region_id] = region
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in regions.json: {e}")
    
    def get_region(
        self, 
        region_id: str, 
        regulation_store: RegulationStore | None = None
    ) -> dict[str, Any] | None:
        """
        Get a region by its ID with aggregated regulations.
        
        Args:
            region_id: The region ID to look up
            regulation_store: RegulationStore instance to load regulations.
                            Uses self.regulation_store if not provided.
        
        Returns:
            Region dictionary with regulations list populated, or None if not found
        """
        normalized_id = normalize_string(region_id)
        region = self.regions.get(normalized_id)
        
        if region is None:
            return None
        
        # Use provided store or fall back to instance store
        store = regulation_store or self.regulation_store
        
        if store is None:
            # If no store available, return region without regulations
            return {**region, "regulations": []}
        
        # Aggregate regulations for this region
        regulation_ids = region.get("regulations", [])
        regulations = []
        
        for reg_id in regulation_ids:
            regulation = store.get_regulation(reg_id)
            if regulation:
                regulations.append(regulation)
            else:
                # Regulation file might be in region subdirectory
                reg_path = self.data_dir / normalized_id / f"{reg_id}.json"
                if reg_path.exists():
                    try:
                        regulation = load_json_file(reg_path)
                        regulations.append(regulation)
                    except Exception:
                        # Skip if we can't load it
                        continue
        
        # Return region with populated regulations
        return {
            **region,
            "regulations": regulations
        }

