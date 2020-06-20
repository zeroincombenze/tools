#!/usr/bin/env bash
# __version__=0.2.2.31
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
if [[ $1 =~ -.*h ]]; then
    echo "$THIS [-h][-o][-p][-P][-q][-S][-v]"
    echo "  -h  this help"
    echo "  -o  compatibility old mode (exec dir in $HOME/dev)"
    echo "  -p  mkdir $HOME/devel if does not exist"
    echo "  -P  permanent environment (update ~/.bash_profile)"
    echo "  -q  quiet mode"
    echo "  -S  store sitecustomize.py in python path"
    echo "  -v  more verbose"
    exit 0
fi

RFLIST__travis_emulator="gen_addons_table.py prjdiff replica.sh travis travisrc vfcp vfdiff wok_doc wok_doc.py"
RFLIST__devel_tools="cvt_csv_2_rst.py cvt_csv_2_xml.py cvt_script dist_pkg generate_all_tnl gen_readme.py makepo_it.py odoo_dependencies.py odoo_translation.py please please.man please.py topep8 topep8.py to_oca.2p8 to_oia.2p8 to_pep8.2p8 to_pep8.py"
RFLIST__clodoo="awsfw bck_filestore.sh . clodoo.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog run_odoo_debug odoo_skin.sh set_color.sh set_worker.sh"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=". z0librc"
RFLIST__zerobug="zerobug z0testrc"
RFLIST__wok_code=""
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="odoo_default_tnl.csv templates"
RFLIST__python_plus="venv_mgr venv_mgr.man"
RFLIST__zerobug_odoo=""
RFLIST__odoo_score="odoo_shell.py transodoo.py transodoo.csv"
MOVED_FILES_RE="(cvt_csv_2_rst.py|cvt_csv_2_xml.py|cvt_script|dist_pkg|gen_readme.py|makepo_it.py|odoo_translation.py|please|please.man|please.py|topep8|to_pep8.2p8|to_pep8.py|topep8.py)"
FILES_2_DELETE="addsubm.sh clodoocore.py clodoolib.py run_odoo_debug.sh set_odoover_confn z0lib.py z0librun.py"
SRCPATH=
DSTPATH=
[[ -d $HOME/tools ]] && SRCPATH=$HOME/tools
[[ -z "$SRCPATH" && -d $TDIR/../tools ]] && SRCPATH=$(readlink -f $TDIR/../tools)
[[ ! $1 =~ -.*o  && ! -d $HOME/devel && -n "$SRCPATH" && $1 =~ -.*p ]] && mkdir -p $HOME/devel
[[ $1 =~ -.*o  && ! -d $HOME/dev && -n "$SRCPATH" && $1 =~ -.*p ]] && mkdir -p $HOME/dev
[[ ! $1 =~ -.*o  && -d $HOME/devel ]] && DSTPATH=$HOME/devel
[[ $1 =~ -.*o  && -d $HOME/dev ]] && DSTPATH=$HOME/dev
if [ -z "$SRCPATH" -o -z "$DSTPATH" ]; then
    echo "Invalid environment"
    [[ -d $HOME/dev ]] && echo "perhaps you can use -o switch"
    echo ""
    $0 -h
    exit 1
fi
find $SRCPATH -name "*.pyc" -delete
find $DSTPATH -name "*.pyc" -delete
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
            if [[ -L "$tgt"  &&  "$(readlink -e $tgt)" == "$src" && ! $1 =~ -.*p ]]; then
                [[ ! $1 =~ -.*q ]] && echo "ln -s $src $tgt  # (confirmed)"
            else
                if [ -L "$tgt"  -o -f "$tgt" ]; then
                    [[ ! $1 =~ -.*q ]] && echo "\$ rm -f $tgt"
                    rm -f $tgt
                    [ "${tgt: -3}" == ".py" -a -f ${tgt}c ] && rm -f ${tgt}c
                fi
                [[ ! $1 =~ -.*q ]] && echo "\$ ln -s $src $tgt"
                ln -s $src $tgt
            fi
        fi
    done
