# __version__=2.0.18
# Based on template 2.1.1
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
ME=$(readlink -e $0)
if [[ -d $HOME/devel || -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
PYPATH=""
[[ $(basename $PWD) == "tests" && $(basename $PWD/../..) == "build" ]] && PYPATH="$(dirname $PWD)"
[[ $(basename $PWD) == "tests" && $(basename $PWD/../..) == "build" && -d $PWD/../scripts ]] && PYPATH="$PYPATH $(readlink -f $PWD/../scripts)"
x=$ME; while [[ $x != $HOME && $x != "/" && ! -d $x/lib && ! -d $x/bin && ! -d $x/pypi ]]; do x=$(dirname $x); done
[[ -d $x/pypi ]] && PYPATH="$PYPATH $x/pypi"
[[ -d $x/pypi/z0lib ]] && PYPATH="$PYPATH $x/pypi/z0lib"
[[ -d $x/pypi/z0lib/z0lib ]] && PYPATH="$PYPATH $x/pypi/z0lib/z0lib"
[[ -d $x/tools ]] && PYPATH="$PYPATH $x/tools"
[[ -d $x/tools/z0lib ]] && PYPATH="$PYPATH $x/tools/z0lib"
[[ -d $x/bin ]] && PYPATH="$PYPATH $x/bin"
[[ -d $x/lib ]] && PYPATH="$PYPATH $x/lib"
[[ -d $HOME_DEVEL/venv/bin ]] && PYPATH="$PYPATH $HOME_DEVEL/venv/bin"
[[ -d $HOME_DEVEL/../tools ]] && PYPATH="$PYPATH $(readlink -f $HOME_DEVEL/../tools)"
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $TDIR $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
[[ -z "$Z0LIBDIR" ]] && echo "Library file z0librc not found in <$PYPATH>!" && exit 72
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
