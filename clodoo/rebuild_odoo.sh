#! /bin/bash
# -*- coding: utf-8 -*-

THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYTHONPATH=$(echo -e "import sys\nprint str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1]"|python)
for d in $TDIR $TDIR/.. ${PYTHONPATH//:/ } /etc; do
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
ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. ${PYTHONPATH//:/ } . .. $HOME/tools/clodoo $HOME/dev" "clodoo")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR

__version__=0.2.0.1


OPTOPTS=(h        m           M         n           R            V           v           x         y)
OPTDEST=(opt_help opt_modules opt_multi opt_dry_run opt_rpt      opt_version opt_verbose opt_excl  opt_yes)
OPTACTI=(1        "="         1         "1"         "="          "*>"        1           "="       1)
OPTDEFL=(1        ""          -1        0           ""           ""          0           ""        0)
OPTMETA=("help"   "modules"   ""        "no op"     "repository" "version"   "verbose"   "modules" "")
OPTHELP=("this help"\
 "modules to test, translate or upgrade"\
 "multi-version odoo environment"\
 "do nothing (dry-run)"\
 "repository name, one of oca oia zero-git zero-http"\
 "show version"\
 "verbose mode"\
 "module list to exclude (comma separated)"\
 "assume yes")
OPTARGS=(odoo_vid)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Rebuild odoo environment"\
  "(C) 2015-2018 by zeroincombenze(R)\nhttp://www.zeroincombenze.it\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

discover_multi
odoo_fver=$(build_odoo_param FULLVER $odoo_vid)
odoo_ver=$(build_odoo_param FULLVER $odoo_fver)
sub_list=
excl_list="addons cover debian doc history odoo openerp node_modules scripts server setup __to_remove woven_fabric"
if [ -z $opt_excl ]; then
  if [ "$actions" == "build" -o "$actions" == "rebuild" -o "$act" == "rebuild_new" ]; then
    opt_excl="OCB/v7,cscs_addons,l10n-italy/7.0,l10n-italy-supplemental/10.0,website/7.0,account_banking_cscs/v7,account_banking_cscs/8.0,account_banking_cscs/9.0,account_banking_cscs/10.0,account_invoice_create_payment,account_payment_approve_invoice,zeroincombenze,openerp_gantt_chart_modification,connector"
  else
    opt_excl="OCB/v7,cscs_addons,l10n-italy/7.0,l10n-italy-supplemental,website/7.0,account_banking_cscs,account_invoice_create_payment,account_payment_approve_invoice,zeroincombenze,openerp_gantt_chart_modification,connector"
  fi
fi
opt_excl="${opt_excl//,/ }"
if [[ " $opt_excl " =~ [[:space:]]themes[[:space:]] ]]; then
  :
else
  opt_excl="$opt_excl themes"
fi
if [[ " $opt_excl " =~ [[:space:]]website/7.0[[:space:]] ]]; then
  :
elif [[ " $opt_excl " =~ [[:space:]]7.0/website[[:space:]] ]]; then
  :
else
  opt_excl="$opt_excl website/7.0"
fi
for oem in $opt_excl; do
  if [[ "$oem" =~ / ]]; then
    :
  else
    excl_list="$excl_list $oem"
  fi
done
