# set -x
__version__=1.0.8.1
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
ACTLIST="dir|docs|info|show|install|update|libdir|replace|travis|travis-summary"
PKGS_LIST="clodoo lisa odoo_score os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
[[ -z "$act" || ! $act =~ ($ACTLIST) ]] && act="help"
[[ $act == "help" ]] && echo "$0 -h|-B|-f|-I|-l|-n|-U $ACTLIST|help [PYPI_PKG] [-d VENV] [-b BRANCH]" && exit 1
[[ -z "$pypi" ]] && pypi="$PKGS_LIST" || pypi="${pypi//,/ }"
[[ -z "$tgtdir" ]] && tgtdir="$HOME/VME/*" || tgtdir="$tgtdir*"
[[ -n "$opts" ]] && opts="-$opts"
[[ $tgtdir =~ ^[~/.] ]] || tgtdir="$HOME/$tgtdir"
[[ $act =~ (docs|replace|travis|travis-summary) ]] && tgtdir=$HOME/devel/pypi/tools
[[ -n $branch ]] && branch="(${branch//,/|})"
echo "$0 $act '$pypi' -d $tgtdir -b $branch $opts"
for d in $tgtdir; do
    if [[ ! $act =~ (docs|replace|travis|travis-summary) ]]; then
        [[ -d "$d" ]] || continue
        [[ -n "$branch" && ! $d =~ $branch ]] && continue
        [[ $d =~ VME(3.5|3.6) ]] && continue
        echo "[$d]"
        pypath=
        [[ -d $d/lib/python2.7/site-packages ]] && pypath=$d/lib/python2.7/site-packages
        [[ -d $d/lib/python3.5/site-packages ]] && pypath=$d/lib/python3.5/site-packages
        [[ -d $d/lib/python3.6/site-packages ]] && pypath=$d/lib/python3.6/site-packages
        [[ -d $d/lib/python3.7/site-packages ]] && pypath=$d/lib/python3.7/site-packages
        if [[ $opts =~ -.*l && ! -d "$pypath" ]]; then
            echo "Package directory not found"
            exit 1
        fi
    fi
    for pkg in $pypi tools; do
        [[ $pkg != "tools" || $act =~ (docs|replace) ]] || continue
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
        if [[ $act =~ (install|update) && $opts =~ -.*l ]]; then
            if [[ $opts =~ -.*B ]]; then
                srcdir="$HOME/devel/pypi/$fn/$fn"
            else
                srcdir="$HOME/tools/$fn"
            fi
            [[ ! -d "$srcdir" ]] && continue
            if [[ -d $pypath/$fn && ! -L $pypath/$fn ]]; then
                echo "vem $d exec \"pip uninstall $pkg\""
                [[ $opts =~ -.*n ]] || vem $d exec "pip uninstall $pkg"
            fi
            echo "ln -s $srcdir $pypath"
            [[ $opts =~ -.*n ]] || ln -s $srcdir $pypath
        elif [[ $act =~ (info|show|install|update) ]]; then
            act2=$act
            if [[ -n $pypath && -L $pypath/$fn ]]; then
                echo "rm -f $pypath/$fn"
                [[ $opts =~ -.*n ]] || rm -f $pypath/$fn
                [[ $act == "update" ]] && act2="install"
            fi
            OPTS=""
            [[ $opts =~ -.*f ]] && OPTS="$OPTS -f"
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*I ]] && OPTS="$OPTS -I"
            echo "vem $d $act2 $pkg $OPTS"
            [[ $opts =~ -.*n ]] || vem $d $act2 $pkg $OPTS
        elif [[ $act == "dir" ]]; then
            srcdir=$(vem $d show $pkg|grep "[Ll]ocation:"|awk -F: '{print " -- " $2}')
            echo $srcdir/$fn
            dir -lh $srcdir/$fn
        elif [[ $act == "libdir" ]]; then
            echo "libdir=$pypath"
            dir -lhd $pypath/$fn
	      elif [[ $act =~ (travis|travis-summary) ]]; then
            srcdir="$HOME/devel/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*B ]] && OPTS="$OPTS -Z"
            echo -e "\n===[$pkg]==="
            [[ $act == "travis" ]] && echo "cd $srcdir; travis $OPTS" || echo "cd $srcdir; travis $OPTS summary"
            cd $srcdir
            [[ $act == "travis" ]] && travis $OPTS || travis $OPTS summary
        elif [[ $act == "docs" ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME/devel/pypi/$fn" || srcdir="$HOME/devel/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            echo -e "\n===[$pkg]==="
            echo "cd $srcdir; please $OPTS docs"
            cd $srcdir
            please $OPTS docs
        elif [[ $act == "replace" ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME/devel/pypi/$fn" || srcdir="$HOME/devel/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            echo -e "\n===[$pkg]==="
            echo "cd $srcdir; please $OPTS replace"
            cd $srcdir
            please $OPTS replace
        else
            echo "Invalid command!"
            exit 1
        fi
    done
done
