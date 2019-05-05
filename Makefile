.PHONY: install docs update-requirements bump

install:
	poetry install

docs:
	poetry run sphinx-build -M html ".\docs" ".\docs\_build"

# Requirements.txt needed to build docs on readthedocs.io
update-requirements:
	poetery update
	poetry run pip freeze --exclude-editable > ./docs/requirements.txt

bump:
	poetry version
	@echo "Remember to increase version in py_wave_runup/__init__.py"
	@echo "and in docs/conf.py"


###############################
# Help command

.DEFAULT_GOAL := help
.PHONY: help

# Refer to https://gist.github.com/prwhite/8168133

#COLORS
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
# A category can be added with @category
HELP_FUN = \
	%help; \
	while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
	print "usage: make [target]\n\n"; \
	for (sort keys %help) { \
	print "${WHITE}$$_:${RESET}\n"; \
	for (@{$$help{$$_}}) { \
	$$sep = " " x (32 - length $$_->[0]); \
	print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
	}; \
	print "\n"; }

help: ##@other Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)
