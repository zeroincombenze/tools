#! /bin/bash
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2018-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 1.0.2.7
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
HOME_DEV="$HOME/devel"
[[ -x $TDIR/../bin/python ]] && PYTHON=$(readlink -f $TDIR/../bin/python) || [[ -x $TDIR/python ]] && PYTHON="$TDIR/python" || PYTHON="python"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\no=os.path\nHOME=os.environ.get('HOME');t=o.join(HOME,'tools')\nn=o.join(HOME,'pypi') if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME,HOME_DEV, 'pypi')\nd=HOME_DEV if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME_DEV,'venv')\ndef apl(l,p,b):\n if p:\n  p2=o.join(p,b,b)\n  p1=o.join(p,b)\n  if o.isdir(p2):\n   l.append(p2)\n  elif o.isdir(p1):\n   l.append(p1)\nl=[TDIR]\nv=''\nfor x in sys.path:\n if not o.isdir(t) and o.isdir(o.join(x,'tools')):\n  t=o.join(x,'tools')\n if not v and o.basename(x)=='site-packages':\n  v=x\nfor x in os.environ['PATH'].split(':'):\n if x.startswith(d):\n  d=x\n  break\nfor b in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(d):\n  apl(l,d,b)\n elif TDIR.startswith(n):\n  apl(l,n,b)\n apl(l,v,b)\n apl(l,t,b)\nl=l+os.environ['PATH'].split(':')\ntdir=o.dirname(TDIR)\np=set()\npa=p.add\np=[x for x in l if x and (x.startswith(HOME) or x.startswith(HOME_DEV) or x.startswith(tdir)) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found in <$PYPATH>!"
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

DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=1.0.2


evaluate_params() {
    local val prc minconn
    [[ $opt_branch =~ ^1[123456789] ]] && minconn=64 || minconn=32
    if [[ $opt_nopsql -ne 0 ]]; then
        ((AVAI_MEM=(CUR_MEM*3)/4))
    elif [[ $opt_huge -ne 0 ]]; then
        ((AVAI_MEM=(CUR_MEM+2)/3))
    else
        ((AVAI_MEM=(CUR_MEM+3)/4))
    fi
    ((REQ_WRKS=(NUSER+WRKS4CPU-1)/WRKS4CPU))
    ((MAX_WRKS=CUR_NCPU*2+opt_cw))
    ((REQ_CPU=((REQ_WRKS+opt_cw)+1)/2))
    [ $REQ_WRKS -gt $MAX_WRKS ] && WK_WORKERS=$MAX_WRKS || WK_WORKERS=$REQ_WRKS
    [ $no_workers -ne 0 ] && WK_WORKERS=1
    ((MAX_HWRK=(MAX_WRKS+4)/5))
    ((MAX_LWRK=MAX_WRKS-MAX_HWRK))
    ((REQ_HWRK=(REQ_WRKS+4)/5))
    ((REQ_LWRK=REQ_WRKS-REQ_HWRK))
    ((HWRK=(WK_WORKERS+4)/5))
    ((LWRK=WK_WORKERS-HWRK))
    [[ $no_workers -eq 0 ]] && prc=2 || prc=$PRC4WRK
    ((REQ_AVAI_MEM=REQ_HWRK*MEM4HWRK*prc+REQ_LWRK*MEM4LWRK*prc))
    [[ $REQ_AVAI_MEM -gt $AVAI_MEM ]] && WK_AVAI_MEM=$AVAI_MEM || WK_AVAI_MEM=$REQ_AVAI_MEM
    [[ $no_workers -ne 0 ]] && ((MAX_HLIMIT=AVAI_MEM)) || (((MAX_HLIMIT=AVAI_MEM+2)/3))
    [[ $MAX_HLIMIT -lt $MEM4HWRK ]] && MAX_HLIMIT=$MEM4HWRK
    [[ $MAX_HLIMIT -lt $MIN_HLIMIT ]] && MAX_HLIMIT=$MIN_HLIMIT
    [[ $MAX_HLIMIT -gt $AVAI_MEM ]] && MAX_HLIMIT=$AVAI_MEM
    ((MAX_LLIMIT=AVAI_MEM*2/MAX_WRKS))
    ((val=MAX_HLIMIT*3/4))
    [[ $MAX_LLIMIT -gt $val ]] && MAX_LLIMIT=$val
    ((val=MAX_HLIMIT/2))
    [[ $MAX_LLIMIT -lt $val ]] && MAX_LLIMIT=$val
    [[ $no_workers -ne 0 ]] && ((REQ_HLIMIT=REQ_AVAI_MEM)) || (((REQ_HLIMIT=REQ_AVAI_MEM+2)/3))
    [[ $REQ_HLIMIT -lt $MEM4HWRK ]] && REQ_HLIMIT=$MEM4HWRK
    [[ $REQ_HLIMIT -lt $MIN_HLIMIT ]] && REQ_HLIMIT=$MIN_HLIMIT
    ((REQ_LLIMIT=REQ_AVAI_MEM*2/REQ_WRKS))
    ((val=REQ_HLIMIT*3/4))
    [[ $REQ_LLIMIT -gt $val ]] && REQ_LLIMIT=$val
    ((val=REQ_HLIMIT/2))
    [[ $REQ_LLIMIT -lt $val ]] && REQ_LLIMIT=$val
    if [[ $REQ_AVAI_MEM -gt $AVAI_MEM ]]; then
        [[ $no_workers -ne 0 ]] && ((WK_HLIMIT=AVAI_MEM)) || (((WK_HLIMIT=AVAI_MEM+2)/3))
        ((WK_LLIMIT=AVAI_MEM*2/WK_WORKERS))
    else
        [[ $no_workers -ne 0 ]] && ((WK_HLIMIT=REQ_AVAI_MEM)) || (((WK_HLIMIT=REQ_AVAI_MEM+2)/3))
        ((WK_LLIMIT=REQ_AVAI_MEM*2/WK_WORKERS))
    fi
    [[ $WK_HLIMIT -lt $MEM4HWRK ]] && WK_HLIMIT=$MEM4HWRK
    [[ $WK_HLIMIT -gt $AVAI_MEM ]] && WK_HLIMIT=$AVAI_MEM
    [[ $WK_HLIMIT -lt $MIN_HLIMIT ]] && WK_HLIMIT=$MIN_HLIMIT
    ((val=WK_HLIMIT*3/4))
    [[ $WK_LLIMIT -gt $val ]] && WK_LLIMIT=$val
    ((val=WK_HLIMIT/2))
    [[ $WK_LLIMIT -lt $val ]] && WK_LLIMIT=$val
    [[ $no_workers -eq 0 ]] && ((MAX_PG_DBCONN=(NUSER/16+1)*32)) || ((MAX_PG_DBCONN=(NUSER/16+1)*16))
    ((MAX_DBCONN=MAX_PG_DBCONN))
    [[ $MAX_PG_DBCONN -gt $CUR_PG_DBCONN ]] && ((MAX_DBCONN=CUR_PG_DBCONN))
    [[ $MAX_DBCONN -gt $max_dbconn ]] && MAX_DBCONN=$max_dbconn
    [[ $MAX_DBCONN -lt $minconn ]] && MAX_DBCONN=$minconn
    [[ $no_workers -eq 0 ]] && ((REQ_PG_DBCONN=(NUSER/16+1)*32)) || ((REQ_PG_DBCONN=(NUSER/16+1)*16))
    ((REQ_DBCONN=REQ_PG_DBCONN))
    [[ $REQ_PG_DBCONN -gt $CUR_PG_DBCONN ]] && ((REQ_DBCONN=CUR_PG_DBCONN))
    [[ $no_workers -eq 0 ]] && ((WK_PG_DBCONN=(NUSER/16+1)*32)) || ((WK_PG_DBCONN=(NUSER/16+1)*16))
    [[ $REQ_DBCONN -lt $minconn ]] && REQ_DBCONN=$minconn
    ((WK_DBCONN=WK_PG_DBCONN))
    [[ $WK_PG_DBCONN -gt $CUR_PG_DBCONN ]] && ((WK_DBCONN=CUR_PG_DBCONN))
    [[ $WK_PG_DBCONN -gt $CUR_PG_DBCONN ]] && WK_PG_DBCONN=$CUR_PG_DBCONN
    [[ $WK_DBCONN -lt $minconn ]] && WK_DBCONN=$minconn
    [[ $WK_WORKERS -lt 2 ]] && WK_WORKERS=0
    [[ $WK_WORKERS -gt 0 ]] && PROXY_MODE="True" || PROXY_MODE="False"
    [[ $WK_WORKERS -le 1 ]] && TIME_CPU=7200 || TIME_CPU=2400
    [[ $WK_WORKERS -le 1 ]] && TIME_REAL=14400 || TIME_REAL=4800
    ((MAX_NUSER=MAX_WRKS*WRKS4CPU))
    if [[ $opt_nopsql -ne 0 ]]; then
        ((RAM=REQ_AVAI_MEM/3*4))
    elif [[ $opt_huge -ne 0 ]]; then
        ((RAM=REQ_AVAI_MEM*3))
    else
        ((RAM=REQ_AVAI_MEM*4))
    fi
}

OPTOPTS=(h        b          C        c      D          K        H        L          M       m         n           N          p          S          V           v)
OPTDEST=(opt_help opt_branch opt_cpu  confn  max_dbconn opt_cw   opt_huge opt_lpport opt_mem opt_multi opt_dry_run no_workers opt_nopsql opt_sparse opt_version opt_verbose)
OPTACTI=("+"      "="        "="      "=>"   "="        "="      1        "="        "="     1         1           1          1          1          "*>"        "+")
OPTDEFL=(0        "12.0"     ""       ""     100        1        0        ""         ""      0         0           0          0          0          ""          -1)
OPTMETA=("help"   "branch"   "number" "file" "number"   "number" ""       "port"     "MB"    ""        ""          ""         ""         ""         ""          "")
OPTHELP=("this help"\
 "branches: may be one or more of 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 or 14.0"\
 "# of cpu to evaluate"\
 "odoo configuration file"\
 "max odoo db connection"\
 "# of cron workers (def=1)"\
 "huge database"\
 "long polling port (def=8072)"\
 "MB of memory to evaluate"\
 "multi-instance odoo environment"\
 "do nothing (dry-run)"\
 "disable workers"\
 "psql server run in separate machine"\
 "multi sparse db"\
 "show version"\
 "verbose mode")
OPTARGS=(NUSER)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
[[ $opt_verbose -eq -1 ]] && opt_verbose=1
if [[ $opt_help -gt 0 ]]; then
  print_help "Update Odoo configuration file to best performance"\
  "(C) 2018-2021 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi
discover_multi
odoo_vid=$(echo ""|grep "^addons_path *=.*" $confn|tr -d " "|awk -F= '{print $2}'|awk -F, '{print $1}')
b=$(basename $odoo_vid)
[[ $b == "addons" ]] && odoo_vid=$(dirname $odoo_vid)
CUR_NUSER=$(echo ""|grep -E "^# .antoniov.*Workers are set for [0-9]+ users" $confn|grep -Eo "[0-9]+"|tail -n1)
[[ -z "$CUR_NUSER" ]] && CUR_NUSER=0
if [[ -n "$NUSER" && ! $NUSER =~ ^[0-9]+$ ]]; then
    echo "Invalid # of user supplied. Please issue a valid number or leave empty to get current value!!"
    exit 1
fi
# Odoo constants
MIN_HLIMIT=1792
if [[ $opt_sparse -ne 0 ]]; then
    WRKS4CPU=10
elif [[ $opt_huge -ne 0 ]]; then
    WRKS4CPU=8
else
    WRKS4CPU=6
fi
MEM4WRK=640
if [[ $opt_huge -ne 0 ]]; then
    ((MEM4HWRK=MEM4WRK*17/7))
    ((MEM4LWRK=MEM4WRK/2))
else
    ((MEM4HWRK=MEM4WRK*8/5))
    ((MEM4LWRK=MEM4WRK/4))
fi
if [[ $no_workers -eq 0 ]]; then
    PRC4WRK=64
elif [[ $opt_huge -eq 0 ]]; then
    PRC4WRK=8
else
    PRC4WRK=4
fi
# Detected or simulated values
CUR_LPPORT=$(echo ""|grep "^longpolling_port *=.*" $confn|awk -F= '{print $2}'|grep -Eo "[0-9]+")
[[ -n $opt_lpport ]] && WK_LPPORT=$opt_lpport || WK_LPPORT=$CUR_LPPORT
[[ -z $WK_LPPORT || $WK_LPPORT == "0" ]] && WK_LPPORT=$(build_odoo_param LPPORT $odoo_vid)
[[ -z "$WK_LPPORT" ]] && WK_LPPORT=8072
[[ -z "$NUSER" && $CUR_NUSER -ne 0 ]] && NUSER=$CUR_NUSER
[[ -z "$NUSER" ]] && NUSER=16
[[ $NUSER -lt 2 ]] && NUSER=2
[[ -n "$opt_cpu" ]] && CUR_NCPU=$opt_cpu || CUR_NCPU="$(lscpu|grep "^CPU.s.:"|awk -F: '{print $2}')"
CUR_NCPU=${CUR_NCPU// /}
[[ -n "$opt_mem" ]] && CUR_MEM=$opt_mem || CUR_MEM=$(free -m|grep "Mem:"|awk '{print $2}')
CUR_PG_DBCONN=$(pg_db_active -s)
[[ -z "$CUR_PG_DBCONN" ]] && CUR_PG_DBCONN=100
[[ $opt_cw -lt 1 ]] && opt_cw=1
[[ $opt_cw -gt 2 ]] && opt_cw=2
cur_proxy_mode=$(echo ""|grep "^proxy_mode *=.*" $confn|awk -F= '{print $2}')
[[ -z "$cur_proxy_mode" ]] && cur_proxy_mode=False
cur_time_cpu=$(echo ""|grep "^limit_time_cpu *=.*" $confn|grep -Eo "[0-9]+")
[[ -z "$cur_time_cpu" ]] && cur_time_cpu=60
cur_time_real=$(echo ""|grep "^limit_time_real *=.*" $confn|grep -Eo "[0-9]+")
[[ -z "$cur_time_real" ]] && cur_time_real=120
CUR_HWRK=$(echo "2147483648"|grep "^limit_memory_hard *=.*" $confn|grep -Eo "[0-9]+")
((CUR_HLIMIT=(CUR_HWRK+1048575)/1048576))
CUR_LWRK=$(echo "1610612736"|grep "^limit_memory_soft *=.*" $confn|grep -Eo "[0-9]+")
((CUR_LLIMIT=(CUR_LWRK+1048575)/1048576))
CUR_WRKS=$(echo ""|grep "^workers *=.*" $confn|grep -Eo "[0-9]+")
[[ -z "$CUR_WRKS" ]] && CUR_WRKS=0
CUR_DBCONN=$(echo ""|grep "^db_maxconn *=.*" $confn|grep -Eo "[0-9]+")
[[ -z "$CUR_DBCONN" ]] && CUR_DBCONN=64
#
evaluate_params
#
[[ $CUR_NCPU -lt $REQ_CPU ]] && STS_NCPU="  <-- <CPU>"
[[ $WK_AVAI_MEM -lt $REQ_AVAI_MEM ]] && STS_MEM="<-- <RAM>"
[[ $CUR_PG_DBCONN -lt $REQ_PG_DBCONN ]] && STS_DBC="   <-- <CONN>"
[[ $WK_HLIMIT -gt $AVAI_MEM ]] && STS_HL="<-- <MEM>"
#
printf "                      Detected      Max Required  Applied\n"
printf "# concurrent users.:  %8d %8d %8d\n" $CUR_NUSER $MAX_NUSER $NUSER
printf "# CPU..............:  %8d          %8d           %s\n" $CUR_NCPU $REQ_CPU "$STS_NCPU"
printf "Available memory...:  %8d %8d %8d %8d MB %s\n" $CUR_MEM $AVAI_MEM $REQ_AVAI_MEM $WK_AVAI_MEM "$STS_MEM"
printf "High limit memory..:  %8d %8d %8d %8d MB %s\n" $CUR_HLIMIT $MAX_HLIMIT $REQ_HLIMIT $WK_HLIMIT "$STS_HL"
printf "Low limit memory...:  %8d %8d %8d %8d MB\n" $CUR_LLIMIT $MAX_LLIMIT $REQ_LLIMIT $WK_LLIMIT
printf "# workers..........:  %8d %8d %8d %8d\n" $CUR_WRKS $MAX_WRKS $REQ_WRKS $WK_WORKERS
printf "# hard workers.....:           %8d %8d %8d\n" $MAX_HWRK $REQ_HWRK $HWRK
printf "# soft workers.....:           %8d %8d %8d\n" $MAX_LWRK $REQ_LWRK $LWRK
printf "# DB connections...:  %8d %8d %8d %8d\n" $CUR_DBCONN $MAX_DBCONN $REQ_DBCONN $WK_DBCONN
printf "# psql connections.:  %8d %8d %8d %8d  %s\n" $CUR_PG_DBCONN $MAX_PG_DBCONN $REQ_PG_DBCONN $WK_PG_DBCONN "$STS_DBC"
printf "longpolling_port...:  %8d                   %8d\n" $CUR_LPPORT $WK_LPPORT
printf "Proxy mode.........:  %8.8s                   %8.8s\n" $cur_proxy_mode $PROXY_MODE
printf "limit time CPU.....:  %8d                   %8d\n" $cur_time_cpu $TIME_CPU
printf "limit time real....:  %8d                   %8d\n" $cur_time_real $TIME_REAL
if [ $opt_nopsql -eq 0 ]; then
((PSQL_MEM=(CUR_MEM*3)/4))
printf "Memory reserved to postgresql server...........: %8d\n" $PSQL_MEM
fi
if [ $CUR_NCPU -lt $REQ_CPU ]; then
    echo "*<CPU>* Warning! You should increase the # of CPU to $REQ_CPU! ***"
fi
if [[ $WK_AVAI_MEM -lt $REQ_AVAI_MEM ]]; then
    echo "*<RAM>* Warning! You should increase the physical memory to $RAM! ***"
fi
if [ $WK_HLIMIT -gt $AVAI_MEM ]; then
    echo "*<MEM>* Warning! System could crash with big data! ***"
fi
if [ $CUR_PG_DBCONN -lt $REQ_PG_DBCONN ]; then
   echo "*<CONN>* Warning! You should increase postgresql max connections to $REQ_PG_DBCONN! ***"
fi

((MEM_HARD=WK_HLIMIT*1024*1024))
((MEM_SOFT=WK_LLIMIT*1024*1024))
if [[ -n "$confn" ]]; then
    echo "Update file $confn ..."
    grep -E "^# .*Workers are set for [0-9]+ users" $confn
    if [ $? -ne 0 ]; then
        run_traced "sed \"/^workers *=.*/i # [antoniov: $(date +%Y-%m-%d)] Workers are set for $NUSER users\" -i $confn"
    else
        run_traced "sed -re \"s/^# .*Workers are set for [0-9]+ users/# [antoniov: $(date +%Y-%m-%d)] Workers are set for $NUSER users/\" -i $confn"
    fi
    run_traced "sed -e \"s/^limit_memory_hard *=.*/limit_memory_hard = $MEM_HARD/\" -i $confn"
    run_traced "sed -e \"s/^limit_memory_soft *=.*/limit_memory_soft = $MEM_SOFT/\" -i $confn"
    run_traced "sed -e \"s/^workers *=.*/workers = $WK_WORKERS/\" -i $confn"
    run_traced "sed -e \"s/^db_maxconn *=.*/db_maxconn = $WK_DBCONN/\" -i $confn"
    run_traced "sed -e \"s/^proxy_mode *=.*/proxy_mode = $PROXY_MODE/\" -i $confn"
    run_traced "sed -e \"s/^longpolling_port *=.*/longpolling_port = $WK_LPPORT/\" -i $confn"
    run_traced "sed -e \"s/^limit_time_cpu *=.*/limit_time_cpu = $TIME_CPU/\" -i $confn"
    run_traced "sed -e \"s/^limit_time_real *=.*/limit_time_real = $TIME_REAL/\" -i $confn"
    run_traced "sed -e \"s/^logrotate *=.*/logrotate = True/\" -i $confn"
    echo "You should restart odoo with a comand like this one"
    echo "sudo systemctl restart odoo"
fi
