#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=$(echo -e "import sys\nprint(str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1])"|python)
for d in $TDIR $TDIR/.. $TDIR/../.. $HOME/dev $HOME/tools ${PYPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ] && [ -e $d/z0lib/z0librc ]; then
    . $d/z0lib/z0librc
    Z0LIBDIR=$d/z0lib
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)
Z0TLIBDIR=$(findpkg z0testrc "$TDIR $TDIR/.. $HOME/tools/zerobug $HOME/dev ${PYPATH//:/ } . .." "zerobug")
if [ -z "$Z0TLIBDIR" ]; then
  echo "Library file z0testrc not found!"
  exit 2
fi
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)

__version__=0.3.28.11
VERSIONS_TO_TEST="14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1"
MAJVERS_TO_TEST="14 13 12 11 10 9 8 7 6"
SUB_TO_TEST="v V VENV- odoo odoo_ ODOO OCB- oca librerp VENV_123- devel"


test_01() {
    local b m o s sts v w x
    sts=0
    local TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        # TODo
        [[ $m =~ (6|7) ]] && continue
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [ ${opt_dry_run:-0} -eq 0 ] && Z0BUG_build_odoo_env "$HOME/$w"

            export opt_multi=0
            TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$HOME/$w/openerp-server"
            ## [[ $w =~ (v|V)(7|6) ]] && TRES="$HOME/$w/server/openerp-server"
            [[ $w =~ V(7|6) ]] && TRES="$HOME/$w/openerp-server"
            [[ $w =~ v(7|6) ]] && TRES="$HOME/$w/server/openerp-server"
            ## [[ $v == "6.1" ]] && TRES="$HOME/$w/server/openerp-server"
            [[ $v == "6.1" ]] && TRES="$HOME/$w/openerp-server"
            b=$(basename $TRES)
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/$b"
            [[ $x =~ ^VENV && $v == "6.1" ]] && TRES="$HOME/$w/odoo/server/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(run_odoo_debug -b $w -n)
            echo $RES | grep "$TRES.*--config" > /dev/null
            [ $? -eq 0 ] &&  s=0 || s=1
            test_result "$opt_multi>$TRES -b $w" "$s" "0"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_multi=1
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/odoo-bin" || TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$(dirname $TRES)/openerp-server"
            ## [[ $w =~ (v|V)(7|6) ]] && TRES="$(dirname $TRES)/server/openerp-server"
            [[ $w =~ v(7|6) ]] && TRES="$(dirname $TRES)/server/openerp-server"
            [[ $w =~ V(7|6) ]] && TRES="$(dirname $TRES)/openerp-server"
            if [[ $v == "6.1" ]]; then
                [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/server/openerp-server" || TRES="$HOME/$w/server/openerp-server"
            fi
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(run_odoo_debug -b $w -n)
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
parseoptest -l$TESTDIR/test_clodoo.log "$@" "-O"
sts=$?
if [ $sts -ne 127 ]; then
  exit $sts
fi
if [ ${opt_oeLib:-0} -ne 0 ]; then
  ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $HOME/tools/clodoo $HOME/dev ${PYPATH//:/ } . .." "clodoo")
  if [ -z "$ODOOLIBDIR" ]; then
    echo "Library file odoorc not found!"
    exit 2
  fi
  . $ODOOLIBDIR
fi

UT1_LIST=
UT_LIST=""
if [ "$(type -t Z0BUG_setup)" == "function" ]; then Z0BUG_setup; fi
Z0BUG_main_file "$UT1_LIST" "$UT_LIST"
sts=$?
if [ "$(type -t Z0BUG_teardown)" == "function" ]; then Z0BUG_teardown; fi
exit $sts
