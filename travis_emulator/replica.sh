__version__=0.1.8
if [ "$1" == "-V" ]; then
  echo $__version__
  exit 0
fi
echo "replica"
if [ "${HOSTNAME:0:6}" == "shsdef" ]; then
  src="dev"
  tgthost="fff17prd"
elif [ "$HOSTNAME" == "fff17prd" ]; then
  src="prd"
  tgthost="shsdef16"
elif [ "${HOSTNAME:0:6}" == "shsdev" ]; then
  src="dev"
  tgthost="shsprd16"
elif [ "${HOSTNAME:0:6}" == "shsprd" ]; then
  src="prd"
  tgthost="shsdev16"
elif [ "$HOSTNAME" == "erp-copia" ]; then
  src="dev"
  tgthost="erp"
elif [ "$HOSTNAME" == "erp" ]; then
  src="prd"
  tgthost="erp-copia"
elif [ "$HOSTNAME" == "erp-copia" ]; then
  src="dev"
  tgthost="erp"
else
  echo "Unknown machine role"
  exit 1
fi
cwd="$PWD"
if [ -z "$1" ]; then
  fls="*"
  flt=
else
  fls="$1"
  flt="$1"
fi
dir $cwd/$fls
a=$(find . -type d|grep "\./")
if [ -n "$a" ]; then
  opts=-r
else
  opts=
fi
echo "> scp $opts $cwd/$fls $tgthost:$cwd/$flt"
dummy=
while [ -z "$dummy" ]; do
  read -p "confirm copy (yes/no)?" dummy
  if [ "$dummy" == "yes" ]; then
    echo "\$ scp $opts $cwd/$fls $tgthost:$cwd/$flt"
    scp $opts $cwd/$fls $tgthost:$cwd/$flt
  elif [ "$dummy" != "no" ]; then
    dummy=""
  fi
done
