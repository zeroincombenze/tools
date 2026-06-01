[[ -z $1 || $1 == "-h" || $1 == "--help" ]] && echo "$0 repo gitorg -b branch [-g][-K][-r][--remote-repo=REMOTE_REPO]" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1
repo=""
gitorg=""
branch=""
use_git=0
param=""
sts=0
while [[ -n "$1" ]]; do
    [[ -z $1 ]] &&  sts=1
    [[ $sts -eq 0 && -n $param ]] && eval $param="$1" && param="" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-repo= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_REPO="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-repo ]] && param="REMOTE_REPO" && sts=1
    [[ $sts -eq 0 && $1 =~ -b ]] && param="branch" && sts=1
    [[ $sts -eq 0 && $1 =~ -g ]] && use_git=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -K ]] && KEEP_OCB_OWN=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -r ]] && param="REMOTE_REPO" && sts=1
    [[ $sts -eq 0 && -z $repo ]] && repo="$1" && sts=1
    [[ $sts -eq 0 && -z $gitorg ]] && gitorg="$1" && sts=1
    [[ $sts -eq 0 ]] && echo "Unknow value $1"
    shift
    sts=0
done
[[ -z $repo ]] && echo "Missing repo" && exit 1
[[ ! $gitorg =~ ^(zero|oca|DueEsseTi)$ ]] && echo "Missing or invalid gitorg $gitorg" && exit 1
[[ -z $branch ]] && echo "Missing branch" && exit 1
[[ -z $REMOTE_REPO ]] && REMOTE_REPO="$repo"
[[ -z $KEEP_OCB_OWN ]] && KEEP_OCB_OWN=0

REPOS=$(find /mnt/ubuntu22/home/odoo/$REMOTE_REPO -maxdepth 2 -type d -name ".git" -exec dirname '{}' \; | xargs basename -a | sed -E "s/$repo/addons/" | sort | tr -d " " | tr "\n" ",")
[[ -z $REPOS ]] && echo "No repo found!" && exit 1
REPOS="OCB,${REPOS:0: -1}"
# echo $REPO
[[ $use_git -eq 1 ]] && opts="-gG$gitorg" || opts="-G$gitorg"
[[ $branch == "10.0" ]] && opts="-gG$gitorg -K"
# [[ $branch == "10.0" ]] && loc_repo="odoo10" || loc_repo="$repo"
echo "Download repo $repo with branch $branch"
echo ""
[[ $KEEP_OCB_OWN -eq 0 ]]&& opts="$opts -kev"
[[ $KEEP_OCB_OWN -ne 0 ]]&& opts="$opts -Kkev"
echo deploy_odoo clone -b$branch $opts -m -p /home/odoo/$repo -r $REPOS
deploy_odoo clone -b$branch $opts -m -p /home/odoo/$repo -r $REPOS
for p in ${REPOS//,/ }; do
    [[ $p == "OCB" ]] && continue
    [[ -d /home/odoo/$repo/$p ]] && continue
    echo "*** Repo $p not found! ***"
done
exit 0
