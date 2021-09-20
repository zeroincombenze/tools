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
__version__=1.0.6

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
    # echo "  -p  mkdir $HOME/dev[el] if does not exist"
    echo "  -P  permanent environment (update ~/.bash_profile)"
    echo "  -q  quiet mode"
    echo "  -s  store sitecustomize.py in python path (you must have privileges)"
    echo "  -S  store sitecustomize.py in python path (you must have privileges)"
    echo "  -t  this script is executing in travis-ci environment"
    echo "  -T  execute regression tests"
    echo "  -U  pull from github for upgrade"
    echo "  -v  more verbose"
    echo "  -V  show version and exit"
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

set_python_hashbang() {
    local t=$(file -b --mime-type $1)
    [[ $t != "application/x-sharedlib" && -n "$PYTHON3" ]] && grep -q "^#\!.*/bin.*python3$" $1 &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python3|#\!$PYTHON3|\" $1" && chmod +x $1
    [[ $t != "application/x-sharedlib" && -n "$PYTHON" ]] && grep -q "^#\!.*/bin.*python2$" $1 &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python2|#\!$PYTHON|\" $1" && chmod +x $1
    [[ $t != "application/x-sharedlib" && -n "$PYTHON" ]] && grep -q "^#\!.*/bin.*python$" $1 &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python|#\!$PYTHON|\" $1" && chmod +x $1
}

pip_install_local() {
    # pip_install(pkg)
    local fn pkg v x
    pkg=$1
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
    [[ -d $PYPATH/$fn && ! -L $PYPATH/$fn ]] && run_traced "rm -fR $PYPATH/$fn"
    v=$(grep "^ *version *=" $SRCPATH/$fn/setup.py|head -n1|cut -f2 -d=|grep -Eo "[0-9.]+")
    x=$(ls -d $PYPATH/${fn}-*dist-info 2>/dev/null|grep -E "${fn}-[0-9.]*dist-info")
    [[ -n $x && $x != $PYPATH/${fn}-${v}.dist-info ]] && run_traced "mv $x $PYPATH/${fn}-${v}.dist-info"
    if [[ ! -d $PYPATH/${fn}-${v}.dist-info ]]; then
      run_traced "mkdir $PYPATH/${fn}-${v}.dist-info"
      for d in INSTALLER METADATA RECORD REQUESTED top_level.txt WHEEL; do
        run_traced "touch $PYPATH/${fn}-${v}.dist-info/$d"
      done
    fi
    [[ -L $PYPATH/$fn ]] && run_traced "rm -f $PYPATH/$fn"
    run_traced "cp -r $SRCPATH/$fn/ $PYPATH/"
}

SRCPATH=
DSTPATH=
RED="\e[31m"
GREEN="\e[32m"
CLR="\e[0m"

