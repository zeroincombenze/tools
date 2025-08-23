#! /bin/bash
# -*- coding: utf-8 -*-
# Regression tests on clodoo
#
# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
# Based on template 2.0.0
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
[[ -x $TDIR/../bin/python3 ]] && PYTHON=$(readlink -f $TDIR/../bin/python3) || [[ -x $TDIR/python3 ]] && PYTHON="$TDIR/python3" || PYTHON=$(which python3 2>/dev/null) || PYTHON="python"
[[ -z $PYPATH ]] && PYPATH=$(echo -e "import os,sys\no=os.path\na=o.abspath\nj=o.join\nd=o.dirname\nb=o.basename\nf=o.isfile\np=o.isdir\nC=a('"$TDIR"')\nD='"$HOME_DEVEL"'\nif not p(D) and '/devel/' in C:\n D=C\n while b(D)!='devel':  D=d(D)\nN='venv_tools'\nU='setup.py'\nO='tools'\nH=o.expanduser('~')\nT=j(d(D),O)\nR=j(d(D),'pypi') if b(D)==N else j(D,'pypi')\nW=D if b(D)==N else j(D,'venv')\nS='site-packages'\nX='scripts'\ndef pt(P):\n P=a(P)\n if b(P) in (X,'tests','travis','_travis'):\n  P=d(P)\n if b(P)==b(d(P)) and f(j(P,'..',U)):\n  P=d(d(P))\n elif b(d(C))==O and f(j(P,U)):\n  P=d(P)\n return P\ndef ik(P):\n return P.startswith((H,D,K,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))\ndef ak(L,P):\n if P not in L:\n  L.append(P)\nL=[C]\nK=pt(C)\nfor B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n for P in [C]+sys.path+os.environ['PATH'].split(':')+[W,R,T]:\n  P=pt(P)\n  if B==b(P) and ik(P):\n   ak(L,P)\n   break\n  elif ik(j(P,B,B)):\n   ak(L,j(P,B,B))\n   break\n  elif ik(j(P,B)):\n   ak(L,j(P,B))\n   break\n  elif ik(j(P,S,B)):\n   ak(L,j(P,S,B))\n   break\nak(L,os.getcwd())\nprint(' '.join(L))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
[[ -z "$Z0LIBDIR" ]] && echo "Library file z0librc not found in <$PYPATH>!" && exit 72
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
Z0TLIBDIR=$(findpkg z0testrc "$PYPATH" "zerobug")
[[ -z "$Z0TLIBDIR" ]] && echo "Library file z0testrc not found!" && exit 72
. $Z0TLIBDIR
Z0TLIBDIR=$(dirname $Z0TLIBDIR)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0TLIBDIR=$Z0TLIBDIR"

# DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
# TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.9
# VERSIONS_TO_TEST="14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1"
# MAJVERS_TO_TEST="14 13 12 11 10 9 8 7 6"
VERSIONS_TO_TEST="16.0 14.0 12.0 10.0 8.0 7.0 6.1"
MAJVERS_TO_TEST="16 14 12 10 8 7 6"

SUB_TO_TEST="v V VENV- odoo odoo_ ODOO OCB- oca librerp VENV_123- devel"


test_01() {
    local RES s sts v w x
    local sts=0
    export opt_multi=0

    RES=$(build_odoo_param _FILE)
    test_result "bash> build_odoo_param _FILE" "$RUNDIR/odoorc" "$RES"
    RES=$(build_odoo_param _VER)
    test_result "bash> build_odoo_param _VER" "$__version__" "$RES"

    ## discover_multi
    ## test_result "Discover_multi (0)" "0" "$opt_multi"
    for v in 12 12.0 v12 V12 v12.0 V12.0 VENV-12.0 VENV_123-12.0; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "bash 1a.${opt_multi}> build_odoo_param FULLVER '$v'" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in odoo12 odoo_12 VENV_123-odoo12 odoo-12-devel odoo12-main odoo12-r10 odoo12-r20.0; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "bash 1b.${opt_multi}> build_odoo_param FULLVER '$v'" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "bash 1b.${opt_multi}> build_odoo_param GIT_ORGID '$v'" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "bash 1b.${opt_multi}> build_odoo_param GIT_ORGNM '$v'" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in OCB-12 OCB-12.0 oca12 odoo12-oca VENV-odoo12-oca VENV_123-odoo12-oca; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "bash 1c.${opt_multi}> build_odoo_param FULLVER '$v'" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "bash 1c.${opt_multi}> build_odoo_param GIT_ORGID '$v'" "oca" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "bash 1c.${opt_multi}> build_odoo_param GIT_ORGNM '$v'" "OCA" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in librerp12 odoo12-librerp odoo_12-librerp VENV-odoo12-librerp VENV_123-odoo12-librerp; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "bash 1d.${opt_multi}> build_odoo_param FULLVER '$v'" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "bash 1d.${opt_multi}> build_odoo_param GIT_ORGID '$v'" "librerp" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "bash 1d.${opt_multi}> build_odoo_param GIT_ORGNM '$v'" "LibrERP-network" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in librerp6 odoo6-librerp VENV-librerp6 VENV_123-librerp6; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "bash 1e.${opt_multi}> build_odoo_param FULLVER '$v'" "6.1" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "bash 1e.${opt_multi}> build_odoo_param GIT_ORGID '$v'" "librerp6" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "bash 1e.${opt_multi}> build_odoo_param GIT_ORGNM '$v'" "iw3hxn" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}


test_02() {
    local s sts m v w x
    sts=0
    export opt_multi=0
    local TRES

    for v in $MAJVERS_TO_TEST; do
        [[ "$v" == "6" ]] && TRES="$v.1" || TRES="$v.0"
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14|12|6) ]] && continue
            [[ $x == "devel" ]] && continue
            w="$x$v"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $w)
            test_result "bash 2a.${opt_multi}> build_odoo_param FULLVER '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [[ $x == "VENV_123-" ]] && continue

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$w"
                pushd $Z0BUG_root/$w>/dev/null || return 1
                RES=$(build_odoo_param FULLVER ".")
                popd >/dev/null || return 1
            fi
            test_result "bash 2b.${opt_multi} $PWD> build_odoo_param FULLVER '.'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $Z0BUG_root/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param FULLVER ".")
                fi
                test_result "bash 2c.${opt_multi} $PWD> build_odoo_param FULLVER '.'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$HOME/$w"
                pushd $HOME/$w>/dev/null || return 1
                RES=$(build_odoo_param FULLVER ".")
                popd >/dev/null || return 1
            fi
            test_result "bash 2e.${opt_multi} $PWD> build_odoo_param FULLVER '.'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $HOME/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param FULLVER ".")
                fi
                test_result "bash 2f.${opt_multi} $PWD> build_odoo_param FULLVER '.'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi
        done
    done

    unset TRES
    local TRES
    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        TRES=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14.0|12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "bash 2g.${opt_multi}> build_odoo_param MAJVER '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp) ]]; then
                w="$x$m"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
                test_result "bash 2h.${opt_multi}> build_odoo_param MAJVER '$w'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            [[ $x == "VENV_123-" ]] && continue

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$w"
                pushd $Z0BUG_root/$w>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                popd >/dev/null || return 1
            fi
            test_result "bash 2i.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero"; do
                    if [ ${opt_dry_run:-0} -eq 0 ]; then
                        Z0BUG_build_odoo_env "$x${m}${o}"
                        pushd $Z0BUG_root/$w>/dev/null || return 1
                        RES=$(build_odoo_param MAJVER ".")
                        popd >/dev/null || return 1
                    fi
                    test_result "bash 2j.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
            if [[ -d $Z0BUG_root/$w/odoo/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/odoo/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "bash 2k.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            elif [[ -d $Z0BUG_root/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "bash 2l.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            fi
            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$HOME/$w"
                pushd $HOME/$w>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                popd >/dev/null || return 1
            fi
            test_result "bash 2m.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $HOME/$w/odoo/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/odoo/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "bash 2n.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            elif [[ -d $HOME/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "bash 2o.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            fi

            [[ $x != "odoo" ]] && continue
            for o in "-oca" "-zero"; do
                Z0BUG_build_odoo_env "$HOME/$x${m}${o}"
                [ ${opt_dry_run:-0} -eq 0 ] && pushd $HOME/$x${m}${o}>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                test_result "bash 2p.${opt_multi} $PWD> build_odoo_param MAJVER '.'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            done
        done
    done

    discover_multi
    test_result "Discover_multi (1)" "1" "$opt_multi"
    return $sts
}

test_03() {
    local m o s sts v w x
    sts=0
    export opt_multi=0
    local TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14.0|12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            TRES="/etc/odoo/odoo.conf"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/etc/odoo/odoo-server.conf"
            [[ "$v" == "6.1" ]] && TRES="/etc/odoo/openerp-server.conf"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/etc/odoo/openerp-server.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "bash 3a.${opt_multi}> build_odoo_param CONFN '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES="/var/log/odoo/odoo.log"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/var/log/odoo/odoo-server.log"
            [[ "$v" == "6.1" ]] && TRES="/var/log/odoo/openerp-server.log"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/var/log/odoo/openerp-server.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "bash 3b.${opt_multi}> build_odoo_param FLOG '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES="/var/run/odoo/odoo.pid"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/var/run/odoo/odoo-server.pid"
            [[ "$v" == "6.1" ]] && TRES="/var/run/odoo/openerp-server.pid"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/var/run/odoo/openerp-server.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "bash 3c.${opt_multi}> build_odoo_param FPID '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES="/etc/init.d/odoo"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/etc/init.d/odoo-server"
            [[ "$v" == "6.1" ]] && TRES="/etc/init.d/openerp-server"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/etc/init.d/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "bash 3d.${opt_multi}> build_odoo_param FULL_SVCNAME '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "bash 3e.${opt_multi}> build_odoo_param SVCNAME '$w'" "$(basename $TRES)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done
    return $sts
}

test_04() {
    local m o s sts v w x
    sts=0
    local TRES
    export opt_multi=1

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14.0|12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x =~ (oca|librerp|devel) ]] && o="-${x}"
            TRES="/etc/odoo/odoo${m}${o}.conf"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/etc/odoo/odoo${m}-server.conf"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/etc/odoo/openerp-server.conf"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/etc/odoo/odoo-server.conf"
            [[ "$w" =~ (v|V)(16|15|14|13|12|11|10) ]] && TRES="/etc/odoo/odoo.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "bash 4a.${opt_multi}> build_odoo_param CONFN '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/etc/odoo/odoo${m}${o}.conf"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
                    test_result "bash 4a.${opt_multi}> build_odoo_param CONFN '$w'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES="/var/log/odoo/odoo${m}${o}.log"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/var/log/odoo/odoo${m}-server.log"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/var/log/odoo/openerp-server.log"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/var/log/odoo/odoo-server.log"
            [[ "$w" =~ (v|V)(16|15|14|13|12|11|10) ]] && TRES="/var/log/odoo/odoo.log"
            [[ $x =~ (oca|librerp) ]] && TRES="/var/log/odoo/odoo${m}-$x.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "bash 4b.${opt_multi}> build_odoo_param FLOG '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/var/log/odoo/odoo${m}${o}.log"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
                    test_result "bash 4b.${opt_multi}> build_odoo_param FLOG '$w'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES="/var/run/odoo/odoo${m}${o}.pid"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/var/run/odoo/odoo${m}-server.pid"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/var/run/odoo/openerp-server.pid"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/var/run/odoo/odoo-server.pid"
            [[ "$w" =~ (v|V)(16|15|14|13|12|11|10) ]] && TRES="/var/run/odoo/odoo.pid"
            [[ $x =~ (oca|librerp) ]] && TRES="/var/run/odoo/odoo${m}-$x.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "bash 4c.${opt_multi}> build_odoo_param FPID '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/var/run/odoo/odoo${m}${o}.pid"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
                    test_result "bash 4c.${opt_multi}> build_odoo_param FPID '$w'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES="/etc/init.d/odoo${m}${o}"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/etc/init.d/odoo${m}-server"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/etc/init.d/openerp-server"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/etc/init.d/odoo-server"
            [[ "$w" =~ (v|V)(16|15|14|13|12|11|10) ]] && TRES="/etc/init.d/odoo"
            [[ $x =~ (oca|librerp) ]] && TRES="/etc/init.d/odoo${m}-$x"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "bash 4d.${opt_multi}> build_odoo_param FULL_SVCNAME '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "bash 4d.${opt_multi}> build_odoo_param SVCNAME '$w'" "$(basename $TRES)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/etc/init.d/odoo${m}${o}"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
                    test_result "bash 4e.${opt_multi}> build_odoo_param FULL_SVCNAME '$w'" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
                    test_result "bash 4e.${opt_multi}> build_odoo_param SVCNAME '$w'" "$(basename $TRES)" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
        done
    done
    return $sts
}

test_05() {
    local b m o r s sts v w x
    sts=0
    local TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14.0|12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"

            export opt_multi=0
            TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$HOME/$w/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES="$HOME/$w/server/openerp-server"
            [[ $v == "6.1" ]] && TRES="$HOME/$w/server/openerp-server"
            b=$(basename $TRES)
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/$b"
            [[ $x =~ ^VENV && $v == "6.1" ]] && TRES="$HOME/$w/odoo/server/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "bash 5a.${opt_multi}> build_odoo_param BIN '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            b=$(dirname $TRES)
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "bash 5b.${opt_multi}> build_odoo_param ROOT '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w)
            test_result "bash 5b.${opt_multi}> build_odoo_param PKGPATH '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w)
            test_result "bash 5b.${opt_multi}> build_odoo_param HOME '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PARENTDIR $w)
            test_result "bash 5b.${opt_multi}> build_odoo_param PARENTDIR '$w'" "$(dirname $b)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "bash 5b.${opt_multi}> build_odoo_param ROOT '$w' 'crm'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w "crm")
            test_result "bash 5b.${opt_multi}> build_odoo_param PKGPATH '$w' 'crm'" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "bash 5b.${opt_multi}> build_odoo_param PARENTDIR '$w' 'crm'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w "crm")
            test_result "bash 5b.${opt_multi}> build_odoo_param HOME '$w' 'crm'" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp) ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "bash 5c.${opt_multi}> build_odoo_param ROOT '$v' 'OCB'" "$HOME/$v" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            export opt_multi=1
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/odoo-bin" || TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$(dirname $TRES)/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES="$(dirname $TRES)/server/openerp-server"
            if [[ $v == "6.1" ]]; then
                [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/server/openerp-server" || TRES="$HOME/$w/server/openerp-server"
            fi
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "bash 5d.${opt_multi}> build_odoo_param BIN '$w'" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ ! $x =~ (VENV_123-|v|V) && ! $v =~ (6\.1) ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w search)
                test_result "bash 5d.${opt_multi}> build_odoo_param BIN '$w' 'search'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            b=$(dirname $TRES)
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "bash 5d.${opt_multi}> build_odoo_param ROOT '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w)
            test_result "bash 5d.${opt_multi}> build_odoo_param PKGPATH '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w)
            test_result "bash 5d.${opt_multi}> build_odoo_param HOME '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PARENTDIR $w)
            test_result "bash 5d.${opt_multi}> build_odoo_param PARENTDIR '$w'" "$(dirname $b)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "bash 5d.${opt_multi}> build_odoo_param ROOT '$w'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w "crm")
            test_result "bash 5d.${opt_multi}> build_odoo_param PKGPATH '$w' 'crm'" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w "crm")
            test_result "bash 5d.${opt_multi}> build_odoo_param HOME '$w' 'crm'" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PARENTDIR $w "crm")
            test_result "bash 5d.${opt_multi}> build_odoo_param PARENTDIR '$w' 'crm'" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp) ]]; then
                [[ $x == "librerp" && $v == "6.1" ]] && continue
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "bash 5e.${opt_multi}> build_odoo_param ROOT '$v' 'OCB'" "$b" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi

            if [[ ! $x == "VENV_123-" ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    Z0BUG_build_odoo_env "$w"
                    Z0BUG_build_os_tree "$w/crm"
                    touch $Z0BUG_root/$w/.travis.yml
                    touch $Z0BUG_root/$w/crm/.travis.yml
                    mkdir -p $Z0BUG_root/$w/crm/.git
                    Z0BUG_build_module_path "$Z0BUG_root/$w/addons/crm" "$v"
                    pushd $Z0BUG_root/$w>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "bash 5d.${opt_multi} $PWD> build_odoo_param ROOT '.'" "$Z0BUG_root/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param REPOS ".")
                [[ $w == "librerp6" ]] &&  test_result "bash 5d.${opt_multi} $PWD> build_odoo_param REPOS '.'" "server" "$RES" || test_result "bash 5d.${opt_multi} $PWD> build_odoo_param REPOS '.'" "OCB" "$RES"
                # test_result "$PWD> REPOS '.' [bash]" "OCB" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param DIRLEVEL ".")
                test_result "bash 5d.${opt_multi} $PWD> build_odoo_param DIRLEVEL '.'" "OCB" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param DIRLEVEL "$Z0BUG_root/$w/crm")
                test_result "bash 5d.${opt_multi}> build_odoo_param DIRLEVEL '$Z0BUG_root/$w/crm'" "repository" "$RES"

                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )

                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/crm>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> ROOT '.' [bash]" "$Z0BUG_root/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param REPOS ".")
                test_result "$PWD> REPOS '.' [bash]" "crm" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && ( popd >/dev/null || return 1 )
            fi

            if [[ ! $x == "VENV_123-" ]]; then
                o="leads"
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    Z0BUG_build_odoo_env "$HOME/$w"
                    Z0BUG_build_os_tree "$HOME/$w/crm $HOME/$w/crm/$o"
                    touch $HOME/$w/.travis.yml
                    touch $HOME/$w/crm/.travis.yml
                    mkdir -p $HOME/$w/crm/.git
                    Z0BUG_build_module_path "$HOME/$w/crm/$o" "$v"
                    pushd $HOME/$w>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> ROOT '.' [bash]" "$HOME/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param LICENSE ".")
                [[ $m -le 8 ]] && r="AGPL" || r="LGPL"
                test_result "$PWD> LICENSE '.' [bash]" "$r" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param LICENSE "$HOME/$w/crm")
                test_result "5f> LICENSE '$w/crm/$o' [bash]" "$r" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param DIRLEVEL "$HOME/$w/crm/$o")
                test_result "5f> DIRLEVEL '$HOME/$w/crm/$o' [bash]" "module" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && ( popd >/dev/null || return 1 )

                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/crm>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> ROOT '.' [bash]" "$HOME/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                RES=$(build_odoo_param PKGPATH ".")
                test_result "$PWD> PKGPATH '.' [bash]" "$HOME/$w/crm/$o" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )

                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/crm/$o>/dev/null || return 1
                    RES=$(build_odoo_param PKGPATH ".")
                fi
                test_result "$PWD> PKGPATH '.' [bash]" "$HOME/$w/crm/$o" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                RES=$(build_odoo_param HOME ".")
                test_result "$PWD> HOME '.' [bash]" "$HOME/$w/crm" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi

            export opt_multi=0
            TRES=8069
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "5h> unique RPCPORT $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            TRES=8072
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param LPPORT $w)
            test_result "5h> unique LPPORT $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_multi=1
            ((TRES=m+8160))
            [[ $w =~ ^(v|V)[0-9] ]] && TRES=8069
            [[ $x =~ (odoo|odoo_|ODOO) ]] && ((TRES=m+8160))
            [[ $x =~ (OCB-|oca) ]] && ((TRES=m+8260))
            [[ $x =~ (librerp) ]] && ((TRES=m+8360))
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "5h> multi RPCPORT $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            ((TRES=m+8130))
            [[ $w =~ ^(v|V)[0-9] ]] && TRES=8072
            [[ $x =~ (odoo|odoo_|ODOO) ]] && ((TRES=m+8130))
            [[ $x =~ (OCB-|oca) ]] && ((TRES=m+8230))
            [[ $x =~ (librerp) ]] && ((TRES=m+8330))
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param LPPORT $w)
            test_result "5h> multi LPPORT $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    ((TRES=m+8160))
                    [[ $o == "-oca" ]] && ((TRES=m+8260))
                    [[ $o == "-zero" ]] && ((TRES=m+8460))
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                    test_result "5h> multi RPCPORT $w [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
        done

        export opt_multi=0
        [[ $v =~ (9.0|8.0|7.0|6.1) ]] && TRES="__openerp__.py"
        [[ $v =~ (16.0|15.0|14.0|13.0|12.0|11.0|10.0) ]] && TRES="__manifest__.py"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MANIFEST $v)
        test_result "5i> manifest $v [bash]" "$TRES" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s

        TRES="odoo"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param DB_USER $v)
        test_result "5i> unique db username $v [bash]" "$TRES" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param USER $v)
        test_result "5i> unique db username $v [bash]" "$TRES" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s

        export opt_multi=1
        TRES="odoo${m}"
        [[ $w =~ ^(v|V)[0-9] ]] && TRES="odoo"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param DB_USER $v)
        test_result "5i> multi db username $v [bash]" "$TRES" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param USER $v)
        test_result "5i> multi db username $v [bash]" "$TRES" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

