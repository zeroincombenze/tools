#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYTHONPATH=$(echo -e "import sys\nprint str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1]"|python)
for d in $TDIR $TDIR/.. $TDIR/../z0lib $TDIR/../../z0lib ${PYTHONPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ]; then
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
Z0TLIBDIR=$(findpkg z0testrc "$TDIR $TDIR/.. $TDIR/../zerobug $TDIR/../../zerobug  . .. $HOME/dev")
if [ -z "$Z0TLIBDIR" ]; then
  echo "Library file z0testrc not found!"
  exit 2
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)

__version__=0.3.2.1


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
    TRES[v7]="7"
    TRES[6.1]="6"
    TRES[7.0]="7"
    TRES[8.0]="8"
    TRES[9.0]="9"
    TRES[10.0]="10"
    TRES[11.0]="11"
    for v in 6.1 v7 7.0 8.0 9.0 10.0 11.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param MAJVER $v)
      fi
      test_result "major version $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=/etc/odoo/openerp-server.conf
    TRES[6]=/etc/odoo/openerp-server.conf
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
    for v in 6 v7 7 8 9 10; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param CONFN $v)
        elif [ $v -eq 6 ]; then
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
    TRES[v7]=/etc/odoo/openerp-server.conf
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
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param CONFN $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param CONFN $v.1)
        else
          RES=$(build_odoo_param CONFN $v.0)
        fi
      fi
      test_result "config filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=/var/log/odoo/openerp-server.log
    TRES[6]=/var/log/odoo/odoo6-server.log
    TRES[7]=/var/log/odoo/odoo7-server.log
    TRES[8]=/var/log/odoo/odoo8-server.log
    TRES[9]=/var/log/odoo/odoo9-server.log
    TRES[10]=/var/log/odoo/odoo10.log
    TRES[11]=/var/log/odoo/odoo11.log
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param FLOG $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param FLOG $v.1)
        else
          RES=$(build_odoo_param FLOG $v.0)
        fi
      fi
      test_result "log filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=/var/run/odoo/openerp-server.pid
    TRES[6]=/var/run/odoo/odoo6-server.pid
    TRES[7]=/var/run/odoo/odoo7-server.pid
    TRES[8]=/var/run/odoo/odoo8-server.pid
    TRES[9]=/var/run/odoo/odoo9-server.pid
    TRES[10]=/var/run/odoo/odoo10.pid
    TRES[11]=/var/run/odoo/odoo11.pid
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param FPID $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param FPID $v.1)
        else
          RES=$(build_odoo_param FPID $v.0)
        fi
      fi
      test_result "pid filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=/etc/init.d/openerp-server
    TRES[6]=/etc/init.d/odoo6-server
    TRES[7]=/etc/init.d/odoo7-server
    TRES[8]=/etc/init.d/odoo8-server
    TRES[9]=/etc/init.d/odoo9-server
    TRES[10]=/etc/init.d/odoo10
    TRES[11]=/etc/init.d/odoo11
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param FULL_SVCNAME $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param FULL_SVCNAME $v.1)
        else
          RES=$(build_odoo_param FULL_SVCNAME $v.0)
        fi
      fi
      test_result "service name $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=openerp-server
    TRES[6]=odoo6-server
    TRES[7]=odoo7-server
    TRES[8]=odoo8-server
    TRES[9]=odoo9-server
    TRES[10]=odoo10
    TRES[11]=odoo11
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param SVCNAME $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param SVCNAME $v.1)
        else
          RES=$(build_odoo_param SVCNAME $v.0)
        fi
      fi
      test_result "service name $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=/opt/odoo/v7/server/openerp-server
    TRES[6]=/opt/odoo/6.1/server/openerp-server
    TRES[7]=/opt/odoo/7.0/openerp-server
    TRES[8]=/opt/odoo/8.0/openerp-server
    TRES[9]=/opt/odoo/9.0/openerp-server
    TRES[10]=/opt/odoo/10.0/odoo-bin
    TRES[11]=/opt/odoo/11.0/odoo-bin
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param BIN $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param BIN $v.1)
        else
          RES=$(build_odoo_param BIN $v.0)
        fi
      fi
      test_result "script name $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=/opt/odoo/v7
    TRES[6]=/opt/odoo/6.1
    TRES[7]=/opt/odoo/7.0
    TRES[8]=/opt/odoo/8.0
    TRES[9]=/opt/odoo/9.0
    TRES[10]=/opt/odoo/10.0
    TRES[11]=/opt/odoo/11.0
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param ROOT $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param ROOT $v.1)
        else
          RES=$(build_odoo_param ROOT $v.0)
        fi
      fi
      test_result "root dir $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=__openerp__.py
    TRES[6]=__openerp__.py
    TRES[7]=__openerp__.py
    TRES[8]=__openerp__.py
    TRES[9]=__openerp__.py
    TRES[10]=__manifest__.py
    TRES[11]=__manifest__.py
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param MANIFEST $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param MANIFEST $v.1)
        else
          RES=$(build_odoo_param MANIFEST $v.0)
        fi
      fi
      test_result "manifest $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=8069
    TRES[6]=8166
    TRES[7]=8167
    TRES[8]=8168
    TRES[9]=8169
    TRES[10]=8170
    TRES[11]=8171
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param RPCPORT $v)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param RPCPORT $v.1)
        else
          RES=$(build_odoo_param RPCPORT $v.0)
        fi
      fi
      test_result "rpcport $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[v7]=odoo
    TRES[6]=odoo6
    TRES[7]=odoo7
    TRES[8]=odoo8
    TRES[9]=odoo9
    TRES[10]=odoo10
    TRES[11]=odoo11
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "$v" == "v7" ]; then
          RES=$(build_odoo_param USER $v debug)
        elif [ $v -eq 6 ]; then
          RES=$(build_odoo_param USER $v.1 debug)
        else
          RES=$(build_odoo_param USER $v.0 debug)
        fi
      fi
      test_result "user $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[6.1]="6.1"
    TRES[7.0]="7.0"
    TRES[8.0]="8.0"
    TRES[9.0]="9.0"
    TRES[10.0]="10.0"
    TRES[11.0]="11.0"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param "FULLVER" "ODOO-$v" "debug")
      fi
      test_result "naming ODOO-$v" "${TRES[$v]}" "$RES"
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
parseoptest -l$TESTDIR/test_clodoo.log "$@" "-O"
sts=$?
if [ $sts -ne 127 ]; then
  exit $sts
fi
if [ ${opt_oelib:-0} -ne 0 ]; then
  ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $TDIR/../clodoo $TDIR/../../clodoo . .. $HOME/dev /etc")
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
