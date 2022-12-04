#! /bin/bash
# -*- coding: utf-8 -*-
#
# Convert Odoo package for comparision
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2018-2020 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
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
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo")
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
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.3

cvt_dir() {
    # echo "cvt_dir ($1,$2)"
    [ -d $2 ] && run_traced "rm -fR $tgtdir"
    [ ! -d $2 ] && run_traced "mkdir -p $2"
    [ -n "$opt_rule" ] && OPTS="-R$opt_rule" || OPTS=
    for f in $1/*; do
      b=$(basename $f)
      if [ -d $f ]; then
        # echo "$f is a dir"
        tgtdir=$2/$b
        cvt_dir "$f" "$tgtdir"
      else
        if [ "${f: -4}" == ".pyc" ]; then
          :
        elif [ "${f: -3}" == ".py" ]; then
          run_traced "$TDIR/topep8 -AA -F$opt_from -b$opt_branch $OPTS $f -o $2/$b"
        elif [ "${f: -4}" == ".xml" ]; then
          run_traced "$TDIR/topep8 -b$opt_branch $f -o $2/$b"
        else
          run_traced "cp $f $2/$b"
        fi
      fi
    done
}


OPTOPTS=(h        b          d       F        n            q           R        V           v)
OPTDEST=(opt_help opt_branch opt_dst opt_from opt_dry_run  opt_verbose opt_rule opt_version opt_verbose)
OPTACTI=("+"      "="        "="      "="     1            0           "="      "*>"        "+")
OPTDEFL=(0        "10.0"     ""       "6.1"   0            0           ""       ""          1)
OPTMETA=("help"   "branch"   "l|r"   "branch" "do nothing" "verbose"   "file"   "version"   "verbose")
OPTHELP=("this help"\
 "target odoo version"\
 "left or rigth destination"\
 "from odoo version"\
 "do nothing (dry-run)"\
 "silent mode"\
 "convertion rules (to_oia|ot_oca)"\
 "show version"\
 "verbose mode")
OPTARGS=(pkgpath)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
[ -z "$pkgpath" ] && opt_help=1
if [ "$opt_dst" == "l" ]; then
  tgtdir="$HOME/tmp/left"
elif [ "$opt_dst" == "r" ]; then
  tgtdir="$HOME/tmp/rigth"
else
  opt_help=1
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Cvt odoo package to comparison"\
  "(C) 2018-2020 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

[ ! -d ~/tmp ] && mkdir -p ~/tmp
cvt_dir "$pkgpath" "$tgtdir"
