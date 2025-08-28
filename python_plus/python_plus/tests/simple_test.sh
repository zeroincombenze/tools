RED="\e[31m"
GREEN="\e[32m"
CYAN="\e[36m"
CLR="\e[0m"
VENV="/home/odoo/SAMPLE"
DEFPKG="z0bug_odoo"
VEM="/home/odoo/devel/pypi/python_plus/python_plus/scripts/vem.sh"
PYVER="3.10"
SAVED_GREP_COLORS="$GREP_COLORS"
export GREP_COLORS="mt=36:mc=36"
RES="\n"
opts=""
while [[ -n $1 ]]; do
    [[ $1 == "-h" || $1 == "--help" ]] && echo "$(basename $0) [-f][-i][-y][--pyver=PYVER][--def-pkg=DEFPKG][--venv=VENV]" && exit 0
    [[ $1 =~ ^(--python=) ]] && PYVER=$(echo $1 | cut -d= -f2 | tr -d " ")
    [[ $1 =~ ^(--def-pkg=) ]] && DEFPKG=$(echo $1 | cut -d= -f2 | tr -d " " | tr -d "'" | tr -d '"')
    [[ $1 =~ ^(--venv=) ]] && VENV=$(echo $1 | cut -d= -f2 | tr -d " " | tr -d "'" | tr -d '"')
    [[ $1 =~ ^-[efiy]$ ]] && opts="$1"
    shift
done
# [[ -n $opts ]] && opts="-${opts}"

do_test() {
#do_test(pkg, test_msg, gbl, y|q, opts ...)
    local dummy p
    p=$(echo $1|grep -Eo "[^<=>]*"|head -1)
    echo -e "\n\n"
    echo "=====[$p $2]====="
    [[ $3 =~ ^-[yie] ]] && dummy="${3:1}"
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
    local pkg="$1" fqp p sts1 sts2 state v x
    fqp=$(echo $pkg|grep -Eo "[^<=>]*"|head -1)
    p=$(basename $fqp)
    echo -e "\n"
    echo "--[$p $2 ($3)]--"
    if [[ "$3" == "i" ]]; then
        state=""
        echo . $VENV/bin/activate
        . $VENV/bin/activate
        echo $VEM install $pkg $4 $5 $6 $7
        $VEM install $pkg -vv $4 $5 $6 $7 | grep --color -E "(pip|$p) .*"
        sts1=$?
        [[ $sts1 -eq 0 ]] && state="${GREEN}Installable${CLR}"
        [[ $sts1 -ne 0 ]] && echo -e "${RED}ERROR! Return status from pip install $p is $sts1!${CLR}"
        echo pip show $p
        pip show $p
        sts2=$?
        [[ $sts2 -eq 0 && sts1 -eq 0 ]] && state="${GREEN}OK${CLR}" && echo -e "$state"
        [[ $sts2 -ne 0 ]] && state="${RED}not detected${CLR}" && echo -e "${RED}ERROR!${CLR} Package $p $2 $state ($sts1)!"
        [[ $sts2 -ne 0 && sts1 -eq 0 ]] && sts1=$sts2
        echo ""
        echo $VEM uninstall $pkg -y
        $VEM uninstall $p -vv -y| grep --color -E "(pip|$p) .*"
        pip show $p
        sts2=$?
        [[ $sts2 -ne 0 && sts1 -eq 0 ]] && state="$state+${GREEN}PASSED${CLR}" && echo -e "$state"
        [[ $sts2 -eq 0 ]] && state="$state+${RED}still installed${CLR}" && echo -e "${RED}ERROR!${CLR} Package $p $2 $state ($sts2)!"
        echo deactivate
        deactivate
    elif [[ "$3" == "e" ]]; then
        echo $VEM $VENV install $pkg $4 $5 $6 $7
        $VEM $VENV install $pkg -vv $4 $5 $6 $7 | grep --color -E "(pip|$p) .*"
        sts1=$?
        [[ $sts1 -eq 0 ]] && state="${GREEN}Installable${CLR}"
        [[ $sts1 -ne 0 ]] && echo -e "${RED}ERROR! Return status from pip install $p is $sts1!${CLR}"
        $VENV/bin/pip show $p
        sts2=$?
        [[ $sts2 -eq 0 && sts1 -eq 0 ]] && state="${GREEN}OK${CLR}" && echo -e "$state"
        [[ $sts2 -ne 0 ]] && state="${RED}not detected${CLR}" && echo -e "${RED}ERROR!${CLR} Package $p $2 $state ($sts1)!"
        [[ $sts2 -ne 0 && sts1 -eq 0 ]] && sts1=$sts2
        echo ""
        echo $VENV $VEM uninstall $pkg -y
        $VEM $VENV uninstall $p -vv -y| grep --color -E "(pip|$p) .*"
        $VENV/bin/pip show $p
        sts2=$?
        [[ $sts2 -ne 0 && sts1 -eq 0 ]] && state="$state+${GREEN}PASSED${CLR}" && echo -e "$state"
        [[ $sts2 -eq 0 ]] && state="$state+${RED}still installed${CLR}" && echo -e "${RED}ERROR!${CLR} Package $p $2 $state ($sts2)!"
    fi
    x="| $(date '+%Y-%m-%d %H:%M:%S') |"
    printf -v v "%-72.72s" "$1 $2 ($3)"
    RES="${RES}$x $v $state\n"
}


