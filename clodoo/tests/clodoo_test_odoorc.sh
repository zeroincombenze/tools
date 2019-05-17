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

__version__=0.3.8.21


test_01() {
    local s sts v w
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES
    TRES[6]="6.1"
    TRES[7]="7.0"
    TRES[8]="8.0"
    TRES[9]="9.0"
    TRES[10]="10.0"
    TRES[11]="11.0"
    TRES[12]="12.0"
    for v in 6 7 8 9 10 11 12; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $v)
      fi
      test_result "full version $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      w="v$v"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="$v.1" || w="$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="v$v.1" || w="v$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="V$v.1" || w="V$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="VENV-$v.1" || w="VENV-$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="odoo-$v.1" || w="odoo-$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="ODOO-$v.1" || w="ODOO-$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param FULLVER $w)
      fi
      test_result "full version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_02() {
    local s sts v w
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES
    TRES[6.1]="6"
    TRES[7.0]="7"
    TRES[8.0]="8"
    TRES[9.0]="9"
    TRES[10.0]="10"
    TRES[11.0]="11"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param MAJVER $v)
      fi
      test_result "major version $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      w="v$v"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param MAJVER $w)
      fi
      test_result "major version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      [ "$v" == "6" ] && w="OCB-$v.1" || w="OCB-$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param MAJVER $w)
      fi
      test_result "major version $w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
    }

