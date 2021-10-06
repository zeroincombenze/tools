#! /bin/bash
# -*- coding: utf-8 -*-

# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
<<<<<<< HEAD:odoo_score/run_odoo_debug.sh
PYPATH=""
for p in $TDIR $TDIR/.. $TDIR/../.. $HOME/venv_tools/bin $HOME/venv_tools/lib $HOME/tools; do
  [[ -d $p ]] && PYPATH=$(find $(readlink -f $p) -maxdepth 3 -name z0librc)
  [[ -n $PYPATH ]] && PYPATH=$(dirname $PYPATH) && break
done
PYPATH=$(echo -e "import os,sys;p=[os.path.dirname(x) for x in '$PYPATH'.split()];p.extend([x for x in os.environ['PATH'].split(':') if x not in p and x.startswith('$HOME')]);p.extend([x for x in sys.path if x not in p]);print(' '.join(p))"|python)
=======
[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\nHOME=os.environ.get('HOME');y=os.path.join(HOME_DEV,'pypi');t=os.path.join(HOME,'tools')\ndef apl(l,p,x):\n  d2=os.path.join(p,x,x)\n  d1=os.path.join(p,x)\n  if os.path.isdir(d2):\n   l.append(d2)\n  elif os.path.isdir(d1):\n   l.append(d1)\nl=[TDIR]\nfor x in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(y):\n  apl(l,y,x)\n elif TDIR.startswith(t):\n  apl(l,t,x)\nl=l+os.environ['PATH'].split(':')\np=set()\npa=p.add\np=[x for x in l if x and x.startswith(HOME) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|python)
>>>>>>> stash:odoo_score/run_odoo_debug
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0lib/z0librc ]]; then
    . $d/z0lib/z0librc
    Z0LIBDIR=$d/z0lib
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo")
if [[ -z "$ODOOLIBDIR" ]]; then
  echo "Library file odoorc not found!"
  exit 72
fi
. $ODOOLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=$ODOOLIBDIR"

__version__=1.0.3

run_traced_debug() {
    if [ $opt_verbose -gt 1 ]; then
        run_traced "$1"
    elif [ $opt_dry_run -eq 0 ]; then
        eval $1
    fi
}

