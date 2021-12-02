#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 1.0.2.7
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
HOME_DEV="$HOME/devel"
[[ -x $TDIR/../bin/python ]] && PYTHON=$(readlink -f $TDIR/../bin/python) || [[ -x $TDIR/python ]] && PYTHON="$TDIR/python" || PYTHON="python"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\no=os.path\nHOME=os.environ.get('HOME');t=o.join(HOME,'tools')\nn=o.join(HOME,'pypi') if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME,HOME_DEV, 'pypi')\nd=HOME_DEV if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME_DEV,'venv')\ndef apl(l,p,b):\n if p:\n  p2=o.join(p,b,b)\n  p1=o.join(p,b)\n  if o.isdir(p2):\n   l.append(p2)\n  elif o.isdir(p1):\n   l.append(p1)\nl=[TDIR]\nv=''\nfor x in sys.path:\n if not o.isdir(t) and o.isdir(o.join(x,'tools')):\n  t=o.join(x,'tools')\n if not v and o.basename(x)=='site-packages':\n  v=x\nfor x in os.environ['PATH'].split(':'):\n if x.startswith(d):\n  d=x\n  break\nfor b in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(d):\n  apl(l,d,b)\n elif TDIR.startswith(n):\n  apl(l,n,b)\n apl(l,v,b)\n apl(l,t,b)\nl=l+os.environ['PATH'].split(':')\ntdir=o.dirname(TDIR)\np=set()\npa=p.add\np=[x for x in l if x and (x.startswith(HOME) or x.startswith(HOME_DEV) or x.startswith(tdir)) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found in <$PYPATH>!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
Z0TLIBDIR=$(findpkg z0testrc "$PYPATH" "zerobug")
if [[ -z "$Z0TLIBDIR" ]]; then
  echo "Library file z0testrc not found!"
  exit 72
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0TLIBDIR=$Z0TLIBDIR"

DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=0.3.53.4


test_01() {
    RES=$($RUNDIR/list_requirements.py -V 2>&1)
    test_result "list_requirements" "$__version__" "$RES"
    #
    TRES="python=six,astroid,Click,codecov,configparser,coverage,coveralls,docopt,flake8,isort,lazy_object_proxy,lxml,MarkupSafe,mock,pbr,polib,pycodestyle,pycparser,pyflakes,Pygments,pylint,pylint-mccabe,pylint-plugin-utils,pylint_odoo,pyopenssl,pyserial,pytest,python_plus,PyWebDAV,PyYAML,QUnitSuite,restructuredtext_lint,rfc3986,setuptools,simplejson,unittest2,urllib3[secure],websocket-client,whichcraft,wrapt,z0bug_odoo,docutils,zerobug"
    RES=$($RUNDIR/list_requirements.py -b10.0 -tpython -T)
    test_result "list_requirements -b10.0 -tpython -T" "$TRES" "$RES"
    #
    TRES="python=Babel==2.3.4,chardet,configparser,decorator==3.4.0,feedparser==5.1.3,future,gdata==2.0.18,gevent==1.0.2,html2text,Jinja2==2.7.3,'lxml>=3.4.1',Mako==1.0.4,num2words,numpy,passlib==1.6.2,psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.5.4',pydot==1.2.3,pyparsing==2.0.3,pyPdf==1.13,pyserial==2.7,Python-Chart==1.39,python-dateutil==2.5.3,python-ldap==2.4.19,python-openid==2.2.5,'python-stdnum>=1.8.1',pytz==2014.10,reportlab==3.1.44,simplejson==3.5.3,urllib3[secure],vatnumber==1.2,Werkzeug==0.9.6,docutils==0.14,six==1.9.0,Pillow==3.4.1"
    RES=$($RUNDIR/list_requirements.py -b8.0 -tpython -BP)
    test_result "list_requirements -b8.0 -tpython -BP" "$TRES" "$RES"
    #
    TRES="python=Babel==2.3.4,chardet,configparser,decorator==4.0.10,feedparser==5.2.1,future,gdata==2.0.18,gevent==1.1.2,html2text,Jinja2==2.10.1,'lxml>=3.4.1',Mako==1.0.4,num2words,numpy,passlib==1.6.5,psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.7.4',pydot==1.2.3,pyparsing==2.1.10,pyPdf==1.13,'pyserial>=3.1.1',Python-Chart==1.39,python-dateutil==2.5.3,python-ldap==2.4.27,python-openid==2.2.5,'python-stdnum>=1.8.1',pytz==2016.7,reportlab==3.3.0,simplejson==3.5.3,'six>=1.10.0',urllib3[secure],vatnumber==1.2,Werkzeug==0.11.11,docutils==0.14,Pillow==3.4.1"
    RES=$($RUNDIR/list_requirements.py -b10.0 -tpython -BP)
    test_result "list_requirements -b10.0 -tpython -BP" "$TRES" "$RES"
    #
    TRES="python=Babel==2.3.4,chardet,configparser,decorator==4.0.10,feedparser==5.2.1,future,gdata==2.0.18,gevent==1.3.4,html2text,Jinja2==2.10.1,'lxml>=3.4.1',Mako==1.0.4,num2words,numpy,passlib==1.6.5,docutils==0.14,Pillow==6.1.0,psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.8.3',pydot==1.2.3,pyparsing==2.1.10,pyPDF2,'pyserial>=3.1.1',Python-Chart==1.39,python-dateutil==2.5.3,python-openid==2.2.5,'python-stdnum>=1.8.1',python3-ldap,pytz==2016.7,reportlab==3.3.0,simplejson==3.5.3,'six>=1.10.0',urllib3[secure],vatnumber==1.2,Werkzeug==0.14.1"
    RES=$($RUNDIR/list_requirements.py -b12.0 -tpython -BP)
    test_result "list_requirements -b12.0 -tpython -BP" "$TRES" "$RES"
}

Z0BUG_setup() {
    :
}

Z0BUG_teardown() {
    :
}


Z0BUG_init
parseoptest -l$TESTDIR/test_clodoo.log "$@"
sts=$?
[[ $sts -ne 127 ]] && exit $sts


UT1_LIST=
UT_LIST=""
[[ "$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
[[ "$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit $sts
