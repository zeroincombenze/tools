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

__version__=0.3.9.21
VERSIONS_TO_TEST="14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1"
MAJVERS_TO_TEST="14 13 12 11 10 9 8 7 6"


test_01() {
    local RES s sts v w x
    local sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES
    for v in 12 12.0 v12 V12 v12.0 V12.0 VENV-12.0 VENV_1234-12.0; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in odoo12 odoo_12 VENV_1234-odoo12; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "git org id $v" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "git org name $v" "odoo" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in OCB-12 OCB-12.0 odoo12-oca VENV-odoo12-oca VENV_1234-odoo12-oca; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "git org id $v" "oca" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "git org name $v" "OCA" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in odoo12-axitec odoo12-axi odoo_12-axi VENV-odoo12-axi VENV_1234-odoo12-axi; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "full version $v" "12.0" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "git org id $v" "axi" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "git org name $v" "axitec" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    for v in librerp6 librerp VENV-librerp6 VENV-librerp VENV_1234-librerp6 VENV_1234-librerp; do
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $v)
        test_result "full version $v" "6.1" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGID $v)
        test_result "git org id $v" "librerp" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param GIT_ORGNM $v)
        test_result "git org name $v" "iw3hxn" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}


test_02() {
    local s sts v w x
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES

    for v in $MAJVERS_TO_TEST; do
        [[ "$v" == "6" ]] && TRES[$v]="$v.1" || TRES[$v]="$v.0"
        for x in "" "v" "V" "VENV-" "odoo" "odoo_" "ODOO" "OCB-" "oca" "librerp" "VENV_123-"; do
            [[ $x == "librerp" && ! $v =~ (12|6) ]] && continue
            w="$x$v"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER $w)
            test_result "full version $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && Z0BUG_build_odoo_env "$HOME/$v"
            pushd $HOME/$v>/dev/null
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER ".")
            test_result "$HOME/$v> full version './' [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            popd >/dev/null
            if [[ -d $HOME/$v/addons ]]; then
                pushd $HOME/$v/addons>/dev/null
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER ".")
                test_result "$HOME/$v/addons> full version './' [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                popd >/dev/null
            fi
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULLVER "$HOME/$w")
            test_result "full version $HOME/$w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done

    unset TRES
    declare -A TRES
    for v in $VERSIONS_TO_TEST; do
        TRES[$v]=$(echo $v|awk -F. '{print $1}')
        for x in "" "v" "V" "VENV-" "odoo" "odoo_" "ODOO" "OCB-" "oca" "librerp" "VENV_123-"; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            w="$x$v"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "major version $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            [[ $x != "odoo" ]] && continue
            w="$x${v}-oca"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "major version $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            w="$x${v}-axi"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "major version $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            w="$x${v}-zero"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MAJVER $w)
            test_result "major version $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done
    return $sts
}

test_03() {
    local m o s sts v w x
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES

    for v in $VERSIONS_TO_TEST; do
        for x in "" "v" "V" "VENV-" "odoo" "odoo_" "ODOO" "OCB-" "oca" "librerp" "VENV_123-"; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            TRES[$v]="/etc/odoo/odoo.conf"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/etc/odoo/odoo-server.conf"
            [[ "$v" == "6.1" ]] && TRES[$v]="/etc/odoo/openerp-server.conf"
            w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/etc/odoo/openerp-server.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "unique config filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES[$v]="/var/log/odoo/odoo.log"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/var/log/odoo/odoo-server.log"
            [[ "$v" == "6.1" ]] && TRES[$v]="/var/log/odoo/openerp-server.log"
            w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/var/log/odoo/openerp-server.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "unique log filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES[$v]="/var/run/odoo/odoo.pid"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/var/run/odoo/odoo-server.pid"
            [[ "$v" == "6.1" ]] && TRES[$v]="/var/run/odoo/openerp-server.pid"
            w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/var/run/odoo/openerp-server.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "unique pid filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            TRES[$v]="/etc/init.d/odoo"
            [[ "$v" =~ (9.0|8.0|7.0) ]] && TRES[$v]="/etc/init.d/odoo-server"
            [[ "$v" == "6.1" ]] && TRES[$v]="/etc/init.d/openerp-server"
            w="$x$v"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="/etc/init.d/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "unique full service name $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "unique service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
        done
    done
    return $sts
}

