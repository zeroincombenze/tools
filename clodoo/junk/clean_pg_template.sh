if [ -z "$1" ]; then
    echo "$0 -n|-v"
    exit 1
fi
for tmpl in template0 template1 postgres; do
    echo "Recreating $tmpl"
    allowconn=true
    echo "psql -c \"update pg_database set datallowconn=$allowconn where datname='$tmpl';\""
    [ "$1" == "-v" ] && psql -c "update pg_database set datallowconn=$allowconn where datname='$tmpl';"
    TL=$(psql $tmpl -c "\dS" -at|grep " table "|grep -v " postgres"|awk -F"|" '{print $2}'|tr "\n" " ")
    echo "Table to drop: $TL"
    for tb in $TL;do
        echo "psql -c \"drop table $tb cascade;\" -d $tmpl;"
        [ "$1" == "-v" ] && psql -c "drop table $tb cascade;" -d $tmpl;
    done
    TL=$(psql $tmpl -c "\dS" -at|grep " sequence "|grep -v " postgres"|awk -F"|" '{print $2}'|tr "\n" " ")
    echo "Sequence to drop: $TL"
    for tb in $TL;do
        echo "psql -c \"drop sequence $tb;\" -d $tmpl;"
        [ "$1" == "-v" ] && psql -c "drop sequence $tb;" -d $tmpl;
    done
    echo "psql -c \"ALTER DATABASE $tmpl OWNER TO postgres\" $tmpl"
    [ "$1" == "-v" ] && psql -c "ALTER DATABASE $tmpl OWNER TO postgres" $tmpl
    echo "psql -c \"grant all privileges on database $tmpl to postgres;\""
    [ "$1" == "-v" ] && psql -c "grant all privileges on database $tmpl to postgres;"
    echo "psql -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='$tmpl';\""
    [ "$1" == "-v" ] && psql -c "UPDATE pg_database SET datistemplate='true' WHERE datname='$tmpl';"
    if [ "$tmpl" == "template0" ]; then
        allowconn=false
    else
        allowconn=true
    fi
    echo "psql -c \"update pg_database set datallowconn=$allowconn where datname='$tmpl';\""
    [ "$1" == "-v" ] && psql -c "update pg_database set datallowconn=$allowconn where datname='$tmpl';"
    psql -c "select datname, datallowconn from pg_database where datname='$tmpl';"
done
psql -l|grep "template"
