from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey

from openplugin.api import auth
from openplugin.plugins.execution.implementations.operation_execution_with_imprompt import (
    ExecutionException,
    OperationExecutionParams,
    OperationExecutionWithImprompt,
)

# Create a FastAPI router instance
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/operation-execution")
def operation_execution(
    params: OperationExecutionParams, api_key: APIKey = Depends(auth.get_api_key)
):
    try:
        ex = OperationExecutionWithImprompt(params)
        response = ex.run()
        return response
    except ExecutionException as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "{}".format(e),
                "metadata": e.metadata,
            },
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": "{}".format(e),
                "metadata": {},
            },
        )