test_04() {
    local m o s sts v w x
    sts=0
    export opt_mult=0
    export opt_multi=0
    declare -A TRES
    export opt_mult=1
    export opt_multi=1

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" "v" "V" "VENV-" "odoo" "odoo_" "ODOO" "OCB-" "oca" "librerp" "VENV_123-"; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            w="$x$v"
            o=""
            [[ $x =~ (OCB-|oca) ]] && o="-oca"
            [[ $x == "librerp" ]] && o="-librerp"
            TRES[$v]="/etc/odoo/odoo${m}${o}.conf"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/etc/odoo/odoo${m}-server.conf"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/etc/odoo/openerp-server.conf"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/etc/odoo/odoo-server.conf"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/etc/odoo/odoo.conf"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
            test_result "multi config filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                o="-oca"
                w="$x${v}${o}"
                TRES[$v]="/etc/odoo/odoo${m}${o}.conf"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
                test_result "multi config filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-axi"
                w="$x${v}${o}"
                TRES[$v]="/etc/odoo/odoo${m}${o}.conf"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
                test_result "multi config filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-zero"
                w="$x${v}${o}"
                TRES[$v]="/etc/odoo/odoo${m}${o}.conf"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param CONFN $w)
                test_result "multi config filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi

            w="$x$v"
            o=""
            [[ $x =~ (OCB-|oca) ]] && o="-oca"
            [[ $x == "librerp" ]] && o="-librerp"
            TRES[$v]="/var/log/odoo/odoo${m}${o}.log"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/var/log/odoo/odoo${m}-server.log"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/var/log/odoo/openerp-server.log"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/var/log/odoo/odoo-server.log"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/var/log/odoo/odoo.log"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
            test_result "multi log filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                o="-oca"
                w="$x${v}${o}"
                TRES[$v]="/var/log/odoo/odoo${m}${o}.log"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
                test_result "multi log filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-axi"
                w="$x${v}${o}"
                TRES[$v]="/var/log/odoo/odoo${m}${o}.log"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
                test_result "multi log filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-zero"
                w="$x${v}${o}"
                TRES[$v]="/var/log/odoo/odoo${m}${o}.log"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FLOG $w)
                test_result "multi log filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi

            w="$x$v"
            o=""
            [[ $x =~ (OCB-|oca) ]] && o="-oca"
            [[ $x == "librerp" ]] && o="-librerp"
            TRES[$v]="/var/run/odoo/odoo${m}${o}.pid"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/var/run/odoo/odoo${m}-server.pid"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/var/run/odoo/openerp-server.pid"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/var/run/odoo/odoo-server.pid"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/var/run/odoo/odoo.pid"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
            test_result "multi pid filename $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                o="-oca"
                w="$x${v}${o}"
                TRES[$v]="/var/run/odoo/odoo${m}${o}.pid"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
                test_result "multi pid filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-axi"
                w="$x${v}${o}"
                TRES[$v]="/var/run/odoo/odoo${m}${o}.pid"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
                test_result "multi pid filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-zero"
                w="$x${v}${o}"
                TRES[$v]="/var/run/odoo/odoo${m}${o}.pid"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FPID $w)
                test_result "multi pid filename $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi


            w="$x$v"
            o=""
            [[ $x =~ (OCB-|oca) ]] && o="-oca"
            [[ $x == "librerp" ]] && o="-librerp"
            TRES[$v]="/etc/init.d/odoo${m}${o}"
            [[ "$v" =~ (9.0|8.0|7.0|6.1) && -z "$o" ]] && TRES[$v]="/etc/init.d/odoo${m}-server"
            [[ "$w" =~ (v|V)(7|6) ]] && TRES[$v]="/etc/init.d/openerp-server"
            [[ "$w" =~ (v|V)(9|8) ]] && TRES[$v]="/etc/init.d/odoo-server"
            [[ "$w" =~ (v|V)(14|13|12|11|10) ]] && TRES[$v]="/etc/init.d/odoo"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
            test_result "multi full service name $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
            test_result "multi service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                o="-oca"
                w="$x${v}${o}"
                TRES[$v]="/etc/init.d/odoo${m}${o}"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
                test_result "multi full service name $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
                test_result "multi service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-axi"
                w="$x${v}${o}"
                TRES[$v]="/etc/init.d/odoo${m}${o}"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
                test_result "multi full service name $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
                test_result "multi service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s                o="-axi"
                o="-zero"
                w="$x${v}${o}"
                TRES[$v]="/etc/init.d/odoo${m}${o}"
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param FULL_SVCNAME $w)
                test_result "multi full service name $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param SVCNAME $w)
                test_result "multi service name $w [bash]" "$(basename ${TRES[$v]})" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s                o="-axi"
            fi
        done
    done
}


