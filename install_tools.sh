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
__version__=1.0.6.9

[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
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
    # echo "  -s  store sitecustomize.py in python path (you must have privileges)"
    # echo "  -S  store sitecustomize.py in python path (you must have privileges)"
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

set_hashbang() {
    local f
    f="$1"
    grep -Eq "^#\!.*/bin.*python[23]?$" $f &>/dev/null && run_traced "sed -E \"s|^#\!.*/bin.*python[23]?|#\!$PYTHON|\" -i $f" && chmod +x $f
}

RFLIST__travis_emulator="travis travis.man travisrc"  # TODO> remove early
RFLIST__devel_tools=""
RFLIST__clodoo="awsfw bck_filestore.sh clodoo.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog odoo_skin.sh set_worker.sh transodoo.py transodoo.xlsx"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=""
RFLIST__zerobug="zerobug z0testrc"
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="activate_devel_env odoo_default_tnl.xlsx templates license_text readlink"
RFLIST__python_plus=""
RFLIST__wok_code="cvt_csv_2_rst.py cvt_csv_2_xml.py dist_pkg generate_all_tnl gen_addons_table.py gen_readme.py license_mgnt.py makepo_it.py odoo_dependencies.py odoo_translation.py topep8 to_oca.2p8 to_zero.2p8 to_pep8.2p8 to_pep8.py vfcp vfdiff wget_odoo_repositories.py"
RFLIST__zerobug_odoo=""
RFLIST__odoo_score="odoo_shell.py run_odoo_debug"
RFLIST__os0=""
MOVED_FILES_RE="(cvt_csv_2_rst.py|cvt_csv_2_xml.py|cvt_script|dist_pkg|gen_addons_table.py|gen_readme.py|makepo_it.py|odoo_translation.py|please|please.man|please.py|run_odoo_debug|topep8|topep8.py|transodoo.py|transodoo.xlsx|vfcp|vfdiff)"
FILES_2_DELETE="addsubm.sh clodoo clodoocore.py clodoolib.py devel_tools export_db_model.py kbase oca-autopep8 odoo_default_tnl.csv please.py prjdiff replica.sh run_odoo_debug.sh set_color.sh set_odoover_confn test_tools.sh topep8.py to_oia.2p8 transodoo.csv upd_oemod.py venv_mgr venv_mgr.man wok_doc wok_doc.py z0lib z0lib.py z0librun.py"

SRCPATH=
DSTPATH=
RED="\e[31m"
GREEN="\e[32m"
CLR="\e[0m"

[[ $opts =~ ^-.*t ]] && HOME=$($READLINK -e $(dirname $0)/..)
[[ $opts =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
[[ -d $TDIR/clodoo && -d $TDIR/wok_code && -d $TDIR/z0lib ]] && SRCPATH=$TDIR
[[ -z "$SRCPATH" && -d $TDIR/../tools && -d $TDIR/../z0lib ]] && SRCPATH=$(readlink -f $TDIR/..)
[[ -z "$SRCPATH" && -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ -z "$SRCPATH" || ! -d $SRCPATH || ! -d $SRCPATH/z0lib ]] && echo "# Environment not found! No tools path found" && exit 1

[[ $(basename $SRCPATH) =~ (pypi|tools) ]] && DSTPATH="$(readlink -f $(dirname $SRCPATH)/devel)"                   # new: SRCPATH/venv_tools
[[ $(basename $(dirname $SRCPATH)) == "devel" ]] && DSTPATH="$(readlink -f $(dirname $(dirname $SRCPATH))/devel)"  # new: SRCPATH/venv_tools
LOCAL_VENV="$DSTPATH/venv"                                                                                         # new: DSTPATH
if [[ $DSTPATH != $LOCAL_VENV && ! -d $DSTPATH && ! $opts =~ ^-.*p ]]; then
    [[ -d "$HOME/dev" && ! -d $HOME/devel ]] && run_traced "mv $HOME/dev $HOME/devel"
    [[ ! -d $HOME/devel && -n "$SRCPATH" && $opts =~ ^-.*p ]] && run_traced "mkdir -p $HOME/devel"
    [[ -d $HOME/devel ]] && DSTPATH=$HOME/devel
fi
[[ -z "$DSTPATH" ]] && echo "# Environment not found! Please use -p switch" && exit 1
DEVELPATH="$(readlink DSTPATH/pypi)"   # new DSTPATH/../pypi

if [[ ! $opts =~ ^-.*t && ! $opts =~ ^-.*D && -d $SRCPATH/.git ]]; then
    [[ $opts =~ ^-.*d && ! $opts =~ ^-.*q ]] && echo "# Use development branch" && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "devel" ]] && git stash -q && git checkout devel -f
    [[ ! $opts =~ ^-.*d ]] && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "master" ]] && git stash -q && git checkout master -fq
    [[ $opts =~ ^-.*U ]] && git stash -q && pull_n_run "$SRCPATH" "$0" "$opts"
