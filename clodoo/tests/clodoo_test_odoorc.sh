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

__version__=0.3.9.24
VERSIONS_TO_TEST="14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1"
MAJVERS_TO_TEST="14 13 12 11 10 9 8 7 6"
SUB_TO_TEST="v V VENV- odoo odoo_ ODOO OCB- oca librerp VENV_123- devel"


test_01() {
    local RES s sts v w x
    local sts=0
    export opt_multi=0
    declare -A TRES
    discover_multi
    test_result "Discover_multi (0)" "0" "$opt_multi"
    for v in 12 12.0 v12 V12 v12.0 V12.0 VENV-12.0 VENV_123-12.0; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1a> full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in odoo12 odoo_12 VENV_123-odoo12 odoo-12-devel odoo12-main; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1b> full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1b> git org id $v" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1b> git org name $v" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in OCB-12 OCB-12.0 oca12 odoo12-oca VENV-odoo12-oca VENV_123-odoo12-oca; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1c> full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1c> git org id $v" "oca" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1c> git org name $v" "OCA" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in axitec12 odoo12-axitec odoo12-axi odoo_12-axi VENV-odoo12-axi VENV_123-odoo12-axi; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1d> full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1d> git org id $v" "axi" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1d> git org name $v" "axitec" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in librerp6 librerp odoo6-librerp VENV-librerp6 VENV-librerp VENV_123-librerp6 VENV_123-librerp; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "1e> full version $v" "6.1" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "1e> git org id $v" "librerp" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "1e> git org name $v" "iw3hxn" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}


