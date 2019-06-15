#! /bin/bash
# -*- coding: utf-8 -*-
#
# Backup filestore
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2018 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=$(echo -e "import sys\nprint(str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1])"|python)
for d in $TDIR $TDIR/.. $TDIR/../.. $HOME/dev $HOME/tools ${PYPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ] && [ -e $d/z0lib/z0librc ]; then
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
ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $HOME/tools/clodoo $HOME/dev ${PYPATH//:/ } . .." "clodoo")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)


__version__=0.3.8.37


OPTOPTS=(h        b          n            q           t       V           v)
OPTDEST=(opt_help opt_branch opt_dry_run  opt_verbose opt_tgt opt_version opt_verbose)
OPTACTI=(1        "="        "1"          0           "=>"    "*>"        "+" )
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
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
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