fi
[[ $opts =~ ^-.*v && ! $opts =~ ^-.*D ]] && echo -e "${GREEN}# Installing tools from $SRCPATH to $DSTPATH ...${CLR}"
[[ $opts =~ ^-.*v && $opts =~ ^-.*D ]] && echo -e "${GREEN}# Creating development environment $DEVELPATH ...${CLR}"
[[ $opts =~ ^-.*v ]] && echo "# Virtual environment is $LOCAL_VENV ..."
[[ $opts =~ ^-.*n ]] || find $SRCPATH $DSTPATH -name "*.pyc" -delete
[[ $opts =~ ^-.*o ]] && echo -e "${RED}# WARNING! The switch -o is not more supported!${CLR}"
[[ -x $SRCPATH/python_plus/python_plus/vem ]] && VEM="$SRCPATH/python_plus/python_plus/vem"
[[ -z "$VEM" && -x $SRCPATH/python_plus/vem ]] && VEM="$SRCPATH/python_plus/vem"
if [[ -z "$VEM" ]]; then
    echo -e "${RED}# Invalid environment! Command vem not found!${CLR}"
    echo ""
    exit 1
fi

for p in bin lib include; do
  [[ $DSTPATH != $LOCAL_VENV && -d $DSTPATH/$p ]] && run_traced "rm -fR $DSTPATH/$p"
done

if [[ $DSTPATH == $LOCAL_VENV || $opts =~ ^-.*[fU] || ! -d $LOCAL_VENV/lib || ! -d $DSTPATH/venv/bin || ! -d $DSTPATH/bin ]]; then
    x="-iDBB"
    [[ $opts =~ ^-.*q ]] && x="-qiDBB"
    [[ $opts =~ ^-.*v ]] && x="-viDBB"
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && x="${x}t"
    if [[ $opts =~ ^-.*3 ]]; then
        run_traced "$VEM create $LOCAL_VENV -p3.7 $x -f"
    else
        run_traced "$VEM create $LOCAL_VENV -p2.7 $x -f"
    fi
    [[ $? -ne 0 ]] && echo -e "${RED}# Error creating Tools virtual environment!${CLR}" && exit 1
    [[ ! -d $LOCAL_VENV/bin || ! -d $LOCAL_VENV/lib ]] && echo -e "${RED}# Incomplete Tools virtual environment!${CLR}" && exit 1
    [[ -d $HOME/.cache/pip && $opts =~ ^-.*p ]] && run_traced "rm -fR $HOME/.cache/pip"
    [[ ! -d $LOCAL_VENV/bin/man/man8 ]] && run_traced "mkdir -p $LOCAL_VENV/bin/man/man8"
fi

[[ ! $opts =~ ^-.*q ]] && echo "# Moving local PYPI packages into virtual environment"
run_traced ". $LOCAL_VENV/bin/activate"

