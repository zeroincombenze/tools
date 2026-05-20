# Import data from refocus using no odoo user
[[ -z $1 || $1 == -h || $1 == --help ]] && echo "$0 date # $(date +%Y%m%d)" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1
DB="refocus18"
CONFN="/etc/odoo/odoo18.conf"
PSQL_PORT=$(grep db_port $CONFN | sed "s/False/5432/" | cut -d= -f2 | tr -d " ")
SERVICE="odoo18"
REMOTE_HOST="refocus"
REMOTE_DB="odoo18"

echo ssh.py $REMOTE_HOST -c "sudo -i -u postgres pg_dump --no-owner -Fp -v -f $DB-$1.sql $REMOTE_HOST"
ssh.py $REMOTE_HOST -c "sudo -i -u postgres pg_dump --no-owner -Fp -v -f $DB-$1.sql $REMOTE_HOST"
echo -e "\n"
echo ssh.py $REMOTE_HOST -c "sudo mv /var/lib/postgresql/$DB-$1.sql ./"
ssh.py $REMOTE_HOST -c "sudo mv /var/lib/postgresql/$DB-$1.sql ./"
echo -e "\n"
echo ssh.py -s $REMOTE_HOST:~/$DB-$1.sql $HOME
ssh.py -s $REMOTE_HOST:~/$DB-$1.sql $HOME
echo sudo chown postgres:postgres $HOME/$DB-$1.sql
sudo chown postgres:postgres $HOME/$DB-$1.sql
echo sudo mv $HOME/$DB-$1.sql /var/lib/postgresql/
sudo sudo mv $HOME/$DB-$1.sql /var/lib/postgresql/
echo systemctl stop $SERVICE
systemctl stop $SERVICE
echo sudo -i -upostgres build_db.sh $DB $1 no-ask
sudo -i -upostgres build_db.sh $DB $1 no-ask
echo "sudo -i -uodoo run_odoo_debug -c $CONFN -usm all -d $DB -v"
sudo -i -uodoo run_odoo_debug -c $CONFN -usm all -d $DB -v
# echo "psql -p$PSQL_PORT -Uodoo18 $DB -c \"update res_users set password='admin' where id=2\""
# psql -p$PSQL_PORT -Uodoo18 $DB -c "update res_users set password='admin' where id=2"
# echo "psql -p$PSQL_PORT -Uodoo18 $DB -c \"update synchro_backend set exchange_path='/home/odoo/ridix' where id=9\""
# psql -p$PSQL_PORT -Uodoo18 $DB -c "update synchro_backend set exchange_path='/home/odoo/ridix' where id=9"
echo "systemctl start $SERVICE"
systemctl start $SERVICE
echo ssh.py $REMOTE_HOST -c "rm ~/$DB-$1.sql"
ssh.py $REMOTE_HOST -c "rm ~/$DB-$1.sql"
