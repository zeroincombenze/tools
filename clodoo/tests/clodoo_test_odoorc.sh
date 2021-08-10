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

__version__=0.3.31.14
VERSIONS_TO_TEST="14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1"
MAJVERS_TO_TEST="14 13 12 11 10 9 8 7 6"
SUB_TO_TEST="v V VENV- odoo odoo_ ODOO OCB- oca powerp librerp VENV_123- devel"


test_01() {
    local RES s sts v w x
    local sts=0
    export opt_multi=0

    discover_multi
    test_result "Discover_multi (0)" "0" "$opt_multi"
    for v in 12 12.0 v12 V12 v12.0 V12.0 VENV-12.0 VENV_123-12.0; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1a> FULLVER $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in odoo12 odoo_12 VENV_123-odoo12 odoo-12-devel odoo12-main; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1b> FULLVER $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1b> GIT_ORGID $v" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1b> GIT_ORGNM $v" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in OCB-12 OCB-12.0 oca12 odoo12-oca VENV-odoo12-oca VENV_123-odoo12-oca; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1c> FULLVER $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1c> GIT_ORGID $v" "oca" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1c> GIT_ORGNM $v" "OCA" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in powerp12 odoo12-powerp odoo12-powerp odoo_12-powerp VENV-odoo12-powerp VENV_123-odoo12-powerp; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1d> FULLVER $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1d> GIT_ORGID $v" "powerp" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1d> GIT_ORGNM $v" "PowERP-cloud" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in librerp6 librerp odoo6-librerp VENV-librerp6 VENV-librerp VENV_123-librerp6 VENV_123-librerp; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1e> FULLVER $v" "6.1" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1e> GIT_ORGID $v" "librerp" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1e> GIT_ORGNM $v" "iw3hxn" "$RES"
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
            [[ $x == "librerp" && ! $v =~ (12|6) ]] && continue
            [[ $x == "powerp" && $v != "12" ]] && continue
            [[ $x == "devel" ]] && continue
            w="$x$v"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $w)
            test_result "2a> FULLVER $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [[ $x == "VENV_123-" ]] && continue

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$w"
                pushd $Z0BUG_root/$w>/dev/null || return 1
                RES=$(build_odoo_param FULLVER ".")
                popd >/dev/null || return 1
            fi
            test_result "$PWD> FULLVER '.' [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $Z0BUG_root/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param FULLVER ".")
                fi
                test_result "$PWD> FULLVER '.' [bash]" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$HOME/$w"
                pushd $HOME/$w>/dev/null || return 1
                RES=$(build_odoo_param FULLVER ".")
                popd >/dev/null || return 1
            fi
            test_result "$PWD> FULLVER '.' [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $HOME/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param FULLVER ".")
                fi
                test_result "$PWD> FULLVER '.' [bash]" "$TRES" "$RES"
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
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "2b> MAJVER $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp|powerp) ]]; then
                w="$x$m"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
                test_result "2b> MAJVER $w [bash]" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            [[ $x == "VENV_123-" ]] && continue

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$w"
                pushd $Z0BUG_root/$w>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                popd >/dev/null || return 1
            fi
            test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero"; do
                    if [ ${opt_dry_run:-0} -eq 0 ]; then
                        Z0BUG_build_odoo_env "$x${m}${o}"
                        pushd $Z0BUG_root/$w>/dev/null || return 1
                        RES=$(build_odoo_param MAJVER ".")
                        popd >/dev/null || return 1
                    fi
                    test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
            if [[ -d $Z0BUG_root/$w/odoo/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/odoo/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            elif [[ -d $Z0BUG_root/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
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
            test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $HOME/$w/odoo/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/odoo/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            elif [[ -d $HOME/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            fi

            [[ $x != "odoo" ]] && continue
            for o in "-oca" "-powerp" "-zero"; do
                Z0BUG_build_odoo_env "$HOME/$x${m}${o}"
                [ ${opt_dry_run:-0} -eq 0 ] && pushd $HOME/$x${m}${o}>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                test_result "$PWD> MAJVER '.' [bash]" "$TRES" "$RES"
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
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            TRES="/etc/odoo/odoo.conf"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/etc/odoo/odoo-server.conf"
            [[ "$v" == "6.1" ]] && TRES="/etc/odoo/openerp-server.conf"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/etc/odoo/openerp-server.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "3a> unique CONFN $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES="/var/log/odoo/odoo.log"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/var/log/odoo/odoo-server.log"
            [[ "$v" == "6.1" ]] && TRES="/var/log/odoo/openerp-server.log"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/var/log/odoo/openerp-server.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "3b> unique FLOG $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES="/var/run/odoo/odoo.pid"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/var/run/odoo/odoo-server.pid"
            [[ "$v" == "6.1" ]] && TRES="/var/run/odoo/openerp-server.pid"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/var/run/odoo/openerp-server.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "3c> unique FPID $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES="/etc/init.d/odoo"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES="/etc/init.d/odoo-server"
            [[ "$v" == "6.1" ]] && TRES="/etc/init.d/openerp-server"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES="/etc/init.d/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "3d> unique FULL_SVCNAME $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "3e> unique SVCNAME $w [bash]" "$(basename $TRES)" "$RES"
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
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x =~ (oca|librerp|powerp|devel) ]] && o="-${x}"
            TRES="/etc/odoo/odoo${m}${o}.conf"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/etc/odoo/odoo${m}-server.conf"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/etc/odoo/openerp-server.conf"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/etc/odoo/odoo-server.conf"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES="/etc/odoo/odoo.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "4a> multi CONFN $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/etc/odoo/odoo${m}${o}.conf"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
                    test_result "4a> multi CONFN $w [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES="/var/log/odoo/odoo${m}${o}.log"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/var/log/odoo/odoo${m}-server.log"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/var/log/odoo/openerp-server.log"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/var/log/odoo/odoo-server.log"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES="/var/log/odoo/odoo.log"
            [[ $x =~ (oca|librerp|powerp) ]] && TRES="/var/log/odoo/odoo${m}-$x.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "4b> multi FLOG $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/var/log/odoo/odoo${m}${o}.log"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
                    test_result "4b> multi FLOG $w [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES="/var/run/odoo/odoo${m}${o}.pid"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/var/run/odoo/odoo${m}-server.pid"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/var/run/odoo/openerp-server.pid"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/var/run/odoo/odoo-server.pid"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES="/var/run/odoo/odoo.pid"
            [[ $x =~ (oca|librerp|powerp) ]] && TRES="/var/run/odoo/odoo${m}-$x.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "4c> multi FPID $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/var/run/odoo/odoo${m}${o}.pid"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
                    test_result "4c> multi FPID $w [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES="/etc/init.d/odoo${m}${o}"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES="/etc/init.d/odoo${m}-server"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES="/etc/init.d/openerp-server"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES="/etc/init.d/odoo-server"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES="/etc/init.d/odoo"
            [[ $x =~ (oca|librerp|powerp) ]] && TRES="/etc/init.d/odoo${m}-$x"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "4d> multi FULL_SVCNAME $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "4d> multi SVCNAME $w [bash]" "$(basename $TRES)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    TRES="/etc/init.d/odoo${m}${o}"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
                    test_result "4d> multi FULL_SVCNAME $w [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
                    test_result "4d> multi SVCNAME $w [bash]" "$(basename $TRES)" "$RES"
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
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"

            export opt_multi=0
            TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$HOME/$w/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES="$HOME/$w/server/openerp-server"
            [[ $v == "6.1" ]] && TRES="$HOME/$w/server/openerp-server"
            b=$(basename $TRES)
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/$b"
            [[ $x =~ ^VENV && $v == "6.1" ]] && TRES="$HOME/$w/odoo/server/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "5a> unique BIN $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            b=$(dirname $TRES)
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "5b> unique ROOT $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w)
            test_result "5b> unique PKGPATH $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w)
            test_result "5b> unique HOME $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PARENTDIR $w)
            test_result "5b> unique PARENTDIR $w [bash]" "$(dirname $b)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "5b> unique ROOT $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w "crm")
            test_result "5b> unique PKGPATH $w/crm [bash]" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "5b> unique PARENTDIR $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w "crm")
            test_result "5b> unique HOME $w/crm [bash]" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp|powerp) ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "5c> unique ROOT $v OCB $x [bash]" "$HOME/$v" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi

            export opt_multi=1
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/odoo-bin" || TRES="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES="$(dirname $TRES)/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES="$(dirname $TRES)/server/openerp-server"
            if [[ $v == "6.1" ]]; then
                [[ $x =~ ^VENV ]] && TRES="$HOME/$w/odoo/server/openerp-server" || TRES="$HOME/$w/server/openerp-server"
            fi
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "5d> multi BIN $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ ! $x =~ (VENV_123-|v|V) && ! $v =~ (6\.1) ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w search)
                test_result "5d> multi BIN $w search [bash]" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            b=$(dirname $TRES)
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "5d> multi ROOT $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w)
            test_result "5d> multi PKGPATH $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w)
            test_result "5d> multi HOME $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PARENTDIR $w)
            test_result "5d> multi PARENTDIR $w [bash]" "$(dirname $b)" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "5d> multi ROOT $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PKGPATH $w "crm")
            test_result "5d> multi PKGPATH $w/crm [bash]" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param HOME $w "crm")
            test_result "5d> multi HOME $w/crm [bash]" "$b/crm" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param PARENTDIR $w "crm")
            test_result "5d> multi PARENTDIR $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp|powerp) ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "5e> multi ROOT $v OCB $x [bash]" "$b" "$RES"
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
                test_result "$PWD> ROOT '.' [bash]" "$Z0BUG_root/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param REPOS ".")
                [[ $w == "librerp6" ]] && test_result "$PWD> REPOS '.' [bash]" "server" "$RES" || test_result "$PWD> REPOS '.' [bash]" "OCB" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param DIRLEVEL ".")
                test_result "$PWD> DIRLEVEL '.' [bash]" "OCB" "$RES"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param DIRLEVEL "$Z0BUG_root/$w/crm")
                test_result "5f> DIRLEVEL '$Z0BUG_root/$w/crm' [bash]" "repository" "$RES"

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
                [[ $w == "powerp12" ]] && r="OPL"
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
            [[ $x =~ (librerp|powerp) ]] && ((TRES=m+8360))
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "5h> multi RPCPORT $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            ((TRES=m+8130))
            [[ $w =~ ^(v|V)[0-9] ]] && TRES=8072
            [[ $x =~ (odoo|odoo_|ODOO) ]] && ((TRES=m+8130))
            [[ $x =~ (OCB-|oca) ]] && ((TRES=m+8230))
            [[ $x =~ (librerp|powerp) ]] && ((TRES=m+8330))
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param LPPORT $w)
            test_result "5h> multi LPPORT $w [bash]" "$TRES" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero" "-devel"; do
                    w="$x${m}${o}"
                    ((TRES=m+8160))
                    [[ $o == "-oca" ]] && ((TRES=m+8260))
                    [[ $o == "-powerp" ]] && ((TRES=m+8360))
                    [[ $o == "-zero" ]] && ((TRES=m+8460))
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                    test_result "5h> multi RPCPORT $w [bash]" "$TRES" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
        done

        export opt_multi=0
        [[ $v =~ (9.0|8.0|7.0|6.1) ]] && TRES="__openerp__.py"
        [[ $v =~ (14.0|13.0|12.0|11.0|10.0) ]] && TRES="__manifest__.py"
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
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"

            opt_multi=0
            [ $m -le 7 ] && TRES="$HOME/$w/openerp/filestore" || TRES="$HOME/.local/share/Odoo"
            if [[ $x =~ ^VENV ]]; then
                [ $m -le 7 ] && TRES="$HOME/$w/odoo/openerp/filestore" || TRES="$HOME/VENV-$v/.local/share/Odoo"
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

    opt_multi=1
    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp|powerp) ]] && w="$x$m"
            for z in "OCB" "l10n-italy"; do
                # [[ $HOSTNAME =~ (shs[a-z0-9]{4,6}|zeroincombenze) ]] && TRES="git@github.com:zeroincombenze/${z}.git" || TRES="https://github.com/zeroincombenze/${z}.git"
                TRES="git@github.com:zeroincombenze/${z}.git"
                [[ $x =~ ^(odoo|ODOO) ]] && TRES="https://github.com/odoo/odoo.git"
                [[ $x =~ ^(odoo|ODOO) && ! $z == "OCB" ]] && continue
                [[ $x == "librerp" && $v == "6.1" && $z == "l10n-italy" ]] && continue
                [[ $x =~ ^(oca|OCB) ]] && TRES="https://github.com/OCA/${z}.git"
                [[ $x == "librerp" && $v == "12.0" ]] && TRES="https://github.com/librerp/${z}.git"
                [[ $x == "librerp" && $v == "6.1" ]] && TRES="https://github.com/iw3hxn/server.git"
                [[ $x == "powerp" ]] && TRES="https://github.com/PowERP-cloud/${z}.git"
                [[ ${opt_dry_run:-0} -eq 0 ]] && RES=$(build_odoo_param GIT_URL $w $z)
                test_result "7a> multi GIT_URL $w/$z [bash]" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RORIGIN $w $z)
                test_result "7b> multi RORIGIN $w/$z [bash]" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s

                [[ $v == "6.1" && $x =~ (odoo|odoo_|ODOO|oca|OCB) ]] && continue
                [[ $x =~ (odoo|odoo_|ODOO) && ! $z == "OCB" ]] && continue
                [[ $x =~ (odoo|odoo_|ODOO) ]] && TRES="https://github.com/odoo/odoo.git" || TRES="https://github.com/OCA/${z}.git"
                [[ $v == "6.1" ]] && TRES="git@github.com:zeroincombenze/${z}.git"
                [[ $x == "librerp" && $v == "6.1" ]] && TRES="https://github.com/iw3hxn/server.git"
                [[ $x == "powerp" ]] && TRES="https://github.com/OCA/${z}.git"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RUPSTREAM $w $z)
                test_result "7c> multi RUPSTREAM $w/$z [bash]" "$TRES" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            done
            if [[ ! $x == "VENV_123-" ]]; then
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
    return $sts
}

