#! /bin/bash
# Import DB from remote host
[[ -z $1 || $1 == -h || $1 == --help ]] && echo -e "$(basename $0)\n[--craft=CRAFT]\n[-c FILE][--conf=FILE]\n[--cont]\n[-d DB]\n[--db-user=USER]\n[-k]\n[-n] [--dry-run]\n[-p PORT]\n[--remote-db=DBNAME]\n[--remote-psql-port=PORT]\n[--reset-pwd]\n date # $(date +%Y%m%d)" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1

param=""
sts=0
while [[ -n "$1" ]]; do
    [[ -z $1 ]] && sts=1
    [[ $sts -eq 0 && -n $param ]] && eval $param="$1" && param="" && sts=1
    [[ $sts -eq 0 && $1 =~ --conf= ]] && x=$(echo $1|cut -d= -f2) && CONFN="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --conf ]] && param="CONFN" && sts=1
    [[ $sts -eq 0 && $1 =~ --craft= ]] && x=$(echo $1|cut -d= -f2) && CRAFT="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --craft ]] && param="CRAFT" && sts=1
    [[ $sts -eq 0 && $1 =~ --cont ]] && CONT=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --database= ]] && x=$(echo $1|cut -d= -f2) && DB="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --database ]] && param="DB" && sts=1
    [[ $sts -eq 0 && $1 =~ --dry-run ]] && DRY_RUN=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --db-user= ]] && x=$(echo $1|cut -d= -f2) && PSQL_USER="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --db-user ]] && param="PSQL_USER" && sts=1
    [[ $sts -eq 0 && $1 =~ --host= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_HOST="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --host ]] && param="REMOTE_HOST" && sts=1
    [[ $sts -eq 0 && $1 =~ --psql-port= ]] && x=$(echo $1|cut -d= -f2) && PSQL_PORT="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --psql-port ]] && param="PSQL_PORT" && sts=1
    [[ $sts -eq 0 && $1 =~ --psql-user= ]] && x=$(echo $1|cut -d= -f2) && PSQL_USER="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --psql-user ]] && param="PSQL_USER" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-db= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_DB="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-db ]] && param="REMOTE_DB" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-port= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_PSQL_PORT="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-port ]] && param="REMOTE_PSQL_PORT" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-user= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_PSQL_USER="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-user ]] && param="REMOTE_PSQL_USER" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-path= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_PSQL_PATH="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-psql-path ]] && param="REMOTE_PSQL_PATH" && sts=1
    [[ $sts -eq 0 && $1 =~ --reset-pwd ]] && RESET_PWD=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --service= ]] && x=$(echo $1|cut -d= -f2) && SERVICE="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --service ]] && param="SERVICE" && sts=1
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