test_03() {
    local s sts v w
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES
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
      test_result "config unique filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param CONFN VENV-$v)
      fi
      test_result "config unique filename VENV-$v" "${TRES[$v]}" "$RES"
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
      test_result "config unique filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    export opt_mult=1
    export opt_multi=1
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
      test_result "config multi filename $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param CONFN VENV-$v)
      fi
      test_result "config multi filename VENV-$v" "${TRES[$v]}" "$RES"
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
      test_result "config multi filename $v" "${TRES[$v]}" "$RES"
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
    #
    TRES[v7]=/opt/odoo/v7/server/openerp-server
    TRES[6]=/opt/odoo/6.1/server/openerp-server
    TRES[7]=/opt/odoo/7.0/openerp-server
    TRES[8]=/opt/odoo/8.0/openerp-server
    TRES[9]=/opt/odoo/9.0/openerp-server
    TRES[10]=/opt/odoo/10.0/odoo-bin
    TRES[11]=/opt/odoo/11.0/odoo-bin
    TRES[12]=/opt/odoo/12.0/odoo-bin
    for v in 6 v7 7 8 9 10 11 12; do
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
    #
    TRES[6.1]=/opt/odoo/VENV-6.1/odoo/server/openerp-server
    TRES[7.0]=/opt/odoo/VENV-7.0/odoo/openerp-server
    TRES[8.0]=/opt/odoo/VENV-8.0/odoo/openerp-server
    TRES[9.0]=/opt/odoo/VENV-9.0/odoo/openerp-server
    TRES[10.0]=/opt/odoo/VENV-10.0/odoo/odoo-bin
    TRES[11.0]=/opt/odoo/VENV-11.0/odoo/odoo-bin
    TRES[12.0]=/opt/odoo/VENV-12.0/odoo/odoo-bin
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param BIN VENV-$v)
      fi
      test_result "script name VENV-$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[v7]=/opt/odoo/v7
    TRES[6]=/opt/odoo/6.1
    TRES[7]=/opt/odoo/7.0
    TRES[8]=/opt/odoo/8.0
    TRES[9]=/opt/odoo/9.0
    TRES[10]=/opt/odoo/10.0
    TRES[11]=/opt/odoo/11.0
    TRES[12]=/opt/odoo/12.0
    for v in 6 v7 7 8 9 10 11 12; do
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
    #
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
    #
    TRES[v7]=8069
    TRES[v8.0]=8069
    TRES[6]=8166
    TRES[7]=8167
    TRES[8]=8168
    TRES[9]=8169
    TRES[10]=8170
    TRES[11]=8171
    for v in 6 v7 v8.0 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "${v:0:1}" == "v" ]; then
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
    #
    TRES[6]=8166
    TRES[7]=8167
    TRES[8]=8168
    TRES[9]=8169
    TRES[10]=8170
    TRES[11]=8171
    for v in 6 7 8 9 10 11; do
      [ "$v" == "6" ] && w="$v.1" || w="$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param RPCPORT VENV-$w)
      fi
      test_result "rpcport VENV-$w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[v7]=odoo
    TRES[v8.0]=odoo
    TRES[6]=odoo6
    TRES[7]=odoo7
    TRES[8]=odoo8
    TRES[9]=odoo9
    TRES[10]=odoo10
    TRES[11]=odoo11
    for v in 6 v7 7 8 9 10 11; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        if [ "${v:0:1}" == "v" ]; then
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
    #
    TRES[6]=odoo6
    TRES[7]=odoo7
    TRES[8]=odoo8
    TRES[9]=odoo9
    TRES[10]=odoo10
    TRES[11]=odoo11
    for v in 6 7 8 9 10 11; do
      [ "$v" == "6" ] && w="$v.1" || w="$v.0"
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param USER VENV-$w debug)
      fi
      test_result "user VENV-$w" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="6.1"
    TRES[7.0]="7.0"
    TRES[8.0]="8.0"
    TRES[9.0]="9.0"
    TRES[10.0]="10.0"
    TRES[11.0]="11.0"
    TRES[12.0]="12.0"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param "FULLVER" "ODOO-$v" "debug")
      fi
      test_result "naming ODOO-$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_04() {
    local s sts v w
    sts=0
    export opt_mult=1
    export opt_multi=1
    declare -A TRES
    TRES[6.1]="/opt/odoo/6.1"
    TRES[v7]="/opt/odoo/v7"
    TRES[7.0]="/opt/odoo/7.0"
    TRES[v8.0]="/opt/odoo/v8.0"
    TRES[8.0]="/opt/odoo/8.0"
    TRES[9.0]="/opt/odoo/9.0"
    TRES[10.0]="/opt/odoo/10.0"
    TRES[11.0]="/opt/odoo/11.0"
    TRES[12.0]="/opt/odoo/12.0"
    for v in 6.1 v7 7.0 v8.0 8.0 9.0 10.0 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param ROOT $v "crm")
      fi
      test_result "Root $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param HOME $v "OCB")
      fi
      test_result "Home $v/OCB" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="/opt/odoo/VENV-6.1/odoo"
    TRES[7.0]="/opt/odoo/VENV-7.0/odoo"
    TRES[8.0]="/opt/odoo/VENV-8.0/odoo"
    TRES[9.0]="/opt/odoo/VENV-9.0/odoo"
    TRES[10.0]="/opt/odoo/VENV-10.0/odoo"
    TRES[11.0]="/opt/odoo/VENV-11.0/odoo"
    TRES[12.0]="/opt/odoo/VENV-12.0/odoo"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param ROOT VENV-$v "crm")
      fi
      test_result "Root VENV-$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="/opt/odoo/6.1/openerp/filestore"
    TRES[v7]="/opt/odoo/v7/openerp/filestore"
    TRES[7.0]="/opt/odoo/7.0/openerp/filestore"
    TRES[v8.0]="/opt/odoo/.local/share/Odoo"
    TRES[8.0]="/opt/odoo/.local/share/Odoo8"
    TRES[9.0]="/opt/odoo/.local/share/Odoo9"
    TRES[10.0]="/opt/odoo/.local/share/Odoo10"
    TRES[VENV-10]="/opt/odoo/VENV-10/.local/share/Odoo"
    TRES[11.0]="/opt/odoo/.local/share/Odoo11"
    TRES[12.0]="/opt/odoo/.local/share/Odoo12"
    for v in 6.1 v7 7.0 v8.0 8.0 9.0 10.0 VENV-10 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param DDIR $v)
      fi
      test_result "Filestore $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    TRES[6.1]="/opt/odoo/6.1/crm"
    TRES[v7]="/opt/odoo/v7/crm"
    TRES[7.0]="/opt/odoo/7.0/crm"
    TRES[v8.0]="/opt/odoo/v8.0/crm"
    TRES[8.0]="/opt/odoo/8.0/crm"
    TRES[9.0]="/opt/odoo/9.0/crm"
    TRES[10.0]="/opt/odoo/10.0/crm"
    TRES[11.0]="/opt/odoo/11.0/crm"
    TRES[12.0]="/opt/odoo/12.0/crm"
    for v in 6.1 v7 7.0 v8.0 8.0 9.0 10.0 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param HOME $v "crm")
      fi
      test_result "Home $v/crm" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="/opt/odoo/VENV-6.1/odoo/crm"
    TRES[7.0]="/opt/odoo/VENV-7.0/odoo/crm"
    TRES[8.0]="/opt/odoo/VENV-8.0/odoo/crm"
    TRES[9.0]="/opt/odoo/VENV-9.0/odoo/crm"
    TRES[10.0]="/opt/odoo/VENV-10.0/odoo/crm"
    TRES[11.0]="/opt/odoo/VENV-11.0/odoo/crm"
    TRES[12.0]="/opt/odoo/VENV-12.0/odoo/crm"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param HOME VENV-$v "crm")
      fi
      test_result "Home VENV-$v/crm" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
    }