test_02() {
    local s sts m v w x
    sts=0
    export opt_multi=0
    declare -A TRES

    for v in $MAJVERS_TO_TEST; do
        [[ "$v" == "6" ]] && TRES[$v]="$v.1" || TRES[$v]="$v.0"
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12|6) ]] && continue
            [[ $x == "devel" ]] && continue
            w="$x$v"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $w)
            test_result "2a> FULLVER $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [[ $x == "VENV_123-" ]] && continue

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$w"
                pushd $Z0BUG_root/$w>/dev/null || return 1
                RES=$(build_odoo_param FULLVER ".")
                popd >/dev/null || return 1
            fi
            test_result "$PWD> FULLVER '.' [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $Z0BUG_root/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param FULLVER ".")
                fi
                test_result "$PWD> full version '.' [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$HOME/$w"
                pushd $HOME/$w>/dev/null || return 1
                RES=$(build_odoo_param FULLVER ".")
                popd >/dev/null || return 1
            fi
            test_result "$PWD> full version '.' [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $HOME/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param FULLVER ".")
                fi
                test_result "$PWD> full version '.' [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi
        done
    done

    unset TRES
    declare -A TRES
    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        TRES[$v]=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "2b> major version $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x =~ (oca|librerp) ]]; then
                w="$x$m"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
                test_result "2b> major version $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            [[ $x == "VENV_123-" ]] && continue

            if [ ${opt_dry_run:-0} -eq 0 ]; then
                Z0BUG_build_odoo_env "$w"
                pushd $Z0BUG_root/$w>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                popd >/dev/null || return 1
            fi
            test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-axi" "-zero"; do
                    if [ ${opt_dry_run:-0} -eq 0 ]; then
                        Z0BUG_build_odoo_env "$x${m}${o}"
                        pushd $Z0BUG_root/$w>/dev/null || return 1
                        RES=$(build_odoo_param MAJVER ".")
                        popd >/dev/null || return 1
                    fi
                    test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
            if [[ -d $Z0BUG_root/$w/odoo/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/odoo/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            elif [[ -d $Z0BUG_root/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
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
            test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ -d $HOME/$w/odoo/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/odoo/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            elif [[ -d $HOME/$w/addons ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/addons>/dev/null || return 1
                    RES=$(build_odoo_param MAJVER ".")
                    test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    popd >/dev/null || return 1
                fi
            fi

            [[ $x != "odoo" ]] && continue
            for o in "-oca" "-axi" "-zero"; do
                Z0BUG_build_odoo_env "$HOME/$x${m}${o}"
                [ ${opt_dry_run:-0} -eq 0 ] && pushd $HOME/$x${m}${o}>/dev/null || return 1
                RES=$(build_odoo_param MAJVER ".")
                test_result "$PWD> major version '.' [bash]" "${TRES[$v]}" "$RES"
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
    declare -A TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            TRES[$v]="/etc/odoo/odoo.conf"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/etc/odoo/odoo-server.conf"
            [[ "$v" == "6.1" ]] && TRES[$v]="/etc/odoo/openerp-server.conf"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/etc/odoo/openerp-server.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "3a> unique config filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES[$v]="/var/log/odoo/odoo.log"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/var/log/odoo/odoo-server.log"
            [[ "$v" == "6.1" ]] && TRES[$v]="/var/log/odoo/openerp-server.log"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/var/log/odoo/openerp-server.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "3b> unique log filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES[$v]="/var/run/odoo/odoo.pid"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/var/run/odoo/odoo-server.pid"
            [[ "$v" == "6.1" ]] && TRES[$v]="/var/run/odoo/openerp-server.pid"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/var/run/odoo/openerp-server.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "3c> unique pid filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES[$v]="/etc/init.d/odoo"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/etc/init.d/odoo-server"
            [[ "$v" == "6.1" ]] && TRES[$v]="/etc/init.d/openerp-server"
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/etc/init.d/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "3d> unique full service name $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "3e> unique service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done
    return $sts
}

test_04() {
    local m o s sts v w x
    sts=0
    declare -A TRES
    export opt_multi=1

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES[$v]="/etc/odoo/odoo${m}${o}.conf"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/etc/odoo/odoo${m}-server.conf"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/etc/odoo/openerp-server.conf"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/etc/odoo/odoo-server.conf"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/etc/odoo/odoo.conf"
            [[ $x =~ (oca|librerp) ]] && TRES[$v]="/etc/odoo/odoo${m}-$x.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "4a> multi config filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-axi" "-zero"; do
                    w="$x${m}${o}"
                    TRES[$v]="/etc/odoo/odoo${m}${o}.conf"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
                    test_result "4a> multi config filename $w [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES[$v]="/var/log/odoo/odoo${m}${o}.log"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/var/log/odoo/odoo${m}-server.log"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/var/log/odoo/openerp-server.log"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/var/log/odoo/odoo-server.log"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/var/log/odoo/odoo.log"
            [[ $x =~ (oca|librerp) ]] && TRES[$v]="/var/log/odoo/odoo${m}-$x.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "4b> multi log filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-axi" "-zero"; do
                    w="$x${m}${o}"
                    TRES[$v]="/var/log/odoo/odoo${m}${o}.log"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
                    test_result "4b> multi log filename $w [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES[$v]="/var/run/odoo/odoo${m}${o}.pid"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/var/run/odoo/odoo${m}-server.pid"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/var/run/odoo/openerp-server.pid"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/var/run/odoo/odoo-server.pid"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/var/run/odoo/odoo.pid"
            [[ $x =~ (oca|librerp) ]] && TRES[$v]="/var/run/odoo/odoo${m}-$x.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "4c> multi pid filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-axi" "-zero"; do
                    w="$x${m}${o}"
                    TRES[$v]="/var/run/odoo/odoo${m}${o}.pid"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
                    test_result "4c> multi pid filename $w [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi

            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            o=""
            [[ $x == "OCB-" ]] && o="-oca"
            [[ $x == "devel" ]] && o="-${x}"
            TRES[$v]="/etc/init.d/odoo${m}${o}"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/etc/init.d/odoo${m}-server"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/etc/init.d/openerp-server"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/etc/init.d/odoo-server"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/etc/init.d/odoo"
            [[ $x =~ (oca|librerp) ]] && TRES[$v]="/etc/init.d/odoo${m}-$x"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "4d> multi full service name $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "4d> multi service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                for o in "-oca" "-axi" "-zero"; do
                    w="$x${m}${o}"
                    TRES[$v]="/etc/init.d/odoo${m}${o}"
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
                    test_result "4d> multi full service name $w [bash]" "${TRES[$v]}" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                    [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
                    test_result "4d> multi service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
                    s=$?; [ ${s-0} -ne 0 ] && sts=$s
                done
            fi
        done
    done
    return $sts
}


test_05() {
    local b m o s sts v w x
    sts=0
    declare -A TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" $SUB_TO_TEST; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"

            export opt_multi=0
            TRES[$v]="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES[$v]="$HOME/$w/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="$HOME/$w/server/openerp-server"
            [[ $v == "6.1" ]] && TRES[$v]="$HOME/$w/server/openerp-server"
            b=$(basename ${TRES[$v]})
            [[ $x =~ ^VENV ]] && TRES[$v]="$HOME/$w/odoo/$b"
            [[ $x =~ ^VENV && $v == "6.1" ]] && TRES[$v]="$HOME/$w/odoo/server/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "5a> unique BIN $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            b=$(dirname ${TRES[$v]})
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "5b> unique ROOT $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "5b> unique ROOT $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x == "oca" ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "5c> unique ROOT $v OCB $x [bash]" "$HOME/$v" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            elif [[ $x == "librerp" ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "5c> unique ROOT $v OCB $x [bash]" "$HOME/$v" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi

            export opt_multi=1
            [[ $x == "devel" ]] && w="${v}-$x" || w="$x$v"
            [[ $x =~ (oca|librerp) ]] && w="$x$m"
            [[ $x =~ ^VENV ]] && TRES[$v]="$HOME/$w/odoo/odoo-bin" || TRES[$v]="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES[$v]="$(dirname ${TRES[$v]})/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="$(dirname ${TRES[$v]})/server/openerp-server"
            if [[ $v == "6.1" ]]; then
                [[ $x =~ ^VENV ]] && TRES[$v]="$HOME/$w/odoo/server/openerp-server" || TRES[$v]="$HOME/$w/server/openerp-server"
            fi
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "5d> multi BIN $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ ! $x =~ (VENV_123-|v|V) && ! $v =~ (6\.1) ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w search)
                test_result "5d> multi BIN $w search [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
            b=$(dirname ${TRES[$v]})
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "5d> multi ROOT $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "5d> multi root $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            if [[ $x == "oca" ]]; then
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $v "OCB" $x)
                test_result "5e> multi ROOT $v OCB $x [bash]" "$b" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            elif [[ $x == "librerp" ]]; then
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
                    Z0BUG_build_module_path "$Z0BUG_root/$w/addons/crm" "$v"
                    pushd $Z0BUG_root/$w>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> ROOT '.' [bash]" "$Z0BUG_root/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param REPOS ".")
                # TODO> Test fails
                [[ $w == "librerp6" ]] && test_result "$PWD> REPOS '.' [bash]" "server" "$RES" || test_result "$PWD> REPOS '.' [bash]" "OCB" "$RES"
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )

                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $Z0BUG_root/$w/crm>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> root '.' [bash]" "$Z0BUG_root/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param REPOS ".")
                # TODO> Test fails
                test_result "$PWD> repository '.' [bash]" "crm" "$RES"
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi

            if [[ ! $x == "VENV_123-" ]]; then
                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    Z0BUG_build_odoo_env "$HOME/$w"
                    Z0BUG_build_os_tree "$HOME/$w/crm"
                    touch $HOME/$w/.travis.yml
                    touch $HOME/$w/crm/.travis.yml
                    pushd $HOME/$w>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> root '.' [bash]" "$HOME/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )

                if [ ${opt_dry_run:-0} -eq 0 ]; then
                    pushd $HOME/$w/crm>/dev/null || return 1
                    RES=$(build_odoo_param ROOT ".")
                fi
                test_result "$PWD> root '.' [bash]" "$HOME/$w" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && ( popd >/dev/null || return 1 )
            fi

            export opt_multi=0
            TRES[$v]=8069
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "5h> unique rpcport $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_multi=1
            ((TRES[$v]=m+8160))
            [[ $w =~ ^(v|V)[0-9] ]] && TRES[$v]=8069
            [[ $x =~ (odoo|odoo_|ODOO) ]] && ((TRES[$v]=m+8160))
            [[ $x =~ (OCB-|oca) ]] && ((TRES[$v]=m+8260))
            [[ $x =~ (librerp) ]] && ((TRES[$v]=m+8360))
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "5h> multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                o="-oca"
                w="$x${m}${o}"
                ((TRES[$v]=m+8260))
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                test_result "5h> multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-axi"
                w="$x${m}${o}"
                ((TRES[$v]=m+8360))
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                test_result "5h> multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-zero"
                w="$x${m}${o}"
                ((TRES[$v]=m+8460))
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                test_result "5h> multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
        done

        export opt_multi=0
        [[ $v =~ (9.0|8.0|7.0|6.1) ]] && TRES[$v]="__openerp__.py"
        [[ $v =~ (14.0|13.0|12.0|11.0|10.0) ]] && TRES[$v]="__manifest__.py"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MANIFEST $v)
        test_result "5i> manifest $v [bash]" "${TRES[$v]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s

        TRES[$v]="odoo"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param USER $v)
        test_result "5i> unique db username $v [bash]" "${TRES[$v]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s

        export opt_multi=1
        TRES[$v]="odoo${m}"
        [[ $w =~ ^(v|V)[0-9] ]] && TRES[$v]="odoo"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param USER $v)
        test_result "5i> multi db username $v [bash]" "${TRES[$v]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

__test_06() {
    local s sts v w
    sts=0
    export opt_multi=1
    declare -A TRES

    TRES[6.1]="$LCL_ROOT/6.1/openerp/filestore"
    TRES[v7]="$LCL_ROOT/v7/openerp/filestore"
    TRES[7.0]="$LCL_ROOT/7.0/openerp/filestore"
    TRES[v8.0]="$LCL_ROOT/.local/share/Odoo"
    TRES[8.0]="$LCL_ROOT/.local/share/Odoo8"
    TRES[9.0]="$LCL_ROOT/.local/share/Odoo9"
    TRES[10.0]="$LCL_ROOT/.local/share/Odoo10"
    TRES[VENV-10]="$LCL_ROOT/VENV-10/.local/share/Odoo"
    TRES[11.0]="$LCL_ROOT/.local/share/Odoo11"
    TRES[12.0]="$LCL_ROOT/.local/share/Odoo12"
    for v in $VERSIONS_TO_TEST VENV-10 v8.0 v7; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param DDIR $v)
      fi
      test_result "Filestore $v" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done

    TRES[6.1]="$LCL_ROOT/6.1/crm"
    TRES[v7]="$LCL_ROOT/v7/crm"
    TRES[7.0]="$LCL_ROOT/7.0/crm"
    TRES[v8.0]="$LCL_ROOT/v8.0/crm"
    TRES[8.0]="$LCL_ROOT/8.0/crm"
    TRES[9.0]="$LCL_ROOT/9.0/crm"
    TRES[10.0]="$LCL_ROOT/10.0/crm"
    TRES[11.0]="$LCL_ROOT/11.0/crm"
    TRES[12.0]="$LCL_ROOT/12.0/crm"
    for v in $VERSIONS_TO_TEST v8.0 v7; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param HOME $v "crm")
      fi
      test_result "Home $v/crm" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s

      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param PARENTDIR $v "crm")
      fi
      test_result "Parent dir $v/crm" "$LCL_ROOT/$v" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done

    TRES[6.1]="$LCL_ROOT/VENV-6.1/odoo/crm"
    TRES[7.0]="$LCL_ROOT/VENV-7.0/odoo/crm"
    TRES[8.0]="$LCL_ROOT/VENV-8.0/odoo/crm"
    TRES[9.0]="$LCL_ROOT/VENV-9.0/odoo/crm"
    TRES[10.0]="$LCL_ROOT/VENV-10.0/odoo/crm"
    TRES[11.0]="$LCL_ROOT/VENV-11.0/odoo/crm"
    TRES[12.0]="$LCL_ROOT/VENV-12.0/odoo/crm"
    for v in $VERSIONS_TO_TEST; do
      if [ ${opt_dry_run:-0} -eq 0 ]; then
        RES=$(build_odoo_param HOME VENV-$v "crm")
      fi
      test_result "Home VENV-$v/crm" "${TRES[$v]}" "$RES"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
    }

