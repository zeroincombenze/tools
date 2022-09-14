# set -x
__version__=2.0.0.2
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
act=""
pypi=""
opts=""
tgtdir=""
branch=""
prm=""
while [[ -n $1 ]]; do
    if [[ -n "$prm" ]]; then
        eval $prm"=$1"
        prm=""
    elif [[ ! $1 =~ ^- ]]; then
        [[ -z "$act" ]] && act=$1 && shift && continue
        [[ -z "$pypi" ]] && pypi=$1 && shift && continue
    else
        [[ $1 =~ -.*h ]] && act="help"
        [[ $1 =~ -.*U ]] && act="update"
        [[ $1 =~ -.*B ]] && opts=${opts}B
        [[ $1 =~ -.*f ]] && opts=${opts}f
        [[ $1 =~ -.*l ]] && opts=${opts}l
        [[ $1 =~ -.*n ]] && opts=${opts}n
        [[ $1 =~ -.*I ]] && opts=${opts}I
        [[ $1 =~ -.*d ]] && prm="tgtdir"
        [[ $1 =~ -.*b ]] && prm="branch"
    fi
    shift
done
ACTLIST="diff|dir|docs|info|show|install|update|libdir|replace|replace-update|travis|travis-summary|version"
PKGS_LIST="clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
PKGS_LIST_RE="(${PKGS_LIST// /|})"
PKGS_LIST_RE=${PKGS_LIST_RE//-/.}
ODOO_ROOT=$(dirname $HOME_DEVEL)
[[ -z "$act" || ! $act =~ ($ACTLIST) ]] && act="help"
[[ $act == "help" ]] && echo "$0 [-h|-B|-f|-I|-l|-n|-U] [-d VENV] [-b BRANCH] $ACTLIST|help [PYPI_PKG]" && exit 0
b=$(basename $PWD)
[[ -z "$pypi" && $(dirname $PWD) == $HOME_DEVEL/pypi/$b && $b =~ $PKGS_LIST_RE ]] && pypi=$b
[[ -z "$pypi" ]] && pypi="$PKGS_LIST" || pypi="${pypi//,/ }"
[[ -z "$tgtdir" ]] && tgtdir="$ODOO_ROOT/VME/* $HOME_DEVEL/venv" || tgtdir="$(readlink -f $tgtdir)/*"
[[ -n "$opts" ]] && opts="-$opts"
[[ $tgtdir =~ ^[~/.] ]] || tgtdir="$ODOO_ROOT/$tgtdir"
[[ $act =~ (docs|replace|travis|travis-summary|version) ]] && tgtdir=$HOME_DEVEL/pypi/tools
[[ -n $branch ]] && branch="(${branch//,/|})"
echo "$0 $act '$pypi' -d $tgtdir -b $branch $opts"
for d in $tgtdir; do
    if [[ ! $act =~ (diff|docs|replace|travis|travis-summary|version) ]]; then
        [[ -d "$d" ]] || continue
        [[ -n "$branch" && ! $d =~ $branch ]] && continue
        [[ $d =~ VME(3.5|3.6) ]] && continue
        echo "[$d]"
        pypath=
        [[ -d $d/lib/python2.7/site-packages ]] && pypath=$d/lib/python2.7/site-packages
        [[ -d $d/lib/python3.5/site-packages ]] && pypath=$d/lib/python3.5/site-packages
        [[ -d $d/lib/python3.6/site-packages ]] && pypath=$d/lib/python3.6/site-packages
        [[ -d $d/lib/python3.7/site-packages ]] && pypath=$d/lib/python3.7/site-packages
        [[ -d $d/lib/python3.8/site-packages ]] && pypath=$d/lib/python3.8/site-packages
        [[ -d $d/lib/python3.9/site-packages ]] && pypath=$d/lib/python3.9/site-packages
        if [[ $opts =~ -.*l && ! -d "$pypath" ]]; then
            echo "Package directory not found"
            exit 1
        fi
    fi
    for pkg in $pypi tools; do
        [[ $pkg != "tools" || $act =~ (docs|replace|replace-update|version) ]] || continue
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
        if [[ $act =~ (info|show|install|replace-update|update) ]]; then
            if [[ $act == "replace-update" ]]; then
                [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
                OPTS=""
                [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
                echo -e "\n===[$pkg]==="
                echo "cd $srcdir; please $OPTS replace"
                cd $srcdir
                [[ $opts =~ -.*n ]] || please $OPTS replace
            fi
            if [[ $opts =~ -.*B ]]; then
                srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            else
                srcdir="$ODOO_ROOT/tools/$fn"
            fi
            [[ ! -d "$srcdir" ]] && continue
            [[ $act == "replace-update" ]] && act2="update" || act2=$act
            [[ $act =~ (install|replace-update|update) ]] && pkg2=$srcdir || pkg2=$pkg
            OPTS=""
            [[ $opts =~ -.*f ]] && OPTS="$OPTS -f"
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*I ]] && OPTS="$OPTS -I"
            if [[ $act =~ (install|replace-update|update) && $opts =~ -.*f && -d $pypath/$fn && ! -L $pypath/$fn ]]; then
                echo "vem $d uninstall $pkg $OPTS"
                [[ $opts =~ -.*n ]] || vem $d uninstall $pkg $OPTS
            elif [[ $act =~ (install|replace-update|update) && -n $pypath && -L $pypath/$fn  ]]; then
                echo "rm -f $pypath/$fn"
                [[ $opts =~ -.*n ]] || rm -f $pypath/$fn
                [[ $act == "update" ]] && act2="install"
            fi
            echo "vem $d $act2 $pkg2 $OPTS"
            [[ $opts =~ -.*n ]] || vem $d $act2 $pkg2 $OPTS
        elif [[ $act == "dir" ]]; then
            srcdir=$(vem $d show $pkg|grep "[Ll]ocation:"|awk -F: '{print " -- " $2}')
            echo $srcdir/$fn
            dir -lh $srcdir/$fn
        elif [[ $act == "libdir" ]]; then
            echo "libdir=$pypath"
            dir -lhd $pypath/$fn
	      elif [[ $act =~ (travis|travis-summary) ]]; then
            srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*B ]] && OPTS="$OPTS -Z"
            echo -e "\n===[$pkg]==="
            [[ $act == "travis" ]] && echo "cd $srcdir; travis $OPTS" || echo "cd $srcdir; travis $OPTS summary"
            cd $srcdir
            [[ $act == "travis" ]] && travis $OPTS || travis $OPTS summary
        elif [[ $act == "diff" ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            diff --suppress-common-line -y ""$srcdir"" "$ODOO_ROOT/tools/$fn" | less
        elif [[ $act == "docs" ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            echo -e "\n===[$pkg]==="
            echo "cd $srcdir; please $OPTS docs"
            cd $srcdir
            [[ $opts =~ -.*n ]] || please $OPTS docs
        elif [[ $act == "replace" ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            echo -e "\n===[$pkg]==="
            echo "cd $srcdir; please $OPTS replace"
            cd $srcdir
            [[ $opts =~ -.*n ]] || please $OPTS replace
        elif [[ $act == "version" ]]; then
            [[ $pkg == "tools" ]] && continue
            srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            echo -e "\n===[$pkg]==="
            echo "cd $srcdir; please version"
            cd $srcdir
            [[ $opts =~ -.*n ]] || please version
        else
            echo "Invalid command!"
            exit 1
        fi
    done
done
