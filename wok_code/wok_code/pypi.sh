# set -x
__version__=2.0.12
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
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

do_replace() {
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
    [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
    OPTS=""
    [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
    echo -e "\n===[$pkg]==="
    [[ $PWD != $srcdir ]] && run_traced "cd $srcdir"
    run_traced "please $OPTS replace"
}

do_wep() {
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
    srcdir="$HOME_DEVEL/pypi/$fn"
    OPTS=""
    [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
    echo -e "\n===[$pkg]==="
    [[ $PWD != $srcdir ]] && run_traced "cd $srcdir"
    run_traced "please $OPTS wep"
}


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
        [[ $1 =~ -.*b ]] && prm="branch"
        [[ $1 =~ -.*B ]] && opts=${opts}B
        [[ $1 =~ -.*d ]] && prm="tgtdir"
        [[ $1 =~ -.*f ]] && opts=${opts}f
        [[ $1 =~ -.*i ]] && opts=${opts}i
        [[ $1 =~ -.*I ]] && opts=${opts}I
        [[ $1 =~ -.*n ]] && opts=${opts}n
        [[ $1 =~ -.*q ]] && opts=${opts}q
        [[ $1 =~ -.*U ]] && act="update"
        [[ $1 =~ -.*y ]] && opts=${opts}y
        [[ $1 =~ -.*Z ]] && opts=${opts}Z
    fi
    shift
done
[[ -n "$opts" ]] && opts="-$opts"
HLPCMDLIST="cvt_script|diff|dir|docs|git-add|info|install|libdir|list|meld|replace|show|travis|travis-summary|update|update+replace|version|wep"
ACT2VME="^(dir|info|show|install|libdir|update|update\+replace|update)$"
ACT2TOOLS="^(docs|git-add|list|replace|travis|travis-summary|version|wep)$"
LOCAL_PKGS="clodoo lisa odoo_score oerplib3 os0 python-plus travis_emulator wok_code z0bug-odoo z0lib zar zerobug"
LOCAL_PKGS_RE="(${LOCAL_PKGS// /|})"
LOCAL_PKGS_RE=${LOCAL_PKGS_RE//-/.}
ODOO_ROOT=$(dirname $HOME_DEVEL)
[[ -z "$act" || ! $act =~ ($HLPCMDLIST) ]] && act="help"
[[ $act == "help" ]] && echo "$0 [-h|-B|-f|-I|-l|-n|-U|-y|-Z] [-d VENV] [-b BRANCH] $HLPCMDLIST|help [PYPI_PKG]" && exit 0
b=$(basename $PWD)
[[ -z "$pypi" && $(dirname $PWD) == $HOME_DEVEL/pypi/$b && $b =~ $LOCAL_PKGS_RE ]] && pypi=$b
[[ -z "$pypi" ]] && pypi="$LOCAL_PKGS" || pypi="${pypi//,/ }"
[[ -z "$tgtdir" ]] && tgtdir="$ODOO_ROOT/VME/* $HOME_DEVEL/venv" || tgtdir="$(readlink -f $tgtdir)/*"
[[ $tgtdir =~ ^[~/.] ]] || tgtdir="$ODOO_ROOT/$tgtdir"
[[ $act =~ $ACT2TOOLS ]] && tgtdir=$HOME_DEVEL/pypi/tools
[[ -n $branch ]] && branch="(${branch//,/|})"
echo "$0 $act '$pypi' -d $tgtdir -b $branch $opts"
act2=$act
for d in $tgtdir; do
    [[ $act =~ "list" && ! $opts =~ -.*B ]] && echo -e "\n$LOCAL_PKGS" && run_traced "find $ODOO_ROOT/tools -maxdepth 1 -type d|grep -Ev \"(/|.git|.idea|docs|egg-info|license_text|templates|tests|z0tester)$\"|sort|cut -d/ -f5|tr '\n' ' '" && echo "" && continue
    [[ $act =~ "list" && $opts =~ -.*B ]] && echo -e "\n$LOCAL_PKGS" && run_traced "find $HOME_DEVEL/pypi -maxdepth 1 -type d|grep -Ev \"(/|.git|.idea|docs|egg-info|license_text|templates|tests|z0tester)$\"|sort|cut -d/ -f6|tr '\n' ' '" && echo "" && continue
    if [[ $act =~ $ACT2VME || ( $act =~ (diff|meld) && -n $branch ) ]]; then
        [[ -d "$d" ]] || continue
        [[ -n "$branch" && ! $d =~ $branch ]] && continue
        # [[ $d =~ VME(3.5|3.6) ]] && continue
        echo "[$d]"
        pypath=
        [[ -d $d/lib/python2.7/site-packages ]] && pypath=$d/lib/python2.7/site-packages
        [[ -d $d/lib/python3.5/site-packages ]] && pypath=$d/lib/python3.5/site-packages
        [[ -d $d/lib/python3.6/site-packages ]] && pypath=$d/lib/python3.6/site-packages
        [[ -d $d/lib/python3.7/site-packages ]] && pypath=$d/lib/python3.7/site-packages
        [[ -d $d/lib/python3.8/site-packages ]] && pypath=$d/lib/python3.8/site-packages
        [[ -d $d/lib/python3.9/site-packages ]] && pypath=$d/lib/python3.9/site-packages
        if [[ -z $pypath || ! -d "$pypath" ]]; then
            echo "Package directory not found"
            [[ $opts =~ -.*i ]] && continue
            exit 1
        fi
    fi
    for pkg in $pypi tools; do
        [[ $pkg != "tools" || $act =~ $ACT2TOOLS ]] || continue
        [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
        if [[ $act =~ (info|show|install|update+replace|update) ]]; then
            [[ $opts =~ -.*B || $act == "update+replace" ]] && srcdir="$HOME_DEVEL/pypi/$fn/$fn" || srcdir="$ODOO_ROOT/tools/$fn"
            [[ ! -d "$srcdir" ]] && continue
            [[ $act == "update+replace" ]] && act2="update"
            [[ ( $opts =~ -.*B && $act =~ (install|update) ) || $act == "update+replace" ]] && pkg2=$(dirname $srcdir) || pkg2="$pkg -BB"
            OPTS=""
            [[ $opts =~ -.*f ]] && OPTS="$OPTS -f"
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*I ]] && OPTS="$OPTS -I"
            if [[ $act =~ (install|update+replace|update) && $opts =~ -.*f && -d $pypath/$fn && ! -L $pypath/$fn ]]; then
                run_traced "vem $d uninstall $pkg $OPTS"
            elif [[ $act =~ (install|update+replace|update) && -n $pypath && -L $pypath/$fn  ]]; then
                run_traced "rm -f $pypath/$fn"
                [[ $act == "update" ]] && act2="install"
            fi
            run_traced "vem $d $act2 $pkg2 $OPTS"
        elif [[ $act == "dir" ]]; then
            srcdir=$(vem $d show $pkg 2>/dev/null|grep "[Ll]ocation:"|awk -F: '{print $2}')
            [[ -n $srcdir ]] && run_traced "dir -lh $srcdir/$fn"|| echo "No path found for $pkg"
        elif [[ $act == "libdir" ]]; then
            run_traced "ls -d $pypath/$fn"
	      elif [[ $act =~ (travis|travis-summary) ]]; then
	          [[ $pkg == "tools" ]] && continue
            srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            [[ $opts =~ -.*B ]] && OPTS="$OPTS -Z"
            echo -e "\n===[$pkg]==="
            [[ $act == "travis" ]] && echo "cd $srcdir; travis $OPTS" || echo "cd $srcdir; travis $OPTS summary"
            run_traced "cd $srcdir"
            [[ $act == "travis" ]] && run_traced "travis $OPTS" || run_traced "travis $OPTS summary"
        elif [[ $act =~ (diff|meld) ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            [[ -n $branch ]] && tgtdir="$pypath/$fn" || tgtdir="$ODOO_ROOT/tools/$fn"
            if [[ $act == "meld" ]]; then
               [[ -n $(which meld.exe 2>/dev/null) ]] && run_traced "meld.exe \"$srcdir\" \"$tgtdir\"" || run_traced "meld \"$srcdir\" \"$tgtdir\""
            else
                run_traced "diff --suppress-common-line -y \"$srcdir\" \"$tgtdir\" | less"
            fi
        elif [[ $act == "docs" ]]; then
            [[ $pkg == "tools" ]] && srcdir="$HOME_DEVEL/pypi/$fn" || srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            OPTS=""
            [[ $opts =~ -.*n ]] && OPTS="$OPTS -n"
            echo -e "\n===[$pkg]==="
            run_traced "cd $srcdir"
            run_traced "please $OPTS docs"
        elif [[ $act =~ "replace" ]]; then
            do_replace
        elif [[ $act == "version" ]]; then
            [[ $pkg == "tools" ]] && continue
            srcdir="$HOME_DEVEL/pypi/$fn"
            echo -e "\n===[$pkg]==="
            [[ ! -f $srcdir/setup.py ]] && continue
            python $srcdir/setup.py --version
            echo ""
            head -n5 $srcdir/$fn/egg-info/history.rst
        elif [[ $act == "git-add" ]]; then
            srcdir="$HOME_DEVEL/pypi"
            [[ $PWD != $srcdir ]] && run_traced "cd $srcdir"
            run_traced "git add ./$fn"
        elif [[ $act == "cvt_script" ]]; then
            [[ $pkg == "tools" ]] && continue
            srcdir="$HOME_DEVEL/pypi/$fn/$fn"
            OPTS="-k"
            [[ $opts =~ -.*n ]] && OPTS="${OPTS}n"
            [[ $opts =~ -.*y ]] && OPTS="${OPTS}y"
            for f in $(find $srcdir -type f); do
                mime=$(file --mime-type -b $f)
                [[ $mime == "text/x-shellscript" || $f =~ .sh$ ]] || continue
                run_traced "cvt_script $OPTS $f"
            done
        elif [[ $act == "wep" ]]; then
            do_wep
        else
            echo "Invalid command!"
            exit 1
        fi
    done
    [[ ! $act =~ $ACT2VME ]] && break
done
if [[ $act == "update+replace" ]]; then
    for pkg in $pypi tools; do
        do_replace
    done
elif [[ $act == "git-add" ]]; then
    srcdir="$HOME_DEVEL/pypi"
    [[ $PWD != $srcdir ]] && run_traced "cd $srcdir"
    run_traced "git status"
fi

