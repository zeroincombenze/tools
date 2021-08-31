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
__version__=1.0.6.1

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
    echo "  -o  compatibility old mode (exec dir in $HOME/dev, deprecated)"
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
    echo "  -Z  reinstall all from zero"
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
RFLIST__clodoo="awsfw bck_filestore.sh clodoo.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog odoo_skin.sh set_color.sh set_worker.sh transodoo.py transodoo.xlsx"
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

[[ $opts =~ ^-.*t ]] && HOME=$($READLINK -e $(dirname $0)/..)
[[ $opts =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
[[ $opts =~ ^-.*o ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
[[ -z "$SRCPATH" && -d $TDIR/../tools ]] && SRCPATH=$($READLINK -f $TDIR/../tools)
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
if [[ $opts =~ ^-.*Z ]]; then
  echo "# Reinstall tools from ZERO!!"
  run_traced "cd $SRCPATH/.."
  run_traced "rm -fR $SRCPATH/../tools"
  run_traced "git clone https://github.com/zeroincombenze/tools.git"
  [[ ! -d $HOME/tools ]] && echo "ERROR!" && exit 1
  run_traced "cd $SRCPATH"
fi
[[ -f $DSTPATH/activate_tools ]] && m1=$(stat -c %Y $DSTPATH/activate_tools) || m1=0
m2=$(stat -c %Y $0)
[[ $m1 -lt $m2 && ! $opts =~ ^-.*f ]] && opts="-f ${opts}"
if [[ ! $opts =~ ^-.*t ]]; then
    [[ $opts =~ ^-.*d ]] && echo "# Use development branch" && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "devel" ]] && git stash -q && git checkout devel -f
    [[ ! $opts =~ ^-.*d ]] && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "master" ]] && git stash -q && git checkout master -fq
    [[ $opts =~ ^-.*U ]] && pull_n_run "$SRCPATH" "$0" "$opts"
fi
[[ $opts =~ ^-.*v ]] && echo "# Installing tools from $SRCPATH to $DSTPATH ..."
[[ $opts =~ ^-.*n ]] || find $SRCPATH $DSTPATH -name "*.pyc" -delete
[[ $opts =~ ^-.*o ]] && echo "# WARNING! The switch -o is deprecated and will be removed early!"

