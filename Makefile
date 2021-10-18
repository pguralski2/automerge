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

save:
	@echo "saving..." && git add . && git commit -m "${COMMIT_MESSAGE}"

save-remote:
	@echo "saving to remote..." && git push origin ${BRANCH_NAME}

release:
	git tag -d ${VERSION} || : && git push --delete origin ${VERSION} || : && git tag -a ${VERSION} -m "latest" && git push origin --tags

format:
	@echo "formatting..." && python3 -m black ${MODULE_NAME}

lint:
	@echo "linting..." && python3 -m pylint ${MODULE_NAME}

prettify: format lint

docs-build:
	@echo "building docs..." && python3 -m pdoc ${MODULE_NAME} -o docs

docs-serve:
	python3 -m pdoc ${MODULE_NAME}