done
[ -d "$DSTPATH/_travis" ] && rm -fR $DSTPATH/_travis 
if [ -f $HOME/maintainers-tools/env/bin/oca-autopep8 ]; then
    tgt=$DSTPATH/oca-autopep8
    if [[ ! -L "$tgt" || $1 =~ -.*p ]]; then
        if [ -L "$tgt"  -o -f "$tgt" ]; then
            [[ ! $1 =~ -.*q ]] && echo "\$ rm -f $tgt"
            rm -f $tgt
            [ "${tgt: -3}" == ".py" -a -f ${tgt}c ] && rm -f ${tgt}c
        fi
        [[ ! $1 =~ -.*q ]] && echo "\$ ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt"
        ln -s $HOME/maintainers-tools/env/bin/oca-autopep8 $tgt
    fi
fi
for fn in $FILES_2_DELETE; do
    tgt="$DSTPATH/$fn"
    if [ -L "$tgt"  -o -f "$tgt" ]; then
        [[ ! $1 =~ -.*q ]] && echo "\$ rm -f $tgt"
        rm -f $tgt
        [ "${tgt: -3}" == ".py" -a -f ${tgt}c ] && rm -f ${tgt}c
    fi
done
echo -e "import sys\nif '$SRCPATH' not in sys.path:    sys.path.insert(0,'$SRCPATH')">$DSTPATH/sitecustomize.py
echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -z "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH">$DSTPATH/activate_tools
echo "[[ ( ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ) && -n "\$PYTHONPATH" ]] || export PYTHONPATH=$SRCPATH:$PYTHONPATH">>$DSTPATH/activate_tools
echo "[[ ! -d $DSTPATH || :\$PATH: =~ :$DSTPATH: ]] || export PATH=$DSTPATH:\$PATH">>$DSTPATH/activate_tools
[ -n "$PLEASE_CMDS" ] && echo "complete -W \"$PLEASE_CMDS\" please">>$DSTPATH/activate_tools
. $DSTPATH/activate_tools
if [[ $1 =~ -.*S ]]; then
    [[ ! $1 =~ -.*o  ]] && SITECUSTOM=$HOME/devel/sitecustomize.py
    [[ $1 =~ -.*o  ]] && SITECUSTOM=$HOME/dev/sitecustomize.py
    if [ -f SITECUSTOM ]; then
        PYLIB=$(dirname $(pip --version|grep -Eo "from [^ ]+"|awk '{print $2}'))
        if [ -n "$PYLIB" ]; then
            if [ -f $PYLIB/sitecustomize.py ]; then
                if grep -q "import sys" $PYLIB/sitecustomize.py; then
                    [[ ! $1 =~ -.*q ]] && echo "\$ tail $SITECUSTOM -n -1 >> $PYLIB/sitecustomize.py"
                    tail $SITECUSTOM -n -1 >> $SITECUSTOM
                else
                    [[ ! $1 =~ -.*q ]] && echo "\$ cat $SITECUSTOM >> $PYLIB/sitecustomize.py"
                    cat $SITECUSTOM >> $PYLIB/sitecustomize.py
                fi
            else
                [[ ! $1 =~ -.*q ]] && echo "\$ cp $SITECUSTOM $PYLIB"
                cp $SITECUSTOM $PYLIB
            fi
        fi
    fi
elif [[ ! $1 =~ -.*q && ! $1 =~ -.*P ]]; then
    echo "-----------------------------------------------------------"
    echo "Please type and add following statements in your login file"
    echo ". $DSTPATH/activate_tools"
    echo "-----------------------------------------------------------"
fi
if [[ $1 =~ -.*P ]]; then
    $(grep -q "\$HOME/dev[el]*/activate_tools" $HOME/.bash_profile) && sed -e "s|\$HOME/dev[el]*/activate_tools|\$HOME/devel/activate_tools|" -i $HOME/.bash_profile || echo "[[ -f $HOME/devel/activate_tools ]] && . $HOME/devel/activate_tools -q" >>$HOME/.bash_profile
fi