check_for_modules() {
    local mods r xi xu XXX
    OPTI=
    xi=-i
    OPTU=
    xu=-u
    XXX=
    if [[ $opt_modules == "all" ]]; then
        OPTU="-uall"
    else
        mods=${opt_modules//,/ }
        for m in $mods; do
            r=$(psql -U$DB_USER $opt_db -tc "select state from ir_module_module where name='$m'" 2>/dev/null)
            if [[ $r =~ uninstallable ]]; then
                XXX="$XXX $m"
            elif [[ $r =~ uninstalled ]]; then
                OPTI="$OPTI$xi$m"
                xi=,
            elif [[ $r =~ installed ]]; then
                OPTU="$OPTU$xu$m"
                xu=,
            elif [[ $opt_force -ne 0 ]]; then
                OPTI="$OPTI$xi$m"
                OPTU="$OPTU$xu$m"
                xu=,
            else
                XXX="$XXX $m"
            fi
        done
    fi
    [[ -n $XXX ]] && echo "Modules $XXX not found!" && exit 1
}



OPTOPTS=(h        B       b          c        d        e       f         k        i       I       l        L        m           M         n           o         O      p        s        T        t         U          u       V           v           w       W        x)
OPTDEST=(opt_help opt_dbg opt_branch opt_conf opt_db   opt_exp opt_force opt_keep opt_imp opt_xtl opt_lang opt_llvl opt_modules opt_multi opt_dry_run opt_ofile opt_ou opt_odir opt_stop opt_test opt_touch opt_dbuser opt_upd opt_version opt_verbose opt_web opt_venv opt_rport)
OPTACTI=(1        1       "=>"       "="      "="      1       1         1        1       1       1        "="      "="         1         1           "="       1      "="      1        1        1         "="        1       "*>"        "+"         1       1        "=")
OPTDEFL=(1        0       ""         ""       ""       0       0         0        0       0       0        ""       ""          -1        0           ""        0      ""       0        0        0         ""         0       ""          -1          0       0        "")
OPTMETA=("help"   ""      "branch"   "fname"  "dbname" ""      ""        ""       ""      ""      ""       "level"  "modules"   ""        "no op"     "file"    ""     "dir"    ""       ""       "touch"   "user"     ""      "version"   "verbose"   0       ""       "port")
OPTHELP=("this help"
    "debug mode"
    "odoo branch (version id)"
    "configuration file"
    "db name to test,translate o upgrade (require -m switch)"
    "export it translation (conflict with -i -u -I)"
    "force update or install modules or default parameters"
    "do not create new DB and keep it after run"
    "import it translation (conflict with -e -u -I)"
    "install module (conflict with -e -i -u)"
    "load it language"
    "set log level: may be info or debug"
    "modules to test, translate or upgrade"
    "multi-version odoo environment"
    "do nothing (dry-run)"
    "output file (if export multiple modules)"
    "use openupgrade, if avaiable"
    "odoo root path"
    "stop after init"
    "execute odoo test on module"
    "touch config file, do not run odoo"
    "db username"
    "upgrade module (conflict with -e -i -I)"
    "show version"
    "verbose mode"
    "run as web server"
    "run virtualenv if avaiable"
    "set odoo xmlrpc port")
OPTARGS=(odoo_vid)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
    echo "$__version__"
    exit 0
fi
if [[ $opt_help -gt 0 ]]; then
    print_help "Run odoo for debug mode" \
        "(C) 2015-2021 by zeroincombenze(R)\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
    exit 0
fi
[[ -n "$opt_branch" && -z "$odoo_vid" ]] && odoo_vid=$opt_branch
discover_multi
odoo_fver=$(build_odoo_param FULLVER $odoo_vid)
odoo_ver=$(build_odoo_param MAJVER $odoo_fver)
[[ -n "$opt_odir" ]] && odoo_root=$($READLINK -f $opt_odir) || odoo_root=$(build_odoo_param ROOT $odoo_vid search)
[[ -n "$opt_conf" ]] && CONFN=$opt_conf || CONFN=$(build_odoo_param CONFN $odoo_vid search)
LCONFN=$(build_odoo_param LCONFN $odoo_vid)
script=$(build_odoo_param BIN $odoo_root search)
if [[ -z "$script" ]]; then
    echo "! No odoo script found!!"
    exit 1
fi
ODOO_RUNDIR=$(dirname $script)
VDIR=$(build_odoo_param VDIR $odoo_root)
GIT_ORGNM=$(build_odoo_param GIT_ORGNM $odoo_root)
manifest=$(build_odoo_param MANIFEST $odoo_vid)
[[ $opt_verbose -gt 0 && -n "$VDIR" ]] && echo "# Found $VDIR virtual directory"

create_db=0
drop_db=0
depmods=""
if [[ -n "$opt_rport" ]]; then
    RPCPORT=$opt_rport
elif [[ $opt_test -ne 0 ]]; then
    RPCPORT=$(build_odoo_param RPCPORT $odoo_vid DEBUG)
elif [[ -z "$CONFN" || ( $opt_force -ne 0 && $opt_web -ne 0 ) ]]; then
    RPCPORT=$(build_odoo_param RPCPORT $odoo_vid $GIT_ORGNM)
else
    RPCPORT=$(grep ^xmlrpc_port $CONFN | awk -F= '{print $2}' | tr -d " ")
fi
if [[ -n "$opt_dbuser" ]]; then
    DB_USER=$opt_dbuser
elif [[ -z "$CONFN" || $opt_force -ne 0 ]]; then
  if [[ $opt_web -ne 0 ]]; then
      DB_USER=$(build_odoo_param DB_USER $odoo_vid $GIT_ORGNM)
  else
      DB_USER=$(build_odoo_param DB_USER $odoo_vid DEBUG)
  fi
else
  DB_USER=$(grep ^db_user $CONFN | awk -F= '{print $2}' | tr -d " ")
fi

if [[ $opt_test -ne 0 ]]; then
    opt_web=0
    opt_lang=0 opt_exp=0 opt_imp=0
    opt_upd=0 opt_stop=1
    opt_xtl=1
    opt_dbg=1
    [[ -z "$opt_db" ]] && opt_db="test_openerp_$odoo_ver"
    create_db=1 drop_db=1
elif [[ $opt_lang -ne 0 ]]; then
    opt_keep=1
    opt_stop=1
    [[ -n "$opt_modules" ]] && opt_modules=
elif [[ $opt_exp -ne 0 || $opt_imp -ne 0 ]]; then
    opt_keep=1
    opt_stop=1
    if [[ -z "$opt_modules" ]]; then
        echo "! Missing -m switch!!"
        exit 1
    fi
    if [[ -z "$opt_db" ]]; then
        echo "! Missing -d switch !!"
        exit 1
    fi
elif [[ $opt_upd -ne 0 ]]; then
    opt_keep=1
    if [[ -z "$opt_modules" ]]; then
        echo "! Missing -m switch !!"
        exit 1
    fi
    if [[ -z "$opt_db" ]]; then
        echo "! Missing -d switch!!"
        exit 1
    fi
elif [[ $opt_xtl -ne 0 ]]; then
    if [[ -z "$opt_modules" ]]; then
        echo "Missing -m switch"
        exit 1
    fi
    if [[ -z "$opt_db" ]]; then
        echo "Missing -d switch"
        exit 1
    fi
fi

if [[ -n "$opt_modules" ]]; then
    if [[ $create_db -ne 0 ]]; then
        PL="$(grep ^addons_path $CONFN | awk -F= '{print $2}')"
        [[ -z $PL ]] && echo "No path list found in $CONFN!" && exit 1
        if [[ -z "$($which odoo_dependencies.py 2>/dev/null)" ]]; then
            echo "Test incomplete!"
            echo "File odoo_dependencies.py not found!"
        else
            if [[ "$opt_modules" == "all" ]]; then
                depmods=$(odoo_dependencies.py -RA mod $PL)
            else
                depmods=$(odoo_dependencies.py -RA mod $PL -PM $opt_modules)
            fi
            [[ -z "$depmods" ]] && echo "Modules $opt_modules not found!" && exit 1
            if [[ "$opt_modules" != "all" ]]; then
                depmods=$(odoo_dependencies.py -RA dep $PL -PM $opt_modules)
            fi
            if [[ -n "$depmods" && $opt_test -eq 0 ]]; then
                opt_modules="$opt_modules,$depmods"
            fi
        fi
        OPTS="-i $opt_modules"
        OPTDB=""
        [[ $opt_test -ne 0 ]] && OPTS="$OPTS --test-enable"
    else
        check_for_modules
        OPTSIU="$OPTI $OPTU"
        alt=
        if [[ $opt_exp -ne 0 && -n "$opt_ofile" ]]; then
            src=$($READLINK -f $opt_ofile)
            OPTS="--modules=$opt_modules --i18n-export=$src -lit_IT"
        elif [ $opt_exp -ne 0 -o $opt_imp -ne 0 ]; then
            srcs=$(find -L $odoo_root -not -path '*/__to_remove/*' -type d -name "$opt_modules")
            f=0
            for src in $srcs; do
                if [[ -n "$src" ]]; then
                    if [[ -f $src/i18n/it.po ]]; then
                        src=$src/i18n/it.po
                        [[ $opt_exp -ne 0 ]] && run_traced "cp $src $src.bak"
                        f=1
                        break
                    else
                        alt=$(find -L $src/i18n -name '*.po' | head -n1)
                        src=
                        [[ -n "$alt" ]] && fi=1 && break
                    fi
                fi
            done
            if [[ $f -eq 0 ]]; then
                echo "! Translation file not found!!"
                [[ -n "$alt" ]] && echo ".. may be $alt ?"
                exit 1
            fi
            src=$($READLINK -f $src)
            if [[ $opt_imp -ne 0 ]]; then
                OPTS="--modules=$opt_modules --i18n-import=$src -lit_IT --i18n-overwrite"
            else
                OPTS="--modules=$opt_modules --i18n-export=$src -lit_IT"
            fi
        elif [[ $opt_upd -ne 0 && $opt_xtl -ne 0 ]]; then
            OPTS="$OPTSIU"
            [ $opt_test -ne 0 ] && OPTS="$OPTS --test-enable"
        elif [[ $opt_upd -ne 0 ]]; then
            OPTS="$OPTU"
            [[ $opt_test -ne 0 ]] && OPTS="$OPTS --test-enable"
            [[ -n $OPTI && $opt_verbose -ne 0 ]] && echo "Warning: some module must be installed before"
            [[ -z $OPTU ]] && echo "No module found to update" && exit 1
        elif [[ $opt_xtl -ne 0 ]]; then
            OPTS="$OPTI"
            [ $opt_test -ne 0 ] && OPTS="$OPTS --test-enable"
            [[ -n $OPTU && $opt_verbose -ne 0 ]] && echo "Warning: some module must be updated"
            [[ -z $OPTI ]] && echo "No module found to install" && exit 1
        else
            OPTS="$OPTSIU"
        fi
    fi
else
    if [[ $opt_lang -ne 0 ]]; then
        OPTS=--load-language=it_IT
    else
        OPTS=""
        OPTDB=""
    fi
fi

if [[ -n "$opt_modules" || $opt_upd -ne 0 || $opt_xtl -ne 0 || $opt_exp -ne 0 || $opt_imp -ne 0 || $opt_lang -ne 0 ]]; then
    if [[ -z "$opt_db" ]]; then
        opt_db="test_openerp"
        [[ $opt_stop -gt 0 && $opt_keep -eq 0 ]] && drop_db=1
    fi
fi
OPTDB="$OPTDB --stop-after-init"
if [[ $opt_stop -gt 0 ]]; then
    OPTS="$OPTS --stop-after-init"
    if [[ $opt_exp -eq 0 && $opt_imp -eq 0 && $opt_lang -eq 0 ]]; then
        [[ $opt_test -ne 0 && $odoo_ver -lt 12 ]] && OPTS="$OPTS --test-commit"
    fi
fi
if [[ -n "$opt_db" ]]; then
    OPTS="$OPTS -d $opt_db"
    OPTDB="$OPTDB -d $opt_db"
fi
if [[ $opt_touch -eq 0 ]]; then
    [[ $drop_db -gt 0 ]] && run_traced "pg_db_active -wa $opt_db; dropdb -U$DB_USER --if-exists $opt_db"
    [[ $create_db -gt 0 && $odoo_ver -lt 10 ]] && run_traced "createdb -U$DB_USER $opt_db"
    [[ -n "$VDIR" ]] && ve_root=$VDIR || ve_root=$HOME
    OPT_LLEV=
    FULL_LCONFN="$ve_root/$LCONFN"
    OPT_CONF="--config=$FULL_LCONFN"
    if [[ $opt_dry_run -eq 0 ]]; then
        for f in .openerp_serverrc .odoorc; do
            for d in $HOME $ve_root; do
                [[ -f $d/$f ]] && rm -f $d/$f
            done
        done
    fi
    [[ -f "$CONFN" ]] && run_traced "cp $CONFN $FULL_LCONFN"
    echo "===================================================================="
    if [[ -n "$VDIR" ]]; then
        x=$(date +"%Y-%m-%d %H:%M:%S,000")
        [[ $opt_verbose -gt 0 ]] && echo "$x $$ DAEMON ? $(basename $0): cd $VDIR; source ./bin/activate"
        if [[ $opt_dry_run -eq 0 ]]; then
          cd $VDIR
          source ./bin/activate
        fi
    fi
    [[ ! -f "$CONFN" ]] && run_traced "$script -s --stop-after-init"
    tty -s
    if [[ $? == 0 ]]; then
        run_traced_debug "sed -e \"s|^logfile *=.*|logfile = False|\" -i $FULL_LCONFN"
    else
        run_traced_debug "sed -e \"s|^logfile *=.*|logfile = $ve_root/$$.log|\" -i $FULL_LCONFN"
    fi
    if [[ $opt_dbg -ne 0 ]]; then
        run_traced_debug "sed -e \"s|^limit_time_cpu *=.*|limit_time_cpu = 0|\" -i $FULL_LCONFN"
        run_traced_debug "sed -e \"s|^limit_time_real *=.*|limit_time_real = 0|\" -i $FULL_LCONFN"
    fi
    if [[ -z "$RPCPORT" || "$RPCPORT" == "0" ]]; then
        run_traced_debug "sed -e \"s|^xmlrpc_port *=.*|xmlrpc_port = False|\" -i $FULL_LCONFN"
        [[ $opt_force -ne 0 ]] && OPT_CONF="$OPT_CONF --no-xmlrpc"
    else
        run_traced_debug "sed -e \"s|^xmlrpc_port *=.*|xmlrpc_port = $RPCPORT|\" -i $FULL_LCONFN"
        [[ $opt_force -ne 0 ]] && OPT_CONF="$OPT_CONF --xmlrpc-port=$RPCPORT"
    fi
    if [[ -n "$DB_USER" ]]; then
        run_traced_debug "sed -e \"s|^db_user *=.*|db_user = $DB_USER|\" -i $FULL_LCONFN"
        [[ $opt_force -ne 0 ]] && OPT_CONF="$OPT_CONF --db_user=$DB_USER"
    fi
    if [[ -n "$opt_llvl" ]]; then
        run_traced_debug "sed -e \"s|^log_level *=.*|log_level = $opt_llvl|\" -i $FULL_LCONFN"
        OPT_LLEV="--log-level=$opt_llvl"
    fi
    run_traced_debug "sed -e \"s|^workers *=.*|workers = 0|\" -i $FULL_LCONFN"
    if [[ $create_db -gt 0 ]]; then
        if [[ -n "$depmods" && $opt_test -ne 0 ]]; then
            run_traced "cd $ODOO_RUNDIR; $script $OPTDB $OPT_CONF --log-level=error -i $depmods"
        else
            run_traced "cd $ODOO_RUNDIR; $script $OPTDB $OPT_CONF --log-level=error"
        fi
    fi
    if [ $odoo_ver -lt 10 -a $opt_dry_run -eq 0 -a $opt_exp -eq 0 -a $opt_imp -eq 0 -a $opt_lang -eq 0 ]; then
        OPTS="--debug $OPTS"
    fi
    run_traced "cd $ODOO_RUNDIR; $script $OPT_CONF $OPT_LLEV $OPTS"
    if [[ -n "$VDIR" ]]; then
        x=$(date +"%Y-%m-%d %H:%M:%S,000")
        [ $opt_verbose -gt 0 ] && echo "$x $$ DAEMON ? $(basename $0): deactivate"
        [ $opt_dry_run -eq 0 ] && deactivate
    fi
    if [ $drop_db -gt 0 ]; then
        if [ -z "$opt_modules" -o $opt_stop -eq 0 ]; then
            run_traced "dropdb -U$DB_USER --if-exists $opt_db"
        fi
    fi
    if [ $opt_exp -ne 0 ]; then
        makepo_it.py -b$odoo_vid -m$opt_modules $src
        echo "# Translation exported to '$src' file"
    elif [ $opt_imp -ne 0 ]; then
        echo "# Translation imported from '$src' file"
    fi
fi