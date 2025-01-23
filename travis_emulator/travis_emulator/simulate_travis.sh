#!/usr/bin/env bash
__version__=2.0.10
if [[ -z "$1" || "$1" == "-h" ]]; then
    echo "$0 -I|-i     # install travis emulator environment (-i stable version, -I devel version)"
    echo "$0 srcdir    # copy src repository into local venv"
    echo "$0 -T        # execute travis test on current package"
    echo "$0 -V        # show version"
    exit 1
fi
if [[ "$1" == "-V" ]]; then
    echo $__version__
    exit 0
fi
if [[ $USER != "travis" ]]; then
    echo "This script works just with user travis"
    exit 1
fi
home_odoo=~odoo
home_travis=~travis
[[ ! -d $home_travis/bin ]] && mkdir $home_travis/bin
if [[ $(diff -q $home_travis/tools/travis_emulator/simulate_travis.sh $home_travis/bin/simulate_travis.sh) ]]; then
    cp $home_travis/tools/travis_emulator/simulate_travis.sh $home_travis/bin
    echo "Run again $0 $*"
    exit 1
fi
if [[ -n "$1" && ( "$1" == "-i" || "$1" == "-I" ) ]]; then
    clear
    rsync -az --delete $home_odoo/tools/ $home_travis/tools/
    sudo chown -R travis:travis $home_travis/tools
    if [[ "$1" == "-I" ]]; then
        for nm in clodoo lisa odoo_score os0 python_plus travis_emulator wok_code z0bug_odoo zar zerobug; do
            [[ -d $home_travis/$nm ]] && rm -fR $home_travis/$nm
            rm -fR $home_travis/tools/$nm
            cp -r $home_odoo/devel/pypi/$nm/$nm/ $home_travis/tools/$nm/
            sudo chown -R travis:travis $home_travis/tools/$nm
        done
    fi
    if [[ ! -f $home_travis/tools/travis_emulator/travis ]]; then
        echo "Travis emulator not found!"
        exit 1
    fi
    if [[ $(diff -q $home_travis/tools/travis_emulator/simulate_travis.sh $home_travis/bin/simulate_travis.sh) ]]; then
        echo "Run again $0 $*"
        exit 1
    fi
    for nm in travis_emulator/travis travis_emulator/travisrc python_plus/vem; do
        cp $home_travis/tools/$nm $home_travis/bin/
    done
    cd $home_travis/tools
    ./install_tools.sh -qfp
    [[ -f $$home_travis/devel/activate_tools ]] && . $home_travis/devel/activate_tools
    echo "Now you can type $0 PACKAGE"
elif [[ -n "$1" && $1 =~ ^[a-zA-Z] ]]; then
    clear
    $home_travis/bin/vem create virtualenv -D -p 2.7 -f -q
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
    sudo chown -R travis:travis $home_travis/virtualenv
    echo "Now you can type $0 -T"
elif [[ -n "$1" && "$1" == "-T" ]]; then
    clear
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
else
    echo "Invalid switch $1"
    exit 1
fi
