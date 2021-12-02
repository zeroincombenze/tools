#! /bin/bash
# -*- coding: utf-8 -*-
#
# Backup filestore
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2020 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
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

__version__=0.3.53.4


OPTOPTS=(h        b          n            q           t       V           v)
OPTDEST=(opt_help opt_branch opt_dry_run  opt_verbose opt_tgt opt_version opt_verbose)
OPTACTI=("+"      "="        "1"          0           "=>"    "*>"        "+" )
OPTDEFL=(1        ""         0            -1          ""      ""          -1)
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
  "(C) 2017-2020 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
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
