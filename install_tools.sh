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
__version__=2.0.0.1

[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
complete &>/dev/null && COMPLETE="complete" || COMPLETE="# complete"
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
opts=$(echo $1 $2 $3 $4 $5 $6 $7 $8 $9 .)
if [[ $opts =~ ^-.*h ]]; then
    echo "$THIS [-h][-n][-o][-p][-P][-q][-S][-T][-v][-V]"
    echo "  -h  this help"
    echo "  -d  use development branch not master"
    echo "  -D  create the development environment"
    echo "  -f  force creation of virtual environment even if exists"
    echo "  -g  do not install hooks in git projects"
    echo "  -G  remove hooks from git projects"
    echo "  -k  keep current virtual environment if exists"
    echo "  -n  dry-run"
    echo "  -p  mkdir $HOME/devel if does not exist"
    echo "  -P  permanent environment (update ~/.bash_profile)"
    echo "  -q  quiet mode"
    echo "  -t  this script is executing in travis-ci environment"
    echo "  -T  execute regression tests"
    echo "  -U  pull from github for upgrade"
    echo "  -v  more verbose"
    echo "  -V  show version and exit"
    echo "  -2  create virtual environment with python2"
    echo -e "\n(C) 2015-2022 by zeroincombenze(R)\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
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
    local d f
    d=$(find $1 \( -type f -executable -o -name "*.py" \)|tr "\n" " ")
    for f in $d; do
      grep -Eq "^#\!.*/bin.*python[23]?$" $f &>/dev/null && run_traced "sed -E \"s|^#\!.*/bin.*python[23]?|#\!$PYTHON|\" -i $f" && chmod +x $f
    done
}

RFLIST__travis_emulator=""
RFLIST__clodoo="awsfw bck_filestore.sh clodoo.py manage_odoo.man set_worker.sh transodoo.py"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=""
RFLIST__zerobug=""
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="odoo_default_tnl.xlsx templates license_text readlink"
RFLIST__python_plus=""
RFLIST__wok_code="cvt_csv_2_xml.py generate_all_tnl gen_addons_table.py odoo_dependencies.py"
RFLIST__zerobug_odoo=""
RFLIST__odoo_score="odoo_shell.py"
RFLIST__os0=""
MOVED_FILES_RE="(cvt_csv_2_xml.py|cvt_script|dist_pkg|gen_addons_table.py|gen_readme.py|makepo_it.py|odoo_translation.py|please|please.man|please.py|run_odoo_debug|topep8|topep8.py|transodoo.py|transodoo.xlsx|travis|travisrc|vfcp|vfdiff)"
FILES_2_DELETE="addsubm.sh clodoo clodoocore.py clodoolib.py devel_tools export_db_model.py kbase oca-autopep8 odoo_default_tnl.csv please.py prjdiff replica.sh run_odoo_debug.sh set_color.sh set_odoover_confn test_tools.sh topep8.py to_oia.2p8 transodoo.csv upd_oemod.py venv_mgr venv_mgr.man wok_doc wok_doc.py z0lib z0lib.py z0librun.py"

SRCPATH=
DSTPATH=
RED="\e[31m"
GREEN="\e[32m"
CLR="\e[0m"