# set -x  #debug
if [[ -n $CRAFT ]]; then
    [[ ! -f $CRAFT ]] && CRAFT="$(dirname $0)/$CRAFT.ini"
    [[ ! -f $CRAFT ]] && echo "Invalid configuration $CRAFT" && exit 3
    x=$(grep -E "^config *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && CONFN=$(echo $x)
    x=$(grep -E "^database *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && DB=$(echo $x)
    x=$(grep -E "^remote_host *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && REMOTE_HOST=$(echo $x)
    x=$(grep -E "^remote_db *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && REMOTE_DB=$(echo $x)
    x=$(grep -E "^remote_psql_port *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && REMOTE_PSQL_PORT=$(echo $x)
    x=$(grep -E "^remote_psql_user *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && REMOTE_PSQL_USER=$(echo $x)
    x=$(grep -E "^remote_psql_path *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && REMOTE_PSQL_PATH=$(echo $x)
    x=$(grep -E "^service *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && SERVICE=$(echo $x)
    x=$(grep -E "^psql_port *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && PSQL_PORT=$(echo $x)
    x=$(grep -E "^psql_user *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && PSQL_USER=$(echo $x)
    x=$(grep -E "^database *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && DB=$(echo $x)
    x=$(grep -E "^reset_pwd *=.*" $CRAFT | cut -d= -f2)
    [[ -n $x ]] && RESET_PWD=$(echo $x)
fi
[[ -z $CONFN ]] && CONFN="/etc/odoo/odoo18.conf"
[[ ! -f $CONFN ]] && echo "Configuration file $CONFN not found" && exit 3
[[ -z $DATE ]] && DATE=$(date +%Y%m%d)
[[ -z $SERVICE ]] && SERVICE="odoo18"
x=$(grep -E "^db_port *=.*" $CONFN | cut -d= -f2)
[[ -n $x && ! $x =~ False ]] && PSQL_PORT=$(echo $x)
[[ -z $PSQL_PORT ]] && PSQL_PORT="5432"
x=$(grep -E "^db_user *=.*" $CONFN | cut -d= -f2)
[[ -n $x && ! $x =~ False ]] && PSQL_USER=$(echo $x)
[[ -z $PSQL_USER ]] && PSQL_USER="odoo18"
[[ -z $DB ]] && echo "Missed local database (--database=DBNAME)" && exit 1
[[ -z $REMOTE_HOST ]] && echo "Missed remote host (--remote-host=HOST)" && exit 1
[[ -z $REMOTE_DB ]] && REMOTE_DB="$DB"
[[ -z $REMOTE_PSQL_PORT ]] && REMOTE_PSQL_PORT="5432"
[[ -z $REMOTE_PSQL_USER ]] && REMOTE_PSQL_USER="postgres"
[[ -z $REMOTE_PSQL_PATH ]] && REMOTE_PSQL_PATH="/var/lib/postgresql"
# set +x  #debug

[[ CONT -eq 0 ]] && echo "$(basename $0): import from $REMOTE_HOST/$REMOTE_DB:$REMOTE_PSQL_PORT"
[[ CONT -ne 0 ]] && echo "$(basename $0)"
echo "Build '$DB-$DATE.sql' for service $SERVICE from $CONFN by psql $PSQL_USER:$PSQL_PORT"
[[ $KEEP_DB -ne 0 ]] && echo "Remote sql file is not deleted"
[[ $DRY_RUN -ne 0 ]] && echo "Warning: no execution (dry-run)"
echo ""

if [[ ! -f $HOME/$DB-$DATE.sql && $CONT -eq 0 ]]; then
    [[ -n $REMOTE_PSQL_PORT ]] && opts="-p $REMOTE_PSQL_PORT -U $REMOTE_PSQL_USER --no-owner $VERBOSE" || opts="--no-owner $VERBOSE"
    echo ssh.py $REMOTE_HOST -c "sudo -i -upostgres pg_dump $opts -Fp -f $REMOTE_DB-$DATE.sql $REMOTE_DB"
    [[ $DRY_RUN -eq 0 ]] && ssh.py $REMOTE_HOST -c "sudo -i -upostgres pg_dump $opts -Fp -f $REMOTE_DB-$DATE.sql $REMOTE_DB"
    [[ -n $VERBOSE ]] && echo -e "\n"
    echo ssh.py $REMOTE_HOST -c "sudo mv $REMOTE_PSQL_PATH/$REMOTE_DB-$DATE.sql ./"
    [[ $DRY_RUN -eq 0 ]] && ssh.py $REMOTE_HOST -c "sudo mv $REMOTE_PSQL_PATH/$REMOTE_DB-$DATE.sql ./"
    [[ -n $VERBOSE ]] && echo -e "\n"
    echo ssh.py -s $REMOTE_HOST:~/$REMOTE_DB-$DATE.sql $HOME
    [[ $DRY_RUN -eq 0 ]] && ssh.py -s $REMOTE_HOST:~/$REMOTE_DB-$DATE.sql $HOME
    echo sudo chown postgres:postgres $HOME/$REMOTE_DB-$DATE.sql
    [[ $DRY_RUN -eq 0 ]] && sudo chown postgres:postgres $HOME/$REMOTE_DB-$DATE.sql
fi
echo ""
if [[ $CONT -eq 0 ]]; then
    echo sudo mv $HOME/$REMOTE_DB-$DATE.sql $REMOTE_PSQL_PATH/$DB-$DATE.sql
    [[ $DRY_RUN -eq 0 ]] && sudo mv $HOME/$REMOTE_DB-$DATE.sql $REMOTE_PSQL_PATH/$DB-$DATE.sql
fi
echo systemctl stop $SERVICE
[[ $DRY_RUN -eq 0 ]] && systemctl stop $SERVICE
echo sudo -i -upostgres build_db.sh $DB $PSQL_USER $DATE $PSQL_PORT no-ask
[[ $DRY_RUN -eq 0 ]] && sudo -i -upostgres build_db.sh $DB $PSQL_USER $DATE $PSQL_PORT no-ask
echo "sudo -i -uodoo run_odoo_debug -c $CONFN -usm all -d $DB $VERBOSE"
[[ $DRY_RUN -eq 0 ]] && sudo -i -uodoo run_odoo_debug -c $CONFN -usm all -d $DB $VERBOSE
if [[ $RESET_PWD -ne 0 ]]; then
    echo "psql -p$PSQL_PORT -U$PSQL_USER $DB -c \"update res_users set password='admin' where id=2\""
    [[ $DRY_RUN -eq 0 ]] && psql -p$PSQL_PORT -U$PSQL_USER $DB -c "update res_users set password='admin' where id=2"
    # echo "psql -p$PSQL_PORT -U$PSQL_USER $DB -c \"update synchro_backend set exchange_path='/home/odoo/ridix' where id=9\""
    # [[ $DRY_RUN -eq 0 ]] && psql -p$PSQL_PORT -U$PSQL_USER $DB -c "update synchro_backend set exchange_path='/home/odoo/ridix' where id=9"
fi
echo "systemctl start $SERVICE"
[[ $DRY_RUN -eq 0 ]] && systemctl start $SERVICE
if [[ $KEEP_DB -eq 0 ]]; then
    echo ssh.py $REMOTE_HOST -c "rm ~/$DB-$DATE.sql"
    [[ $DRY_RUN -eq 0 ]] && ssh.py $REMOTE_HOST -c "rm ~/$DB-$DATE.sql"
fi
