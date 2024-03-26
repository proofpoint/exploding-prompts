""" 
This file defines the config used to define inputs and outputs of the prompt
template rendering process.
"""

from pathlib import Path

import yaml


class Config:
    def __init__(self, inputs: list[str] = None, outputs: list[str] = None):
        self.inputs = inputs if inputs else []
        self.outputs = outputs if outputs else []

    def from_file(prompt_path: Path) -> "Config":
        config_path = prompt_path / "config.yaml"
        if config_path.exists():
            with config_path.open("r") as f:
                config = yaml.safe_load(f)
        else:
            config = {}
        inputs = config.get("inputs")
        outputs = config.get("outputs")
        return Config(inputs, outputs)
