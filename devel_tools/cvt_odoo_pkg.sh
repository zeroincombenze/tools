#! /bin/bash
# -*- coding: utf-8 -*-
#
# Convert Odoo package for comparision
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2018-2020 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=$(echo -e "import sys\nprint(str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1])"|python)
for d in $TDIR $TDIR/.. $TDIR/../z0lib $TDIR/../.. $TDIR/../../z0lib $TDIR/../../z0lib/z0lib $HOME/dev $HOME/tools ${PYPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi
ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $HOME/tools/clodoo $HOME/dev ${PYPATH//:/ } . .." "clodoo")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)

__version__=1.0.1.3

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
if [ "$opt_version" ]; then
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
if [ $opt_help -gt 0 ]; then
  print_help "Cvt odoo package to comparition"\
  "(C) 2018-2020 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

[ ! -d ~/tmp ] && mkdir -p ~/tmp
cvt_dir "$pkgpath" "$tgtdir"