test_06() {
    local b m o s sts v w x
    sts=0
    local TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14.0|12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"

            opt_multi=0
            [ $m -le 7 ] && TRES="$HOME/$w/openerp/filestore" || TRES="$HOME/.local/share/Odoo"
            if [[ $x =~ ^VENV ]]; then
                [ $m -le 7 ] && TRES="$HOME/$w/odoo/openerp/filestore" || TRES="$HOME/$w/.local/share/Odoo"
            elif [[ $w =~ (v|V) ]]; then
                [ $m -le 7 ] && TRES="$HOME/$w/openerp/filestore" || TRES="$HOME/.local/share/Odoo"
            fi
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param DDIR $w)
            test_result "6a> Unique DDIR $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done
    return $sts
}

test_07() {
    local b m o s sts v w x z
    sts=0
    local TRES

    export ODOO_GIT_ORGID="(librerp|zero)"
    opt_multi=1
    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for g in "" $SUB_TO_TEST; do
            [[ $g == "librerp" && ! $v =~ (14.0|12.0|6.1) ]] && continue
            [[ $g == "devel" ]] && w="${v}-$g" || w="$g$v"
            [[ $g =~ (oca|librerp) ]] && w="$g$m"
            for z in "OCB" "l10n-italy"; do
                # TODO>
                [[ $z == "OCB" && $v == "6.1" ]] && continue
                TRES="git@github.com:zeroincombenze/${z}.git"
                [[ $g =~ ^(odoo|ODOO) ]] && TRES="https://github.com/odoo/odoo.git"
                [[ $g =~ ^(odoo|ODOO) && ! $z == "OCB" ]] && continue
                [[ $g == "librerp" && $v == "6.1" && $z == "l10n-italy" ]] && continue
                [[ $g =~ ^(oca|OCB) ]] && TRES="https://github.com/OCA/${z}.git"
                [[ ( -z $g || $g =~ (v|V|VENV-|VENV_123-|devel|librerp) ) && $v =~ (14.0|12.0) && $z == "l10n-italy" ]] && TRES="git@github.com:LibrERP-network/${z}.git"
                [[ $g == "librerp" && $v == "6.1" ]] && TRES="git@github.com:iw3hgn/server.git"
                # [[ ${opt_dry_run:-0} -eq 0 && $z == "OCB" ]] && set -x && build_odoo_param GIT_URL $w $z && set +x    #debug
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param GIT_URL $w $z)
                test_result "bash 7a.${opt_multi}> build_odoo_param GIT_URL '$w' '$z'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RORIGIN $w $z)
                test_result "bash 7b.${opt_multi}> build_odoo_param RORIGIN '$w' '$z'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                [[ $v == "6.1" && $g =~ (odoo|odoo_|ODOO|oca|OCB) ]] && continue
                [[ $g =~ (odoo|odoo_|ODOO) && ! $z == "OCB" ]] && continue
                [[ $g =~ (odoo|odoo_|ODOO) ]] && TRES="https://github.com/odoo/odoo.git" || TRES="https://github.com/OCA/${z}.git"
                [[ $v == "6.1" ]] && TRES="git@github.com:zeroincombenze/${z}.git"
                [[ $g == "librerp" && $v == "6.1" ]] && TRES="git@github.com:iw3hxn/server.git"
                [[ $g == "librerp" && $v =~ (14.0|12.0) ]] && continue
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RUPSTREAM $w $z)
                test_result "bash 7c.${opt_multi}> build_odoo_param RUPSTREAM '$w' '$z'" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            done
            if [[ ! $g == "VENV_123-" ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    Z0BUG_build_os_tree "$w/venv_odoo $w/venv_odoo/bin"
                    touch $Z0BUG_root/$w/venv_odoo/bin/activate
                    pushd $Z0BUG_root/$w>/dev/null || return 1
                    RES=$(build_odoo_param VDIR ".")
                fi
                test_result "$PWD> VDIR '.' [bash]" "$Z0BUG_root/$w/venv_odoo" "$RES"
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    Z0BUG_remove_os_tree "$w/venv_odoo"
                    Z0BUG_build_os_tree "VENV-$w/bin"
                    touch $Z0BUG_root/VENV-$w/bin/activate
                    pushd $Z0BUG_root/$w>/dev/null || return 1
                    RES=$(build_odoo_param VDIR ".")
                fi
                test_result "$PWD> VDIR '.' [bash]" "$Z0BUG_root/VENV-$w" "$RES"
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
                RES=$(build_odoo_param VDIR "VENV-$w")
                test_result "7d> VDIR VENV-$w [bash]" "$HOME/VENV-$w" "$RES"
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi
        done
    done

    z="l10n-italy"
    if [[ $HOSTNAME =~ (shs[a-z0-9]{4,6}|zeroincombenze) && -d $HOME//10.0/${z} ]]; then
        if [ ${opt_dry_run:-0} -eq 0 ]; then
            pushd $HOME//10.0/${z}>/dev/null || return 1
            RES=$(build_odoo_param RORIGIN ".")
        fi
        TRES="git@github.com:zeroincombenze/${z}.git"
        test_result "$PWD> shs RORIGIN [bash]" "$TRES" "$RES"

        RES=$(build_odoo_param RUPSTREAM ".")
        TRES="https://github.com/OCA/${z}.git"
        test_result "$PWD> shs RUPSTREAM [bash]" "$TRES" "$RES"

        [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
    fi

    v="12.0"
    for z in accounting custom-addons double-trouble; do
        RES=$(build_odoo_param GIT_URL $v $z)
        [[ $z == "accounting" ]] && TRES="git@github.com:LibrERP-network/accounting.git" || TRES="git@github.com:LibrERP/$z.git"
        test_result "7e> multi GIT_URL $v/$z [bash]" "$TRES" "$RES"
    done
    return $sts
}

__test_08() {
    local s sts v w
    sts=0
    export opt_multi=1
    local TRES="OCB account-analytic account-budgeting account-closing account-consolidation account-financial-reporting account-financial-tools account-fiscal-rule account-invoice-reporting account-invoicing account-payment account-reconcile ansible-odoo apps-store bank-payment bank-statement-import brand business-requirement calendar commission community-data-files connector contract contribute-md-template credit-control crm currency data-protection ddmrp delivery-carrier department dms donation e-commerce edi event field-service fleet geospatial helpdesk hr hr-attendance hr-expense hr-holidays infrastructure intrastat-extrastat iot knowledge l10n-italy maintenance management-system manufacture manufacture-reporting margin-analysis mis-builder mis-builder-contrib multi-company operating-unit partner-contact payroll pms pos product-attribute product-configurator product-kitting product-pack product-variant program project project-agile project-reporting purchase-reporting purchase-workflow queue report-print-send reporting-engine rma role-policy sale-financial sale-reporting sale-workflow search-engine server-auth server-backend server-brand server-env server-tools server-ux social stock-logistics-barcode stock-logistics-reporting stock-logistics-tracking stock-logistics-transport stock-logistics-warehouse stock-logistics-workflow storage survey timesheet web webhook webkit-tools website website-cms website-themes wms zerobug-test"
    local RES=$(module_list "7.0")
    test_result "Module list 7.0" "$TRES" "$RES"

    TRES="OCB account-analytic account-budgeting account-closing account-consolidation account-financial-reporting account-financial-tools account-fiscal-rule account-invoice-reporting account-invoicing account-payment account-reconcile ansible-odoo apps-store bank-payment bank-statement-import brand business-requirement calendar commission community-data-files connector contract contribute-md-template credit-control crm currency data-protection ddmrp delivery-carrier department dms donation e-commerce edi event field-service fleet geospatial helpdesk hr hr-attendance hr-expense hr-holidays infrastructure intrastat-extrastat iot knowledge l10n-italy maintenance management-system manufacture manufacture-reporting margin-analysis mis-builder mis-builder-contrib multi-company operating-unit partner-contact payrollpms pos product-attribute product-configurator product-kitting product-pack product-variant program project project-agile project-reporting purchase-reporting purchase-workflow queue report-print-send reporting-engine rma role-policy sale-financial sale-reporting sale-workflow search-engine server-auth server-backend server-brand server-env server-tools server-ux social stock-logistics-barcode stock-logistics-reporting stock-logistics-tracking stock-logistics-transport stock-logistics-warehouse stock-logistics-workflow storage survey timesheet web webhook webkit-tools website website-cms website-themes wms zerobug-test"
    local RES=$(module_list "8.0")
    # test_result "Module list 8.0" "$TRES" "$RES"
}


Z0BUG_build_module_path() {
    local path=$1 ver=$2 b m
    mkdir -p $path
    touch $path/__init__.py
    [[ $v =~ (6.1|7.0|8.0|9.0|10.0) ]] && touch $path/__openerp__.py || touch $path/__manifest__.py
    [[ $v =~ (6.1|7.0|8.0|9.0|10.0) ]] && m="$path/__openerp__.py" || m="$path/__manifest__.py"
    b=$(basename $path)
    echo "{">$m
    echo "    'name': '$b'">>$m
    echo "    'version': '$v.0.1.0'">>$m
    [[ $b == "crm" && $v =~ (6.1|7.0|8.0) ]] && echo "    'license': 'AGPL-3'">>$m
    [[ $b == "crm" && ! $v =~ (6.1|7.0|8.0) ]] && echo "    'license': 'LGPL-3'">>$m
    [[ $b != "crm" ]] && echo "    'license': 'OPL-1'">>$m
    echo "}">>$m
}


Z0BUG_setup() {
# Modules Tree for tests
# l10n-italy/l10n_it_base
# addons/web
#   |---- addons/account
#   |---- addons/base
#   |---- addons/sale
#   \---- addons/web
# unported/l10n_it_base

    local f m o v w x OS_TREE
    [ ${opt_dry_run:-0} -ne 0 ] && return
    export ODOO_GIT_ORGID=zero
    export ODOO_GIT_SHORT="(oca|librerp)"
    export ODOO_DB_USER=""

    for v in $VERSIONS_TO_TEST $MAJVERS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (14|12|6) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (odoo|odoo_|ODOO|oca|librerp) ]] && w="$x$m"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (oca|librerp) ]] && w="odoo${m}-$x"
            OS_TREE="$OS_TREE $w $HOME/$w"
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
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
            [[ $x == "librerp" && ! $v =~ (14|12|6) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (odoo|odoo_|ODOO|oca|librerp) ]] && w="$x$m"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (oca|librerp) ]] && w="odoo${m}-$x"
            OS_TREE="$OS_TREE $w $HOME/$w"
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-zero" "-devel"; do
                    OS_TREE="$OS_TREE $x${m}${o} $HOME/$x${m}${o}"
                done
            fi
        done
    done
    Z0BUG_remove_os_tree "$OS_TREE"
}


