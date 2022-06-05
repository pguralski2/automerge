"""
automerge is a simple python CLI that automatically
merges GitHub PRs (by default it only merges PRs that
i) pass all checks & ii) are authored by **dependabot**)

it runs on top of the official `gh` CLI and requires you to
authenticate using `automerge login`

***

**commands**

***

*login*: log in to GitHub account

*logout*: log out of current GitHub account

*info*: get info abount PRs in current account

*merge*: merge all valid PRs in current account

***

**util. functions**

***

*from_url*: get owner/repo from git url

*_repos*: get all repos in current account

*_prs*: get prs for a given repo

*_stats*: get stats for current account

*_display*: display info abount current account

*_merge*: take the name of a repo + a PR num & merge if stable

***
"""
import time
import subprocess

import click
import rich
from rich.console import Console
from rich.style import Style

from automerge.utils import _stats, _display, _repos, _merge

console = Console()


@click.group()
def cli():
    """
    automerge is a simple python CLI that automatically
    merges GitHub PRs
    """


@cli.command()
def login():
    """login to GitHub"""
    subprocess.run(["gh", "auth", "login"], check=True)


@cli.command()
def logout():
    """logout of GitHub"""
    subprocess.run(["gh", "auth", "logout"], check=True)


@cli.command()
@click.option("--repos", "-r", multiple=True)
@click.option(
    "--verbose", "-v", is_flag=True, help="display more detailed information."
)
def info(repos, verbose):
    """merge all stable/unstable PRs"""
    base_style = Style.parse("magenta on yellow")
    console.print(
        "automerge: fetching GitHub data using gh\n",
        style=base_style + Style(underline=True, bold=True),
    )
    stats = _stats(repos)
    _display(stats, verbose=verbose)


@cli.command()
@click.option("--repos", "-r", multiple=True)
@click.option("--author", "-a")
@click.option(
    "--verbose", "-v", is_flag=True, help="display more detailed information."
)
def merge(repos, verbose, author=None):
    """merge all[stable] PRs"""
    base_style = Style.parse("magenta on yellow")
    merge_style = Style.parse("green on yellow")
    error_style = Style.parse("yellow on red")
    console.print(
        "automerge: fetching GitHub data using gh\n",
        style=base_style + Style(underline=True, bold=True),
    )
    # author can be passed to stats -> get prs
    if author is None:
        author = "dependabot"
    stats = _stats(repos, author=author)
    _display(stats, verbose=verbose)
    while len(stats["stable_prs"]) > 0:
        for repo in _repos():
            prs = stats[repo]["stable_prs"]
            if verbose:
                if not prs:
                    console.print(
                        f"automerge: no PRs found in {repo}\n",
                        style=merge_style + Style(underline=True, bold=True),
                    )
                    continue
            pr_nums = [pr["number"] for pr in prs]
            if len(pr_nums) > 0:
                rich.print(f"automerging {len(pr_nums)} PR(s) in {repo}")
                for pr_num in pr_nums:
                    merged = _merge(repo, pr_num)
                    if merged:
                        console.print(
                            f"automerge: successfully merged {pr_num} in {repo}\n",
                            style=merge_style + Style(underline=True, bold=True),
                        )
                    else:
                        console.print(
                            f"automerge: error merging {pr_num} in {repo}\n",
                            style=error_style + Style(underline=True, bold=True),
                        )
        time.sleep(60)
        stats = _stats(repos, author=author)


if __name__ == "__main__":
    cli()
