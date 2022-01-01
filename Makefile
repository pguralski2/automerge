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
ifeq ($(topts),)
topts := -vv
endif
ifeq ($(dtype),)
dtype := development
endif

.DEFAULT_GOAL := help
TARGET_MAX_CHAR_NUM=20
# COLORS
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell tput -Txterm setaf 0 || exit 0)
	RED          := $(shell tput -Txterm setaf 1 || exit 0)
	GREEN        := $(shell tput -Txterm setaf 2 || exit 0)
	YELLOW       := $(shell tput -Txterm setaf 3 || exit 0)
	LIGHTPURPLE  := $(shell tput -Txterm setaf 4 || exit 0)
	PURPLE       := $(shell tput -Txterm setaf 5 || exit 0)
	BLUE         := $(shell tput -Txterm setaf 6 || exit 0)
	WHITE        := $(shell tput -Txterm setaf 7 || exit 0)
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

## show usage / common commands available
.PHONY: help
help:
	@printf "${RED}cmds:\n\n";

	@awk '{ \
			if ($$0 ~ /^.PHONY: [a-zA-Z\-\_0-9]+$$/) { \
				helpCommand = substr($$0, index($$0, ":") + 2); \
				if (helpMessage) { \
					printf "  ${PURPLE}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n\n", helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^[a-zA-Z\-\_0-9.]+:/) { \
				helpCommand = substr($$0, 0, index($$0, ":")); \
				if (helpMessage) { \
					printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
					helpMessage = ""; \
				} \
			} else if ($$0 ~ /^##/) { \
				if (helpMessage) { \
					helpMessage = helpMessage"\n                     "substr($$0, 3); \
				} else { \
					helpMessage = substr($$0, 3); \
				} \
			} else { \
				if (helpMessage) { \
					print "\n${LIGHTPURPLE}             "helpMessage"\n" \
				} \
				helpMessage = ""; \
			} \
		}' \
		$(MAKEFILE_LIST)

## -- git --

## save changes locally [git]
save-local:
	@echo "saving..."
	@git add .
	@git commit -m "${cm}"

## save changes to remote [git]
save-remote:
	@echo "saving to remote..."
	@git push origin ${branch}

## pull changes from remote
pull-remote:
	@echo "pulling from remote..."
	@git pull origin ${branch}

## create new tag, recreate if it exists
tag:
	git tag -d ${version} || : 
	git push --delete origin ${version} || : 
	git tag -a ${version} -m "latest" 
	git push origin --tags

## -- python --

## build package
pkg-build:
	@echo "building..." && python3 setup.py build

## install package
pkg-install:
	@echo "installing..." && python3 setup.py install

## install package dependencies [dtype = development | production]
deps:
	@python3 -m pip install --upgrade pip setuptools wheel
	@if [ -f requirements/${dtype}.txt ]; then pip install -r requirements/${dtype}.txt; fi

## run tests [pytest]
test:
	@echo "running tests..."
	@python3 -m pytest --durations=10 --cov-report term-missing --cov=${mn} ${tn} ${topts}

## -- code quality --

## run test profiling [pytest-profiling]
profile:
	@echo "running tests..."
	@python3 -m pytest --profile ${tn} ${topts}

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

## -- docs --

## build docs [pdoc]
docs-build:
	@echo "building docs..."
	@python3 -m pdoc ${mn} -o docs

## serve docs [pdoc]
docs-serve:
	@python3 -m pdoc ${mn}
