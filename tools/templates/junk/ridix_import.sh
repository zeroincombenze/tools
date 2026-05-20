# Import data from cloudpepper using no odoo user
[[ -z $1 || $1 == -h || $1 == --help ]] && echo "$0 date # $(date +%Y%m%d)" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1
RIDIX_PATH="/home/odoo/ridix"
DB="ridix18"
DB_USER="odoo18ee"
CONFN="/etc/odoo/odoo18-ee.conf"
PSQL_PORT=$(grep db_port $CONFN | sed "s/False/5432/" | cut -d= -f2 | tr -d " ")
SERVICE="odoo18-ee"
REMOTE_HOST="cloudpepper"
REMOTE_DB="202506-staging-ridix.cloudpepper.site"

echo ssh.py $REMOTE_HOST -c "sudo -i -u postgres pg_dump --no-owner -Fp -v -f $DB-$1.sql $REMOTE_db"
ssh.py $REMOTE_HOST -c "sudo -i -u postgres pg_dump --no-owner -Fp -v -f $DB-$1.sql $REMOTE_db"
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
echo "psql -p$PSQL_PORT -U$DB_USER $DB -c \"update res_users set password='admin' where id=2\""
psql -p$PSQL_PORT -U$DBUSER $DB -c "update res_users set password='admin' where id=2"
echo "psql -p$PSQL_PORT -U$DB_USER $DB -c \"update synchro_backend set exchange_path='/home/odoo/ridix' where id=9\""
psql -p$PSQL_PORT -U$DB_USER $DB -c "update synchro_backend set exchange_path='/home/odoo/ridix' where id=9"
echo "systemctl start $SERVICE"
systemctl start $SERVICE
echo ssh.py $REMOTE_HOST -c "rm ~/$DB-$1.sql"
ssh.py $REMOTE_HOST -c "rm ~/$DB-$1.sql"
