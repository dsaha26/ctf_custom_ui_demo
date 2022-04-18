import argparse
import os
from glob import glob
from pathlib import PurePath

REPO_CONFIGS = {
    "dtf": {
        "path": "dtf", # simulated github url
        "test_suites": [ "test_suites/**/test_suite_data" ],
        "test_setups": [ "test_setups/**/test_setup_data" ],
        "test_actions": [ "tests/**/test_data" ],
    },
    "tg_test_runner": {
        "path": "tg_test_runner", # simulated github url
        "test_suites": [ "test_suites/**/test_suite_data" ],
        "test_setups": [ "test_setups/**/test_setup_data" ],
        "test_actions": [ "tests/**/test_data" ],
    },
}


def _list(args):
    repo = args.repo
    level = args.level

    config = REPO_CONFIGS[repo]
    root_path = os.path.join(PurePath(__file__).parent, "repos", config["path"])
    paths = []

    for pattern in config[level]:
        search_pattern = os.path.join(root_path, pattern)
        paths += glob(search_pattern)

    # we only care about relative paths off the root of the github repo
    for i in range(len(paths)):
        paths[i] = paths[i].replace(root_path, "", 1).strip("/")

    print(paths)


def _scrape(args):
    repo = args.repo
    path = args.path

    # validate
    assert os.path.exists(os.path.join(repo, path)), f"Repo '{repo}' does not contain Path '{path}'"

    # algorithm:
    # the files are run through a JINJA preprocessor
    # this way that can inline elements from their parent levels in the folder structure

    pass


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
