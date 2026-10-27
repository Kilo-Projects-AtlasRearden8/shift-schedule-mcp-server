"""Entry point so `python -m shift_mcp` runs the server."""

import asyncio
import logging

from .server import main


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())