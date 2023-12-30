#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
# Based on template 2.0.13
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
[[ -x $TDIR/../bin/python3 ]] && PYTHON=$(readlink -f $TDIR/../bin/python3) || [[ -x $TDIR/python3 ]] && PYTHON="$TDIR/python3" || PYTHON=$(which python3 2>/dev/null) || PYTHON="python"
[[ -z $PYPATH ]] && PYPATH=$(echo -e "import os,sys\no=os.path\na=o.abspath\nj=o.join\nd=o.dirname\nb=o.basename\nf=o.isfile\np=o.isdir\nC=a('"$TDIR"')\nD='"$HOME_DEVEL"'\nU='setup.py'\nH=o.expanduser('~')\nR=j(D,'pypi')\nW=j(D,'venv')\nS='site-packages'\nX='scripts'\nY=[x for x in sys.path if b(x)==S]\nY=Y[0] if Y else C\ndef isk(P):\n return P.startswith((H,D,C,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))\ndef adk(L,P):\n if p(j(P,X)) and j(P,X) not in L:\n  L.append(j(P,X))\n if P not in L:\n  L.append(P)\nL=[C]\nfor B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n for P in [C]+os.environ['PATH'].split(':')+[W,R]:\n  P=a(P)\n  if b(P) in (X,'tests','travis','_travis'):\n   P=d(P)\n  if b(P)==b(d(P)) and f(j(P,'..',U)):\n   P=d(d(P))\n  if B==b(P) and isk(P):\n   adk(L,P)\n   break\n  elif isk(j(P,B,B)):\n   adk(L,j(P,B,B))\n   break\n  elif isk(j(P,B)):\n   adk(L,j(P,B))\n   break\n  else:\n   adk(L, j(Y,B))\nadk(L,os.getcwd())\nprint(' '.join(L))\n"|$PYTHON)
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

__version__=2.0.8


test_01() {
    local cmd
    cmd="$RUNDIR/odoo_skin.sh -Tq 7.0 skin1"
    eval $cmd
    test_result "skin: favicon" "$TESTDIR/website-themes/skin1/favicon.ico" "$TESTDIR/odoo/addons/web/static/src/img/favicon.ico"  "diff"
}

Z0BUG_setup() {
    mkdir -p $TESTDIR/odoo
    mkdir -p $TESTDIR/odoo/addons
    mkdir -p $TESTDIR/odoo/addons/web
    touch $TESTDIR/odoo/addons/web/__openerp__.py
    mkdir -p $TESTDIR/odoo/addons/web/static
    mkdir -p $TESTDIR/odoo/addons/web/static/src
    mkdir -p $TESTDIR/odoo/addons/web/static/src/xml
    touch $TESTDIR/odoo/addons/web/static/src/xml/base.xml
    mkdir -p $TESTDIR/odoo/addons/web/static/src/js
    mkdir -p $TESTDIR/odoo/addons/web/static/src/img
    touch $TESTDIR/odoo/addons/web/static/src/img/favicon.ico
    mkdir -p $TESTDIR/odoo/addons/web/static/src/css
    touch $TESTDIR/odoo/addons/web/static/src/css/base.sass
    touch $TESTDIR/odoo/addons/web/static/src/css/base.css
    mkdir -p $TESTDIR/website-themes
    mkdir -p $TESTDIR/website-themes/example
    touch $TESTDIR/website-themes/example/__openerp__.py
    mkdir -p $TESTDIR/website-themes/skin1
    echo "favicon" > $TESTDIR/website-themes/skin1/favicon.ico
    cat << EOF > $TESTDIR/website-themes/skin1/skin_colors.conf
# Example of skin file
CSS_facets-border=#F1E2D3
CSS_sheet-max-width=860px
EOF
    cat << EOF > $TESTDIR/website-themes/skin1/base.sass
// V0.3.36
// Text def color: dev=#805070 qt=#123456 prod=#2a776d
//\$zi-def-text: #805070
\$zi-def-text: #123456
//\$zi-def-text: #2a776d
// Text def color: dev=#805070 prod=#2a776d
//\$zi-def-text-bg: #805070
\$zi-def-text-bg: #2a776d
// Text def color: dev=#805070 prod=#2a776d
\$zi-login-text: #805070
//\$zi-login-text: #2a776d
// Text def color: dev=#805070 prod=#2a776d
\$zi-login-text-bg: #805070
\$zi-login-text-bg: #2a776d
\$facets-border: #afafb6
\$sheet-max-width: auto
\$sheet-padding: 16px
EOF
    cat << EOF > $TESTDIR/website-themes/skin1/base.sass
// V0.3.36
// Text def color: dev=#805070 qt=#123456 prod=#2a776d
//\$zi-def-text: #805070
//\$zi-def-text: #123456
\$zi-def-text: #2a776d
// Text def color: dev=#805070 prod=#2a776d
//\$zi-def-text-bg: #805070
\$zi-def-text-bg: #2a776d
// Text def color: dev=#805070 prod=#2a776d
//\$zi-login-text: #805070
\$zi-login-text: #2a776d
// Text def color: dev=#805070 prod=#2a776d
//\$zi-login-text-bg: #805070
\$zi-login-text-bg: #2a776d
\$facets-border: #F1E2D3
\$sheet-max-width: 860px
\$sheet-padding: 16px
EOF
}

Z0BUG_teardown() {
    :
}


Z0BUG_init
parseoptest -l$TESTDIR/test_clodoo.log "$@"
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
