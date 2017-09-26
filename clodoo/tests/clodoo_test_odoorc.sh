#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in $TDIR $TDIR/.. $TDIR/../z0lib $TDIR/../../z0lib . .. /etc; do
  if [ -e $x/z0librc ]; then
    . $x/z0librc
    Z0LIBDIR=$x
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
Z0TLIBDIR=$(findpkg z0testrc "$TDIR $TDIR/.. $TDIR/../zerobug $TDIR/../../zerobug  . .. $HOME/dev")
if [ -z "$Z0TLIBDIR" ]; then
  echo "Library file z0testrc not found!"
  exit 2
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)
__version__=0.0.2


test_01() {
    local s sts v
    sts=0
    opt_mult=0
    declare -A TRES
    TRES[6]="6.1"
    TRES[7]="7.0"
    TRES[8]="8.0"
    TRES[9]="9.0"
    TRES[10]="10.0"
    TRES[11]="11.0"
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $v)
      fi
      test_result "full version $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[6]=/etc/odoo/odoo-server.conf
    TRES[7]=/etc/odoo/odoo-server.conf
    TRES[8]=/etc/odoo/odoo-server.conf
    TRES[9]=/etc/odoo/odoo-server.conf
    TRES[10]=/etc/odoo/odoo.conf
    TRES[11]=/etc/odoo/odoo.conf
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param CONFN $v)
      fi
      test_result "config filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in 6 7 8 9 10; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ $v -eq 6 ]; then
          RES=$(build_odoo_param CONFN $v.1)
        else
          RES=$(build_odoo_param CONFN $v.0)
        fi
      fi
      test_result "config filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    opt_mult=1
    declare -A TRES
    TRES[6]=/etc/odoo/odoo6-server.conf
    TRES[7]=/etc/odoo/odoo7-server.conf
    TRES[8]=/etc/odoo/odoo8-server.conf
    TRES[9]=/etc/odoo/odoo9-server.conf
    TRES[10]=/etc/odoo/odoo10.conf
    TRES[11]=/etc/odoo/odoo11.conf
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param CONFN $v)
      fi
      test_result "config filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ $v -eq 6 ]; then
          RES=$(build_odoo_param CONFN $v.1)
        else
          RES=$(build_odoo_param CONFN $v.0)
        fi
      fi
      test_result "config filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[6]=/var/log/odoo/odoo6-server.log
    TRES[7]=/var/log/odoo/odoo7-server.log
    TRES[8]=/var/log/odoo/odoo8-server.log
    TRES[9]=/var/log/odoo/odoo9-server.log
    TRES[10]=/var/log/odoo/odoo10.log
    TRES[11]=/var/log/odoo/odoo11.log
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ $v -eq 6 ]; then
          RES=$(build_odoo_param FLOG $v.1)
        else
          RES=$(build_odoo_param FLOG $v.0)
        fi
      fi
      test_result "log filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[6]=/var/run/odoo/odoo6-server.pid
    TRES[7]=/var/run/odoo/odoo7-server.pid
    TRES[8]=/var/run/odoo/odoo8-server.pid
    TRES[9]=/var/run/odoo/odoo9-server.pid
    TRES[10]=/var/run/odoo/odoo10.pid
    TRES[11]=/var/run/odoo/odoo11.pid
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ $v -eq 6 ]; then
          RES=$(build_odoo_param FPID $v.1)
        else
          RES=$(build_odoo_param FPID $v.0)
        fi
      fi
      test_result "pid filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[6]=/etc/init.d/odoo6-server
    TRES[7]=/etc/init.d/odoo7-server
    TRES[8]=/etc/init.d/odoo8-server
    TRES[9]=/etc/init.d/odoo9-server
    TRES[10]=/etc/init.d/odoo10
    TRES[11]=/etc/init.d/odoo11
    for v in 6 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ $v -eq 6 ]; then
          RES=$(build_odoo_param SVCNAME $v.1)
        else
          RES=$(build_odoo_param SVCNAME $v.0)
        fi
      fi
      test_result "script name $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

Z0BUG_setup() {
    local VERSION=9.0
    local ODOO_REPO=local/odoo
    LCLTEST_PRJNAME="Odoo"
    LCLTEST_REPOSNAME=l10n_italy
    LCLTEST_PKGNAME=l10n_it_base
    LCLTEST_TMPDIR0=~/dev/odoo/$VERSION
    LCLTEST_PRJPATH=$LCLTEST_TMPDIR0/$LCLTEST_REPOSNAME
    LCLTEST_TMPDIR=$LCLTEST_PRJPATH/$LCLTEST_PKGNAME
    LCLTEST_TMPDIR2=$LCLTEST_PRJPATH/__unported__/$LCLTEST_PKGNAME
    mkdir -p $LCLTEST_TMPDIR0
    mkdir -p $LCLTEST_PRJPATH
    mkdir -p $LCLTEST_TMPDIR
    mkdir -p $LCLTEST_TMPDIR2
    touch $LCLTEST_TMPDIR/__openerp__.py
    touch $LCLTEST_TMPDIR2/__openerp__.py
    LCLTEST_SETUP=__openerp__.py
    LCLTEST_MQT_PATH=$HOME/maintainer-quality-tools/travis
    if [ ! -f /etc/odoo/odoo9-server.conf ]; then
      LCLTEST_ODOO9_SERVER=/etc/odoo/odoo9-server.conf
      touch $LCLTEST_ODOO9_SERVER
    fi
    if [ -d ~/$VERSION/dependencies ]; then rm -fR ~/$VERSION/dependencies; fi
    if [ -L ~/$VERSION/dependencies ]; then rm -f ~/$VERSION/dependencies; fi
}

Z0BUG_teardown() {
    rm -fR $LCLTEST_TMPDIR2
    rm -fR $LCLTEST_TMPDIR
    rm -fR $LCLTEST_PRJPATH
    rm -fR $LCLTEST_TMPDIR0
    if [ -n "$LCLTEST_ODOO9_SERVER" ]; then
      rm -f $LCLTEST_ODOO9_SERVER
    fi
    if [ -f $FOUT ]; then rm -f $FOUT; fi
    if [ -f $FTEST ]; then rm -f $FTEST; fi
}


Z0BUG_init
parseoptest -l$TESTDIR/test_clodoo.log "$@ -J"
sts=$?
if [ $sts -ne 127 ]; then
  exit $sts
fi
opt_oelib=1
if [ ${opt_oelib:-0} -ne 0 ]; then
  ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $TDIR/../clodoo $TDIR/../../clodoo . .. $HOME/dev")
  if [ -z "$ODOOLIBDIR" ]; then
    echo "Library file odoorc not found!"
    exit 2
  fi
  . $ODOOLIBDIR
fi
if [ ${opt_tlib:-0} -ne 0 ]; then
  TRAVISLIBDIR=$(findpkg travisrc "$TDIR $TDIR/.. $TDIR/../travis_emulator $TDIR/../../travis_emulator . .. $HOME/dev")
  if [ -z "$TRAVISLIBDIR" ]; then
    echo "Library file travisrc not found!"
    exit 2
  fi
  . $TRAVISLIBDIR
fi
UT1_LIST=
UT_LIST=""
if [ "$(type -t Z0BUG_setup)" == "function" ]; then Z0BUG_setup; fi
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
if [ "$(type -t Z0BUG_teardown)" == "function" ]; then Z0BUG_teardown; fi
exit $sts
