#! /bin/bash
# -*- coding: utf-8 -*-

THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in "$TDIR" "." ".." "~" "/etc"; do
  if [ -e $x/z0librc ]; then
    . $x/z0librc
    Z0LIBDIR=$x
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 1
fi


__version__=0.1.5

OPTOPTS=(h        d        m           n            t         s        V           v           x)
OPTDEST=(opt_help opt_db   opt_modules opt_dry_run  opt_touch opt_stop opt_version opt_verbose opt_xport)
OPTACTI=(1        "="      "="         "1"          1         1        "*>"        1           "=")
OPTDEFL=(1        ""       ""          0            0         0        ""          0           "")
OPTMETA=("help"   "dbname" "modules"   "do nothing" "touch"   ""       "version"   "verbose"   "port")
OPTHELP=("this help"\
 "db name to test"\
 "modules to test"\
 "do nothing (dry-run)"\
 "touch config file, do not run odoo"\
 "stop after init"\
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
script="/opt/odoo/$odoo_ver$sfx/openerp-server"
create_db=0
drop_db=0
if [ -n "$opt_modules" ]; then
   opts="-i $opt_modules --test-enable"
   create_db=1
   if [ $opt_stop -gt 0 ]; then
    opts="$opts --stop-after-init"
   fi
   if [ -z "$opt_db" ]; then
     opt_db="test_openerp"
     if [ $opt_stop -gt 0 ]; then
       drop_db=1
       if [ -z "$opt_xport" ]; then
         opt_xport=807$sfxver
       fi
     fi
   fi
else
   opts=""
fi
if [ -n "$opt_db" ]; then
   opts="$opts -d $opt_db"
fi


if [ $opt_verbose -gt 0 -o  $opt_dry_run -gt 0 -o $opt_touch -gt 0 ]; then
  echo "cp $confn ~/.openerp_serverrc"
fi
if [ $opt_dry_run -eq 0 ]; then
  cp $confn ~/.openerp_serverrc
  sed -ie 's:^logfile *=.*:logfile = False:' ~/.openerp_serverrc
  if [ -n "$opt_xport" ]; then
    sed -ie "s:^xmlrpc_port *=.*:xmlrpc_port = $opt_xport:" ~/.openerp_serverrc
  fi
  if [ $opt_verbose -gt 0 ]; then
    vim ~/.openerp_serverrc
  fi
fi
if [ $opt_touch -eq 0 ]; then
  if [ $drop_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "dropdb --if-exists $opt_db"
    fi
    dropdb --if-exists $opt_db
  fi
  if [ $create_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "createdb $opt_db"
    fi
    createdb $opt_db
  fi
  if [ $opt_verbose -gt 0 -o  $opt_dry_run -gt 0 ]; then
    echo "$script --debug $opts"
  fi
  if [ $opt_dry_run -eq 0 ]; then
    eval $script --debug $opts
  fi
  if [ $drop_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "dropdb --if-exists $opt_db"
    fi
    dropdb --if-exists $opt_db
  fi
fi
