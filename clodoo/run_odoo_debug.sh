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
ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $TDIR/../clodoo $TDIR/../../clodoo . .. $HOME/dev")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR

__version__=0.3.6.3


OPTOPTS=(h        d        e       k        i       l        m           M         n           o         s         t         U          u       V           v           w       x)
OPTDEST=(opt_help opt_db   opt_exp opt_keep opt_imp opt_lang opt_modules opt_multi opt_dry_run opt_ofile opt_stop  opt_touch opt_dbuser opt_upd opt_version opt_verbose opt_web opt_xport)
OPTACTI=(1        "="      1       1        1       1        "="         1         "1"         "="       1         1         "="        1       "*>"        1           1       "=")
OPTDEFL=(1        ""       0       0        0       0        ""          -1        0           ""        0         0         ""         0       ""          0           0       "")
OPTMETA=("help"   "dbname" ""      ""       ""      ""       "modules"   ""        "no op"     "file"    ""        "touch"   "user"     ""      "version"   "verbose"   0       "port")
OPTHELP=("this help"\
 "db name to test,translate o upgrade (require -m switch)"\
 "export it translation (conflict with -i -u)"\
 "do not create new DB and keep it after run"\
 "import it translation (conflict with -e -u)"\
 "load it language"
 "modules to test, translate or upgrade"\
 "multi-version odoo environment"\
 "do nothing (dry-run)"\
 "output file (if export multiple modules)"\
 "stop after init"\
 "touch config file, do not run odoo"\
 "db username"\
 "upgrade module (conflict with -e -i)"\
 "show version"\
 "verbose mode"\
 "run as web server"\
 "set odoo xmlrpc port")
OPTARGS=(odoo_vid)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Run odoo in debug mode"\
  "(C) 2015-2018 by zeroincombenze(R)\nhttp://www.zeroincombenze.it\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

discover_multi
odoo_fver=$(build_odoo_param FULLVER $odoo_vid)
odoo_ver=$(build_odoo_param FULLVER $odoo_fver)
confn=$(build_odoo_param CONFN $odoo_vid search)
script=$(build_odoo_param BIN $odoo_vid search)
odoo_root=$(build_odoo_param ROOT $odoo_vid search)
manifest=$(build_odoo_param MANIFEST $odoo_vid search)

if [ $opt_web -ne 0 ]; then
  rpcport=$(build_odoo_param RPCPORT $odoo_vid)
  odoo_user=$(build_odoo_param USER $odoo_vid)
else
  rpcport=$(build_odoo_param RPCPORT $odoo_vid debug)
  odoo_user=$(build_odoo_param USER $odoo_vid debug)
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
  opt_stop=1
  if [ -z "$opt_modules" ]; then
    echo "Missing -m switch"
    exit 1
  fi
elif [ $opt_upd -ne 0 ]; then
  opt_keep=1
  if [ -z "$opt_modules" ]; then
    echo "Missing -m switch"
    exit 1
  fi
  if [ -z "$opt_db" ]; then
    echo "Missing -d switch"
    exit 1
  fi
fi
if [ -z "$opt_dbuser" ]; then
  opt_dbuser=$odoo_user
fi
if [ -n "$opt_modules" ]; then
  if [ $opt_keep -eq 0 ]; then
    # mods=${opt_modules//,/ }
    # for m in $mods; do
    #   p=$(find $odoo_root -type d -name $m|head -n1)
    #   if [ -f $p/$manifest ]; then
    #     f=$p/$manifest
    #     x=$(cat $f|grep -A10 depends|tr -d '\n'|awk -F"[" '{print $2}'|awk -F"]" '{print $1}'|tr -d '" '|tr -d "'")
    #     if [ -n "$x" ]; then
    #       opt_modules="$opt_modules,$x"
    #     fi
    #   fi
    # done
    addons_list=
    [ -d $PWD/addons ] && addons_list=$addons_list,$PWD/addons
    [ -d $PWD/openerp/addons ] && addons_list=$addons_list,$PWD/openerp/addons
    [ -d $PWD/server/openerp/addons ] && addons_list=$addons_list,$PWD/server/openerp/addons
    addons_list=${addons_list:1}
    pushd /opt/odoo/dev/pypi/maintainer-quality-tools/maintainer-quality-tools/travis/ >/dev/null
cat <<EOF >./get_test_dependencies.py
import sys
from getaddons import get_addons, get_modules, is_installable_module
from test_server import get_test_dependencies
ltype=''
path=''
addons_list=None
if len(sys.argv)>1: ltype=sys.argv[1]
if len(sys.argv)>2: path=sys.argv[2]
if len(sys.argv)>3: addons_list=sys.argv[3].split(',')
if ltype == 'mod':
    paths=path.split(',')
    res=[]
    for path in paths:
        r=get_modules(path)
        for m in r:
            if m not in res:
                res.append(m)
    print ','.join(res)