test_05() {
    local s sts v w
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES
    z="OCB"
    TRES[zero-git]="git@github.com:zeroincombenze/$z"
    TRES[zero-http]="https://github.com/zeroincombenze/$z"
    TRES[oca]="https://github.com/OCA/$z"
    TRES[oia-git]="git@github.com:Odoo-Italia-Associazione/$z"
    TRES[oia-http]="https://github.com/Odoo-Italia-Associazione/$z"
    TRES[librerp]="https://github.com/iw3hxn/server"
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      TRES[zero]=${TRES[zero-git]}
      TRES[oia]=${TRES[oia-http]}
    else
      TRES[zero]=${TRES[zero-http]}
      TRES[oia]=${TRES[oia-http]}
    fi
    for w in zero zero-git zero-http oca oia oia-git oia-http librerp; do
      for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param URL $v $z $w)
        fi
        test_result "URL $w/$z $v" "${TRES[$w]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        #
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param GIT_URL $v $z $w)
        fi
        test_result "GIT_URL $w/$z $v" "${TRES[$w]}.git" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        #
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param URL_BRANCH $v $z $w)
        fi
        test_result "URL_BRANCH $w/$z $v" "${TRES[$w]}/tree/$v" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
      done
    done
    #
    TRES[zero-git]="git@github.com:zeroincombenze"
    TRES[zero-http]="https://github.com/zeroincombenze"
    TRES[oca]="https://github.com/OCA"
    TRES[oia-git]="git@github.com:Odoo-Italia-Associazione"
    TRES[oia-http]="https://github.com/Odoo-Italia-Associazione"
    TRES[librerp]="https://github.com/iw3hxn"
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      TRES[zero]=${TRES[zero-git]}
      TRES[oia]=${TRES[oia-http]}
    else
      TRES[zero]=${TRES[zero-http]}
      TRES[oia]=${TRES[oia-http]}
    fi
    for w in zero zero-git zero-http oca oia oia-git oia-http librerp; do
      for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param GIT_ORG $v $z $w)
        fi
        test_result "GIT_ORG $w/$z $v" "${TRES[$w]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
      done
    done
    #
    TRES[zero]="https://github.com/OCA/$z"
    TRES[zero-git]="https://github.com/OCA/$z"
    TRES[zero-http]="https://github.com/OCA/$z"
    TRES[oca]="https://github.com/OCA/$z"
    TRES[oia]="https://github.com/OCA/$z"
    TRES[oia-git]="https://github.com/OCA/$z"
    TRES[oia-http]="https://github.com/OCA/$z"
    TRES[librerp]="https://github.com/iw3hxn/$z"
    for w in zero zero-git zero-http oca oia oia-git oia-http librerp; do
      for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param UPSTREAM $v $z $w)
        fi
        if [ "$v" == "6.1" -o "$w" == "oca" -o "$w" == "librerp" ]; then
          test_result "UPSTREAM $w/$z $v" "" "$RES"
          s=$?; [ ${s-0} -ne 0 ] && sts=$s
        else
          test_result "UPSTREAM $w/$z $v" "${TRES[$w]}.git" "$RES"
          s=$?; [ ${s-0} -ne 0 ] && sts=$s
        fi
      done
    done


    #
    for v in 12.0 11.0 10.0 8.0 7.0; do
      w=$(echo $v|grep -Eo "[0-9]+"|head -n1)
      # TO FIX HOME
      # TRES[zero]="$HOME/zero$w"
      # TRES[zero-git]="$HOME/zero$w"
      # TRES[zero-http]="$HOME/zero$w"
      # TRES[oca]="$HOME/oca$w"
      # TRES[oia]="$HOME/oia$w"
      # TRES[oia-git]="$HOME/oia$w"
      # TRES[oia-http]="$HOME/oia$w"
      TRES[zero]="$RHOME/zero$w"
      TRES[zero-git]="$RHOME/zero$w"
      TRES[zero-http]="$RHOME/zero$w"
      TRES[oca]="$RHOME/oca$w"
      TRES[oia]="$RHOME/oia$w"
      TRES[oia-git]="$RHOME/oia$w"
      TRES[oia-http]="$RHOME/oia$w"
      for w in zero zero-git zero-http oca oia oia-git oia-http; do
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param HOME $v '' $w)
        fi
        test_result "HOME $v $w" "${TRES[$w]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
      done
    done

    return $sts
    }

