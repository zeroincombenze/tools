[[ -z $1 || $1 == "-h" || $1 == "--help" ]] && echo "$0 OCB_REPO DEF_GITORG -b BRANCH [-e][-g][-K][-r][--remote-repo=REMOTE_REPO]" && exit 1
[[ $1 == -V ]] && echo "2.0.0" && exit 1
repo=""
gitorg=""
branch=""
use_git=1
skip_exist=1
keep_ocb_own=0
param=""
sts=0
while [[ -n "$1" ]]; do
    [[ -z $1 ]] &&  sts=1
    [[ $sts -eq 0 && -n $param ]] && eval $param="$1" && param="" && sts=1
    [[ $sts -eq 0 && $1 =~ -b ]] && param="branch" && sts=1
    [[ $sts -eq 0 && $1 =~ -e ]] && skip_exist=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -g ]] && use_git=1 && sts=1
    [[ $sts -eq 0 && $1 =~ -K ]] && keep_ocb_own=1 && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-repo= ]] && x=$(echo $1|cut -d= -f2) && REMOTE_REPO="$x" && sts=1
    [[ $sts -eq 0 && $1 =~ --remote-repo ]] && param="REMOTE_REPO" && sts=1
    [[ $sts -eq 0 && $1 =~ -r ]] && param="REMOTE_REPO" && sts=1
    [[ $sts -eq 0 && -z $repo ]] && repo="$1" && sts=1
    [[ $sts -eq 0 && -z $gitorg ]] && gitorg="$1" && sts=1
    [[ $sts -eq 0 ]] && echo "Unknow value $1"
    shift
    sts=0
done
[[ -z $repo ]] && echo "Missing repo" && exit 1
[[ -z $gitorg && $branch =~ (16.0|17.0|18.0|19.0|20.0) ]] && gitorg="oca"
[[ -z $gitorg ]] && gitorg="zero"
[[ ! $gitorg =~ ^(zero|oca|essetech)$ ]] && echo "Missing or invalid default gitorg $gitorg" && exit 1
[[ -z $branch ]] && echo "Missing branch" && exit 1
[[ -z $REMOTE_REPO ]] && REMOTE_REPO="$repo"
[[ $branch =~ (6.1|7.0|8.0|10.0) ]] && keep_ocb_own=1

echo "Searching for repo:"
echo "\$ find /mnt/ubuntu22/home/odoo/$REMOTE_REPO -maxdepth 2 -type d -name \".git\""
REPOS=$(find /mnt/ubuntu22/home/odoo/$REMOTE_REPO -maxdepth 2 -type d -name ".git" -exec dirname '{}' \; | xargs basename -a | sed -E "s/$repo/addons/" | sort | tr -d " " | tr "\n" ",")
[[ -z $REPOS ]] && echo "No repo found!" && exit 1
REPOS="${REPOS/$branch/}"
REPOS="OCB,${REPOS:0: -1}"
REPOS="${REPOS//,,/,}"
[[ $use_git -eq 1 ]] && opts="-gG$gitorg" || opts="-G$gitorg"
[[ $branch =~ (16.0|18.0) && $gitorg == "oca" ]] && opts="-gGessetech,$gitorg"
[[ $gitorg != "oca" ]] && opts="$opts,oca"
[[ $keep_ocb_own -ne 0 ]] && opts="$opts -K"
[[ $skip_exit -ne 0 ]] && opts="$opts -e"
opts="$opts -kmv"
echo "Download all repositories with branch $branch into $repo"
echo ""
echo deploy_odoo clone -b$branch $opts -p /home/odoo/$repo -r $REPOS

echo ""
deploy_odoo clone -b$branch $opts -p /home/odoo/$repo -r $REPOS
for p in ${REPOS//,/ }; do
    [[ $p == "OCB" ]] && continue
    [[ -d /home/odoo/$repo/$p ]] && continue
    echo "*** Repo $p not found! ***"
done
exit 0
