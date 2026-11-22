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
# Skip the download when the local copy has the same size and mtime of the remote
# one (the local mtime is aligned to the remote one after each download), so a
# repeated run after a crash does not download again the files already loaded.
download_file() {
    local host=$1 rpath=$2 name dest age rinfo rsize rmtime
    name=$(basename "$rpath")
    dest="$HOME/backups/$name"
    rinfo=$(ssh.py $host -c "stat -c '%s %Y' $rpath" 2>/dev/null | grep -E "^[0-9]+ [0-9]+$" | tail -n1)
    read rsize rmtime <<<"$rinfo"
    if [[ -f $dest ]]; then
        if [[ -n $rsize ]]; then
            if [[ $(stat -c %s "$dest") == "$rsize" && $(stat -c %Y "$dest") == "$rmtime" ]]; then
                rm -f ~/backups/.part/"$name"
                echo "$name gia' scaricato (stessa dimensione/data) -> skip"
                return 0
            fi
        else
            # remote info not available: fall back on the age of the local copy
            ((age=$(date +%s)-$(stat -c %Y "$dest")))
            if [[ $age -lt $MARGIN ]]; then
                rm -f ~/backups/.part/"$name"
                echo "$name scaricato ${age}s fa -> skip"
                return 0
            fi
        fi
    fi
    mkdir -p ~/backups/.part
    rm -f ~/backups/.part/"$name"
    ssh.py -sr "$host:$rpath" ~/backups/.part/ || return 1
    mv -f ~/backups/.part/"$name" "$dest" || return 1
    if [[ -n $rmtime ]]; then
        touch -d "@$rmtime" "$dest"
    else
        touch "$dest"
    fi
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
    for host in shs23pro metalpack; do
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

