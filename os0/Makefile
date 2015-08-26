# Makefile 0.1.12
default: check

.PHONY: help test coverage annotate pep8 version

# Evaluate if running on local machine or on travis-ci environment
x=$(shell echo $${HOSTNAME:0:6}|grep shs-av)
ifeq ($(x),shs-av)
	travis_ci=z0_travis_run_tests
	LGITPATH=/opt/odoo/tools
    DEVPATH=$(shell if [ -d ~/dev ]; then echo "~/dev"; else echo "/opt/openerp/dev"; fi)
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
TESTFILE=$(shell if [ -f $(TESTPATH)/all_tests ]; then echo "all_tests"; else echo "python test_$(prjname).py"; fi)


help:
	@echo "Execute action on project $(prjname) V$(prjversion) [$(pkgname)]- use:"
	@echo "make version  # check for version -> TODO before publish!"
	@echo "make test     # run regression tests"
	@echo "make check    # run pep8 check"
	@echo "make coverage # run coverage test"
	@echo "make travis   # simulate travis-ci action (check + coverage)"
	@echo "make replace  # copy files into git cloned dir to pubblish code"
	@echo "make publish  # exec build + upload + publish on pypi"
	@echo "make pep8     # do pep8 on all source python files"


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
	@cd $(PKGPATH)/..; $(DEVPATH)/dist_pkg -- $(prjname)
	@echo "Project $(prjname) V$(prjversion) [$(pkgname)] answer:"
	@cd $(PKGPATH); PYTHONPATH=$(PKGPATH) python $(prjname)

check:
	$(travis_ci)

test:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	cd $(TESTPATH); PYTHONPATH=$(PKGPATH) $(TESTFILE)

coverage:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage run --source $(prjname) $(TESTDIR)/test_$(prjname).py
	cd $(PRJPATH); coverage report

travis:	check
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); DEV_ENVIRONMENT=$(prjname) PYTHONPATH=$(PKGPATH) coverage run --source $(prjname) __main__.py
	cd $(PRJPATH); coverage report

annotate:
	 cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage annotate -d cover ./*

pep8:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@find $(PKGPATH) -name "*.py" -exec $(DEVPATH)/topep8 '{}' \;

replace:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	cd $(PKGPATH)/..; $(DEVPATH)/dist_pkg -p $(LGITPATH) $(prjname)

