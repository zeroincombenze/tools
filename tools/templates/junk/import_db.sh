#! /bin/bash
# Import data from refocus (Refocus)
[[ -z $1 || $1 == -h || $1 == --help ]] && echo -e "$(basename $0)\n[-c FILE][--conf=FILE]\n[--cont]\n[-d DB]\n[--db-user=USER]\n[-k]\n[-n] [--dry-run]\n[-p PORT]\n[--remote-db=DBNAME]\n[--remote-psql-port=PORT]\n[--reset-pwd]\n date # $(date +%Y%m%d)" && exit 1
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
[[ -z $DB ]] && DB="refocus18"
[[ -z $DB_USER ]] && DB_USER="odoo18"
[[ -z $CONFN ]] && CONFN="/etc/odoo/odoo18.conf"
[[ -z $PSQL_PORT ]] && PSQL_PORT=$(sudo grep db_port $CONFN | sed "s/False/5432/" | cut -d= -f2 | tr -d " ")
[[ -z $SERVICE ]] && SERVICE="odoo18"
[[ -z $REMOTE_HOST ]] && REMOTE_HOST="refocus"
[[ -z $REMOTE_DB ]] && REMOTE_DB="refocus18"
[[ -z $REMOTE_PSQL_PORT ]] && REMOTE_PSQL_PORT=5434
[[ -z $DRY_RUN ]] && DRY_RUN=0
[[ -z $KEEP_DB ]] && KEEP_DB=0
[[ -z $RESET_PWD ]] && RESET_PWD=0

[[ CONT -eq 0 ]] && echo "$(basename $0): import from $REMOTE_HOST/$REMOTE_DB:$REMOTE_PSQL_PORT"
[[ CONT -ne 0 ]] && echo "$(basename $0)"
echo "Build $DB-$DATE.sql for service $SERVICE:$PSQL_PORT with $CONFN:$DB_USER"
[[ $KEEP_DB -ne 0 ]] && echo "DB is not deleted"
[[ $DRY_RUN -ne 0 ]] && echo "Warning: no execution (dry-run)"
echo ""

if [[ ! -f $HOME/$DB-$DATE.sql && $CONT -eq 0 ]]; then
    [[ -n $REMOTE_PSQL_PORT ]] && opts="-p $REMOTE_PSQL_PORT --no-owner $VERBOSE" || opts="--no-owner $VERBOSE"
    echo ssh.py $REMOTE_HOST -c "sudo -i -u postgres pg_dump $opts -Fp -f $REMOTE_DB-$DATE.sql $REMOTE_DB"
    [[ $DRY_RUN -eq 0 ]] && ssh.py $REMOTE_HOST -c "sudo -i -u postgres pg_dump $opts -Fp -f $REMOTE_DB-$DATE.sql $REMOTE_DB"
    [[ -n $VERBOSE ]] && echo -e "\n"
    echo ssh.py $REMOTE_HOST -c "sudo mv /var/lib/postgresql/$REMOTE_DB-$DATE.sql ./"
    [[ $DRY_RUN -eq 0 ]] && ssh.py $REMOTE_HOST -c "sudo mv /var/lib/postgresql/$REMOTE_DB-$DATE.sql ./"
    [[ -n $VERBOSE ]] && echo -e "\n"
    echo ssh.py -s $REMOTE_HOST:~/$REMOTE_DB-$DATE.sql $HOME
    [[ $DRY_RUN -eq 0 ]] && ssh.py -s $REMOTE_HOST:~/$REMOTE_DB-$DATE.sql $HOME
    echo sudo chown postgres:postgres $HOME/$REMOTE_DB-$DATE.sql
    [[ $DRY_RUN -eq 0 ]] && sudo chown postgres:postgres $HOME/$REMOTE_DB-$DATE.sql
fi
echo ""
if [[ $CONT -eq 0 ]]; then
    echo sudo mv $HOME/$REMOTE_DB-$DATE.sql /var/lib/postgresql/$DB-$DATE.sql
    [[ $DRY_RUN -eq 0 ]] && sudo mv $HOME/$REMOTE_DB-$DATE.sql /var/lib/postgresql/$DB-$DATE.sql
fi
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
    echo ssh.py $REMOTE_HOST -c "rm ~/$DB-$DATE.sql"
    [[ $DRY_RUN -eq 0 ]] && ssh.py $REMOTE_HOST -c "rm ~/$DB-$DATE.sql"
fi
