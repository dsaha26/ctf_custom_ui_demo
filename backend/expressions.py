import ast
import json
import re
from typing import Dict, List, Tuple

from jinja2 import Template


RE_EXPRESSION_TEMPL = r"(?<={{)[^{}]+(?=}})"
# {{ hello welcome {{ to the}} {{jungle }} }}

RE_PARAMETER_TEMPL = r"(?<=<<)[^<>]+(?=>>)"
# {{ hello welcome << to the>> <<jungle >> }}


def _find_expression_templates(input: str) -> List[str]:
    return re.findall(RE_EXPRESSION_TEMPL, input)


def _find_parameter_templates(input: str) -> List[str]:
    return re.findall(RE_PARAMETER_TEMPL, input)


def _pad_template(input: str) -> str:
    return f"{{{{{input}}}}}"


def _pad_parameter_template(input: str) -> str:
    return f"<<{input}>>"


def _safe_expand_dict(values: Dict, compound_key: str, path: str):
    keys = compound_key.split('.')
    values_ptr = values
    for i in range(0, len(keys)):
        if not keys[i] in values_ptr:
            values_ptr.update({keys[i]: {}})
        values_ptr = values_ptr[keys[i]]

    with open(path) as _f:
        values_ptr.update(json.load(_f))


def _render_nested_expression_templates(input: str, values: Dict, paths_map: Dict[str, str]) -> str:
    matches = _find_expression_templates(input)

    # nothing to do
    if not matches:
        return input

    for match in matches:
        for k in paths_map.keys():
            if k in match:
                _safe_expand_dict(values, k, paths_map[k])

        match = _pad_template(match)

        output = Template(match).render(values)
        assert output, f"template could not resolve: {match}"

        # final render
        if input == match:
            return output

        input = input.replace(match, output)

    return _render_nested_expression_templates(
        input,
        values,
        paths_map,
    )


def render_nested_template(input: str, values: Dict, paths_map: Dict[str, str]) -> object:
    assert type(input) is str, "template must be a str"
    if not _find_parameter_templates(input):
        input = _render_nested_expression_templates(input, values, paths_map)
        try:
            new_input = ast.literal_eval(input)
            new_input_type = type(new_input)
            if new_input_type not in [bool, int, float]:
                input = new_input
        except (SyntaxError, ValueError):
            pass
    return input


def render_parameters_in_template(input: str, values: Dict) -> Tuple[str, bool]:
    for parameter_template in _find_parameter_templates(input):
        parameter_name = parameter_template.strip()
        if parameter_name in values:
            input = input.replace(
                _pad_parameter_template(parameter_template),
                values[parameter_name],
            )
    return input, not _find_parameter_templates(input)
