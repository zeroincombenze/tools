#! /bin/bash
#
# Manage virtual environment
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2018-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# -----------------------------------------------------------------------------
# PIP features truth table depending on pip version (21.0 + only python3):
# option                                    |  18- | 18.0 | 19.0 | 20.0 | 21.0
# --disable-pip-version-check               |  OK  |  OK  |  OK  |  OK  |  OK
# --no-python-version-warning               |  OK  |  OK  |  OK  |  OK  |  OK
# --no-warn-conflicts                       |   X  |  OK  |  OK  |  OK  |  OK
# --use-features=(2020-resolver, fast-deps) |   X  |  OK  |  OK  |  no  |   X
# --use-features=in-tree-build              |   X  |   X  |   X  |   X  |  OK
# -----------------------------------------------------------------------------
# OK -> Use feature / X -> Feature unavailable / no -> Do use use
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 1.0.2.7
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
HOME_DEV="$HOME/devel"
[[ -x $TDIR/../bin/python ]] && PYTHON=$(readlink -f $TDIR/../bin/python) || [[ -x $TDIR/python ]] && PYTHON="$TDIR/python" || PYTHON="python"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\no=os.path\nHOME=os.environ.get('HOME');t=o.join(HOME,'tools')\nn=o.join(HOME,'pypi') if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME,HOME_DEV, 'pypi')\nd=HOME_DEV if o.basename(HOME_DEV)=='venv_tools' else o.join(HOME_DEV,'venv')\ndef apl(l,p,b):\n if p:\n  p2=o.join(p,b,b)\n  p1=o.join(p,b)\n  if o.isdir(p2):\n   l.append(p2)\n  elif o.isdir(p1):\n   l.append(p1)\nl=[TDIR]\nv=''\nfor x in sys.path:\n if not o.isdir(t) and o.isdir(o.join(x,'tools')):\n  t=o.join(x,'tools')\n if not v and o.basename(x)=='site-packages':\n  v=x\nfor x in os.environ['PATH'].split(':'):\n if x.startswith(d):\n  d=x\n  break\nfor b in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(d):\n  apl(l,d,b)\n elif TDIR.startswith(n):\n  apl(l,n,b)\n apl(l,v,b)\n apl(l,t,b)\nl=l+os.environ['PATH'].split(':')\ntdir=o.dirname(TDIR)\np=set()\npa=p.add\np=[x for x in l if x and (x.startswith(HOME) or x.startswith(HOME_DEV) or x.startswith(tdir)) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found in <$PYPATH>!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"

DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=1.0.5

declare -A PY3_PKGS
NEEDING_PKGS="future clodoo configparser os0 z0lib"
DEV_PKGS="click coveralls codecov flake8 pycodestyle pylint"
SUP_PKGS="future python-plus"
SECURE_PKGS="urllib3[secure] cryptography pyOpenSSL idna certifi asn1crypto pyasn1"
EI_PKGS="(distribute)"
BZR_PKGS="(aeroolib)"
WGET_PKGS="(pychart|python-chart)"
GIT_PKGS="(openupgradelib|prestapyt)"
PYBIN_PKGS="(dateutil|ldap|openid)"
BIN_PKGS="(wkhtmltopdf|lessc)"
FLT_PKGS="(jwt|FOO)"
ERROR_PKGS=""
LOCAL_PKGS="(clodoo|odoo_score|os0|python_plus|z0bug_odoo|z0lib|zerobug)"
XPKGS_RE=""
PY3_PKGS[jsonlib]="jsonlib-python3"
RED="\e[31m"
CLR="\e[0m"

push_venv() {
    # push_venv(VENV)
    [[ $opt_verbose -gt 2 ]] && echo ">>> push_venv($*)"
    local f=0 i
    ((i=${#VENV_STACK[@]}))
    [[ $f -eq 0 ]] && VENV_STACK[$i]="$1"
    export VENV_STACK
}

pop_venv() {
    # pop_venv(VENV)
    [[ $opt_verbose -gt 2 ]] && echo ">>> pop_venv($*)"
    ((i=${#VENV_STACK[@]} - 2))
    if [[ $i -ge 0 && -n "${VENV_STACK[$i]}" ]]; then
      VIRTUAL_ENV=${VENV_STACK[$i]}
      unset VENV_STACK[$i]
    else
      unset VIRTUAL_ENV
    fi
    [[ $opt_verbose -gt 2 ]] && echo ">>> VIRTUAL_ENV=$VIRTUAL_ENV"
    export VENV_STACK
}

do_activate() {
  # do_activate(VENV -q)
  local i f VENV_DIR="$1"
  [[ $opt_verbose -gt 2 ]] && echo ">>> VIRTUAL_ENV=$VIRTUAL_ENV" && echo ">>> do_activate($*)"
  if [[ -z "$VIRTUAL_ENV" || $VIRTUAL_ENV != $VENV_DIR ]]; then
    [[ $opt_verbose -ge 3 || ( ! ${2}z =~ q && $opt_verbose -ne 0 ) ]] && echo "$FLAG source $VENV_DIR/bin/activate"
    [[ ! -f $VENV_DIR/bin/activate ]] && echo "Fatal error! bin/activate not found in $(readlink -f $VENV_DIR)" && exit 1
    [[ $opt_verbose -gt 3 ]] && set +x
    . $VENV_DIR/bin/activate
    [[ $opt_verbose -ge 3 && -n $NVM_DIR && -f $NVM_DIR/nvm.sh ]] && echo "$FLAG source $NVM_DIR/nvm.sh"
    [[ -n $NVM_DIR && -f $NVM_DIR/nvm.sh ]] && . $NVM_DIR/nvm.sh
    [[ $opt_verbose -gt 3 ]] && set -x
    push_venv "$1"
  fi
}

do_deactivate() {
  local i VENV
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_deactivate($*)"
  if [[ -n "$VIRTUAL_ENV" ]]; then
    [[ $opt_verbose -ge 3 || ( ! $1 =~ q && $opt_verbose -ne 0 ) ]] && echo "$FLAG deactivate"
    [[ "$(type -t deactivate)" == "function" ]] && deactivate
    pop_venv
  fi
}

run_traced() {
  local xcmd="$1"
  local sts=0
  local PMPT=
  [[ $opt_dry_run -ne 0 ]] && PMPT="> " || PMPT="\$ "
  [[ $opt_verbose -lt 2 ]] || echo "$PMPT$xcmd"
  [[ $opt_dry_run -ne 0 ]] || eval $xcmd
  sts=$?
  return $sts
}

get_actual_pkg() {
  local pkg=$1
  [[ $pkg == "pychart" ]] && pkg="python-chart"
  [[ $pkg =~ ^(psycopg2).* ]] && pkg="psycopg2-binary>=2.0.0"
  [[ $pkg =~ ^$PYBIN_PKGS([<=>!][0-9.]+)?$ ]] && pkg="python-$pkg"
  [[ $opt_pyver =~ ^3 && $pkg =~ ^${!PY3_PKGS[*]}$ ]] && pkg=${PY3_PKGS[$pkg]}
  echo $pkg
}

get_local_version() {
  # grep "version" ./setup.py|awk -F= '{print $2}'|tr -d "'"|tr -d ","
  python ./setup.py --version
}

get_pkg_wo_version() {
  pkg=$(echo "$1"|grep -Eo '[^!<=>\\[]*'|head -n1)
  echo $pkg
}


get_wkhtmltopdf_dwname() {
  #get_wkhtmltopdf_dwname(pkg FH dist MACHARCH)
  local pkg=$1 FH=$2 dist=$3 MACHARCH=$4 pkgext wkhtmltopdf_wget x y z
  dist=${dist,,}
  [[ $dist =~ debian ]] && y="_" || y="-"
  [[ "$FH" == "RHEL" ]] && x="." || x="_"
  [[ $dist =~ (redhat|fedora) ]] && dist="centos7"
  [[ "$dist" == "ubuntu20" ]] && dist="focal"
  [[ "$dist" == "ubuntu18" ]] && dist="bionic"
  [[ "$dist" == "ubuntu16" ]] && dist="xenial"
  [[ "$dist" == "ubuntu14" ]] && dist="trusty"
  [[ "$dist" == "debian10" ]] && dist="buster"
  [[ "$dist" == "debian9" ]] && dist="stretch"
  [[ "$dist" == "debian8" ]] && dist="jessie"
  [[ "$FH" == "RHEL" ]] && pkgext=".rpm" || pkgext=".deb"
  [[ "$FH" == "Debian" && "$MACHARCH" == "x86_64" ]] && MACHARCH="amd64"
  reqver=$(echo "$pkg" | grep -Eo '[^!<=>]*' | tr -d "'" | sed -n '2 p')
  [[ -z "$reqver" ]] && reqver="0.12.5"
  [[ "$FH" == "RHEL" && "$MACHARCH" == "x86_64" && $reqver =~ 0.12.[14] ]] && MACHARCH="amd64"
  z="wkhtmltopdf"
  if [[ ${reqver} =~ 0.12.6 ]]; then
    reqver="0.12.6-1"
    z="packaging"
    wkhtmltopdf_wget="wkhtmltox${y}${reqver}.${dist}${x}${MACHARCH}${pkgext}"
  elif [[ ${reqver} == "0.12.5" ]]; then
    wkhtmltopdf_wget="wkhtmltox${y}${reqver}-1.${dist}${x}${MACHARCH}${pkgext}"
  elif [[ ${reqver} == "0.12.4" ]]; then
    wkhtmltopdf_wget="wkhtmltox-${reqver}_linux-generic-${MACHARCH}.tar.xz"
  else
    wkhtmltopdf_wget="wkhtmltox-${reqver}_linux-${dist}-${MACHARCH}${pkgext}"
  fi
  echo "https://github.com/wkhtmltopdf/${z}/releases/download/${reqver}/${wkhtmltopdf_wget}"
}

set_hashbang() {
    #set_hashbang(venv)
    local cmd d f mime V VENV_TGT
    V="$1"
    d=$(find $V \( -type f -executable -o -name "*.py" \)|tr "\n" " ")
    for f in $d; do
      grep -Eq "^#\!.*/bin.*python[23]?$" $f &>/dev/null && run_traced "sed -E \"s|^#\!.*/bin.*python[23]?|#\!$PYTHON|\" -i $f" && chmod +x $f
    done
}

bin_install() {
  # bin_install(pkg)
  [[ $opt_verbose -gt 2 ]] && echo ">>> bin_install($*)"
  local x
  local reqver size
  local FH=$(xuname -f)
  local MACHARCH=$(xuname -m)
  local dist=$(xuname -d)
  dist=${dist,,}$(xuname -v | grep -Eo "[0-9]*" | head -n1)
  local pkg=$1
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    if [[ $pkg =~ lessc ]]; then
      [[ $pkg == "lessc" ]] && pkg="less@3.0.4"
      pkg=${pkg/==/@}
      pkg=$(echo $pkg | tr -d "'")
      run_traced "npm install $pkg"
      run_traced "npm install less-plugin-clean-css"
      x=$(find $(npm bin) -name lessc 2>/dev/null)
      [[ -n "$x" ]] && run_traced "ln -s $x $VENV/bin"
    elif [[ $pkg =~ wkhtmltopdf ]]; then
      mkdir wkhtmltox.rpm_files
      pushd wkhtmltox.rpm_files >/dev/null
      wkhtmltopdf_wget=$(get_wkhtmltopdf_dwname $pkg $FH $dist $MACHARCH)
      pkgext=$(echo wkhtmltopdf_wget | grep -Eo ".xz$")
      [[ -z "$pkgext" ]] && pkgext=${wkhtmltopdf_wget: -4}
      [[ $opt_verbose -gt 0 ]] && echo "Download ${wkhtmltopdf_wget}"
      wget -q --timeout=240 ${wkhtmltopdf_wget} -O wkhtmltox${pkgext}
      size=$(stat -c %s wkhtmltox${pkgext})
      if [ $size -eq 0 ]; then
        echo "File wkhtmltox${pkgext} not found!"
      elif [ "$pkgext" == ".rpm" ]; then
        run_traced "rpm2cpio wkhtmltox${pkgext} | cpio -idm"
        run_traced "cp ./usr/local/bin/wkhtmltopdf ${VENV}/bin/wkhtmltopdf"
      elif [ "$pkgext" == ".deb" ]; then
        run_traced "dpkg --extract wkhtmltox${pkgext} wkhtmltox.deb_files"
        run_traced "cp wkhtmltox.deb_files/usr/local/bin/wkhtmltopdf ${VENV}/bin/wkhtmltopdf"
        run_traced "rm -r wkhtmltox.deb*"
      else
        run_traced "tar -xf wkhtmltox${pkgext}"
        run_traced "cp ./wkhtmltox/bin/wkhtmltopdf ${VENV}/bin/wkhtmltopdf"
        run_traced "rm -fr ./wkhtmltox"
      fi
      popd >/dev/null
      rm -fR wkhtmltox.rpm_files
    fi
    x="${pkgs//+/.}"
    [[ -z $XPKGS_RE ]] && XPKGS_RE="$x" || XPKGS_RE="$XPKGS_RE|$x"
  fi
}

bin_install_1() {
  # bin_install_1()
  [[ $opt_verbose -gt 2 ]] && echo ">>> bin_install_1($*)"
  local pkg
  local binreq bin_re
  [[ -n "$opt_bins" ]] && binreq="${opt_bins//,/ }"
  if [[ -n "$opt_bins" ]]; then
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m.Analyzing $opt_bins\e[0m"
    for pkg in $binreq; do
      bin_install $pkg
    done
  fi
}

pip_install() {
  #pip_install(pkg opts)
  local pkg d x srcdir pfn popts pypath v tmpdir
  pypath=$(find $VIRTUAL_ENV/lib -type d -name "python$opt_pyver")
  [[ -n "$pypath" && -d $pypath/site-packages ]] && pypath=$pypath/site-packages || pypath=$(find $(readlink -f $(dirname $(which $PYTHON))/../lib) -type d -name site-packages)
  tmpdir=$VIRTUAL_ENV/tmp
  pkg="$(get_actual_pkg $1)"
  [[ $pkg =~ "-e " ]] && pkg=${pkg//-e /--editable=}
  [[ $opt_alone -ne 0 && ! $pkg =~ ^.?- ]] && popts="--isolated --disable-pip-version-check --no-python-version-warning --no-cache-dir" || popts="--disable-pip-version-check --no-python-version-warning"
  [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
  [[ $PIPVER -eq 19 && ! 2020-resolver =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
  [[ $opt_verbose -lt 2 ]] && popts="$popts -q"
  [[ $opt_verbose -ne 0 && PRINTED_PIPVER -eq 0 ]] && echo "# $PIP.$PIPVER $popts ..." && PRINTED_PIPVER=1
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    if [[ ! $pkg =~ $BIN_PKGS ]]; then
      srcdir=""
      [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg//-/_} || pfn=$pkg
      [[ $opt_debug -eq 2 && -d $SAVED_HOME/tools/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME/tools/$pfn)
      if [[ $opt_debug -ge 3 ]]; then
        [[ -d $SAVED_HOME/devel/pypi/$pfn/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME/devel/pypi/$pfn/$pfn)
      fi
      if [[ $pkg =~ ^(odoo|openerp)$ && -z $opt_oepath ]]; then
        echo "Missed Odoo version to install (please use -O and -o switches)!"
        exit 1
      fi
      [[ $pkg =~ ^(odoo|openerp)$ && -n $opt_oepath ]] && srcdir=$(odoo_orm_path $opt_oepath)
      if [[ $pkg =~ ^(odoo|openerp)$ && -z $srcdir ]]; then
        echo "Odoo path not found! Please supply path with -o switch)!"
        exit 1
      fi
    fi
    if [[ $pkg =~ $BIN_PKGS ]]; then
      bin_install "$pkg"
    elif [[ -n "$srcdir" ]]; then
      [[ -d $pypath/$pfn && ! -L $pypath/$pfn ]] && run_traced "rm -fR $pypath/$pfn"
      [[ -L $pypath/$pfn ]] && run_traced "rm -f $pypath/$pfn"
      if [[ $opt_debug -eq 2 ]]; then
        [[ ! -d $tmpdir ]] && run_traced "mkdir $tmpdir"
        run_traced "mkdir -p $tmpdir/$pfn"
        run_traced "cp -r $srcdir $tmpdir/$pfn/"
        run_traced "mv $tmpdir/$pfn/$pfn/setup.py $tmpdir/$pfn/setup.py"
        x=$(grep -A3 -E "^ *package_data" $tmpdir/$pfn/setup.py|grep -Eo "\./README.rst")
        # [[ $x == "\./README.rst" ]] && run_traced "mv $tmpdir/$pfn/$pfn/README.rst $tmpdir/$pfn/README.rst"
        [[ $PIPVER -ge 21 ]] && run_traced "$PIP install $tmpdir/$pfn --use-feature=in-tree-build $popts" || run_traced "$PIP install $tmpdir/$pfn $popts"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        run_traced "rm -fR $tmpdir/$pfn"
      elif [[ $opt_debug -eq 3 ]]; then
        [[ $PIPVER -ge 21 ]] && run_traced "$PIP install $(dirname $srcdir) --use-feature=in-tree-build $popts" || run_traced "$PIP install $(dirname $srcdir) $popts"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        pushd $srcdir/.. >/dev/null
        [[ $pkg =~ ^(odoo|openerp)$ ]] && x="$opt_oever" || x=$(get_local_version $pfn)
        v=$([[ $(echo $x|grep "mismatch") ]] && echo $x|awk -F/ '{print $2}' || echo $x)
        popd >/dev/null
        x=$(ls -d $pypath/${pfn}-*dist-info 2>/dev/null|grep -E "${pfn}-[0-9.]*dist-info")
        [[ -n $x && $x != $pypath/${pfn}-${v}.dist-info ]] && run_traced "mv $x $pypath/${pfn}-${v}.dist-info"
        if [[ ! -d $pypath/${pfn}-${v}.dist-info ]]; then
          run_traced "mkdir $pypath/${pfn}-${v}.dist-info"
          for d in INSTALLER METADATA RECORD REQUESTED top_level.txt WHEEL; do
            run_traced "touch $pypath/${pfn}-${v}.dist-info/$d"
          done
        fi
        run_traced "ln -s $srcdir $pypath/$pfn"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      fi
      # TODO> ?
      # set_hashbang "$pypath/${pfn}"
      [[ -x $VIRTUAL_ENV/bin/${pkg}-info ]] && run_traced "$VIRTUAL_ENV/bin/${pkg}-info --copy-pkg-data"
    elif [[ $pkg =~ $EI_PKGS ]]; then
      run_traced "easy_install install $pkg"
      run_traced "$PIP install $popts --upgrade $pkg"
    elif [[ $pkg =~ $WGET_PKGS ]]; then
      d=""
      [[ $pkg == "python-chart" ]] && d="https://files.pythonhosted.org/packages/22/bf/f37ecd52d9f6ce81d4372956dc52c792de527abfadbf8393dd25deb5c90b/Python-Chart-1.39.tar.gz"
      [[ -z "$d" ]] && echo "Unknown URL for $pkg" && return
      x=$(basename $d)
      run_traced "mkdir -p $VIRTUAL_ENV/tmp"
      run_traced "cd $VIRTUAL_ENV/tmp"
      [[ -f $x ]] && run_traced "rm -f $x"
      run_traced "wget $d"
      run_traced "$PIP install $popts $x"
    elif [[ $pkg =~ $GIT_PKGS ]]; then
      d=""
      [[ $pkg =~ "openupgradelib" ]] && d="git+https://github.com/OCA/openupgradelib.git"
      [[ $pkg =~ "prestapyt" ]] && d="git+https://github.com/prestapyt/prestapyt.git@master"
      [[ -z "$d" ]] && echo "Unknown URL for $pkg" && return
      run_traced "$PIP install $d"
    elif [[ $pkg =~ $BZR_PKGS ]]; then
      x=$(which bzr 2>/dev/null)
      if [[ -z "$x" ]]; then
        echo "Package $pkg require bazar software but this software is not installed on your system"
        echo "You should install bazar ..."
        DISTO=$(xuname -d)
        FH=$(xuname -f)
        [[ $DISTO == "Fedora" ]] && echo "dnf install bzr"
        [[ $DISTO != "Fedora" && $FH == "RHEL" ]] && echo "yum install bzr"
        [[ $DISTO == "Debian" ]] && echo "apt -t lenny-backports install bzr"
        [[ $DISTO == "Ubuntu" ]] && echo "add-apt-repository ppa:bzr/ppa"
        [[ $FH == "Debian" ]] && echo "apt update"
      else
        run_traced "mkdir -p $HOME/bazar"
        run_traced "cd $HOME/bazar"
        run_traced "bzr branch lp:$pkg"
        d=$(find $pkg -name setup.py | head -n1)
        [[ -n "$d" ]] && d=$(dirname $d) || d=""
        if [[ -n "$d" && -d "$d" ]]; then
          run_traced "cd $d"
          run_traced "python ./setup.py install"
        else
          echo "Invalid bazar package: file setup.py not found!"
        fi
      fi
    elif [[ $opt_debug -eq 1 ]]; then
      [[ -L $pypath/$pkg ]] && rm -f $pypath/$pkg
      run_traced "$PIP install $popts --extra-index-url https://testpypi.python.org/pypi $pkg $2"
      [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
    else
      [[ -L $pypath/$pkg ]] && rm -f $pypath/$pkg
      run_traced "$PIP install $popts $pkg $2"
      [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
    fi
    x="${pkgs//+/.}"
    [[ -z $XPKGS_RE ]] && XPKGS_RE="$x" || XPKGS_RE="$XPKGS_RE|$x"
  fi
}

pip_install_1() {
  # pip_install_1(popts)
  local pkg popts
  [[ $opt_verbose -lt 2 ]] && popts="$1 -q" || popts="$1"
  [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m2 - Analyzing $SUP_PKGS $SECURE_PKGS $DEV_PKGS\e[0m (1)"
  for pkg in $SUP_PKGS $SECURE_PKGS $DEV_PKGS; do
    [[ $opt_verbose -lt 2 ]] && echo -en "."
    pip_install "$pkg" "$popts"
  done
  [[ $opt_verbose -lt 2 ]] && echo -en "\r"
}

pip_install_2() {
  # pip_install_2(popts)
  local pkg
  [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m3 - Analyzing $OEPKGS\e[0m (2)"
  for pkg in $OEPKGS; do
    pip_install "$pkg" "$1"
  done
}

pip_install_req() {
  # pip_install_req(popts)
  local f pfn pkg flist cmd
  for f in ${opt_rfile//,/ }; do
    pfn=$(readlink -f $f)
    [ -z "$pfn" ] && echo "File $f not found!"
    [ -z "$pfn" ] && continue
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing file $pfn\e[0m"
    cmd="$LIST_REQ -qt python -BP"
    [[ $opt_dev -ne 0 ]] && cmd="${cmd}TR"
    [[ -n "$opt_pyver" ]] && cmd="$cmd -y$opt_pyver"
    [[ -n "$opt_oever" ]] && cmd="$cmd -b$opt_oever"
    [[ -d $HOME/OCA ]] && cmd="$cmd -d${HOME}/OCA"
    [[ $opt_verbose -gt 1 ]] && echo "$cmd -m $pfn -qs\" \""
    flist=$($cmd -m $pfn -qs" ")
    [[ $opt_verbose -gt 2 ]] && echo "flist=$flist"
    for pkg in $flist; do
      pip_install "$pkg" "$1"
    done
  done
}

pip_uninstall() {
  #pip_uninstall(pkg opts)
  local pkg d x srcdir pfn popts v
  local pypath=$VIRTUAL_ENV/lib/python$opt_pyver/site-packages
  pkg=$(get_pkg_wo_version $(get_actual_pkg $1))
  [[ $opt_verbose -eq 0 ]] && popts="$popts -q"
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    srcdir=""
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg//-/_} || pfn=$pkg
    [[ $opt_debug -eq 2 && -d $SAVED_HOME/tools/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME/tools/$pfn)
    [[ $opt_debug -eq 3 && -d $SAVED_HOME/dev/pypi/$pfn/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME/dev/pypi/$pfn/$pfn)
    [[ $opt_debug -eq 3 && -d $SAVED_HOME/pypi/$pfn/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME/pypi/$pfn/$pfn)
    if [[ -n "$srcdir" ]]; then
      [[ -d $pypath/$pfn && ! -L $pypath/$pfn ]] && run_traced "rm -fR $pypath/$pfn"
      pushd $srcdir/.. >/dev/null
      [[ $pkg =~ ^(odoo|openerp)$ ]] && x="$opt_oever" || x=$(get_local_version $pfn)
      v=$([[ $(echo $x|grep "mismatch") ]] && echo $x|awk -F/ '{print $2}' || echo $x)
      popd >/dev/null
      x=$(ls -d $pypath/${pfn}-*dist-info 2>/dev/null|grep -E "${pfn}-[0-9.]*dist-info")
      [[ -n $x && $x != $pypath/${pfn}-${v}.dist-info ]] && run_traced "rm $x"
    else
      [[ -L $pypath/$pkg ]] && rm -f $pypath/$pkg
      run_traced "$PIP uninstall $popts $pkg $2"
      [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
    fi
    x="${pkgs//+/.}"
    [[ -z $XPKGS_RE ]] && XPKGS_RE="$x" || XPKGS_RE="$XPKGS_RE|$x"
  fi
}

check_bin_package() {
  # check_bin_package(pkg)
  local op reqver xreqver sts curver vpkg x
  local vpkg=$1

  op=$(echo "$vpkg" | grep -Eo '[!<=>]*' | head -n1)
  pkg=$(echo "$vpkg" | grep -Eo '[^!<=>\\[]*' | tr -d "'" | head -n1)
  reqver=$(echo "$vpkg" | grep -Eo '[^!<=>]*' | tr -d "'" | sed -n '2 p')
  [ -n "$reqver" ] && xreqver=$(echo $reqver | grep -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xreqver=0
  sts=0
  curver=$($pkg --version 2>/dev/null | grep -Eo "[0-9]+\.[0-9]+\.?[0-9]*x" | head -n1)
  if [[ -n "$reqver" ]]; then
    if [[ -z "$curver" ]]; then
      echo "Package $pkg not installed!!!"
      if [[ "$cmd" == "amend" ]]; then
        bin_install "$vpkg"
        [ $? -ne 0 ] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      fi
    else
      [ -n "$curver" ] && xcurver=$(echo $curver | grep -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xcurver=0
      if [[ -z "$op" ]] || [ $xcurver -ne $xreqver -a "$op" == '==' ] || [ $xcurver -ge $xreqver -a "$op" == '<' ] || [ $xcurver -le $xreqver -a "$op" == '>' ] || [ $xcurver -lt $xreqver -a "$op" == '>=' ] || [ $xcurver -gt $xreqver -a "$op" == '<=' ]; then
        echo "Package $pkg version $curver but expected $pkg$op$reqver!!!"
        if [[ "$cmd" == "amend" ]]; then
          bin_install "$vpkg"
          [ $? -ne 0 ] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        else
          ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        fi
      else
        printf "Package %-40.40s OK\n" "${pkg}${op}${curver}........................................"
      fi
    fi
  else
    if [[ -n "$curver" ]]; then
      printf "Package %-40.40s OK\n" "${pkg}........................................"
    else
      echo "Package $pkg not installed!!!"
      ERROR_PKGS="$ERROR_PKGS   '$pkg'"
    fi
  fi
  if [[ -n "$curver" ]]; then
    x=$(readlink -e $(which $pkg 2>/dev/null) 2>/dev/null)
    [[ -z "$x" ]] && echo "Corrupted VME: file $pkg not found!!"
    if [[ -n "$x" && ! $x =~ ^$VENV && ! -L $VENV/bin/$pkg ]]; then
      [[ $opt_verbose -gt 0 ]] && echo "Warning: file $x is outside of virtual env"
      run_traced "ln -s $x $VENV/bin"
    fi
  fi
}

bin_check_1() {
  # bin_check(cmd VENV)
  local pkg
  local binreq bin_re
  [[ -n "$opt_bins" ]] && binreq="${opt_bins//,/ }"
  [[ -z "$opt_bins" ]] && binreq="${BIN_PKGS//|/ }" && binreq="${binreq:1:-1}"
  [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing bin $binreq\e[0m"
  for pkg in $binreq; do
    check_bin_package $pkg
  done
}

check_package() {
  # check_package(pkg cmd)
  local op reqver xreqver sts curver vpkg x
  local vpkg="$(get_actual_pkg $1)"

  op=$(echo "$vpkg" | grep -Eo '[!<=>]*' | head -n1)
  pkg=$(echo "$vpkg" | grep -Eo '[^!<=>\\[]*' | tr -d "'" | head -n1)
  reqver=$(echo "$vpkg" | grep -Eo '[^!<=>]*' | tr -d "'" | sed -n '2 p')
  [[ -n "$reqver" ]] && xreqver=$(echo $reqver | grep -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xreqver=0
  sts=0
  if [[ -n "$reqver" ]]; then
    curver=$($PIP show $pkg | grep "^[Vv]ersion" | awk -F: '{print $2}' | tr -d ', \r\n\(\)') || curver=
    if [[ -z "$curver" ]]; then
      echo "Package $pkg not installed!!!"
      if [[ "$cmd" == "amend" ]]; then
        pip_install "$vpkg"
        [ $? -ne 0 ] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      fi
    else
      [[ -n "$curver" ]] && xcurver=$(echo $curver | grep -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xcurver=0
      if [[ -z "$op" ]] || [ $xcurver -ne $xreqver -a "$op" == '==' ] || [ $xcurver -ge $xreqver -a "$op" == '<' ] || [ $xcurver -le $xreqver -a "$op" == '>' ] || [ $xcurver -lt $xreqver -a "$op" == '>=' ] || [ $xcurver -gt $xreqver -a "$op" == '<=' ]; then
        echo "Package $pkg version $curver but expected $pkg$op$reqver!!!"
        if [[ "$cmd" == "amend" ]]; then
          pip_install "$vpkg" "--upgrade"
          [ $? -ne 0 ] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        else
          ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        fi
      else
        printf "Package %-40.40s OK\n" "${pkg}${op}${reqver}........................................"
      fi
    fi
  else
    eval $PIP show $pkg &>/dev/null
    if [ $? -eq 0 ]; then
      printf "Package %-40.40s OK\n" "${pkg}........................................"
    else
      echo "Package $pkg not installed!!!"
      if [[ "$cmd" == "amend" ]]; then
        pip_install "$vpkg"
        [ $? -ne 0 ] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      fi
    fi
  fi
  x=$($PIP show $pkg | grep "^[Ll]ocation" | awk -F: '{print $2}' | tr -d ', \r\n\(\)')
  [[ -n "$x" && ! $x =~ ^$VENV ]] && echo "Warning: file $x is outside of virtual env"
}

pip_check_1() {
  # pip_check_1(cmd)
  local pkg cmd=$1
  local op reqver xreqver sts curver vpkg
  [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m1 - Analyzing\e[0m"
  for vpkg in $SUP_PKGS $SECURE_PKGS $DEV_PKGS; do
    check_package $vpkg $cmd
  done
}

pip_check_2() {
  # pip_check_2(cmd)
  local pkg cmd=$1
  [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m2 - Analyzing\e[0m"
  for vpkg in $OEPKGS; do
    check_package $vpkg $cmd
  done
}

pip_check_req() {
  # pip_check_req(cmd)
  local f pfn pkg cmd=$1 flist cmd
  for f in ${opt_rfile//,/ }; do
    pfn=$(readlink -f $f)
    [ -z "$pfn" ] && echo "File $f not found!"
    [ -z "$pfn" ] && continue
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing file $pfn\e[0m"
    cmd="$LIST_REQ -qt python -BP"
    [[ $opt_dev -ne 0 ]] && cmd="${cmd}TR"
    [[ -n "$opt_pyver" ]] && cmd="$cmd -y$opt_pyver"
    [[ -n "$opt_oever" ]] && cmd="$cmd -b$opt_oever"
    [[ -d $HOME/OCA ]] && cmd="$cmd -d${HOME}/OCA"
    [[ $opt_verbose -gt 1 ]] && echo "$cmd -m $pfn -qs\" \""
    flist=$($cmd -m $pfn -qs" ")
    [[ $opt_verbose -gt 1 ]] && echo "--> $flist"
    for pkg in $flist; do
      check_package $pkg $cmd
    done
  done
}

package_debug() {
  # package_debug()
  local pkg pkgdir
  local pkgs="${LOCAL_PKGS//|/ }"
  pkgs="${pkgs:1:-1}"
  [[ -d $HOME/devel/pypi ]] && pkgdir=$HOME/devel/pypi
  if [[ -n "$pkgdir" ]]; then
    for pkg in $pkgs; do
      [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pkg=${pkg//-/_} || pkg=$pkg
      if [[ -d $pkgdir/$pkg/$pkg && ! :$PYTHONPATH: =~ :$pkgdir/$pkg/$pkg: ]]; then
        [[ -n "$PYTHONPATH" ]] && export PYTHONPATH=$pkgdir/$pkg:$PYTHONPATH || export PYTHONPATH=$pkgdir/$pkg
      fi
    done
  fi
}

custom_env() {
  # custom_env(VENV pyver)
  [[ $opt_verbose -gt 2 ]] && echo ">>> custom_env($*)"
  local VIRTUAL_ENV=$1 pyver=$(echo $2|grep -Eo "[0-9]"|head -n1)
  sed -e 's:VIRTUAL_ENV=.*:VIRTUAL_ENV="\$(dirname \$(dirname \$(readlink -f \$BASH_SOURCE[0])))":g' -i $VIRTUAL_ENV/bin/activate
  if $(grep -q "^export HOME=" $VIRTUAL_ENV/bin/activate); then
    sed -e 's|^export HOME=.*|export HOME="\$VIRTUAL_ENV"|g' -i $VIRTUAL_ENV/bin/activate
  elif $(grep -q "^# export HOME=" $VIRTUAL_ENV/bin/activate); then
    sed -e 's|^# export HOME=.*|# export HOME="\$VIRTUAL_ENV"|g' -i $VIRTUAL_ENV/bin/activate
  else
    sed -r "/deactivate *\(\) *\{/i\READLINK=\$(which greadlink 2>/dev/null) || READLINK=\$(which readlink 2>/dev/null)" -i $VIRTUAL_ENV/bin/activate
    sed -r "/deactivate *\(\) *\{/i\export READLINK\n" -i $VIRTUAL_ENV/bin/activate
    [[ $opt_alone -gt 1 ]] && sed -r "/deactivate *\(\) *\{/a\    export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" -i $VIRTUAL_ENV/bin/activate
    [[ $opt_alone -le 1 ]] && sed -r "/deactivate *\(\) *\{/a\    # export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" -i $VIRTUAL_ENV/bin/activate
    [[ $opt_alone -gt 1 ]] && echo "export HOME=\"\$VIRTUAL_ENV\"" >>$VIRTUAL_ENV/bin/activate
    [[ $opt_alone -le 1 ]] && echo "# export HOME=\"\$VIRTUAL_ENV\"" >>$VIRTUAL_ENV/bin/activate
#    echo "for f in \$VIRTUAL_ENV/bin/*;do" >>$VIRTUAL_ENV/bin/activate
#    echo "    [[ -x \$f && ! -d \$f ]] && grep -q \"^#\!.*[ /]python\" \$f &>/dev/null && sed -i -e \"s|^#\!.*[ /]python|#\!\$VIRTUAL_ENV/bin/python|\" \$f" >>$VIRTUAL_ENV/bin/activate
#    echo "done" >>$VIRTUAL_ENV/bin/activate
  fi
  sed -e 's|PATH="\$VIRTUAL_ENV/bin:\$PATH"|PATH="\$VIRTUAL_ENV/.local/bin:\$VIRTUAL_ENV/bin:\$PATH"|g' -i $VIRTUAL_ENV/bin/activate
  if [[ $opt_spkg -ne 0 ]]; then
    if [[ -d $VIRTUAL_ENV/.local/lib/python$2/site-packages ]]; then
      echo -e "import site\nsite.addsitedir('$VIRTUAL_ENV/.local/lib/python$2/site-packages')\nsite.addsitedir('/usr/lib/python$2/site-packages')\nsite.addsitedir('/usr/lib64/python$2/site-packages')\n" >$VIRTUAL_ENV/lib/python$2/site-packages/sitecustomize.py
    else
      echo -e "import site\nsite.addsitedir('/usr/lib/python$2/site-packages')\nsite.addsitedir('/usr/lib64/python$2/site-packages')\n" >$VIRTUAL_ENV/lib/python$2/site-packages/sitecustomize.py
    fi
  elif [[ -d $VIRTUAL_ENV/.local/lib/python$2/site-packages ]]; then
    echo -e "import site\nsite.addsitedir('$VIRTUAL_ENV/.local/lib/python$2/site-packages')\n" >$VIRTUAL_ENV/lib/python$2/site-packages/sitecustomize.py
  fi
}

find_cur_py() {
    PYTHON=""
    PIP=""
    PIPVER=""
    if [[ -n "$opt_pyver" ]]; then
      PYTHON=$(which python$opt_pyver 2>/dev/null)
      [[ -z "$PYTHON" && $opt_pyver =~ ^3 ]] && PYTHON=python3
      [[ -z "$PYTHON" && $opt_pyver =~ ^2 ]] && PYTHON=python2
      PYTHON=$(which $PYTHON 2>/dev/null)
      [[ -z "$PYTHON" ]] && PYTHON=$(which python 2>/dev/null)
      opt_pyver=$($PYTHON --version 2>&1 | grep -o "[0-9]\.[0-9]" | head -n1)
      PIP=$(which pip$opt_pyver 2>/dev/null)
      [[ -z $PIP ]] && PIP="$PYTHON -m pip"
    else
      PYTHON=$(which python 2>/dev/null)
      opt_pyver=$($PYTHON --version 2>&1 | grep -o "[0-9]\.[0-9]" | head -n1)
      PIP=$(which pip 2>/dev/null)
      [[ -z $PIP ]] && PIP="$PYTHON -m pip"
    fi
}

venv_mgr_check_src_path() {
  # venv_mgr_check_src_path(VENV)
  [[ $opt_verbose -gt 2 ]] && echo ">>> venv_mgr_check_src_path($*)"
  local f VENV
  VENV="$1"
  if [[ -z "$VENV" ]]; then
    for f in $(find . -max-depth 2 -type f -not -path "*/.*/*" -not -name ".*" -name activate); do
      [[ -d $f/../lib && -d $f/../bin ]] && VENV=$(readlink -e $f/../..) && break
    done
  fi
  if [[ -z "$VENV" ]]; then
    echo "Missed virtual environment path!!"
    exit 1
  fi
  if [[ ! -d $VENV || ! -d $VENV/lib || ! -d $VENV/bin || ! -f $VENV/bin/activate ]]; then
    echo "Invalid virtual env $VENV!!"
    exit 1
  fi
  find_cur_py
  if [[ -z "$PYTHON" ]]; then
    [[ $2 != "create" ]] && echo "Virtual env $VENV without python!!"
    [[ $2 == "create" ]] && echo "Python executable not found!!"
    exit 1
  fi
  [[ $opt_verbose -gt 1 ]] && echo "### Python version $opt_pyver ... ###"
}

check_4_needing_pkgs() {
  local p x
  for p in $NEEDING_PKGS; do
    x=${p^^}
    eval $x=$($PIP show "$p" 2>/dev/null | grep "Version" | grep -Eo "[0-9.]+")
  done
}

check_installed_pkgs() {
  [[ $opt_verbose -gt 2 ]] && echo ">>> check_installed_pkgs()"
  local mime p p2 popts x
  check_4_needing_pkgs
  [[ $PIPVER -eq 19 ]] && popts="--use-feature=2020-resolver" || popts=""
  [[ $opt_verbose -lt 2 ]] && popts="-q"
  for p in $NEEDING_PKGS; do
    x=${p^^}
    [[ $opt_debug -ne 0 && $p =~ $LOCAL_PKGS ]] && p2=" --extra-index-url https://testpypi.python.org/pypi" || p2=""
    p2=""
    [[ $opt_verbose -gt 2 && -z "${!x}" ]] && echo ">>> $PIP install $popts$p2 $p"
    [[ $opt_verbose -lt 2 ]] && echo -en "."
    [[ -z "${!x}" ]] && $PIP install $popts$p2 $p
  done
  LIST_REQ="list_requirements.py"
  if [[ -n "$opt_oepath" || -n "$opt_oever" ]]; then
    if [[ -z $(which list_requirements.py 2>/dev/null) ]]; then
      x=$($PIP show clodoo|grep Location|awk -F: '{print $2}')
      x=$(echo $x/clodoo/list_requirements.py)
      run_traced "chmod +x $x"
      LIST_REQ="$(readlink -f $x)"
      mime=$(file -b --mime-type $f)
      if [[ $mime =~ (text/x-python|text/plain) || $f =~ \.py$ ]]; then
        [[ $opt_verbose -lt 2 ]] && echo -en "."
        run_traced "sed -i -e \"s|^#\!.*[ /]python|#\!$PYTHON|\" $x"
      fi
    fi
  fi
  [[ $opt_verbose -lt 2 ]] && echo -en "\r"
  check_4_needing_pkgs
}

odoo_orm_path() {
    p=$1
    for x in odoo openerp; do
      [[ -d $1/$x ]] && p="$1/$x" && break
      [[ -d $1/odoo/$x ]] && p="$1/odoo/$x" && break
      [[ -d $1/server/$x ]] && p="$1/server/$x" && break
    done
    eval readlink -f $p
}

venv_mgr_check_oever() {
  #venv_mgr_check_oever action venv
  local p x
  if [[ -z "$opt_oever" && ! $1 =~ (help|create) ]]; then
    p=""
    [[ $2 =~ ^VENV- ]] && p="$p $(echo $HOME/"$2"|grep -Eo "[0-9]+\.[0-9]"|head -n1)"
    [[ $2 =~ /venv_odoo ]] && p="$p $(dirname $2)"
    for x in lib/python$opt_pyver/site-packages/odoo odoo openerp server; do
      [[ -d $p2/odoo/$x ]] && p="$p $p2/odoo/$x"
      [[ $x != "odoo" && -d $p2/$x ]] && p="$p $p2/$x"
    done
    [[ -z $p ]] && p="$2"
    find_odoo_path "$p2" "-L"
  fi
  if [[ ! $1 =~ (help|create) ]]; then
    [[ -n "$opt_oever" && $opt_verbose -gt 1 ]] && echo "### Odoo version $opt_oever ...  ###"
  fi
}

do_venv_mgr_test() {
  # do_venv_mgr_test(VENV)
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_venv_mgr_test($*)"
  local f ssp x VENV
  VENV="$1"
  [[ $opt_verbose -gt 0 ]] && echo "Validation test ..."
  [ $opt_dry_run -ne 0 ] && return
  do_deactivate
  do_activate $VENV
  [[ -z "$HOME" ]] && echo "Wrong environment (No HOME directory declared)!" && return
  [[ $opt_alone -eq 2 && "$HOME" == "$SAVED_HOME" ]] && echo -e "${RED}Virtual Environment not isolated!${CLR}"
  [[ $opt_verbose -gt 0 && "$HOME" != "$SAVED_HOME" ]] && echo "Isolated environment (-I switch)."
  if [[ $opt_verbose -gt 0 ]]; then
    [[ $opt_dev -eq 0 ]] && echo "Environment w/o devel packages." || echo "Environment with devel packages (created with -D switch)."
    if [[ -f $V/pyvenv.cfg ]]; then
      ssp=$(grep -E "^include-system-site-packages" $V/pyvenv.cfg|awk -F= '{print $2}'|tr -d " ")
    else
      ssp="false"
    fi
    [[ $ssp != true ]] && echo "No system site packages" || echo "System site packages"; x="$x -s"
  fi
  [[ $opt_verbose -gt 1 ]] && echo "VPATH=$PATH"
  [[ $opt_verbose -gt 1 ]] && echo "VPYTHONPATH=$PYTHONPATH"
  for f in $PYTHON $PIP; do
    f=$(echo $f | awk -F= '{print $1}')
    x=$(readlink -e $(which "$f" 2>/dev/null) 2>/dev/null)
    [[ -z "$x" ]] && echo "Corrupted VME: file $f not found!!" && continue
    [[ -n "$x" && ! $x =~ ^$VENV ]] && echo "Warning: file $x is outside of virtual env"
  done
}

do_venv_mgr() {
  # do_venv_mgr {amend|check|cp|mv|merge|test} VENV NEW_VENV
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_venv_mgr($*)"
  local d f mime VENV V sitecustom x lropts
  local cmd=$1
  VENV="$2"
  [[ -n "$3" ]] && VENV_TGT=$(readlink -m $3)
  [[ $cmd =~ (amend|check|test|inspect) ]] && VENV_TGT=$VENV
  if [[ -z "$VENV" || -z "$VENV_TGT" ]]; then
    echo "Missed parameters!"
    echo "use: venv_mgr ${CMDS// /|} VENV NEW_VENV"
    exit 1
  fi
  if [[ "$VENV" == "$VENV_TGT" && ! $cmd =~ (amend|check|test|inspect) ]]; then
    echo "Source and destination directories are the same!"
    echo "use: venv_mgr ${CMDS// /|} VENV NEW_VENV"
    exit 1
  fi
  if [[ $cmd =~ (amend) ]]; then
    if grep -q "^ *\[ -x \$f -a ! -d \$f ] " $VENV/bin/activate &>/dev/null; then
      echo "Wrong activation script $VENV/bin/activate"
      sed -Ee "s|^ *\[ -x \\\$f -a ! -d \\\$f ] |    [[ -x \$f \&\& ! -d \$f ]] \&\& grep -q \"^#\!.*[ /]python\" \$f \&>/dev/null |" -i $VENV/bin/activate
    fi
  fi
  [[ -n "$opt_oepath" ]] && lropts="-y $opt_pyver -BPRT -p $opt_oepath" || lropts="-y $opt_pyver -BPRT"
  [[ -n "$opt_oever" ]] && lropts="$lropts -b $opt_oever"
  [[ -d $HOME/OCA ]] && lropts="$lropts -d${HOME}/OCA"
  [[ $opt_verbose -gt 1 ]] && echo "$LIST_REQ -qs' ' $lropts -t bin"
  BINPKGS=$($LIST_REQ -qs' ' $lropts -t bin)
  [[ $opt_verbose -gt 2 ]] && echo "BINPKGS=$BINPKGS"
  [[ $opt_verbose -gt 1 ]] && echo "$LIST_REQ -qs' ' $lropts -t python"
  OEPKGS=$($LIST_REQ -qs' ' $lropts -t python)
  [[ $opt_verbose -gt 2 ]] && echo "OEPKGS=$OEPKGS"
  if [[ $cmd =~ (amend|check|test|inspect) ]]; then
    V=$VENV
  elif [[ "$cmd" == "cp" ]]; then
    do_deactivate "-q"
    if [[ -f $VENV_TGT ]]; then
      # Result by strange bug
      run_traced "rm -f $VENV_TGT"
    elif [[ -d $VENV_TGT ]]; then
      if [[ $opt_force -eq 0 ]]; then
        echo "Destination v.environment $VENV_TGT already exists!!"
        echo "use: venv_mgr cp -f VENV NEW_VENV"
        exit 1
      fi
      run_traced "rm -fR $VENV_TGT"
    fi
    [[ -d $(dirname $VENV_TGT) ]] || run_traced "mkdir -p $(dirname $VENV_TGT)"
    run_traced "cp -r $VENV $VENV_TGT"
    [[ $opt_dry_run -eq 0 ]] && custom_env $VENV_TGT $opt_pyver
    V=$VENV_TGT
    do_activate "$V" "-q"
    find_cur_py
  elif [[ "$cmd" == "merge" ]]; then
    do_deactivate "-q"
    if [[ ! -d $VENV_TGT || ! -d $VENV_TGT/bin || ! -f $VENV_TGT/bin/activate ]]; then
      echo "Invalid destination virtual env $VENV_TGT!"
      exit 1
    fi
    for d in bin include lib lib64 .local; do
      if [ -d "$VENV/$d" ]; then
        [[ $opt_verbose -gt 1 ]] && run_traced "rsync -a $VENV/$d/ $VENV_TGT/$d/"
        [[ $opt_verbose -eq 0 ]] && run_traced "rsync -aq $VENV/$d/ $VENV_TGT/$d/"
      fi
    done
    V=$VENV_TGT
    do_activate "$V" "-q"
  else
    if [[ -d $VENV_TGT ]]; then
      echo "Destination virtual env $VENV_TGT already exists!"
      exit 1
    fi
    V=$VENV
  fi
  [[ ! $cmd =~ (amend|check|test|inspect) ]] && set_hashbang "$V/bin"
  if [[ ! $cmd =~ (test|inspect) ]]; then
    if [ $opt_dry_run -eq 0 -a -L $V/lib64 ]; then
      rm -f $V/lib64
      ln -s $V/lib $V/lib64
    fi
    [[ ! $cmd =~ (amend|check|cp) ]] && bin_install_1 $VENV
    [[ $cmd =~ (amend|check) ]] && bin_check_1 $VENV
    x=$($PIP --version|grep -Eo "python *[23]"|grep -Eo "[23]")
    [[ $x == "2" ]] && run_traced "$PIP install \"pip<21.0\" -U" || run_traced "$PIP install pip -U"
    PIPVER=$($PIP --version | grep -Eo "[0-9]+" | head -n1)
    [[ ! $cmd =~ (amend|check|cp) ]] && pip_install_1 "--upgrade"
    [[ $cmd =~ (amend|check) ]] && pip_check_1 $cmd
    [[ -n "$opt_oever" && "$cmd" == "amend" ]] && pip_install_2 "--upgrade"
    [[ -n "$opt_oever" && $cmd =~ (amend|check) ]] && pip_check_2 $cmd
    [[ $cmd == "amend" && -n "$opt_rfile" ]] && pip_install_req "--upgrade"
    [[ $cmd =~ (amend|check) && -n "$opt_rfile" ]] && pip_check_req $cmd
    if [[ ! $cmd == "check" && -z "$VENV_STS" ]]; then
      run_traced "sed -i -e 's:VIRTUAL_ENV=.*:VIRTUAL_ENV=\"'$VENV_TGT'\":g' $V/bin/activate"
      if $(grep -q "^# export HOME=" $V/bin/activate); then
        [ $opt_alone -le 1 ] && run_traced "sed -e 's|^# export HOME=.*|# export HOME=\"\$VIRTUAL_ENV\"|g' -i $V/bin/activate"
        [ $opt_alone -gt 1 ] && run_traced "sed -e 's|^# export HOME=.*|export HOME=\"\$VIRTUAL_ENV\"|g' -i $V/bin/activate"
      elif $(grep -q "^export HOME=" $V/bin/activate); then
        [ $opt_alone -gt 1 ] && run_traced "sed -e 's|^export HOME=.*|export HOME=\"\$VIRTUAL_ENV\"|g' -i $V/bin/activate"
        [ $opt_alone -le 1 ] && run_traced "sed -e 's|^export HOME=.*|# export HOME=\"\$VIRTUAL_ENV\"|g' -i $V/bin/activate"
      fi
      if $(grep -q "^ *# export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" $V/bin/activate); then
        [ $opt_alone -le 1 ] && run_traced "sed -e 's|# export HOME=\$(grep|export HOME=\$(grep|' -i $V/bin/activate"
      elif $(grep -q "^ *export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" $V/bin/activate); then
        [ $opt_alone -le 1 ] && run_traced "sed -e 's|export HOME=\$(grep|# export HOME=\$(grep|' -i $V/bin/activate"
      fi
      if [ $opt_dry_run -eq 0 ]; then
        if [ $opt_spkg -ne 0 ]; then
          if [[ -d $V/.local/lib/python$opt_pyver/site-packages ]]; then
            sitecustom=$V/.local/lib/python$opt_pyver/site-packages/sitecustomize.py
            echo "import sys" >$sitecustom
            echo -e "import site\nif '$VENV_TGT/.local/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('$VENV_TGT/.local/lib/python$opt_pyver/site-packages')\nif '/usr/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('/usr/lib/python$opt_pyver/site-packages')\nif '/usr/lib64/python$opt_pyver/site-packages' not in sys.path:     site.addsitedir('/usr/lib64/python$opt_pyver/site-packages')\n" >>$sitecustom
          else
            sitecustom=$V/lib/python$opt_pyver/site-packages/sitecustomize.py
            echo "import sys" >$sitecustom
            echo -e "import site\nif '/usr/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('/usr/lib/python$opt_pyver/site-packages')\nif '/usr/lib64/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('/usr/lib64/python$opt_pyver/site-packages')\n" >>$sitecustom
          fi
        elif [[ -d $V/.local/lib/python$opt_pyver/site-packages ]]; then
          sitecustom=$V/.local/lib/python$opt_pyver/site-packages/sitecustomize.py
          echo "import sys" >$sitecustom
          echo -e "import site\nif '$VENV_TGT/.local/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('$VENV_TGT/.local/lib/python$opt_pyver/site-packages')\n" >>$sitecustom
        fi
        if [[ -n "$sitecustom" ]]; then
          x=$sitecustom
          while [[ ! "$x" == "/" && ! "$(basename $x)" == "lib" ]]; do x=$(dirname $x); done
          x=$(dirname $x)
          x=$x/bin
          [[ ! :$PATH: =~ :$x: ]] && export PATH=$x:$PATH
        fi
      fi
    fi
    if [[ "$cmd" == "mv" ]]; then
      do_deactivate
      run_traced "mv $VENV $VENV_TGT"
      do_activate "$VENV_TGT" "-q"
    fi
  elif [[ $cmd == "inspect" ]]; then
    x="vem create $V"
    echo "Virtual Environment name: $V"
    echo "Python version: $opt_pyver ($PYTHON)"
    [[ -n $opt_pyver ]] && x="$x -p $opt_pyver"
    [[ -z $opt_pyver && -n $PYTHON ]] && x="$x -p $PYTHON"
    echo "PIP command: $PIP"
    [[ $opt_dev -ne 0 ]] && x="$x -D"
    [[ -n "$HOME" && $HOME != $SAVED_HOME ]] && x="$x -I"
    if [[ -f $V/pyvenv.cfg ]]; then
      ssp=$(grep -E "^include-system-site-packages" $V/pyvenv.cfg|awk -F= '{print $2}'|tr -d " ")
    else
      ssp="false"
    fi
    [[ $ssp != true ]] || x="$x -s"
    echo "Odoo version: $opt_oever"
    [[ -n $opt_oever ]] && x="$x -O $opt_oever"
    echo "Odoo path: $opt_oepath"
    [[ -n $opt_oepath ]] && x="$x -o $opt_oepath"
    echo "Internal sys.path: $PATH"
    echo -e "Environment created with \e[1m$x\e[0m"
  fi
  do_venv_mgr_test $V
}

do_venv_create() {
  # do_venv_create VENV
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_venv_create($*)"
  local f lropts p pkg v VENV xpkgs SAVED_PATH x
  local venvexe pyexe
  VENV="$1"
  if [[ -d $VENV ]]; then
    if [[ $opt_force -eq 0 ]]; then
      echo "Warning: virtual environment $VENV already exists!!"
    else
      for f in bin include lib node_modules; do
         [[ -d $VENV/$f ]] && run_traced "rm -fR $VENV/$f"
      done
      for f in odoo package-lock.json pyvenv.cfg "=2.0.0"; do
         [[ -f $VENV/$f ]] && run_traced "rm -f $VENV/$f"
      done
      f=$(ls $VENV)
      if [[ -n "$f" ]]; then
          [[ -d ${VENV}~ ]] && run_traced "rm -fR ${VENV}~"
          run_traced "mv $VENV ${VENV}~"
          if [[ -z $(find ${VENV}~ -maxdepth 0 -empty) ]]; then
              for f in ${VENV}~/*; do
                  b=$(basename $f)
                  if [[ $b =~ (bin|include|lib|node_modules|odoo|package-lock.json|pyvenv.cfg|activate_tools) ]]; then
                      [[ -L $f || ! -d $f ]] && run_traced "rm -f $f" || run_traced "rm -fR $f/"
                  fi
              done
          fi
      fi
    fi
  fi
  PYTHON=""
  if [[ -x $opt_pyver ]]; then
    PYTHON=$opt_pyver
    opt_pyver=$($PYTHON --version 2>&1 | grep -o "[0-9]\.[0-9]" | head -n1)
    PIP=$(which pip$opt_pyver 2>/dev/null)
    [[ -z $PIP ]] && PIP="$PYTHON -m pip"
  elif [[ -n $opt_pyver ]]; then
    PYTHON=$(which python$opt_pyver 2>/dev/null)
    [[ -z "$PYTHON" && $opt_pyver =~ ^3 ]] && PYTHON=python3
    [[ -z "$PYTHON" && $opt_pyver =~ ^2 ]] && PYTHON=python2
    PYTHON=$(which $PYTHON 2>/dev/null)
    [[ -z "$PYTHON" ]] && PYTHON=$(which python 2>/dev/null)
    opt_pyver=$($PYTHON --version 2>&1 | grep -o "[0-9]\.[0-9]" | head -n1)
    PIP=$(which pip$opt_pyver 2>/dev/null)
    [[ -z $PIP ]] && PIP="$PYTHON -m pip"
  else
    PYTHON=$(which python 2>/dev/null)
    opt_pyver=$($PYTHON --version 2>&1 | grep -o "[0-9]\.[0-9]" | head -n1)
    PIP=$(which pip 2>/dev/null)
    [[ -z $PIP ]] && PIP="$PYTHON -m pip"
  fi
  [[ -n "$PIP" ]] && PIPVER=$($PIP --version | grep -Eo "[0-9]+" | head -n1)
  validate_py_oe_vers
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  venvexe=$(which virtualenv 2>/dev/null)
  if [[ -n "$venvexe" ]]; then
    v=$(virtualenv --version 2>&1 | grep -Eo "[0-9]+" | head -n1)
    if [ $v -gt 17 ]; then
      [[ $opt_spkg -ne 0 ]] && p="--system-site-packages"
    else
      [[ $opt_spkg -ne 0 ]] && p="--system-site-packages" || p="--no-site-packages"
    fi
    [[ -d $VENV ]] && p="$p --clear"
    [[ $opt_alone -ne 0 ]] && p="$p --always-copy"
    p="$p -q"
    p="$p -p $PYTHON"
  else
    $pyexe -m venv --help &>/dev/null
    if [[ $? -ne 0 ]]; then
      echo "No virtualenv / venv package found!"
      exit 1
    fi
    venvexe="$pyexe -m venv"
    [[ $opt_spkg -ne 0 ]] && p="--system-site-packages"
    [[ -d $VENV ]] && p="$p --clear"
    [[ $opt_alone -ne 0 ]] && p="$p --copies"
  fi
  run_traced "$venvexe $p $VENV"
  sts=$?
  [[ $sts -ne 0 ]] && return
  if [[ -d ${VENV}~ ]]; then
      empty=1
      if [[ -z $(find ${VENV}~ -maxdepth 0 -empty) ]]; then
          for f in ${VENV}~/*; do
              b=$(basename $f)
              [[ ! -e $VENV/$b ]] && run_traced "mv $f $VENV/"
              empty=0
          done
      fi
      [[ $empty -ne 0 ]] && run_traced "rm -fR ${VENV}~"
  fi

  do_activate "$VENV"
  # [[ -d $VENV/bin ]] && export PATH=$VENV/bin:$PATH
  venv_mgr_check_src_path "$VENV"
  x=$($PIP --version|grep -Eo "python *[23]"|grep -Eo "[23]")
  [[ $x == "2" ]] && run_traced "$PIP install \"pip<21.0\" -Uq" || run_traced "$PIP install pip -Uq"
  PIPVER=$($PIP --version | grep -Eo "[0-9]+" | head -n1)
  run_traced "$PIP install \"setuptools<58.0\" -Uq"
  [[ $opt_verbose -ne 0 && PRINTED_PIPVER -eq 0 ]] && echo "# $PIP.$PIPVER ..." && PRINTED_PIPVER=1
  check_installed_pkgs
  if [[ -n "$opt_oepath" || -n "$opt_oever" ]]; then
    [[ -n "$opt_oepath" ]] && lropts="-y $opt_pyver -BPRT -p $opt_oepath" || lropts="-y $opt_pyver -BPRT"
    [[ -n "$opt_oever" ]] && lropts="$lropts -b $opt_oever"
    [[ $opt_verbose -gt 1 ]] && echo "$LIST_REQ -qs' ' $lropts -t bin"
    BINPKGS=$($LIST_REQ -qs' ' $lropts -t bin)
    [[ $opt_verbose -gt 2 ]] && echo "BINPKGS=$BINPKGS"
    [[ $opt_verbose -gt 1 ]] && echo "$LIST_REQ -qs' ' $lropts -t python"
    OEPKGS=$($LIST_REQ -qs' ' $lropts -t python)
    [[ $opt_verbose -gt 2 ]] && echo "OEPKGS=$OEPKGS"
    bin_install_1 $VENV
  fi
  [[ $opt_dry_run -eq 0 ]] && custom_env $VENV $opt_pyver
  pip_install_1
  [[ -n "$opt_oever" ]] && pip_install_2
  [[ -n "$opt_rfile" ]] && pip_install_req
  # [[ $opt_travis -ne 0 ]] && set_hashbang "$VENV/bin"
  # do_deactivate
  # [[ -n "$opt_oever" && -d $HOME/$opt_oever ]] && run_traced "ln -s $opt_oepath $(readlink -f ./odoo)"
  do_venv_mgr_test $VENV
}

do_venv_exec() {
  # do_venv_exec VENV cmd
  local d f mime VENV V sitecustom
  VENV="$1"
  #do_activate
  run_traced "$2 $3 $4 $5 $6 $7 $8 $9"
  # do_deactivate
}

do_venv_pip() {
  # do_venv_pip VENV action pkg
  local d f VENV V popts x
  local SAVED_PATH=$PATH
  local cmd="$2"
  VENV="$1"
  if [[ $opt_alone -ne 0 ]]; then
    V=""
    for d in ${PATH//:/ }; do
      [[ ! $d =~ ^$HOME/ || $d =~ ^/(usr/bin) ]] && V="$V:$d"
    done
    PATH=${V:1}
    [[ $opt_verbose -ne 0 ]] && echo "$ PATH=$PATH"
  fi
  V=""
  pkg="$(get_actual_pkg $3)"
  [[ $pkg =~ "-e " ]] && pkg=${pkg//-e /--editable=}
  if [[ $cmd == "uninstall" ]]; then
    pip_uninstall "$pkg"
  else
    [[ $opt_alone -ne 0 && ! $pkg =~ ^- ]] && popts="--isolated --disable-pip-version-check --no-cache-dir" || popts="--disable-pip-version-check"
    [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
    [[ $PIPVER -eq 19 && ! 2020-resolver =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
    [[ $opt_verbose -eq 0 ]] && popts="$popts -q"
    if [[ $cmd =~ (info|show) ]]; then
      pkg=$(get_pkg_wo_version $pkg)
      run_traced "$PIP show $pkg"
      x=$($PIP show $pkg | grep -E ^Location | awk -F: '{print $2}' | sed -e "s| ||")
      [[ -n $x ]] && x=$x/$pkg
      [[ -L $x ]] && echo "Actual location is $(readlink -e $x)"
    fi
    [[ $cmd == "install" ]] && pip_install "$pkg"
    [[ "$cmd" == "uninstall" ]] && run_traced "$PIP $cmd $pkg"
    [[ $cmd == "update" ]] && pip_install "$pkg" "--upgrade"
  fi
  do_deactivate
  export PATH=$SAVED_PATH
}

find_odoo_path() {
# find_odoo_path(path opts)
    local p v x
    [[ $opt_verbose -gt 2 ]] && echo ">>> find $2 $1 -maxdepth 3 -type f -not -path "*tmp*" -a -not -path "*old*" -not -path "*/__to_remove/*" -not -path "*/lib/*" -not -path "*/lib64/*" -not -path "*/tests/res/*" -not -path "*/include/*" -not -path "*/.*/*" -not -path "*/node_modules/*" -name release.py"
    for f in $(find $2 $1 -maxdepth 3 -type f -not -path "*tmp*" -a -not -path "*old*" -not -path "*/__to_remove/*" -not -path "*/lib/*" -not -path "*/lib64/*" -not -path "*/tests/res/*" -not -path "*/include/*" -not -path "*/.*/*" -not -path "*/node_modules/*" -name release.py 2>/dev/null|sort); do
        v=$(grep "^version_info" $f|cut -d= -f2|tr -d "("|tr -d ")"|tr -d " "|awk -F, '{print $1 "." $2}')
        [[ -n "$opt_oever" && $v == $opt_oever ]] && opt_oepath="$(readlink -e $(dirname $f)/..)" && break
        [[ -z "$opt_oever" ]] && opt_oever="$v" && break
    done
}

validate_py_oe_vers() {
  local odoo_majver
  if [[ -n $opt_oever && -z $opt_pyver ]]; then
    odoo_majver=$(echo $opt_oever|cut -d. -f1)
    [[ $odoo_majver -le 10 ]] && opt_pyver=2 || opt_pyver=3
  elif [[ -n $opt_oever && -n $opt_pyver ]]; then
    odoo_majver=$(echo $opt_oever|cut -d. -f1)
    if [[ ( $odoo_majver -le 10 && $opt_pyver =~ ^3 ) || ( $odoo_majver -gt 10 && $opt_pyver =~ ^2 ) ]]; then
      echo "Invalid python version $opt_pyver for Odoo $opt_oever!"
      exit 1
    fi
  fi
}


OPTOPTS=(h        a        B         C      D       f         k        I           i         n           O         o          p         q           r           s                    t          V           v)
OPTLONG=(help     ""       ""        ""     devel   force     keep     indipendent isolated  dry_run     odoo-ver  odoo-path  python    quiet       requirement system-site-packages travis     version     verbose)
OPTDEST=(opt_help opt_bins opt_debug opt_cc opt_dev opt_force opt_keep opt_alone   opt_alone opt_dry_run opt_oever opt_oepath opt_pyver opt_verbose opt_rfile   opt_spkg             opt_travis opt_version opt_verbose)
OPTACTI=('+'      "="      "+"       1      1       1         1        2           1         1           "="       "="        "="       0           "="         1                    1          "*>"        "+")
OPTDEFL=(1        ""       0         0      0       0         0        0           0         0           ""        ""         ""        0           ""          0                    0          ""          -1)
OPTMETA=("help"   "list"   ""        ""     ""      ""        ""       ""          ""        ""          "version" "dir"      "pyver"   ""          "file"      ""                   ""         "version"   "verbose")
OPTHELP=("this help"
  "bin packages to install (* means wkhtmltopdf,lessc)"
  "use unstable packages: -B testpypi / -BB from ~/tools / -BBB from ~/pypi / -BBBB link to local ~/pypi"
  "clear cache before executing pip command"
  "create v.environment with development packages"
  "force v.environment create, even if exists or inside another virtual env"
  "keep python2 executable as python (deprecated)"
  "run pip in an isolated mode and set home virtual directory"
  "run pip in an isolated mode, ignoring environment variables and user configuration"
  "do nothing (dry-run)"
  "install pypi required by odoo ver (amend or create)"
  "odoo path used to search odoo requirements"
  "python version"
  "silent mode"
  "after created v.environment install from the given requirements file"
  "create v.environment with access to the global site-packages"
  "activate environment for travis test"
  "show version"
  "verbose mode")
OPTARGS=(p3 p4 p5 p6 p7 p8 p9)
# no-global-site-packages.txt
parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi

ACTIONS="help amend cp check create exec info inspect install merge mv python shell rm show uninstall update test"
REXACT="^(${ACTIONS// /|})\$"
# In old vem version p1 -> action and p2 > venv
[[ $opt_verbose -gt 3 ]] && set -x
action=""
p2=""
for x in 3 4 5 6; do
  p="p$x"
  if [[ ${!p} =~ $REXACT ]]; then
    action="${!p}"
    eval $p=""
    [[ $action == "help" ]] && break
  elif [[ -d "${!p}" && -f ${!p}/bin/activate ]]; then
    p2="$(readlink -e ${!p})"
    eval $p=""
  elif [[ $action == "create" ]]; then
    if [[ -z "$p2" && -n "${!p}" ]]; then
      p2="${!p}"
      eval $p=""
    fi
  elif [[ $action == "" ]]; then
    action="exec"
  fi
  [[ -n "$p2" && -n "$action" ]] && break
done
if [[ -z "$p2" && -n "$VIRTUAL_ENV" && -f $VIRTUAL_ENV/bin/activate ]]; then
  p2=$VIRTUAL_ENV
  VENV_STS="preinstalled"   # running inside a virtual environment
elif [[ -z "$p2" && -f ./bin/activate ]]; then
  p2="$(readlink -e ./)"
fi
[[ -z "$p8" && -n "$p9" ]] && p8="$p9" && p9=""
[[ -z "$p7" && -n "$p8" ]] && p7="$p8" && p8=""
[[ -z "$p6" && -n "$p7" ]] && p6="$p7" && p7=""
[[ -z "$p5" && -n "$p6" ]] && p5="$p6" && p6=""
[[ -z "$p4" && -n "$p5" ]] && p4="$p5" && p5=""
[[ -z "$p3" && -n "$p4" ]] && p3="$p4" && p4=""
if [[ $opt_help -gt 0 ]]; then
  print_help "Manage virtual environment\naction may be: $ACTIONS" "(C) 2018-2021 by zeroincombenze(R)\nhttps://zeroincombenze-tools.readthedocs.io/en/latest/pypi_python_plus/rtd_description.html#vem-virtual-environment-manager\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi
[[ ! $action =~ (help|create) && ( -z "$p2" || ! -f $p2/bin/activate ) ]] && echo -e "${RED}Virtual environment not issued! Use $0 <VENV> ...${CLR}" && exit 1
# If it is running inside travis test environment
[[ -z "$opt_pyver" && -n "$TRAVIS_PYTHON_VERSION" ]] && opt_pyver=$TRAVIS_PYTHON_VERSION
[[ -z $VENV_STACK ]] && declare -A VENV_STACK && export VENV_STACK
[[ -n "$VIRTUAL_ENV" && -z "$VENV_STACK" ]] && push_venv "$VIRTUAL_ENV"
[[ $opt_verbose -eq -1 ]] && opt_verbose=1
if [[ $action == "create" && -n "$VIRTUAL_ENV" && ${opt_force:-0} -eq 0 ]]; then
  echo "You cannot create a new virtual environment inside $VIRTUAL_ENV"
  exit 1
fi
PYTHON=""
PIP=""
DO_POP=0
DO_DEACT=0
export PYTHONWARNINGS="ignore"
if [[ $action != "create" && -f $p2/bin/activate ]]; then
  grep -q "^export HOME=\"\$VIRTUAL_ENV\"" $p2/bin/activate && opt_alone=2
  [[ $opt_dev -eq 0 ]] && x=$(find ${p2}/lib -name pylint -o -name unittest2 -o -name coverage -o -name flake8 | wc -l)
  [[ $opt_dev -eq 0 && ${x:-0} -gt 1 ]] && opt_dev=1
fi
SAVED_HOME=$HOME
SAVED_PYTHONPATH=$PYTHONPATH
PRINTED_PIPVER=0
[[ $opt_alone -ne 0 ]] && PYTHONPATH=""
# [[ $opt_debug -eq 2 && -d $HOME/tools && :$PATH: =~ :$HOME/tools: && -n "$PYTHONPATH" ]] && PYTHONPATH=$HOME/tools:$PYTHONPATH
# [[ $opt_debug -eq 2 && -d $HOME/tools && :$PATH: =~ :$HOME/tools: && -z "$PYTHONPATH" ]] && PYTHONPATH=$HOME/tools
# [[ $opt_debug -ge 3 ]] && package_debug
FLAG=">"
[[ $opt_dry_run -eq 0 ]] && FLAG="\$"
if [[ $action == "rm" ]]; then
  [[ $PWD == $(readlink -f $p2) ]] && cd
  rm -fR $p2
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  unset PYTHON PIP
  exit 0
elif [[ ! $action =~ (help|create) ]]; then
  do_activate "$p2" "-q"
  venv_mgr_check_src_path $p2
  check_installed_pkgs
  venv_mgr_check_oever $action $p2
  validate_py_oe_vers
fi
[[ "$opt_bins" == "*" ]] && opt_bins="${BIN_PKGS//|/,}" && opt_bins="${opt_bins:1:-1}"
if [[ $action != "help" ]]; then
  [[ -n "$opt_oever" && -z "$opt_oepath" ]] && find_odoo_path $HOME "-L"
  [[ $opt_verbose -gt 2 ]] && echo "# Odoo dir = '$opt_oepath'"
fi
if [[ $action =~ (help|create|exec|python|shell) || $opt_dev -eq 0 || -z "$FUTURE" || -z "$CONFIGPARSER" || -z "$Z0LIB" || -z "$OS0" || -z $(which list_requirements.py 2>/dev/null) ]]; then
  [[ $opt_dev -eq 0 ]] && DEV_PKGS=""
else
  cmd="list_requirements.py -qt python -BP"
  [[ $opt_dev -ne 0 ]] && cmd="$cmd -TR"
  [[ -n "$opt_pyver" ]] && cmd="$cmd -y$opt_pyver"
  [[ -n "$opt_oever" ]] && cmd="$cmd -b$opt_oever"
  [[ -d $HOME/OCA ]] && cmd="$cmd -d${HOME}/OCA"
  [[ -d $HOME/maintainer-tools ]] && cmd="$cmd -d${HOME}/maintainer-tools"
  [[ -d $HOME/maintainer-quality-tools ]] && cmd="$cmd -d${HOME}/maintainer-quality-tools"
  DEV_PKGS=$($cmd -s" ")
  [[ $opt_verbose -gt 2 ]] && echo "DEV_PKGS=$DEV_PKGS"
fi
if [ "$action" == "help" ]; then
  man $(dirname $0)/man/man8/$(basename $0).8.gz
elif [ "$action" == "exec" ]; then
  do_venv_exec "$p2" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [ "$action" == "python" ]; then
  do_venv_exec "$p2" "python" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [ "$action" == "shell" ]; then
  do_venv_exec "$p2" "$SHELL -i" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [[ $action =~ (info|install|show|uninstall|update) ]]; then
  [[ $opt_cc -ne 0 && -d $HOME/.cache/pip ]] && run_traced "rm -fR $HOME/.cache/pip"
  do_venv_pip "$p2" "$action" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [ "$action" == "create" ]; then
  [[ $opt_cc -ne 0 && -d $HOME/.cache/pip ]] && run_traced "rm -fR $HOME/.cache/pip"
  do_venv_create "$p2" "$p3" "$p4" "$p5" "$p6"
  do_deactivate "-q"
else
  do_venv_mgr "$action" "$p2" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
fi
PYTHONPATH=$SAVED_PYTHONPATH
[[ $opt_verbose -gt 3 ]] && set +x
if [[ -n "$ERROR_PKGS" ]]; then
  echo "************************************************************"
  echo -e "\e[1mWarning! Following packages with wrong version or uninstalled\e[0m"
  echo "$ERROR_PKGS"
  echo "************************************************************"
  DISTO=$(xuname -d)
  FH=$(xuname -f)
  [[ $FH == "RHEL" ]] && XTAL="yum" || XTAL="apt"
  [[ $DISTO == "Fedora" ]] && XTAL="dnf"
  echo "Perhaps you should install ..."
  [[ $FH == "RHEL" ]] && PKGLIST="python-devel" || PKGLIST="python-dev"
  [[ $DISTO == "Fedora" ]] && PKGLIST=""
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST python3-devel" || PKGLIST="$PKGLIST python3-dev"
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST python3-pip" || PKGLIST="$PKGLIST python3-pip"
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST python3-venv" || PKGLIST="$PKGLIST python3-venv"
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libsass-devel"
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST zlib-devel" || PKGLIST="$PKGLIST zlib1g-dev"
  echo "$XTAL install $PKGLIST"
  if [[ $ERROR_PKGS =~ lxml ]]; then
    PKGLIST=""
    [[ $DISTO == "Fedora" ]] && PKGLIST="redhat-rpm-config"
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libxml2-devel" || PKGLIST="$PKGLIST libxml2-dev"
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libxslt-devel" || PKGLIST="$PKGLIST libxslt-dev"
    echo "$XTAL install $PKGLIST    # lxml"
  fi
  if [[ $ERROR_PKGS =~ ldap ]]; then
    PKGLIST=""
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST openldap-devel" || PKGLIST="$PKGLIST libsasl2-dev libldap2-dev libssl-dev"
    echo "$XTAL install $PKGLIST    # ldap"
  fi
  if [[ $ERROR_PKGS =~ gevent ]]; then
    PKGLIST=""
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libevent-devel" || PKGLIST="$PKGLIST libevent-dev"
    echo "$XTAL install $PKGLIST    # gevent"
  fi
  if [[ $ERROR_PKGS =~ pycups ]]; then
    PKGLIST=""
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST cups-devel" || PKGLIST="$PKGLIST libcups2-dev"
    echo "$XTAL install $PKGLIST    # pycups"
  fi
  if [[ $ERROR_PKGS =~ shapely ]]; then
    PKGLIST=""
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST geos-devel" || PKGLIST="$PKGLIST libgeos-dev"
    echo "$XTAL install $PKGLIST    # shapely"
  fi
fi
unset PYTHON PIP
exit 0