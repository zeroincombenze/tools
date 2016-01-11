# Makefile __version__=0.1.79

.DEFAULT: check

SHELL=/bin/bash
ODOO_SETUP=__openerp__.py
XX:=$(wildcard ../setup.py)
ifeq ($(XX),)
  XX:=$(wildcard ./setup.py)
endif
ifeq ($(XX),)
  XX:=$(ODOO_SETUP)
endif
SETUP:=$(abspath $(XX))
PKGPATH:=$(dir $(SETUP))
# Evaluate if running on local machine or on travis-ci environment
x:=$(shell A=$${PWD\#*/*/}; echo $${A%%/*})
ifeq ($(x),travis)
  HOSTENV=travis
else
  HOSTENV=local
  ifeq ($(DEVPATH),)
    DEVPATH:=$(shell if [ -x ./dist_pkg ]; then echo "$$PWD"; else dirname $$(which dist_pkg); fi)
  endif
  ifeq ($(DEVPATH),)
    DEVPATH:=$(shell if [ "$$PYTHONPATH" ]; then echo "$$PYTHONPATH"; elif [ -d $(HOME)/dev ]; then echo "$(HOME)/dev"; elif [ -d /opt/odoo/dev ]; then echo "/opt/odoo/dev"; else echo "/opt/openerp/dev"; fi)
  endif
endif
PRJNAME:=$(shell grep "[^a-zA-Z0-9_]name *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "\"', \r\n")
prjversion:=$(shell grep "[^a-zA-Z0-9_]version *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "\"', \r\n")
pkgids=""
devstatus:=""
ifeq ($(HOSTENV),local)
  ifeq ($(PRJNAME),odoo)
    PRJNAME:=Odoo
  endif
  ifeq ($(PRJNAME),openerp)
    PRJNAME:=Odoo
  endif
  ifneq ($(PRJNAME),Odoo)
    BASESETUP=$(notdir $(SETUP))
    ifeq ($(BASESETUP),$(ODOO_SETUP))
      PRJNAME:=Odoo
    endif
  endif
  ifeq ($(PRJNAME),Odoo)
    ifeq ($(prjversion),version)
      prjversion:=$(shell if $$(echo "$$PWD/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
    endif
    ifeq ($(prjversion),)
      prjversion:=$(shell if $$(echo "$$PWD/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
    endif
  endif
  DEVSSTS0="0"
  devstatus:=$(shell if [ -f setup.py ]; then echo ""; else echo "$(DEVSSTS0)"; fi)
  ifneq ($(PRJNAME),Odoo)
    ifeq ($(devstatus),)
      devstatus:=$(shell if [ $$(find . -executable -type f -cnewer setup.py|head -n1) ]; then echo "$(DEVSSTS0)"; fi)
    endif
    ifeq ($(devstatus),)
      devstatus:=$(shell if [ $$(find . -type f -name "*.py" -cnewer setup.py|head -n1) ]; then echo "$(DEVSSTS0)"; fi)
    endif
    ifeq ($(devstatus),)
      devstatus:=$(shell grep " *'Development Status" setup.py 2>/dev/null|awk -F":" '{print $$3}'|awk -F"-" '{print $$1}'|tr -d "\"', \r\n")
    endif
  endif
endif
ifeq ($(devstatus),)
  devstatus:=$(DEVSSTS0)
endif
ifeq ($(PRJNAME),Odoo)
  SETUP:=$(ODOO_SETUP)
  #ifeq ($(PKGPATH),)
  #  PKGPATH=$(shell pwd)
  #endif
  pkgname:=$(shell if [ -f $(SETUP) ]; then basename $$PWD; elif [ "$$(basename $$(readlink -e ../))" == "openerp" ]; then basename $$PWD; else echo ""; fi)
  PRJPATH:=$(shell if [ -f $(SETUP) ]; then cd ..; pwd; elif [ "$$(basename $$(readlink -e ../))" == "openerp" ]; then cd ..; pwd; else pwd; fi)
  BRANCH=$(shell if $$(echo "$(PRJPATH)/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
  MODVER=$(shell grep "'version' *:" $(SETUP) 2>/dev/null|awk -F":" '{print $$2}'|tr -d "\"', \r\n")
  ifneq ($(MODVER),)
     prjversion:=$(BRANCH).$(MODVER)
  endif
  pkgids=$(shell grep "'name' *:" $(SETUP) 2>/dev/null|awk -F":" '{print $$2}'|tr -d "[]\"', \r\n")
  TESTDIR=$(PKGPATH)
  TESTPATH=$(PKGPATH)
  TESTFILE=$(DEVPATH)/travis local/$(PRJNAME) test
else
  #ifeq ($(PKGPATH),)
  #  PKGPATH=$(dir $(SETUP))
  #endif
  pkgname:=$(shell basename $(PKGPATH))
  pkgids=$(shell grep "[^a-zA-Z0-9_]packages *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "[]\"', \r\n")
  PRJPATH:=$(PKGPATH)$(PRJNAME)
  BRANCH=""
  TESTDIR=tests
  TESTPATH=$(PRJPATH)/$(TESTDIR)
  TESTFILE=$(shell if [ -f $(TESTPATH)/all_tests ]; then readlink -e $(TESTPATH)/all_tests; else echo "python test_$(PRJNAME).py"; fi)
  ifeq ($(PRJNAME)",travis_emulator)
    DEVPATH=$(shell if [ -x ./dist_pkg ]; then echo "$$PWD"; else echo "$$DEVPATH"; fi)
  endif
endif
ifeq ($(HOSTENV),local)
  export LGITPATH=$(shell $(DEVPATH)/dist_pkg -W LGITPATH)
  export BRANCH
  export PKGPATH
endif
ifneq ($(pkgname),$(PRJNAME))
  @echo "Warning: package name $(pkgname) and project name $(PRJNAME) are different!"
endif

.PHONY: chkconfig
chkconfig:
	@echo "Project name   = \"$(PRJNAME)\""
	@echo "Tools path     = \"$(DEVPATH)\""
	@echo "Status         = \"$$(cd $(PKGPATH); $(DEVPATH)/dist_pkg -n -S$(devstatus) $(pkgname))\""
	@echo "Hosted         = \"$(HOSTENV)\""
	@echo "Branch         = \"$(BRANCH)\""
	@echo "Package name   = \"$(pkgname)\"($(pkgids))"
	@echo "Version        = \"$(prjversion)\""
	@echo "Setup file     = \"$(SETUP)\""
	@echo "Project path   = \"$(PRJPATH)\""
	@echo "Package path   = \"$(PKGPATH)\""
	@echo "Local git path = \"$(LGITPATH)\""
	@echo "Test file      = \"$(TESTFILE)\""

.PHONY: help
help:
	@echo "Execute action on project $(PRJNAME) V$(prjversion) [$(pkgname)]- use:"
	@echo "make version    # check for version -> TODO before publish!"
	@echo "make test       # run regression tests"
	@echo "make check      # run pep8 check"
	@echo "make coverage   # run coverage test"
	@echo "make travis     # simulate travis-ci action (check + coverage)"
	@echo "make annotate   # annotate running coverage test"
	@echo "make diff       # diff files with local git dir"
	@echo "make replace    # copy files into local git dir to pubblish code"
	@echo "make if-replace # simulate replace but it does nothing"
	@echo "make fetch      # copy files from local git dir and restore previous version"
	@echo "make if-fetch   # simulate fetch but it does nothing"
	@echo "make publish    # exec build + upload + publish (just for pypi projects)"
	@echo "make pep8       # do pep8 on all source python files"
	@echo "make push       # copy file to other directories"
	@echo "make if-push    # simulate push but it does nothing"
	@echo "make commit     # copy file to production dir/host"
	@echo "make if-commit  # simulate commit but it does nothing"
	@echo "make wep..      # wep directory"
	@echo "make docs       # write module documentation"

.PHONY: build
build:
	if [ "$(PRJNAME)" != "Odoo" ]; then \
	  cd ..; python setup.py build;\
	fi

.PHONY: register
register:
	if [ "$(PRJNAME)" != "Odoo" ]; then \
	  cd ..; python setup.py register;\
	fi

upload: build
	if [ "$(PRJNAME)" != "Odoo" ]; then \
	  cd ..; python setup.py sdist;\
	fi

.PHONY: publish 
publish: upload
	if [ "$(PRJNAME)" != "Odoo" ]; then \
	  cd ..; python setup.py build sdist upload;\
	fi

install: build
	if [ "$(PRJNAME)" != "Odoo" ]; then \
	  cd ..; python setup.py install;\
	fi

.PHONY: version
version:
	@# Follow line is just for internal use: it couldn't work outside Zeroincombenze(R) environment
	@cd $(PKGPATH); $(DEVPATH)/dist_pkg -- $(pkgname) $(PRJNAME);
	@if [ "$(PRJNAME)" != "Odoo" ]; then \
	  echo "Project $(PRJNAME) V$(prjversion) [$(pkgname)] answer:"; \
	  cd $(PKGPATH); PYTHONPATH=$(PKGPATH) python $(PRJNAME); \
	else \
	  echo "Project $(PRJNAME) V$(BRANCH) [$(pkgname) $(prjversion)]"; \
	fi;

.PHONY: check
check:
	@$(DEVPATH)/travis local/$(PRJNAME) check;

.PHONY: test
test:
	@find $(PKGPATH) -name "*$(PRJNAME)*.log" -exec rm -f '{}' \;
	@if [ "$(PRJNAME)" != "Odoo" ]; then \
	  cd $(TESTPATH); PYTHONPATH=$(PKGPATH) $(TESTFILE); \
	else \
	  $(DEVPATH)/travis local/$(PRJNAME) test; \
	fi

.PHONY: coverage
coverage:
	find $(PKGPATH) -name "*$(PRJNAME)*.log" -exec rm -f '{}' \;
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); DEV_ENVIRONMENT=$(PRJNAME) PYTHONPATH=$(PKGPATH) coverage run --source $(PRJNAME) __main__.py
	# cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage run --source $(PRJNAME) $(TESTDIR)/test_$(PRJNAME).py
	cd $(PRJPATH); coverage report

.PHONY: travis
travis:
	if [ "$(HOSTENV)" == "travis" ]; then \
	  travis_run_tests; \
	elif [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  $(DEVPATH)/travis local/$(PRJNAME); \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -S3 $(pkgname); \
	else \
	  $(DEVPATH)/travis local/$(PRJNAME); \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -S3 $(pkgname); \
	fi

.PHONY: annotate
annotate:
	 cd $(PRJPATH); PYTHONPATH=$(PKGPATH) coverage annotate -d cover ./*.py

.PHONY: pep8
pep8:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@find $(PKGPATH) -name "*.py" -exec $(DEVPATH)/topep8 '{}' \;
	@find $(PKGPATH) -name "*.xml" -exec $(DEVPATH)/beauty '{}' \;

.PHONY: replace
replace:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then\
	   cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -vR $(pkgname);\
	else\
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -vR $(pkgname);\
	fi

.PHONY: if-replace
if-replace:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then\
	   cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -nvR $(pkgname);\
	else\
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -nvR $(pkgname);\
	fi

.PHONY: fetch
fetch:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then\
	   cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -vF $(pkgname);\
	else\
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -vF $(pkgname);\
	fi

.PHONY: if-fetch
if-fetch:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then\
	   cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -nvF $(pkgname);\
	else\
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -nvF $(pkgname);\
	fi

.PHONY: diff
diff:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -vd $(pkgname); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -vd $(pkgname); \
	fi

.PHONY: push
push:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -vP $(pkgname) $(PRJNAME); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -vP $(pkgname) $(PRJNAME); \
	fi

.PHONY: if-push
if-push:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -nvP $(pkgname) $(PRJNAME); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -nvP $(pkgname) $(PRJNAME); \
	fi

.PHONY: commit
commit:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -vC $(pkgname) $(PRJNAME); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -vC $(pkgname) $(PRJNAME); \
	fi

.PHONY: if-commit
if-commit:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -nvC $(pkgname) $(PRJNAME); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -nvC $(pkgname) $(PRJNAME); \
	fi

.PHONY: wep
wep:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(PRJNAME)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(PRJNAME)/dist_pkg -w $(pkgname) $(PRJNAME); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -w $(pkgname) $(PRJNAME); \
	fi

.PHONY: docs
docs:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	cd $(PRJPATH); PYTHONPATH=$(PKGPATH) $(DEVPATH)/wok_doc -v $(pkgname)
	# cd $(PRJPATH); PYTHONPATH=$(PKGPATH) ./wok_doc -v $(pkgname)
