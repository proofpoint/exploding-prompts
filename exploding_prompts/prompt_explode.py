import re
from abc import ABC
from pathlib import Path
from typing import Dict, Generator, List, Tuple

import jinja2  # pylint: disable=import-error
import yaml

from exploding_prompts.prompt_view import PromptView


def _merge_and_explode_views(
    views_list_a: List[PromptView], views_list_b: List[PromptView]
):
    # Merge and explode the new node's views
    new_prompt_views = []
    for prompt_view_a in views_list_a:
        for prompt_view_b in views_list_b:
            new_view = prompt_view_b.clone()
            new_view.update(prompt_view_a)
            new_prompt_views.append(new_view)
    return new_prompt_views


class PromptNode(ABC):
    def __init__(self, path: Path):
        self.path = path
        self._children: List["PromptNode"] = []

    @property
    def name(self):
        return self.path.stem

    @property
    def value(self):
        return None

    @property
    def required_variables(self):
        raise NotImplementedError()

    def add_child(self, node: "PromptNode"):
        self._children.append(node)

    def root_rendered_views(
        self,
        prompt_views: List[Dict[str, str]] = None,
        prefix: str = "",
        global_prompt_view: Dict[str, str] = PromptView(),
    ) -> List[PromptView]:
        if prompt_views is None:
            prompt_views = []
        variable_nodes: List[VariableNode] = []
        template_nodes: List[TemplateNode] = []
        explode_nodes: List[ExplodeNode] = []
        for child in self._children:
            if isinstance(child, VariableNode) or isinstance(child, ConstantNode):
                variable_nodes.append(child)
            elif isinstance(child, TemplateNode):
                template_nodes.append(child)
            elif isinstance(child, ExplodeNode):
                explode_nodes.append(child)

        if len(prompt_views) == 0:
            prompt_views = [global_prompt_view.clone()]

        for explode_node in explode_nodes:
            node_explode_views = []
            for explode_variant in explode_node._children:
                variant_prefix = f"{prefix}{explode_node.name}_"
                for prompt_view in explode_variant.root_rendered_views(
                    prefix=variant_prefix, global_prompt_view=global_prompt_view
                ):
                    prompt_view[f"{variant_prefix}name"] = explode_variant.name
                    node_explode_views.append(prompt_view)
                    prompt_view.add_variant(explode_node.name, explode_variant.name)
            prompt_views = _merge_and_explode_views(prompt_views, node_explode_views)

        for variable_node in variable_nodes:
            for prompt_view in prompt_views:
                variable_name = f"{prefix}{variable_node.name}"
                if variable_name in prompt_view:
                    raise ValueError(
                        f"Duplicate variable name: '{variable_name}' in {prompt_view.keys()}"
                    )
                prompt_view[variable_name] = variable_node.value

        template_nodes = _sort_by_dependencies(template_nodes)
        for template_node in template_nodes:
            prompt_views = template_node.rendered_views(prompt_views, prefix=prefix)
        return prompt_views

    def print(self, depth: int = 0):
        print(f"{'-' * depth}{self.path.name}")
        for child in self._children:
            child.print(depth + 1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class TemplateNode(PromptNode):
    def __init__(self, path: Path):
        super().__init__(path)
        self._template = path.read_text()

    def value():
        raise NotImplementedError()

    @property
    def required_variables(self):
        jinja_variable = r"{{(.+?)}}"
        matches = re.findall(jinja_variable, self._template)
        return [match.strip() for match in matches]

    def rendered_views(
        self,
        prompt_views: List[PromptView] = None,
        prefix: str = "",
    ) -> List[PromptView]:
        if prompt_views is None:
            prompt_views = []
        env = jinja2.Environment()
        result_views = []
        for prompt_view in prompt_views:
            kwargs_keys = self.required_variables
            kwargs = {}
            for key in kwargs_keys:
                try:
                    kwargs[key] = prompt_view[key]
                except KeyError:
                    raise KeyError(f"No prompt variable '{key}' found in {prompt_view}")
            try:
                self_value = env.from_string(self._template).render(**kwargs)
            except jinja2.exceptions.UndefinedError as e:
                print("Error rendering template", self.name)
                raise e
            prompt_view[f"{prefix}{self.name}"] = self_value
            result_views.append(prompt_view)
        return result_views


class VariableNode(PromptNode):
    def __init__(self, path: Path):
        super().__init__(path)
        self._name = path.stem
        self._value = path.read_text()

    @property
    def value(self):
        return self._value


class ConstantNode(PromptNode):
    def __init__(self, path: Path, name: str, value: str):
        super().__init__(path)
        self._name = name
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name


class ExplodeNode(PromptNode):
    def __init__(self, path: Path):
        super().__init__(path)

    def rendered_views(self):
        return {}


class ExplodeVariantNode(PromptNode):
    def __init__(self, path: Path):
        super().__init__(path)

    @property
    def name(self):
        return self.path.name


def _sort_by_dependencies(template_nodes: List[TemplateNode]):
    added_node_names = []
    template_map = {node.name: node for node in template_nodes}

    node_names = {node.name for node in template_nodes}
    while len(added_node_names) < len(template_nodes):
        for template_node in [
            node for node in template_nodes if node.name not in added_node_names
        ]:
            # This is discovering the leaf nodes
            if (
                len(
                    node_names.intersection(
                        set(template_node.required_variables).difference(
                            added_node_names
                        )
                    )
                )
                == 0
            ):
                added_node_names.append(template_node.name)

    return [template_map[node_name] for node_name in added_node_names]


def _load_var_yaml(var_path: Path) -> List[ConstantNode]:
    with var_path.open("r") as f:
        var_dict: Dict[str, str] = yaml.safe_load(f)
        return [ConstantNode(var_path, key, value) for key, value in var_dict.items()]


def _build_tree_from_dir(cur_node: PromptNode, cur_path: Path, depth: int = 0):
    prompt_item: Path
    for prompt_item in cur_path.iterdir():
        if (
            depth == 0 and prompt_item.name == "root.template"
        ) or prompt_item.name == "config.yaml":
            continue
        elif prompt_item.suffix == ".template":
            cur_node.add_child(TemplateNode(prompt_item))
        elif prompt_item.name == "var.yaml":
            for var_const_node in _load_var_yaml(prompt_item):
                cur_node.add_child(var_const_node)
        elif prompt_item.suffix == ".var":
            cur_node.add_child(VariableNode(prompt_item))
        elif prompt_item.suffix == ".explode":
            explode_node = ExplodeNode(prompt_item)
            cur_node.add_child(explode_node)
            for explode_variant in prompt_item.iterdir():
                explode_node_variant = ExplodeVariantNode(explode_variant)
                explode_node_variant = _build_tree_from_dir(
                    explode_node_variant, explode_variant, depth + 1
                )
                explode_node.add_child(explode_node_variant)

    return cur_node


def _get_exploded_prompt_template(output_format: str) -> str:
    match (output_format.lower()):
        case "jinja" | "jinja2":
            return "{{{{ {} }}}}"
        case "langchain" | "lang_chain" | "lang-chain":
            return "{{{}}}"
        case _:
            return "{{{{ {} }}}}"


def get_exploded_prompt_views(
    prompt_path: Path, inputs: List[str], output_format: str = "jinja"
) -> Generator[PromptView, None, None]:
    root_prompt_path = prompt_path / "root.template"
    root_node = TemplateNode(root_prompt_path)

    root_node: TemplateNode = _build_tree_from_dir(root_node, prompt_path)

    template_format = _get_exploded_prompt_template(output_format)

    default_views = PromptView(
        {input_key: template_format.format(input_key) for input_key in inputs}
    )

    for view in root_node.rendered_views(
        root_node.root_rendered_views(global_prompt_view=default_views)
    ):
        yield view
