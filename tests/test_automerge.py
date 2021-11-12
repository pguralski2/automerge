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
def test_login():
    """test automerge login command"""
    pass

def test_logout():
    """test automerge logout command"""
    pass

def test_info():
    """test automerge info command"""
    pass

def test_merge():
    """test automerge merge command"""
    pass


