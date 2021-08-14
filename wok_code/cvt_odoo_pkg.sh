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
THIS=$(basename "$0")
TDIR=$($READLINK -f $(dirname $0))
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys\np=[x for x in (os.environ['PATH']+':$TDIR:..:$HOME_DEV').split(':') if x not in sys.path];p.extend(sys.path);print(' '.join(p))"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$($READLINK -e $Z0LIBDIR)
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

__version__=1.0.1.14

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
OPTACTI=(1        "="        "="      "="     1            0           "="      "*>"        "+")
OPTDEFL=(0        "10.0"     ""       "6.1"   0            -1          ""       ""          1)
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
  print_help "Cvt odoo package to comparition"\
  "(C) 2018-2020 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

[ ! -d ~/tmp ] && mkdir -p ~/tmp
cvt_dir "$pkgpath" "$tgtdir"
