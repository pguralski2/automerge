PACKAGE_NAME := automerge
MODULE_NAME := automerge.py
MODULE_TEST_NAME := tests
PYTEST_OPTS := -vv

ifeq ($(VERSION),)
VERSION := 0.0.1
endif
ifeq ($(COMMIT_MESSAGE),)
COMMIT_MESSAGE := default commit message
endif
ifeq ($(BRANCH_NAME),)
BRANCH_NAME := main
endif


help:
	@echo "list of available commands"
	@echo
	@echo "save               	- save changes locally using git"
	@echo "save-remote          	- save changes to remote using git"
	@echo "release          	- release current version (just tags master with current version & pushes to master)"
	@echo "test           		- run tests using pytest"
	@echo "format             	- format code using black"
	@echo "lint           		- lint code using pylint"
	@echo "prettify             	- run linting + formatting"
	@echo "docs-build       	- build docs using pdoc"
	@echo "docs-serve       	- serve docs using pdoc"

save:
	@echo "saving..." && git add . && git commit -m "${COMMIT_MESSAGE}"

save-remote:
	@echo "saving to remote..." && git push origin ${BRANCH_NAME}

release:
	git tag -d ${VERSION} || : && git push --delete origin ${VERSION} || : && git tag -a ${VERSION} -m "latest" && git push origin --tags

test:
	@echo "running tests..." && python3 -m pytest --cov-report term-missing --cov=${MODULE_NAME} ${MODULE_TEST_NAME} ${PYTEST_OPTS}

format:
	@echo "formatting..." && python3 -m black ${MODULE_NAME} && python3 -m black ${MODULE_TEST_NAME}

lint:
	@echo "linting..." && python3 -m pylint ${MODULE_NAME} && python3 -m pylint ${MODULE_TEST_NAME}

prettify: format lint

docs-build:
	@echo "building docs..." && python3 -m pdoc ${MODULE_NAME} -o docs

docs-serve:
	python3 -m pdoc ${MODULE_NAME}