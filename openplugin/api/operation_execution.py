from openplugin.api import auth
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from openplugin import OperationExecutionParams, OperationExecutionImpl
from typing import Optional
# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/operation-execution")
def operation_execution(
        params: OperationExecutionParams,
        api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        ex = OperationExecutionImpl(params)
        response = ex.run()
        return response
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500,
                            content={"message": "Failed to run plugin: {}".format(e)})
