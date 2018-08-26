# __version__=0.1.9
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
if [[ $1 =~ -.*h ]]; then
  echo "$THIS [-h][-p][-q]"
  echo "  -h  this help"
  echo "  -p  mkdir ~/dev if not exists"
  echo "  -q  quiet mode"
  exit 0
fi
RFLIST__travis_emulator="dist_pkg gen_addons_table.py please please.man please.py prjdiff replica.sh topep8 topep8.py to_pep8.2p8 to_pep8.py travis travisrc vfcp vfdiff wok_doc wok_doc.py"
RFLIST__clodoo="addsubm.sh awsfw clodoo.py clodoocore.py clodoolib.py inv2draft_n_restore.py list_requirements.py manage_db manage_odoo odoorc oe_watchdog run_odoo_debug.sh odoo_skin.sh set_odoover_confn transodoo.py transodoo.csv upd_oemod.py"
RFLIST__zar="pg_db_active"
RFLIST__z0lib="z0lib.py z0librc"
RFLIST__zerobug="z0testrc"
RFLIST__wok_code="cvt_script"
RFLIST__lisa="lisa lisa.conf.sample lisa.man kbase"
SRCPATH=
DSTPATH=
[ -d ~/tools ] && SRCPATH=~/tools
[ -z "$SRCPATH" -a -d $TDIR/../tools ] && SRCPATH=$(readlink -f $TDIR/../tools)
[[ ! -d ~/dev && -n "$SRCPATH" && $1 =~ -.*p ]] && mkdir -p ~/dev
[ -d ~/dev ] && DSTPATH=~/dev
if [ -z "$SRCPATH" -o -z "$DSTPATH" ]; then
  echo "Invalid environment"
  exit 1
fi
for pkg in travis_emulator clodoo zar z0lib zerobug wok_code lisa; do
  l="RFLIST__$pkg"
  flist=${!l}
  [[ ! $1 =~ -.*q ]] && echo "[$pkg=$flist]"
  for fn in $flist; do
    src="$SRCPATH/${pkg}/$fn"
    tgt="$DSTPATH/$fn"
    if [ ! -f "$src" -a ! -d "$src" ]; then
      echo "File $src not found!"
    elif [[ ! -L "$tgt" || $1 =~ -.*p ]]; then
      if [ -L "$tgt" ]; then
        [[ ! $1 =~ -.*q ]] && echo "\$ rm -f $tgt"
        rm -f $tgt
      fi
      [[ ! $1 =~ -.*q ]] && echo "\$ ln -s $src $tgt"
      ln -s $src $tgt
    fi
  done
done