clear
echo "Simple test vem.sh $opts --python=$PYVER --def-pkg=$DEFPKG --venv=$VENV"
echo ""

if [[ ! -d $VENV || $opts =~ ^-[fyie] ]]; then
    [[ -d $VENV ]] && rm -fR $VENV
    if [[ $PYVER == "2.7" ]]; then
      echo python$PYVER -m virtualenv $VENV
      python$PYVER -m virtualenv $VENV
    else
      echo python$PYVER -m venv create $VENV
      python$PYVER -m venv create $VENV
      for p in wheel setuptools; do
        echo pip install $p -q
        pip install $p -q
    done
    fi
fi

dummy=""
[[  $opts =~ ^-[fyie] ]] && dummy="y"
[[ -z $dummy ]] && read -p "Upgrade python-plus (y/n)? " dummy
if [[ $dummy =~ ^[Yy] ]]; then
    echo . $VENV/bin/activate
    . $VENV/bin/activate
    # pip install pip -Uq
    for p in wheel setuptools z0lib python_plus $DEFPKG; do
        echo pip install $p -q
        pip install $p -q
    done
    echo pip uninstall $DEFPKG -y
    pip uninstall $DEFPKG -y
    echo deactivate
    deactivate
    # echo /home/odoo/devel/venv/bin/pip install /home/odoo/devel/pypi/$DEFPKG -q
    # /home/odoo/devel/venv/bin/pip install /home/odoo/devel/pypi/$DEFPKG -q
fi

do_test "$DEFPKG" "from PYPI" "$opts"
do_test "coverage==4.0" "PYPI==ver" "$opts"
do_test "coverage" "PYPI.defver" "$opts"
do_test "$DEFPKG" "from PYPI-devel" "$opts" "" "-B"
do_test "/home/odoo/devel/pypi/$DEFPKG" "from /devel/pypi" "$opts"
do_test "/home/odoo/tools/$DEFPKG" "from /tools" "$opts"
do_test "/home/odoo/devel/venv/lib/python$PYVER/site-packages/$DEFPKG" "from /venv/bin" "$opts"
do_test "odoo" "odoo/12.0" "" "" "-o" "/home/odoo/12.0"
[[ $PYVER == "2.7" ]] && do_test "odoo" "openerp/7.0" "$opts" "" "-o" "/home/odoo/7.0"
[[ $PYVER == "2.7" ]] && do_test "distribute" "easy install" "$opts"
do_test "prestapyt" "git" "$opts"
do_test "Python-Chart" "wget" "$opts"
GREP_COLORS="$SAVED_GREP_COLORS"
echo -e "$RES"