# [[ $opts =~ ^-.*t ]] && HOME=$(readlink -e $(dirname $0)/..)
[[ $opts =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
[[ -d $TDIR/clodoo && -d $TDIR/wok_code && -d $TDIR/z0lib ]] && SRCPATH=$TDIR
[[ -z "$SRCPATH" && -d $TDIR/../tools && -d $TDIR/../z0lib ]] && SRCPATH=$(readlink -f $TDIR/..)
[[ -z "$SRCPATH" && -d $HOME/odoo/tools ]] && SRCPATH=$HOME/odoo/tools
[[ -z "$SRCPATH" && -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ -z "$SRCPATH" || ! -d $SRCPATH || ! -d $SRCPATH/z0lib ]] && echo "# Environment not found! No tools path found" && exit 1

[[ ! $opts =~ ^-.*p && ! $opts =~ ^-.*t && -n $HOME_DEVEL && -f $HOME_DEVEL ]] && DSTPATH=$HOME_DEVEL
[[ -z "$DSTPATH" && $(basename $SRCPATH) =~ (pypi|tools) ]] && DSTPATH="$(readlink -f $(dirname $SRCPATH)/devel)"
[[ $(basename $(dirname $SRCPATH)) == "devel" ]] && DSTPATH="$(readlink -f $(dirname $(dirname $SRCPATH))/devel)"
[[ -z "$DSTPATH" && -d $HOME/odoo/devel ]] && DSTPATH="$HOME/odoo/devel"
[[ -z "$DSTPATH" && -d $HOME/devel ]] && DSTPATH="$HOME/devel"
[[ -z "$DSTPATH" && -d $HOME/devel ]] && DSTPATH="$HOME/devel"
LOCAL_VENV="$DSTPATH/venv"
[[ $DSTPATH != $LOCAL_VENV && ! -d $DSTPATH && ! $opts =~ ^-.*p ]] && run_traced "mkdir -p $DSTPATH"
[[ -z "$DSTPATH" ]] && echo "# Environment not found! Please use -p switch" && exit 1
DEVELPATH="$(readlink $DSTPATH/pypi)"

if [[ ! $opts =~ ^-.*t && ! $opts =~ ^-.*D && -d $SRCPATH/.git ]]; then
    [[ $opts =~ ^-.*d && ! $opts =~ ^-.*q ]] && echo "# Use development branch" && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep --color=never -Eo "[a-zA-Z0-9_-]+") != "devel" ]] && git stash -q && git checkout devel -f
    [[ ! $opts =~ ^-.*d ]] && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep --color=never -Eo "[a-zA-Z0-9_-]+") != "master" ]] && git stash -q && git checkout master -fq
    [[ $opts =~ ^-.*U ]] && git stash -q && pull_n_run "$SRCPATH" "$0" "$opts"
fi
[[ $opts =~ ^-.*v && ! $opts =~ ^-.*D ]] && echo -e "${GREEN}# Installing tools from $SRCPATH to $DSTPATH ...${CLR}"
[[ $opts =~ ^-.*v && $opts =~ ^-.*D ]] && echo -e "${GREEN}# Creating development environment $DEVELPATH ...${CLR}"
[[ $opts =~ ^-.*v ]] && echo "# Virtual environment is $LOCAL_VENV ..."
[[ $opts =~ ^-.*n ]] || find $SRCPATH -name "*.pyc" -delete
[[ $opts =~ ^-.*o ]] && echo -e "${RED}# WARNING! The switch -o is not more supported!${CLR}"
[[ -x $SRCPATH/python_plus/python_plus/vem ]] && VEM="$SRCPATH/python_plus/python_plus/vem"
[[ -x $SRCPATH/python_plus/python_plus/scripts/vem.sh ]] && VEM="$SRCPATH/python_plus/python_plus/scripts/vem.sh"
[[ -z "$VEM" && -x $SRCPATH/python_plus/vem ]] && VEM="$SRCPATH/python_plus/vem"
[[ -z "$VEM" && -x $SRCPATH/python_plus/scripts/vem.sh ]] && VEM="$SRCPATH/python_plus/scripts/vem.sh"
if [[ -z "$VEM" ]]; then
    echo -e "${RED}# Invalid environment! Command vem not found!${CLR}"
    echo ""
    exit 1
fi

if [[ ! $opts =~ ^-.*k ]]; then
    for p in bin lib include; do
        [[ $DSTPATH != $LOCAL_VENV && -d $DSTPATH/$p ]] && run_traced "rm -fR $DSTPATH/$p"
    done
fi

