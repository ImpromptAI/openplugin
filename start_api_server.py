import os
import uvicorn
from api import app
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    host = os.environ['HOST']
    port = int(os.environ['PORT'])
    print("Server listening on port " + str(port))
    uvicorn.run(app, host=host, port=port)
