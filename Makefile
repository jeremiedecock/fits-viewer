all: help

.PHONY : all help list publish pypi clean init

## HELP #######################################################################

# See http://stackoverflow.com/questions/4219255/how-do-you-get-the-list-of-targets-in-a-makefile

help: list

list:
	@echo "Available targets:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

## PUBLISH ####################################################################

publish: pypi

pypi:
	python3 setup.py sdist upload

## CLEAN ######################################################################

init: clean

clean:
	@echo "Remove generated files"
	@rm -rvf dist/
	@rm -rvf *.egg-info/