if [[ -x $LOCAL_VENV/python ]]; then
  x=$($LOCAL_VENV/python --version 2>&1 | grep --color=never -Eo "[0-9]" | head -n1)
  [[ ! $opts =~ ^-.*2 && x -eq 2 ]] && opts="${opts} -f"
  [[ $opts =~ ^-.*2 && x -ne 2 ]] && opts="${opts} -f"
fi

[[ $opts =~ ^-.*2 ]] && PYVER=$(python2 --version 2>&1 | grep --color=never -Eo "[0-9]\.[0-9]+" | head -n1) || PYVER=$(python3 --version 2>&1 | grep --color=never -Eo "[0-9]\.[0-9]+" | head -n1)
[[ -z $PYVER && $opts =~ ^-.*2 ]] && PYVER=$(python --version 2>&1 | grep --color=never -Eo "2\.[0-9]+" | head -n1)
[[ -z $PYVER && ! $opts =~ ^-.*2 ]] && PYVER=$(python --version 2>&1 | grep --color=never -Eo "3\.[0-9]+" | head -n1)
[[ -z $PYVER ]] && echo "No python not found in path|" && exit 1
if [[ ! $opts =~ ^-.*k && ( $DSTPATH == $LOCAL_VENV || $opts =~ ^-.*[fU] || ! -d $LOCAL_VENV/lib || ! -d $DSTPATH/venv/bin || ! -d $DSTPATH/bin ) ]]; then
    x="-iDBB"
    [[ $opts =~ ^-.*q ]] && x="-qiDBB"
    [[ $opts =~ ^-.*v ]] && x="-viDBB"
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && x="${x}t"
    run_traced "$VEM create $LOCAL_VENV -p$PYVER $x -f"
    [[ $? -ne 0 ]] && echo -e "${RED}# Error creating Tools virtual environment!${CLR}" && exit 1
    [[ ! -d $LOCAL_VENV/bin || ! -d $LOCAL_VENV/lib ]] && echo -e "${RED}# Incomplete Tools virtual environment!${CLR}" && exit 1
    [[ -d $HOME/.cache/pip && $opts =~ ^-.*p ]] && run_traced "rm -fR $HOME/.cache/pip"
    [[ ! -d $LOCAL_VENV/bin/man/man8 ]] && run_traced "mkdir -p $LOCAL_VENV/bin/man/man8"
fi

[[ $opts =~ ^-.*n ]] || find $DSTPATH -not -path "*/.*/*" -name "*.pyc" -delete
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
PKGS_LIST="z0lib os0 python-plus clodoo lisa odoo_score travis_emulator wok_code zerobug z0bug-odoo zar"
BINPATH="$LOCAL_VENV/bin"
PIPVER=$(pip --version | grep --color=never -Eo '[0-9]+' | head -n1)
PYVER=$($PYTHON --version 2>&1 | grep --color=never -Eo "[0-9]" | head -n1)
popts="--disable-pip-version-check --no-python-version-warning"
[[ $PIPVER -gt 18 ]] && popts="$popts --no-warn-conflicts"
[[ $PIPVER -eq 19 ]] && popts="$popts --use-feature=2020-resolver"
[[ $PIPVER -eq 21 ]] && popts="$popts --use-feature=in-tree-build"
[[ $opts =~ ^-.*q ]] && popts="$popts -q"
[[ $opts =~ ^-.*v ]] && echo "# $(which pip).$PIPVER $popts ..."
[[ -d $DSTPATH/tmp ]] && rm -fR $DSTPATH/tmp
[[ -d $LOCAL_VENV/tmp ]] && rm -fR $LOCAL_VENV/tmp
[[ ! -d $LOCAL_VENV/tmp ]] && mkdir -p $LOCAL_VENV/tmp