__test_07() {
    local s sts v w
    sts=0
    export opt_multi=0
    declare -A TRES
    for z in "OCB" "l10n-italy"; do
      TRES[zero-git]="git@github.com:zeroincombenze/$z"
      TRES[zero-http]="https://github.com/zeroincombenze/$z"
      TRES[oca]="https://github.com/OCA/$z"
      TRES[librerp]="https://github.com/iw3hxn/server"
      if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
        TRES[zero]=${TRES[zero-git]}
      else
        TRES[zero]=${TRES[zero-http]}
      fi
      for w in zero zero-git zero-http oca librerp; do
        [ "$z" == "l10n-italy" -a "$w" == "librerp" ] && continue
        for v in $VERSIONS_TO_TEST; do
          if [ ${opt_dry_run:-0} -eq 0 ]; then
            RES=$(build_odoo_param URL $v $z $w)
          fi
          test_result "URL $w/$z $v" "${TRES[$w]}" "$RES"
          s=$?; [ ${s-0} -ne 0 ] && sts=$s
          #
          if [ ${opt_dry_run:-0} -eq 0 ]; then
            RES=$(build_odoo_param GIT_URL $v $z $w)
          fi
          test_result "GIT_URL $w/$z $v" "${TRES[$w]}.git" "$RES"
          s=$?; [ ${s-0} -ne 0 ] && sts=$s
          #
          if [ ${opt_dry_run:-0} -eq 0 ]; then
            RES=$(build_odoo_param URL_BRANCH $v $z $w)
          fi
          test_result "URL_BRANCH $w/$z $v" "${TRES[$w]}/tree/$v" "$RES"
          s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
      done
    done
    #
    for z in "OCB" "l10n-italy"; do
      TRES[zero-git]="git@github.com:zeroincombenze"
      TRES[zero-http]="https://github.com/zeroincombenze"
      TRES[oca]="https://github.com/OCA"
      TRES[librerp]="https://github.com/iw3hxn"
      if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
        TRES[zero]=${TRES[zero-git]}
      else
        TRES[zero]=${TRES[zero-http]}
      fi
      for w in zero zero-git zero-http oca librerp; do
        [ "$z" == "l10n-italy" -a "$w" == "librerp" ] && continue
        for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
          if [ ${opt_dry_run:-0} -eq 0 ]; then
            RES=$(build_odoo_param GIT_ORG $v $z $w)
          fi
          test_result "GIT_ORG $w/$z $v" "${TRES[$w]}" "$RES"
          s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
      done
    done
    #
    for z in "OCB" "l10n-italy"; do
      TRES[zero]="https://github.com/OCA/$z"
      TRES[zero-git]="https://github.com/OCA/$z"
      TRES[zero-http]="https://github.com/OCA/$z"
      TRES[oca]="https://github.com/OCA/$z"
      TRES[librerp]="https://github.com/iw3hxn/$z"
      for w in zero zero-git zero-http oca librerp; do
        [ "$z" == "l10n-italy" -a "$w" == "librerp" ] && continue
        for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0; do
          if [ ${opt_dry_run:-0} -eq 0 ]; then
            RES=$(build_odoo_param UPSTREAM $v $z $w)
          fi
          if [ "$v" == "6.1" -o "$w" == "oca" -o "$w" == "librerp" ]; then
            test_result "UPSTREAM $w/$z $v" "" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
          else
            test_result "UPSTREAM $w/$z $v" "${TRES[$w]}.git" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
          fi
        done
      done
    done
    #
    for v in 12.0 11.0 10.0 8.0 7.0; do
      w=$(echo $v|grep -Eo "[0-9]+"|head -n1)
      # TO FIX HOME
      # TRES[zero]="$HOME/zero$w"
      # TRES[zero-git]="$HOME/zero$w"
      # TRES[zero-http]="$HOME/zero$w"
      # TRES[oca]="$HOME/oca$w"
      # TRES[oia]="$HOME/oia$w"
      # TRES[oia-git]="$HOME/oia$w"
      # TRES[oia-http]="$HOME/oia$w"
      TRES[zero]="$LCL_ROOT/zero$w"
      TRES[zero-git]="$LCL_ROOT/zero$w"
      TRES[zero-http]="$LCL_ROOT/zero$w"
      TRES[oca]="$LCL_ROOT/oca$w"
      TRES[oia]="$LCL_ROOT/oia$w"
      TRES[oia-git]="$LCL_ROOT/oia$w"
      TRES[oia-http]="$LCL_ROOT/oia$w"
      for w in zero zero-git zero-http oca oia oia-git oia-http; do
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          RES=$(build_odoo_param HOME $v '' $w)
        fi
        test_result "HOME $v $w" "${TRES[$w]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
      done
    done

    return $sts
    }

