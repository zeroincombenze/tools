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

__version__=0.3.8.5


test_01() {
    local k v RES
    declare -A TRES
    TRES[6.1]="Sales Management"
    TRES[7.0]="Sales"
    TRES[8.0]="Sales"
    TRES[9.0]="Sales"
    TRES[10.0]="Sales"
    TRES[11.0]="Sales"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0; do
      RES=$($RUNDIR/transodoo.py translate -m res.groups -s SALES -b$v)
      test_result "translate SALES $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    k="name"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0; do
      RES=$($RUNDIR/transodoo.py translate -m res.groups -k "$k" -s "Sales" -f 7.0 -b$v)
      test_result "translate $k/Sales from 7.0 to $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
}

test_02() {
    local k v RES
    declare -A TRES
    TRES[6.1]="report_type"
    TRES[7.0]="report_type"
    TRES[8.0]="report_type"
    TRES[9.0]="type"
    TRES[10.0]="type"
    TRES[11.0]="type"
    #
    k="report_type"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -s "$k" -f 7.0 -b$v)
      test_result "translate $k/account.account.type from 7.0 to $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    k="type"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -s "$k" -f 10.0 -b$v)
      test_result "translate $k/account.account.type from 10.0 to $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
}


Z0BUG_setup() {
    :
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
# UT_LIST="__version_V_${__version__}$RUNDIR/transodoo.py"
UT_LIST=
if [ "$(type -t Z0BUG_setup)" == "function" ]; then Z0BUG_setup; fi
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
if [ "$(type -t Z0BUG_teardown)" == "function" ]; then Z0BUG_teardown; fi
exit $sts