test_06() {
    local s sts v w x
    sts=0
    export opt_mult=1
    export opt_multi=1
    declare -A TRES
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 librerp6 oca7 oca8 oca10; do
        pushd $RHOME/$v >/dev/null
        RES=$(build_odoo_param HOME '.')
        test_result "HOME ./$v" "$PWD" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        #
        w=$(echo $v|grep -Eo "[0-9]+"|head -n1)
        if [ "$w" == "6" ]; then
          w="$w.1"
        else
          w="$w.0"
        fi
        RES=$(build_odoo_param FULLVER '.')
        test_result "Full version ./$v" "$w" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        #
        w=$(echo $v|grep -Eo "[0-9]+"|head -n1)
        if [[ "10.0 11.0 12.0" =~ "$v" ]]; then
          w="/etc/odoo/odoo${w}.conf"
        elif [[ "6.1 7.0 8.0 9.0" =~ "$v" ]]; then
          w="/etc/odoo/odoo${w}-server.conf"
        elif [[ "${v:0:3}" == "oca" ]]; then
          w="/etc/odoo/odoo${w}-oca.conf"
        elif [[ "${v:0:3}" == "oia" ]]; then
          w="/etc/odoo/odoo${w}-oia.conf"
        elif [[ "${v:0:7}" == "librerp" ]]; then
          w="/etc/odoo/odoo${w}-librerp.conf"
        else
          w=
        fi
        RES=$(build_odoo_param CONFN $v)
        test_result "Configuration file ./$v" "$w" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        popd >/dev/null
        # [ ${opt_dry_run:-0} -eq 0 ] && set -x   #debug
        if [ "${v:0:3}" != "oia" ]; then
          x=$(readlink -f $RHOME/$v)
          RES=$(build_odoo_param HOME $RHOME/$v)
          test_result "HOME $RHOME/$v" "$x" "$RES"
          RES=$(build_odoo_param HOME $RHOME/$v/addons)
          test_result "HOME $RHOME/$v/addons" "$x" "$RES"
          RES=$(build_odoo_param HOME "$x")
          test_result "HOME $x" "$x" "$RES"
          RES=$(build_odoo_param HOME "$x/addons")
          test_result "HOME $x/addons" "$x" "$RES"
        fi
      done
    fi
    return $sts
}

