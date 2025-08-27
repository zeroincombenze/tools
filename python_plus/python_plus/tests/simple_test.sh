[[ $1 == "-h" ]] && echo "$0 [-f][-y]" && exit 0

RED="\e[31m"
GREEN="\e[32m"
CLR="\e[0m"
VENV="/home/odoo/SAMPLE"
def_pkg="travis_emulator"
VEM="/home/odoo/devel/pypi/python_plus/python_plus/scripts/vem.sh"
PYVER="3.11"
SAVED_GREP_COLORS="$GREP_COLORS"
export GREP_COLORS="mt=36:mc=36"

do_test() {
#do_test(pkg, test_msg, gbl, y|q, opts ...)
    local dummy p
    p=$(echo $1|grep -Eo "[^<=>]*"|head -1)
    echo -e "\n\n"
    echo "=====[$p $2]====="
    [[ $3 =~ ^-[y] ]] && dummy="y"
    [[ -n "$4" ]] && dummy="$4"
    [[ -z $dummy ]] && read -p "Test $2 (reload python+)(Inside/External/Yes both/No)? " dummy
    if [[ $dummy =~ [+] ]]; then
        . $VENV/bin/activate
        pip install /home/odoo/devel/pypi/travis_emulator/ -Uq
        deactivate
    fi
    if [[ $dummy =~ [+IiYy] ]]; then
        [[ $dummy =~ [IiYy] ]] && run_test "$1" "$2" "i" "$5" "$6" "$7" "$8"
        read -p "Press RET to continue ..."
    fi
    if [[ $dummy =~ [YyEe] ]]; then
        [[ $dummy =~ [IiYy] ]] && run_test "$1" "$2" "e" "$5" "$6" "$7" "$8"
        read -p "Press RET to continue ..."
    fi
}


run_test() {
#run_test pkg msg i|e opts ...
    local pkg="$1" p sts
    p=$(echo $pkg|grep -Eo "[^<=>]*"|head -1)
    echo -e "\n"
    echo "--[$p $2 ($3)]--"
    if [[ "$3" == "i" ]]; then
        echo . $VENV/bin/activate
        . $VENV/bin/activate
        echo $VEM install $pkg $4 $5 $6 $7
        $VEM install $pkg -vv $4 $5 $6 $7 | grep --color -E "(pip|$p) .*"
        pip show $p
        sts=$?
        [[ $sts -eq 0 ]] && echo -e "${GREEN}OK${CLR}"
        [[ $sts -ne 0 ]] && echo -e "${RED}ERROR! Package $p $2 not detected!${CLR}"
        echo ""
        echo $VEM uninstall $pkg -y
        $VEM uninstall $p -vv -y| grep --color -E "(pip|$p) .*"
        pip show $p
        sts=$?
        [[ $sts -ne 0 ]] && echo -e "${GREEN}OK${CLR}"
        [[ $sts -eq 0 ]] && echo -e "${RED}ERROR! Package $p $2 still installed!${CLR}"
        echo deactivate
        deactivate
    elif [[ "$3" == "e" ]]; then
        echo $VEM $VENV install $pkg $4 $5 $6 $7
        $VEM $VENV install $pkg -vv $4 $5 $6 $7 | grep --color -E "(pip|$p) .*"
        $VENV/bin/pip show $p
        sts=$?
        [[ $sts -eq 0 ]] && echo -e "${GREEN}OK${CLR}"
        [[ $sts -ne 0 ]] && echo -e "${RED}ERROR! Package $p $2 not detected!${CLR}"
        echo ""
        echo $VENV $VEM uninstall $pkg -y
        $VEM $VENV uninstall $p -vv -y| grep --color -E "(pip|$p) .*"
        $VENV/bin/pip show $p
        sts=$?
        [[ $sts -ne 0 ]] && echo -e "${GREEN}OK${CLR}"
        [[ $sts -eq 0 ]] && echo -e "${RED}ERROR! Package $p $2 still installed!${CLR}"
    fi
}


clear
if [[ ! -d $VENV || $1 == "-f" || $1 == "-y" ]]; then
    [[ -d $VENV ]] && rm -fR $VENV
    echo python$PYVER -m venv create $VENV
    python$PYVER -m venv create $VENV
fi

dummy=""
[[  $1 == "-f" || $1 == "-y" ]] && dummy="y"
[[ -z $dummy ]] && read -p "Upgrade python-plus (y/n)? " dummy
if [[ $dummy =~ ^[Yy] ]]; then
    echo . $VENV/bin/activate
    . $VENV/bin/activate
    # pip install pip -Uq
    for p in wheel setuptools z0lib python_plus; do
        echo pip install /home/odoo/devel/pypi/$p -q
        pip install /home/odoo/devel/pypi/$p -q
    done
    echo deactivate
    deactivate
    echo /home/odoo/devel/venv/bin/pip install /home/odoo/devel/pypi/travis_emulator/ -q
    /home/odoo/devel/venv/bin/pip install /home/odoo/devel/pypi/travis_emulator/ -q
fi

do_test "$def_pkg" "from PYPI" "$1"
do_test "coverage==4.0" "PYPI==ver" "$1"
do_test "coverage" "PYPI.defver" "$1"
do_test "$def_pkg" "from PYPI-devel" "$1" "" "-B"
do_test "/home/odoo/devel/pypi/$def_pkg" "from /devel/pypi" "$1"
do_test "/home/odoo/tools/$def_pkg" "from /tools" "$1"
do_test "/home/odoo/devel/venv/lib/python$PYVER/site-packages/$def_pkg" "from /venv/bin" "$1"
do_test "odoo" "odoo/12.0" "" "" "-o" "/home/odoo/12.0"
do_test "odoo" "openerp/7.0" "" "" "-o" "/home/odoo/7.0"
do_test "prestapyt" "git" "$1"
GREP_COLORS="$SAVED_GREP_COLORS"