#! /bin/bash
# -*- coding: utf-8 -*-

THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in $TDIR $TDIR/.. $TDIR/../z0lib $TDIR/../../z0lib . .. /etc; do
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

__version__=0.1.11.2

OPTOPTS=(h        d        e       k        i       l        m           n           s         t         U         V           v           w       x)
OPTDEST=(opt_help opt_db   opt_exp opt_keep opt_imp opt_lang opt_modules opt_dry_run opt_stop  opt_touch opt_user  opt_version opt_verbose opt_web opt_xport)
OPTACTI=(1        "="      1       1        1       1        "="         "1"         1         1         "="       "*>"        1           1       "=")
OPTDEFL=(1        ""       0       0        0       0        ""          0           0         0         ""        ""          0           0       "")
OPTMETA=("help"   "dbname" ""      ""       ""      ""       "modules"   "do nothing" ""       "touch"   "user"    "version"   "verbose"   0       "port")
OPTHELP=("this help"\
 "db name to test (require -m switch)"\
 "export it translation"\
 "do not create new DB and keep it after run"\
 "import it translation"\
 "load it language"
 "modules to test or translate"\
 "do nothing (dry-run)"\
 "stop after init"\
 "touch config file, do not run odoo"\
 "db username"\
 "show version"\
 "verbose mode"\
 "run as web server"\
 "set odoo xmlrpc port")
OPTARGS=(odoo_ver)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Run odoo in debug mode"\
  "(C) 2015-2017 by zeroincombenze(R)\nhttp://www.zeroincombenze.it\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

if [ "$odoo_ver" == "v7" ]; then
  sfxver=7
  pfx="openerp"
  pfx2=
  sfx="/server"
else
  sfxver=$(echo $odoo_ver|grep -Eo [0-9]+|head -n1)
  pfx="odoo$sfxver"
  pfx2=odoo
  sfx=
fi

if [ "$odoo_ver" == "10.0" ]; then
  confn=/etc/odoo/${pfx}.conf
  confn2=/etc/odoo/${pfx2}.conf
  script="/opt/odoo/$odoo_ver$sfx/odoo-bin"
elif [ "$odoo_ver" == "v7" ]; then
  confn=/etc/odoo/openerp-server.conf
  confn2=/etc/odoo/openerp-server.conf
  script="/opt/odoo/$odoo_ver$sfx/openerp-server"
else
  confn=/etc/odoo/${pfx}-server.conf
  confn2=/etc/odoo/${pfx2}-server.conf
  script="/opt/odoo/$odoo_ver$sfx/openerp-server"
fi
create_db=0
drop_db=0
if [ $opt_lang -ne 0 ]; then
  opt_keep=1
  opt_stop=1
  if [ -n "$opt_modules" ]; then
    opt_modules=
  fi
elif [ $opt_exp -ne 0 -o $opt_imp -ne 0 ]; then
  opt_keep=1
  if [ -z "$opt_modules" ]; then
    echo "Missing -m switch"
    exit 1
  fi