test_07() {
    local s sts v w x
    sts=0
    export opt_mult=1
    export opt_multi=1
    declare -A TRES
    #
    pushd $LCL_OE_PKGPATH >/dev/null
    RES=$(build_odoo_param PKGPATH '.')
    test_result "Test Odoo PKGPATH" "$LCL_OE_PKGPATH" "$RES"
    RES=$(build_odoo_param ROOT '.')
    test_result "Test Odoo ROOT" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param HOME '.')
    test_result "Test Odoo HOME" "$LCL_OE_PRJPATH" "$RES"
    RES=$(build_odoo_param PARENTDIR '.')
    test_result "Test Odoo PARENTDIR" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "$LCL_OO_REPOS" "$RES"
    RES=$(build_odoo_param RORIGIN '.' default)
    test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/l10n_italy.git" "$RES"
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/l10n_italy.git" "$RES"
    popd >/dev/null
    #
    pushd $LCL_OE_PRJPATH >/dev/null
    RES=$(build_odoo_param PKGPATH '.')
    test_result "Test Odoo PKGPATH" "" "$RES"
    RES=$(build_odoo_param ROOT '.')
    test_result "Test Odoo ROOT" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param HOME '.')
    test_result "Test Odoo HOME" "$LCL_OE_PRJPATH" "$RES"
    RES=$(build_odoo_param PARENTDIR '.')
    test_result "Test Odoo PARENTDIR" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "$LCL_OO_REPOS" "$RES"
    RES=$(build_odoo_param RORIGIN '.' default)
    test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/l10n_italy.git" "$RES"
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/l10n_italy.git" "$RES"
    popd >/dev/null
    #
    pushd $LCL_OE_ROOT >/dev/null
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "OCB" "$RES"
    RES=$(build_odoo_param RORIGIN '.' default)
    test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/OCB.git" "$RES"
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/OCB.git" "$RES"
    popd >/dev/null
    #
    pushd $LCL_VE_PKGPATH >/dev/null
    RES=$(build_odoo_param PKGPATH '.')
    test_result "Test Odoo PKGPATH" "$LCL_VE_PKGPATH" "$RES"
    RES=$(build_odoo_param ROOT '.')
    test_result "Test Odoo ROOT" "$LCL_VE_ROOT" "$RES"
    RES=$(build_odoo_param HOME '.')
    test_result "Test Odoo HOME" "$LCL_VE_PRJPATH" "$RES"
    RES=$(build_odoo_param PARENTDIR '.')
    test_result "Test Odoo PARENTDIR" "$LCL_VE_ROOT" "$RES"
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "$LCL_OO_REPOS" "$RES"
    RES=$(build_odoo_param RORIGIN '.' default)
    test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/l10n_italy.git" "$RES"
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/l10n_italy.git" "$RES"
    popd >/dev/null
    #
    return $sts
}