test_08() {
    local s sts v w
    sts=0
    export opt_multi=1
    local TRES="OCB account-closing account-financial-reporting account-financial-tools account-invoicing account-payment account_banking_cscs bank-payment commission connector contract crm cscs_addons knowledge l10n-italy l10n-italy-supplemental management-system partner-contact product-attribute profiles project purchase-workflow report-print-send reporting-engine sale-workflow server-tools stock-logistics-barcode stock-logistics-tracking zeroincombenze"
    local RES=$(module_list "7.0")
    test_result "Module list 7.0" "$TRES" "$RES"

    TRES="OCB account-closing account-financial-reporting account-financial-tools account-invoicing account-payment bank-payment commission connector contract crm knowledge l10n-italy l10n-italy-supplemental management-system partner-contact product-attribute project purchase-workflow report-print-send reporting-engine sale-workflow server-tools stock-logistics-barcode stock-logistics-tracking zeroincombenze"
    local RES=$(module_list "8.0")
    test_result "Module list 8.0" "$TRES" "$RES"
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
    export ODOO_GIT_SHORT="(oca|librerp|powerp)"
    export ODOO_DB_USER=""

    for v in $VERSIONS_TO_TEST $MAJVERS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12|6) ]] && continue
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (odoo|odoo_|ODOO|oca|librerp|powerp) ]] && w="$x$m"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (oca|librerp|powerp) ]] && w="odoo${m}-$x"
            OS_TREE="$OS_TREE $w $HOME/$w"
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-powerp" "-zero" "-devel"; do
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
            [[ $x == "powerp" && $v != "12.0" ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (odoo|odoo_|ODOO|oca|librerp|powerp) ]] && w="$x$m"
            OS_TREE="$OS_TREE $w $HOME/$w"
            [[ $x =~ (oca|librerp|powerp) ]] && w="odoo${m}-$x"
            OS_TREE="$OS_TREE $w $HOME/$w"
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-powerp" "-zero" "-devel"; do
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