__test_08() {
    local s sts v w x
    sts=0
    export opt_multi=1
    declare -A TRES
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 librerp6 oca7 oca8 oca10; do
        pushd $Z0BUG_root/$v >/dev/null
        RES=$(build_odoo_param HOME '.')
        test_result "HOME ./$v" "$PWD" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        #
        w=$(echo $v|grep -Eo "[0-9]+"|head -n1)
        if [ "$w" == "6" ]; then
          w="$w.1"
        else
          w="$w.0"
        fi
        RES=$(build_odoo_param FULLVER '.')
        test_result "Full version ./$v" "$w" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        #
        w=$(echo $v|grep -Eo "[0-9]+"|head -n1)
        if [[ "10.0 11.0 12.0" =~ "$v" ]]; then
          w="/etc/odoo/odoo${w}.conf"
        elif [[ "6.1 7.0 8.0 9.0" =~ "$v" ]]; then
          w="/etc/odoo/odoo${w}-server.conf"
        elif [[ "${v:0:3}" == "oca" ]]; then
          w="/etc/odoo/odoo${w}-oca.conf"
        elif [[ "${v:0:3}" == "oia" ]]; then
          w="/etc/odoo/odoo${w}-oia.conf"
        elif [[ "${v:0:7}" == "librerp" ]]; then
          w="/etc/odoo/odoo${w}-librerp.conf"
        else
          w=
        fi
        RES=$(build_odoo_param CONFN $v)
        test_result "Configuration file ./$v" "$w" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        popd >/dev/null || return 1


        if [ "${v:0:3}" != "oia" ]; then
          x=$(readlink -f $Z0BUG_root/$v)
          RES=$(build_odoo_param HOME $Z0BUG_root/$v)
          test_result "HOME $Z0BUG_root/$v" "$x" "$RES"
          RES=$(build_odoo_param HOME $Z0BUG_root/$v/addons)
          test_result "HOME $Z0BUG_root/$v/addons" "$x" "$RES"
          RES=$(build_odoo_param HOME "$x")
          test_result "HOME $x" "$x" "$RES"
          RES=$(build_odoo_param HOME "$x/addons")
          test_result "HOME $x/addons" "$x" "$RES"
        fi
      done
    fi
    return $sts
}

