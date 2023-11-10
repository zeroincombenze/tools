#! /bin/bash
# -*- coding: utf-8 -*-

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
[[ -z $PYPATH ]] && PYPATH=$(echo -e "import os,sys\no=os.path\na=o.abspath\nj=o.join\nd=o.dirname\nb=o.basename\nf=o.isfile\np=o.isdir\nC=a('"$TDIR"')\nD='"$HOME_DEVEL"'\nif not p(D) and '/devel/' in C:\n D=C\n while b(D)!='devel':  D=d(D)\nN='venv_tools'\nU='setup.py'\nO='tools'\nH=o.expanduser('~')\nT=j(d(D),O)\nR=j(d(D),'pypi') if b(D)==N else j(D,'pypi')\nW=D if b(D)==N else j(D,'venv')\nS='site-packages'\nX='scripts'\ndef pt(P):\n P=a(P)\n if b(P) in (X,'tests','travis','_travis'):\n  P=d(P)\n if b(P)==b(d(P)) and f(j(P,'..',U)):\n  P=d(d(P))\n elif b(d(C))==O and f(j(P,U)):\n  P=d(P)\n return P\ndef ik(P):\n return P.startswith((H,D,K,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))\ndef ak(L,P):\n if P not in L:\n  L.append(P)\nL=[C]\nK=pt(C)\nfor B in ('z0lib','zerobug','clodoo','travis_emulator'):\n for P in [C]+sys.path+os.environ['PATH'].split(':')+[W,R,T]:\n  P=pt(P)\n  if B==b(P) and ik(P):\n   ak(L,P)\n   break\n  elif ik(j(P,B,B)):\n   ak(L,j(P,B,B))\n   break\n  elif ik(j(P,B)):\n   ak(L,j(P,B))\n   break\n  elif ik(j(P,S,B)):\n   ak(L,j(P,S,B))\n   break\nak(L,os.getcwd())\nprint(' '.join(L))\n"|$PYTHON)
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

CFG_init "ALL"
# ODOO_ROOT=$(readlink -f $HOME_DEVEL/..)
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.12

