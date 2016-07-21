q="-qb"
p="a"
if [ "$p" == "a" ] && [[  "$q" =~ q ]]; then
  echo "ok"
fi
