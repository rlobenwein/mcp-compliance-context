"""Setup script to create the regulation data directory and copy sample data."""

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


def get_regulation_data_dir() -> Path:
    """
    Get the regulation data directory from environment variable.
    
    Returns:
        Path to the regulation data directory
        
    Raises:
        SystemExit: If REGULATION_DATA_DIR is not set
    """
    # Load .env file if it exists
    load_dotenv()
    
    data_dir = os.getenv("REGULATION_DATA_DIR")
    if not data_dir:
        print("Error: REGULATION_DATA_DIR environment variable is not set.")
        print("\nPlease create a .env file in the project root with:")
        print("  REGULATION_DATA_DIR=C:\\regulation-data")
        print("\nOr set the environment variable directly.")
        print("\nYou can copy .env.example to .env and update it:")
        print("  copy .env.example .env")
        sys.exit(1)
    
    return Path(data_dir)


def setup_regulation_data():
    """Create the regulation data directory and copy sample data."""
    # Target directory from environment variable
    target_dir = get_regulation_data_dir()
    source_dir = Path(__file__).parent / "sample_data"
    
    if not source_dir.exists():
        print(f"Error: Source directory '{source_dir}' not found.")
        print("Please ensure you're running this script from the project root.")
        sys.exit(1)
    
    # Create target directory if it doesn't exist
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {target_dir}")
    except PermissionError:
        print(f"Error: Permission denied. Cannot create directory '{target_dir}'.")
        print("Please run this script with appropriate permissions or create the directory manually.")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating directory: {e}")
        sys.exit(1)
    
    # Copy files
    try:
        # Copy regions.json
        if (source_dir / "regions.json").exists():
            shutil.copy2(source_dir / "regions.json", target_dir / "regions.json")
            print(f"Copied: regions.json")
        
        # Copy EU regulations
        eu_source = source_dir / "eu"
        eu_target = target_dir / "eu"
        if eu_source.exists():
            eu_target.mkdir(exist_ok=True)
            for file in eu_source.glob("*.json"):
                shutil.copy2(file, eu_target / file.name)
                print(f"Copied: eu/{file.name}")
        
        # Copy USA regulations
        usa_source = source_dir / "usa"
        usa_target = target_dir / "usa"
        if usa_source.exists():
            usa_target.mkdir(exist_ok=True)
            for file in usa_source.glob("*.json"):
                shutil.copy2(file, usa_target / file.name)
                print(f"Copied: usa/{file.name}")
        
        # Copy Brazil regulations
        brazil_source = source_dir / "brazil"
        brazil_target = target_dir / "brazil"
        if brazil_source.exists():
            brazil_target.mkdir(exist_ok=True)
            for file in brazil_source.glob("*.json"):
                shutil.copy2(file, brazil_target / file.name)
                print(f"Copied: brazil/{file.name}")
        
        print(f"\n✓ Successfully set up regulation data at: {target_dir}")
        print("\nDirectory structure:")
        print(f"  {target_dir}/")
        print(f"    ├── regions.json")
        print(f"    ├── eu/")
        for file in sorted(eu_target.glob("*.json")) if eu_target.exists() else []:
            print(f"    │   ├── {file.name}")
        print(f"    ├── usa/")
        for file in sorted(usa_target.glob("*.json")) if usa_target.exists() else []:
            print(f"    │   ├── {file.name}")
        print(f"    └── brazil/")
        for file in sorted(brazil_target.glob("*.json")) if brazil_target.exists() else []:
            print(f"        ├── {file.name}")
        
    except Exception as e:
        print(f"Error copying files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Setting up regulation data directory...")
    print(f"Source: {Path(__file__).parent / 'sample_data'}")
    
    # Get target directory from environment
    try:
        target_dir = get_regulation_data_dir()
        print(f"Target: {target_dir}\n")
    except SystemExit:
        sys.exit(1)
    
    setup_regulation_data()

