default: check

.PHONY: __init__ help test coverage annotate

prjname=$(shell grep name setup.py|awk -F"'" '{print $$2}')
prjversion=$(shell grep version setup.py|awk -F"'" '{print $$2}')
# prjname=pytok
TESTDIR=tests
PWD=$(shell pwd)
PKGPATH=$(PWD)
TESTPATH=$(PKGPATH)/$(prjname)/$(TESTDIR)
LGITPATH=/opt/odoo/tools
# Local test use z0_travis_run_tests instead travis_run_tests
x=$(echo ${HOSTNAME:0:6}|grep shs-av)
ifeq ($(x),shs-av)
	travis_ci=z0_travis_run_tests
else
	travis_ci=travis_run_tests
endif

help:
	@echo "Execucte action on project $(prjname) V$(prjversion) - use:"
	@echo "make version  # check fo version -> TODO before publish!"
	@echo "make test     # run regression tests"
	@echo "make check    # run pep8 check"
	@echo "make coverage # run coverage test"
	@echo "make travis   # simulate travis-ci action (check + coverage)"
	@echo "make replace  # copy files into git cloned dir to pubblish code"
	@echo "make publish  # exec build + upload + publish on pypi"


build:
	python setup.py build

register:
	python setup.py register

upload: build
	python setup.py sdist

publish: upload
	python setup.py build sdist upload

install: build
	sudo python setup.py install

version:
	@echo "Project $(prjname) V$(prjversion) answer:"
	PYTHONPATH=$(PKGPATH) python $(prjname)

check:
	$(travis_ci)

test:
	find . -name "$(prjname)*.log" -exec rm -f '{}' \;
	cd $(TESTPATH); PYTHONPATH=$(PKGPATH) python test_pytok.py

coverage:
	find . -name "$(prjname)*.log" -exec rm -f '{}' \;
	cd ./$(prjname)/; coverage erase
	cd ./$(prjname)/; PYTHONPATH=$(PKGPATH)  coverage run --source $(prjname) $(TESTDIR)/test_pytok.py
	cd ./$(prjname)/; coverage report

travis:	check
	cd ./$(prjname)/; coverage erase
	cd ./$(prjname)/; DEV_ENVIRONMENT=$(prjname) PYTHONPATH=$(PKGPATH) coverage run --source $(prjname) __main__.py
	cd ./$(prjname)/; coverage report

annotate:
	 cd ./$(prjname)/; PYTHONPATH=$(PKGPATH)  coverage annotate -d cover ./*

replace:
	# This command is just for internal use: it doesn't work outside Zeroincombenze(R) environment
	cd ..; dist_pkg -p $(LGITPATH) $(prjname)

