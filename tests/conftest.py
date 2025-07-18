import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "stubs"))

pytest_plugins = ["pytest_asyncio"]
