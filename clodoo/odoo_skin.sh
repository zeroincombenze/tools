#! /bin/bash
# -*- coding: utf-8 -*-
THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in "$TDIR" "$TDIR/.." "." ".." "~" "/etc"; do
  if [ -e $x/z0librc ]; then
    . $x/z0librc
    Z0LIBDIR=$x
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)

__version__=0.0.1

list_themes() {
    local webdir=$1
    local themelist
    for fn in $webdir/*.sass; do
      f=$(basename $fn)
      f=${f:0: -5}
      if [ "$f" != "base" ]; then
        themelist="$themelist $f"
      fi
    done
    echo $themelist
}

OPTOPTS=(h        n            V           v)
OPTDEST=(opt_help opt_dry_run  opt_version opt_verbose)
OPTACTI=(1        1            "*>"        1)
OPTDEFL=(1        0            ""          0)
OPTMETA=("help"   "do nothing" "version"   "verbose")
OPTHELP=("this help"\
 "do nothing (dry-run)"\
 "show version"\
 "verbose mode")
OPTARGS=(odoo_ver theme_name)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Install odoo theme"\
  "(C) 2015-2016 by zeroincombenze(R)\nhttp://www.zeroincombenze.it\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

if [ "$odoo_ver" == "v7" ]; then
  sfxver=7
  pfx="openerp"
  pfx2=
  sfx="/server"
else
  sfxver=${odoo_ver:0:1}
  pfx="odoo$sfxver"
  pfx2=odoo
  sfx=
fi

confn=/etc/odoo/${pfx}-server.conf
if [ ! -f $confn ]; then
  confn=/etc/odoo/${pfx2}-server.conf
fi
script=$(findpkg "${pfx}-server" "/etc/init.d rc.d" "init.d")
if [ -z "$script" ]; then
  script=$(findpkg "${pfx}" "/etc/init.d rc.d" "init.d")
fi
if [ -z "$script" ]; then
  echo "Version $odoo_ver not found!"
  exit 1
fi
svcname=$(basename $script)
webdir=$(findpkg "base.sass" "/opt/odoo/$odoo_ver/addons/web/static/src/css")
if [ -z "$webdir" ]; then
  webdir=$(findpkg "base.sass" "/opt/odoo/$odoo_ver/web/addons/web/static/src/css")
fi
if [ -z "$webdir" ]; then
  echo "Theme files not found!"
  exit 1
fi
webdir=$(dirname $webdir)
# echo "service $svcname restart"
# echo "dir $webdir"
themelist=$(list_themes "$webdir")
if [ -z "$themelist" ]; then
   echo "cp $webdir/base.sass $webdir/odoo.sass"
   exit 1
fi
if [ -z "$theme_name"]; then
  echo $themelist
  exit 0
fi
