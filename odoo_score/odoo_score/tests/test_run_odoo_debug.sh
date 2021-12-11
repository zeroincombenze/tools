#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 1.0.2.7
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
HOME_DEV="$HOME/devel"
[[ -x $TDIR/../bin/python ]] && PYTHON=$(readlink -f $TDIR/../bin/python) || [[ -x $TDIR/python ]] && PYTHON="$TDIR/python" || PYTHON="python"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\no=os.path\nHOME=os.environ.get('HOME');t=o.join(HOME,'tools')\nn=o.join(HOME,'pypi') if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME,HOME_DEV, 'pypi')\nd=HOME_DEV if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME_DEV,'venv')\ndef apl(l,p,b):\n if p:\n  p2=o.join(p,b,b)\n  p1=o.join(p,b)\n  if o.isdir(p2):\n   l.append(p2)\n  elif o.isdir(p1):\n   l.append(p1)\nl=[TDIR]\nv=''\nfor x in sys.path:\n if not o.isdir(t) and o.isdir(o.join(x,'tools')):\n  t=o.join(x,'tools')\n if not v and o.basename(x)=='site-packages':\n  v=x\nfor x in os.environ['PATH'].split(':'):\n if x.startswith(d):\n  d=x\n  break\nfor b in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(d):\n  apl(l,d,b)\n elif TDIR.startswith(n):\n  apl(l,n,b)\n apl(l,v,b)\n apl(l,t,b)\nl=l+os.environ['PATH'].split(':')\ntdir=o.dirname(TDIR)\np=set()\npa=p.add\np=[x for x in l if x and (x.startswith(HOME) or x.startswith(HOME_DEV) or x.startswith(tdir)) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found in <$PYPATH>!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
Z0TLIBDIR=$(findpkg z0testrc "$PYPATH" "zerobug")
if [[ -z "$Z0TLIBDIR" ]]; then
  echo "Library file z0testrc not found!"
  exit 72
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0TLIBDIR=$Z0TLIBDIR"

DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=1.0.4.2
VERSIONS_TO_TEST="14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1"
MAJVERS_TO_TEST="14 13 12 11 10 9 8 7 6"
SUB_TO_TEST="v V VENV- odoo odoo_ ODOO OCB- oca librerp VENV_123- devel"


test_01() {
    local b m o s sts v w x
    sts=0
    local TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        # TODO> cannot test 6.1
        [[ $v == "6.1" ]] && continue
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [[ ${opt_dry_run:-0} -eq 0 ]] && Z0BUG_build_odoo_env "$HOME/$w"

            export opt_multi=0
            TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$HOME/$w/openerp-server"
            [[ $w =~ V(7|6) ]] && TRES="$HOME/$w/openerp-server"
            [[ $w =~ v(7|6) ]] && TRES="$HOME/$w/server/openerp-server"
            [[ $v == "6.1" ]] && TRES="$HOME/$w/openerp-server"
            b=$(basename $TRES)
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/$b"
            [[ $x =~ ^VENV && $v == "6.1" ]] && TRES="$HOME/$w/odoo/server/openerp-server"
            [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(run_odoo_debug -b $w -n 2>&1 | grep -vE "File .*no.*(exist|esistente)")
            echo $RES | grep "$TRES.*--config" > /dev/null
            [ $? -eq 0 ] &&  s=0 || s=1
            test_result "$opt_multi>$TRES -b $w" "$s" "0"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_multi=1
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/odoo-bin" || TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$(dirname $TRES)/openerp-server"
            [[ $w =~ v(7|6) ]] && TRES="$(dirname $TRES)/server/openerp-server"
            [[ $w =~ V(7|6) ]] && TRES="$(dirname $TRES)/openerp-server"
            if [[ $v == "6.1" ]]; then
                [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/server/openerp-server" || TRES="$HOME/$w/server/openerp-server"
            fi
            [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(run_odoo_debug -b $w -n 2>&1 | grep -vE "File .*no.*(exist|esistente)")
            echo $RES | grep "$TRES.*--config" > /dev/null
            [ $? -eq 0 ] &&  s=0 || s=1
            test_result "$opt_multi>$TRES -b $w" "$s" "0"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done
    return $sts
}


Z0BUG_setup() {
    local f m o v w x OS_TREE
    [ ${opt_dry_run:-0} -ne 0 ] && return
    export ODOO_GIT_ORGID=zero
    export ODOO_GIT_SHORT="(oca|librerp)"
    export ODOO_DB_USER=""

    for v in $VERSIONS_TO_TEST $MAJVERS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12|6) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (odoo|odoo_|ODOO|oca|librerp) ]] && w="$x$m"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (oca|librerp) ]] && w="odoo${m}-$x"
            OS_TREE="$OS_TREE $w $HOME/$w"
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero"; do
                    OS_TREE="$OS_TREE $x${m}${o} $HOME/$x${m}${o}"
                done
            fi
        done
    done
    Z0BUG_remove_os_tree "$OS_TREE"
}

__Z0BUG_teardown() {
    local f m o v w x OS_TREE
    [ ${opt_dry_run:-0} -ne 0 ] && return
    for v in $VERSIONS_TO_TEST $MAJVERS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12|6) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (odoo|odoo_|ODOO|oca|librerp) ]] && w="$x$m"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (oca|librerp) ]] && w="odoo${m}-$x"
            OS_TREE="$OS_TREE $w $HOME/$w"
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero"; do
                    OS_TREE="$OS_TREE $x${m}${o} $HOME/$x${m}${o}"
                done
            fi
        done
    done
    Z0BUG_remove_os_tree "$OS_TREE"
}


Z0BUG_init
parseoptest -l$TESTDIR/test_odoo_score.log "$@"
sts=$?
[[ $sts -ne 127 ]] && exit $sts


UT1_LIST=
UT_LIST=""
[[ "$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
[[ "$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit $sts
