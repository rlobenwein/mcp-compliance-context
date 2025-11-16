#!/usr/bin/env python
"""Entry point script for the MCP Regulatory Context Server.

This script ensures the server can be run from any directory by
adding the project root to the Python path.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import and run the server
from server.main import main

if __name__ == "__main__":
    main()