PYLIB=$(find $LOCAL_VENV/lib -type d -name site-packages)
PYTHON=""
PYTHON3=""
[[ -x $LOCAL_VENV/bin/python ]] && PYTHON=$LOCAL_VENV/bin/python
[[ -x $LOCAL_VENV/bin/python2 ]] && PYTHON=$LOCAL_VENV/bin/python2
[[ -x $LOCAL_VENV/bin/python3 ]] && PYTHON3=$LOCAL_VENV/bin/python3
PLEASE_CMDS=""
TRAVIS_CMDS=""
PKGS_LIST="python-plus clodoo lisa odoo_score os0 travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
PYPI_LIST="babel lxml"
BINPATH="$LOCAL_VENV/bin"
PIPVER=$(pip --version | grep -Eo [0-9]+ | head -n1)
[[ $opts =~ ^-.*q ]] && popts="-q --disable-pip-version-check --no-python-version-warning" || popts="--disable-pip-version-check --no-python-version-warning"
[[ $PIPVER -gt 18 ]] && popts="$popts --no-warn-conflicts"
[[ $PIPVER -eq 19 ]] && popts="$popts --use-feature=2020-resolver"
[[ $PIPVER -ge 21 ]] && popts="$popts --use-feature=in-tree-build"
[[ $opts =~ ^-.*v ]] && echo "# $(which pip).$PIPVER $popts ..."
[[ -d $DSTPATH/tmp ]] && rm -fR $DSTPATH/tmp
[[ -d $LOCAL_VENV/tmp ]] && rm -fR $LOCAL_VENV/tmp
[[ ! -d $LOCAL_VENV/tmp ]] && mkdir -p $LOCAL_VENV/tmp
# TODO> Remove early
if [[ $opts =~ ^-.*[fU] && $DSTPATH != $LOCAL_VENV ]]; then
    # Please do not change package list order
    for pkg in $PYPI_LIST; do
        echo -n "."
        pfn=$(echo "$pkg"|grep -Eo '[^!<=>\\[]*'|head -n1)
        run_traced "$VEM $LOCAL_VENV install $pkg -q"
    done
    echo ""