PLEASE_CMDS=""
TRAVIS_CMDS=""
PKGS_LIST="clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
for pkg in $PKGS_LIST tools; do
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
    l="RFLIST__$pfn"
    flist=${!l}
    [[ $opts =~ ^-.*v ]] && echo "[$pkg=$flist]"
    for fn in $flist; do
        if [[ $fn == "." ]]; then
            src="$SRCPATH/${pfn}"
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
        elif [[ $pkg == "tools" ]]; then
            src="$SRCPATH/$fn"
            tgt="$DSTPATH/$fn"
            [[ -d "$SRCPATH/$fn" ]] && ftype=d || ftype=f
        else
            src="$SRCPATH/${pfn}/$fn"
            tgt="$DSTPATH/$fn"
            [[ -d "$SRCPATH/${pfn}/$fn" ]] && ftype=d || ftype=f
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
        elif [[ ! -e "$tgt" || -L "$tgt" || $opts =~ ^-.*[fpU] || $fn =~ $MOVED_FILES_RE ]]; then
            [[ -L "$tgt" ]] && run_traced "rm -f $tgt"
            [[ -d "$tgt" ]] && run_traced "rm -fR $tgt"
            if [[ $fn =~ (kbase|templates|license_text|readlink) ]]; then
                [[ ! -d $(dirname $tgt) ]] && run_traced "mkdir -p $(dirname $tgt)"
                run_traced "ln -s $src $tgt"
            elif [[ ! -e "$tgt" || $opts =~ ^-.*[fpU] ]]; then
                [[ $ftype == f ]] && copts="" || copts="-r"
                run_traced "cp $copts $src $tgt"
                [[ ! $opts =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
            fi
        fi
    done
done

[[ -d "$DSTPATH/_travis" ]] && run_traced "rm -fR $DSTPATH/_travis"
run_traced "cp $SRCPATH/tests/test_tools.sh $DSTPATH/test_tools.sh"
if [[ -f $HOME/maintainers-tools/env/bin/oca-autopep8 ]]; then
    tgt=$DSTPATH/oca-autopep8
    if [[ ! -L "$tgt" || $opts =~ ^-.*[fpU] ]]; then
        if [[ -L "$tgt" || -f "$tgt" ]]; then
            run_traced "rm -f $tgt"
            [[ ! $opts =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
        fi
        run_traced "ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt"
    fi
fi

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
if [[ $opts =~ ^-.*[Ss] ]]; then
    [[ ! $opts =~ ^-.*o ]] && SITECUSTOM=$HOME/devel/sitecustomize.py
    [[ $opts =~ ^-.*o ]] && SITECUSTOM=$HOME/dev/sitecustomize.py
    PYLIB=$(dirname $(pip --version 2>/dev/null|grep -Eo "from [^ ]+"|awk '{print $2}') 2>/dev/null)
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

run_traced "source $DSTPATH/activate_tools"
if [[ $opts =~ ^-.*[fU] || ! -d $DSTPATH/venv ]]; then
    x="-iDBB"
    [[ $opts =~ ^-.*q ]] && x="-qiDBB"
    [[ $opts =~ ^-.*v ]] && x="-vvviDBB"
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && x="${x}t"
    run_traced "vem create $DSTPATH/venv -p2.7 $x -f"
    [[ $? -ne 0 ]] && echo "# Error creating Tools virtual environment!" && exit 1
fi
[[ $PATH =~ $DSTPATH/venv/bin ]] || export PATH="$DSTPATH/venv/bin:$PATH"
PYTHON=""
PYTHON3=""
[[ -x $DSTPATH/venv/bin/python ]] && PYTHON=$DSTPATH/venv/bin/python
[[ -x $DSTPATH/venv/bin/python2 ]] && PYTHON=$DSTPATH/venv/bin/python2
[[ -x $DSTPATH/venv/bin/python3 ]] && PYTHON3=$DSTPATH/venv/bin/python3

path="$DSTPATH/*"
[[ $opts =~ ^-.*[fU] && -d $DSTPATH/venv ]] && path=$(find $SRCPATH \( -type f -executable -o -name "*.py" \)|tr "\n" " ")
for f in $path; do
    grep -q "^#\!.*/bin.*python3$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python3|#\!$PYTHON3|\" $f" && chmod +x $f
    grep -q "^#\!.*/bin.*python2$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python2|#\!$PYTHON|\" $f" && chmod +x $f
    grep -q "^#\!.*/bin.*python$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python|#\!$PYTHON|\" $f" && chmod +x $f
done
if [[ $opts =~ ^-.*[fU] || ! -d $DSTPATH/venv ]]; then
    # Please do not change package list order
    for pkg in configparser odoorpc oerplib babel jsonlib lxml unidecode openpyxl pyyaml z0lib zerobug clodoo; do
        [[ -d $HOME_DEV/pypi/$pkg/$pkg ]] && run_traced "vem $DSTPATH/venv install $pkg -qBB" || run_traced "vem $DSTPATH/venv install $pkg"
    done
    [[ -d $DSTPATH/clodoo ]] && run_traced "rm -f $DSTPATH/clodoo"
    x=$(vem $DSTPATH/venv info clodoo|grep -E "Location"|cut -d' ' -f2)/clodoo
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
[[ $opts =~ ^-.*T ]] && $DSTPATH/test_tools.sh
[[ $opts =~ ^-.*U && -f $DSTPATH/egg-info/history.rst ]] && tail $DSTPATH/egg-info/history.rst
if [[ ! $opts =~ ^-.*[gt] ]]; then
  [[ ! $opts =~ ^-.*q ]] && echo "# Searching for git projects ..."
  for d in $(find $HOME -not -path "*/_*" -not -path "*/VME/*" -not -path "*/VENV*" -not -path "*/oca*" -not -path "*/tmp*" -name ".git" 2>/dev/null|sort); do
    run_traced "cp $SRCPATH/wok_code/pre-commit $d/hooks"
    run_traced "rm -f $d/hooks/pre-commit"
  done
fi
if [[ ! $opts =~ ^-.*q && ! $opts =~ ^-.*P ]]; then
    echo "------------------------------------------------------------"
    echo "If you wish to use these tools at the next time,  please add"
    echo "the following statement in your login file (.bash_profile)"
    echo "source $DSTPATH/activate_tools"
    echo "If you prefer, you can re-execute this script with -P switch"
    echo "------------------------------------------------------------"
    echo "For furthermore info visit https://zeroincombenze-tools.readthedocs.io/"
fi
