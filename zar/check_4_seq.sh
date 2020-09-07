#!/usr/bin/env bash
# __version__=1.3.35
THIS=$(basename $0)
if [ -z "$1" ]; then
  echo "$0 db [user] [-f|-z]"
  exit 1
fi
user=${2:-odoo}
while IFS=\| read a tbl typ own; do
  if [[ "$a" == "public" && ( "$typ" == "table" || "$typ" == "tabella" ) && "$own" == $user ]]; then
    # echo "Table=$tbl type=$typ own=$own"
    sql="select last_value from ${tbl}_id_seq;"
    psql -tc "$sql" "$1" &>/dev/null
    if [ $? -eq 0 ]; then
      last=$(psql -tc "$sql" "$1")
      last=$(printf "%d" $last)
      sql="select max(id) from ${tbl};"
      psql -tc "$sql" "$1" &>/dev/null
      if [ $? -eq 0 ]; then
        max=$(psql -tc "$sql" "$1")
        max=$(printf "%d" $max)
        if [ $last -lt $max ] || [ "$3" == "-z" -a $max -eq 0 ] || [ "$3" == "-f" -a $last -ne $max ]; then
          [ $last -lt $max ] && echo "*** Error in table $tbl: last value $last < max $max! ***"
          [ $last -ge $max ] && echo "Reset table $tbl: last value $last != max $max!!"
          ((max++))
          psql -c "alter sequence ${tbl}_id_seq restart $max" "$1"
        else
          printf "Table %-50.50s (%d/%d)\n" "$tbl" $last $max
        fi
      fi
    fi
  fi
done < <(psql -Atc "\\d" "$1")
