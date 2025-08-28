PYPI="/home/odoo/devel/pypi"

find $PYPI -type f -not -path "*/.*/*" -not -path "*/venv_odoo/*" -not -path "*/venv/*" -not -path "*/setup/*" -not -path "*/__pycache__/*" -not -path "*/egg-info/*" -not -path "*/build/*" -not -path "*/_build/*" -not -path "*/dist/*" -name "*.sh"  > ~/tmp.log
for p in $(find $PYPI -type f -not -path "*/.*/*" -not -path "*/venv_odoo/*" -not -path "*/venv/*" -not -path "*/setup/*" -not -path "*/__pycache__/*" -not -path "*/egg-info/*" -not -path "*/build/*" -not -path "*/_build/*" -not -path "*/dist/*" -not -name "*.bak" -not -name "*~" -executable); do
    file -b --mime-type $p | grep -Eq "text/x-shellscript" && echo "$p" >> ~/tmp.log
done
LL=$(cat ~/tmp.log | sort | uniq | tr -d " " | tr "\n" " ")
for p in $LL; do
    echo cvt_script -k $p
    /home/odoo/devel/pypi/arcangelo/arcangelo/scripts/cvt_script.sh -k $p
done
