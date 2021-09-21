#! /bin/bash
# -*- coding: utf-8 -*-
#
# Force Odoo password
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=""
for p in $TDIR $TDIR/.. $TDIR/../.. $HOME/venv_tools/bin $HOME/venv_tools/lib $HOME/tools; do
  [[ -d $p ]] && PYPATH=$(find $(readlink -f $p) -maxdepth 3 -name z0librc)
  [[ -n $PYPATH ]] && break
done
PYPATH=$(echo -e "import os,sys;p=[os.path.dirname(x) for x in '$PYPATH'.split()];p.extend([x for x in os.environ['PATH'].split(':') if x not in p and not x.startswith('/usr') and not x.startswith('/sbin') and not x.startswith('/bin')]);p.extend([x for x in sys.path if x not in p]);print(' '.join(p))"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo")
if [[ -z "$ODOOLIBDIR" ]]; then
  echo "Library file odoorc not found!"
  exit 72
fi
. $ODOOLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=$ODOOLIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$($READLINK -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"

__version__=0.3.34.99

get_dbuser() {
  # get_dbuser odoo_majver
  local u
  for u in $USER odoo openerp postgresql; do
    if [[ -n "$1" ]]; then
      psql -U$u$1 -l &>/dev/null
      if [[ $? -eq 0 ]]; then
        echo "$u$1"
        break
      fi
    fi
    psql -U$u -l &>/dev/null
    if [[ $? -eq 0 ]]; then
      echo "$u"
      break
    fi
  done
}

OPTOPTS=(h        b          d        k         m         n            q           u        U          V           v)
OPTDEST=(opt_help opt_branch opt_db   opt_crypt opt_multi opt_dry_run  opt_verbose opt_user opt_dbuser opt_version opt_verbose)
OPTACTI=(1        "="        "="      1         1         1            0           "="      "="        "*>"        "+")
OPTDEFL=(0        ""         ""       -1        0         0            -1          ""       ""         ""          1)
OPTMETA=("help"   "branch"   "dbname" ""        ""        "do nothing" "verbose"   "user"   "user"     "version"   "verbose")
OPTHELP=("this help"
  "odoo version"
  "dbname"
  "use crypt password"
  "multi-version odoo environment"
  "do nothing (dry-run)"
  "silent mode"
  "username to change password"
  "postgres db role"
  "show version"
  "verbose mode")
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
    "(C) 2015-2021 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

if [[ ! $opt_branch =~ (6.1|7.0|8.0|9.0|10.0|11.0|12.0|13.0|14.0) ]]; then
  echo "Invalid Odoo version"
  exit 1
fi

discover_multi
odoo_ver=$(build_odoo_param MAJVER $opt_branch)

[[ -n $opt_dbuser ]] && db_user=$opt_dbuser || db_user=$(get_dbuser)
userid=$(psql -U$db_user -tc "select id from res_users where login='$opt_user';" $opt_db)
userid=$(echo $userid)
if [ -z "$userid" ]; then
  echo "User $opt_user not found!"
  exit 1
fi
if [[ $odoo_ver -ge 8 ]]; then
  opt_crypt=1
elif [[ $opt_crypt -eq -1 ]]; then
  opt_crypt=0
fi
pwd1=''
pwd2=''
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
  echo -e "from passlib.context import CryptContext\nprint CryptContext(['pbkdf2_sha512']).encrypt('$pwd1')\n" | python
  crypt=$(echo -e "from passlib.context import CryptContext\nprint CryptContext(['pbkdf2_sha512']).encrypt('$pwd1')\n" | python)
  crypt="${crypt//\$/\\\$}"
  if [[ $odoo_ver -lt 12 ]]; then
    run_traced "psql -U$db_user -c \"update res_users set password='',password_crypt='$crypt' where id=$userid;\" $opt_db"
  else
    run_traced "psql -U$db_user -c \"update res_users set password='$crypt' where id=$userid;\" $opt_db"
  fi
else
  run_traced "psql -c \"update res_users set password='$pwd1' where id=$userid;\" $opt_db"
fi
echo "Restart Odoo Service"
