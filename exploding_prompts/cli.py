"""
This module contains the command line interface for the exploding-prompts package.
"""

from typing import List
from collections import namedtuple
from pathlib import Path

import click

from exploding_prompts.config import Config
from exploding_prompts.prompt_explode import get_exploded_prompt_views
from exploding_prompts.prompt_view import PromptView


FilterTuple = namedtuple("FilterTuple", ["variant", "value"])


@click.group()
def cli():
    pass


@cli.command("render")
@click.argument("prompt_directory", type=click.Path(exists=True, file_okay=False))
@click.argument("output_directory", type=click.Path(file_okay=False))
@click.option(
    "--template-format",
    "-t",
    default="jinja2",
    help="The format of the template files. Defaults to Jinja2.",
)
@click.option(
    "--filters",
    "-f",
    multiple=True,
    help="The filters to apply to the prompts.",
    default=[],
)
@click.option(
    "--outputs",
    "-o",
    multiple=True,
    help="The variants to be outputed. Overrides the values in the prompt config.",
    default=[],
)
@click.option(
    "--inputs",
    "-i",
    multiple=True,
    help="The arguments to leave templated. Overrides the values in the prompt config.",
    default=[],
)
def render(
    prompt_directory: str,
    output_directory: str,
    template_format: str,
    filters: List[str],
    outputs: List[str],
    inputs: List[str],
):
    filters: List[FilterTuple] = [
        FilterTuple(*_filter.split("=")) for _filter in filters
    ]

    prompt_path = Path(prompt_directory)
    output_path = Path(output_directory)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    config = Config.from_file(prompt_path)
    if len(inputs) > 0:
        config.inputs = list(inputs)
    if len(outputs) > 0:
        config.outputs = list(outputs)
    prompt_view: PromptView
    for prompt_view in get_exploded_prompt_views(prompt_path, config.inputs):
        keys = prompt_view.keys() if len(config.outputs) == 0 else config.outputs
        for output_variant_name in keys:
            # Filter to only the prompts with the desired variant values
            if all(
                [
                    prompt_view.get(_filter.variant) == _filter.value
                    for _filter in filters
                ]
            ):
                # The filename is a combination of the variant_name, and the variant that
                # went into making up that particular view
                file_name = "-".join(
                    [
                        f"{key}={prompt_view[key]}"
                        for key in prompt_view.keys()
                        if key.endswith("_name")
                    ]
                )
                # We add the output_variant_name signifies which variant is being outputed
                output_file_path = (
                    output_path / f"{output_variant_name}.{file_name}.template"
                )
                with output_file_path.open("w") as f:
                    f.write(prompt_view[output_variant_name])
