#!/usr/bin/env bash
# __version__=0.2.3.12
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
if [[ $1 =~ -.*h ]]; then
    echo "$THIS [-h][-n][-o][-p][-P][-q][-S][-T][-v]"
    echo "  -h  this help"
    echo "  -n  dry-run"
    echo "  -o  compatibility old mode (exec dir in $HOME/dev)"
    echo "  -p  mkdir $HOME/dev[el] if does not exist"
    echo "  -P  permanent environment (update ~/.bash_profile)"
    echo "  -q  quiet mode"
    echo "  -s  store sitecustomize.py in python path (you must have privileges)"
    echo "  -S  store sitecustomize.py in python path (you must have privileges)"
    echo "  -t  activate test environment (PATH with CI/CT commands)"
    echo "  -T  activate OCA test environment (PATH with CI/CT commands) deprecated"
    echo "  -v  more verbose"
    exit 0
fi

RFLIST__travis_emulator="replica.sh travis travisrc"
RFLIST__devel_tools="cvt_csv_2_rst.py cvt_csv_2_xml.py cvt_script dist_pkg generate_all_tnl gen_addons_table.py gen_readme.py makepo_it.py odoo_dependencies.py odoo_translation.py please please.man please.py topep8  to_oca.2p8 to_zero.2p8 to_pep8.2p8 to_pep8.py vfcp vfdiff"
RFLIST__clodoo="awsfw bck_filestore.sh . clodoo.py export_db_model.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog run_odoo_debug odoo_skin.sh set_color.sh set_worker.sh transodoo.py transodoo.csv"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=". z0librc"
RFLIST__zerobug="zerobug z0testrc"
RFLIST__wok_code=""
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="odoo_default_tnl.csv odoo_default_tnl.xlsx templates"
RFLIST__python_plus="vem vem.man"
RFLIST__WOK_CODE="wget_odoo_repositories.py"
RFLIST__zerobug_odoo=""
RFLIST__odoo_score="odoo_shell.py"
MOVED_FILES_RE="(cvt_csv_2_rst.py|cvt_csv_2_xml.py|cvt_script|dist_pkg|gen_addons_table.py|gen_readme.py|makepo_it.py|odoo_translation.py|please|please.man|please.py|topep8|to_pep8.2p8|to_pep8.py|topep8.py|vfcp|vfdiff)"
FILES_2_DELETE="addsubm.sh clodoocore.py clodoolib.py prjdiff run_odoo_debug.sh set_odoover_confn wok_doc wok_doc.py z0lib.py z0librun.py"
SRCPATH=
DSTPATH=
[[ $1 =~ -.*[tT] ]] && HOME=$(readlink -e $(dirname $0)/..)
[[ $1 =~ -.*n ]] && PMPT="> " || PMPT="\$ "
[[ $1 =~ -.*o ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
[[ -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ -z "$SRCPATH" && -d $TDIR/../tools ]] && SRCPATH=$(readlink -f $TDIR/../tools)
[[ ! $1 =~ -.*o && ! -d $HOME/devel && -n "$SRCPATH" && $1 =~ -.*p && $1 =~ -.*v ]] && echo "$PMPT mkdir -p $HOME_DEV"
[[ ! $1 =~ -.*o && ! -d $HOME/devel && -n "$SRCPATH" && $1 =~ -.*p && ! $1 =~ -.*n ]] && mkdir -p $HOME_DEV
[[ $1 =~ -.*o && ! -d $HOME/dev && -n "$SRCPATH" && $1 =~ -.*p && $1 =~ -.*v ]] && echo "$PMPT mkdir -p $HOME_DEV"
[[ $1 =~ -.*o && ! -d $HOME/dev && -n "$SRCPATH" && $1 =~ -.*p && ! $1 =~ -.*n ]] && mkdir -p $HOME_DEV
[[ ! $1 =~ -.*o && -d $HOME/devel ]] && DSTPATH=$HOME_DEV
[[ $1 =~ -.*o && -d $HOME/dev ]] && DSTPATH=$HOME_DEV
if [ -z "$SRCPATH" -o -z "$DSTPATH" ]; then
    echo "Invalid environment!"
    [[ -d $HOME/dev ]] && echo ".. perhaps you can use -o switch"
    echo ""
    $0 -h
    exit 1
fi
[[ $1 =~ -.*v ]] && echo "# Installing tools from $SRCPATH to $DSTPATH ..."
[[ $1 =~ -.*n ]] || find $SRCPATH -name "*.pyc" -delete
[[ $1 =~ -.*n ]] || find $DSTPATH -name "*.pyc" -delete
PLEASE_CMDS=
for pkg in clodoo devel_tools lisa odoo_score python_plus tools travis_emulator wok_code z0lib zar zerobug; do
    l="RFLIST__$pkg"
    flist=${!l}
    [[ $1 =~ -.*v ]] && echo "[$pkg=$flist]"
    for fn in $flist; do
        if [ "$fn" == "." ]; then
            src="$SRCPATH/${pkg}"
            tgt="$DSTPATH/${pkg}"
            ftype=d
        elif [ "$pkg" != "tools" ]; then
            src="$SRCPATH/${pkg}/$fn"
            tgt="$DSTPATH/$fn"
            ftype=f
            if [ "$fn" == "please" ]; then
                PLEASE_CMDS=$(grep "^HLPCMDLIST=" $src|awk -F= '{print $2}'|tr -d '"')
                PLEASE_CMDS="${PLEASE_CMDS//|/ }"
            fi
        else
            src="$SRCPATH/$fn"
            tgt="$DSTPATH/$fn"
            ftype=f
        fi
        if $(echo "$src"|grep -Eq "\*"); then
            src=$(dirname "$src")
            tgt=$(dirname "$tgt")
            ftype=d
        fi
        if [ ! -f "$src" -a ! -d "$src" ]; then
            echo "File $src not found!"
        elif [[ ! -L "$tgt" || $1 =~ -.*p || $fn =~ $MOVED_FILES_RE ]]; then
            if [[ -L "$tgt" && "$(readlink -e $tgt)" == "$src" && ! $1 =~ -.*p ]]; then
                [[ ! $1 =~ -.*q ]] && echo "$PMPT ln -s $src $tgt  # (confirmed)"
            else
                if [ -L "$tgt"  -o -f "$tgt" ]; then
                    [[ ! $1 =~ -.*q ]] && echo "$PMPT rm -f $tgt"
                    [[ $1 =~ -.*n ]] || rm -f $tgt
                    [[ ! $1 =~ -.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
                fi
                [[ ! $1 =~ -.*q ]] && echo "$PMPT ln -s $src $tgt"
                [[ $1 =~ -.*n ]] || ln -s $src $tgt
            fi
        fi
    done
done
[[ ! $1 =~ -.*n && -d "$DSTPATH/_travis" ]] && rm -fR $DSTPATH/_travis
if [[ -f $HOME/maintainers-tools/env/bin/oca-autopep8 ]]; then
    tgt=$DSTPATH/oca-autopep8
    if [[ ! -L "$tgt" || $1 =~ -.*p ]]; then
        if [ -L "$tgt" -o -f "$tgt" ]; then
            [[ ! $1 =~ -.*q ]] && echo "$PMPT rm -f $tgt"
            [[ $1 =~ -.*n ]] || rm -f $tgt
            [[ ! $1 =~ -.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
        fi
        [[ ! $1 =~ -.*q ]] && echo "$PMPT ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt"
        [[ $1 =~ -.*n ]] || ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt
    fi
fi
for fn in $FILES_2_DELETE; do
    tgt="$DSTPATH/$fn"
    if [ -L "$tgt" -o -f "$tgt" ]; then
        [[ ! $1 =~ -.*q ]] && echo "$PMPT rm -f $tgt"
        [[ $1 =~ -.*n ]] || rm -f $tgt
        [[ ! $1 =~ -.*n && "${tgt: -3}" == ".py" && -f ${tgt}c ]] && rm -f ${tgt}c
    fi
done
if [[ ! $1 =~ -.*n ]]; then
    echo -e "import sys\nif '$SRCPATH' not in sys.path:    sys.path.insert(0,'$SRCPATH')">$DSTPATH/sitecustomize.py
    echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -z "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH">$DSTPATH/activate_tools
    echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -n "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH:$PYTHONPATH">>$DSTPATH/activate_tools
    echo "[[ ! -d $DSTPATH || :\$PATH: =~ :$DSTPATH: ]] || export PATH=$DSTPATH:\$PATH">>$DSTPATH/activate_tools
    [[ $1 =~ -.*[tT] ]] && echo "[[ ! -d $SRCPATH/zerobug/_travis || :\$PATH: =~ :$SRCPATH/zerobug/_travis: ]] || export PATH=$SRCPATH/zerobug/_travis:\$PATH">>$DSTPATH/activate_tools
    [[ $1 =~ -.*T ]] && echo "[[ ! -d $SRCPATH/maintainer-quality-tools/travis || :\$PATH: =~ :$SRCPATH/maintainer-quality-tools/travis: ]] || export PATH=$SRCPATH/maintainer-quality-tools/travis:\$PATH">>$DSTPATH/activate_tools
    [[ $1 =~ -.*t ]] && echo "[[ -d $SRCPATH/z0bug_odoo/travis || ! -d $SRCPATH/maintainer-quality-tools/travis || :\$PATH: =~ :$SRCPATH/maintainer-quality-tools/travis: ]] || export PATH=$SRCPATH/maintainer-quality-tools/travis:\$PATH">>$DSTPATH/activate_tools
    [[ $1 =~ -.*t ]] && echo "[[ ! -d $SRCPATH/z0bug_odoo/travis || :\$PATH: =~ :$SRCPATH/z0bug_odoo/travis: ]] || export PATH=$SRCPATH/z0bug_odoo/travis:\$PATH">>$DSTPATH/activate_tools
    [ -n "$PLEASE_CMDS" ] && echo "complete -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
    [[ $1 =~ -.*[Tt] ]] || source $DSTPATH/activate_tools
fi
if [[ $1 =~ -.*[Ss] ]]; then
    [[ ! $1 =~ -.*o ]] && SITECUSTOM=$HOME/devel/sitecustomize.py
    [[ $1 =~ -.*o ]] && SITECUSTOM=$HOME/dev/sitecustomize.py
    PYLIB=$(dirname $(pip --version|grep -Eo "from [^ ]+"|awk '{print $2}'))
    if [[ -n "$PYLIB" && -f SITECUSTOM ]]; then
        if [[ -f $PYLIB/sitecustomize.py ]]; then
            if grep -q "import sys" $PYLIB/sitecustomize.py; then
                [[ ! $1 =~ -.*q ]] && echo "$PMPT tail $SITECUSTOM -n -1 >> $PYLIB/sitecustomize.py"
                [[ $1 =~ -.*n ]] || tail $SITECUSTOM -n -1 >> $SITECUSTOM
            else
                [[ ! $1 =~ -.*q ]] && echo "$PMPT cat $SITECUSTOM >> $PYLIB/sitecustomize.py"
                [[ $1 =~ -.*n ]] || cat $SITECUSTOM >> $PYLIB/sitecustomize.py
            fi
        else
            [[ ! $1 =~ -.*q ]] && echo "$PMPT cp $SITECUSTOM $PYLIB"
            [[ $1 =~ -.*n ]] || cp $SITECUSTOM $PYLIB
        fi
    fi
elif [[ ! $1 =~ -.*q && ! $1 =~ -.*P ]]; then
    echo "------------------------------------------------------------"
    echo "If you wish to use these tools at the next time,  please add"
    echo "the following statement in your login file (.bash_profile)"
    echo ". $DSTPATH/activate_tools"
    echo "If you prefer, you can re-execute this script with -P switch"
    echo "------------------------------------------------------------"
fi
if [[ ! $1 =~ -.*n && $1 =~ -.*P ]]; then
    $(grep -q "\$HOME/dev[el]*/activate_tools" $HOME/.bash_profile) && sed -e "s|\$HOME/dev[el]*/activate_tools|\$HOME/devel/activate_tools|" -i $HOME/.bash_profile || echo "[[ -f $HOME/devel/activate_tools ]] && . $HOME/devel/activate_tools -q" >>$HOME/.bash_profile
fi
