import os
from dotenv import load_dotenv
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.security.api_key import APIKeyHeader

keys = set()
load_dotenv()
if os.environ.get("USER_ACCESS_KEYS_FILE_PATH") is not None:
    load_dotenv(os.environ.get("USER_ACCESS_KEYS_FILE_PATH"))
for key in os.environ:
    if key.startswith("user_access_key_"):
        keys.add(os.environ[key])
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    # if keys not setup then allow all
    if len(keys) == 0:
        return api_key_header
    if api_key_header in keys:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