Z0BUG_init
parseoptest -l$TESTDIR/test_clodoo.log "$@"
sts=$?
[[ $sts -ne 127 ]] && exit $sts
for p in z0librc odoorc travisrc zarrc z0testrc; do
  if [[ -f $RUNDIR/$p ]]; then
    [[ $p == "z0librc" ]] && Z0LIBDIR="$RUNDIR" && source $RUNDIR/$p && echo source $RUNDIR/$p
    [[ $p == "odoorc" ]] && ODOOLIBDIR="$RUNDIR" && source $RUNDIR/$p && echo source $RUNDIR/$p
    [[ $p == "travisrc" ]] && TRAVISLIBDIR="$RUNDIR" && source $RUNDIR/$p && echo source $RUNDIR/$p
    [[ $p == "zarrc" ]] && ZARLIB="$RUNDIR" && source $RUNDIR/$p && echo source $RUNDIR/$p
    [[ $p == "z0testrc" ]] && Z0TLIBDIR="$RUNDIR" && source $RUNDIR/$p && echo source $RUNDIR/$p
  fi
done


UT1_LIST=
UT_LIST=
[[ "$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
[[ $TRAVIS_PYTHON_VERSION == "2.7" ]] && Z0BUG_main_file "$UT1_LIST" "$UT_LIST" || true
sts=$?
[[ "$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit $sts


