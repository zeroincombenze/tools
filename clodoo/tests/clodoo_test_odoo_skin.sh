#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=$(echo -e "import sys\nprint(str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1])"|python)
for d in $TDIR $TDIR/.. $TDIR/../.. $HOME/dev $HOME/tools ${PYPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ] && [ -e $d/z0lib/z0librc ]; then
    . $d/z0lib/z0librc
    Z0LIBDIR=$d/z0lib
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)
Z0TLIBDIR=$(findpkg z0testrc "$TDIR $TDIR/.. $HOME/tools/zerobug $HOME/dev ${PYPATH//:/ } . .." "zerobug")
if [ -z "$Z0TLIBDIR" ]; then
  echo "Library file z0testrc not found!"
  exit 2
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)

__version__=0.3.7.12


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
// V0.1.3
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
// V0.1.3
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
parseoptest -l$TESTDIR/test_clodoo.log "$@" "-O"
sts=$?
if [ $sts -ne 127 ]; then
  exit $sts
fi
if [ ${opt_oeLib:-0} -ne 0 ]; then
  ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $HOME/tools/clodoo $HOME/dev ${PYPATH//:/ } . .." "clodoo")
  if [ -z "$ODOOLIBDIR" ]; then
    echo "Library file odoorc not found!"
    exit 2
  fi
  . $ODOOLIBDIR
fi





UT1_LIST=
UT_LIST=""
if [ "$(type -t Z0BUG_setup)" == "function" ]; then Z0BUG_setup; fi
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
if [ "$(type -t Z0BUG_teardown)" == "function" ]; then Z0BUG_teardown; fi
exit $sts
