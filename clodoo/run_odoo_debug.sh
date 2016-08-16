#! /bin/bash
# -*- coding: utf-8 -*-

THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
if [ -e $TDIR/z0librc ]; then
. $TDIR/z0librc
elif [ -e ./z0librc ]; then
. ./z0librc
elif [ -e ../z0librc ]; then
. ../z0librc
elif [ -e ~/z0librc ]; then
. ~/z0librc
elif [ -e /etc/z0librc ]; then
. /etc/z0librc
else
  echo "Library file z0librc not found!"
  exit $STS_FAILED
fi

__version__=0.1.4

OPTOPTS=(h        n            t         V           v           x)
OPTDEST=(opt_help opt_dry_run  opt_touch opt_version opt_verbose opt_xport)
OPTACTI=(1        "1"          1         "*>"        1           "=")
OPTDEFL=(1        0            0         ""          0           "")
OPTMETA=("help"   "do nothing" "touch"   "version"   "verbose"   "port")
OPTHELP=("this help"\
 "do nothing (dry-run)"\
 "touch config file, do not run odoo"\
 "show version"\
 "verbose mode"\
 "set odoo xmlrpc port")
OPTARGS=(odoo_ver)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Run odoo in debug mode"\
  "(C) 2015-2016 by zeroincombenze(R)\nhttp://www.zeroincombenze.it\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

if [ "$odoo_ver" == "v7" ]; then
  pfx="openerp"
  pfx2=
  tag="/server"
else
  pfx="odoo${odoo_ver:0:1}"
  pfx2=odoo
  tag=
fi

confn=/etc/odoo/${pfx}-server.conf
if [ ! -f $confn ]; then
  confn=/etc/odoo/${pfx2}-server.conf
fi
script="/opt/odoo/$odoo_ver$tag/openerp-server"


if [ $opt_verbose -gt 0 -o  $opt_dry_run -gt 0 -o $opt_touch -gt 0 ]; then
  echo "cp $confn ~/.openerp_serverrc"
fi
if [ $opt_dry_run -eq 0 ]; then
  cp $confn ~/.openerp_serverrc
  sed -ie 's:^logfile *=.*:logfile = False:' ~/.openerp_serverrc
  if [ -n "$opt_xport" ]; then
    sed -ie 's:^xmlrpc_port *=.*:xmlrpc_port = $opt_xport:' ~/.openerp_serverrc
  fi
  # vim ~/.openerp_serverrc
fi
if [ $opt_touch -eq 0 ]; then
  if [ $opt_verbose -gt 0 -o  $opt_dry_run -gt 0 ]; then
    echo "$script --debug"
  fi
  if [ $opt_dry_run -eq 0 ]; then
    eval $script --debug
  fi
fi
