FROM python:latest

# Add src
ADD automerge /root/automerge/automerge
ADD requirements /root/automerge/requirements
ADD README.md /root/automerge/README.md 
ADD setup.py /root/automerge/

# Init gh
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/etc/apt/trusted.gpg.d/githubcli-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/trusted.gpg.d/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
RUN apt update
RUN apt install gh

# Install
RUN pip install -e /root/automerge

# Authentication
RUN gh auth login

# Run on startup
ENTRYPOINT [ "automerge" ]