# set -x
__version__=1.0.1.8
cmd=""
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
        [[ -z "$cmd" ]] && cmd=$1 && shift && continue
        [[ -z "$pypi" ]] && pypi=$1 && shift && continue
    else
        [[ $1 =~ -.*h ]] && cmd="help"
        [[ $1 =~ -.*U ]] && cmd="update"
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
[[ -z "$cmd" || ! $cmd =~ (dir|info|show|install|update|libdir|travis|travis-summary) ]] && cmd="help"
[[ $cmd == "help" ]] && echo "$0 dir|info|show|install|update|libdir|travis|travis-summary|help -h|-B|-f|-I|-l|-n|-U [PYPI_PKG] [-d VENV] [-b BRANCH]" && exit 1
[[ -z "$pypi" ]] && pypi="clodoo devel_tools odoo_score os0 python_plus z0bug_odoo z0lib zerobug" || pypi="${pypi//,/ }"
[[ -z "$tgtdir" ]] && tgtdir="$HOME/VME/*" || tgtdir="$tgtdir*"
[[ -n "$opts" ]] && opts="-$opts"
[[ $tgtdir =~ ^[~/.] ]] || tgtdir="$HOME/$tgtdir"
[[ $cmd =~ (travis|travis-summary) ]] && tgtdir=$HOME/devel/pypi/tools
[[ -n $branch ]] && branch="(${branch//,/|})"
echo "$0 $cmd '$pypi' -d $tgtdir -b $branch $opts"
for d in $tgtdir; do
    if [[ ! $cmd =~ (travis|travis-summary) ]]; then
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
    for pkg in $pypi; do
        if [[ $cmd =~ (install|update) && $opts =~ -.*l ]]; then
            if [[ $opts =~ -.*B ]]; then
                srcdir="$HOME/devel/pypi/$pkg/$pkg"
            else
                srcdir="$HOME/tools/$pkg"
            fi
            [[ ! -d "$srcdir" ]] && continue
            if [[ -d $pypath/$pkg && ! -L $pypath/$pkg ]]; then
                echo "vem $d exec \"pip uninstall $pkg\""
                [[ $opts =~ -.*n ]] || vem $d exec "pip uninstall $pkg"
            fi
            echo "ln -s $srcdir $pypath"
            [[ $opts =~ -.*n ]] || ln -s $srcdir $pypath
        elif [[ $cmd =~ (info|show|install|update) ]]; then
            cmd2=$cmd
            if [[ -n $pypath && -L $pypath/$pkg ]]; then
                echo "rm -f $pypath/$pkg"
                [[ $opts =~ -.*n ]] || rm -f $pypath/$pkg
                [[ $cmd == "update" ]] && cmd2="install"
            fi
            OPTS=""
            [[ $opts =~ -.*f ]] && OPTS="$OPTS -f"
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*I ]] && OPTS="$OPTS -I"
            echo "vem $d $cmd2 $pkg $OPTS"
            [[ $opts =~ -.*n ]] || vem $d $cmd2 $pkg $OPTS
        elif [[ $cmd == "dir" ]]; then
            srcdir=$(vem $d show $pkg|grep "[Ll]ocation:"|awk -F: '{print " -- " $2}')
            echo $srcdir/$pkg
            dir -lh $srcdir/$pkg
        elif [[ $cmd == "libdir" ]]; then
            echo "libdir=$pypath"
            dir -lhd $pypath/$pkg
	      elif [[ $cmd =~ (travis|travis-summary) ]]; then
            srcdir="$HOME/devel/pypi/$pkg/$pkg"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            echo "cd $srcdir; travis $OPTS"
            cd $srcdir
            [[ $cmd == "travis" ]] && travis $OPTS || travis $OPTS summary
        else
            echo "Invalid command!"
            exit 1
        fi
    done
done
