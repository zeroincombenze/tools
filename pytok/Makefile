# Makefile 0.1.10
default: check

.PHONY: help test coverage annotate

# Evaluate if running on local machine or on travis-ci environment
x=$(shell echo $${HOSTNAME:0:6}|grep shs-av)
ifeq ($(x),shs-av)
	travis_ci=z0_travis_run_tests
 	LGITPATH=/opt/odoo/tools
	SETUP=../setup.py
else
 	travis_ci=travis_run_tests
	SETUP=setup.py
endif
PKGPATH=$(shell cd ..; pwd)
pkgname=$(shell basename $$PWD)
prjname=$(shell grep name $(SETUP)|awk -F"'" '{print $$2}')
ifneq ($(pkgname),$(prjname))
	@echo "Warning: package name $(pkgname) and project name $((prjname) are different!"
endif
prjversion=$(shell grep version $(SETUP)|awk -F"'" '{print $$2}')
PKGPATH=$(shell cd ..; pwd)
PRJPATH=$(PKGPATH)/$(prjname)
TESTDIR=tests
TESTPATH=$(PRJPATH)/$(TESTDIR)


help:
	@echo "Execute action on project $(prjname) V$(prjversion) [$(pkgname)]- use:"
	@echo "make version  # check for version -> TODO before publish!"
	@echo "make test     # run regression tests"
	@echo "make check    # run pep8 check"
	@echo "make coverage # run coverage test"
	@echo "make travis   # simulate travis-ci action (check + coverage)"
	@echo "make replace  # copy files into git cloned dir to pubblish code"
	@echo "make publish  # exec build + upload + publish on pypi"


build:
	cd ..; python setup.py build

register:
	cd ..; python setup.py register

upload: build
	cd ..; python setup.py sdist

publish: upload
	cd ..; python setup.py build sdist upload

install: build
	cd ..; python setup.py install

version:
	@# Follow line is just for internal use: it couldn't work outside Zeroincombenze(R) environment
	@cd $(PKGPATH)/..; dist_pkg -- $(prjname)
	@echo "Project $(prjname) V$(prjversion) [$(pkgname)] answer:"
	@cd $(PKGPATH); PYTHONPATH=$(PKGPATH) python $(prjname)

check:
	$(travis_ci)

test:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	cd $(TESTPATH); PYTHONPATH=$(PKGPATH) python test_pytok.py

coverage:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage run --source $(prjname) $(TESTDIR)/test_pytok.py
	cd $(PRJPATH); coverage report

travis:	check
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); DEV_ENVIRONMENT=$(prjname) PYTHONPATH=$(PKGPATH) coverage run --source $(prjname) __main__.py
	cd $(PRJPATH); coverage report

annotate:
	 cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage annotate -d cover ./*

replace:
	# This command is just for internal use: it doesn't work outside Zeroincombenze(R) environment
	cd $(PKGPATH)/..; dist_pkg -p $(LGITPATH) $(prjname)

