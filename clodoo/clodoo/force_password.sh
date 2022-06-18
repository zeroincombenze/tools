#! /bin/bash
# -*- coding: utf-8 -*-
#
# Force Odoo password
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 1.0.2.7
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
HOME_DEV="$HOME/devel"
[[ -x $TDIR/../bin/python ]] && PYTHON=$(readlink -f $TDIR/../bin/python) || [[ -x $TDIR/python ]] && PYTHON="$TDIR/python" || PYTHON="python"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\no=os.path\nHOME=os.environ.get('HOME');t=o.join(HOME,'tools')\nn=o.join(HOME,'pypi') if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME,HOME_DEV, 'pypi')\nd=HOME_DEV if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME_DEV,'venv')\ndef apl(l,p,b):\n if p:\n  p2=o.join(p,b,b)\n  p1=o.join(p,b)\n  if o.isdir(p2):\n   l.append(p2)\n  elif o.isdir(p1):\n   l.append(p1)\nl=[TDIR]\nv=''\nfor x in sys.path:\n if not o.isdir(t) and o.isdir(o.join(x,'tools')):\n  t=o.join(x,'tools')\n if not v and o.basename(x)=='site-packages':\n  v=x\nfor x in os.environ['PATH'].split(':'):\n if x.startswith(d):\n  d=x\n  break\nfor b in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(d):\n  apl(l,d,b)\n elif TDIR.startswith(n):\n  apl(l,n,b)\n apl(l,v,b)\n apl(l,t,b)\nl=l+os.environ['PATH'].split(':')\ntdir=o.dirname(TDIR)\np=set()\npa=p.add\np=[x for x in l if x and (x.startswith(HOME) or x.startswith(HOME_DEV) or x.startswith(tdir)) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found in <$PYPATH>!"
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
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"

DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=1.0.6

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
OPTACTI=("+"      "="        "="      1         1         1            0           "="      "="        "*>"        "+")
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
