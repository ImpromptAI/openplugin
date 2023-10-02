from openplugin.bindings.operation_execution_impl import (
    OperationExecutionImpl,
    OperationExecutionParams,
)


def test_operation_execution_impl():
    params = OperationExecutionParams(
        api="https://www.klarna.com/us/shopping/public/openai/v0/products",
        method="get",
        query_params={"countryCode": "US", "q": "tshirt", "size": 4},
        body=None,
        header=None,
        post_processing_cleanup_prompt="Write a summary of the response.",
        llm=None,
    )
    response = OperationExecutionImpl(params=params).run()
    assert response is not None
    assert response.response is not None
    assert response.post_cleanup_text is not None
