#!/usr/bin/env bash
#
__version__=1.0.5.39

READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$($READLINK -f $(dirname $0))
if [[ $1 =~ ^-.*h ]]; then
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
    echo -e "\n(C) 2015-2021 by zeroincombenze(R)\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
    exit 0
elif [[ $1 =~ ^-.*V ]]; then
    echo $__version__
    exit 0
fi

RFLIST__travis_emulator="travis travis.man travisrc"
RFLIST__devel_tools=""
RFLIST__clodoo="awsfw bck_filestore.sh clodoo.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog odoo_skin.sh set_color.sh set_worker.sh transodoo.py transodoo.xlsx"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=". z0librc"
RFLIST__zerobug="zerobug z0testrc"
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="odoo_default_tnl.xlsx templates license_text"
RFLIST__python_plus="vem vem.man"
RFLIST__wok_code="cvt_csv_2_rst.py cvt_csv_2_xml.py cvt_script dist_pkg generate_all_tnl gen_addons_table.py gen_readme.py license_mgnt.py makepo_it.py odoo_dependencies.py odoo_translation.py please please.man topep8 to_oca.2p8 to_zero.2p8 to_pep8.2p8 to_pep8.py vfcp vfdiff wget_odoo_repositories.py"
RFLIST__zerobug_odoo=""
RFLIST__odoo_score="odoo_shell.py run_odoo_debug"
RFLIST__os0=""
MOVED_FILES_RE="(cvt_csv_2_rst.py|cvt_csv_2_xml.py|cvt_script|dist_pkg|gen_addons_table.py|gen_readme.py|makepo_it.py|odoo_translation.py|please|please.man|please.py|run_odoo_debug|topep8|topep8.py|transodoo.py|transodoo.xlsx|vfcp|vfdiff)"
FILES_2_DELETE="addsubm.sh clodoocore.py clodoolib.py export_db_model.py odoo_default_tnl.csv please.py prjdiff replica.sh run_odoo_debug.sh set_odoover_confn topep8.py to_oia.2p8 transodoo.csv upd_oemod.py venv_mgr venv_mgr.man wok_doc wok_doc.py z0lib.py z0librun.py"
SRCPATH=
DSTPATH=
[[ $1 =~ ^-.*t ]] && HOME=$($READLINK -e $(dirname $0)/..)
[[ $1 =~ ^-.*n ]] && PMPT="> " || PMPT="\$ "
[[ $1 =~ ^-.*o ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
[[ -z "$SRCPATH" && -d $TDIR/../tools ]] && SRCPATH=$($READLINK -f $TDIR/../tools)
[[ -z "$SRCPATH" && -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ ! -d $HOME_DEV && -n "$SRCPATH" && $1 =~ ^-.*p && $1 =~ ^-.*v ]] && echo "$PMPT mkdir -p $HOME_DEV"
[[ ! -d $HOME_DEV && -n "$SRCPATH" && $1 =~ ^-.*p && ! $1 =~ ^-.*n ]] && mkdir -p $HOME_DEV
[[ -d $HOME_DEV ]] && DSTPATH=$HOME_DEV
if [[ -z "$SRCPATH" || -z "$DSTPATH" ]]; then
    echo "Invalid environment!"
    [[ -d $HOME/dev ]] && echo ".. you should rename $HOME/dev to $HOME/devel"
    echo ""
    $0 -h
    exit 1
fi
if [[ ! $1 =~ ^-.*t ]]; then
    [[ $1 =~ ^-.*d ]] && echo "# Use development branch" && cd $SRCPATH && [[ $(git branch --show-current) != "devel" ]] && git stash -q && git checkout devel -f
    [[ ! $1 =~ ^-.*d ]] && cd $SRCPATH && [[ $(git branch --show-current) != "master" ]] && git stash -q && git checkout master -fq
    [[ $1 =~ ^-.*U ]] && cd $SRCPATH && git pull
fi
[[ $1 =~ ^-.*v ]] && echo "# Installing tools from $SRCPATH to $DSTPATH ..."
[[ $1 =~ ^-.*n ]] || find $SRCPATH $DSTPATH -name "*.pyc" -delete
[[ $1 =~ ^-.*o ]] && echo "WARNING! The switch -o is deprecated and will be removed early!"
PLEASE_CMDS=
PKGS_LIST="clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
for pkg in $PKGS_LIST tools; do
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
    l="RFLIST__$pfn"
    flist=${!l}
    [[ $1 =~ ^-.*v ]] && echo "[$pkg=$flist]"
    for fn in $flist; do
        if [[ $fn == "." ]]; then
            src="$SRCPATH/${pfn}"
            tgt="$DSTPATH/${pfn}"
            ftype=d
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
            fi
        fi
        if $(echo "$src"|grep -Eq "\*"); then
            src=$(dirname "$src")
            tgt=$(dirname "$tgt")
            ftype=d
        fi
        if [[ ! -e "$src" ]]; then
            echo "File $src not found!"
        elif [[ ! -e "$tgt" || -L "$tgt" || $1 =~ ^-.*[fpU] || $fn =~ $MOVED_FILES_RE ]]; then
            [[ -L "$tgt" ]] && echo "$PMPT rm -f $tgt"
            [[ -L "$tgt" && ! $1 =~ ^-.*n ]] && rm -f $tgt
            [[ -d "$tgt" ]] && echo "$PMPT rm -fR $tgt"
            [[ -d "$tgt" && ! $1 =~ ^-.*n ]] && rm -fR $tgt
            if [[ $fn =~ (kbase|templates|license_text) ]]; then
                [[ ! $1 =~ ^-.*q ]] && echo "$PMPT ln -s $src $tgt"
                [[ $1 =~ ^-.*n ]] || ln -s $opts $src $tgt
            elif [[ ! -e "$tgt" || $1 =~ ^-.*[fpU] ]]; then
                [[ $ftype == f ]] && opts="" || opts="-r"
                [[ ! $1 =~ ^-.*q ]] && echo "$PMPT cp $opts $src $tgt"
                [[ $1 =~ ^-.*n ]] || cp $opts $src $tgt
                [[ ! $1 =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
            fi
        fi
    done
done
[[ ! $1 =~ ^-.*n && -d "$DSTPATH/_travis" ]] && rm -fR $DSTPATH/_travis
[[ $1 =~ ^-.*v ]] && echo "$PMPT cp $SRCPATH/tests/test_tools.sh $DSTPATH/test_tools.sh"
[[ $1 =~ ^-.*n ]] || cp $SRCPATH/tests/test_tools.sh $DSTPATH/test_tools.sh
if [[ -f $HOME/maintainers-tools/env/bin/oca-autopep8 ]]; then
    tgt=$DSTPATH/oca-autopep8
    if [[ ! -L "$tgt" || $1 =~ ^-.*[fpU] ]]; then
        if [[ -L "$tgt" || -f "$tgt" ]]; then
            [[ ! $1 =~ ^-.*q ]] && echo "$PMPT rm -f $tgt"
            [[ $1 =~ ^-.*n ]] || rm -f $tgt
            [[ ! $1 =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
        fi
        [[ ! $1 =~ ^-.*q ]] && echo "$PMPT ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt"
        [[ $1 =~ ^-.*n ]] || ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt
    fi
fi
for fn in $FILES_2_DELETE; do
    tgt="$DSTPATH/$fn"
    if [[ -L "$tgt" || -f "$tgt" ]]; then
        [[ ! $1 =~ ^-.*q ]] && echo "$PMPT rm -f $tgt"
        [[ $1 =~ ^-.*n ]] || rm -f $tgt
        [[ ! $1 =~ ^-.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
    fi
done
if [[ ! $1 =~ ^-.*n ]]; then
    echo -e "import sys\nif '$SRCPATH' not in sys.path:    sys.path.insert(0,'$SRCPATH')">$DSTPATH/sitecustomize.py
    echo "[[ -f $DSTPATH/venv/bin/activate ]] && export PATH=\$PATH:$DSTPATH/venv/bin">$DSTPATH/activate_tools
    echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -z "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH">>$DSTPATH/activate_tools
    echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -n "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH:\$PYTHONPATH">>$DSTPATH/activate_tools
    echo "[[ ! -d $DSTPATH || :\$PATH: =~ :$DSTPATH: ]] || export PATH=$DSTPATH:\$PATH">>$DSTPATH/activate_tools
    [[ $1 =~ ^-.*t || $TRAVIS =~ (true|emulate) ]] && echo "[[ ! -d $SRCPATH/zerobug/_travis || :\$PATH: =~ :$SRCPATH/zerobug/_travis: ]] || export PATH=$SRCPATH/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
    [[ $1 =~ ^-.*t || $TRAVIS =~ (true|emulate) ]] && echo "[[ ! -d $SRCPATH/z0bug_odoo/travis || :\$PATH: =~ :$SRCPATH/z0bug_odoo/travis: ]] || export PATH=$SRCPATH/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    [[ -n $PLEASE_CMDS ]] && echo "complete -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
    [[ $1 =~ ^-.*t ]] || source $DSTPATH/activate_tools
fi
if [[ $1 =~ ^-.*[Ss] ]]; then
    [[ ! $1 =~ ^-.*o ]] && SITECUSTOM=$HOME/devel/sitecustomize.py
    [[ $1 =~ ^-.*o ]] && SITECUSTOM=$HOME/dev/sitecustomize.py
    PYLIB=$(dirname $(pip --version 2>/dev/null|grep -Eo "from [^ ]+"|awk '{print $2}') 2>/dev/null)
    [[ -n "$PYLIB" ]] || PYLIB=$(dirname $(pip3 --version 2>/dev/null|grep -Eo "from [^ ]+"|awk '{print $2}') 2>/dev/null)
    if [[ -n "$PYLIB" && -f SITECUSTOM ]]; then
        if [[ -f $PYLIB/sitecustomize.py ]]; then
            if grep -q "import sys" $PYLIB/sitecustomize.py; then
                [[ ! $1 =~ ^-.*q ]] && echo "$PMPT tail $SITECUSTOM -n -1 >> $PYLIB/sitecustomize.py"
                [[ $1 =~ ^-.*n ]] || tail $SITECUSTOM -n -1 >> $SITECUSTOM
            else
                [[ ! $1 =~ ^-.*q ]] && echo "$PMPT cat $SITECUSTOM >> $PYLIB/sitecustomize.py"
                [[ $1 =~ ^-.*n ]] || cat $SITECUSTOM >> $PYLIB/sitecustomize.py
            fi
        else
            [[ ! $1 =~ ^-.*q ]] && echo "$PMPT cp $SITECUSTOM $PYLIB"
            [[ $1 =~ ^-.*n ]] || cp $SITECUSTOM $PYLIB
        fi
    fi
fi
if [[ ! $1 =~ ^-.*n ]]; then
    source $DSTPATH/activate_tools
    if [[ $1 =~ ^-.*[fU] || ! -d $DSTPATH/venv ]]; then
        x="-iDBB"
        [[ $1 =~ ^-.*q ]] && x="-qiDBB"
        [[ $1 =~ ^-.*v ]] && x="-vvviDBB"
        vem create $DSTPATH/venv -p2.7 $x -f
        [[ $? -ne 0 ]] && echo "Error creating Tools virtual environment!" && exit 1
    fi
    [[ $PATH =~ $DSTPATH/venv/bin ]] || export PATH="$DSTPATH/venv/bin:$PATH"
    PYTHON=""
    PYTHON3=""
    [[ -x $DSTPATH/venv/bin/python ]] && PYTHON=$DSTPATH/venv/bin/python
    [[ -x $DSTPATH/venv/bin/python2 ]] && PYTHON=$DSTPATH/venv/bin/python2
    [[ -x $DSTPATH/venv/bin/python3 ]] && PYTHON3=$DSTPATH/venv/bin/python3
    [[ $1 =~ ^-.*[fU] || ! -d $DSTPATH/venv ]] && path="$DSTPATH/bin/*" || path2=""
    for f in $DSTPATH/* $path2; do
        [[ ( -x $f || $f =~ .py$ ) && ! -d $f ]] && grep -q "^#\!.*/bin.*python3$" $f &>/dev/null && sed -i -e "s|^#\!.*/bin.*python3|#\!$PYTHON3|" $f
        [[ ( -x $f || $f =~ .py$ ) && ! -d $f ]] && grep -q "^#\!.*/bin.*python2$" $f &>/dev/null && sed -i -e "s|^#\!.*/bin.*python2|#\!$PYTHON|" $f
        [[ ( -x $f || $f =~ .py$ ) && ! -d $f ]] && grep -q "^#\!.*/bin.*python$" $f &>/dev/null && sed -i -e "s|^#\!.*/bin.*python|#\!$PYTHON|" $f
    done
    if [[ $1 =~ ^-.*[fU] || ! -d $DSTPATH/venv ]]; then
        # Please do not change package list order
        for pkg in configparser odoorpc oerplib babel lxml unidecode openpyxl pyyaml z0lib zerobug clodoo; do
            [[ ! $1 =~ ^-.*q ]] && echo "Installing $pkg ..."
            [[ -d $HOME_DEV/pypi/$pkg/$pkg ]] && vem $DSTPATH/venv install $pkg -qBB || vem $DSTPATH/venv install $pkg
        done
        [[ ! $1 =~ ^-.*q && -d $DSTPATH/clodoo ]] && echo "rm -f $DSTPATH/clodoo"
        [[ -d $DSTPATH/clodoo ]] && rm -f $DSTPATH/clodoo
        x=$(vem $DSTPATH/venv info clodoo|grep -E "Location"|cut -d' ' -f2)/clodoo
        [[ ! $1 =~ ^-.*q && -d $x ]] && echo "ln -s $x $DSTPATH/clodoo"
        [[ -d $x ]] && ln -s $x $DSTPATH/clodoo
    fi
fi
if [[ ! $1 =~ ^-.*n && $1 =~ ^-.*D ]]; then
    mkdir -p $HOME_DEV/pypi
    for pkg in $PKGS_LIST tools; do
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg/-/_} || pfn=$pkg
        mkdir -p $HOME_DEV/pypi/$pfn
        [[ $pkg == "tools" ]] && rsync -avzb $SRCPATH/$pkg/ $HOME_DEV/pypi/$pkg/ || rsync -avzb $SRCPATH/$pfn/ $HOME_DEV/pypi/$pfn/$pfn/
    done
fi
if [[ ! $1 =~ ^-.*n && $1 =~ ^-.*P ]]; then
    $(grep -q "\$HOME/dev[el]*/activate_tools" $HOME/.bash_profile) && sed -e "s|\$HOME/dev[el]*/activate_tools|\$HOME/devel/activate_tools|" -i $HOME/.bash_profile || echo "[[ -f $HOME/devel/activate_tools ]] && . $HOME/devel/activate_tools -q" >>$HOME/.bash_profile
fi
[[ $1 =~ ^-.*T ]] && $DSTPATH/test_tools.sh
if [[ ! $1 =~ ^-.*g && ! $1 =~ ^-.*t ]]; then
  [[ ! $1 =~ ^-.*q ]] && echo "Searching for git projects ..."
  for d in $(find $HOME -not -path "*/_*" -not -path "*/VME/*" -not -path "*/VENV*" -not -path "*/oca*" -not -path "*/tmp*" -name ".git"|sort); do
    [[ $1 =~ ^-.*v && ! $1 =~ ^-.*G ]] && echo "cp $SRCPATH/wok_code/pre-commit $d/hooks"
    [[ ! $1 =~ ^-.*n && ! $1 =~ ^-.*G ]] && cp $SRCPATH/wok_code/pre-commit $d/hooks
    [[ $1 =~ ^-.*v && $1 =~ ^-.*G && -f $d/hooks/pre-commit ]] && echo "rm -f $d/hooks/pre-commit"
    [[ ! $1 =~ ^-.*n && $1 =~ ^-.*G && -f $d/hooks/pre-commit ]] && rm -f $d/hooks/pre-commit
  done
fi
if [[ ! $1 =~ ^-.*q && ! $1 =~ ^-.*P ]]; then
    echo "------------------------------------------------------------"
    echo "If you wish to use these tools at the next time,  please add"
    echo "the following statement in your login file (.bash_profile)"
    echo "source $DSTPATH/activate_tools"
    echo "If you prefer, you can re-execute this script with -P switch"
    echo "------------------------------------------------------------"
fi
