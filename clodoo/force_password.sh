#! /bin/bash
# -*- coding: utf-8 -*-
#
# Force Odoo password
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2023 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# Based on template 2.1.1
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
ME=$(readlink -e $0)
if [[ -d $HOME/devel || -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
PYPATH=""
[[ $(basename $PWD) == "tests" && $(basename $PWD/../..) == "build" ]] && PYPATH="$(dirname $PWD)"
[[ $(basename $PWD) == "tests" && $(basename $PWD/../..) == "build" && -d $PWD/../scripts ]] && PYPATH="$PYPATH $(readlink -f $PWD/../scripts)"
x=$ME; while [[ $x != $HOME && $x != "/" && ! -d $x/lib && ! -d $x/bin && ! -d $x/pypi ]]; do x=$(dirname $x); done
[[ -d $x/pypi ]] && PYPATH="$PYPATH $x/pypi"
[[ -d $x/pypi/z0lib ]] && PYPATH="$PYPATH $x/pypi/z0lib"
[[ -d $x/pypi/z0lib/z0lib ]] && PYPATH="$PYPATH $x/pypi/z0lib/z0lib"
[[ -d $x/tools ]] && PYPATH="$PYPATH $x/tools"
[[ -d $x/tools/z0lib ]] && PYPATH="$PYPATH $x/tools/z0lib"
[[ -d $x/bin ]] && PYPATH="$PYPATH $x/bin"
[[ -d $x/lib ]] && PYPATH="$PYPATH $x/lib"
[[ -d $HOME_DEVEL/venv/bin ]] && PYPATH="$PYPATH $HOME_DEVEL/venv/bin"
[[ -d $HOME_DEVEL/../tools ]] && PYPATH="$PYPATH $(readlink -f $HOME_DEVEL/../tools)"
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $TDIR $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
[[ -z "$Z0LIBDIR" ]] && echo "Library file z0librc not found in <$PYPATH>!" && exit 72
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo" "clodoo")
[[ -z "$ODOOLIBDIR" ]] && echo "Library file odoorc not found!" && exit 72
. $ODOOLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=$ODOOLIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"

# DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
# TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
CYAN="\e[1;36m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.18

get_dbuser() {
  # get_dbuser odoo_majver
  local u
  for u in $USER odoo openerp postgresql; do
    if [[ -n "$1" ]]; then
      psql -p $opt_port -U$u$1 -l &>/dev/null
      if [[ $? -eq 0 ]]; then
        echo "$u$1"
        break
      fi
    fi
    psql -p $opt_port -U$u -l &>/dev/null
    if [[ $? -eq 0 ]]; then
      echo "$u"
      break
    fi
  done
}

OPTOPTS=(h        b          d        k         m         n            p        q           u        U          V           v           w)
OPTDEST=(opt_help opt_branch opt_db   opt_crypt opt_multi opt_dry_run  opt_port opt_verbose opt_user opt_dbuser opt_version opt_verbose opt_pwd)
OPTACTI=("+"      "="        "="      1         1         1            "="      0           "="      "="        "*>"        "+"         "=")
OPTDEFL=(0        ""         ""       -1        0         0            "5432"   -1          ""       ""         ""          1           "")
OPTMETA=("help"   "branch"   "dbname" ""        ""        "do nothing" "port"   "verbose"   "user"   "user"     "version"   "verbose"   "pwd")
OPTHELP=("this help"
  "odoo version"
  "dbname"
  "use crypt password"
  "multi-version odoo environment"
  "do nothing (dry-run)"
  "psql port (def 5432)"
  "silent mode"
  "username to change password"
  "postgres db role"
  "show version"
  "verbose mode"
  "password (do not use this option: password is cleared stored in history)")
OPTARGS=()

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
[ -z "$opt_db" ] && opt_help=1
[ -z "$opt_user" ] && opt_help=1
if [[ $opt_help -gt 0 ]]; then
  print_help "Install odoo theme" \
    "(C) 2015-2023 by zeroincombenze®\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

if [[ ! $opt_branch =~ (6.1|7.0|8.0|9.0|10.0|11.0|12.0|13.0|14.0|15.0|16.0) ]]; then
  echo "Invalid Odoo version"
  exit 1
fi

discover_multi
odoo_ver=$(build_odoo_param MAJVER $opt_branch)

[[ -n $opt_dbuser ]] && db_user=$opt_dbuser || db_user=$(get_dbuser)
userid=$(psql -p $opt_port -U$db_user -Atc "select id from res_users where login='$opt_user';" "$opt_db")
if [ -z "$userid" ]; then
  echo "User $opt_user not found!"
  psql -p $opt_port -U$db_user -Atc "select id,login from res_users" "$opt_db"
  exit 1
fi
if [[ $odoo_ver -ge 8 ]]; then
  opt_crypt=1
elif [[ $opt_crypt -eq -1 ]]; then
  opt_crypt=0
fi
pwd1=''
pwd2=''
[[ -n "$opt_pwd " ]] && pwd1="$opt_pwd" && pwd2="$pwd1"
while [ -z "$pwd1" -o "$pwd1" != "$pwd2" ]; do
  pwd1=''
  while [ -z "$pwd1" ]; do
    read -sp "Password:  " pwd1
    echo ""
  done
  pwd2=''
  while [ -z "$pwd2" ]; do
    read -sp "Type again:" pwd2
    echo ""
  done
done
if [ $opt_crypt -ne 0 ]; then
  echo -e "from passlib.context import CryptContext\nprint(CryptContext(['pbkdf2_sha512']).encrypt('$pwd1'))\n" | python
  crypt=$(echo -e "from passlib.context import CryptContext\nprint(CryptContext(['pbkdf2_sha512']).encrypt('$pwd1'))\n" | python)
  crypt="${crypt//\$/\\\$}"
  if [[ $odoo_ver -lt 12 ]]; then
    run_traced "psql -p $opt_port -U$db_user -c \"update res_users set password='',password_crypt='$crypt' where id=$userid;\" \"$opt_db\""
  else
    run_traced "psql -p $opt_port -U$db_user -c \"update res_users set password='$crypt' where id=$userid;\" \"$opt_db\""
  fi
else
  run_traced "psql -p $opt_port -c \"update res_users set password='$pwd1' where id=$userid;\" \"$opt_db\""
fi
echo "Restart Odoo Service"
