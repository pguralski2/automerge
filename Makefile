pn := automerge
mn := automerge
tn := tests

ifeq ($(version),)
version := 0.0.1
endif
ifeq ($(cm),)
cm := default commit message
endif
ifeq ($(branch),)
branch := main
endif
ifeq ($(opts),)
opts := -vv
endif

# COLORS
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell tput -Txterm setaf 0)
	RED          := $(shell tput -Txterm setaf 1)
	GREEN        := $(shell tput -Txterm setaf 2)
	YELLOW       := $(shell tput -Txterm setaf 3)
	LIGHTPURPLE  := $(shell tput -Txterm setaf 4)
	PURPLE       := $(shell tput -Txterm setaf 5)
	BLUE         := $(shell tput -Txterm setaf 6)
	WHITE        := $(shell tput -Txterm setaf 7)
	RESET := $(shell tput -Txterm sgr0)
else
	BLACK        := ""
	RED          := ""
	GREEN        := ""
	YELLOW       := ""
	LIGHTPURPLE  := ""
	PURPLE       := ""
	BLUE         := ""
	WHITE        := ""
	RESET        := ""
endif


TARGET_MAX_CHAR_NUM=20
## show help
help:
	@echo ''
	@echo 'usage:'
	@echo '  ${BLUE}make${RESET} ${RED}<cmd>${RESET}'
	@echo ''
	@echo 'cmds:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${PURPLE}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

# SCM #
## save changes locally using git
save-local:
	@echo "saving..."
	@git add .
	@git commit -m "${cm}"

## save changes to remote using git
save-remote:
	@echo "saving to remote..."
	@git push origin ${branch}

## pull changes from remote
pull-remote:
	@echo "pulling from remote..."
	@git merge origin ${branch}

## create new tag, recreate if it exists
tag:
	git tag -d ${version} || : 
	git push --delete origin ${version} || : 
	git tag -a ${version} -m "latest" 
	git push origin --tags
#######

# DEV #
## build package
pkg-build:
	@echo "building..." && python3 setup.py build

## install package
pkg-install:
	@echo "installing..." && python3 setup.py install

## install package dependencies [dev]
deps-dev:
	@python3 -m pip install --upgrade pip setuptools wheel
	@if [ -f requirements/dev.txt ]; then pip install -r requirements/dev.txt; fi

## install package dependencies [prod]
deps-prod:
	@python3 -m pip install --upgrade pip setuptools wheel
	@if [ -f requirements/prod.txt ]; then pip install -r requirements/prod.txt; fi

## run tests [pytest]
test:
	@echo "running tests..."
	@python3 -m pytest --cov-report term-missing --cov=${mn} ${tn} ${opts}

## run test profiling [pytest-profiling]
profile:
	@echo "running tests..."
	@python3 -m pytest --profile ${tn} ${opts}

## run formatting [black]
format:
	@echo "formatting..."
	@python3 -m black ${mn}
	@python3 -m black ${tn}

## run linting [pylint]
lint:
	@echo "linting..."
	@python3 -m pylint ${mn}
	@python3 -m pylint ${tn}

## run linting & formatting
prettify: format lint

## type inference [pyre]
type-infer:
	@echo "inferring types..."
	@pyre infer

## type checking [pyre]
type-check:
	@echo "checking types..."
	@pyre

## scan for dead code [vulture]
scan-deadcode:
	@echo "checking dead code..."
	@vulture ${mn} || exit 0
	@vulture ${tn} || exit 0

## scan for security issues [bandit]
scan-security:
	@echo "checking for security issues..."
	@bandit ${mn}
#######

# DOCS #
## build docs [pdoc]
docs-build:
	@echo "building docs..."
	@python3 -m pdoc ${mn} -o docs

## serve docs [pdoc]
docs-serve:
	@python3 -m pdoc ${mn}
#######