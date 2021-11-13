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
	@echo "saving..." && git add . && git commit -m "${cm}"

save-remote:
	@echo "saving to remote..." && git push origin ${branch}

release:
	git tag -d ${version} || : && git push --delete origin ${version} || : && git tag -a ${version} -m "latest" && git push origin --tags

test:
	@echo "running tests..." && python3 -m pytest --cov-report term-missing --cov=${mn} ${tn} ${opts}

format:
	@echo "formatting..." && python3 -m black ${mn} && python3 -m black ${tn}

lint:
	@echo "linting..." && python3 -m pylint ${mn} && python3 -m pylint ${tn}

prettify: format lint

docs-build:
	@echo "building docs..." && python3 -m pdoc ${mn} -o docs

docs-serve:
	python3 -m pdoc ${mn}