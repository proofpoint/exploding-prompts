# Exploding Prompts

## Install

1. Clone the repo and cd into it. 
2. Install the cli `pip install -e .`


## Usage

```
Usage: exploding-prompts render [OPTIONS] PROMPT_DIRECTORY OUTPUT_DIRECTORY

Options:
  -t, --template-format TEXT  The format of the template files. Defaults to
                              Jinja2.
  -f, --filters TEXT          The filters to apply to the prompts.
  -o, --outputs TEXT          The variants to be outputed. Overrides the
                              values in the prompt config.
  -i, --inputs TEXT           The arguments to leave templated. Overrides the
                              values in the prompt config.
  --help                      Show this message and exit.
```