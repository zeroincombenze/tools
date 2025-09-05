[[ ! -d .git ]] && echo "It is not a git directory!" && exit 1
du -h .git
echo git gc --prune=now --aggressive
git gc --prune=now --aggressive
echo git clean -ndfx
git clean -ndfx
du -h .git