fi

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
    # TODO> remove early: copy files
    if [[ $pkg == "tools" ]]; then
      [[ -d $SRCPATH/$pfn ]] && srcdir="$SRCPATH/$pfn" || srcdir="$SRCPATH"
    else
      [[ -d $SRCPATH/$pfn/$pfn ]] && srcdir="$SRCPATH/$pfn/$pfn" || srcdir="$SRCPATH/$pfn"
    fi
    for fn in $flist; do
        if [[ $fn == "." ]]; then
            src="$srcdir"
            tgt="$BINPATH/${pfn}"
            ftype=d
        elif [[ $fn == "readlink" ]]; then
            READLINK=$(which greadlink 2>/dev/null)
            if [[ -z "$READLINK" ]]; then
                [[ -L $BINPATH/readlink ]] && rm -f $BINPATH/readlink
                continue
            fi
            src=$READLINK
            tgt="$BINPATH/${fn}"
            ftype=f
        else
            src="$srcdir/$fn"
            tgt="$BINPATH/$fn"
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
        else
            [[ -L $DSTPATH/${fn} || -f $DSTPATH/${fn} ]] && run_traced "rm -f $DSTPATH/${fn}"
            [[ -d $DSTPATH/${fn} ]] && run_traced "rm -fR $DSTPATH/${fn}"
            [[ -L "$tgt" ]] && run_traced "rm -f $tgt"
            [[ -d "$tgt" && ! -L "$tgt" ]] && run_traced "rm -fR $tgt"
            if [[ $fn =~ (kbase|templates|license_text|readlink) ]]; then
                [[ ! -d $(dirname $tgt) ]] && run_traced "mkdir -p $(dirname $tgt)"
                run_traced "ln -s $src $tgt"
            else
                [[ $ftype == f ]] && copts="" || copts="-r"
                run_traced "cp $copts $src $tgt"
                [[ ! $opts =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
                set_hashbang $tgt
            fi
        fi
    done
    # Tools PYPI installation
    [[ $pkg == "tools" ]] && continue
    x=$(find $SRCPATH/$pfn -maxdepth 3 -name __manifest__.rst 2>/dev/null|head -n 1)
    [[ -n "$x" ]] && x=$(grep -E "^\.\. .set no_pypi ." $x|grep -Eo "[0-9]")
    if [[ -z "$x" || $x -eq 0 ]]; then
        if [[ -d $SRCPATH/$pfn/$pfn ]]; then
            run_traced "cp -r $SRCPATH/$pfn/ $LOCAL_VENV/tmp/"
        else
            run_traced "mkdir $LOCAL_VENV/tmp/$pfn"
            run_traced "cp -r $SRCPATH/$pfn/ $LOCAL_VENV/tmp/$pfn/"
            run_traced "mv $LOCAL_VENV/tmp/$pfn/$pfn/setup.py $LOCAL_VENV/tmp/$pfn/setup.py"
        fi
        run_traced "pip install $LOCAL_VENV/tmp/$pfn $popts"
        if [[ $pkg == "python-plus" ]]; then
            [[ -x $PYLIB/$pfn/vem ]] && VEM="$PYLIB/$pfn/vem"
        elif [[ $pkg == "clodoo" ]]; then
            [[ -d $BINPATH/clodoo ]] && run_traced "rm -f $BINPATH/clodoo"
            [[ -d $PYLIB/$pfn ]] && run_traced "ln -s $PYLIB/$pfn $BINPATH/clodoo"
        fi
        if [[ -n $(which ${pkg}-info 2>/dev/null) ]]; then
            run_traced "${pkg}-info --copy-pkg-data"
        fi
    fi
done
[[ -d "$DSTPATH/_travis" ]] && run_traced "rm -fR $DSTPATH/_travis"
[[ -f $SRCPATH/tests/test_tools.sh ]] && run_traced "cp $SRCPATH/tests/test_tools.sh $BINPATH/test_tools.sh"
[[ -d $LOCAL_VENV/tmp ]] && run_traced "rm -fR $LOCAL_VENV/tmp"

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
    # echo -e "import sys\nif '$SRCPATH' not in sys.path:    sys.path.insert(0,'$SRCPATH')">$DSTPATH/sitecustomize.py
    echo "# SRCPATH=$SRCPATH">$DSTPATH/activate_tools
    echo "# DSTPATH=$DSTPATH">>$DSTPATH/activate_tools
    echo "[[ -f $LOCAL_VENV/bin/activate ]] && export PATH=\$PATH:$LOCAL_VENV/bin">>$DSTPATH/activate_tools
    [[ $DSTPATH != $LOCAL_VENV ]] && echo "export PATH=\$PATH:$DSTPATH">>$DSTPATH/activate_tools
    # echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -z "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH">>$DSTPATH/activate_tools
    # echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -n "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH:\$PYTHONPATH">>$DSTPATH/activate_tools
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && echo "[[ ! -d $PYLIB/zerobug/_travis || :\$PATH: =~ :$PYLIB/zerobug/_travis: ]] || export PATH=$PYLIB/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && echo "[[ ! -d $PYLIB/z0bug_odoo/travis || :\$PATH: =~ :$PYLIB/z0bug_odoo/travis: ]] || export PATH=$PYLIB/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    [[ -n $PLEASE_CMDS ]] && echo "$COMPLETE -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
    [[ -n $TRAVIS_CMDS ]] && echo "$COMPLETE -W \"$TRAVIS_CMDS\" travis">>$DSTPATH/activate_tools
fi

if [[ $opts =~ ^-.*[Ss] ]]; then
    SITECUSTOM=$DSTPATH/sitecustomize.py
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

# Final test to validate environment
[[ $opts =~ ^-.*q ]] || echo -e "# Check for $LOCAL_VENV"
for pkg in clodoo/odoorc cvt_csv_2_rst.py cvt_csv_2_xml.py gen_readme.py odoo_dependencies.py odoo_translation.py please to_pep8.py transodoo.py wget_odoo_repositories.py; do
  echo -n "."
  [[ ! -f $BINPATH/$pkg ]] && echo -e "${RED}Incomplete installation! File $pkg non found in $BINPATH!!${CLR}" && exit
done
for pkg in vem; do
  echo -n "."
  [[ ! -f $LOCAL_VENV/bin/$pkg ]] && echo -e "${RED}Incomplete installation! File $pkg non found in $LOCAL_VENV/bin/$pkg!!${CLR}" && exit
done
for pkg in kbase templates; do
  echo -n "."
  [[ ! -d $BINPATH/$pkg ]] && echo -e "${RED}Incomplete installation! Directory $pkg non found in $BINPATH!!${CLR}" && exit
done
for pkg in $PYPI_LIST; do
    echo -n "."
    pfn=$(echo "$pkg"|grep -Eo '[^!<=>\\[]*'|head -n1)
    x=$($VEM $LOCAL_VENV info $pkg 2>/dev/null|grep -E "^Location: .*")
    [[ -z "$x" ]] && echo -e "${RED}Incomplete installation! Package $pkg non installed in $LOCAL_VENV!!${CLR}" && exit
done
echo ""
[[ $opts =~ ^-.*T ]] && $BINPATH/test_tools.sh

run_traced "deactivate"
[[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null

if [[ $opts =~ ^-.*D ]]; then
    run_traced "mkdir -p $DEVELPATH"
    for pkg in $PKGS_LIST tools; do
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
        mkdir -p $HOME_DEV/pypi/$pfn
        [[ $pkg == "tools" ]] && run_traced "cp -R $SRCPATH/$pkg/* $DEVELPATH/" || run_traced "cp -R $SRCPATH/$pfn/ $DEVELPATH/$pkg/"
    done
fi
if [[ ! $opts =~ ^-.*n && $opts =~ ^-.*P ]]; then
    $(grep -q "\$HOME.*/activate_tools" $HOME/.bash_profile) && sed -e "s|\$HOME.*/activate_tools|$DSTPATH/activate_tools|" -i $HOME/.bash_profile || echo "[[ -f $DSTPATH/activate_tools ]] && . $DSTPATH/activate_tools -q" >>$HOME/.bash_profile
fi

if [[ ! $opts =~ ^-.*[gtT] ]]; then
  [[ ! $opts =~ ^-.*q ]] && echo "# Searching for git projects ..."
  for d in $(find $HOME -not -path "*/_*" -not -path "*/VME/*" -not -path "*/VENV*" -not -path "*/oca*" -not -path "*/tmp*" -name ".git" 2>/dev/null|sort); do
    run_traced "cp $SRCPATH/wok_code/pre-commit $d/hooks"
    run_traced "rm -f $d/hooks/pre-commit"
  done
fi

[[ $opts =~ ^-.*U && ! $opts =~ ^-.*q && -f $DSTPATH/egg-info/history.rst ]] && tail $DSTPATH/egg-info/history.rst
if [[ ! $opts =~ ^-.*q && ! $opts =~ ^-.*P ]]; then
    echo -e "${GREEN}--------------------------------------------------------------"
    echo -e "Zeroincombenze(R) tools successfully installed on your system."
    echo -e "In order to make available the these tools, please type:${CLR}"
    echo -e "source $DSTPATH/activate_tools\n"
    echo -e "${GREEN}If you wish to use  these tools  at the next time,  please add"
    echo -e "the following statement in your login file (.bash_profile):"
    echo -e "source $DSTPATH/activate_tools"
    echo -e "If you prefer, you can re-execute this script using  -P switch"
    echo -e "--------------------------------------------------------------${CLR}"
    echo -e "For furthermore info visit https://zeroincombenze-tools.readthedocs.io/"
fi
