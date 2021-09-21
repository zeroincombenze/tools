#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=""
for p in $TDIR $TDIR/.. $TDIR/../.. $HOME/venv_tools/bin $HOME/venv_tools/lib $HOME/tools; do
  [[ -d $p ]] && PYPATH=$(find $(readlink -f $p) -maxdepth 3 -name z0librc)
  [[ -n $PYPATH ]] && break
done
PYPATH=$(echo -e "import os,sys;p=[os.path.dirname(x) for x in '$PYPATH'.split()];p.extend([x for x in os.environ['PATH'].split(':') if x not in p and not x.startswith('/usr') and not x.startswith('/sbin') and not x.startswith('/bin')]);p.extend([x for x in sys.path if x not in p]);print(' '.join(p))"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$($READLINK -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
Z0TLIBDIR=$(findpkg z0testrc "$PYPATH" "zerobug")
if [[ -z "$Z0TLIBDIR" ]]; then
  echo "Library file z0testrc not found!"
  exit 72
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0TLIBDIR=$Z0TLIBDIR"

__version__=0.3.34.99


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
// V0.3.34.99
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
// V0.3.34.99
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
parseoptest -l$TESTDIR/test_UNKNOWN.log "$@"
sts=$?
[[ $sts -ne 127 ]] && exit $sts



UT1_LIST=
UT_LIST=""
[[ "$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
[[ "$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit $sts