__test_09() {
    local s sts v w x
    sts=0
    export opt_multi=1
    declare -A TRES
    #
    pushd $LCL_OE_PKGPATH >/dev/null
    RES=$(build_odoo_param PKGPATH '.')
    test_result "Test Odoo PKGPATH" "$LCL_OE_PKGPATH" "$RES"
    RES=$(build_odoo_param ROOT '.')
    test_result "Test Odoo ROOT" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param HOME '.')
    test_result "Test Odoo HOME" "$LCL_OE_PRJPATH" "$RES"
    RES=$(build_odoo_param PARENTDIR '.')
    test_result "Test Odoo PARENTDIR" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "$LCL_OO_REPOS" "$RES"
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      RES=$(build_odoo_param RORIGIN '.' default)
      test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/l10n_italy.git" "$RES"
    fi
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/l10n_italy.git" "$RES"
    popd >/dev/null
    #
    pushd $LCL_OE_PRJPATH >/dev/null
    RES=$(build_odoo_param PKGPATH '.')
    test_result "Test Odoo PKGPATH" "" "$RES"
    RES=$(build_odoo_param ROOT '.')
    test_result "Test Odoo ROOT" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param HOME '.')
    test_result "Test Odoo HOME" "$LCL_OE_PRJPATH" "$RES"
    RES=$(build_odoo_param PARENTDIR '.')
    test_result "Test Odoo PARENTDIR" "$LCL_OE_ROOT" "$RES"
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "$LCL_OO_REPOS" "$RES"
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      RES=$(build_odoo_param RORIGIN '.' default)
      test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/l10n_italy.git" "$RES"
    fi
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/l10n_italy.git" "$RES"
    popd >/dev/null
    #
    pushd $LCL_OE_ROOT >/dev/null
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "OCB" "$RES"
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      RES=$(build_odoo_param RORIGIN '.' default)
      test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/OCB.git" "$RES"
    fi
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/OCB.git" "$RES"
    popd >/dev/null
    #
    pushd $LCL_VE_PKGPATH >/dev/null
    RES=$(build_odoo_param PKGPATH '.')
    test_result "Test Odoo PKGPATH" "$LCL_VE_PKGPATH" "$RES"
    RES=$(build_odoo_param ROOT '.')
    test_result "Test Odoo ROOT" "$LCL_VE_ROOT" "$RES"
    RES=$(build_odoo_param HOME '.')
    test_result "Test Odoo HOME" "$LCL_VE_PRJPATH" "$RES"
    RES=$(build_odoo_param PARENTDIR '.')
    test_result "Test Odoo PARENTDIR" "$LCL_VE_ROOT" "$RES"
    RES=$(build_odoo_param REPOS '.')
    test_result "Test Odoo REPOS" "$LCL_OO_REPOS" "$RES"
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      RES=$(build_odoo_param RORIGIN '.' default)
      test_result "Test Odoo RORIGIN" "git@github.com:zeroincombenze/l10n_italy.git" "$RES"
    fi
    RES=$(build_odoo_param RUPSTREAM '.' default)
    test_result "Test Odoo RUPSTREAM" "https://github.com/OCA/l10n_italy.git" "$RES"
    popd >/dev/null
    #
    return $sts
}

