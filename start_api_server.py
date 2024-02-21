import os
import sys

import uvicorn
from dotenv import load_dotenv
from loguru import logger

from openplugin.api import app

load_dotenv()

log_level = os.environ.get("LOG_LEVEL", "FLOW")
if log_level:
    logger.remove()
    logger.level("FLOW", no=38, color="<yellow>", icon="🚀")
    logger.add(sys.stderr, level=log_level.upper())

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8007))
    port = 8006
    print("Server listening on port " + str(port))
    uvicorn.run(app, host=host, port=port)