test_05() {
    local b m o s sts v w x
    sts=0
    declare -A TRES

    for v in $VERSIONS_TO_TEST; do
        m=$(echo $v|awk -F. '{print $1}')
        for x in "" "v" "V" "VENV-" "odoo" "odoo_" "ODOO" "OCB-" "oca" "librerp" "VENV_123-"; do
            [[ $x == "librerp" && ! $v =~ (12.0|6.1) ]] && continue
            export opt_mult=0
            export opt_multi=0
            w="$x$v"
            TRES[$v]="$HOME/$w/odoo-bin"
            [[ $w =~ (9|8|7) ]] && TRES[$v]="$HOME/$w/openerp-server"
            [[ $w =~ (v|V)(7|6) ]] && TRES[$v]="$HOME/$w/server/openerp-server"
            [[ $v == "6.1" ]] && TRES[$v]="$HOME/$w/server/openerp-server"
            b=$(basename ${TRES[$v]})
            [[ $x =~ ^VENV ]] && TRES[$v]="$HOME/$w/odoo/$b"
            [[ $x =~ ^VENV && $v == "6.1" ]] && TRES[$v]="$HOME/$w/odoo/server/openerp-server"
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "unique script name $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            b=$(dirname ${TRES[$v]})
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w)
            test_result "root dir name $w [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_mult=1
            export opt_multi=1
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param BIN $w)
            test_result "multi script name $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s
            b=$(dirname ${TRES[$v]})
            [[ $b =~ server$ ]] && b=$(dirname $b)
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param ROOT $w "crm")
            test_result "root dir name $w/crm [bash]" "$b" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_mult=0
            export opt_multi=0
            TRES[$v]=8069
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "unique rpcport $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            export opt_mult=1
            export opt_multi=1
            ((TRES[$v]=m+8160))
            [[ $w =~ ^(v|V)[0-9] ]] && TRES[$v]=8069
            [[ $x =~ (odoo|odoo_|ODOO) ]] && ((TRES[$v]=m+8160))
            [[ $x =~ (OCB-|oca) ]] && ((TRES[$v]=m+8260))
            [[ $x =~ (librerp) ]] && ((TRES[$v]=m+8360))
            [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
            test_result "multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
            s=$?; [ ${s-0} -ne 0 ] && sts=$s

            if [[ $x == "odoo" ]]; then
                o="-oca"
                w="$x${v}${o}"
                ((TRES[$v]=m+8260))
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                test_result "multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-axi"
                w="$x${v}${o}"
                ((TRES[$v]=m+8360))
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                test_result "multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
                o="-zero"
                w="$x${v}${o}"
                ((TRES[$v]=m+8460))
                [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param RPCPORT $w)
                test_result "multi rpcport $w [bash]" "${TRES[$v]}" "$RES"
                s=$?; [ ${s-0} -ne 0 ] && sts=$s
            fi
        done

        export opt_mult=0
        export opt_multi=0
        [[ $v =~ (9.0|8.0|7.0|6.1) ]] && TRES[$v]="__openerp__.py"
        [[ $v =~ (14.0|13.0|12.0|11.0|10.0) ]] && TRES[$v]="__manifest__.py"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param MANIFEST $v)
        test_result "manifest $v [bash]" "${TRES[$v]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s

        TRES[$v]="odoo"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param USER $v)
        test_result "unique db username $v [bash]" "${TRES[$v]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s

        export opt_mult=1
        export opt_multi=1
        TRES[$v]="odoo${m}"
        [[ $w =~ ^(v|V)[0-9] ]] && TRES[$v]="odoo"
        [ ${opt_dry_run:-0} -eq 0 ] && RES=$(build_odoo_param USER $v)
        test_result "multi db username $v [bash]" "${TRES[$v]}" "$RES"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
    done
    return $sts
}

