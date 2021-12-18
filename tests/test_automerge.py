"""
tests for automerge, a simple python CLI that automatically
merges GitHub PRs (by default it only merges PRs that
i) pass all checks & ii) are authored by **dependabot**)

it runs on top of the official `gh` (using the subprocess
module) CLI and requires you to authenticate using `automerge login`

***

**tests**

***

*test_login*: test login command

*test_logout*: test logout command

*test_info*: test info command

*test_merge*: test merge command

***
"""
import pytest
from click.testing import CliRunner

from automerge import merge, info

MOCK_USER = "mergy"
MOCK_REPO = "reppy"
MOCK_STATS = {
    "abmamo/ferry.sh": {
        "stable_prs": [
            "https://github.com/{/ferry.sh/pull/130",
            "https://github.com/abmamo/ferry.sh/pull/129",
            "https://github.com/abmamo/ferry.sh/pull/128",
            "https://github.com/abmamo/ferry.sh/pull/127",
        ],
        "unstable_prs": [],
        "num_stable": 4,
        "num_unstable": 0,
    },
    "abmamo/mok": {
        "stable_prs": [],
        "unstable_prs": ["https://github.com/abmamo/mok/pull/65"],
        "num_stable": 0,
        "num_unstable": 1,
    },
    "abmamo/relok": {
        "stable_prs": [
            "https://github.com/abmamo/relok/pull/34",
            "https://github.com/abmamo/relok/pull/33",
            "https://github.com/abmamo/relok/pull/32",
            "https://github.com/abmamo/relok/pull/31",
        ],
        "unstable_prs": [],
        "num_stable": 4,
        "num_unstable": 0,
    },
    "abmamo/teret": {
        "stable_prs": [
            "https://github.com/abmamo/teret/pull/36",
            "https://github.com/abmamo/teret/pull/35",
            "https://github.com/abmamo/teret/pull/34",
        ],
        "unstable_prs": [],
        "num_stable": 3,
        "num_unstable": 0,
    },
    "abmamo/habits.sh": {
        "stable_prs": [
            "https://github.com/abmamo/habits.sh/pull/37",
            "https://github.com/abmamo/habits.sh/pull/36",
            "https://github.com/abmamo/habits.sh/pull/35",
        ],
        "unstable_prs": [],
        "num_stable": 3,
        "num_unstable": 0,
    },
    "abmamo/tunez": {
        "stable_prs": [
            "https://github.com/abmamo/tunez/pull/35",
            "https://github.com/abmamo/tunez/pull/34",
            "https://github.com/abmamo/tunez/pull/33",
        ],
        "unstable_prs": [],
        "num_stable": 3,
        "num_unstable": 0,
    },
    "abmamo/portfolio": {
        "stable_prs": ["https://github.com/abmamo/portfolio/pull/49"],
        "unstable_prs": [],
        "num_stable": 1,
        "num_unstable": 0,
    },
    "abmamo/automerge": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/jval": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/flask_rl": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/infra": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/thesis": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/wedding": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/fastdb": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/BlacJac": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/grub": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/populate": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/micropt": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/rcache": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "abmamo/dockerscan": {
        "stable_prs": [],
        "unstable_prs": [],
        "num_stable": 0,
        "num_unstable": 0,
    },
    "total_stable": 18,
    "total_unstable": 1,
    "stable_repos": [
        "abmamo/ferry.sh",
        "abmamo/relok",
        "abmamo/teret",
        "abmamo/habits.sh",
        "abmamo/tunez",
        "abmamo/portfolio",
        "abmamo/automerge",
        "abmamo/jval",
        "abmamo/flask_rl",
        "abmamo/infra",
        "abmamo/thesis",
        "abmamo/wedding",
        "abmamo/fastdb",
        "abmamo/BlacJac",
        "abmamo/grub",
        "abmamo/populate",
        "abmamo/micropt",
        "abmamo/rcache",
        "abmamo/dockerscan",
    ],
    "unstable_repos": ["abmamo/mok"],
    "stable_prs": [
        "https://github.com/abmamo/ferry.sh/pull/130",
        "https://github.com/abmamo/ferry.sh/pull/129",
        "https://github.com/abmamo/ferry.sh/pull/128",
        "https://github.com/abmamo/ferry.sh/pull/127",
        "https://github.com/abmamo/relok/pull/34",
        "https://github.com/abmamo/relok/pull/33",
        "https://github.com/abmamo/relok/pull/32",
        "https://github.com/abmamo/relok/pull/31",
        "https://github.com/abmamo/teret/pull/36",
        "https://github.com/abmamo/teret/pull/35",
        "https://github.com/abmamo/teret/pull/34",
        "https://github.com/abmamo/habits.sh/pull/37",
        "https://github.com/abmamo/habits.sh/pull/36",
        "https://github.com/abmamo/habits.sh/pull/35",
        "https://github.com/abmamo/tunez/pull/35",
        "https://github.com/abmamo/tunez/pull/34",
        "https://github.com/abmamo/tunez/pull/33",
        "https://github.com/abmamo/portfolio/pull/49",
    ],
    "unstable_prs": ["https://github.com/abmamo/mok/pull/65"],
}


@pytest.fixture
def mock_stats(monkeypatch):
    """mock return of the _stats function"""
    monkeypatch.setattr("src._stats", lambda x: MOCK_STATS)


@pytest.fixture
def mock_merge(monkeypatch):
    """mock return of the _merge function"""
    monkeypatch.setattr("src._merge", lambda x: True)


def test_info(mock_stats):  # pylint: disable=redefined-outer-name,unused-argument
    """test automerge login command"""
    runner = CliRunner()
    result = runner.invoke(info)
    assert result.exit_code == 0


def test_merge(mock_stats):  # pylint: disable=redefined-outer-name,unused-argument
    """test automerge merge command"""
    runner = CliRunner()
    result = runner.invoke(merge)
    assert "fetching GitHub data..." in result.stdout