[[ $opts =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
[[ -d $TDIR/clodoo && -d $TDIR/wok_code && -d $TDIR/z0lib ]] && SRCPATH=$TDIR
[[ -z "$SRCPATH" && -d $TDIR/../tools ]] && SRCPATH=$(readlink -f $TDIR/..)
[[ -z "$SRCPATH" && -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ ! $opts =~ ^-.*t && -n "$TRAVIS_BUILD_DIR" ]] && SRCPATH=$TRAVIS_BUILD_DIR
if [[ -z "$SRCPATH" ]]; then
    echo -e "${RED}# Invalid environment!${CLR}"
    echo ""
    $0 -h
    exit 1
fi
DSTPATH="$(readlink -f $(dirname $SRCPATH)/venv_tools)"
if [[ ! $opts =~ ^-.*t && -d $SRCPATH/.git ]]; then
    [[ $opts =~ ^-.*d ]] && echo "# Use development branch" && cd $SRCPATH && [[ $(git branch --list|grep "^\* "|grep -Eo "[a-zA-Z0-9_-]+") != "devel" ]] && git stash -q && git checkout devel -f
    [[ ! $opts =~ ^-.*d ]] && cd $SRCPATH && [[ $(git branch --show-current) != "master" ]] && git stash -q && git checkout master -fq
    [[ $opts =~ ^-.*U ]] && pull_n_run "$SRCPATH" "$0" "$opts"
fi
[[ $opts =~ ^-.*v ]] && echo "# Installing tools from $SRCPATH to $DSTPATH ..."
[[ $opts =~ ^-.*n ]] || find $SRCPATH -name "*.pyc" -delete
[[ $opts =~ ^-.*o ]] && echo -e "${RED}# WARNING! The switch -o is not more supported!${CLR}"

[[ -x $SRCPATH/python_plus/python_plus/vem.sh ]] && VEM="$SRCPATH/python_plus/python_plus/vem.sh"
[[ -x $SRCPATH/python_plus/vem.sh ]] && VEM="$SRCPATH/python_plus/vem.sh"
if [[ -z "$VEM" ]]; then
    echo -e "${RED}# Invalid environment! Command vem not found!${CLR}"
    echo ""
    exit 1
fi
if [[ $opts =~ ^-.*[fU] || ! -d $DSTPATH/lib || ! -d $DSTPATH/bin ]]; then
    x="-iDBB"
    [[ $opts =~ ^-.*q ]] && x="-qiDBB"
    [[ $opts =~ ^-.*v ]] && x="-viDBB"
    [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && x="${x}t"
    run_traced "$VEM create $DSTPATH -p3.7 $x -f"
    [[ $? -ne 0 || ! -d $DSTPATH/bin || ! -d $DSTPATH/lib ]] && echo -e "${RED}# Error creating Tools virtual environment!${CLR}" && exit 1
    [[ -d $DSTPATH/venv ]] && run_traced "rm -fR $DSTPATH/venv"
fi
run_traced "pushd $DSTPATH &>/dev/null"
run_traced ". bin/activate"
run_traced "popd &>/dev/null"

PYPATH=$(find $DSTPATH/lib -type d -name site-packages)
PLEASE_CMDS=""
TRAVIS_CMDS=""
PKGS_LIST="clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
BINPATH="$DSTPATH/bin"

[[ ! -d $DSTPATH/tmp ]] && mkdir -p $DSTPATH/tmp
for pkg in $PKGS_LIST; do
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg//-/_} || pfn=$pkg
    if [[ ! -d $SRCPATH/$pfn ]]; then
        echo -e "${RED}# Invalid environment! Source dir $SRCPATH/$pfn not found!${CLR}"
        echo ""
        exit 1
    fi
    if [[ -d $SRCPATH/$pfn/$pfn ]]; then
        run_traced "cp -r $SRCPATH/$pfn/ $DSTPATH/tmp/"
    else
        run_traced "mkdir $DSTPATH/tmp/$pfn"
        run_traced "cp -r $SRCPATH/$pfn/ $DSTPATH/tmp/$pfn/"
        run_traced "mv $DSTPATH/tmp/$pfn/$pfn/setup.py $DSTPATH/tmp/$pfn/setup.py"
    fi
    run_traced "pip install $DSTPATH/tmp/$pfn --use-feature=in-tree-build"
    run_traced "${pfn}-info --copy-pkg-data"
done
[[ ! -d $DSTPATH/tmp ]] && run_trace "rm -fR $DSTPATH/tmp"

if [[ ! $opts =~ ^-.*n ]]; then
    echo -e "import sys\nif '$SRCPATH' not in sys.path:    sys.path.insert(0,'$SRCPATH')">$DSTPATH/sitecustomize.py
    echo "SRCPATH=$SRCPATH">$DSTPATH/activate_tools
    echo "DSTPATH=$DSTPATH">>$DSTPATH/activate_tools
    echo "[[ -f \$DSTPATH/bin/activate ]] && export PATH=\$PATH:\$DSTPATH/bin">>$DSTPATH/activate_tools
    # echo "[[ ( ! -d \$SRCPATH || :\$PYTHONPATH: =~ :\$SRCPATH: ) && -z "\$PYTHONPATH" ]] || export PYTHONPATH=\$SRCPATH">>$DSTPATH/activate_tools
    # echo "[[ ( ! -d \$SRCPATH || :\$PYTHONPATH: =~ :\$SRCPATH: ) && -n "\$PYTHONPATH" ]] || export PYTHONPATH=\$SRCPATH:\$PYTHONPATH">>$DSTPATH/activate_tools
    # echo "[[ ! -d \$DSTPATH || :\$PATH: =~ :\$DSTPATH: ]] || export PATH=\$DSTPATH:\$PATH">>$DSTPATH/activate_tools
    # [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && echo "[[ ! -d $SRCPATH/zerobug/_travis || :\$PATH: =~ :$SRCPATH/zerobug/_travis: ]] || export PATH=$SRCPATH/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
    # [[ $opts =~ ^-.*t || $TRAVIS =~ (true|false|emulate) ]] && echo "[[ ! -d $SRCPATH/z0bug_odoo/travis || :\$PATH: =~ :$SRCPATH/z0bug_odoo/travis: ]] || export PATH=$SRCPATH/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    # [[ -n $PLEASE_CMDS ]] && echo "$COMPLETE -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
    # [[ -n $TRAVIS_CMDS ]] && echo "$COMPLETE -W \"$TRAVIS_CMDS\" travis">>$DSTPATH/activate_tools
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
[[ $PATH =~ $BINPATH ]] || export PATH="$PATH:$BINPATH"

if [[ ! $opts =~ ^-.*n && $opts =~ ^-.*D ]]; then
    mkdir -p $DSTPATH/pypi
    for pkg in $PKGS_LIST tools; do
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
        mkdir -p $DSTPATH/pypi/$pfn
        [[ $pkg == "tools" ]] && rsync -avzb $SRCPATH/$pkg/ $DSTPATH/pypi/$pkg/ || rsync -avzb $SRCPATH/$pfn/ $DSTPATH/pypi/$pfn/$pfn/
    done
fi
if [[ ! $opts =~ ^-.*n && $opts =~ ^-.*P ]]; then
    $(grep -q "\$HOME/dev[el]*/activate_tools" $HOME/.bash_profile) && sed -e "s|\$HOME/dev[el]*/activate_tools|\$HOME/devel/activate_tools|" -i $HOME/.bash_profile || echo "[[ -f $HOME/devel/activate_tools ]] && . $HOME/devel/activate_tools -q" >>$HOME/.bash_profile
fi
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
    echo -e "${GREEN}------------------------------------------------------------"
    echo "If you wish to use these tools at the next time,  please add"
    echo "the following statement in your login file (.bash_profile)"
    echo "source $DSTPATH/activate_tools"
    echo "If you prefer, you can re-execute this script with -P switch"
    echo -e "------------------------------------------------------------${CLR}"
    echo "For furthermore info visit https://zeroincombenze-tools.readthedocs.io/"
fi