__test_06() {
    local s sts v w
    sts=0
    export opt_mult=1
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
    export opt_mult=0
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
    export opt_mult=1
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
        popd >/dev/null
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
    export opt_mult=1
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
    export opt_mult=1
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


Z0BUG_setup() {
# Modules Tree for tests
# l10n-italy/l10n_it_base
# addons/web
#   |---- addons/account
#   |---- addons/base   
#   |---- addons/sale
#   \---- addons/web
# unported/l10n_it_base

    local f v x
    local ODOO_REPO=local/odoo
    LCL_ROOT=$HOME
    LCL_VERSION=9.0
    LCL_OO_PRJNAME="Odoo"
    LCL_OO_REPOS=l10n_italy
    LCL_OO_PKGNAME=l10n_it_base
    Z0BUG_build_os_tree "$LCL_VERSION/openerp $LCL_VERSION/addons/base $LCL_VERSION/addons/account $LCL_VERSION/addons/sale $LCL_VERSION/addons/web $LCL_VERSION/$LCL_OO_REPOS/$LCL_OO_PKGNAME $LCL_VERSION/__unported__/$LCL_OO_PKGNAME"
    LCL_OE_ROOT=$Z0BUG_root/$LCL_VERSION

    LCL_OE_PRJPATH=$LCL_OE_ROOT/$LCL_OO_REPOS
    LCL_OE_PKGPATH=$LCL_OE_PRJPATH/$LCL_OO_PKGNAME
    LCL_OE_PKGPATH2=$LCL_OE_ROOT/__unported__/$LCL_OO_PKGNAME
    touch $LCL_OE_ROOT/openerp-server
    touch $LCL_OE_PKGPATH/__openerp__.py
    touch $LCL_OE_PKGPATH2/__openerp__.py
    LCL_OO_SETUP=__openerp__.py
    LCLTEST_MQT_PATH=$HOME/maintainer-quality-tools/travis
    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      if [ ! -f /etc/odoo/odoo9-server.conf ]; then
        LCLTEST_ODOO9_SERVER=/etc/odoo/odoo9-server.conf
        touch $LCLTEST_ODOO9_SERVER
      fi
    fi
    if [ -d $Z0BUG_root/$LCL_VERSION/dependencies ]; then rm -fR $Z0BUG_root/$LCL_VERSION/dependencies; fi
    if [ -L $Z0BUG_root/$LCL_VERSION/dependencies ]; then rm -f $Z0BUG_root/$LCL_VERSION/dependencies; fi

    # LCL_VE_ROOT=$RHOME/dev/odoo/VENV-$LCL_VERSION/odoo
    LCL_VE_ROOT=$TESTDIR/res/VENV-$LCL_VERSION/odoo
    LCL_VE_PRJPATH=$LCL_VE_ROOT/$LCL_OO_REPOS
    LCL_VE_PKGPATH=$LCL_VE_PRJPATH/$LCL_OO_PKGNAME
    LCL_VE_PKGPATH2=$LCL_VE_ROOT/__unported__/$LCL_OO_PKGNAME

    Z0BUG_build_os_tree "VENV-$LCL_VERSION/odoo/openerp VENV-$LCL_VERSION/odoo/addons/base VENV-$LCL_VERSION/odoo/addons/account VENV-$LCL_VERSION/odoo/addons/sale VENV-$LCL_VERSION/odoo/addons/web VENV-$LCL_VERSION/odoo/$LCL_OO_REPOS/$LCL_OO_PKGNAME VENV-$LCL_VERSION/odoo/__unported__/$LCL_OO_PKGNAME"

    touch $LCL_VE_ROOT/openerp-server
    touch $LCL_VE_PKGPATH/__openerp__.py
    touch $LCL_VE_PKGPATH2/__openerp__.py

    Z0BUG_build_os_tree "6.1 7.0 8.0 9.0 10.0 11.0 12.0 librerp6 oca7 oca8 oca10"
    for v in 6.1 7.0 8.0 9.0 10.0 11.0 12.0 librerp6 oca7 oca8 oca10; do
      f=$(echo $v|grep -Eo [0-9]+|head -n1)
      [ $f -ge 10 ] && x=odoo-bin || x=openerp-server
      touch $Z0BUG_root/$v/$x
      [ $f -ge 10 ] && x=odoo || x=openerp
      Z0BUG_build_os_tree "$v/addons $v/$x/addons"
    done
}

Z0BUG_teardown() {
    Z0BUG_remove_os_tree "$LCL_VERSION VENV-$LCL_VERSION"
    Z0BUG_remove_os_tree "6.1 7.0 8.0 9.0 10.0 11.0 12.0 librerp6 oca7 oca8 oca10"

    if [[ $HOSTNAME =~ shs[a-z0-9]+ ]]; then
      if [ -n "$LCLTEST_ODOO9_SERVER" ]; then
        rm -f $LCLTEST_ODOO9_SERVER
      fi
    fi
    if [ -f $FOUT ]; then rm -f $FOUT; fi
    if [ -f $FTEST ]; then rm -f $FTEST; fi
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
