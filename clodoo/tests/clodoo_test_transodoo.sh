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

__version__=0.3.34.4


test_01() {
    local k v RES
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m res.groups -s SALES -b$v)
      test_result "translate -m res.groups -s SALES -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    k="name"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m res.groups -k "$k" -s "Sales" -f 7.0 -b$v)
      test_result "translate -m res.groups -k "$k" -s "Sales" -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
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
    TRES[12.0]="type"
    TRES[13.0]="type"
    TRES[14.0]="type"
    #
    k="report_type"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -s "$k" -f 7.0 -b$v)
      test_result "translate -m account.account.type -s "$k" -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    k="type"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -s "$k" -f 10.0 -b$v)
      test_result "translate -m account.account.type -s "$k" -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_03() {
    local k v RES
    declare -A TRES
    TRES[6.1]="action_cancel"
    TRES[7.0]="action_cancel"
    TRES[8.0]="action_cancel"
    TRES[9.0]="action_cancel"
    TRES[10.0]="action_invoice_cancel"
    TRES[11.0]="action_invoice_cancel"
    TRES[12.0]="action_invoice_cancel"
    TRES[13.0]="action_invoice_cancel"
    TRES[14.0]="action_invoice_cancel"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s action_cancel -f 7.0 -b$v)
      test_result "translate -m account.invoice -k action -s action_cancel -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s action_invoice_cancel -f 10.0 -b$v)
      test_result "translate -m account.invoice -k action -s action_invoice_cancel -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_04() {
    local k v RES
    declare -A TRES
    TRES[6.1]="invoice_cancel_draft"
    TRES[7.0]="invoice_cancel_draft"
    TRES[8.0]="invoice_cancel_draft"
    TRES[9.0]="invoice_cancel_draft"
    TRES[10.0]="action_invoice_draft"
    TRES[11.0]="action_invoice_draft"
    TRES[12.0]="action_invoice_draft"
    TRES[13.0]="action_invoice_draft"
    TRES[14.0]="action_invoice_draft"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s invoice_cancel_draft -f 7.0 -b$v)
      test_result "translate translate -m account.invoice -k action -s invoice_cancel_draft -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.invoice -k action -s action_invoice_draft -f 10.0 -b$v)
      test_result "translate -m account.invoice -k action -s action_invoice_draft -f 10.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_05() {
    local k v RES
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.account.type -k value -N name -s Asset -f 7.0 -b$v)
      test_result "translate -m account.account.type -k value -N name -s Asset -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    local k v RES
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m account.tax -k value -N amount -s 0.22 -f 7.0 -b$v)
      test_result "translate -m account.tax -k value -N amount -s 0.22 -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m sale.order -k value -N state -s manual -f 7.0 -b$v)
      test_result "translate translate -m sale.order -k value -N state -s manual -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_07() {
    local k m v RES
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.module.module -k module -s account_payment -f 7.0 -b$v)
      test_result "translate -m ir.module.module -k module -s account_payment -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      RES=$($RUNDIR/transodoo.py translate -m ir.module.module -k merge -s account_financial_report_webkit_xls -f 7.0 -b$v)
      test_result "translate -m ir.module.module -k merge -s account_financial_report_webkit_xls -f 7.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    TRES[6.1]="['account_financial_report_webkit_xls', 'account_journal_report']"
    TRES[7.0]="['account_financial_report_webkit_xls', 'account_journal_report']"
    TRES[8.0]="['account_financial_report_webkit_xls', 'account_journal_report']"
    TRES[9.0]="['account_financial_report_qweb', 'account_journal_report']"
    TRES[10.0]="account_financial_report_qweb"
    TRES[11.0]="account_financial_report_qweb"
    TRES[12.0]="['account_financial_report', 'account_financial_report_qweb']"
    TRES[13.0]="['account_financial_report', 'account_financial_report_qweb']"
    TRES[14.0]="['account_financial_report', 'account_financial_report_qweb']"
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
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
    #
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0; do
      m=$(echo $v|grep -Eo [0-9]+|head -n1)
      RES=$($RUNDIR/transodoo.py translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -b$v)
      test_result "translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -b$v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      RES=$($RUNDIR/transodoo.py translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -bzero$m)
      test_result "translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -bzero$m" "None" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      [[ $m -lt 12 ]] && continue
      RES=$($RUNDIR/transodoo.py translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -bpowerp$m)
      test_result "translate -k module -s l10n_it_vat_statement_split_payment -f 12.0 -bpowerp$m" "None" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    #
    return $sts
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
[[ $sts -ne 127 ]] && exit $sts
if [[ ${opt_oeLib:-0} -ne 0 ]]; then
  ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $HOME/tools/clodoo $HOME/dev ${PYPATH//:/ } . .." "clodoo")
  if [[ -z "$ODOOLIBDIR" ]]; then
    echo "Library file odoorc not found!"
    exit 2
  fi
  . $ODOOLIBDIR
fi

UT1_LIST=
UT_LIST=
if [ "$(type -t Z0BUG_setup)" == "function" ]; then Z0BUG_setup; fi
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
if [ "$(type -t Z0BUG_teardown)" == "function" ]; then Z0BUG_teardown; fi
exit $sts
