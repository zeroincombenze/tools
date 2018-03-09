if [ -z "$1" ]; then
  echo $0 user dbname
  exit 1
fi
psql -U$1 -P "pager=off" -F";" -Atc 'select I.name,G.name from ir_module_category I,res_groups G where G.category_id=I.id order by I.name,G.id;' $2
