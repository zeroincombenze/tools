mesg=""
[[ -n "$4" ]] || mesg="Missed odoo verion"
[[ -f "$3" ]] || mesg="Missed conf file"
[[ -d "$2" ]] || mesg="Missed Odoo path"
[[ -n "$1" ]] || mesg="Missed DB"
if [[ -n "$mesg" ]]; then
    echo "$mesg"
    echo "$0 db path conf oever [-W]"
    exit 1
fi
cd ~/clodoo
echo "Analizing modules ..."
MODULES=$(odoo_dependencies.py -D $1 -c $3 ~/$2 -A tree|sort -rg|awk '{print $2}'|tr "\n" " ")
echo "Module found: $MODULES"
read -p "Press RET to start test"
sts=0
for module in $MODULES; do
    echo ""
    echo "Analizing module $module ..."
    echo ""
    echo "run_odoo_debug -b $4 $5 -d $1 -usm $module"
    run_odoo_debug -b $4 $5 -d $1 -usm $module
    s=$?
    if [ $s -ne 0 ]; then
        sts=$s
        echo "Upgrade is failed!"
    fi
    read -p "Press RET to continue"
done

