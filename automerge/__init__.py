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
import json
import time
import subprocess
from typing import Optional, List

import click

from automerge.utils import from_url, col_print


def _execute(cmd):
    """execute shell command

    ***

    **parameters**

    ***

    *cmd*: shell command to execute
    """
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as cmd_process:
        stdout, stderr = cmd_process.communicate()
        return cmd_process, stdout, stderr


def _repos(frepos: Optional[List[str]] = None):
    """
    get all repos in current account


    workflow:
        i) fetch GitHub repo urls using subprocess + gh
        ii) extract each url from result & store in a python list
        iii) get the owner/repo from each url (needed by `gh` for merging)
    """
    cmd = ["gh", "repo", "list", "--json", "url"]
    cmd_process, stdout, stderr = _execute(cmd)
    if cmd_process.returncode != 0 or stderr:
        return stderr
    gh_urls = json.loads(stdout.decode("ascii"))
    urls = [gh_url["url"] for gh_url in gh_urls]
    repos = [from_url(url) for url in urls]
    if frepos:
        repos = [repo for repo in repos if repo in frepos]
    return repos


def _prs(
    repo: str,
    author: str = "dependabot",
    mergeable: str = "MERGEABLE",
    state: str = "OPEN",
    stability: str = "CLEAN",
):
    """get prs for a given repo

    workflow:
        i) fetch GitHub repo PRs using subprocess + gh
        ii) extract each url from result & store in a python list

    ***

    **parameters**

    ***

    *author*: author of PR

    *mergable*: mergable status

    *state*: current PR status (open vs closed vs stale etc)

    *stability*: roudabout way of checking if builds are stable

    ***
    """
    cmd = [
        "gh",
        "pr",
        "-R",
        repo,
        "list",
        "--json",
        "number,author,state,mergeable,mergeStateStatus,url",
    ]
    cmd_process, stdout, stderr = _execute(cmd)
    if cmd_process.returncode != 0 or stderr:
        return stderr

    gh_prs = json.loads(stdout.decode("ascii"))
    prs = [
        pr
        for pr in gh_prs
        if pr["author"]["login"] == author
        and pr["mergeable"] == mergeable
        and pr["state"] == state
        and pr["mergeStateStatus"] == stability
    ]
    return prs


def _stats(frepos: Optional[List[str]] = None, author: str = "dependabot"):
    """
    fetch stats for the current GitHub account

    ***

    **parameters**

    ***

    *repos*: list of repos to get data for

    ***
    """
    data = {}
    repos = _repos()
    if frepos:
        repos = [repo for repo in repos if repo in frepos]
    (
        total_stable,
        total_unstable,
        unstable_repos,
        stable_repos,
        total_unstable_prs,
        total_stable_prs,
    ) = (0, 0, [], [], [], [])
    for repo in repos:
        repo_stats = {}
        stable_prs, unstable_prs = [pr["url"] for pr in _prs(repo, author=author)], [
            pr["url"] for pr in _prs(repo, author=author, stability="UNSTABLE")
        ]
        total_unstable_prs.extend(unstable_prs)
        total_stable_prs.extend(stable_prs)

        total_stable, total_unstable = (
            total_stable + len(stable_prs),
            total_unstable + len(unstable_prs),
        )
        if len(unstable_prs) > 0:
            unstable_repos.append(repo)
        else:
            stable_repos.append(repo)

        repo_stats["stable_prs"] = stable_prs
        repo_stats["unstable_prs"] = unstable_prs
        repo_stats["num_stable"] = len(stable_prs)
        repo_stats["num_unstable"] = len(unstable_prs)

        data[repo] = repo_stats

    data["total_stable"] = total_stable
    data["total_unstable"] = total_unstable
    data["stable_repos"] = stable_repos
    data["unstable_repos"] = unstable_repos
    data["stable_prs"] = total_stable_prs
    data["unstable_prs"] = total_unstable_prs
    print(data)
    return data


def _display(stats, verbose=True):
    """display general stats in terminal about GitHub PRs

    ***

    **parameters**

    ***

    *stats*: automerge stats

    ***
    """
    reponames = [
        key
        for key in list(stats.keys())
        if key
        not in ["total_stable", "total_unstable", "stable_repos", "unstable_repos"]
    ]
    print(f"found {len(reponames)} repos")
    if verbose:
        col_print(reponames)
    print()
    if stats["total_stable"] == 0:
        print("no PRs found for automerging!")
        print(f"unstable repos require manual effort: {len(stats['unstable_repos'])}")
        if verbose:
            col_print(stats["unstable_repos"])
        print(f"total unstable PRs: {len(stats['unstable_prs'])}")
        if verbose:
            col_print(stats["unstable_prs"])
        print()
    else:
        print("PRs found for automerging!")
        print(f"repos with PRs ready for automerging: {len(stats['stable_repos'])}")
        if verbose:
            col_print(stats["stable_repos"])
        print(f"total stable PRs: {len(stats['stable_prs'])}")
        if verbose:
            col_print(stats["stable_prs"])
        print(
            f"total unstable repos (with PRs that require manual effort): {len(stats['unstable_repos'])}"  # pylint: disable=line-too-long
        )
        if verbose:
            col_print(stats["unstable_repos"])
        print(f"total unstable PRs: {len(stats['unstable_prs'])}")
        if verbose:
            col_print(stats["unstable_prs"])
        print()


def _merge(repo: str, pr_num: int, retries: int = 0, max_retry: int = 5):
    """
    merge a GitHub PR using repo name + PR num

    ***

    **parameters**

    ***

    *repo*: GitHub repo we are trying to merge PR into

    *pr_num*: PR num to merge

    *retries*: number of times merge function has been called
                 (if > 5 merge will fail)
    ***
    """
    if retries > max_retry:
        print(f"couldn't merge {pr_num} tried {max_retry} times :(")
        return None
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "-R",
                str(repo),
                "merge",
                str(pr_num),
                "--auto",
                "--delete-branch",
                "--merge",
            ],
            capture_output=True,
            check=True,
        )
        if "not in the correct state to enable auto-merge" in result.stderr.decode(
            "ascii"
        ):
            time.sleep(30)
            _merge(repo, pr_num, retries + 1)
        if not result.stderr:
            return True
    except subprocess.CalledProcessError:
        print(f"couldn't merge {pr_num} in {repo} retrying in: 30s")
        time.sleep(30)
        _merge(repo, pr_num, retries + 1)
    return None


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
    print("fetching GitHub data...")
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
    print("fetching GitHub data...")
    # author can be passed to stats -> get prs
    if author is None:
        author = "dependabot"
    stats = _stats(repos, author=author)
    _display(stats, verbose=verbose)
    if stats["total_stable"] > 0:
        for repo in _repos():
            prs = stats[repo]["stable_prs"]
            pr_nums = [pr["number"] for pr in prs]
            if len(pr_nums) > 0:
                print(f"automerging {len(pr_nums)} PRs in {repo}")
                for pr_num in pr_nums:
                    merged = _merge(repo, pr_num)
                    if merged:
                        print(f"successfully merged {pr_num} in {repo}")
                    else:
                        print(f"error merging {pr_num} in {repo}")


if __name__ == "__main__":
    cli()
