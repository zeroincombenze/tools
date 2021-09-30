#!/usr/bin/env bash
#
# Do not move above code and follow function to avoid crash
# after this script is updated when running!
pull_n_run() {
    # pull_n_run($1=path $2="$0" $3="$1")
    local l m1 m2 o opts x
    m1=$(stat -c %Y $2)
    cd $1 && git pull
    m2=$(stat -c %Y $2)
    o="$3"; opts=""; l=${#o}
    while ((l>1)); do
        ((l--)); x="${o:$l:1}"; [[ $x != "U" ]] && opts="$opts$x"
    done
    [[ $m1 == $m2 ]] && eval $2 -${opts} || eval $2 -f${opts}
    exit $?
}

# From here, code may be update
__version__=1.0.6.7

READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
complete &>/dev/null && COMPLETE="complete" || COMPLETE="# complete"
THIS=$(basename "$0")
TDIR=$($READLINK -f $(dirname $0))
opts=$(echo $1 $2 $3 $4 $5 $6 $7 $8 $9)
if [[ $opts =~ ^-.*h ]]; then
    echo "$THIS [-h][-n][-o][-p][-P][-q][-S][-T][-v][-V]"
    echo "  -h  this help"
    echo "  -d  use development branch not master"
    echo "  -D  create development environment"
    echo "  -f  force creation of virtual environment even if exists"
    echo "  -g  do not install hooks in git projects"
    echo "  -G  remove hooks from git projects"
    echo "  -n  dry-run"
    # echo "  -o  compatibility old mode (exec dir in $HOME/dev, deprecated)"
    echo "  -p  mkdir $HOME/dev[el] if does not exist"
    echo "  -P  permanent environment (update ~/.bash_profile)"
    echo "  -q  quiet mode"
    echo "  -s  store sitecustomize.py in python path (you must have privileges)"
    echo "  -S  store sitecustomize.py in python path (you must have privileges)"
    echo "  -t  this script is executing in travis-ci environment"
    echo "  -T  execute regression tests"
    echo "  -U  pull from github for upgrade"
    echo "  -v  more verbose"
    echo "  -V  show version and exit"
    echo "  -3  create virtual environment with python3"
    echo -e "\n(C) 2015-2021 by zeroincombenze(R)\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
    exit 0
elif [[ $opts =~ ^-.*V ]]; then
    echo $__version__
    exit 0
fi

run_traced() {
    local xcmd="$1"
    local sts=0
    local PMPT=
    [[ $opts =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
    [[ $opts =~ ^-.*q ]] || echo "$PMPT$xcmd"
    [[ $opts =~ ^-.*n ]] || eval $xcmd
    sts=$?
    return $sts
}

RFLIST__travis_emulator="travis travis.man travisrc"
RFLIST__devel_tools=""
RFLIST__clodoo="awsfw bck_filestore.sh clodoo.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog odoo_skin.sh set_worker.sh transodoo.py transodoo.xlsx"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=". z0librc"
RFLIST__zerobug="zerobug z0testrc"
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="activate_devel_env odoo_default_tnl.xlsx templates license_text readlink"
RFLIST__python_plus="vem vem.man"
RFLIST__wok_code="cvt_csv_2_rst.py cvt_csv_2_xml.py cvt_script dist_pkg generate_all_tnl gen_addons_table.py gen_readme.py license_mgnt.py makepo_it.py odoo_dependencies.py odoo_translation.py please please.man topep8 to_oca.2p8 to_zero.2p8 to_pep8.2p8 to_pep8.py vfcp vfdiff wget_odoo_repositories.py"
RFLIST__zerobug_odoo=""
RFLIST__odoo_score="odoo_shell.py run_odoo_debug"
RFLIST__os0=""
MOVED_FILES_RE="(cvt_csv_2_rst.py|cvt_csv_2_xml.py|cvt_script|dist_pkg|gen_addons_table.py|gen_readme.py|makepo_it.py|odoo_translation.py|please|please.man|please.py|run_odoo_debug|topep8|topep8.py|transodoo.py|transodoo.xlsx|vfcp|vfdiff)"
FILES_2_DELETE="addsubm.sh clodoocore.py clodoolib.py devel_tools export_db_model.py odoo_default_tnl.csv please.py prjdiff replica.sh run_odoo_debug.sh set_odoover_confn topep8.py to_oia.2p8 transodoo.csv upd_oemod.py venv_mgr venv_mgr.man wok_doc wok_doc.py z0lib.py z0librun.py"

SRCPATH=
DSTPATH=
RED="\e[31m"
GREEN="\e[32m"
CLR="\e[0m"

[[ $opts =~ ^-.*t ]] && HOME=$($READLINK -e $(dirname $0)/..)
[[ $opts =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
[[ $opts =~ ^-.*o ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
[[ -d $TDIR/clodoo && -d $TDIR/wok_code && -d $TDIR/z0lib ]] && SRCPATH=$TDIR
[[ -z "$SRCPATH" && -d $TDIR/../tools && -d $TDIR/../z0lib ]] && SRCPATH=$(readlink -f $TDIR/..)
[[ -z "$SRCPATH" && -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ ! -d $HOME_DEV && -n "$SRCPATH" && $opts =~ ^-.*p ]] && run_traced "mkdir -p $HOME_DEV"
[[ -d $HOME_DEV ]] && DSTPATH=$HOME_DEV
if [[ -z "$SRCPATH" || -z "$DSTPATH" ]]; then
    echo "# Invalid environment!"
    [[ -d $HOME/dev ]] && echo "# .. you should rename $HOME/dev to $HOME/devel"
    echo ""
    $0 -h
    exit 1
fi
if [[ ! $opts =~ ^-.*t && ! $opts =~ ^-.*D && -d $SRCPATH/.git ]]; then
    [[ $opts =~ ^-.*d && ! $opts =~ ^-.*q ]] && echo "# Use development branch" && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "devel" ]] && git stash -q && git checkout devel -f
    [[ ! $opts =~ ^-.*d ]] && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "master" ]] && git stash -q && git checkout master -fq
    [[ $opts =~ ^-.*U ]] && git stash -q && pull_n_run "$SRCPATH" "$0" "$opts"
fi
[[ $opts =~ ^-.*v && ! $opts =~ ^-.*D ]] && echo -e "${GREEN}# Installing tools from $SRCPATH to $DSTPATH ...${CLR}"
[[ $opts =~ ^-.*v && $opts =~ ^-.*D ]] && echo "# Creating development environment $HOME_DEV/pypi ..."
[[ $opts =~ ^-.*n ]] || find $SRCPATH $DSTPATH -name "*.pyc" -delete
[[ $opts =~ ^-.*o ]] && echo -e "${RED}# WARNING! The switch -o is not more supported!${CLR}"

[[ -x $SRCPATH/python_plus/python_plus/vem ]] && VEM="$SRCPATH/python_plus/python_plus/vem"
[[ -z "$VEM" && -x $SRCPATH/python_plus/vem ]] && VEM="$SRCPATH/python_plus/vem"
if [[ -z "$VEM" ]]; then
    echo -e "${RED}# Invalid environment! Command vem not found!${CLR}"
    echo ""
    exit 1
fi

if [[ $opts =~ ^-.*[fU] || ! -d $DSTPATH/venv/lib || ! -d $DSTPATH/venv/bin || ! -d $DSTPATH/bin ]]; then
    [[ -d $DSTPATH/tmp ]] && run_traced "rm -fR $DSTPATH/tmp"
    [[ -d $HOME/.cache/pip && $opts =~ ^-.*p ]] && run_traced "rm -fR $HOME/.cache/pip"
    x="-iDBB"
    [[ $opts =~ ^-.*q ]] && x="-qiDBB"
    [[ $opts =~ ^-.*v ]] && x="-viDBB"
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && x="${x}t"
    if [[ $opts =~ ^-.*3 ]]; then
        run_traced "$VEM create $DSTPATH/venv -p3.7 $x -f"
    else
        run_traced "$VEM create $DSTPATH/venv -p2.7 $x -f"
    fi
    [[ $? -ne 0 ]] && echo -e "${RED}# Error creating Tools virtual environment!${CLR}" && exit 1
    [[ ! -d $DSTPATH/venv/bin || ! -d $DSTPATH/venv/lib ]] && echo -e "${RED}# Incomplete Tools virtual environment!${CLR}" && exit 1
fi

[[ ! $opts =~ ^-.*q ]] && echo "# Moving local PYPI packages into virtual environment"
run_traced ". $DSTPATH/venv/bin/activate"
# PYPATH=$(find $DSTPATH/venv/lib -type d -name site-packages)

PLEASE_CMDS=""
TRAVIS_CMDS=""
PKGS_LIST="clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
PIPVER=$(pip --version | grep -Eo [0-9]+ | head -n1)
[[ $opts =~ ^-.*q ]] && popts="-q --disable-pip-version-check --no-python-version-warning" || popts="--disable-pip-version-check --no-python-version-warning"
[[ $PIPVER -gt 18 ]] && popts="$popts --no-warn-conflicts"
[[ $PIPVER -eq 19 ]] && popts="$popts --use-feature=2020-resolver"
[[ $PIPVER -ge 21 ]] && popts="$popts --use-feature=in-tree-build"
[[ $opts =~ ^-.*v ]] && echo "# $(which pip).$PIPVER $popts ..."
[[ ! -d $DSTPATH/tmp ]] && mkdir -p $DSTPATH/tmp

for pkg in $PKGS_LIST tools; do
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
    l="RFLIST__$pfn"
    flist=${!l}
    [[ $opts =~ ^-.*q ]] || echo -e "# ====[$pkg=($flist)]===="
    if [[ $pkg != "tools" && ! -d $SRCPATH/$pfn ]]; then
        echo -e "${RED}# Invalid environment! Source dir $SRCPATH/$pfn not found!${CLR}"
        echo ""
        exit 1
    fi
    if [[ $pkg == "tools" ]]; then
      [[ -d $SRCPATH/$pfn ]] && srcdir="$SRCPATH/$pfn" || srcdir="$SRCPATH"
    else
      [[ -d $SRCPATH/$pfn/$pfn ]] && srcdir="$SRCPATH/$pfn/$pfn" || srcdir="$SRCPATH/$pfn"
    fi
    for fn in $flist; do
        if [[ $fn == "." ]]; then
            src="$srcdir"
            tgt="$DSTPATH/${pfn}"
            ftype=d
        elif [[ $fn == "readlink" ]]; then
            READLINK=$(which greadlink 2>/dev/null)
            if [[ -z "$READLINK" ]]; then
                [[ -L $DSTPATH/readlink ]] && rm -f $DSTPATH/readlink
                continue
            fi
            src=$READLINK
            tgt="$DSTPATH/${fn}"
            ftype=f
        else
            src="$srcdir/$fn"
            tgt="$DSTPATH/$fn"
            [[ -d "$src" ]] && ftype=d || ftype=f
            if [[ $fn == "please" ]]; then
                PLEASE_CMDS=$(grep "^HLPCMDLIST=" $src|awk -F= '{print $2}'|tr -d '"')
                PLEASE_CMDS="${PLEASE_CMDS//|/ }"
            elif [[ $fn == "travis" ]]; then
                TRAVIS_CMDS=$(grep "^ACTIONS=" $src|awk -F= '{print $2}'|tr -d '"')
                TRAVIS_CMDS=${TRAVIS_CMDS:1: -1}
                TRAVIS_CMDS="${TRAVIS_CMDS//|/ }"
            fi
        fi
        if $(echo "$src"|grep -Eq "\*"); then
            src=$(dirname "$src")
            tgt=$(dirname "$tgt")
            ftype=d
        fi
        if [[ ! -e "$src" ]]; then
            echo "# File $src not found!"
        # elif [[ ! -e "$tgt" || -L "$tgt" || $opts =~ ^-.*[fpU] || $fn =~ $MOVED_FILES_RE ]]; then
        else
            [[ -L "$tgt" ]] && run_traced "rm -f $tgt"
            [[ -d "$tgt" ]] && run_traced "rm -fR $tgt"
            if [[ $fn =~ (kbase|templates|license_text|readlink) ]]; then
                [[ ! -d $(dirname $tgt) ]] && run_traced "mkdir -p $(dirname $tgt)"
                run_traced "ln -s $src $tgt"
            # elif [[ ! -e "$tgt" || $opts =~ ^-.*[fpU] ]]; then
            else
                [[ $ftype == f ]] && copts="" || copts="-r"
                run_traced "cp $copts $src $tgt"
                [[ ! $opts =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
            fi
        fi
    done
    if [[ $pkg =~ (clodoo|odoo_score|os0|python-plus|z0bug-odoo|z0lib|zar|zerobug) ]]; then
        if [[ -d $SRCPATH/$pfn/$pfn ]]; then
            run_traced "cp -r $SRCPATH/$pfn/ $DSTPATH/tmp/"
        else
            run_traced "mkdir $DSTPATH/tmp/$pfn"
            run_traced "cp -r $SRCPATH/$pfn/ $DSTPATH/tmp/$pfn/"
            run_traced "mv $DSTPATH/tmp/$pfn/$pfn/setup.py $DSTPATH/tmp/$pfn/setup.py"
        fi
        run_traced "pip install $DSTPATH/tmp/$pfn $popts"
    fi
done
[[ -d "$DSTPATH/_travis" ]] && run_traced "rm -fR $DSTPATH/_travis"
[[ -f $SRCPATH/tools/tests/test_tools.sh ]] && run_traced "cp $SRCPATH/tools/tests/test_tools.sh $DSTPATH/test_tools.sh" || run_traced "cp $SRCPATH/tests/test_tools.sh $DSTPATH/test_tools.sh"
[[ -d $DSTPATH/tmp ]] && run_traced "rm -fR $DSTPATH/tmp"

for fn in $FILES_2_DELETE; do
    tgt="$DSTPATH/$fn"
    if [[ -d "$tgt" ]]; then
        run_traced "rm -fR $tgt"
    elif [[ -L "$tgt" || -f "$tgt" ]]; then
        run_traced "rm -f $tgt"
        [[ ! $opts =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
    fi
done

if [[ ! $opts =~ ^-.*n ]]; then
    echo -e "import sys\nif '$SRCPATH' not in sys.path:    sys.path.insert(0,'$SRCPATH')">$DSTPATH/sitecustomize.py
    echo "[[ -f $DSTPATH/venv/bin/activate ]] && export PATH=\$PATH:$DSTPATH/venv/bin">$DSTPATH/activate_tools
    echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -z "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH">>$DSTPATH/activate_tools
    echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -n "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH:\$PYTHONPATH">>$DSTPATH/activate_tools
    echo "[[ ! -d $DSTPATH || :\$PATH: =~ :$DSTPATH: ]] || export PATH=$DSTPATH:\$PATH">>$DSTPATH/activate_tools
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && echo "[[ ! -d $SRCPATH/zerobug/_travis || :\$PATH: =~ :$SRCPATH/zerobug/_travis: ]] || export PATH=$SRCPATH/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && echo "[[ ! -d $SRCPATH/z0bug_odoo/travis || :\$PATH: =~ :$SRCPATH/z0bug_odoo/travis: ]] || export PATH=$SRCPATH/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    [[ -n $PLEASE_CMDS ]] && echo "$COMPLETE -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
    [[ -n $TRAVIS_CMDS ]] && echo "$COMPLETE -W \"$TRAVIS_CMDS\" travis">>$DSTPATH/activate_tools
fi
PYLIB=$(dirname $(pip --version 2>/dev/null|grep -Eo "from [^ ]+"|awk '{print $2}') 2>/dev/null)
if [[ $opts =~ ^-.*[Ss] ]]; then
    [[ ! $opts =~ ^-.*o ]] && SITECUSTOM=$HOME/devel/sitecustomize.py
    [[ $opts =~ ^-.*o ]] && SITECUSTOM=$HOME/dev/sitecustomize.py
    [[ -n "$PYLIB" ]] || PYLIB=$(dirname $(pip3 --version 2>/dev/null|grep -Eo "from [^ ]+"|awk '{print $2}') 2>/dev/null)
    if [[ -n "$PYLIB" && -f SITECUSTOM ]]; then
        if [[ -f $PYLIB/sitecustomize.py ]]; then
            if grep -q "import sys" $PYLIB/sitecustomize.py; then
                run_traced "tail $SITECUSTOM -n -1 >> $SITECUSTOM"
            else
                run_traced "cat $SITECUSTOM >> $PYLIB/sitecustomize.py"
            fi
        else
            run_traced "cp $SITECUSTOM $PYLIB"
        fi
    fi
fi
run_traced "deactivate"
# run_traced "source $DSTPATH/activate_tools"

[[ $PATH =~ $DSTPATH/venv/bin ]] || export PATH="$DSTPATH/venv/bin:$PATH"
PYTHON=""
PYTHON3=""
[[ -x $DSTPATH/venv/bin/python ]] && PYTHON=$DSTPATH/venv/bin/python
[[ -x $DSTPATH/venv/bin/python2 ]] && PYTHON=$DSTPATH/venv/bin/python2
[[ -x $DSTPATH/venv/bin/python3 ]] && PYTHON3=$DSTPATH/venv/bin/python3
path="$DSTPATH/*"
[[ $opts =~ ^-.*[fU] && -d $DSTPATH/venv ]] && path=$(find $DSTPATH $PYLIB -maxdepth 1 \( -type f -executable -o -name "*.py" \)|tr "\n" " ")
for f in $path; do
    grep -q "^#\!.*/bin.*python3$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python3|#\!$PYTHON3|\" $f" && chmod +x $f
    grep -q "^#\!.*/bin.*python2$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python2|#\!$PYTHON|\" $f" && chmod +x $f
    grep -q "^#\!.*/bin.*python$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python|#\!$PYTHON|\" $f" && chmod +x $f
done
if [[ $opts =~ ^-.*[fU] || -d $DSTPATH/venv ]]; then
    # Please do not change package list order
    for pkg in psycopg2-binary babel lxml pyyaml; do
        pfn=$(echo "$pkg"|grep -Eo '[^!<=>\\[]*'|head -n1)
        [[ -d $HOME_DEV/pypi/$pfn/$pfn ]] && run_traced "$VEM $DSTPATH/venv install $pkg -qBB" || run_traced "$VEM $DSTPATH/venv install $pkg"
    done
    [[ -d $DSTPATH/clodoo ]] && run_traced "rm -f $DSTPATH/clodoo"
    x=$($VEM $DSTPATH/venv info clodoo|grep -E "Location"|cut -d' ' -f2)/clodoo
    [[ -d $x ]] && run_traced "ln -s $x $DSTPATH/clodoo"
fi
if [[ ! $opts =~ ^-.*n && $opts =~ ^-.*D ]]; then
    mkdir -p $HOME_DEV/pypi
    for pkg in $PKGS_LIST tools; do
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
        mkdir -p $HOME_DEV/pypi/$pfn
        [[ $pkg == "tools" ]] && rsync -avzb $SRCPATH/$pkg/ $HOME_DEV/pypi/$pkg/ || rsync -avzb $SRCPATH/$pfn/ $HOME_DEV/pypi/$pfn/$pfn/
    done
fi
if [[ ! $opts =~ ^-.*n && $opts =~ ^-.*P ]]; then
    $(grep -q "\$HOME/dev[el]*/activate_tools" $HOME/.bash_profile) && sed -e "s|\$HOME/dev[el]*/activate_tools|\$HOME/devel/activate_tools|" -i $HOME/.bash_profile || echo "[[ -f $HOME/devel/activate_tools ]] && . $HOME/devel/activate_tools -q" >>$HOME/.bash_profile
fi
[[ ! -f $DSTPATH/clodoo/odoorc ]] && echo -e "${RED}Incomplete installation! Ask Antonio to install clodoo!!${CLR}" && exit
[[ ! -d $DSTPATH/templates ]] && echo -e "${RED}Incomplete installation! Ask Antonio to reinstall tools!!${CLR}" && exit
[[ $opts =~ ^-.*T ]] && $DSTPATH/test_tools.sh
[[ $opts =~ ^-.*U && -f $DSTPATH/egg-info/history.rst ]] && tail $DSTPATH/egg-info/history.rst
if [[ ! $opts =~ ^-.*[gtT] ]]; then
  [[ ! $opts =~ ^-.*q ]] && echo "# Searching for git projects ..."
  for d in $(find $HOME -not -path "*/_*" -not -path "*/VME/*" -not -path "*/VENV*" -not -path "*/oca*" -not -path "*/tmp*" -name ".git" 2>/dev/null|sort); do
    run_traced "cp $SRCPATH/wok_code/pre-commit $d/hooks"
    run_traced "rm -f $d/hooks/pre-commit"
  done
fi
if [[ ! $opts =~ ^-.*q && ! $opts =~ ^-.*P ]]; then
    echo -e "${GREEN}--------------------------------------------------------------"
    echo -e "Zeroincombenze(R) tools successfully installed on your system."
    echo -e "In order to make available the these tools, please type:${CLR}"
    echo -e "source $DSTPATH/activate_tools\n"
    echo -e "${GREEN}If you wish to use  these tools  at the next time,  please add"
    echo -e "the  following statement  in your  login file  (.bash_profile)"
    echo -e "source $DSTPATH/activate_tools"
    echo -e "If you prefer, you can re-execute this script using  -P switch"
    echo -e "--------------------------------------------------------------${CLR}"
    echo -e "For furthermore info visit https://zeroincombenze-tools.readthedocs.io/"
fi