__test_10() {
    local s sts v w
    sts=0
    export opt_multi=1
    local TRES="OCB account-analytic account-budgeting account-closing account-consolidation\
 account-financial-reporting account-financial-tools account-fiscal-rule account-invoice-reporting\
 account-invoicing account-payment account-reconcile account_banking_cscs ansible-odoo apps-store\
 bank-payment bank-statement-import brand business-requirement calendar commission community-data-files\
 connector connector-accountedge connector-cmis connector-ecommerce connector-infor connector-interfaces\
 connector-jira connector-lengow connector-lims connector-magento connector-magento-php-extension\
 connector-odoo2odoo connector-prestashop connector-redmine connector-sage connector-salesforce\
 connector-spscommerce connector-telephony connector-woocommerce contract credit-control crm cscs_addons\
 currency data-protection ddmrp delivery-carrier department donation dotnet e-commerce edi event\
 field-service geospatial helpdesk hr infrastructure-dns interface-github intrastat-extrastat iot knowledge\
 l10n-italy l10n-italy-supplemental maintenance management-system manufacture manufacture-reporting\
 margin-analysis mis-builder mis-builder-contrib multi-company oca-custom oca-decorators odoo-community.org\
 odoo-sentinel operating-unit partner-contact payroll pos product-attribute product-kitting product-pack\
 product-variant profiles program project project-agile project-reporting purchase-reporting purchase-workflow\
 queue report-print-send reporting-engine rest-framework rma sale-financial sale-reporting sale-workflow\
 search-engine server-auth server-backend server-brand server-env server-tools server-ux social\
 stock-logistics-barcode stock-logistics-reporting stock-logistics-tracking stock-logistics-transport\
 stock-logistics-warehouse stock-logistics-workflow storage survey timesheet tools uncovered vertical-abbey\
 vertical-agriculture vertical-association vertical-community vertical-construction vertical-edition\
 vertical-education vertical-hotel vertical-isp vertical-medical vertical-ngo vertical-realestate\
 vertical-travel web webhook webkit-tools website website-cms website-themes wms zerobug-test zeroincombenze"
    local RES=$(module_list "7.0")
    test_result "Module list 7.0" "$TRES" "$RES"

    TRES="OCB account-analytic account-budgeting account-closing account-consolidation\
 account-financial-reporting account-financial-tools account-fiscal-rule account-invoice-reporting\
 account-invoicing account-payment account-reconcile account_banking_cscs ansible-odoo apps-store\
 bank-payment bank-statement-import brand business-requirement calendar commission community-data-files\
 connector connector-accountedge connector-cmis connector-ecommerce connector-infor connector-interfaces\
 connector-jira connector-lengow connector-lims connector-magento connector-magento-php-extension\
 connector-odoo2odoo connector-prestashop connector-redmine connector-sage connector-salesforce\
 connector-spscommerce connector-telephony connector-woocommerce contract credit-control crm cscs_addons\
 currency data-protection ddmrp delivery-carrier department didotech_80 donation dotnet e-commerce edi event\
 field-service geospatial helpdesk hr infrastructure-dns interface-github intrastat-extrastat iot knowledge\
 l10n-italy l10n-italy-supplemental maintenance management-system manufacture manufacture-reporting\
 margin-analysis mis-builder mis-builder-contrib multi-company oca-custom oca-decorators odoo-community.org\
 odoo-sentinel operating-unit partner-contact payroll pos product-attribute product-kitting product-pack\
 product-variant profiles program project project-agile project-reporting purchase-reporting purchase-workflow\
 queue report-print-send reporting-engine rest-framework rma sale-financial sale-reporting sale-workflow\
 search-engine server-auth server-backend server-brand server-env server-tools server-ux social\
 stock-logistics-barcode stock-logistics-reporting stock-logistics-tracking stock-logistics-transport\
 stock-logistics-warehouse stock-logistics-workflow storage survey timesheet tools uncovered vertical-abbey\
 vertical-agriculture vertical-association vertical-community vertical-construction vertical-edition\
 vertical-education vertical-hotel vertical-isp vertical-medical vertical-ngo vertical-realestate\
 vertical-travel web webhook webkit-tools website website-cms website-themes wms zerobug-test zeroincombenze"
    local RES=$(module_list "8.0")
    test_result "Module list 8.0" "$TRES" "$RES"
}


