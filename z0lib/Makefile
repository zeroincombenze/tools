# Makefile 0.1.56

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
prjname=$(shell grep "[^a-zA-Z0-9_]name *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "\"', \r\n")
prjversion=$(shell grep "[^a-zA-Z0-9_]version *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "\"', \r\n")
pkgids=""
devstatus=""
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
  DEVSSTS0="0"
  devstatus=$(shell if [ -f setup.py ]; then echo ""; else echo "$(DEVSSTS0)"; fi)
  ifneq ($(prjname),Odoo)
    ifeq ($(devstatus),)
      devstatus=$(shell if [ $$(find . -executable -type f -cnewer setup.py|head -n1) ]; then echo "$(DEVSSTS0)"; fi)
    endif
    ifeq ($(devstatus),)
      devstatus=$(shell if [ $$(find . -type f -name "*.py" -cnewer setup.py|head -n1) ]; then echo "$(DEVSSTS0)"; fi)
    endif
    ifeq ($(devstatus),)
      devstatus=$(shell grep " *'Development Status" setup.py 2>/dev/null|awk -F":" '{print $$3}'|awk -F"-" '{print $$1}'|tr -d "\"', \r\n")
    endif
  endif
endif
ifeq ($(devstatus),)
  devstatus=$(DEVSSTS0)
endif
ifeq ($(prjname),Odoo)
  SETUP=$(ODOO_SETUP)
  PKGPATH=$(shell pwd)
  pkgname=$(shell if [ -f $(SETUP) ]; then basename $$PWD; else echo ""; fi)
  PRJPATH=$(shell if [ -f $(SETUP) ]; then cd ..; pwd; else pwd; fi)
  LGITPATH=$(shell echo $(PRJPATH)|sed s:/openerp/:/odoo/:)
  BRANCH=$(shell if $$(echo "$(PRJPATH)/"|grep "/v8/\|8.0/">/dev/null); then echo "8.0"; else echo "7.0"; fi)
  MODVER=$(shell grep "'version' *:" $(SETUP) 2>/dev/null|awk -F":" '{print $$2}'|tr -d "\"', \r\n")
  ifneq ($(MODVER),)
     prjversion=$(BRANCH).$(MODVER)
  endif
  pkgids=$(shell grep "'name' *:" $(SETUP) 2>/dev/null|awk -F":" '{print $$2}'|tr -d "[]\"', \r\n")
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
  pkgids=$(shell grep "[^a-zA-Z0-9_]packages *=" $(SETUP) 2>/dev/null|awk -F"=" '{print $$2}'|tr -d "[]\"', \r\n")
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
  @echo "Warning: package name $(pkgname) and project name $(prjname) are different!"
endif

.PHONY: chkconfig
chkconfig:
	@echo "Project name   = \"$(prjname)\""
	@if [ "$(prjname)" == "travis_emulator" ]; then \
	  echo "Status         = \"$$(cd $(PKGPATH); $(PKGPATH)/$(prjname)/dist_pkg -n -S$(devstatus) $(pkgname))\""; \
	else \
	  echo "Status         = \"$$(cd $(PKGPATH); $(DEVPATH)/dist_pkg -n -S$(devstatus) $(pkgname))\""; \
	fi
	@echo "Hosted         = \"$(HOSTENV)\""
	@echo "Branch         = \"$(BRANCH)\""
	@echo "Package name   = \"$(pkgname)\"($(pkgids))"
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
	@echo "make diff     # diff files with git cloned dir"
	@echo "make replace  # copy files into git cloned dir to pubblish code"
	@echo "make publish  # exec build + upload + publish on pypi"
	@echo "make pep8     # do pep8 on all source python files"
	@echo "make push     # copy file ot other directories"
	@echo "make docs     # write module documentation"

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
	@if [ "$(prjname)" == "travis_emulator" ]; then\
	  cd $(PKGPATH); $(PKGPATH)/$(prjname)/dist_pkg -- $(pkgname) $(prjname);\
	else\
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -- $(pkgname) $(prjname);\
	fi
	@if [ "$(prjname)" != "Odoo" ]; then \
	  echo "Project $(prjname) V$(prjversion) [$(pkgname)] answer:"; \
	  cd $(PKGPATH); PYTHONPATH=$(PKGPATH) python $(prjname); \
	else \
	  echo "Project $(prjname) V$(BRANCH) [$(pkgname) $(prjversion)]"; \
	fi;

.PHONY: check
check:
	@if [ "$(prjname)" == "travis_emulator" ]; then \
       $(PKGPATH)/$(prjname)/travis local/$(prjname) check; \
    else \
      $(DEVPATH)/travis local/$(prjname) check; \
    fi

.PHONY: test
test:
	@find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	@if [ "$(prjname)" != "Odoo" ]; then \
	  cd $(TESTPATH); PYTHONPATH=$(PKGPATH) $(TESTFILE); \
	else \
	  $(DEVPATH)/travis local/$(prjname) test; \
	fi

.PHONY: coverage
coverage:
	find $(PKGPATH) -name "*$(prjname)*.log" -exec rm -f '{}' \;
	cd $(PRJPATH); coverage erase
	cd $(PRJPATH); DEV_ENVIRONMENT=$(prjname) PYTHONPATH=$(PKGPATH) coverage run --source $(prjname) __main__.py
	# cd $(PRJPATH); PYTHONPATH=$(PKGPATH)  coverage run --source $(prjname) $(TESTDIR)/test_$(prjname).py
	cd $(PRJPATH); coverage report

.PHONY: travis
travis:
	$(DEVPATH)/travis local/$(prjname)
	@if [ "$(prjname)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(prjname)/dist_pkg -S3 $(pkgname); \
	else \
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
	@if [ "$(prjname)" == "travis_emulator" ]; then\
	   cd $(PKGPATH); $(PKGPATH)/$(prjname)/dist_pkg -p $(LGITPATH) $(pkgname);\
	else\
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -p $(LGITPATH) $(pkgname);\
	fi

.PHONY: diff
diff:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	@if [ "$(prjname)" == "travis_emulator" ]; then \
	  cd $(PKGPATH); $(PKGPATH)/$(prjname)/dist_pkg -d -p $(LGITPATH) $(pkgname); \
	else \
	  cd $(PKGPATH); $(DEVPATH)/dist_pkg -d -p $(LGITPATH) $(pkgname); \
	fi

.PHONY: push
push:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	cd $(PKGPATH); $(DEVPATH)/dist_pkg -c $(pkgname) $(prjname);

.PHONY: docs
docs:
	@# Warning! This command is just for internal use and doesn't work outside Zeroincombenze(R) environment
	cd $(PRJPATH); PYTHONPATH=$(PKGPATH) $(DEVPATH)/wok_doc -v $(pkgname)
	# cd $(PRJPATH); PYTHONPATH=$(PKGPATH) ./wok_doc -v $(pkgname)
