from mangum import Mangum
from openplugin.api import create_app


def handler(event, context):
    print(f"Running event: {event}")
    app = create_app(root_path="openplugin")
    asgi_handler = Mangum(app, lifespan="off")
    response = asgi_handler(event, context)
    print(f"Response: {response}")
    return response