fi
if [ -n "$opt_modules" ]; then
  if [ $opt_keep -eq 0 ]; then
    mods=${opt_modules//,/ }
    for m in $mods; do
      p=$(find /opt/odoo/$odoo_ver -type d -name $m|head -n1)
      if [ -f $p/__openerp__.py ]; then
        f=$p/__openerp__.py
        x=$(cat $f|grep -A10 depends|tr -d '\n'|awk -F"[" '{print $2}'|awk -F"]" '{print $1}'|tr -d '" '|tr -d "'")
        if [ -n "$x" ]; then
          opt_modules="$opt_modules,$x"
        fi
      fi
    done
    opts="-i $opt_modules --test-enable"
    create_db=1
  elif [ $opt_exp -ne 0 -o $opt_imp -ne 0 ]; then
    src=$(find /opt/odoo/$odoo_ver -type d -name "$opt_modules"|head -n1)
    if [ -n "$src" ]; then
      if [ -f $src/i18n/it.po ]; then
        src=$src/i18n/it.po
        if [ $opt_exp -ne 0 ]; then
          run_traced "cp $src $src.bak"
        fi
      else
        src=
      fi
    fi
    if [ -z "$src" ]; then
      echo "Translation file not found!"
      exit 1
    fi
    if [ $opt_imp -ne 0 ]; then
      opts="--modules=$opt_modules --i18n-import=$src -lit_IT --i18n-overwrite"
    else
      opts="--modules=$opt_modules --i18n-export=$src -lit_IT"
    fi
  else
    opts="-u $opt_modules --test-enable"
  fi
else
  if [ $opt_lang -ne 0 ]; then
    opts=--load-language=it_IT
  else
    opts=""
  fi
fi
if [ $opt_web -ne 0 ]; then
  if [ -z "$opt_xport" -a $opt_web -ne 0 ]; then
    let opt_xport="8160+$sfxver"
  fi
  if [ -z "$opt_user" ]; then
    opt_user=odoo$sfxver
  fi
elif [ -n "$opt_modules" -o $opt_exp -ne 0 -o $opt_imp -ne 0 -o $opt_lang -ne 0 ]; then
  if [ -z "$opt_xport" ]; then
    let opt_xport="8070+$sfxver"
  fi
  if [ -z "$opt_user" ]; then
    opt_user=odoo$sfxver
  fi
  if [ -z "$opt_db" ]; then
    opt_db="test_openerp"
    if [ $opt_stop -gt 0 -a $opt_keep -eq 0 ]; then
      drop_db=1
    fi
  fi
else
  if [ -z "$opt_user" ]; then
    opt_user=postgres
  fi
fi
if [ $opt_stop -gt 0 ]; then
  opts="$opts --stop-after-init"
  if [ $opt_exp -eq 0 -a $opt_imp -eq 0 -a  $opt_lang -eq 0 ]; then
     opts="$opts --test-commit"
  fi
fi
if [ -n "$opt_db" ]; then
   opts="$opts -d $opt_db"
fi
if [ $opt_verbose -gt 0 -o  $opt_dry_run -gt 0 -o $opt_touch -gt 0 ]; then
  if [ -f $confn ]; then
    echo "cp $confn ~/.openerp_serverrc"
  else
    echo "cp $confn2 ~/.openerp_serverrc"
  fi
fi
if [ $opt_dry_run -eq 0 ]; then
  if [ -f $confn ]; then
    cp $confn ~/.openerp_serverrc
    opt_multi=1
  else
    echo "cp $confn2 ~/.openerp_serverrc"
    opt_multi=0
    if [ $opt_web -ne 0 ]; then
      opt_xport=8069
    fi
  fi
  sed -ie 's:^logfile *=.*:logfile = False:' ~/.openerp_serverrc
  if [ -n "$opt_xport" ]; then
    sed -ie "s:^xmlrpc_port *=.*:xmlrpc_port = $opt_xport:" ~/.openerp_serverrc
  fi
  if [ -n "$opt_user" ]; then
    sed -ie "s:^db_user *=.*:db_user = $opt_user:" ~/.openerp_serverrc
  fi
  if [ $opt_verbose -gt 0 ]; then
    vim ~/.openerp_serverrc
  fi
fi
if [ $opt_touch -eq 0 ]; then
  if [ $drop_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "pg_db_active -a $opt_db; dropdb -U$opt_user --if-exists $opt_db"
    fi
    pg_db_active -a $opt_db; dropdb -U$opt_user --if-exists $opt_db
  fi
  if [ $create_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "createdb -U$opt_user $opt_db"
    fi
    createdb -U$opt_user $opt_db
  fi
  if [ "$odoo_ver" != "10.0" -a $opt_dry_run -eq 0 -a $opt_exp -eq 0 -a $opt_imp -eq 0 -a $opt_lang -eq 0 ]; then
    opts="--debug $opts"
  fi
  if [ $opt_verbose -gt 0 -o $opt_dry_run -gt 0 ]; then
    echo "$script $opts"
  fi
  if [ $opt_dry_run -eq 0 ]; then
    eval $script $opts
  fi
  if [ $drop_db -gt 0 ]; then
    if [ -z "$opt_modules" -o $opt_stop -eq 0 ]; then
      if [ $opt_verbose -gt 0 ]; then
        echo "dropdb -U$opt_user --if-exists $opt_db"
      fi
      dropdb -U$opt_user --if-exists $opt_db
    fi
  fi
  if [ $opt_exp -ne 0 ]; then
    echo "Translation exported to '$src' file"
  elif [ $opt_imp -ne 0 ]; then
    echo "Translation imported from '$src' file"
  fi
fi