Z0BUG_build_module_path() {
    local path=$1 ver=$2
    mkdir -p $path
    touch $path/__init__.py
    [[ $v =~ (6.1|7.0|8.0|9.0|10.0) ]] && touch $path/__openerp__.py || touch $path/__manifest__.py
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
    export ODOO_GIT_PROT=git
    export ODOO_GIT_ORGM="(oca|librerp)"
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
                for o in "-oca" "-axi" "-zero"; do
                    OS_TREE="$OS_TREE $x${m}${o} $HOME/$x${m}${o}"
                done
            fi
            # Z0BUG_build_odoo_env "$w"
            # for f in l10n-italy l10n-italy/l10n_it_base web; do
            #     OS_TREE="$OS_TREE $Z0BUG_root/$w/$f"
            #     if [ $m -ge 10 ]; then
            #         OS_TREE="$OS_TREE $Z0BUG_root/$w/odoo"
            #         OS_TREE="$OS_TREE $Z0BUG_root/$w/odoo/addons"
            #         OS_TREE="$OS_TREE $Z0BUG_root/$w/odoo/addons/base"
            #     else
            #         OS_TREE="$OS_TREE $Z0BUG_root/$w/openerp"
            #         OS_TREE="$OS_TREE $Z0BUG_root/$w/openerp/addons"
            #         OS_TREE="$OS_TREE $Z0BUG_root/$w/openerp/addons/base"
            #     fi
            # done
            # for f in account sale web; do
            #     OS_TREE="$OS_TREE $Z0BUG_root/$w/addons/$f"
            # done
            # Z0BUG_build_os_tree "$OS_TREE"
            # for f in l10n-italy web; do
            #     touch $Z0BUG_root/$w/$f/.travis.yml
            #     if [ $m -ge 10 ]; then
            #         touch $Z0BUG_root/$w/odoo/addons/base/__init__.py
            #         touch $Z0BUG_root/$w/odoo/addons/base/__manifest__.py
            #     else
            #         touch $Z0BUG_root/$w/openerp/addons/base/__init__.py
            #         touch $Z0BUG_root/$w/openerp/addons/base/__openerp__.py
            #     fi
            # done
            # if [ $m -ge 10 ]; then
            #     touch $Z0BUG_root/$w/odoo/addons/base/__manifest__.py
            #     touch $Z0BUG_root/$w/odoo/addons/base/__init__.py
            # else
            #     touch $Z0BUG_root/$w/openerp/addons/base/__openerp__.py
            #     touch $Z0BUG_root/$w/openerp/addons/base/__init__.py
            # fi
            # for f in l10n-italy/l10n_it_base addons/account addons/sale addons/web; do
            #     [ $m -lt 10 ] && touch $Z0BUG_root/$w/$f/__openerp__.py || touch $Z0BUG_root/$w/$f/__manifest__.py
            #     touch $Z0BUG_root/$w/$f/__init__.py
            # done
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
                for o in "-oca" "-axi" "-zero"; do
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
