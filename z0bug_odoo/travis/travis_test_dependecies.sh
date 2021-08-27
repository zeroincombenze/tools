#! /bin/bash
# -*- coding: utf-8 -*-
#
# Run test in travis environment
# This script is default script to run syntax and regression tests
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$($READLINK -f $(dirname $0))
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys\np=[x for x in (os.environ['PATH']+':$TDIR:..:$HOME_DEV').split(':') if x not in sys.path];p.extend(sys.path);print(' '.join(p))"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$($READLINK -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
TRAVISLIBDIR=$(findpkg travisrc "$PYPATH" "travis_emulator")
if [[ -z "$TRAVISLIBDIR" ]]; then
  echo "Library file travisrc not found!"
  exit 72
fi
. $TRAVISLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TRAVISLIBDIR=$TRAVISLIBDIR"

__version__=1.0.1.3


OPTOPTS=(h        c        j        n            q           t         V           v)
OPTDEST=(opt_help opt_conf opt_dprj opt_dry_run  opt_verbose test_mode opt_version opt_verbose)
OPTACTI=(1        "="      1        1            0           1         "*>"        "+")
OPTDEFL=(0        ""       0        0            -1          0         ""          -1)
OPTMETA=("help"   "file"   "dprj"   "do nothing" "qiet"      "test"    "version"   "verbose")
OPTHELP=("this help"\
 "configuration file (def .travis.conf)"\
 "execute tests in project dir rather in test dir"\
 "do nothing (dry-run)"\
 "silent mode"\
 "test mode (implies dry-run)"\
 "show version"\
 "verbose mode")
OPTARGS=(pkg PRJNAME)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
    echo "$__version__"
    exit 0
fi
if [[ $opt_help -gt 0 ]]; then
    print_help "Run dependecies test in travis environment" \
               "(C) 2015-2021 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
    exit 0
fi

[ "${MQT_DRY_RUN:-0}" == "1" ] && opt_dry_run=1
[ "${MQT_VERBOSE_MODE:-0}" == "1" ] && opt_verbose=1
[ "${MQT_VERBOSE_MODE:-1}" == "0" ] && opt_verbose=0
[ ${TRAVIS_DEBUG_MODE:-0} -ne 0 ] && opt_verbose=1

opts_travis
CFG_init
conf_default
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -gt 2 ]] && set -x
init_travis
prepare_env_travis

sts=0
echo "======[Show dependecies tree mismatch]======"
MODULES=""
for fn in $(find . -maxdepth 2 -name __manifest__.py); do
    module=$(basename $(dirname $fn))
    MODULES="$MODULES,$module"
done
MODULES=${MODULES:1}
PATHS="$TRAVIS_BUILD_DIR"
for p in odoo/addons openerp/addons addons; do
    [[ -d ${ODOO_REPO}-${VERSION}/$p ]] && PATHS="$PATHS ${ODOO_REPO}-${VERSION}/$p"
done
PATHS="$PATHS $HOME/dependencies"
[[ $TRAVIS_DEBUG_MODE -gt 0 ]] && echo "Paths: $PATHS"
[[ $TRAVIS_DEBUG_MODE -gt 0 ]] && echo "Modules to test: $MODULES"
odoo_dependencies.py -A tree -RE $PATHS -M$MODULES
echo -e "\n\n"
exit $sts
