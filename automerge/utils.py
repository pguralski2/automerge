"""
util functions for the automerge CLI

***

**functions**

***

*from_url*: get owner/repo from git url

*col_print*: pretty print list using columns
"""
import json
import time
import pathlib
import subprocess
from typing import Optional, List

import rich
import tabulate


def from_url(url: str):
    """helper function to get owner/repo from a git url

    ***

    **parameters**

    ***

    *url*: git repo url

    ***
    """
    return f"{pathlib.Path(url).parent.name}/{pathlib.Path(url).name}"


def chunks(lst, num_chunks):
    """split list into n-sized chunks

    ***

    **parameters**

    ***

    *lst*: list to split into chunks

    *n*: size of each chunk

    ***
    """
    split = []
    for i in range(0, len(lst), num_chunks):
        split.append(lst[i : i + num_chunks])
    return split


def col_print(data, cols=2):
    """print list of items as columns

    ***

    **parameters**

    ***

    *data*: list to pretty print

    ***
    """
    rich.print(tabulate.tabulate(chunks(data, cols)))


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
    cmd = ["gh", "repo", "list", "--json", "url", "--limit", "1000"]
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
    author: str = "app/dependabot",
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


def _stats(frepos: Optional[List[str]] = None, author: str = "app/dependabot"):
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

    if isinstance(repos, (str, bytes)):
        return repos

    if frepos:
        repos = [repo for repo in repos if repo in frepos]
    (
        total_stable,
        total_unstable,
        total_unstable_prs,
        total_stable_prs,
    ) = (0, 0, [], [])
    for repo in repos:
        repo_stats = {}
        stable_prs = [
            {"url": pr["url"], "number": pr["number"], "author": pr["author"]}
            for pr in _prs(repo, author=author)
        ]
        unstable_prs = [
            {"url": pr["url"], "number": pr["number"], "author": pr["author"]}
            for pr in _prs(repo, author=author, stability="UNSTABLE")
        ]
        total_unstable_prs.extend(unstable_prs)
        total_stable_prs.extend(stable_prs)

        total_stable, total_unstable = (
            total_stable + len(stable_prs),
            total_unstable + len(unstable_prs),
        )
        repo_stats["stable_prs"] = stable_prs
        repo_stats["unstable_prs"] = unstable_prs
        repo_stats["num_stable"] = len(stable_prs)
        repo_stats["num_unstable"] = len(unstable_prs)

        data[repo] = repo_stats

    stable_repos = [
        repo
        for repo, repo_stats in data.items()
        if (repo_stats["num_stable"] > 0 and repo_stats["num_unstable"] == 0)
    ]
    unstable_repos = [
        repo for repo, repo_stats in data.items() if repo_stats["num_unstable"] > 0
    ]
    neutral_repos = [
        repo
        for repo, repo_stats in data.items()
        if (repo_stats["num_stable"] == 0 and repo_stats["num_unstable"] == 0)
    ]
    data["total_stable"] = total_stable
    data["total_unstable"] = total_unstable
    data["stable_repos"] = stable_repos
    data["unstable_repos"] = unstable_repos
    data["neutral_repos"] = neutral_repos
    data["stable_prs"] = total_stable_prs
    data["unstable_prs"] = total_unstable_prs
    return data


def _display(stats, verbose=True):  # pylint: disable=too-many-branches
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
        not in [
            "total_stable",
            "total_unstable",
            "stable_repos",
            "unstable_repos",
            "stable_prs",
            "unstable_prs",
            "neutral_repos",
        ]
    ]
    rich.print(f"[bold green on yellow]TOTAL: {len(reponames)} repo(s)")
    if verbose:
        col_print(reponames)
    rich.print(f'[bold black on yellow]NEUTRAL: {len(stats["neutral_repos"])} repo(s)')
    if verbose:
        col_print(stats["neutral_repos"])
    rich.print()
    if stats["total_stable"] == 0:
        rich.print(
            f"[bold red on yellow]UNSTABLE REPO(s): {len(stats['unstable_repos'])}"  # pylint: disable=line-too-long
        )
        if verbose:
            if stats["unstable_repos"]:
                col_print(stats["unstable_repos"])
        rich.print(f"[bold red on yellow]UNSTABLE PR(s): {len(stats['unstable_prs'])}")
        if verbose:
            if stats["unstable_prs"]:
                col_print([pr["url"] for pr in stats["unstable_prs"]])
        rich.print()
        rich.print("[bold magenta on yellow]OUTCOME: no PRs found for automerging!\n")
    else:
        rich.print(
            f"[bold green on yellow]STABLE REPO(s): {len(stats['stable_repos'])}"
        )
        if verbose:
            col_print(stats["stable_repos"])
        rich.print(f"[bold green on yellow]STABLE PR(s): {len(stats['stable_prs'])}")
        if verbose:
            if stats["stable_prs"]:
                col_print([pr["url"] for pr in stats["stable_prs"]])
        rich.print(
            f"[bold red on yellow]UNSTABLE REPO(s): {len(stats['unstable_repos'])}"  # pylint: disable=line-too-long
        )
        if verbose:
            col_print(stats["unstable_repos"])
        rich.print(f"[bold red on yellow]UNSTABLE PR(s): {len(stats['unstable_prs'])}")
        if verbose:
            if stats["unstable_prs"]:
                col_print([pr["url"] for pr in stats["unstable_prs"]])
        rich.print()
        rich.print("[bold green on yellow]OUTCOME: PRs found for automerging!\n")


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
        rich.print(f"Couldn't merge {pr_num} tried {max_retry} times :(")
        return None
    try:
        cmd = [
            "gh",
            "pr",
            "-R",
            str(repo),
            "merge",
            str(pr_num),
            "--auto",
            "--delete-branch",
            "--merge",
        ]
        cmd_process, _, stderr = _execute(cmd)
        if cmd_process.returncode != 0 or stderr:
            return stderr

        if "not in the correct state to enable auto-merge" in stderr.decode("ascii"):
            time.sleep(30)
            _merge(repo, pr_num, retries + 1)
        if not stderr:
            return True
    except subprocess.CalledProcessError:
        time.sleep(30)
        _merge(repo, pr_num, retries + 1)
    return None