if [[ ! $opts =~ ^-.*k ]]; then
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
          [[ -f $SRCPATH/$pfn/$pfn/scripts/setup.info ]] && srcdir="$SRCPATH/$pfn/$pfn" || srcdir="$SRCPATH/$pfn"
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
        [[ -n "$x" ]] && x=$(grep -E "^\.\. .set no_pypi ." $x|grep --color=never -Eo "[0-9]")
        if [[ -z "$x" || $x -eq 0 ]]; then
            if [[ -f $SRCPATH/$pfn/$pfn/scripts/setup.info && -f $SRCPATH/$pfn/$pfn/__init__.py ]]; then
                run_traced "cp -r $SRCPATH/$pfn/ $LOCAL_VENV/tmp/"
            else
                run_traced "mkdir $LOCAL_VENV/tmp/$pfn"
                run_traced "cp -r $SRCPATH/$pfn/ $LOCAL_VENV/tmp/$pfn/"
                run_traced "mv $LOCAL_VENV/tmp/$pfn/$pfn/setup.py $LOCAL_VENV/tmp/$pfn/setup.py"
            fi
            run_traced "pip install $LOCAL_VENV/tmp/$pfn $popts"
            if [[ $pkg =~ (python-plus|python_plus) ]]; then
                [[ -x $PYLIB/$pfn/vem ]] && VEM="$PYLIB/$pfn/vem"
            elif [[ $pkg == "clodoo" ]]; then
                [[ -d $BINPATH/clodoo ]] && run_traced "rm -f $BINPATH/clodoo"
                [[ -d $PYLIB/$pfn ]] && run_traced "ln -s $PYLIB/$pfn $BINPATH/clodoo"
            elif [[ $pkg == "zerobug" ]]; then
              set_hashbang $PYLIB/$pfn/_travis
            elif [[ $pkg =~ (z0bug-odoo|z0bug_odoo) ]]; then
              set_hashbang $PYLIB/$pfn/travis
            fi
            if [[ -n $(which ${pkg}-info 2>/dev/null) ]]; then
                run_traced "${pkg}-info --copy-pkg-data"
            fi
        fi
    done
fi
if [[ -f $BINPATH/please ]]; then
    PLEASE_CMDS=$(grep "^HLPCMDLIST=" $BINPATH/please|awk -F= '{print $2}'|tr -d '"')
    PLEASE_CMDS="${PLEASE_CMDS//|/ }"
fi
if [[ -f $BINPATH/travis ]]; then
    TRAVIS_CMDS=$(grep "^ACTIONS=" $BINPATH/travis|awk -F= '{print $2}'|tr -d '"')
    TRAVIS_CMDS=${TRAVIS_CMDS:1: -1}
    TRAVIS_CMDS="${TRAVIS_CMDS//|/ }"
