#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 2.0.0
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
[[ -x $TDIR/../bin/python3 ]] && PYTHON=$(readlink -f $TDIR/../bin/python3) || [[ -x $TDIR/python3 ]] && PYTHON="$TDIR/python3" || PYTHON=$(which python3 2>/dev/null) || PYTHON="python"
[[ -z $PYPATH ]] && PYPATH=$(echo -e "import os,sys\no=os.path\na=o.abspath\nj=o.join\nd=o.dirname\nb=o.basename\nf=o.isfile\np=o.isdir\nC=a('"$TDIR"')\nD='"$HOME_DEVEL"'\nif not p(D) and '/devel/' in C:\n D=C\n while b(D)!='devel':  D=d(D)\nN='venv_tools'\nU='setup.py'\nO='tools'\nH=o.expanduser('~')\nT=j(d(D),O)\nR=j(d(D),'pypi') if b(D)==N else j(D,'pypi')\nW=D if b(D)==N else j(D,'venv')\nS='site-packages'\nX='scripts'\ndef pt(P):\n P=a(P)\n if b(P) in (X,'tests','travis','_travis'):\n  P=d(P)\n if b(P)==b(d(P)) and f(j(P,'..',U)):\n  P=d(d(P))\n elif b(d(C))==O and f(j(P,U)):\n  P=d(P)\n return P\ndef ik(P):\n return P.startswith((H,D,K,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))\ndef ak(L,P):\n if P not in L:\n  L.append(P)\nL=[C]\nK=pt(C)\nfor B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n for P in [C]+sys.path+os.environ['PATH'].split(':')+[W,R,T]:\n  P=pt(P)\n  if B==b(P) and ik(P):\n   ak(L,P)\n   break\n  elif ik(j(P,B,B)):\n   ak(L,j(P,B,B))\n   break\n  elif ik(j(P,B)):\n   ak(L,j(P,B))\n   break\n  elif ik(j(P,S,B)):\n   ak(L,j(P,S,B))\n   break\nak(L,os.getcwd())\nprint(' '.join(L))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
[[ -z "$Z0LIBDIR" ]] && echo "Library file z0librc not found in <$PYPATH>!" && exit 72
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
Z0TLIBDIR=$(findpkg z0testrc "$PYPATH" "zerobug")
[[ -z "$Z0TLIBDIR" ]] && echo "Library file z0testrc not found!" && exit 72
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0TLIBDIR=$Z0TLIBDIR"

CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.11


test_01() {
    RES=$(list_requirements.py -V 2>&1)
    # test_result "list_requirements -V" "$__version__" "$RES"
    #
    TRES="asn1crypto certifi cryptography idna pyasn1 pyOpenSSL urllib3[secure]"
    RES=$(list_requirements.py -qStpython -s ' ')
    test_result "list_requirements -qStpython" "$TRES" "$RES"
    #
    TRES="astroid Click configparser coverage docopt docutils flake8 future GitPython isort lazy_object_proxy lxml MarkupSafe mock pbr polib pycodestyle pycparser pyflakes Pygments pylint pylint-mccabe pylint-odoo pylint-plugin-utils pyserial pytest python-magic PyWebDAV PyYAML QUnitSuite restructuredtext_lint rfc3986 setuptools simplejson six translators unittest2 websocket-client whichcraft wrapt z0bug_odoo zerobug"
    RES=$(list_requirements.py -qTtpython -s ' ')
    test_result "list_requirements -qTtpython" "$TRES" "$RES"
    #
    TRES="clodoo odoorpc os0"
    RES=$(list_requirements.py -qRtpython -s ' ')
    test_result "list_requirements -qRtpython" "$TRES" "$RES"
    #
    TRES="build-essential expect-dev libffi-dev libpq-dev libssl-dev python-dev python-setuptools"
    RES=$(list_requirements.py -qSTRtbin -s ' ')
    test_result "list_requirements -qSTRtbin" "$TRES" "$RES"
    #
    TRES="libcups2-dev"
    RES=$(list_requirements.py -qtbin -jpycups -s ' ')
    test_result "list_requirements -qtbin -jpycups" "$TRES" "$RES"
}

test_02() {
    TRES="Babel,chardet,configparser,decorator,docutils,feedparser,future,gdata,gevent,html2text,Jinja2,lessc,lxml,Mako,num2words,numpy,passlib,Pillow,psutil,psycogreen,psycopg2-binary,pydot,pyparsing,pyPdf,pyPDF2,pyserial,Python-Chart,python-dateutil,python-ldap,python-openid,python-plus,python-stdnum,pytz,reportlab,simplejson,six,vatnumber,Werkzeug"
    RES=$(list_requirements.py -B -b12.0 -qtpython)
    test_result "list_requirements -B -b12.0 -qtpython" "$TRES" "$RES"
    #
    TRES="astroid Babel chardet Click clodoo configparser coverage decorator docopt docutils feedparser flake8 future gdata gevent GitPython html2text isort Jinja2 lazy_object_proxy lessc lxml Mako MarkupSafe mock num2words numpy odoorpc os0 passlib pbr Pillow polib psutil psycogreen psycopg2-binary pycodestyle pycparser pydot pyflakes Pygments pylint pylint-mccabe pylint-odoo pylint-plugin-utils pyparsing pyPdf pyPDF2 pyserial pytest Python-Chart python-dateutil python-ldap python-magic python-openid python-plus python-stdnum pytz PyWebDAV3 PyYAML QUnitSuite reportlab restructuredtext_lint rfc3986 setuptools simplejson six translators unittest2 vatnumber websocket-client Werkzeug whichcraft wrapt z0bug_odoo zerobug"
    RES=$(list_requirements.py -BTR -b12.0 -qtpython -s ' ')
    test_result "list_requirements -BTR -b12.0 -qtpython" "$TRES" "$RES"
    #
    TRES="asn1crypto astroid certifi Click clodoo configparser coverage cryptography docopt docutils flake8 future GitPython idna isort lazy_object_proxy lxml MarkupSafe mock odoorpc os0 pbr polib pyasn1 pycodestyle pycparser pyflakes Pygments pylint pylint-mccabe pylint-odoo pylint-plugin-utils pyOpenSSL pyserial pytest python-magic PyWebDAV3 PyYAML QUnitSuite restructuredtext_lint rfc3986 setuptools simplejson six translators unittest2 urllib3[secure] websocket-client whichcraft wrapt z0bug_odoo zerobug"
    RES=$(list_requirements.py -TRS -b12.0 -qtpython -s ' ')
    test_result "list_requirements -TRS -b12.0 -qtpython" "$TRES" "$RES"
    #
    TRES="Babel chardet decorator feedparser gdata gevent html2text Jinja2 lessc Mako num2words numpy passlib Pillow psutil psycogreen psycopg2-binary pydot pyparsing pyPdf pyPDF2 Python-Chart python-dateutil python-ldap python-openid python-plus python-stdnum pytz reportlab six vatnumber Werkzeug"
    RES=$(list_requirements.py -BX -b12.0 -qtpython -s ' ')
    test_result "list_requirements -BX -b12.0 -qtpython" "$TRES" "$RES"
}

test_03() {
    TRES="python=astroid,Click,configparser,coverage,docopt,docutils,flake8,future,GitPython,isort,lazy_object_proxy,lxml,MarkupSafe,mock,pbr,polib,pycodestyle,pycparser,pyflakes,Pygments,pylint,pylint-mccabe,pylint-odoo,pylint-plugin-utils,pyserial,pytest,python-magic,PyWebDAV,PyYAML,QUnitSuite,restructuredtext_lint,rfc3986,setuptools,simplejson,six,unittest2,websocket-client,whichcraft,wrapt,z0bug_odoo,zerobug"
    RES=$(list_requirements.py -b10.0 -tpython -T)
    test_result "list_requirements -b10.0 -tpython -T" "$TRES" "$RES"
    #
    TRES="python=asn1crypto,Babel==2.3.4,certifi,chardet,configparser,'cryptography>=2.2.2,<3.4',decorator==3.4.0,docutils==0.16,feedparser==5.1.3,future,gdata==2.0.18,gevent==1.0.2,html2text,idna,Jinja2==2.7.3,'lxml>=3.3.5,<=3.4.1','Mako>=1.0.4',num2words,numpy,passlib==1.6.2,Pillow==3.4.1,psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.5.4,<2.8.0',pyasn1,pydot==1.2.3,'pyOpenSSL>=16.2.0,<19.0',pyparsing==2.0.3,pyPDF2==1.28.4,pyPdf==1.13,pyserial==2.7,Python-Chart==1.39,python-dateutil==2.5.3,python-ldap==2.4.19,python-openid==2.2.5,python-plus,'python-stdnum>=1.8.1','pytz>=2014.10',reportlab==3.1.44,simplejson==3.5.3,six==1.9.0,urllib3[secure],vatnumber==1.2,Werkzeug==0.9.6"
    RES=$(list_requirements.py -b8.0 -tpython -BSP)
    test_result "list_requirements -b8.0 -tpython -BSP" "$TRES" "$RES"
    #
    TRES="python=asn1crypto,Babel==2.3.4,certifi,chardet,configparser,'cryptography>=2.2.2,<3.4',decorator==4.0.10,docutils==0.16,feedparser==5.2.1,future,gdata==2.0.18,'gevent>=1.1.2,<=1.4.0',html2text,idna,Jinja2==2.10.1,'lessc>=3.0.0','lxml>=3.5.0,<=3.6.4','Mako>=1.0.4',num2words,numpy,passlib==1.6.5,Pillow==3.4.1,psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.7.4',pyasn1,pydot==1.2.3,'pyOpenSSL>=16.2.0,<19.0',pyparsing==2.1.10,pyPDF2==1.28.4,pyPdf==1.13,'pyserial>=3.1.1',Python-Chart==1.39,python-dateutil==2.5.3,python-ldap==2.4.27,python-openid==2.2.5,python-plus,'python-stdnum>=1.8.1','pytz>=2016.7',reportlab==3.3.0,'simplejson>=3.5.3','six>=1.10.0',urllib3[secure],vatnumber==1.2,Werkzeug==0.11.11"
    RES=$(list_requirements.py -b10.0 -tpython -BSP)
    test_result "list_requirements -b10.0 -tpython -BSP" "$TRES" "$RES"
    #
    TRES="python=asn1crypto,Babel==2.3.4,certifi,chardet,configparser,'cryptography>=23.0,<38.0',decorator==4.0.10,docutils==0.16,feedparser==5.2.1,future,gdata==2.0.18,'gevent>=1.5.0,<=21.12.0',html2text,idna,Jinja2==2.10.1,'lessc>=3.0.0','lxml>=4.2.3,<=4.6.5','Mako>=1.0.4',num2words,numpy,passlib==1.6.5,Pillow==4.0.0,psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.8.3',pyasn1,pydot==1.2.3,'pyOpenSSL>=16.2.0,<19.0',pyparsing==2.1.10,'pyPDF2<2.0',pyPdf==1.13,'pyserial>=3.1.1',Python-Chart==1.39,python-dateutil==2.5.3,python-ldap==3.1.0,python-openid==2.2.5,python-plus,'python-stdnum>=1.8.1','pytz>=2016.7',reportlab==3.3.0,'simplejson>=3.5.3','six>=1.10.0',urllib3[secure],vatnumber==1.2,Werkzeug==0.14.1"
    RES=$(list_requirements.py -b12.0 -tpython -BSP)
    test_result "list_requirements -b12.0 -tpython -BSP" "$TRES" "$RES"
    #
    TRES="python=asn1crypto,'Babel>=2.6.0,<=2.9.1',certifi,chardet,configparser,'cryptography>=23.0,<38.0',decorator==4.0.10,docutils==0.16,feedparser==5.2.1,future,gdata==2.0.18,'gevent>=22.10.0,<=22.10.99',html2text,idna,Jinja2==2.10.1,'lessc>=3.0.0','lxml>=4.6.5','Mako>=1.0.4',num2words,numpy,'passlib>=1.7.0','Pillow>=7.0.0',psutil==4.3.1,psycogreen==1.0,'psycopg2-binary>=2.8.3',pyasn1,pydot==1.2.3,'pyOpenSSL>=16.2.0,<23.0',pyparsing==2.1.10,'pyPDF2<2.0',pyPdf==1.13,'pyserial>=3.1.1',Python-Chart==1.39,python-dateutil==2.5.3,python-ldap==3.1.0,python-openid==2.2.5,python-plus,'python-stdnum>=1.8.1','pytz>=2016.7',qrcode==5.3,reportlab==3.3.0,'simplejson>=3.5.3','six>=1.10.0',urllib3[secure],vatnumber==1.2,Werkzeug==0.16.1,zeep==2.4.0"
    RES=$(list_requirements.py -b16.0 -tpython -BSP)
    test_result "list_requirements -b16.0 -tpython -BSP" "$TRES" "$RES"
}

Z0BUG_setup() {
    chmod -c +x $RUNDIR/scripts/list_requirements.py
    build_cmd $RUNDIR/scripts/list_requirements.py
}

Z0BUG_teardown() {
    :
}


Z0BUG_init
parseoptest -l$TESTDIR/test_python_plus.log "$@"
sts=$?
[[ $sts -ne 127 ]] && exit $sts
for p in z0librc odoorc travisrc zarrc z0testrc; do
  if [[ -f $RUNDIR/$p ]]; then
    [[ $p == "z0librc" ]] && Z0LIBDIR="$RUNDIR" && source $RUNDIR/$p
    [[ $p == "odoorc" ]] && ODOOLIBDIR="$RUNDIR" && source $RUNDIR/$p
    [[ $p == "travisrc" ]] && TRAVISLIBDIR="$RUNDIR" && source $RUNDIR/$p
    [[ $p == "zarrc" ]] && ZARLIB="$RUNDIR" && source $RUNDIR/$p
    [[ $p == "z0testrc" ]] && Z0TLIBDIR="$RUNDIR" && source $RUNDIR/$p
  fi
done


UT1_LIST=
UT_LIST=""
[[ "$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
[[ "$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit $sts