test_08() {
    local s sts v w
    sts=0
    export opt_mult=1
    export opt_multi=1
    local TRES="OCB account-analytic account_banking_cscs account-budgeting\
 account-closing account-consolidation account-financial-reporting\
 account-financial-tools account-fiscal-rule account_invoice_create_payment\
 account-invoice-reporting account-invoicing account-payment\
 account_payment_approve_invoice account-reconcile ansible-odoo apps-store\
 bank-payment bank-statement-import bank-statement-reconcile\
 business-requirement calendar commission community-data-files connector\
 connector-accountedge connector-cmis connector-ecommerce connector-infor\
 connector-interfaces connector-lengow connector-lims connector-magento\
 connector-magento-php-extension connector-odoo2odoo connector-prestashop\
 connector-redmine connector-sage connector-salesforce connector-telephony\
 connector-woocommerce contract crm cscs_addons currency ddmrp\
 delivery-carrier donation dotnet e-commerce edi event geospatial\
 hr hr-timesheet infrastructure-dns interface-github intrastat knowledge\
 l10n-italy l10n-italy-supplemental maintainer-quality-tools\
 maintainer-tools maintenance management-system manufacture\
 manufacture-reporting margin-analysis margin-analysis mis-builder\
 multi-company oca-custom oca-decorators odoorpc odoo-sentinel\
 odoo-sphinx-autodoc OpenUpgrade openupgradelib operating-unit\
 partner-contact pos product-attribute product-kitting product-variant\
 project project-agile project-reporting purchase-reporting\
 purchase-workflow pylint-odoo queue reporting-engine report-print-send\
 rma runbot-addons sale-financial sale-reporting sale-workflow server-auth\
 server-backend server-brand server-env server-tools server-ux social\
 stock-logistics-barcode stock-logistics-reporting stock-logistics-tracking\
 stock-logistics-transport stock-logistics-warehouse\
 stock-logistics-workflow survey user_contributes vertical-abbey\
 vertical-agriculture vertical-association vertical-community\
 vertical-construction vertical-edition vertical-education vertical-hotel\
 vertical-isp vertical-medical vertical-ngo vertical-realestate\
 vertical-travel web webhook webkit-tools website website-cms\
 website-themes zeroincombenze"
    local RES=$(module_list "7.0")
    test_result "Module list 7.0" "$TRES" "$RES"

    TRES="OCB account-analytic account_banking_cscs account-budgeting\
 account-closing account-consolidation account-financial-reporting\
 account-financial-tools account-fiscal-rule account_invoice_create_payment\
 account-invoice-reporting account-invoicing account-payment\
 account_payment_approve_invoice account-reconcile ansible-odoo apps-store\
 bank-payment bank-statement-import bank-statement-reconcile\
 business-requirement calendar commission community-data-files connector\
 connector-accountedge connector-cmis connector-ecommerce connector-infor\
 connector-interfaces connector-lengow connector-lims connector-magento\
 connector-magento-php-extension connector-odoo2odoo connector-prestashop\
 connector-redmine connector-sage connector-salesforce connector-telephony\
 connector-woocommerce contract crm cscs_addons currency ddmrp delivery-carrier\
 donation dotnet e-commerce edi event geospatial hr hr-timesheet\
 infrastructure-dns interface-github intrastat knowledge l10n-italy\
 l10n-italy-supplemental maintainer-quality-tools maintainer-tools\
 maintenance management-system manufacture manufacture-reporting\
 margin-analysis margin-analysis mis-builder multi-company oca-custom\
 oca-decorators odoorpc odoo-sentinel odoo-sphinx-autodoc OpenUpgrade\
 openupgradelib operating-unit partner-contact pos product-attribute\
 product-kitting product-variant project project-agile\
 project-reporting purchase-reporting purchase-workflow pylint-odoo queue\
 reporting-engine report-print-send rma runbot-addons sale-financial\
 sale-reporting sale-workflow server-auth server-backend server-brand\
 server-env server-tools server-ux social stock-logistics-barcode\
 stock-logistics-reporting stock-logistics-tracking stock-logistics-transport\
 stock-logistics-warehouse stock-logistics-workflow survey user_contributes\
 vertical-abbey vertical-agriculture vertical-association vertical-community\
 vertical-construction vertical-edition vertical-education\
 vertical-hotel vertical-isp vertical-medical vertical-ngo vertical-realestate\
 vertical-travel web webhook webkit-tools website website-cms website-themes\
 zeroincombenze"
    local RES=$(module_list "8.0")
    test_result "Module list 8.0" "$TRES" "$RES"

    TRES="bank-payment l10n-italy user_contributes"
    local RES=$(module_list "7.0" "" "oia")
    test_result "Module list 7.0" "$TRES" "$RES"
}