fi
[[ ! $opts =~ ^-.*k && -d "$DSTPATH/_travis" ]] && run_traced "rm -fR $DSTPATH/_travis"
[[ ! $opts =~ ^-.*k && -f $SRCPATH/tests/test_tools.sh ]] && run_traced "cp $SRCPATH/tests/test_tools.sh $BINPATH/test_tools.sh"
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
    echo "# SRCPATH=$SRCPATH">$DSTPATH/activate_tools
    echo "# DSTPATH=$DSTPATH">>$DSTPATH/activate_tools
    echo "HOME_DEVEL=\"$DSTPATH\"">>$DSTPATH/activate_tools
    echo "BINDIR=\"$LOCAL_VENV/bin\"">>$DSTPATH/activate_tools
    echo "ACTIVATE=\"\$BINDIR/activate\"">>$DSTPATH/activate_tools
    echo "PYLIB=\"$PYLIB\"">>$DSTPATH/activate_tools
    echo "opts=\$(echo $1 $2 $3 $4 $5 $6 $7 $8 $9 .)">>$DSTPATH/activate_tools
    echo "[[ \$opts =~ ^-.*h ]] && echo \$0 [-f][-t] && exit 0">>$DSTPATH/activate_tools
    if [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]]; then
      echo "[[ -d \$PYLIB/zerobug/_travis ]] && echo \":\$PATH:\"|grep -qv \":\$PYLIB/zerobug/_travis:\" && export PATH=\$PYLIB/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
      echo "[[ -d \$PYLIB/z0bug_odoo/travis ]] && echo \":\$PATH:\"|grep -qv \"\$PYLIB/z0bug_odoo/travis:\" && export PATH=\$PYLIB/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    else
      echo "[[ \$opts =~ ^-.*t && -d \$PYLIB/zerobug/_travis ]] && echo \":\$PATH:\"|grep -qv \":\$PYLIB/zerobug/_travis:\" && export PATH=\$PYLIB/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
      echo "[[ \$opts =~ ^-.*t && -d \$PYLIB/z0bug_odoo/travis ]] && echo \":\$PATH:\"|grep -qv \"\$PYLIB/z0bug_odoo/travis:\" && export PATH=\$PYLIB/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    fi
    for fn in codecov coverage coverage3 coveralls flake8 pylint; do
      echo "[[ ! -L \$PYLIB/zerobug/_travis/$fn ]] && ln -s \$BINDIR/$fn \$PYLIB/zerobug/_travis/$fn">>$DSTPATH/activate_tools
    done
    echo "[[ -f \$ACTIVATE ]] && echo \":\$PATH:\"|grep -qv \":\$BINDIR:\" && [[ ! \$opts =~ ^-.*f ]] && export PATH=\$PATH:\$BINDIR">>$DSTPATH/activate_tools
    echo "[[ -f \$ACTIVATE ]] && echo \":\$PATH:\"|grep -qv \":\$BINDIR:\" && [[ \$opts =~ ^-.*f ]] && export PATH=\$(echo \$PATH|sed -E \"s|:\$BINDIR|:|\")">>$DSTPATH/activate_tools
    echo "[[ -f \$ACTIVATE ]] && echo \"+\$PATH:\"|grep -qv \"+\$BINDIR:\" && [[ \$opts =~ ^-.*f ]] && export PATH=\$BINDIR:\$PATH">>$DSTPATH/activate_tools
    [[ -n $PLEASE_CMDS ]] && echo "$COMPLETE -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
    [[ -n $TRAVIS_CMDS ]] && echo "$COMPLETE -W \"$TRAVIS_CMDS\" travis">>$DSTPATH/activate_tools
fi

# OCA tools
if [[ $PYVER -eq 3 ]]; then
    run_traced "cd $DSTPATH"
    [[ $opts =~ ^-.*v ]] && x="" || x="--quiet"
    if [[ ! $opts =~ ^-.*t ]]; then
        [[ -d $DSTPATH/maintainer-tools ]] && rm -fR $DSTPATH/maintainer-tools
        run_traced "git clone https://github.com/OCA/maintainer-tools.git"
        if [[ -d $DSTPATH/maintainer-tools ]]; then
            run_traced "cd $DSTPATH/maintainer-tools"
            run_traced "$PYTHON setup.py $x install"
            for pkg in black pre-commit pyupgrade flake8-bugbear; do
                run_traced "pip install $pkg $popts"
            done
        fi
        run_traced "git clone $x https://github.com/OCA/odoo-module-migrator.git"
        for pkg in sphinx sphinx_rtd_theme; do
            run_traced "pip install $pkg $popts"
        done
    fi
    run_traced "git clone $x https://github.com/OCA/maintainer-quality-tools.git"
fi

# Final test to validate environment
[[ $opts =~ ^-.*q ]] || echo -e "# Check for $LOCAL_VENV"
for pkg in odoorc clodoo/odoorc cvt_csv_2_xml.py gen_readme.py odoo_dependencies.py odoo_translation.py please to_pep8.py transodoo.py wget_odoo_repositories.py; do
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
for pkg in babel lxml python-magic pyyaml python-plus z0lib z0bug-odoo zerobug; do
    echo -n "."
    pfn=$(echo "$pkg"| grep --color=never -Eo '[^!<=>\\[]*'|head -n1)
    x=$($VEM $LOCAL_VENV info $pkg 2>/dev/null|grep -E "^Location: .*")
    [[ -z "$x" ]] && echo -e "${RED}Incomplete installation! Package $pkg non installed in $LOCAL_VENV!!${CLR}" && exit
