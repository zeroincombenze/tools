#! /bin/bash
# Import data from  shs23pro (any DB)
[[ -z $1 || $1 == -h || $1 == --help ]] && echo -e "$(basename $0)\n[-c FILE][--conf=FILE]\n[--cont]\n[-d DB]\n[--db-user=USER]\n[-k]\n[-n] [--dry-run]\n[-p PORT]\n[--reset-pwd ]\n[--remote-psql-port=PORT]\n date # $(date +%Y%m%d)" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1

param=""
sts=0
while [[ -n "$1" ]]; do
    [[ -z $1 ]] &&  sts=1
    [[ $sts -eq 0 && -n $param ]] && eval $param="$1" && param="" && sts=1
    [[ $sts -eq 0 && $1 =~ --conf= ]] && x=$(echo $1|cut -d= -f2) && CONFN="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --conf ]] && param="CONFN" && sts=1
    [[ $sts -eq 0 && $1 =~ --cont ]] && CONT=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --dry-run ]] && DRY_RUN=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --db-user= ]] && x=$(echo $1|cut -d= -f2) && DB_USER="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --db-user ]] && param="DB_USER" && sts=1
    [[ $sts -eq 0 && $1 =~ --host= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_HOST="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --host ]] && param="REMOTE_HOST" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-db= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_DB="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-db ]] && param="REMOTE_DB" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-port= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_PSQL_PORT="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-port ]] && param="REMOTE_PSQL_PORT" && sts=1
    [[ $sts -eq 0 && $1 =~ --reset-pwd ]] && RESET_PWD=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -.*c ]] && param="CONFN" && sts=1
    [[ $sts -eq 0 && $1 =~ -.*d ]] && param="DB" && sts=1
    [[ $sts -eq 0 && $1 =~ -.*k ]] && KEEP_DB=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -.*n ]] && DRY_RUN=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -.*p ]] && param="PSQL_PORT" && sts=1
    [[ $sts -eq 0 && $1 =~ -.*v ]] && VERBOSE="-v" && sts=1
    [[ $sts -eq 0 && $1 =~ [0-9]{8} ]] && DATE="$1" && sts=1
    [[ $sts -eq 0 ]] && echo "Unknow value $1"
    shift
    sts=0
done

# Custom values
[[ -z $DATE ]] && DATE=$(date +%Y%m%d)
[[ -z $REMOTE_HOST ]] && REMOTE_HOST="shs23pro"
[[ -z $REMOTE_PSQL_PORT ]] && REMOTE_PSQL_PORT=5432
[[ -z $DRY_RUN ]] && DRY_RUN=0
[[ -z $KEEP_DB ]] && KEEP_DB=0
[[ -z $RESET_PWD ]] && RESET_PWD=0
[[ -z $DB ]] && echo "Missing DB name" && exit 1
[[ -z $REMOTE_DB ]] && REMOTE_DB="$DB"
majver=$(echo $DB | grep -Eo "[0-9]+$")
[[ -z $majver ]] && majver="10"
[[ -z $DB_USER ]] && DB_USER="odoo$majver"
[[ -z $CONFN ]] && CONFN="/etc/odoo/odoo$majver.conf"
[[ -z $PSQL_PORT ]] && PSQL_PORT=$(sudo grep db_port $CONFN | sed "s/False/5433/" | cut -d= -f2 | tr -d " ")
[[ -z $SERVICE ]] && SERVICE="odoo$majver"
[[ CONT -eq 0 ]] && echo "$(basename $0): import from $REMOTE_HOST/$REMOTE_DB:$REMOTE_PSQL_PORT"
[[ CONT -ne 0 ]] && echo "$(basename $0)"
echo "Build $DB-$DATE.sql for service $SERVICE:$PSQL_PORT with $CONFN:$DB_USER"
[[ $KEEP_DB -ne 0 ]] && echo "DB is not deleted"
[[ $DRY_RUN -ne 0 ]] && echo "Warning: no execution (dry-run)"
echo ""

if [[ ! -f $HOME/$DB-$DATE.sql && $CONT -eq 0 ]]; then
    [[ -n $REMOTE_PSQL_PORT ]] && opts="-p $REMOTE_PSQL_PORT --no-owner $VERBOSE" || opts="--no-owner $VERBOSE"
    echo sudo su - postgres -c "ssh.py $REMOTE_HOST -c \"pg_dump $opts -Fp -f $DB-$DATE.sql $REMOTE_DB\""
    [[ $DRY_RUN -eq 0 ]] && sudo su - postgres -c "ssh.py $REMOTE_HOST -c \"pg_dump $opts -Fp -f $DB-$DATE.sql $REMOTE_DB\""
    [[ -n $VERBOSE ]] && echo -e "\n"
    echo sudo su - postgres -c "ssh.py -s $REMOTE_HOST:~/$DB-$DATE.sql ./"
    [[ $DRY_RUN -eq 0 ]] && sudo su - postgres -c "ssh.py -s $REMOTE_HOST:~/$DB-$DATE.sql ./"
fi
echo ""
echo systemctl stop $SERVICE
[[ $DRY_RUN -eq 0 ]] && systemctl stop $SERVICE
echo sudo -i -upostgres build_db.sh $DB $DB_USER $DATE $PSQL_PORT no-ask
[[ $DRY_RUN -eq 0 ]] && sudo -i -upostgres build_db.sh $DB $DB_USER $DATE $PSQL_PORT no-ask
echo "sudo -i -uodoo run_odoo_debug -c $CONFN -usm all -d $DB $VERBOSE"
[[ $DRY_RUN -eq 0 ]] && sudo -i -uodoo run_odoo_debug -c $CONFN -usm all -d $DB $VERBOSE
if [[ $RESET_PWD -ne 0 ]]; then
    echo "psql -p$PSQL_PORT -U$DB_USER $DB -c \"update res_users set password='admin' where id=2\""
    [[ $DRY_RUN -eq 0 ]] && psql -p$PSQL_PORT -U$DB_USER $DB -c "update res_users set password='admin' where id=2"
    echo "psql -p$PSQL_PORT -U$DB_USER $DB -c \"update synchro_backend set exchange_path='/home/odoo/ridix' where id=9\""
    [[ $DRY_RUN -eq 0 ]] && psql -p$PSQL_PORT -U$DB_USER $DB -c "update synchro_backend set exchange_path='/home/odoo/ridix' where id=9"
fi
echo "systemctl start $SERVICE"
[[ $DRY_RUN -eq 0 ]] && systemctl start $SERVICE
if [[ $KEEP_DB -eq 0 ]]; then
    echo sudo -i -postgres ssh.py $REMOTE_HOST -c "rm ~/$DB-$DATE.sql"
    [[ $DRY_RUN -eq 0 ]] && sudo -i -postgres ssh.py $REMOTE_HOST -c "rm ~/$DB-$DATE.sql"
fi
