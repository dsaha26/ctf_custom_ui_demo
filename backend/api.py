import argparse
import json
from glob import glob
from pathlib import Path, PurePath

from expressions import render_nested_template
from typing import List

CONFIG_FILE_ENDING = "json"
CONFIG_SCHEMA_FILE_ENDING = "schema.json"

REPO_CONFIGS = {
    "dtf": {
        "path": "dtf",  # simulated github url
        "test_suites": ["test_suites"],
        "test_setups": ["test_setups"],
        "test_actions": ["tests"],
    },
    "tg_test_runner": {
        "path": "tg_test_runner",  # simulated github url
        "test_suites": ["test_suites/**/test_suite_data"],
        "test_setups": ["test_setups/**/test_setup_data"],
        "test_actions": ["tests/**/test_data"],
    },
}


def _get_root_path(path: str) -> PurePath:
    return PurePath(PurePath(__file__).parent).joinpath("repos", path)


def _glob_for_config_files(root_path: PurePath, pattern: str):
    glob_paths = glob(
        str(root_path.joinpath(pattern.strip("/*"), "**", f"*.{CONFIG_FILE_ENDING}")),
        recursive=True,
    )

    paths = []
    schema_paths = []

    # we only care about relative paths off the root of the github repo
    for i in range(len(glob_paths)):
        glob_paths[i] = glob_paths[i].replace(str(root_path), "", 1).strip("/")
        if (
            glob_paths[i].endswith(f".{CONFIG_SCHEMA_FILE_ENDING}")
            or glob_paths[i] == CONFIG_SCHEMA_FILE_ENDING
        ):
            schema_paths.append(glob_paths[i])
        else:
            paths.append(glob_paths[i])

    return paths, schema_paths


def _list(args):
    repo = args.repo
    level = args.level

    repo_config = REPO_CONFIGS[repo]
    repo_root_path = _get_root_path(repo_config["path"])

    paths = []
    for pattern in repo_config[level]:
        _paths, _ = _glob_for_config_files(repo_root_path, pattern)
        paths += _paths

    # only interested in config files
    print(paths)


def _render_tree(_obj, values, paths_map):
    if type(_obj) is dict:
        for k, v in _obj.items():
            _obj[k] = _render_tree(v, values, paths_map)
    elif type(_obj) is list:
        for i in range(0, len(_obj)):
            _obj[i] = _render_tree(_obj[i], values, paths_map)
    elif type(_obj) is str:
        _new_obj = render_nested_template(_obj, values, paths_map)
        if _obj != _new_obj:
            _obj = _render_tree(_new_obj, values, paths_map)
    return _obj


def _create_values_map(file_ending: str, repo_root_path: PurePath, paths_to_map: List[str]):
    full_paths_map = {}
    for p in paths_to_map:
        full_paths_map.update({
            p.replace('/', '.').replace(file_ending, '').rstrip('.'): repo_root_path.joinpath(p)
        })
    return full_paths_map


def _scrape(args):
    repo = args.repo
    path = PurePath(args.path)
    path_str = str(path)

    repo_config = REPO_CONFIGS[repo]
    repo_root_path = _get_root_path(repo_config["path"])

    full_path = repo_root_path.joinpath(path)
    full_path_str = str(full_path)

    # validate path exists
    assert Path(full_path_str).exists(), f"Repo '{repo}' does not contain Path '{path_str}'"
    assert not full_path_str.endswith("schema.json"), f"Path '{path_str}' should NOT end in 'schema.json'"
    assert full_path_str.endswith(".json"), f"Path '{path_str}' should end in '.json'"

    # scrape everything possible to be inlined
    paths, schema_paths = _glob_for_config_files(repo_root_path, "")

    # apply nested inlining
    # NOTE: this is also how CTF implements "foreach" loops at runtime
    with open(str(full_path)) as _f:
        config = json.load(_f)
    expanded_config = _render_tree(
        config,
        {},
        _create_values_map(CONFIG_FILE_ENDING, repo_root_path, paths)
    )

    # find schema file, but only up to the parent directory level
    # this is in specific order of priority
    possible_schema_paths = [
        str(path.with_suffix(f".{CONFIG_SCHEMA_FILE_ENDING}")),
        str(path.parent.joinpath(CONFIG_SCHEMA_FILE_ENDING)),
        str(path.parent.with_suffix(f".{CONFIG_SCHEMA_FILE_ENDING}")),
        str(path.parents[1].joinpath(CONFIG_SCHEMA_FILE_ENDING)),
    ]

    schema_path = None
    for p in possible_schema_paths:
        if p in schema_paths:
            schema_path = p

    # if there is no schema, that is also ok
    # it just means that CTF UI will show everything readOnly
    if schema_path:
        full_schema_path = repo_root_path.joinpath(schema_path)

        with open(str(full_schema_path)) as _f:
            schema = json.load(_f)

        expanded_schema = _render_tree(
            schema,
            {},
            _create_values_map(CONFIG_SCHEMA_FILE_ENDING, repo_root_path, schema_paths)
        )
    else:
        expanded_schema = {}

    # return combined config and schema
    print(json.dumps({
        "config": expanded_config,
        "schema": expanded_schema,
    }))


parser = argparse.ArgumentParser("Scrapes some CTF Test Harness example repos.")
parser.add_argument("repo", choices=["dtf", "tg_test_runner"])

subparsers = parser.add_subparsers()

list_parser = subparsers.add_parser("list")
list_parser.add_argument(
    "level",
    help="Level to operate.",
    choices=["test_suites", "test_setups", "test_actions"],
)
list_parser.set_defaults(func=_list)

scrape_parser = subparsers.add_parser("scrape")
scrape_parser.add_argument("path", help="Path to scrape.. (Choose from 'list')")
scrape_parser.set_defaults(func=_scrape)

args = parser.parse_args()
args.func(args)
