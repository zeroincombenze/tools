#! /bin/bash
NOW=$(date "+%s")
PID="$HOME/startup.log"
if [[ -f $PID ]]; then
    LAST=$(stat -c "%Y" $PID)
    ((DIFF=NOW-LAST))
    if [[ $DIFF -lt 180 && $1 != "-f" ]]; then
        echo "Another process running this script ..."
        exit
    fi
fi
touch $PID
NOW=$(date "+%s")
CONFN="$HOME/.$(basename $0).conf"
[[ -f $CONFN ]] && LAST=$(cat $CONFN|grep "^last_update *="|tr -d " "|awk -F= '{print $2}') || LAST=0
((DIFF=NOW-LAST))
if [[ $DIFF -gt 79200 || $1 == "-f" ]]; then
    for host in shs23pro zavixtech refocus metalpack; do
        ssh.py -sr $host:~/backups/*.gz ~/backups/
    done
    echo ssh.py -sr cscs16:~/9.3/backups/cscs2016.gz ~/backups/
    rm -f ~/backups/__old_*
    for db in $(psql -p5434 -Uodoo10 -Atl|cut -d"|" -f1|tr "\n" " "); do
        [[ ! $db =~ ^(test|template|connect|oca|odoo.*CTc|postgres) ]] && ./zar_rest  -p5434 -Uodoo10 -vR $db
    done
    for db in $(psql -p5434 -Uodoo12 -Atl|cut -d"|" -f1|tr "\n" " "); do
        [[ ! $db =~ ^(test|template|connect|oca|odoo.*CTc|postgres) ]] && ./zar_rest  -p5434 -Uodoo12 -vR $db
    done
    for db in $(psql -p5432 -Uodoo18 -Atl|cut -d"|" -f1|tr "\n" " "); do
        [[ ! $db =~ ^(test|template|connect|oca|odoo.*CTc|postgres) ]] && ./zar_rest  -p5432 -Uodoo18 -vR $db
    done
    echo "[startup]">$CONFN
    echo "last_update = $NOW">>$CONFN
fi
rm $PID

