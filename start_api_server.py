import os

import uvicorn
from dotenv import load_dotenv

from openplugin.api import create_app

if __name__ == "__main__":
    load_dotenv()
    host = os.environ["HOST"]
    port = int(os.environ["PORT"])
    root_path = os.environ.get("ROOT_PATH")

    print("STARTED OPENPLUGIN SERVER ON PORT: " + str(port))
    app = create_app(root_path=root_path)
    uvicorn.run(app, host=host, port=port)