Z0BUG_setup() {
# Modules Tree for tests
# l10n-italy/l10n_it_base
# addons/web
#   |---- addons/account
#   |---- addons/base   
#   |---- addons/sale
#   \---- addons/web
# unported/l10n_it_base

    local VERSION=9.0
    local ODOO_REPO=local/odoo
    RHOME="/opt/odoo"
    LCL_OO_PRJNAME="Odoo"
    LCL_OO_REPOS=l10n_italy
    LCL_OO_PKGNAME=l10n_it_base
    LCL_OE_ROOT=$RHOME/dev/odoo/$VERSION
    LCL_OE_PRJPATH=$LCL_OE_ROOT/$LCL_OO_REPOS
    LCL_OE_PKGPATH=$LCL_OE_PRJPATH/$LCL_OO_PKGNAME
    LCL_OE_PKGPATH2=$LCL_OE_ROOT/__unported__/$LCL_OO_PKGNAME
    [ -f $LCL_OE_ROOT ] && rm -fR $LCL_OE_ROOT
    mkdir -p $LCL_OE_ROOT
    mkdir -p $LCL_OE_ROOT/openerp
    touch $LCL_OE_ROOT/openerp-server
    mkdir -p $LCL_OE_ROOT/addons
    mkdir -p $LCL_OE_ROOT/addons/base
    mkdir -p $LCL_OE_ROOT/addons/account
    mkdir -p $LCL_OE_ROOT/addons/sale
    mkdir -p $LCL_OE_ROOT/addons/web
    mkdir -p $LCL_OE_PRJPATH
    mkdir -p $LCL_OE_PKGPATH
    mkdir -p $LCL_OE_PKGPATH2
    touch $LCL_OE_PKGPATH/__openerp__.py
    touch $LCL_OE_PKGPATH2/__openerp__.py
    LCL_OO_SETUP=__openerp__.py
    LCLTEST_MQT_PATH=$HOME/maintainer-quality-tools/travis
    if [ ! -f /etc/odoo/odoo9-server.conf ]; then
      LCLTEST_ODOO9_SERVER=/etc/odoo/odoo9-server.conf
      touch $LCLTEST_ODOO9_SERVER
    fi
    if [ -d $RHOME/$VERSION/dependencies ]; then rm -fR $RHOME/$VERSION/dependencies; fi
    if [ -L $RHOME/$VERSION/dependencies ]; then rm -f $RHOME/$VERSION/dependencies; fi

    LCL_VE_ROOT=$RHOME/dev/odoo/VENV-$VERSION/odoo
    LCL_VE_PRJPATH=$LCL_VE_ROOT/$LCL_OO_REPOS
    LCL_VE_PKGPATH=$LCL_VE_PRJPATH/$LCL_OO_PKGNAME
    LCL_VE_PKGPATH2=$LCL_VE_PRJPATH/__unported__/$LCL_OO_PKGNAME
    mkdir -p $RHOME/dev/odoo/VENV-$VERSION
    mkdir -p $LCL_VE_ROOT
    mkdir -p $LCL_VE_ROOT/openerp
    touch $LCL_VE_ROOT/openerp-server
    mkdir -p $LCL_VE_ROOT/addons
    mkdir -p $LCL_VE_ROOT/addons/base
    mkdir -p $LCL_VE_ROOT/addons/account
    mkdir -p $LCL_VE_ROOT/addons/sale
    mkdir -p $LCL_VE_ROOT/addons/web
    mkdir -p $LCL_VE_PRJPATH
    mkdir -p $LCL_VE_PKGPATH
    mkdir -p $LCL_VE_PKGPATH2
    touch $LCL_VE_PKGPATH/__openerp__.py
    touch $LCL_VE_PKGPATH2/__openerp__.py
}

Z0BUG_teardown() {
    mkdir -p $LCL_VE_PKGPATH2
    mkdir -p $LCL_VE_PKGPATH
    mkdir -p $LCL_VE_PRJPATH
    mkdir -p $LCL_VE_ROOT
    mkdir -p $RHOME/dev/odoo/VENV-$VERSION
    rm -fR $LCL_OE_PKGPATH2
    rm -fR $LCL_OE_PKGPATH
    rm -fR $LCL_OE_PRJPATH
    rm -fR $LCL_OE_ROOT
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