run_traced_debug() {
    if [[ $opt_verbose -gt 1 ]]; then
        run_traced "$1"
    elif [[ $opt_dry_run -eq 0 ]]; then
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
            elif [[ $r =~ (uninstalled|to install) ]]; then
                OPTI="$OPTI$xi$m"
                xi=,
            elif [[ $r =~ (installed|to upgrade) ]]; then
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

coverage_set() {
    if [[ $opt_test -ne 0 && $opt_nocov -eq 0 ]]; then
      COVERAGE_DATA_FILE="$LOGDIR/coverage_${UDI}"
      COVERAGE_PROCESS_START="$LOGDIR/coverage_${UDI}rc"
      coverage_tmpl=$(find $PYPATH -name coveragerc|head -n 1)
      run_traced "cp $coverage_tmpl $COVERAGE_PROCESS_START"
      if [[ $opt_dry_run -eq 0 ]]; then
        grep -Eq "^data_file *=" $COVERAGE_PROCESS_START || sed -E "/^\[run\]/a\\\ndata_file=$COVERAGE_DATA_FILE\n" -i $COVERAGE_PROCESS_START
        [[ $PKGNAME != "midea" && $REPOSNAME == "zerobug-test" ]] && sed -e "/\/tests\//d" -i $COVERAGE_PROCESS_START
      fi
    fi
}

coverage_erase() {
    if [[ -n $COVERAGE_PROCESS_START ]]; then
        [[ -f $COVERAGE_DATA_FILE ]] && rm -f $COVERAGE_DATA_FILE
        [[ $v -ge 6 ]] && run_traced "coverage erase --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE" || run_traced "coverage erase --rcfile=$COVERAGE_PROCESS_START"
    fi
}

coverage_report() {
     if [[ -n $COVERAGE_PROCESS_START ]]; then
      opts="-i"
      for m in ${opt_modules//,/ }; do
        opts="$opts --include=$(find $odoo_root -type d -not -path "*/setup/*" -name $m)/*"
      done
      v=$(coverage --version|grep --color=never -Eo "[0-9]+"|head -n1)
      [[ $v -ge 6 ]] && coverage report --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $opts -m || coverage report --rcfile=$COVERAGE_PROCESS_START $opts -m
    fi
}

set_log_filename() {
    # UDI (Unique DB Identifier): format "{pkgname}_{git_org}{major_version}"
    # UMLI (Unique Module Log Identifier): format "{git_org}{major_version}.{repos}.{pkgname}"
    [[ -n $opt_modules ]] && m="${opt_modules//,/+}" || m="$PKGNAME"
    [[ -z $GIT_ORGID ]] && GIT_ORGID="$(build_odoo_param GIT_ORGID '.')"
    [[ -n $ODOO_GIT_ORGID && $GIT_ORGID =~ $ODOO_GIT_ORGID ]] && UDI="$m" || UDI="$m_${GIT_ORGID}"
    [[ $PRJNAME == "Odoo" && -n $UDI ]] && UDI="${UDI}_${odoo_ver}"
    [[ $PRJNAME == "Odoo" && -z $UDI ]] && UDI="${odoo_ver}"
    [[ $PRJNAME == "Odoo" ]] && UMLI="${GIT_ORGID}${odoo_ver}" || UMLI="${GIT_ORGID}"
    [[ -n "$REPOSNAME" && $REPOSNAME != "OCB" ]] && UMLI="${UMLI}.${REPOSNAME//,/+}"
    [[ -n $m ]] && UMLI="${UMLI}.$m"
    LOGDIR="$PKGPATH/tests/logs"
    export LOGFILE="$LOGDIR/${PKGNAME}_$(date +%Y%m%d).txt"
    [[ -f $LOGFILE ]] && rm -f $LOGFILE
}

check_path_n_branch() {
    # check_path_n_branch(path branch)
    local x
    [[ -n $1 ]] && odoo_fver=$(build_odoo_param FULLVER "$1") || odoo_fver=""
    [[ -n $2 ]] && x=$(build_odoo_param FULLVER "$2") || x=""
    [[ -n $odoo_fver && -n $x && $odoo_fver != $x ]] && echo "Version mismatch -p $1 != -b $2" && exit 1
    [[ -z $odoo_fver ]] && odoo_fver=$x
}

replace_web_module() {
    # replace_web_module()
    local l m param z w woca
    woca="$ODOO_RUNDIR/addons/_web_oca"
    w="$ODOO_RUNDIR/addons/web"
    if [[ $odoo_ver -le 7 && -f $TEST_CONFN ]]; then
        z=""
        l=""
        param=$(grep -E "^server_wide_modules *=.*" $TEST_CONFN|cut -d"=" -f2|tr -d " ")
        [[ $param == "Non" ]] && param=""
        if [[ -n $param ]]; then
          for m in ${param//,/ }; do
              [[ $m =~ ^(web|web_kanban|None)$ ]] && continue
              [[ $m == "web_zeroincombenze" ]] && z=$m || l="$l,$m"
          done
          [[ -n $l ]] && OPTS="$OPTS --load=\"${l:1}\""
        fi
        if [[ -z $z ]]; then
            [[ -L $w ]] && rm -f $w
            [[ -d $woca ]] && mv $woca $w
        else
            z=$(find $ODOO_RUNDIR -type f -path "*/$z/*" -not -path "*/doc/*" -not -path "*/setup/*" -name "__openerp__.py"|head -n 1)
            if [[ -n $z ]]; then
                z=$(dirname $z)
                [[ ! -d $woca ]] && mv $w $woca
                [[ ! -L $w ]] && ln -s $z $w
            fi
        fi
    fi
}

set_confn() {
    [[ $opt_test -ne 0 ]] && run_traced_debug "sed -e \"s|^admin_passwd *=.*|admin_passwd = admin|\" -i $TEST_CONFN"
    [[ $opt_test -ne 0 ]] && run_traced_debug "sed -e \"s|^db_password *=.*|db_password = False|\" -i $TEST_CONFN"
    [[ $opt_test -ne 0 ]] && run_traced_debug "sed -e \"s|^proxy_mode *=.*|proxy_mode = False|\" -i $TEST_CONFN"
    run_traced_debug "sed -e \"s|^server_wide_modules *=|# server_wide_modules =|\" -i $TEST_CONFN"
    if [[ $opt_dae -ne 0 ]]; then
      run_traced_debug "sed -e \"s|^logfile *=.*|logfile = $LOGFILE|\" -i $TEST_CONFN"
    else
      tty -s
      if [[ $? == 0 ]]; then
          run_traced_debug "sed -e \"s|^logfile *=.*|logfile = False|\" -i $TEST_CONFN"
      else
          run_traced_debug "sed -e \"s|^logfile *=.*|logfile = $ve_root/$$.log|\" -i $TEST_CONFN"
      fi
    fi
    if [[ $opt_dbg -ne 0 || $opt_test -ne 0 ]]; then
        run_traced_debug "sed -e \"s|^limit_time_cpu *=.*|limit_time_cpu = 0|\" -i $TEST_CONFN"
        run_traced_debug "sed -e \"s|^limit_time_real *=.*|limit_time_real = 0|\" -i $TEST_CONFN"
    fi
    if [[ $odoo_ver -le 10 ]]; then
        run_traced_debug "sed -e \"s|^xmlrpc_port *=.*|xmlrpc_port = $RPCPORT|\" -i $TEST_CONFN"
        OPT_CONFPORT="--xmlrpc-port=$RPCPORT"
    else
        run_traced_debug "sed -e \"s|^http_port *=.*|http_port = $RPCPORT|\" -i $TEST_CONFN"
        OPT_CONFPORT="--http-port=$RPCPORT"
    fi
    if [[ -n "$DB_USER" ]]; then
        run_traced_debug "sed -e \"s|^db_user *=.*|db_user = $DB_USER|\" -i $TEST_CONFN"
        [[ $opt_force -ne 0 ]] && OPT_CONF="$OPT_CONF --db_user=$DB_USER"
    fi
    if [[ -n "$opt_llvl" ]]; then
        run_traced_debug "sed -e \"s|^log_level *=.*|log_level = $opt_llvl|\" -i $TEST_CONFN"
        OPT_LLEV="--log-level=$opt_llvl"
    fi
    run_traced_debug "sed -e \"s|^workers *=.*|workers = 0|\" -i $TEST_CONFN"
}

wait_process_idle() {
    local c ctr p sz t x
    ctr=0
    [[ ! -f $LOGDIR/odoo.pid ]] && p="" && sleep 3
    [[ -f $LOGDIR/odoo.pid ]] && p=$(cat $LOGDIR/odoo.pid) || echo "Warning! File $LOGDIR/odoo.pid not found!"
    if [[ -n $p ]]; then
        sleep 2
        t=""
        sz=0
        c=0
        for ctr in {0..32}; do
          [[ $t == $(ps --no-headers -o time -p $p) && $sz -eq $(stat -c%s $LOGFILE) ]] && ((c=c+1)) || c=0
          [[ $c -ge 5 && $t == $(ps --no-headers -o time -p $p) && $sz -eq $(stat -c%s $LOGFILE) ]] && break
          t=$(ps --no-headers -o time -p $p)
          sz=$(stat -c%s $LOGFILE)
          sleep 1;
          x=$(date +"%Y-%m-%d %H:%M:%S,000")
          echo -e "$x $p DAEMON $opt_db $(basename $0): Waiting for process $p idle ... # $ctr"
        done
    fi
}

stop_bg_process() {
    local p
    [[ -f $LOGDIR/odoo.pid ]] && p=$(cat $LOGDIR/odoo.pid) || p=""
    [[ -n $p ]] && wait_process_idle $p && run_traced "kill $p" && rm -f $LOGDIR/odoo.pid
}

clean_old_templates() {
    local c d m x
    m=$(odoo_dependencies.py -RA rev $opaths -PB $opt_modules)
    for x in ${m//,/ }; do
        [[ $x == $opt_modules ]] && continue
        d="template_$x"
        [[ $opt_verbose -gt 1 ]] && echo "Searching for $d ..."
        if psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$d"; then
          run_traced "pg_db_active -L -wa \"$d\" && dropdb $opts --if-exists \"$d\""
          c=$(pg_db_active -c "$d")
          [[ $c -ne 0 ]] && echo "FATAL! There are $c other sessions using the database \"$d\"" && continue
          [[ $opt_dry_run -eq 0 ]] && psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$d" && echo "Database \"$d\" removal failed!"
        fi
    done
}

test_with_external_process() {
    local x p s
    echo -e "$x $$ DAEMON $opt_db $p: \e[37;43mRestarting Odoo for concurrent test\e[0m"
    echo -e "$x $$ DAEMON $opt_db $p: \e[37;43mRestarting Odoo for concurrent test\e[0m" >> $LOGFILE
    export TEST_DB="$opt_db"
    export ODOO_VERSION="$odoo_fver"
    echo "\$ export LOGFILE=$LOGFILE"
    echo "\$ export ODOO_RUNDIR=$ODOO_RUNDIR"
    echo "\$ export ODOO_VERSION=$ODOO_VERSION"
    echo "\$ export TEST_CONFN=$TEST_CONFN"
    echo "\$ export TEST_DB=$TEST_DB"
    echo "\$ export TEST_VDIR=$TEST_VDIR"
    OPTS="--pidfile=$LOGDIR/odoo.pid -d $TEST_DB"
    opt_dae=1
    run_odoo_server
    wait_process_idle
    for p in $(ls -1 $PKGPATH/tests/concurrent_test/|grep -E "^test_.*.py$"); do
        ext_test="$PKGPATH/tests/concurrent_test/$p"
        x=$(date +"%Y-%m-%d %H:%M:%S,000")
        echo -e "$x $$ DAEMON $opt_db $p: \e[37;43mStarting $ext_test\e[0m ..."
        echo -e "$x $$ DAEMON $opt_db $p: \e[37;43mStarting $ext_test\e[0m ..." >> $LOGFILE
        run_traced "python $ext_test"
        s=$?
        x=$(date +"%Y-%m-%d %H:%M:%S,000")
        if [[ $s -eq 0 ]]; then
          echo -e "$x $$ DAEMON $opt_db $p: \e[37;43mTest terminated\e[0m"
          echo -e "$x $$ DAEMON $opt_db $p: \e[37;43mTest terminated\e[0m" >> $LOGFILE
        else
          echo -e "$x $$ DAEMON $opt_db $p: \e[31;43mTest terminated with error $s\e[0m"
          echo -e "$x $$ DAEMON $opt_db $p: \e[31;43mTest terminated with error $s\e[0m" >> $LOGFILE
          sts=$s
          break
        fi
    done
    stop_bg_process
}

run_odoo_server() {
    run_traced "pushd $ODOO_RUNDIR &>/dev/null"
    if [[ -n $COVERAGE_PROCESS_START ]]; then
        v=$(coverage --version|grep --color=never -Eo "[0-9]+"|head -n1)
        if [[ $opt_dae -eq 0 ]]; then
            if [[ $v -ge 6 ]]; then
                [[ $opt_dry_run -ne 0 ]] && echo "> coverage run -a --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE"
                [[ $opt_dry_run -eq 0 ]] && echo "\$ coverage run -a --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE"
                [[ $opt_dry_run -eq 0 ]] && coverage run -a --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE
            else
                run_traced "export COVERAGE_DATA_FILE=\"$COVERAGE_DATA_FILE\""
                [[ $opt_dry_run -ne 0 ]] && echo "> coverage run -a --rcfile=$COVERAGE_PROCESS_START $script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE"
                [[ $opt_dry_run -eq 0 ]] && echo "\$ coverage run -a --rcfile=$COVERAGE_PROCESS_START $script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE"
                [[ $opt_dry_run -eq 0 ]] && coverage run -a --rcfile=$COVERAGE_PROCESS_START $script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE
            fi
        else
            if [[ $v -ge 6 ]]; then
                [[ $opt_dry_run -ne 0 ]] && echo "> nohup coverage run -a --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $script $OPT_CONF $OPT_LLEV $OPTS &"
                [[ $opt_dry_run -eq 0 ]] && echo "\$ nohup coverage run -a --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $script $OPT_CONF $OPT_LLEV $OPTS &"
                [[ $opt_dry_run -eq 0 ]] && nohup coverage run -a --rcfile=$COVERAGE_PROCESS_START --data-file=$COVERAGE_DATA_FILE $script $OPT_CONF $OPT_LLEV $OPTS &
            else
                run_traced "# export COVERAGE_DATA_FILE=\"$COVERAGE_DATA_FILE\""
                [[ $opt_dry_run -ne 0 ]] && echo "> nohup coverage run -a --rcfile=$COVERAGE_PROCESS_START $script $OPT_CONF $OPT_LLEV $OPTS &"
                [[ $opt_dry_run -eq 0 ]] && echo "\$ nohup coverage run -a --rcfile=$COVERAGE_PROCESS_START $script $OPT_CONF $OPT_LLEV $OPTS &"
                [[ $opt_dry_run -eq 0 ]] && nohup coverage run -a --rcfile=$COVERAGE_PROCESS_START $script $OPT_CONF $OPT_LLEV $OPTS &
            fi
        fi
    else
        if [[ $opt_dae -eq 0 ]]; then
            [[ $opt_dae -eq 0 ]] && run_traced "$script $OPT_CONF $OPT_LLEV $OPTS 2>&1 | stdbuf -i0 -o0 -e0 tee -a $LOGFILE"
        else
            [[ $opt_dry_run -ne 0 ]] && echo "> $script $OPT_CONF $OPT_LLEV $OPTS &"
            [[ $opt_dry_run -eq 0 ]] && echo "\$ $script $OPT_CONF $OPT_LLEV $OPTS &"
            [[ $opt_dry_run -eq 0 ]] && $script $OPT_CONF $OPT_LLEV $OPTS &
        fi
    fi
    [[ $opt_dae -ne 0 ]] && wait_process_idle
    run_traced "popd &>/dev/null"
}


OPTOPTS=(h        B       b          c        C           d        D       e       f         K       k        i       I       l        L        m           M         n           o         p        P         q           S        s        T        t         U          u       V           v           w       x)
OPTLONG=(help     debug   branch     config   no-coverage database daemon  export  force     no-ext  keep     import  install lang     lint-lev modules     multi     dry-run     ""        path     psql-port quiet       stat     stop     test     ""        db-user    update  version     verbose     web     xmlrpc-port)
OPTDEST=(opt_help opt_dbg opt_branch opt_conf opt_nocov   opt_db   opt_dae opt_exp opt_force opt_nox opt_keep opt_imp opt_xtl opt_lang opt_llvl opt_modules opt_multi opt_dry_run opt_ofile opt_odir opt_qport opt_verbose opt_stat opt_stop opt_test opt_touch opt_dbuser opt_upd opt_version opt_verbose opt_web opt_rport)
OPTACTI=("+"      "+"     "=>"       "=>"     1           "="      1       1       1         1       1        1       1       1        "="      "="         1         1           "="       "="      "="       0           1        1        1        1         "="        1       "*>"        "+"         1       "=")
OPTDEFL=(1        0       ""         ""       0           ""       0       0       0         0       0        0       0       0        ""       ""          -1        0           ""        ""       ""        0           0        0        0        0         ""         0       ""          -1          0       "")
OPTMETA=("help"   ""      "version"  "fname"  ""          "name"   ""      ""      ""        ""      ""       ""      ""      ""       "level"  "modules"   ""        "no op"     "file"    "dir"    "port"    ""          ""       ""       ""       "touch"   "user"     ""      "version"   "verbose"   0       "port")
OPTHELP=("this help"
    "debug mode (-BB debug via pycharm)"
    "odoo branch"
    "odoo configuration file"
    "no use coverage to run test"
    "db name to test,translate o upgrade (require -m switch)"
    "run odoo as daemon"
    "export translation (conflict with -i -u -I -T)"
    "force update or install modules or default parameters or create db template"
    "do not run external test (tests/concurrent_test/test_*.py)"
    "do not create new DB and keep it after run"
    "import translation (conflict with -e -u -I -T)"
    "install module (conflict with -e -i -u -T)"
    "load language"
    "set log level: may be info or debug"
    "modules to test, translate or upgrade"
    "multi-version odoo environment"
    "do nothing (dry-run)"
    "output file (if export multiple modules)"
    "odoo root path"
    "psql port"
    "silent mode"
    "show coverage stats (do not run odoo)"
    "stop after init"
    "execute odoo test on module (conflict with -e -i -I -u)"
    "touch config file, do not run odoo"
    "db username"
    "upgrade module (conflict with -e -i -I -T)"
    "show version"
    "verbose mode"
    "run as web server"
    "set odoo xmlrpc port")
OPTARGS=()

parseoptargs "$@"
if [[ "$opt_version" ]]; then
    echo "$__version__"
    exit 0
fi
if [[ $opt_help -gt 0 ]]; then
    print_help "Run odoo for debug" \
        "(C) 2015-2023 by zeroincombenze(R)\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
    exit 0
fi

[[ $opt_multi -lt 0 ]] && discover_multi
CONFN=""
opaths=""
odoo_root=""
odoo_fver=""
[[ -z $MQT_TEMPLATE_DB ]] && MQT_TEMPLATE_DB="template_odoo"
[[ -z $MQT_TEST_DB ]] && MQT_TEST_DB="test_odoo"
if [[ -n $opt_conf ]]; then
    CONFN=$opt_conf
    [[ ! -f $CONFN ]] && echo "File $CONFN not found!" && exit 1
    opaths="$(grep ^addons_path $CONFN | awk -F= '{print $2}')"
    [[ -z $opaths ]] && echo "No path list found in $CONFN!" && exit 1
    for p in ${opaths//,/ }; do
        [[ -x $p/../odoo-bin || -x $p/../openerp-server ]] && odoo_root=$(readlink -f $p/..) && break
    done
    check_path_n_branch "$odoo_root" "$opt_branch"
    [[ -n $opt_modules && -z $opt_odir ]] && opt_odir=$(find $odoo_root -type d -not -path "*/doc/*" -not -path "*/setup/*" -not -path "*/.*/*" -name $opt_modules)
    if [[ -n $opt_odir ]]; then
      PKGNAME=$(build_odoo_param PKGNAME "$opt_odir")
      PKGPATH=$(build_odoo_param PKGPATH "$opt_odir")
      REPOSNAME=$(build_odoo_param REPOS "$opt_odir")
    else
      REPOSNAME=""
      PKGNAME=""
      PKGPATH=""
    fi
    GIT_ORGID=$(build_odoo_param GIT_ORGID "$odoo_root")
elif [[ -n $opt_odir ]]; then
    [[ ! -d $opt_dir ]] && echo "Path $opt_dir not found!" && exit 1
    odoo_root=$(readlink -f $opt_odir)
    check_path_n_branch "$opt_dir" "$opt_branch"
    PKGNAME=$(build_odoo_param PKGNAME "$opt_odir")
    PKGPATH=$(build_odoo_param PKGPATH "$opt_odir")
    REPOSNAME=$(build_odoo_param REPOS "$opt_odir")
    GIT_ORGID=$(build_odoo_param GIT_ORGID "$opt_odir")
    CONFN=$(build_odoo_param CONFN "$odoo_root" search)
    opaths="$(grep ^addons_path $CONFN | awk -F= '{print $2}')"
    [[ -z $opaths ]] && echo "No path list found in $CONFN!" && exit 1
elif [[ -n $opt_modules || -n $opt_branch ]]; then
    odoo_fver=$(build_odoo_param FULLVER "$opt_branch")
    odoo_root=$(build_odoo_param ROOT "$opt_branch")
    [[ -n $opt_modules ]] && opt_odir=$(find $odoo_root -type d -not -path "*/doc/*" -not -path "*/setup/*" -not -path "*/.*/*" -name $opt_modules)
    [[ -z $opt_odir ]] && opt_odir="$odoo_root"
    PKGNAME=$(build_odoo_param PKGNAME "$opt_odir")
    PKGPATH=$(build_odoo_param PKGPATH "$opt_odir")
    REPOSNAME=$(build_odoo_param REPOS "$opt_odir")
    GIT_ORGID=$(build_odoo_param GIT_ORGID "$opt_odir")
    CONFN=$(build_odoo_param CONFN "$odoo_root" search)
    [[ -f $CONFN ]] && opaths="$(grep ^addons_path $CONFN | awk -F= '{print $2}')" || opaths="$odoo_root"
    [[ -z $opaths ]] && echo "No path list found in $CONFN!" && exit 1
else
    odoo_fver=$(build_odoo_param FULLVER "$PWD")
    odoo_root=$(readlink -f $PWD)
    [[ -z $opt_odir ]] && opt_odir="$odoo_root"
    PKGNAME=$(build_odoo_param PKGNAME "$PWD")
    PKGPATH=$(build_odoo_param PKGPATH "$PWD")
    REPOSNAME=$(build_odoo_param REPOS "$PWD")
    GIT_ORGID=$(build_odoo_param GIT_ORGID "$PWD")
    CONFN=$(build_odoo_param CONFN "$odoo_root" search)
    [[ -f $CONFN ]] && opaths="$(grep ^addons_path $CONFN | awk -F= '{print $2}')" || opaths="$odoo_root"
    [[ -z $opaths ]] && echo "No path list found in $CONFN!" && exit 1
fi
[[ -z $odoo_root || ! -d $odoo_root ]] && echo "Odoo path $odoo_root not found!" && exit 1
odoo_ver=$(build_odoo_param MAJVER $odoo_fver)
LCONFN=$(build_odoo_param LCONFN $odoo_fver)
script=$(build_odoo_param BIN "$odoo_root" search)
[[ -z "$script" ]] && echo "No odoo script found!!" && exit 1
export ODOO_RUNDIR=$(dirname $script)
export TEST_VDIR=$(build_odoo_param VDIR "$odoo_root")
[[ ! -d $TEST_VDIR ]] && export TEST_VDIR=""
[[ $opt_verbose -gt 1 && -n "$TEST_VDIR" ]] && echo "# Found $TEST_VDIR virtual directory"
set_log_filename

if [[ -n $opt_rport ]]; then
    RPCPORT=$opt_rport
elif [[ $opt_test -ne 0 ]]; then
    [[ opt_dbg -gt 1 ]] && RPCPORT=$(build_odoo_param RPCPORT $odoo_fver DEBUG) || RPCPORT=$((($(date +%s) % 46000) + 19000))
elif [[ -f $opt_conf ]]; then
    RPCPORT=$(grep ^http_port $CONFN | awk -F= '{print $2}' | tr -d " ")
    [[ -z "$RPCPORT" ]] && RPCPORT=$(grep ^xmlrpc_port $CONFN | awk -F= '{print $2}' | tr -d " ")
elif [[ $opt_web -ne 0 ]]; then
    RPCPORT=$(build_odoo_param RPCPORT $odoo_fver $GIT_ORGID)
elif [[ -f $CONFN ]]; then
    RPCPORT=$(grep ^http_port $CONFN | awk -F= '{print $2}' | tr -d " ")
    [[ -z "$RPCPORT" ]] && RPCPORT=$(grep ^xmlrpc_port $CONFN | awk -F= '{print $2}' | tr -d " ")
else
    RPCPORT=$(build_odoo_param RPCPORT $odoo_fver $GIT_ORGID)
fi
[[ -z "$RPCPORT" || $RPCPORT -eq 0 ]] && RPCPORT=$(build_odoo_param RPCPORT $odoo_fver $GIT_ORGID)

if [[ -n $opt_dbuser ]]; then
    DB_USER=$opt_dbuser
elif [[ -f $opt_conf || -f $CONFN ]]; then
    DB_USER=$(grep ^db_user $CONFN | awk -F= '{print $2}' | tr -d " ")
else
    DB_USER=$(build_odoo_param DB_USER $odoo_fver $GIT_ORGID)
fi

if [[ -n "$opt_qport" ]]; then
    DB_PORT=$opt_qport
elif [[ -f $CONFN ]]; then
    DB_PORT=$(grep ^db_port $CONFN | awk -F= '{print $2}' | tr -d " ")
    [[ $DB_PORT == "False" ]] && unset DB_PORT
fi

create_db=0
drop_db=0
depmods=""
TEMPLATE=""

if [[ $opt_test -ne 0 ]]; then
    opt_web=0
    opt_lang=0 opt_exp=0 opt_imp=0
    opt_upd=0 opt_stop=1
    opt_xtl=1
    [[ $opt_dbg -ne 0 ]] && opt_nocov=1 || opt_nocov=0
    TEMPLATE="template_${UDI}"
    [[ -z $opt_db && $opt_keep -eq 0 ]] && opt_db="test_${UDI}" && drop_db=1
    [[ -z $opt_db && $opt_keep -ne 0 ]] && opt_db="${MQT_TEST_DB}_${odoo_ver}" && drop_db=0
    create_db=1
    [[ ! -d $ODOO_ROOT/travis_log ]] && run_traced "mkdir $ODOO_ROOT/travis_log"
elif [[ $opt_lang -ne 0 ]]; then
    opt_keep=1
    opt_stop=1
    [[ -n "$opt_modules" ]] && opt_modules=
elif [[ $opt_exp -ne 0 || $opt_imp -ne 0 ]]; then
    opt_keep=1
    opt_stop=1
    [[ -z "$opt_modules" ]] && echo "Missing -m switch!!" && exit 1
    [[ -z "$opt_db" ]] && echo "Missing -d switch !!" && exit 1
elif [[ $opt_upd -ne 0 ]]; then
    opt_keep=1
    [[ -z "$opt_modules" ]] && echo "Missing -m switch!!" && exit 1
    [[ -z "$opt_db" ]] && echo "Missing -d switch !!" && exit 1
elif [[ $opt_xtl -ne 0 ]]; then
    [[ -z "$opt_modules" ]] && echo "Missing -m switch!!" && exit 1
    [[ -z "$opt_db" ]] && echo "Missing -d switch !!" && exit 1
fi

if [[ -n "$opt_modules" ]]; then
    if [[ $create_db -ne 0 ]]; then
        if [[ -z "$($which odoo_dependencies.py 2>/dev/null)" ]]; then
            echo "Test incomplete!"
            echo "File odoo_dependencies.py not found!"
        else
            [[ $opt_verbose -ne 0 ]] && echo "# Searching for module paths ..."
            if [[ "$opt_modules" == "all" ]]; then
                depmods=$(odoo_dependencies.py -RA mod "$opaths")
            else
                depmods=$(odoo_dependencies.py -RA mod "$opaths" -PM $opt_modules)
            fi
            [[ -z "$depmods" ]] && echo "Modules $opt_modules not found!" && exit 1
            if [[ "$opt_modules" != "all" ]]; then
                depmods=$(odoo_dependencies.py -RA dep $opaths -PM $opt_modules)
            fi
            [[ -n "$depmods" && $opt_test -eq 0 ]] && opt_modules="$opt_modules,$depmods"
        fi
        OPTS="-i $opt_modules"
        OPTDB=""
        [[ $opt_test -ne 0 && $odoo_ver -gt 6 ]] && OPTS="$OPTS --test-enable"
        [[ $opt_test -eq 0 && $odoo_ver -eq 6 ]] && OPTS="$OPTS --test-disable"
    else
        check_for_modules
        OPTSIU="$OPTI $OPTU"
        if [[ $opt_exp -ne 0 && -n "$opt_ofile" ]]; then
            src=$(readlink -f $opt_ofile)
            OPTS="--modules=$opt_modules --i18n-export=$src -lit_IT"
        elif [[ $opt_exp -ne 0 || $opt_imp -ne 0 ]]; then
            src=$(find ${opaths//,/ } -maxdepth 1 -type d -name $opt_modules 2>/dev/null|head -n1)
            if [[ -z $src ]]; then
                echo "Translation file not found!!"
                exit 1
            fi
            src=$(readlink -f $src)
            [[ ! -d $src/i18n ]] && echo "No directory $src/i18n found!!" && exit 1
            src="$src/i18n/it.po"
            makepo_it.py -f -b$odoo_fver -m$opt_modules $src
            if [[ $opt_imp -ne 0 ]]; then
                OPTS="--modules=$opt_modules --i18n-import=$src -lit_IT --i18n-overwrite"
            else
                OPTS="--modules=$opt_modules --i18n-export=$src -lit_IT"
            fi
        elif [[ $opt_upd -ne 0 && $opt_xtl -ne 0 ]]; then
            OPTS="$OPTSIU"
            [[ $opt_test -ne 0 ]] && OPTS="$OPTS --test-enable"
        elif [[ $opt_upd -ne 0 ]]; then
            OPTS="$OPTU"
            [[ $opt_test -ne 0 ]] && OPTS="$OPTS --test-enable"
            [[ -n $OPTI && $opt_verbose -ne 0 ]] && echo -e "Warning: some modules must be installed before\n$OPTI"
            [[ -z $OPTU ]] && echo "No module found to update" && exit 1
        elif [[ $opt_xtl -ne 0 ]]; then
            OPTS="$OPTI"
            [[ $opt_test -ne 0 ]] && OPTS="$OPTS --test-enable"
            [[ -n $OPTU && $opt_verbose -ne 0 ]] && echo -e "Warning: some modules must be updated\n$OPTU"
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
        opt_db="$MQT_TEST_DB"
        [[ $opt_stop -gt 0 && $opt_keep -eq 0 ]] && drop_db=1
    fi
fi

ext_test=""
if [[ $opt_nox -eq 0 && $opt_test -ne 0 && -d $PKGPATH/tests/concurrent_test ]]; then
    ext_test=$(ls -1 $PKGPATH/tests/concurrent_test/|grep -E "^test_.*.py$"|head -n1)
fi
[[ -n $ext_test ]] && echo -e "\e[37;43mExternal test $ext_test wil be executed\e[0m"
[[ $opt_dae -ne 0 ]] && OPTDB="$OPTDB --pidfile=$LOGDIR/odoo.pid" || OPTDB="$OPTDB --stop-after-init"

if [[ $opt_stop -gt 0 ]]; then
    [[ $opt_dae -ne 0 ]] && OPTS="$OPTS --pidfile=$LOGDIR/odoo.pid" || OPTS="$OPTS --stop-after-init"
    if [[ $opt_exp -eq 0 && $opt_imp -eq 0 && $opt_lang -eq 0 ]]; then
        [[ $opt_keep -ne 0 && $opt_test -ne 0 && $odoo_ver -lt 12 ]] && OPTS="$OPTS --test-commit"
    fi
fi
[[ $opt_stop -ne 0 || $opt_dae -ne 0 ]] && stop_bg_process
if [[ -n "$opt_db" ]]; then
    OPTS="$OPTS -d $opt_db"
    OPTDB="$OPTDB -d $opt_db"
fi
if [[ $opt_stat -ne 0 ]]; then
    # run only show stats
    if [[ -n "$TEST_VDIR" ]]; then
        coverage_set
        coverage_report
    fi
    exit 0
fi

sts=0
if [[ $opt_touch -eq 0 ]]; then
    [[ -n "$TEST_VDIR" ]] && ve_root=$TEST_VDIR || ve_root=$HOME
    OPT_LLEV=
    [[ $opt_test -ne 0 && ! -d $LOGDIR ]] && mkdir -p $LOGDIR
    [[ $opt_test -ne 0 ]] && export TEST_CONFN="$LOGDIR/${UMLI}.conf" || export TEST_CONFN="$ve_root/$LCONFN"
    [[ $opt_test -gt 1 ]] && export TEST_CONFN="$ve_root/pycharm_odoo.conf"
    OPT_CONF="--config=$TEST_CONFN"
    if [[ $opt_dry_run -eq 0 ]]; then
        for f in .openerp_serverrc .odoorc; do
            for d in $HOME $ve_root; do
                [[ -f $d/$f ]] && rm -f $d/$f
            done
        done
    fi
    [[ -f "$CONFN" ]] && run_traced "cp $CONFN $TEST_CONFN"
    replace_web_module
    [[ ! -f "$CONFN" ]] && run_traced "$script -s --stop-after-init"
    set_confn
    if [[ -n "$TEST_VDIR" ]]; then
      coverage_set
      x=$(date +"%Y-%m-%d %H:%M:%S,000")
      [[ $opt_verbose -gt 0 && $opt_test -eq 0 ]] && echo "$x $$ DAEMON $opt_db $(basename $0): cd $TEST_VDIR && source ./bin/activate"
      [[ -d LOGDIR && ! -f $LOGFILE ]] && touch $LOGFILE
      [[ $opt_verbose -gt 0 && $opt_test -ne 0 ]] && echo "$x $$ DAEMON $opt_db $(basename $0): cd $TEST_VDIR && source ./bin/activate" | tee -a $LOGFILE
      if [[ $opt_dry_run -eq 0 ]]; then
        cd $TEST_VDIR
        source ./bin/activate
        if [[ $opt_test -ne 0 && $opt_nocov -eq 0 ]]; then
          cov=$(which coverage 2>/dev/null)
          [[ -z $cov || ! $cov =~ $HOME ]] && run_traced "pip install coverage"
          cov=$(which coverage 2>/dev/null)
          if [[ -n $cov ]]; then
            v=$(coverage --version|grep --color=never -Eo "[0-9]+"|head -n1)
            [[ $v -lt 5 ]] && run_traced "pip install coverage -U"
          fi
        fi
      fi
    fi

    [[ -n $ODOO_COMMIT_TEST ]] && unset ODOO_COMMIT_TEST
    if [[ $create_db -gt 0 ]]; then
        [[ -n "$DB_PORT" ]] && opts="-U$DB_USER -p$DB_PORT" || opts="-U$DB_USER"
        if [[ $opt_test -ne 0 ]]; then
            if [[ -n "$depmods" ]]; then
                fnparam="$LOGDIR/${UDI}.sh"
                if [[ $opt_force -ne 0 ]] && psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$TEMPLATE"; then
                    run_traced "pg_db_active -L -wa \"$TEMPLATE\" && dropdb $opts --if-exists \"$TEMPLATE\""
                    c=$(pg_db_active -c "$TEMPLATE")
                    [[ $c -ne 0 ]] && echo "FATAL! There are $c other sessions using the database \"$TEMPLATE\"" && exit 1
                    [[ $opt_dry_run -eq 0 ]] && psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$TEMPLATE" && echo "Database \"$TEMPLATE\" removal failed!" && exit 1
                fi
                if [[ $opt_force -ne 0 ]] || ! psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$TEMPLATE"; then
                    [[ $odoo_ver -lt 10 ]] && run_traced "psql -U$DB_USER template1 -c 'create database \"$TEMPLATE\" owner $DB_USER'"
                    [[ $odoo_ver -le 10 ]] && cmd="cd $ODOO_RUNDIR && $script -d$TEMPLATE $OPT_CONF -i $depmods --stop-after-init --no-xmlrpc"
                    [[ $odoo_ver -gt 10 ]] && cmd="cd $ODOO_RUNDIR && $script -d$TEMPLATE $OPT_CONF -i $depmods --stop-after-init --no-http"
                    run_traced "$cmd"
                fi
            fi
            if psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$opt_db"; then
                run_traced "pg_db_active -L -wa \"$opt_db\" && dropdb $opts --if-exists \"$opt_db\""
                c=$(pg_db_active -c \"$opt_db\")
                [[ $c -ne 0 ]] && echo "FATAL! There are $c other sessions using the database \"$opt_db\"" && exit 1
                [[ $opt_dry_run -eq 0 ]] && psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$opt_db" && echo "Database \"$opt_db\" removal failed!" && exit 1
            fi
            if [[ $opt_dry_run -ne 0 ]] || ! psql -U$DB_USER -Atl|cut -d"|" -f1|grep -q "$opt_db"; then
                [[ -n "$depmods" ]] && run_traced "psql -U$DB_USER template1 -c 'create database \"$opt_db\" owner $DB_USER template \"$TEMPLATE\"'"
                [[ -z "$depmods" ]] && run_traced "psql -U$DB_USER template1 -c 'create database \"$opt_db\" owner $DB_USER template template1'"
            fi
        fi
    fi


    [[ $opt_keep -ne 0 && -z $ext_test ]] && export ODOO_COMMIT_TEST="1"
    if [[ $opt_test -ne 0 && $opt_dbg -eq 0 ]]; then
        run_traced "pip list --format=freeze > $LOGDIR/requirements.txt"
        coverage_erase
        run_odoo_server
        [[ -n $ext_test ]] && test_with_external_process
    elif [[ opt_dbg -gt 1 ]]; then
        echo ""
        echo "Now you can test module $opt_modules on pycharm"
        echo ""
        echo "Debug Odoo by pycharm after set configuration \"Debug Odoo $odoo_fver\""
        echo -e "parameters=\"\e[33m$script\e[0m \e[31m$OPT_CONF $OPT_LLEV $OPTS\e[0m\""
        echo ""
        echo "If your test code contains the follow statements"
        echo ""
        echo -e "    \e[33mdef tearDown(self):\e[0m"
        echo -e "        \e[33mself.env.cr.commit()\e[0m  # pylint: disable=invalid-commit"
        echo ""
        echo "you can browse test database from:"
        echo -e "\e[33mhttp://localhost:8069\e[0m or \e[33mhttp://localhost:$(build_odoo_param RPCPORT $odoo_fver)\e[0m"
        echo -e "DB=\e[31m$opt_db\e[0m login: admin/admin"
        echo ""
    else
        run_traced "cd $ODOO_RUNDIR && $script $OPT_CONF $OPT_LLEV $OPTS"
    fi

    if [[ -n "$TEST_VDIR" ]]; then
        x=$(date +"%Y-%m-%d %H:%M:%S,000")
        [[ $opt_verbose -gt 0 && opt_dbg -le 1 ]] && echo "$x $$ DAEMON $opt_db $(basename $0): deactivate"
        [[ $opt_dry_run -eq 0 ]] && deactivate
    fi
    # [[ $opt_test -ne 0 && $opt_keep -eq 0 && -f $TEST_CONFN ]] && rm -f $TEST_CONFN
    [[ -n $ODOO_COMMIT_TEST ]] && unset ODOO_COMMIT_TEST

    if [[ $opt_test -ne 0 && $opt_dbg -eq 0 ]]; then
        if [[ $opt_dry_run -eq 0 ]]; then
            echo -e "\n+===================================================================" | tee -a $LOGFILE
            x="\e[32mSUCCESS!\e[0m"
            grep -Eq "[0-9]+ (ERROR|CRITICAL) $opt_db" $LOGFILE && x="\e[31mFAILED!\e[0m" && sts=11
            grep -Eq "[0-9]+ (ERROR|CRITICAL|WARNING) .*invalid module names.*$opt_modules" $LOGFILE && x="\e[31mFAILED!\e[0m" && sts=11
            echo -e "| please test \e[36m${opt_modules}\e[0m (${odoo_fver}): $x" | tee -a $LOGFILE
            echo -e "+===================================================================\n"  | tee -a $LOGFILE
            [[ $sts -eq 0 ]] && coverage_report | tee -a $LOGFILE
            echo "less -R \$(readlink -f \$(dirname \$0))/$(basename $LOGFILE)" > $LOGDIR/show-log.sh
            chmod +x $LOGDIR/show-log.sh
        else
            run_traced "coverage_report | tee -a $LOGFILE"
        fi
    fi
    if [[ $opt_exp -ne 0 ]]; then
        makepo_it.py -b$odoo_fver -m$opt_modules $src
        echo "# Translation exported to '$src' file"
    elif [[ $opt_imp -ne 0 ]]; then
        echo "# Translation imported from '$src' file"
    fi

    [[ $opt_keep -eq 0 && $opt_dae -ne 0 ]] && stop_bg_process
    if [[ $drop_db -gt 0 ]]; then
        clean_old_templates
        if [[ -z "$opt_modules" || $opt_stop -eq 0 ]]; then
            [[ -n "$DB_PORT" ]] && opts="-U$DB_USER -p$DB_PORT" || opts="-U$DB_USER"
            run_traced "pg_db_active -L -wa \"$opt_db\"; dropdb $opts --if-exists '$opt_db'"
            c=$(pg_db_active -c "$opt_db")
            [[ $c -ne 0 ]] && echo "FATAL! There are $c other sessions using the database \"$opt_db\"" && exit 1
        fi
    fi
fi
exit $sts

