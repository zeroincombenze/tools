RED="\e[31m"
GREEN="\e[32m"
CLR="\e[0m"
[[ -z $HOME_DEVEL ]] && HOME_DEVEL=~/devel
LOCAL_VENV="$HOME_DEVEL/venv"
BINPATH="$LOCAL_VENV/bin"
if [[ -n "$2" && -x "$2" ]]; then
    # Execution inside install_tools.sh
    VEM="$2"
    if_standalone() {
false 
}
    if_inside() {
true
}
else
    # Stand alone execution
    VEM="vem"
    echo "source $HOME_DEVEL/activate_tools"
    source $HOME_DEVEL/activate_tools
    if_standalone() {
true
}
    if_inside() {
false
}
fi

PYVER=$($LOCAL_VENV/bin/python --version 2>&1 | grep "Python" | grep --color=never -Eo "[23]" | head -n1)
for pkg in license_text templates tests; do
    if_inside && echo -n "."
    if_standalone && echo "Testing directory $pkg .."
    [[ ! -d $LOCAL_VENV/tools/$pkg ]] && echo -e "\n${RED}Incomplete installation! Directory $pkg non found in $LOCAL_VENV/tools/!!${CLR}" && exit 1
done
for pkg in odoo_template_tnl.xlsx; do
    if_inside && echo -n "."
    if_standalone && echo "Testing file $pkg .."
    [[ ! -f $LOCAL_VENV/tools/$pkg ]] && echo -e "\n${RED}Incomplete installation! File $pkg non found in $LOCAL_VENV/tools/!!${CLR}" && exit 1
done
for pkg in clodoo; do
    if_inside && echo -n "."
    if_standalone && echo "Testing directory $pkg .."
    [[ ! -d $BINPATH/$pkg ]] && echo -e "\n${RED}Incomplete installation! Directory $pkg non found in $BINPATH!!${CLR}" && exit 1
done
for pkg in odoorc odoo_dependencies.py zerobug; do
    if_inside && echo -n "."
    if_standalone && echo "Testing file $pkg .."
    [[ ! -f $BINPATH/$pkg ]] && echo -e "\n${RED}Incomplete installation! File $pkg non found in $BINPATH!!${CLR}" && exit 1
done
for pkg in cvt_csv_2_rst.py cvt_csv_2_xml.py cvt_script deploy_odoo gen_readme.py lisa_bld_ods list_requirements.py odooctl odoo_dependencies.py odoo_shell.py odoo_translation.py please pylint transodoo.py travis twine vem wget_odoo_repositories.py black flake8 pre-commit; do
    [[ ( $1 =~ ^-.*t || $PYVER -eq 2 ) && $pkg =~ ^(black|odooctl|pre-commit)$ ]] && continue
    if_inside && echo -n "."
    if_standalone && echo "Testing $pkg --version .."
    [[ ! -f $BINPATH/$pkg ]] && echo -e "\n${RED}Incomplete installation! File $pkg non found in $BINPATH!!${CLR}" && exit 1
    [[ ! -x $BINPATH/$pkg ]] && echo -e "\n${RED}Incomplete installation! File $pkg in $BINPATH is not executable!!${CLR}" && exit 1
    [[ $pkg =~ ^(odooctl|oca-gen-addon-readme)$ ]] && continue
    if_inside && echo -n "."
    if [[ $pkg =~ ^(lisa_bld_ods|odoo_install_repository|makepo_it.py)$ ]]; then
        $pkg -V &>/dev/null
        [[ $? -ne 0 ]] && echo -e "\n${RED}****** TEST $pkg FAILED ******${CLR}" && exit 1
    else
        $pkg --version &>/dev/null
        [[ $? -ne 0 ]] && echo -e "\n${RED}****** TEST $pkg FAILED ******${CLR}" && exit 1
    fi
done
for pkg in babel lxml python-magic pyyaml z0lib z0bug-odoo zerobug; do
    if_inside && echo -n ".."
    if_standalone && echo "Testing package $pkg installation .."
    pfn=$(echo "$pkg"| grep --color=never -Eo '[^!<=>\\[]*'|head -n1)
    x=$($VEM $LOCAL_VENV info $pkg 2>/dev/null|grep  --color=never -E "^Location: .*")
    [[ -z "$x" ]] && echo -e "\n${RED}Incomplete installation! Package $pkg non installed in $LOCAL_VENV!!${CLR}" && exit 1
done
if [[ ! $1 =~ ^-.*t && $PYVER -eq 3 ]]; then
    for pkg in oca-gen-addon-readme; do
        if_inside && echo -n ".."
        if_standalone && echo "Testing command $pkg installation .."
        x=$(which $pkg)
        [[ -z "$x" ]] && echo -e "\n${RED}Incomplete installation! Package $pkg non installed!${CLR}" && exit 1
    done
fi
echo ""
echo -e "${GREEN}Installed environment test SUCCESSFULLY completed${CLR}"
