#! /bin/bash
# -*- coding: utf-8 -*-
#
# Set reconcile flag in Odoo account.account
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2018 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
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

__version__=0.1.2


xec() {
#xec($val $type [name])
    local val=$1
    local t=$2
    local parent
    if [ -z "$3" ]; then
      local name="%"
    elif [ "$3" == "%IMMOBILIZZ%MATERIALI" -o "$3" == "BENI%MATERIALI" ]; then
      local name="%"
      parent="*"
    else
      local name="%$3%"
    fi
    local n x
    if [ $odoo_ver -ge 9 ]; then
      sql="select A.id,A.code,A.name,A.internal_type,T.type,A.reconcile from account_account A,account_account_type T where A.user_type_id=T.id and T.type='$t' and A.reconcile<>$val and lower(A.name) like lower('$name');"
      parent=
    else
      if [ "$parent" == "*" ]; then
        parent=$(psql -tc "select id from account_account where type='view' and lower(name) like lower('$3');" $db|tr -d "\n")
        parent=${parent//  / }
        parent=$(echo $parent)
        parent=${parent// /,}
        sql="select A.id,A.code,A.name,A.type,T.code,A.reconcile from account_account A,account_account_type T where A.user_type=T.id and T.code='$t' and A.reconcile<>$val and parent_id in ($parent);"
      else
        sql="select A.id,A.code,A.name,A.type,T.code,A.reconcile from account_account A,account_account_type T where A.user_type=T.id and T.code='$t' and A.reconcile<>$val and lower(A.name) like lower('$name');"
      fi
    fi
    psql -ec "$sql" $db
    if [ -n "$parent" ]; then
      sql=$(printf "update account_account set reconcile=%s where user_type='%s' and reconcile<>%s and parent_id in ($parent);" "$val" "$t" "$val" "$name")
    else
      sql=$(printf "update account_account set reconcile=%s where user_type='%s' and reconcile<>%s and lower(name) like lower('%s');" "$val" "$t" "$val" "$name")
    fi
    if [ $odoo_ver -ge 9 ]; then
      x=$(psql -tc "select id from account_account_type where type='$t';"  $db)
      n=$(echo $x)
      n=${n// /,}
      sql=$(printf "update account_account set reconcile=%s where user_type_id in (%s) and reconcile<>%s and lower(name) like lower('%s');" "$val" "$n" "$val" "$name")
    else
      x=$(psql -tc "select id from account_account_type where code='$t';" $db)
      n=$(echo $x)
      n=${n// /,}
      sql=$(printf "update account_account set reconcile=%s where user_type in (%s) and reconcile<>%s and lower(name) like lower('%s');" "$val" "$n" "$val" "$name")
    fi
    psql -ec "$sql" $db
}

OPTOPTS=(h        b          n            q           V           v)
OPTDEST=(opt_help opt_branch opt_dry_run  opt_verbose opt_version opt_verbose)
OPTACTI=(1        "="        1            0           "*>"        "+")
OPTDEFL=(0        ""         0            -1          ""          -1)
OPTMETA=("help"   "branch"   "do nothing" "verbose"   "version"   "verbose")
OPTHELP=("this help"\
 "Odoo branch"\
 "do nothing (dry-run)"\
 "silent mode"\
 "show version"\
 "verbose mode")
OPTARGS=(dbname)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
if [ -z "$dbname" ]; then
  opt_help=1
fi
if [ $opt_help -gt 0 ]; then
  print_help "Set reconcile flag in Odoo account.account"\
  "(C) 2017-2018 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi
if [ $opt_verbose -eq -1 ]; then
  opt_verbose=1
fi
discover_multi
if [ -n "$opt_branch" ]; then
  odoo_vid=$opt_branch
  odoo_fver=$(build_odoo_param FULLVER $odoo_vid)
  odoo_ver=$(build_odoo_param MAJVER $odoo_vid)
fi
DBlist=$(psql -lt|grep -E "[[:space:]](odoo|openerp)[[:space:]]"|awk -F"|" '{print $1}'|tr -d "\n")
for db in $DBlist; do
  if [[ "$dbname" == "all" || "$db" =~ "$dbname" ]]; then
    echo "$db"
    val=false
    for typ in income expense view cash bank; do
      xec "$val" "$typ"
    done
    for name in "%IMMOBILIZZ%MATERIALI" "BENI%MATERIALI" "IVA " " IVA" "ratei" "risconti" "FA " "capitale" "riserve"; do
      for typ in asset liability; do
        xec "$val" "$typ" "$name"
      done
    done
    val=true
    for typ in payable receivable; do
      xec "$val" "$typ"
    done
  fi
done
exit $STS_SUCCESS
