[[ -z $1 ]] && echo "$0 odoo_root branch" && exit 1
b="$2"
root="$1"
[[ -z $b ]] && b="10.0"
[[ -z $root ]] && root="$HOME/$b"
odoo_root=$(basename $root)
echo -e "Analyzing and recloning path \e[32m$root\e[0m by branch \e[32m$b\e[0m ..."
ctr=0
upd=0
for g in $(find $root -name ".git" | sort); do
    p=$(dirname $g) && cd $p && r=$(basename $p) && echo -e "\n\e[31m$r\e[0m - git ls-remote --heads git@github.com:zeroincombenze/$r.git $b"
    ((ctr++))
    [[ $r == "OCB" ]] && continue
    [[ $r == "odoo" ]] && continue
    [[ $r == $odoo_root ]] && continue
    URL="https://github.com/OCA/$r.git"
    URL2="/odoo/$r.git"
    t=$(git ls-remote --heads git@github.com:zeroincombenze/$r.git $b 2>&1)
    git remote -v | grep -E "($URL|$URL2)" && continue
    echo $t | grep refs/heads/$b && continue
    echo $t | grep -v "ERROR"

    git remote -v
    read -p "Reclone $r [y/N]? " dummy
    [[ ! $dummy == "y" ]] && continue

    ((upd++))
    cd ..
    rm -fR $g
    git clone $URL -b $b
    echo ""
done
deploy_odoo status -p $root
echo ""
echo "$ctr repositories read, $upd repositories recloned"
