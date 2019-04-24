# __version__=0.2.2.9
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
if [[ $1 =~ -.*h ]]; then
  echo "$THIS [-h][-p][-q]"
  echo "  -h  this help"
  echo "  -p  mkdir $HOME/dev if not exists"
  echo "  -q  quiet mode"
  echo "  -v  more verbose"
  exit 0
fi

RFLIST__travis_emulator="cvt_csv_2_rst.py cvt_csv_2_xml.py dist_pkg gen_addons_table.py please please.man please.py prjdiff replica.sh travis travisrc vfcp vfdiff wok_doc wok_doc.py"
RFLIST__devel_tools="generate_all_tnl gen_readme.py makepo_it.py odoo_dependencies.py odoo_translation.py topep8 topep8.py to_oca.2p8 to_oia.2p8 to_pep8.2p8 to_pep8.py"
RFLIST__clodoo="awsfw . clodoo.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo manage_odoo.man odoo_install_repository odoorc oe_watchdog run_odoo_debug odoo_skin.sh set_odoover_confn transodoo.py transodoo.csv upd_oemod.py"
RFLIST__zar="pg_db_active pg_db_reassign_owner"
RFLIST__z0lib=". z0librc"
RFLIST__zerobug="z0testrc"
RFLIST__wok_code="cvt_script"
RFLIST__lisa="lisa lisa.conf.sample lisa.man lisa_bld_ods kbase/*.lish odoo-server_Debian odoo-server_RHEL"
RFLIST__tools="odoo_default_tnl.csv templates"
MOVED_FILES_RE="(gen_readme.py|makepo_it.py|odoo_translation.py|topep8|to_pep8.2p8|to_pep8.py|topep8.py)"
SRCPATH=
DSTPATH=
[ -d $HOME/tools ] && SRCPATH=$HOME/tools
[ -z "$SRCPATH" -a -d $TDIR/../tools ] && SRCPATH=$(readlink -f $TDIR/../tools)
[[ ! -d $HOME/dev && -n "$SRCPATH" && $1 =~ -.*p ]] && mkdir -p $HOME/dev
[ -d $HOME/dev ] && DSTPATH=$HOME/dev
if [ -z "$SRCPATH" -o -z "$DSTPATH" ]; then
  echo "Invalid environment"
  exit 1
fi
find $SRCPATH -name "*.pyc" -delete
find $DSTPATH -name "*.pyc" -delete
for pkg in travis_emulator clodoo devel_tools zar z0lib zerobug wok_code lisa tools; do
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
      if [ -L "$tgt"  -o -f "$tgt" ]; then
        [[ ! $1 =~ -.*q ]] && echo "\$ rm -f $tgt"
        rm -f $tgt
        [ "${tgt: -3}" == ".py" -a -f ${tgt}c ] && rm -f ${tgt}c
      fi
      [[ ! $1 =~ -.*q ]] && echo "\$ ln -s $src $tgt"
      ln -s $src $tgt
    fi
  done
done
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
for fn in addsubm.sh clodoocore.py clodoolib.py run_odoo_debug.sh z0lib.py z0lib.pyc z0librun.py z0librun.pyc; do
  tgt="$DSTPATH/$fn"
  if [ -L "$tgt"  -o -f "$tgt" ]; then
    [[ ! $1 =~ -.*q ]] && echo "\$ rm -f $tgt"
    rm -f $tgt
  fi
done
export PYTHONPATH=$DSTPATH:$SRCPATH
[ $(echo "$PATH"|grep -v "$DSTPATH") ] && export PATH=$DSTPATH:$PATH
# echo "set -v">$DSTPATH/activate_tools
echo "[[ ! -d $SRCPATH || :\$PYTHONPATH: =~ :$SRCPATH: ]] || export PYTHONPATH=$SRCPATH">$DSTPATH/activate_tools
echo "[[ ! -d $DSTPATH || :\$PATH: =~ :$DSTPATH: ]] || export PATH=$DSTPATH:\$PATH">>$DSTPATH/activate_tools
# echo "set +v">>$DSTPATH/activate_tools
if [[ ! $1 =~ -.*q ]]; then
  echo "-----------------------------------------------------------"
  echo "Please type and add following statements in your login file"
  echo ". $DSTPATH/activate_tools"
  echo "-----------------------------------------------------------"
fi
