# Makefile 0.1.44

.DEFAULT: check

ODOO_SETUP=__openerp__.py
# Evaluate if running on local machine or on travis-ci environment
x=$(shell A=$${PWD\#*/*/}; echo $${A%%/*})
ifeq ($(x),travis)
  HOSTENV=travis
else
  HOSTENV=local
  DEVPATH=$(shell if [ "$$PYTHONPATH" ]; then echo "$$PYTHONPATH"; elif [ -d $(HOME)/dev ]; then echo "$(HOME)/dev"; else echo "/opt/openerp/dev"; fi)
endif
SETUP=$(shell if [ -f ../setup.py ]; then echo "../setup.py"; elif [ -f setup.py ]; then echo "setup.py"; else echo $(ODOO_SETUP); fi)
prjname=$(shell grep "[^a-zA-Z0-9_]name *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "\"', \n")
prjversion=$(shell grep "[^a-zA-Z0-9_]version *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "\"', \n")
ifeq ($(HOSTENV),local)
  ifeq ($(prjname),odoo)
    prjname=Odoo
  endif
  ifeq ($(prjname),openerp)
    prjname=Odoo
  endif
  ifneq ($(prjname),Odoo)
    ifeq ($(SETUP),$(ODOO_SETUP))
      prjname=Odoo
    endif
  endif
  ifeq ($(prjname),Odoo)
    ifeq ($(prjversion),version)
      prjversion=$(shell if $$(echo "$$PWD/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
    endif
    ifeq ($(prjversion),)
      prjversion=$(shell if $$(echo "$$PWD/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
    endif
  endif
endif
ifeq ($(prjname),Odoo)
  SETUP=$(ODOO_SETUP)
  PKGPATH=$(shell pwd)
  pkgname=$(shell if [ -f $(SETUP) ]; then basename $$PWD; else echo ""; fi)
  PRJPATH=$(shell if [ -f $(SETUP) ]; then cd ..; pwd; else pwd; fi)
  LGITPATH=$(shell echo $(PRJPATH)|sed s:/openerp/:/odoo/:)
  BRANCH=$(shell if $$(echo "$(PRJPATH)/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
  MODVER=$(shell grep "'version' *:" $(SETUP) 2>/dev/null|awk -F":" '{print $$2}'|tr -d "\"', \n")
  ifneq ($(MODVER),)
     prjversion=$(BRANCH).$(MODVER)
  endif
  TESTDIR=$(PKGPATH)
  TESTPATH=$(PKGPATH)
  TESTFILE=$(DEVPATH)/travis local/$(prjname) test
else
  ifeq ($(SETUP),setup.py)
    PKGPATH=$(shell pwd)
    PRJPATH=$(PWD)/$(prjname)
  else
    PKGPATH=$(shell cd ..; pwd)
  endif
  pkgname=$(shell basename $$PWD)
  PRJPATH=$(PKGPATH)/$(prjname)
  LGITPATH=/opt/odoo/tools
  BRANCH=""
  TESTDIR=tests
  TESTPATH=$(PRJPATH)/$(TESTDIR)
  TESTFILE=$(shell if [ -f $(TESTPATH)/all_tests ]; then echo "all_tests"; else echo "python test_$(prjname).py"; fi)
endif
ifeq ($(HOSTENV),local)
  export BRANCH
  export PKGPATH
endif
ifneq ($(pkgname),$(prjname))
  @echo "Warning: package name $(pkgname) and project name $((prjname) are different!"
endif

.PHONY: chkconfig
chkconfig:
	@echo "Project name   = \"$(prjname)\""
	@echo "Hosted         = \"$(HOSTENV)\""
	@echo "Branch         = \"$(BRANCH)\""
	@echo "Package name   = \"$(pkgname)\""
	@echo "Version        = \"$(prjversion)\""
	@echo "Setup file     = \"$(SETUP)\""
	@echo "Project path   = \"$(PRJPATH)\""
	@echo "Package path   = \"$(PKGPATH)\""
	@echo "Test file      = \"$(TESTFILE)\""
	@echo "Local git path = \"$(LGITPATH)\""

.PHONY: help
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

.PHONY: build
build:
	if [ "$(prjname)" != "Odoo" ]; then \
	  cd ..; python setup.py build;\
	fi

.PHONY: register
register:
	if [ "$(prjname)" != "Odoo" ]; then \
	  cd ..; python setup.py register;\
	fi

upload: build
	if [ "$(prjname)" != "Odoo" ]; then \
	  cd ..; python setup.py sdist;\
	fi

.PHONY: publish 
publish: upload
	if [ "$(prjname)" != "Odoo" ]; then \
	  cd ..; python setup.py build sdist upload;\
	fi

install: build
	if [ "$(prjname)" != "Odoo" ]; then \
	  cd ..; python setup.py install;\
	fi

.PHONY: version
version:
	@# Follow line is just for internal use: it couldn't work outside Zeroincombenze(R) environment
	cd $(PKGPATH); $(DEVPATH)/dist_pkg -- $(pkgname) $(prjname);
	@if [ "$(prjname)" != "Odoo" ]; then \
	  echo "Project $(prjname) V$(prjversion) [$(pkgname)] answer:"; \
	  cd $(PKGPATH); PYTHONPATH=$(PKGPATH) python $(prjname); \
	else \
	  echo "Project $(prjname) V$(BRANCH) [$(pkgname) $(prjversion)]"; \
	fi;

.PHONY: check
check:
	$(DEVPATH)/travis local/$(prjname) check

.PHONY: test
test:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	if [ "$(prjname)" != "Odoo" ]; then \
	  cd $(TESTPATH); PYTHONPATH=$(PKGPATH) $(TESTFILE);\
	else\
	  $(DEVPATH)/travis local/$(prjname) test;\
	fi

.PHONY: coverage
coverage:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage run --source $(prjname) $(TESTDIR)/test_$(prjname).py
	cd $(PRJPATH); coverage report

.PHONY: travis
travis:
	$(DEVPATH)/travis local/$(prjname)

.PHONY: annotate
annotate:
	 cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage annotate -d cover ./*

.PHONY: pep8
pep8:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@find $(PKGPATH) -name "*.py" -exec $(DEVPATH)/topep8 '{}' \;
	@find $(PKGPATH) -name "*.xml" -exec $(DEVPATH)/beauty '{}' \;

.PHONY: replace
replace:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	cd $(PKGPATH); $(DEVPATH)/dist_pkg -p $(LGITPATH) $(pkgname)
