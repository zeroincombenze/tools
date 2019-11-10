__version__=0.3.8.60
# set -x
if [ "$1" == "-h" ]; then
    echo "$0 num_users [confn] [-0|-n|longpolling_port]"
    echo "use -0 to disable workers"
    [ -n "$2" ] && grep -E "^# .*Workers are set for [0-9]+ users" $2
    exit 0
fi
if [ -z "$1" ]; then
    read -p "# of users?: " NUSER
else
    NUSER=$1
fi
no_workers=0
if [ "$2" == "-0" ]; then
    no_workers=1
else
    confn="$2"
fi
[ "$3" == "-0" ] && no_workers=1
longpolling_port=8072
[[ -n "$3" && ! "$3" == "-n" &&  ! "$3" == "-0" ]] && longpolling_port=$3
[ -z "$NUSER" ] && NUSER=32
[ $NUSER -lt 16 ] && NUSER=16
#
NCPU="$(lscpu|grep "^CPU.s.:"|awk -F: '{print $2}')"
NCPU=${NCPU// /}
MEM=$(free -m|grep "Mem:"|awk '{print $2}')
#
((AVAI_MEM=(MEM+3)/4))
((REQ_WRKS=(NUSER+9)/10))
((MAX_WKRS=NCPU*2+1))
[ $REQ_WRKS -gt $MAX_WKRS ] && WORKERS=$MAX_WKRS || WORKERS=$REQ_WRKS
[ $no_workers -ne 0 ] && WORKERS=1
((HWRK=(WORKERS+4)/5))
((LWRK=WORKERS-HWRK))
((WMEM=(HWRK*1024)+(LWRK*150)))
((WRK_MEM=AVAI_MEM*2/WORKERS))
# ((BEST_DB_NUSER=NUSER*WORKERS/2))
((BEST_DB_NUSER=(NUSER*3)/(3+WORKERS)))
[ $BEST_DB_NUSER -lt 32 ] && BEST_DB_NUSER=32
((MAX_NUSER=(3+WORKERS)*BEST_DB_NUSER))
[ $BEST_DB_NUSER -gt 300 ] && DB_NUSER=300 || DB_NUSER=$BEST_DB_NUSER
[ $WORKERS -lt 2 ] && WORKERS=0
[ $WORKERS -gt 0 ] && PROXY_MODE="True" || PROXY_MODE="False"
[ $WORKERS -gt 0 ] && TIME_CPU=600 || TIME_CPU=60
[ $WORKERS -gt 0 ] && TIME_REAL=1200 || TIME_REAL=120
echo "# CPU............: $NCPU"
echo "Ph. Memory.......: $MEM MB"
echo "Req.users........: $NUSER"
echo "Req.workers......: $REQ_WRKS"
echo "Max # workers....: $MAX_WKRS"
echo "# of workers.....: $WORKERS"
echo "Working mem......: $WMEM MB"
echo "Hard limit mem...: $AVAI_MEM MB"
echo "Soft limit mem...: $WRK_MEM MB"
echo "Best DB users....: $BEST_DB_NUSER"
echo "DB users.........: $DB_NUSER"
echo "Max conc. users..: $MAX_NUSER"
echo "Proxy mode.......: $PROXY_MODE"
echo "longpolling_port.: $longpolling_port"
echo "limit time CPU...: $TIME_CPU"
echo "limit time real..: $TIME_REAL"
if [ $WMEM -gt $AVAI_MEM ]; then
   echo "Warning! You have to increase physical memory!!!"
fi
if [ $DB_NUSER -gt 100 ]; then
   echo "Warning! You have to increase postgresql max connections!!!"
fi
echo ""
cur_mem_hard=$(echo "2147483648"|grep "^limit_memory_hard *=.*" $confn|grep -Eo "[0-9]+")
cur_mem_soft=$(echo "1610612736"|grep "^limit_memory_soft *=.*" $confn|grep -Eo "[0-9]+")
cur_workers=$(echo "0"|grep "^workers *=.*" $confn|grep -Eo "[0-9]+")
cur_db_maxconn=$(echo "64"|grep "^db_maxconn *=.*" $confn|grep -Eo "[0-9]+")
cur_proxy_mode=$(echo "False"|grep "^proxy_mode *=.*" $confn|awk -F= '{print $2}')
cur_longpolling_port=$(echo "8072"|grep "^longpolling_port *=.*" $confn|grep -Eo "[0-9]+")
cur_time_cpu=$(echo "60"|grep "^limit_time_cpu *=.*" $confn|grep -Eo "[0-9]+")
cur_time_real=$(echo "60"|grep "^limit_time_real *=.*" $confn|grep -Eo "[0-9]+")
((MEM_HARD=AVAI_MEM*1024*1024))
echo "sed -e \"s/^limit_memory_hard *= *$cur_mem_hard/limit_memory_hard = $MEM_HARD/\" -i $confn"
((MEM_SOFT=WRK_MEM*1024*1024))
echo "sed -e \"s/^limit_memory_soft *= *$cur_mem_soft/limit_memory_soft = $MEM_SOFT/\" -i $confn"
echo "sed -e \"s/^workers *= *$cur_workers/workers = $WORKERS/\" -i $confn"
echo "sed -e \"s/^db_maxconn *= *$cur_db_maxconn/db_maxconn = $DB_NUSER/\" -i $confn"
echo "sed -e \"s/^proxy_mode *= *$cur_proxy_mode/proxy_mode = $PROXY_MODE/\" -i $confn"
echo "sed -e \"s/^longpolling_port *= *$cur_longpolling_port/longpolling_port = $longpolling_port/\" -i $confn"
echo "sed -e \"s/^limit_time_cpu *= *$cur_time_cpu/limit_time_cpu = $TIME_CPU/\" -i $confn"
echo "sed -e \"s/^limit_time_real *= *$cur_time_real/limit_time_real = $TIME_REAL/\" -i $confn"
if [[ -n "$confn" && ! "$3" == "-n" ]]; then
    echo "Update file $confn ..."
    grep -E "^# .*Workers are set for [0-9]+ users" $confn
    if [ $? -ne 0 ]; then
        sed "/^workers *=.*/i # [antoniov: $(date +%Y-%m-%d)] Workers are set for $NUSER users" -i $confn
    else
        sed -re "s/^# .*Workers are set for [0-9]+ users/# [antoniov: $(date +%Y-%m-%d)] Workers are set for $NUSER users/" -i $confn
    fi
    sed -e "s/^limit_memory_hard *=.*/limit_memory_hard = $MEM_HARD/" -i $confn
    sed -e "s/^limit_memory_soft *=.*/limit_memory_soft = $MEM_SOFT/" -i $confn
    sed -e "s/^workers *=.*/workers = $WORKERS/" -i $confn
    sed -e "s/^db_maxconn *=.*/db_maxconn = $DB_NUSER/" -i $confn
    sed -e "s/^proxy_mode *=.*/proxy_mode = $PROXY_MODE/" -i $confn
    sed -e "s/^longpolling_port *=.*/longpolling_port = $longpolling_port/" -i $confn
    sed -e "s/^limit_time_cpu *=.*/limit_time_cpu = $TIME_CPU/" -i $confn
    sed -e "s/^limit_time_real *=.*/limit_time_real = $TIME_REAL/" -i $confn
    echo "You should restart odoo with a comand like this one"
    echo "sudo systemctl restart odoo"
fi
# set +x
