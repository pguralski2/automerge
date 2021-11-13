"""
util functions for the automerge CLI

***

**functions**

***

*from_url*: get owner/repo from git url

*col_print*: pretty print list using columns
"""
import pathlib
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


def col_print(data, cols=3):
    """print list of items as columns

    ***

    **parameters**

    ***

    *data*: list to pretty print

    ***
    """
    print(tabulate.tabulate(chunks(data, cols)))
