#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
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

# DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
# TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.9


test_01() {
    local k v RES sts=0
    declare -A TRES
    TRES[6.1]="Sales Management"
    TRES[7.0]="Sales"
    TRES[8.0]="Sales"
    TRES[9.0]="Sales"
    TRES[10.0]="Sales"
    TRES[11.0]="Sales"
    TRES[12.0]="Sales"
    TRES[13.0]="Sales"
    TRES[14.0]="Sales"
    TRES[15.0]="Sales"
    TRES[16.0]="Sales"

    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m res.groups -s SALES -b$v)
      test_result "translate -m res.groups -s SALES -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    k="name"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m res.groups -k "$k" -s "Sales" -f 7.0 -b$v)
      test_result "translate -m res.groups -k "$k" -s "Sales" -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_02() {
    local k v RES sts=0
    declare -A TRES
    TRES[6.1]="report_type"
    TRES[7.0]="report_type"
    TRES[8.0]="report_type"
    TRES[9.0]="type"
    TRES[10.0]="type"
    TRES[11.0]="type"
    TRES[12.0]="type"
    TRES[13.0]="type"
    TRES[14.0]="type"
    TRES[15.0]="type"
    TRES[16.0]="type"
    #
    k="report_type"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -s "$k" -f 7.0 -b$v)
      test_result "translate -m account.account.type -s "$k" -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    k="type"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -s "$k" -f 10.0 -b$v)
      test_result "translate -m account.account.type -s "$k" -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_03() {
    local k m v RES sts=0
    declare -A TRES
    TRES[6.1]="action_cancel"
    TRES[7.0]="action_cancel"
    TRES[8.0]="action_cancel"
    TRES[9.0]="action_cancel"
    TRES[10.0]="action_invoice_cancel"
    TRES[11.0]="action_invoice_cancel"
    TRES[12.0]="action_invoice_cancel"
    TRES[13.0]="button_cancel"
    TRES[14.0]="button_cancel"
    TRES[15.0]="button_cancel"
    TRES[16.0]="button_cancel"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      # [[ $v =~ (13|14) ]] && m="account.move" || m="account.invoice"
      m="account.invoice"
      RES=$($RUNDIR/transodoo.py translate -m $m -k action -s action_cancel -f 7.0 -b$v)
      test_result "translate -m $m -k action -s action_cancel -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s action_invoice_cancel -f 10.0 -b$v)
      test_result "translate -m account.invoice -k action -s action_invoice_cancel -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_04() {
    local k v RES sts=0
    declare -A TRES
    TRES[6.1]="invoice_cancel_draft"
    TRES[7.0]="invoice_cancel_draft"
    TRES[8.0]="invoice_cancel_draft"
    TRES[9.0]="invoice_cancel_draft"
    TRES[10.0]="action_invoice_draft"
    TRES[11.0]="action_invoice_draft"
    TRES[12.0]="action_invoice_draft"
    TRES[13.0]="None"
    TRES[14.0]="None"
    TRES[15.0]="None"
    TRES[16.0]="None"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s invoice_cancel_draft -f 7.0 -b$v)
      test_result "translate translate -m account.invoice -k action -s invoice_cancel_draft -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s action_invoice_draft -f 12.0 -b$v)
      test_result "translate -m account.invoice -k action -s action_invoice_draft -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_05() {
    local k v RES sts=0
    declare -A TRES
    TRES[6.1]="asset"
    TRES[7.0]="asset"
    TRES[8.0]="asset"
    TRES[9.0]="['liquidity', 'other', 'receivable']"
    TRES[10.0]="['liquidity', 'other', 'receivable']"
    TRES[11.0]="['liquidity', 'other', 'receivable']"
    TRES[12.0]="['liquidity', 'other', 'receivable']"
    TRES[13.0]="['liquidity', 'other', 'receivable']"
    TRES[14.0]="['liquidity', 'other', 'receivable']"
    TRES[15.0]="['liquidity', 'other', 'receivable']"
    TRES[16.0]="['liquidity', 'other', 'receivable']"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -k value -N report_type -s asset -f 7.0 -b$v)
      test_result "translate -m account.account.type -k value -N report_type -s asset -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="asset"
    TRES[7.0]="asset"
    TRES[8.0]="asset"
    TRES[9.0]="receivable"
    TRES[10.0]="receivable"
    TRES[11.0]="receivable"
    TRES[12.0]="receivable"
    TRES[13.0]="receivable"
    TRES[14.0]="receivable"
    TRES[15.0]="receivable"
    TRES[16.0]="receivable"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -k value -N type -s receivable -f 10.0 -b$v)
      test_result "translate -m account.account.type -k value -N type -s receivable -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="Asset"
    TRES[7.0]="Asset"
    TRES[8.0]="Asset"
    TRES[9.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[10.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[11.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[12.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[13.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[14.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[15.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    TRES[16.0]="['Current Assets', 'Fixed Assets', 'Prepayments']"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -k value -N name -s Asset -f 7.0 -b$v)
      test_result "translate -m account.account.type -k value -N name -s Asset -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -k valuetnl -N name -f 7.0 -b$v)
      test_result "translate -m account.account.type -k valuetnl -N name -f 7.0 -b$v" "1" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -k valuetnl -N note -f 7.0 -b$v)
      test_result "translate -m account.account.type -k valuetnl -N note -f 7.0 -b$v" "" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="product.product_uom_unit"
    TRES[7.0]="product.product_uom_unit"
    TRES[8.0]="product.product_uom_unit"
    TRES[9.0]="product.product_uom_unit"
    TRES[10.0]="product.product_uom_unit"
    TRES[11.0]="product.product_uom_unit"
    TRES[12.0]="uom.product_uom_unit"
    TRES[13.0]="uom.product_uom_unit"
    TRES[14.0]="uom.product_uom_unit"
    TRES[15.0]="uom.product_uom_unit"
    TRES[16.0]="uom.product_uom_unit"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.module.data -k xref -s product.product_uom_unit -f 10.0 -b$v)
      test_result "translate -m ir.module.data -k xref -s product.product_uom_unit -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      #
      RES=$($RUNDIR/transodoo.py translate -m "" -k xref -s uom.product_uom_unit -f 12.0 -b$v)
      test_result "translate -m '' -k xref -s uom.product_uom_unit -f 12.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    return $sts
}

test_06() {
    local k v RES sts=0
    declare -A TRES
    TRES[6.1]="0.22"
    TRES[7.0]="0.22"
    TRES[8.0]="0.22"
    TRES[9.0]="22.0"
    TRES[10.0]="22.0"
    TRES[11.0]="22.0"
    TRES[12.0]="22.0"
    TRES[13.0]="22.0"
    TRES[14.0]="22.0"
    TRES[15.0]="22.0"
    TRES[16.0]="22.0"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.tax -k value -N amount -s 0.22 -f 7.0 -b$v)
      test_result "translate -m account.tax -k value -N amount -s 0.22 -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.tax -k value -N amount -s 22 -f 10.0 -b$v)
      test_result "translate -m account.tax -k value -N amount -s 22 -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="progress"
    TRES[7.0]="progress"
    TRES[8.0]="progress"
    TRES[9.0]="sale"
    TRES[10.0]="sale"
    TRES[11.0]="sale"
    TRES[12.0]="sale"
    TRES[13.0]="sale"
    TRES[14.0]="sale"
    TRES[15.0]="sale"
    TRES[16.0]="sale"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m sale.order -k value -N state -s progress -f 7.0 -b$v)
      test_result "translate -m sale.order -k value -N state -s progress -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="manual"
    TRES[7.0]="manual"
    TRES[8.0]="manual"
    TRES[9.0]="sale"
    TRES[10.0]="sale"
    TRES[11.0]="sale"
    TRES[12.0]="sale"
    TRES[13.0]="sale"
    TRES[14.0]="sale"
    TRES[15.0]="sale"
    TRES[16.0]="sale"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m sale.order -k value -N state -s manual -f 7.0 -b$v)
      test_result "translate translate -m sale.order -k value -N state -s manual -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_07() {
    local k m v RES sts=0
    declare -A TRES
    TRES[6.1]="account_payment"
    TRES[7.0]="account_payment"
    TRES[8.0]="account_payment"
    TRES[9.0]="account_payment_order"
    TRES[10.0]="account_payment_order"
    TRES[11.0]="account_payment_order"
    TRES[12.0]="account_payment_order"
    TRES[13.0]="account_payment_order"
    TRES[14.0]="account_payment_order"
    TRES[15.0]="account_payment_order"
    TRES[16.0]="account_payment_order"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.module.module -k module -s account_payment -f 7.0 -b$v)
      test_result "translate -m ir.module.module -k module -s account_payment -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m "" -k module -s account_payment_order -f 10.0 -b$v)
      test_result "translate -m '' -k module -s account_payment_order -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="account_financial_report_webkit_xls"
    TRES[7.0]="account_financial_report_webkit_xls"
    TRES[8.0]="account_financial_report_webkit_xls"
    TRES[9.0]="account_financial_report_qweb"
    TRES[10.0]="account_financial_report_qweb"
    TRES[11.0]="account_financial_report_qweb"
    TRES[12.0]="account_financial_report"
    TRES[13.0]="account_financial_report"
    TRES[14.0]="account_financial_report"
    TRES[15.0]="account_financial_report"
    TRES[16.0]="account_financial_report"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.module.module -k merge -s account_financial_report_webkit_xls -f 7.0 -b$v)
      test_result "translate -m ir.module.module -k merge -s account_financial_report_webkit_xls -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="['account_financial_report_qweb', 'account_financial_report_webkit_xls', 'account_journal_report']"
    TRES[7.0]="['account_financial_report_qweb', 'account_financial_report_webkit_xls', 'account_journal_report']"
    TRES[8.0]="['account_financial_report_qweb', 'account_financial_report_webkit_xls', 'account_journal_report']"
    TRES[9.0]="['account_financial_report_qweb', 'account_journal_report']"
    TRES[10.0]="account_financial_report_qweb"
    TRES[11.0]="account_financial_report_qweb"
    TRES[12.0]="['account_financial_report', 'account_financial_report_qweb']"
    TRES[13.0]="['account_financial_report', 'account_financial_report_qweb']"
    TRES[14.0]="['account_financial_report', 'account_financial_report_qweb']"
    TRES[15.0]="['account_financial_report', 'account_financial_report_qweb']"
    TRES[16.0]="['account_financial_report', 'account_financial_report_qweb']"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.module.module -k merge -s account_financial_report_qweb -f 10.0 -b$v)
      test_result "translate -m ir.module.module -k merge -s account_financial_report_qweb -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="None"
    TRES[7.0]="None"
    TRES[8.0]="None"
    TRES[9.0]="None"
    TRES[10.0]="None"
    TRES[11.0]="None"
    TRES[12.0]="l10n_it_vat_statement_split_payment"
    TRES[13.0]="l10n_it_vat_statement_split_payment"
    TRES[14.0]="l10n_it_vat_statement_split_payment"
    TRES[15.0]="l10n_it_vat_statement_split_payment"
    TRES[16.0]="l10n_it_vat_statement_split_payment"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      m=$(echo $v|grep --color=never -Eo '[0-9]+'|head -n1)
      RES=$($RUNDIR/transodoo.py translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -b$v)
      test_result "translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      RES=$($RUNDIR/transodoo.py translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -bzero$m)
      test_result "translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -bzero$m" "None" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      [[ $m -lt 12 ]] && continue
      [[ $v =~ (6.1|12.0) ]] || continue
      RES=$($RUNDIR/transodoo.py translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -blibrerp$m)
      test_result "translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -blibrerp$m" "None" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    return $sts
}