done
echo ""
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

if [[ ! $opts =~ ^-.*[gt] ]]; then
    . $DSTPATH/venv/bin/clodoo/odoorc
    [[ ! $opts =~ ^-.*q ]] && echo "# Searching for git projects ..."
    for d in $(find $HOME -not -path "*/.cache/*" -not -path "*/_*" -not -path "*/VME/*" -not -path "*/VENV*" -not -path "*/oca*" -not -path "*/tmp*" -name ".git" 2>/dev/null|sort); do
        d=$(readlink -f $d/..)
        run_traced "cd $d"
        v=$(build_odoo_param MAJVER $d)
        g=$(build_odoo_param GIT_ORGID $d)
        [[ $g == "oca" ]] && continue
        act="install"
        [[ ! -f $d/.travis.yml ]]  && continue
        r=$(build_odoo_param REPOS $d)
        [[ $opts =~ ^-.*G && -f $d/.git/hooks/pre-commit ]] && act="autoupdate" && run_traced "rm -f $d/.git/hooks/pre-commit" && run_traced "pre-commit uninstall"
        [[ $opts =~ ^-.*G && $d/.pre-commit-config.yaml ]] && run_traced "rm -f $d/.pre-commit-config.yaml"
        [[ $r == "OCB" ]] && continue
        [[ $PYVER -ne 3 || ( $opts =~ ^-.*G && ! $opts =~ ^-.*f.*G && ! $opts =~ ^-.*G.*f ) || -f $d/.pre-commit-config.yaml ]] && continue
        for fn in copier-answers.yml editorconfig eslintrc.yml flake8 isort.cfg pre-commit-config.yaml prettierrc.yml pylintrc pylintrc-mandatory; do
            [[ $fn == "pre-commit-config.yaml" && $v -le 10 ]] && run_traced "cp $SRCPATH/templates/pre-commit-config2.yaml $d/.$fn" || run_traced "cp $SRCPATH/templates/$fn $d/.$fn"
        done
        v=$(build_odoo_param FULLVER $d)
        run_traced "sed -E \"s|^odoo_version:.*|odoo_version: $v|\" -i $d/.copier-answers.yml"
        run_traced "sed -E \"s|^valid_odoo_versions=.*|valid_odoo_versions=$v|\" -i $d/.pylintrc"
        run_traced "sed -E \"s|^valid_odoo_versions=.*|valid_odoo_versions=$v|\" -i $d/.pylintrc-mandatory"
        n="$g"
        [[ $g == "zero" ]] && n="Zeroincombenze(R)"
        [[ $g == "librerp" ]] && n="Librerp enterprise network"
        run_traced "sed -E \"s|^org_name:.*|org_name: $n|\" -i $d/.copier-answers.yml"
        n=$(build_odoo_param GIT_ORGNM $d)
        run_traced "sed -E \"s|^org_slug:.*|org_slug: $n|\" -i $d/.copier-answers.yml"
        n=$(basename $d)
        run_traced "sed -E \"s|^repo_name:.*|repo_name: $n|\" -i $d/.copier-answers.yml"
        run_traced "sed -E \"s|^repo_slug:.*|repo_slug: $n|\" -i $d/.copier-answers.yml"
        n=$(build_odoo_param GIT_ORG $d)
        run_traced "sed -E \"s|^repo_website:.*|repo_website: $n|\" -i $d/.copier-answers.yml"
        run_traced "pre-commit install"
    done
fi

[[ $opts =~ ^-.*T ]] && $BINPATH/test_tools.sh

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
