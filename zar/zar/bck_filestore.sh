#! /bin/bash
# -*- coding: utf-8 -*-
#
# Backup filestore
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2018 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\nHOME=os.environ.get('HOME');y=os.path.join(HOME_DEV,'pypi');t=os.path.join(HOME,'tools')\ndef apl(l,p,x):\n  d2=os.path.join(p,x,x)\n  d1=os.path.join(p,x)\n  if os.path.isdir(d2):\n   l.append(d2)\n  elif os.path.isdir(d1):\n   l.append(d1)\nl=[TDIR]\nfor x in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(y):\n  apl(l,y,x)\n elif TDIR.startswith(t):\n  apl(l,t,x)\nl=l+os.environ['PATH'].split(':')\np=set()\npa=p.add\np=[x for x in l if x and x.startswith(HOME) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|python)
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
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=1.3.38


OPTOPTS=(h        b          n            q           t       V           v)
OPTDEST=(opt_help opt_branch opt_dry_run  opt_verbose opt_tgt opt_version opt_verbose)
OPTACTI=(1        "="        "1"          0           "=>"    "*>"        "+" )
OPTDEFL=(1        ""         0            0          ""      ""           -1)
OPTMETA=("help"   "vid"      "do nothing" "verbose"   "host"  "version"   "silent")
OPTHELP=("this help"\
 "branch: must be 7.0 or 8.0 or 9.0 or 10.0 11.0 or 12.0 (def all)"\
 "do nothing (dry-run)"\
 "silent mode"\
 "target host"\
 "show version"\
 "verbose mode")
OPTARGS=()

parseoptargs "$@"
[ -z "$opt_tgt" ] && opt_help=1
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Backup Odoo filestore (with attachments)"\
  "(C) 2017-2018 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

discover_multi
sts=0
[ -z "$opt_branch" ] && opt_branch="12.0 11.0 10.0 9.0 8.0 7.0 6.1"
for odoo_vid in ${opt_branch//,/ };do
  DDIR=$(build_odoo_param DDIR $odoo_vid)
  echo "rsync -avz $DDIR/filestore/ $opt_tgt:$DDIR/filestore/"
  [ $opt_dry_run -eq 0 ] && rsync -avz $DDIR/filestore/ $opt_tgt:$DDIR/filestore/
done
exit $sts
