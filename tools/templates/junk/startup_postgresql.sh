#!/bin/bash
MARGIN=1800       # 1 ora

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
trap 'rm -f $PID' EXIT

# download_file host remote_path
download_file() {
    local host=$1 rpath=$2 name dest age
    name=$(basename "$rpath")
    dest="$HOME/backups/$name"
    if [[ -f $dest ]]; then
        ((age=$(date +%s)-$(stat -c %Y "$dest")))
        if [[ $age -lt $MARGIN ]]; then
	    rm -f ~/backups/.part/"$name"
            echo "$name scaricato ${age}s fa -> skip"
            return 0
        fi
    fi
    mkdir -p ~/backups/.part
    rm -f ~/backups/.part/"$name"
    ssh.py -sr "$host:$rpath" ~/backups/.part/ || return 1
    mv -f ~/backups/.part/"$name" "$dest" && touch "$dest"
}

restore_dbs() {
    local port=$1 user=$2 db
    for db in $(psql -p$port -U$user -Atl|cut -d"|" -f1); do
        [[ $db =~ ^(test|template|connect|oca|odoo.*CTc|postgres) ]] && continue
        ./zar_rest -p$port -U$user -vR $db
    done
}

NOW=$(date "+%s")
CONFN="$HOME/.$(basename $0).conf"
[[ -f $CONFN ]] && LAST=$(grep "^last_update *=" $CONFN|tr -d " "|awk -F= '{print $2}') || LAST=0
((DIFF=NOW-LAST))
if [[ $DIFF -gt 79200 || $1 == "-f" ]]; then
    ERR=0
    for host in shs23pro zavixtech refocus metalpack; do
        files=$(ssh.py $host -c 'ls -1 ~/backups/*.gz') || { echo "Errore: $host non raggiungibile"; ERR=1; continue; }
        for f in $files; do
            download_file $host "$f" || { echo "Errore download $f da $host"; ERR=1; continue; }
        done
    done
    # download_file cscs16 "~/9.3/backups/cscs2016.gz" || ERR=1
    rm -f ~/backups/__old_*
    restore_dbs 5434 odoo10
    restore_dbs 5434 odoo12
    restore_dbs 5432 odoo18
    [[ $ERR -eq 0 ]] && printf "[startup]\nlast_update = %s\n" $NOW > $CONFN
fi

