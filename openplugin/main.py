import asyncio
import os
from typing import Optional

import typer
import uvicorn
from dotenv import load_dotenv
from typing_extensions import Annotated

from openplugin.core.plugin_runner import run_prompt_on_plugin
from openplugin.prompt.parser import PromptParser
from openplugin.prompt.prompt_page import PromptPage, create_prompt_page_from_json

app = typer.Typer(pretty_exceptions_enable=False)


@app.callback()
def callback():
    """
    Permutate is an automated testing framework for LLM Plugins.
    """


@app.command()
def start_server(
    env_file: Optional[
        Annotated[
            str,
            typer.Option(
                help="ENV File Location", rich_help_panel="Customization and Utils"
            ),
        ]
    ]
):
    """
    Start the openplugin server
    """
    if env_file is None:
        typer.echo("Please pass environment file path.")
        raise typer.Exit(code=1)
    load_dotenv(env_file)
    from openplugin.api import create_app

    app = create_app()
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8012)),
    )


@app.command()
def run_plugin(
    openplugin: str = typer.Option(
        ...,
        prompt="Provide your openplugin manifest: ",
        help="OpenPlugin Manifest File or URL",
    ),
    prompt: str = typer.Option(
        ..., prompt="Provide your prompt: ", help="Prompt to execute the plugin"
    ),
    log_level: Optional[
        Annotated[
            str,
            typer.Option(
                "--log-level",
                help="Set the level of log",
                show_default=True,
            ),
        ]
    ] = "INFO",
):
    """
    Execute a plugin with custom prompt
    """
    if openplugin is None:
        typer.echo("Pass OpenPlugin Manifest File or URL.")
        raise typer.Exit(code=1)
    if prompt is None:
        typer.echo("Pass Prompt.")
        raise typer.Exit(code=1)
    asyncio.run(run_prompt_on_plugin(openplugin, prompt, log_level=log_level))


@app.command()
def run_prompt_page(
    page: Optional[
        Annotated[
            str,
            typer.Option(
                help="Prompt Page File",
                rich_help_panel="Customization and Utils",
            ),
        ]
    ],
    prompt: Optional[
        Annotated[
            str,
            typer.Option(
                help="Prompt to execute",
                rich_help_panel="Customization and Utils",
            ),
        ]
    ],
):
    """
    Run a prompt page
    """
    typer.echo("=====WELCOME TO PAGE PROMPT PARSER===")
    if page is None:
        typer.echo("Please pass page.")
        raise typer.Exit(code=1)
    if prompt is None:
        typer.echo("Please pass prompt.")
        raise typer.Exit(code=1)
    prompt_page: PromptPage = create_prompt_page_from_json(file_path=page)
    user_input_map: dict = {}
    for user_input in prompt_page.user_inputs:
        value = typer.prompt(f"{user_input.name}")
        user_input_map[user_input.name] = value
    parser = PromptParser(prompt_page=prompt_page)
    parser.parse(prompt=prompt, user_input_map=user_input_map)


if __name__ == "__main__":
    app()
