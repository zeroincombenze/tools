#!/usr/bin/env bash
if [ -z "$1" -o "$1" == "-h" ]; then
    echo "sudo $0 -i|-I     # install travis emulator environment (-i stable version, -I devel version)"
    echo "sudo $0 srcdir    # copy src repository into local venv"
    echo "$0 -T             # Execute travis test on current package"
    exit 1
fi
home_odoo=/home/odoo
home_travis=/home/travis
[[ ! -d $home_travis/bin ]] && mkdir $home_travis/bin
if [[ -n "$1" && ( "$1" == "-i" || "$1" == "-I" ) ]]; then
    rsync -az --delete $home_odoo/tools/ $home_travis/tools/
    chown -R travis:travis $home_travis/tools
    if [[ "$1" == "-I" ]]; then
        for nm in clodoo devel_tools lisa odoo_score os0 python_plus travis_emulator wok_code z0bug_odoo zerobug; do
            [[ -d $home_travis/$nm ]] && rm -fR $home_travis/$nm
            rm -fR $home_travis/tools/$nm
            cp -r $home_odoo/devel/pypi/$nm/$nm/ $home_travis/tools/$nm/
            chown -R travis:travis $home_travis/tools/$nm
        done
    fi
    if [[ ! -f $home_travis/tools/travis_emulator/travis ]]; then
        echo "Travis emulator not found!"
        exit 1
    fi
    cd $home_travis/tools
    ./install_tools.sh -qp
    # [[ ! -L $home_travis/bin/travis ]] && ln -s $home_travis/tools/travis_emulator/travis $home_travis/bin
    # [[ ! -L $home_travis/bin/vem ]] && ln -s $home_travis/tools/python_plus/vem $home_travis/bin
elif [[ -n "$1" && ! "$1" == "-i" && ! "$1" == "-I"  && ! "$1" == "-T" ]]; then
    $home_travis/bin/vem create virtualenv -D -p 2.7 -f -q
    clear
    srcdir="$home_odoo/$1"
    if [[ ! -d "$srcdir" ]]; then
        echo "Source dir $srcdir not found!"
        exit 1
    fi
    mkdir $home_travis/virtualenv/build
    mkdir $home_travis/virtualenv/travis_log
    tgtdir="$home_travis/virtualenv/build/$1"
    [[ -d $tgtdir ]] && rm -fR $tgtdir
    cp -r $srcdir/ $tgtdir/
    chown -R travis:travis $home_travis/virtualenv
else
    cd $home_travis/virtualenv
    for d in $home_travis/virtualenv/build/*; do
        [[ -d $d ]] && tgtdir="$d" && break
    done
    if [[ -z "$tgtdir" ]]; then
        echo "No package to test!"
    else
        . bin/activate
        cd $tgtdir
        travis
        deactivate
    fi
fi
