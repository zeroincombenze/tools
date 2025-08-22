[[ -z $1 ]] && echo "$0 PYPIPKG [-fU3]" && exit 1
# set -v
[[ $2 =~ -.*3 ]] && V="$HOME/VENV_3" || V="$HOME/VENV_2"
[[ $2 =~ -.*3 ]] && PY="3.7" || PY="2.7"
[[ ! -d $V || $2 =~ -.*f ]] && echo "\$ vem create $V -DIf -p$PY" && vem create $V -DIf -p$PY
[[ $2 =~ -.*U ]] && echo "\$ vem $V update $1 -BBB" &&  vem $V update $1 -BBB
[[ ! -d $V/build ]] && mkdir $V/build
[[ ! -d $V/build/$1 ]] && mkdir $V/build/$1
[[ ! -d $V/tools ]] && cp -r $HOME/tools/ $V/
echo rsync -avz --delete $HOME/devel/pypi/$1/$1/ $V/build/$1/
rsync -avz --delete $HOME/devel/pypi/$1/$1/ $V/build/$1/
echo cd $V
cd $V
rm -f $V/*.log
for v in 15.0 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1; do
  m=$(echo $v|grep --color=never -Eo '[0-9]+'|head -n1)
  for x in '' VENV OCB oca odoo ODOO v V powerp librerp; do
    [[ -d $V/${x}$v ]] && rm -fR $V/${x}$v
    [[ -d $V/${x}$m ]] && rm -fR $V/${x}$m
    [[ -d $V/${x}-$v ]] && rm -fR $V/${x}-$v
    [[ -d $V/${x}-$m ]] && rm -fR $V/${x}-$m
    [[ -d $V/${x}_$v ]] && rm -fR $V/${x}_$v
    [[ -d $V/${x}_$m ]] && rm -fR $V/${x}_$m
    for y in odoo oca zero powerp devel; do
      [[ -d $V/${x}$v-$y ]] && rm -fR $V/${x}$v-$y
      [[ -d $V/${x}$m-$y ]] && rm -fR $V/${x}$m-$y
    done
  done
done
echo ". bin/activate"
. bin/activate
cd $V/build/$1/tests
rm -f $V/build/$1/.coveragerc
# which zerobug
coverage erase
export TRAVIS_BUILD_DIR="$V/build/$1"
echo ""
echo "##########################################################################################################"
zerobug
deactivate
cd $V/build/$1/tests
coverage report
