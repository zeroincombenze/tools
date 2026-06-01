[[ -z $1 || $1 == "-h" || $1 == "--help" ]] && echo "$0 db_name [7|8|10|12|13|14|15|16|17|18|19][81*][DATE][list][odoo*][PG_PORT][no-ask]" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1
db=""
db_user=""
over=""
dt=$(date +%Y%m%d)
pgport=""
httpport=""
cmd="restore"
no_ask=0
sts=0
while [[ -n "$1" ]]; do
    [[ $sts -eq 0 && -n $1 && $1 =~ ^543[0-9]+$ ]] && pgport="$1" && sts=1
    [[ $sts -eq 0 && -n $1 && $1 =~ ^81[0-9]+$ ]] && httpport="$1" && sts=1
    [[ $sts -eq 0 && -n $1 && $1 =~ ^20[0-3][0-9]+$ ]] && dt="$1" && sts=1
    [[ $sts -eq 0 && -n $1 && $1 =~ ^(7|8|10|12|13|14|15|16|17|18|19)$ ]] && over="$1" && sts=1
    [[ $sts -eq 0 && -n $1 && $1 =~ ^odoo[0-9]+$ ]] && db_user="$1" && sts=1
    [[ $sts -eq 0 && -n $1 && $1 == "list" ]] && cmd="$1" && sts=1
    [[ $sts -eq 0 && -n $1 && -z $db ]] && db="$1"
    [[ $sts -eq 0 && -n $1 && $1 == "no-ask" ]] && no_ask=1
    shift
    sts=0
done
[[ -z $over ]] && over=$(echo ${db: -2})
[[ ! $over =~ ^(7|8|10|12|13|14|15|16|17|18|19)$ ]] && over="10"
[[ -z $db_user && $db =~ ^ridix ]] && db_user="odoo18ee"
[[ -z $db_user ]] && db_user="odoo$over"
if [[ -z $pgport ]]; then
    # Postgres / odoo mapping
    # Odoo 6.1 - 7.0 -> psql-9.5: 5435
    # Odoo 7.0 - 10.0 -> psql-10: 5433
    # Odoo 10.0 - 15.0 -> psql-12: 5434
    # Odoo 16.0 - 19.0 -> psql-16: 5436
    # Odoo 18-0 - 19.0 -> psql-18: 5432 *
    pgport="5432"
    [[ $over -le 16 ]] && pgport="5434"
    # [[ $over -lt 11 ]] && pgport="5433"
    [[ $over -lt 7 ]] && pgport="5435"
fi
if [[ -z $httpport ]]; then
    httpport=$((8160+$over))
    [[ db_user == "odoo18ee" ]] && httpposrt=8278
fi

fn="${db}-${dt}.sql"
echo "$cmd db $db for odoo version $over from file $fn (by date ${dt:0:4}-${dt:4:2}-${dt:6:2}) pgport=$pgport db_user=$db_user"
[[ $no_ask -eq 0 ]] && read -p "Press RET to continue ..."

if [[ -f $fn ]]; then
    echo "Found file $fn ..."
else
    gz="$HOME/backups/$db.gz"
    [[ ! -f $gz ]] && "No backup $gz found!" && exit 1
    if [[ $cmd == "list" ]]; then
        echo tar -tvf $gz
        tar -tvf $gz	    
    else
        echo tar -xvf $gz $fn
        tar -xvf $gz $fn
    fi
fi
if [[ ! -f $fn ]]; then
    echo "File $fn not found!"
    echo "You can select one of following:"
    dir ${db}-*.sql
    exit 1
fi
ddb="true"
psql -U$db_user -p$pgport -l|grep -Eq "^ *${db} " && ddb="dropdb -U$db_user -p$pgport $db"
echo "$ddb && createdb -U$db_user -p$pgport $db && psql -U$db_user -p$pgport $db -f $fn"
$ddb && createdb -U$db_user -p$pgport $db && psql -U$db_user -p$pgport $db -f $fn 1>/dev/null
[[ -$? -ne 0 ]] && echo "********** Error creating DB **********" && ./zar_rest -qR $db && exit 1
[[ -z $pgport ]] && opts="" || opts="-p $pgport"
echo ./zar_rest -U$db_user -p$pgport -vR $db
./zar_rest -U$db_user -p$pgport -vR $opts $db
echo psql -U$db_user -p$pgport $db -c "update ir_config_parameter set value='http://127.0.0.1:$httpport' where key='web.base.url'"
psql -U$db_user -p$pgport $db -c "update ir_config_parameter set value='http://127.0.0.1:$httpport' where key='web.base.url'"

[[ $no_ask -eq 0 ]] && for f in *.sql; do [[ ! $f =~ ${dt}.sql ]] && rm -i $f; done
