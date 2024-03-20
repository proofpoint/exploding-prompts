"""
This module contains the command line interface for the exploding-prompts package.
"""

import click


@click.group()
def cli():
    pass


@click.command("render")
@click.argument("prompt_directory", type=click.Path(exists=True, file_okay=False))
@click.argument("output_directory", type=click.Path(file_okay=False))
def render(prompt_directory, output_directory):
    print("Hello Prompting World!")


cli.add_command(render)