test_08() {
    local k m v RES sts=0
    declare -A TRES
    TRES[6.1]="product.uom"
    TRES[7.0]="product.uom"
    TRES[8.0]="product.uom"
    TRES[9.0]="product.uom"
    TRES[10.0]="product.uom"
    TRES[11.0]="product.uom"
    TRES[12.0]="uom.uom"
    TRES[13.0]="uom.uom"
    TRES[14.0]="uom.uom"
    TRES[15.0]="uom.uom"
    TRES[16.0]="uom.uom"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.model -k model -s product.uom -f 7.0 -b$v)
      test_result "translate -m ir.model -k model -s product.uom -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -k model -s product.uom -f 7.0 -b$v)
      test_result "translate -k model -s product.uom -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -k model -s uom.uom -f 12.0 -b$v)
      test_result "translate -k model -s uom.uom -f 12.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done

    TRES[6.1]="account.invoice"
    TRES[7.0]="account.invoice"
    TRES[8.0]="account.invoice"
    TRES[9.0]="account.invoice"
    TRES[10.0]="account.invoice"
    TRES[11.0]="account.invoice"
    TRES[12.0]="account.invoice"
    TRES[13.0]="account.move"
    TRES[14.0]="account.move"
    TRES[15.0]="account.move"
    TRES[16.0]="account.move"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0  15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.model -k model -s account.invoice -f 7.0 -b$v)
      test_result "translate -m ir.model -k model -s account.invoice -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s

      RES=$($RUNDIR/transodoo.py translate -m ir.model -k model -s account.invoice -f zero7 -b$v)
      test_result "translate -m ir.model -k model -s account.invoice -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -k model -s account.invoice -f 7.0 -b$v)
      test_result "translate -k model -s account.invoice -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="['account.move', 'account.invoice']"
    TRES[7.0]="['account.move', 'account.invoice']"
    TRES[8.0]="['account.move', 'account.invoice']"
    TRES[9.0]="['account.move', 'account.invoice']"
    TRES[10.0]="['account.move', 'account.invoice']"
    TRES[11.0]="['account.move', 'account.invoice']"
    TRES[12.0]="['account.move', 'account.invoice']"
    TRES[13.0]="account.move"
    TRES[14.0]="account.move"
    TRES[15.0]="account.move"
    TRES[16.0]="account.move"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0  15.0 16.0; do
      RES=$($RUNDIR/transodoo.py translate -k model -s account.move -f 14.0 -b$v)
      test_result "translate -k model -s account.move -f 14.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done

    return $sts
}

test_09() {
    local k RES sts=0
    declare -A TRES
    TRES[1205]="123380"
    TRES[1601]="153010"
    TRES[2601]="260010"
    TRES[3112]="510000"
    for k in "1205" "1601" "2601" "3112"; do
      RES=$($RUNDIR/transodoo.py translate -kvalue -maccount.account -Ncode -f12.0 -blibrerp12 -s $k)
      test_result "transodoo.py translate -kvalue -maccount.account -Ncode -f12.0 -blibrerp12 -s $k" "${TRES[$k]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[123380]="1205"
    TRES[153010]="1601"
    TRES[260010]="2601"
    TRES[510000]="3112"
    for k in "123380" "153010" "260010" "510000"; do
      RES=$($RUNDIR/transodoo.py translate -kvalue -maccount.account -Ncode -flibrerp12 -b12.0 -s $k)
      test_result "transodoo.py translate -kvalue -maccount.account -Ncode -flibrerp12 -b12.0 -s $k" "${TRES[$k]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
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
UT_LIST=
[[ "$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
[[ "$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit $sts