elif ltype == 'dep':
    res=get_test_dependencies(path, addons_list)
    print ','.join(res)
else:
    print 'get_test_dependencies.py mod|dep path [addons_list]'
EOF
    if [ "$opt_modules" == "all" ];then
      opt_modules=$(python ./get_test_dependencies.py mod $addons_list)
    fi
    x=$(python ./get_test_dependencies.py dep $addons_list $opt_modules)
    if [ -n "$x" ]; then
      opt_modules="$opt_modules,$x"
    fi
    popd >/dev/null
    opts="-i $opt_modules --test-enable"
    create_db=1
  else
    mods=${opt_modules//,/ }
    opti=
    xi=-i
    optu=
    xu=-u
    for m in $mods; do
      r=$(psql -U$opt_dbuser $opt_db -tc "select state from ir_module_module where name='$m';")
      if [[ $r =~ uninstalled ]]; then
        opti="$opti$xi$m"
        xi=,
      else
        optu="$optu$xu$m"
        xu=,
      fi
    done
    optsiu="$opti $optu"
    alt=
    if [ $opt_exp -ne 0 -a -n "$opt_ofile" ]; then
      src=$(readlink -f $opt_ofile)
      opts="--modules=$opt_modules --i18n-export=$src -lit_IT"
    elif [ $opt_exp -ne 0 -o $opt_imp -ne 0 ]; then
      srcs=$(find $odoo_root -type d -name "$opt_modules")
      f=0
      for src in $srcs; do
        if [ -n "$src" ]; then
          if [ -f $src/i18n/it.po ]; then
            src=$src/i18n/it.po
            if [ $opt_exp -ne 0 ]; then
              run_traced "cp $src $src.bak"
            fi
            f=1
            break
          else
            alt=$(find $src/i18n -name '*.po'|head -n1)
            src=
            if [ -n "$alt" ]; then fi=1 break; fi
          fi
        fi
      done
      # if [ -z "$src" ]; then
      if [ $f -eq 0 ]; then
        echo "Translation file not found!"
        if [ -n "$alt" ]; then
          echo "may be $alt"
        fi
        exit 1
      fi
      if [ $opt_imp -ne 0 ]; then
        opts="--modules=$opt_modules --i18n-import=$src -lit_IT --i18n-overwrite"
      else
        opts="--modules=$opt_modules --i18n-export=$src -lit_IT"
      fi
    elif [ $opt_upd -ne 0 ]; then
      opts="$optsiu"
    else
      opts="$optsiu --test-enable"
    fi
  fi
else
  if [ $opt_lang -ne 0 ]; then
    opts=--load-language=it_IT
  else
    opts=""
  fi
fi
if [ -z "$opt_xport" ]; then
  opt_xport=$rpcport
fi
if [ -n "$opt_modules" -o $opt_upd -ne 0 -o $opt_exp -ne 0 -o $opt_imp -ne 0 -o $opt_lang -ne 0 ]; then
  if [ -z "$opt_db" ]; then
    opt_db="test_openerp"
    if [ $opt_stop -gt 0 -a $opt_keep -eq 0 ]; then
      drop_db=1
    fi
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
if [ $opt_verbose -gt 0 -o $opt_dry_run -gt 0 -o $opt_touch -gt 0 ]; then
  echo "cp $confn ~/.openerp_serverrc"
fi

if [ $opt_dry_run -eq 0 ]; then
  cp $confn ~/.openerp_serverrc
  sed -ie 's:^logfile *=.*:logfile = False:' ~/.openerp_serverrc
  if [ -n "$opt_xport" ]; then
    sed -ie "s:^xmlrpc_port *=.*:xmlrpc_port = $opt_xport:" ~/.openerp_serverrc
  fi
  if [ -n "$opt_dbuser" ]; then
    sed -ie "s:^db_user *=.*:db_user = $opt_dbuser:" ~/.openerp_serverrc
  fi
  if [ $opt_verbose -gt 0 ]; then
    vim ~/.openerp_serverrc
  fi
fi
if [ $opt_touch -eq 0 ]; then
  if [ $drop_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "pg_db_active -a $opt_db; dropdb -U$opt_dbuser --if-exists $opt_db"
    fi
    pg_db_active -a $opt_db; dropdb -U$opt_dbuser --if-exists $opt_db
  fi
  if [ $create_db -gt 0 ]; then
    if [ $opt_verbose -gt 0 ]; then
      echo "createdb -U$opt_dbuser $opt_db"
    fi
    createdb -U$opt_dbuser $opt_db
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
        echo "dropdb -U$opt_dbuser --if-exists $opt_db"
      fi
      dropdb -U$opt_dbuser --if-exists $opt_db
    fi
  fi
  if [ $opt_exp -ne 0 ]; then
    echo "Translation exported to '$src' file"
  elif [ $opt_imp -ne 0 ]; then
    echo "Translation imported from '$src' file"
  fi
fi
