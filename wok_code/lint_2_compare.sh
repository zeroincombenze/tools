# set -x
match() {
# match(left right)
    local b l r
    l="$1"
    r="$2"
    [[ -e $l ]] && b=$(basename $l) || b=$(basename $r)
    [[ -f $l && $dry_run -eq 0 ]] && cp $l $LDIFFPATH/$b
    [[ -f $l && $dry_run -ne 0 ]] && echo cp $l $LDIFFPATH/$b
    [[ -f $r && $dry_run -eq 0 ]] && cp $r $RDIFFPATH/$b
    [[ -f $r && $dry_run -ne 0 ]] && echo cp $r $RDIFFPATH/$b
}

matchdir() {
# matchdir(left right)
    local b f l r LSAVED RSAVED
    l="$1"
    r="$2"
    [[ -e $l ]] && b=$(basename $l) || b=$(basename $r)
    if [[ -d $l ]]; then
        LSAVED="$LDIFFPATH"
        LDIFFPATH="$LDIFFPATH/$b"
        [[ ! -d $LDIFFPATH && $dry_run -eq 0 ]] && mkdir -p $LDIFFPATH
        [[ ! -d $LDIFFPATH && $dry_run -ne 0 ]] && echo mkdir -p $LDIFFPATH
        RSAVED="$RDIFFPATH"
        RDIFFPATH="$RDIFFPATH/$b"
        [[ ! -d $RDIFFPATH && $dry_run -eq 0 ]] && mkdir -p $RDIFFPATH
        [[ ! -d $RDIFFPATH && $dry_run -ne 0 ]] && echo mkdir -p $RDIFFPATH
        for f in $l/*; do
            b=$(basename $f)
            matchdir "$f" "$r/$b"
        done
        for f in $r/*; do
            b=$(basename $f)
            [[ ! -e $l/$b ]] && matchdir "$l/$b" "$f"
        done
        LDIFFPATH="$LSAVED"
        RDIFFPATH="$RSAVED"
    elif [[ ! $l =~ .pyc$ ]]; then
        match "$l" "$r"
    fi
}



tgtpath=""
srcpath=""
prm=""
sh_help=0
dry_run=0
diffcmd="diff"
ctr=0
while [[ -n $1 ]]; do
    if [[ -n "$prm" ]]; then
        eval $prm"=$1"
        prm=""
    elif [[ ! $1 =~ ^- ]]; then
        [[ $ctr -eq 1 ]] && tgtpath="$1" && ((ctr++))
        [[ $ctr -eq 0 ]] && srcpath="$1" && ((ctr++))
    else
        [[ $1 =~ -.*h ]] && sh_help=1
        [[ $1 =~ -.*m ]] && diffcmd="meld.exe"
        [[ $1 =~ -.*n ]] && dry_run=1
    fi
    shift
done
[[ $sh_help -ne 0 || -z $srcpath ]] && echo "$0 [-hmn] [srcpath] tgtpath" && exit 1
[[ -z $tgtpath ]] && tgtpath="$srcpath" && srcpath=$PWD
[[ -d $srcpath && ! -d $tgtpath ]] && echo "Incompatible $srdir and $tgtpath!" && exit 1
[[ -f $srcpath && ! -f $tgtpath ]] && echo "Incompatible $srdir and $tgtpath!" && exit 1
srcpath=$(readlink -e $srcpath)
tgtpath=$(readlink -e $tgtpath)
DIFFPATH="$HOME/tmp/diff"
[[ ! -d $DIFFPATH ]] && mkdir -p $DIFFPATH
xl=$srcpath
xr=$tgtpath
bl=""
br=""
while [[ -n $xl && -n $xr && $xr != $xl ]]; do
    bl=$(basename $xl)
    xl=$(dirname $xl)
    br=$(basename $xr)
    xr=$(dirname $xr)
done
[[ -z $bl ]] && bl="left"
[[ -z $br ]] && bl="right"
LDIFFPATH=$DIFFPATH/$bl
[[ $dry_run -eq 0 && -d $LDIFFPATH ]] && chmod -R +w $LDIFFPATH && rm -fR $LDIFFPATH
RDIFFPATH=$DIFFPATH/$br
[[ $dry_run -eq 0 && -d $RDIFFPATH ]] && chmod -R +w $RDIFFPATH && rm -fR $RDIFFPATH
[[ $dry_run -eq 0 ]] && mkdir $LDIFFPATH
[[ $dry_run -eq 0 ]] && mkdir $RDIFFPATH
matchdir "$srcpath" "$tgtpath"
[[ $dry_run -ne 0 ]] && echo $diffcmd $LDIFFPATH $RDIFFPATH && exit 0
black $LDIFFPATH
black $RDIFFPATH
chmod -R -w $LDIFFPATH
chmod -R -w $RDIFFPATH
eval $diffcmd $LDIFFPATH $RDIFFPATH
echo -e "\n\n\n\nNow you can compare the path $LDIFFPATH $RDIFFPATH"
exit 0

