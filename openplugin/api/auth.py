import os

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

# Create an empty set to store valid API keys
keys = set()
# Load environment variables from a .env file in the current directory
load_dotenv()

# If a custom path for user access keys is specified in an environment variable,
# load keys from that file
if os.environ.get("USER_ACCESS_KEYS_FILE_PATH") is not None:
    load_dotenv(os.environ.get("USER_ACCESS_KEYS_FILE_PATH"))

# Iterate through environment variables to find keys that start with "user_access_key_"
for key in os.environ:
    if key.startswith("user_access_key_"):
        keys.add(os.environ[key])

# Create an APIKeyHeader instance with the name "x-api-key" and auto_error set to False
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


# Define an asynchronous function to get the API key from the header
async def get_api_key(api_key_header: str = Security(api_key_header)):
    # If no keys are set up (empty set), allow all API keys (no validation)
    if len(keys) == 0:
        return api_key_header
    # Check if the provided API key is in the set of valid keys
    if api_key_header in keys:
        return api_key_header
    else:
        # If the API key is not valid, raise a 403 Forbidden HTTP exception
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
