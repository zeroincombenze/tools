#!/bin/bash
# Postgres / odoo mapping
# Odoo 6.1 - 7.0 -> psql-9.5: 5435
# Odoo 7.0 - 10.0 -> psql-10: 5433
# Odoo 10.0 - 15.0 -> psql-12: 5434
# Odoo 16.0 - 19.0 -> psql-16: 5436
# Odoo 18-0 - 19.0 -> psql-18: 5432 *


msg=""
for port in 8172 8170 8174 8176 8178; do
  if [[ $port -ge 8200 ]]; then
      odoo_maj=$((port-8260))
      pg_user="odoo${odoo_maj}ee"
      svc="odoo${odoo_maj}-ee"
      db="demo${odoo_maj}ee"
  else
      odoo_maj=$((port-8160))
      pg_user="odoo${odoo_maj}"
      svc="odoo${odoo_maj}"
      db="demo${odoo_maj}"
  fi
  [[ $odoo_maj -eq 10 ]] && pg_port=5434
  [[ $odoo_maj -eq 12 ]] && pg_port=5434
  [[ $odoo_maj -eq 14 ]] && pg_port=5434
  [[ $odoo_maj -eq 16 ]] && pg_port=5432
  [[ $odoo_maj -eq 18 ]] && pg_port=5432

  for ctr in {11..0}; do
      [[ -z $pg_port ]] && sts=1 || sts=0
      # echo "ss -lt|$pg_port"
      # ss -l|grep $pg_port &>/dev/null
      # s=$? && [[ $s -ne 0 ]] && sts=$s
      # [[ $sts -ne 0 ]] && msg="$msg\nNo postgresql running found at port $pg_port ($db)" && break

      # echo "ss -lt|grep 0.0.0.0:$port"
      ss -lt|grep 0.0.0.0:$port
      s=$? && [[ $s -ne 0 ]] && sts=$s
      if [[ $sts -ne 0 ]]; then
        echo "No Odoo instance running found at port $port ($svc) ..."
        # echo sudo systemctl start $svc
        odooctl start $svc
        sleep 5
        ss -lt|grep 0.0.0.0:$port
        [[ $? -eq 0 ]] && sts=0
      fi
      [[ $sts -ne 0 ]] && msg="$msg\nNo Odoo instance running found at port $port ($svc)" && break
      # echo "psql -U$pg_user -p $pg_port -Atl|grep -E \"^$db\|\""
      psql -U$pg_user -p $pg_port -Atl|grep -E "^$db\|" 1>/dev/null
      s=$? && [[ $s -ne 0 ]] && sts=$s
      [[ $sts -ne 0 ]] && msg="$msg\nDatabase $db not found!" && break
      [[ $sts -eq 0 ]] && break
  done
done
[[ -n $msg ]] && echo -e $msg && exit 1
exit 0
