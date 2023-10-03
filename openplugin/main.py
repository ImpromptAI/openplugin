import os
from typing import Optional

import typer
import uvicorn
from dotenv import load_dotenv
from typing_extensions import Annotated

app = typer.Typer()


@app.callback()
def callback():
    """
    Permutate is an automated testing framework for LLM Plugins.
    """


@app.command()
def start_server(
    openai_api_key: Optional[
        Annotated[
            str,
            typer.Option(
                help="OpenAI API Key", rich_help_panel="Customization and Utils"
            ),
        ]
    ]
):
    """
    Start the openplugin server
    """
    if openai_api_key is None:
        if os.environ.get("OPENAI_API_KEY") is None:
            typer.echo("OPENAI_API_KEY is not set.")
            raise typer.Exit(code=1)
    else:
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = openai_api_key

    from openplugin.api import app

    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8012)),
    )
