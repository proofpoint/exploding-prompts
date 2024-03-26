from typing import Dict


class PromptView:
    """A class to represent a prompt view. This contains the the rendered templates, and all variants used to
    render the template. The variables and variants can be accessed directly on this object by interacting with
    it like a dictionary. For example, to get the value of the rendered template named "root", you can do `prompt_view["root"]`.
    Likewise to get the model_name that was used to render the prompt-view, you can access it via `prompt_view["model_name"]`.
    """

    def __init__(self, variables: Dict[str, str] = None):
        """Initialize the prompt view.

        **args**:
            :variables (Dict[str, str]): The variables to use.
        """
        if variables is None:
            variables = {}
        self._variables = variables
        self._variants: Dict[str, str] = {}

    @property
    def variants(self):
        return self._variants

    @property
    def root(self):
        return self._variables.get("root", "")

    def add_variant(self, variant_type, variant_value):
        self._variants[variant_type] = variant_value

    def add_variable(self, name: str, value: str):
        self._variables[name] = value

    def keys(self):
        return self._variables.keys()

    def update(self, other: "PromptView"):
        self._variants.update(other._variants)
        self._variables.update(other._variables)

    def clone(self):
        new_view = PromptView(self._variables.copy())
        new_view._variants = self._variants.copy()
        return new_view

    def get(self, name: str) -> str:
        return self._variables.get(name)

    def __getitem__(self, name: str) -> str:
        return self._variables.get(name)

    def __setitem__(self, name: str, value: str):
        self._variables[name] = value

    def __contains__(self, name: str) -> bool:
        return name in self._variables

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"PromptView({str(self._variants)}, {(self._variables)})"
