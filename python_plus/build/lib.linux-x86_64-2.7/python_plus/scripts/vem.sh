#! /bin/bash
#
# Manage virtual environment
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2018-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# -----------------------------------------------------------------------------
# PIP features truth table depending on pip version (21.0 + only python3):
# option                        |  18- | 18.0 | 19.0 | 20.0 | 21.0 | 22.0
# --disable-pip-version-check   |  OK  |  OK  |  OK  |  OK  |  OK  |  OK
# --no-python-version-warning   |  OK  |  OK  |  OK  |  OK  |  OK  |  OK
# --no-warn-conflicts           |   X  |  OK  |  OK  |  OK  |  OK  |  OK
# --use-features=2020-resolver  |   X  |  OK  |  OK  |  no  |   X  |   X
# --use-features=fast-deps      |   X  |  OK  |  OK  |  no  |   X  |   X
# --use-features=in-tree-build  |   X  |   X  |   X  |   X  |  OK  |   X
# -----------------------------------------------------------------------------
# OK -> Use feature / X -> Feature unavailable / no -> Do use use
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 2.0.0
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
[[ -x $TDIR/../bin/python3 ]] && PYTHON=$(readlink -f $TDIR/../bin/python3) || [[ -x $TDIR/python3 ]] && PYTHON="$TDIR/python3" || PYTHON="python3"
[[ -z $PYPATH ]] && PYPATH=$(echo -e "import os,sys\no=os.path\na=o.abspath\nj=o.join\nd=o.dirname\nb=o.basename\nf=o.isfile\np=o.isdir\nC=a('"$TDIR"')\nD='"$HOME_DEVEL"'\nif not p(D) and '/devel/' in C:\n D=C\n while b(D)!='devel':  D=d(D)\nN='venv_tools'\nU='setup.py'\nO='tools'\nH=o.expanduser('~')\nT=j(d(D),O)\nR=j(d(D),'pypi') if b(D)==N else j(D,'pypi')\nW=D if b(D)==N else j(D,'venv')\nS='site-packages'\nX='scripts'\ndef pt(P):\n P=a(P)\n if b(P) in (X,'tests','travis','_travis'):\n  P=d(P)\n if b(P)==b(d(P)) and f(j(P,'..',U)):\n  P=d(d(P))\n elif b(d(C))==O and f(j(P,U)):\n  P=d(P)\n return P\ndef ik(P):\n return P.startswith((H,D,K,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))\ndef ak(L,P):\n if P not in L:\n  L.append(P)\nL=[C]\nK=pt(C)\nfor B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n for P in [C]+sys.path+os.environ['PATH'].split(':')+[W,R,T]:\n  P=pt(P)\n  if B==b(P) and ik(P):\n   ak(L,P)\n   break\n  elif ik(j(P,B,B)):\n   ak(L,j(P,B,B))\n   break\n  elif ik(j(P,B)):\n   ak(L,j(P,B))\n   break\n  elif ik(j(P,S,B)):\n   ak(L,j(P,S,B))\n   break\nak(L,os.getcwd())\nprint(' '.join(L))\n"|$PYTHON)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
[[ -z "$Z0LIBDIR" ]] && echo "Library file z0librc not found in <$PYPATH>!" && exit 72
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"

# DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
# TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.0

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
UNISOLATED_PKGS="(.?-|lxml)"
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
  pkg=$(echo "$1"|grep --color=never -Eo '[^!<=>\\[]*'|head -n1)
  echo $pkg
}


get_wkhtmltopdf_dwname() {
  #get_wkhtmltopdf_dwname(pkg FH DISTO MACHARCH)
  local pkg=$1 FH=$2 DISTO=$3 MACHARCH=$4 pkgext wkhtmltopdf_wget x y z
  DISTO=${DISTO,,}
  [[ $DISTO =~ ^debian ]] && y="_" || y="-"
  [[ "$FH" == "RHEL" ]] && x="." || x="_"
  [[ $DISTO =~ ^(redhat|fedora) ]] && DISTO="centos7"
  [[ "$DISTO" == "ubuntu20" ]] && DISTO="focal"
  [[ "$DISTO" == "ubuntu18" ]] && DISTO="bionic"
  [[ "$DISTO" == "ubuntu16" ]] && DISTO="xenial"
  [[ "$DISTO" == "ubuntu14" ]] && DISTO="trusty"
  [[ "$DISTO" == "debian10" ]] && DISTO="buster"
  [[ "$DISTO" == "debian9" ]] && DISTO="stretch"
  [[ "$DISTO" == "debian8" ]] && DISTO="jessie"
  [[ "$FH" == "RHEL" ]] && pkgext=".rpm" || pkgext=".deb"
  [[ "$FH" == "Debian" && "$MACHARCH" == "x86_64" ]] && MACHARCH="amd64"
  reqver=$(echo "$pkg" | grep --color=never -Eo '[^!<=>]*' | tr -d "'" | sed -n '2 p')
  [[ -z "$reqver" ]] && reqver="0.12.5"
  [[ "$FH" == "RHEL" && "$MACHARCH" == "x86_64" && $reqver =~ 0.12.[14] ]] && MACHARCH="amd64"
  z="wkhtmltopdf"
  if [[ ${reqver} =~ 0.12.6 ]]; then
    reqver="0.12.6-1"
    z="packaging"
    wkhtmltopdf_wget="wkhtmltox${y}${reqver}.${DISTO}${x}${MACHARCH}${pkgext}"
  elif [[ ${reqver} == "0.12.5" ]]; then
    wkhtmltopdf_wget="wkhtmltox${y}${reqver}-1.${DISTO}${x}${MACHARCH}${pkgext}"
  elif [[ ${reqver} == "0.12.4" ]]; then
    wkhtmltopdf_wget="wkhtmltox-${reqver}_linux-generic-${MACHARCH}.tar.xz"
  else
    wkhtmltopdf_wget="wkhtmltox-${reqver}_linux-${DISTO}-${MACHARCH}${pkgext}"
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

get_req_list() {
# get_req_list(req_file type debug)
    local cmd fn mime tt x
    fn="$1"
    tt="$2"

    [[ "$3" == "debug" ]] && cmd="$(which $LIST_REQ)" || cmd="$LIST_REQ"
    [[ -n $tt ]] && cmd="$cmd -qt $tt -BP" || cmd="$cmd -qt python -BP"
    [[ $opt_dev -ne 0 ]] && cmd="${cmd}TR"
    [[ -n "$opt_pyver" ]] && cmd="$cmd -y$opt_pyver"
    [[ -n "$opt_oever" ]] && cmd="$cmd -b$opt_oever"
    [[ -n "$opt_oepath" ]] && cmd="$cmd -p$opt_oepath"
    x=""
    [[ -d $HOME/OCA ]] && x="$x,${HOME}/OCA"
    [[ -d $HOME/maintainer-tools ]] && x="$x,${HOME}/maintainer-tools"
    [[ -d $HOME/maintainer-quality-tools ]] && x="$x,${HOME}/maintainer-quality-tools"
    [[ -n $x ]] && cmd="$cmd -d${x:1}"
    [[ -n $fn ]] && cmd="$cmd -m $pfn"
    [[ "$3" == "debug" ]] && echo $cmd -qs "" || $cmd -qs" "
}

bin_install() {
  # bin_install(pkg)
  [[ $opt_verbose -gt 2 ]] && echo ">>> bin_install($*)"
  local x FH DISTO
  local reqver size
  [[ -n $opt_FH ]] && FH=$opt_FH || FH=$(xuname -f)
  local MACHARCH=$(xuname -m)
  [[ -n $opt_distro ]] && DISTO=${opt_distro,,} || DISTO=$(xuname -d)
  [[ -z $opt_distro ]] && DISTO=${DISTO,,}$(xuname -v | grep --color=never -Eo "[0-9]*" | head -n1)
  local pkg=$1
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    if [[ $pkg =~ lessc ]]; then
      x=$(which npm 2>/dev/null)
      if [[ -z "$x" ]]; then
        echo "Package $pkg require npm software but this software is not installed on your system"
        echo "You should install npm ..."
        [[ $DISTO =~ ^fedora ]] && echo "dnf install npm"
        [[ ! $DISTO =~ ^fedora && $FH == "RHEL" ]] && echo "yum install npm"
        [[ $DISTO =~ ^debian ]] && echo "apt install npm"
        ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        [[ $pkg == "lessc" ]] && pkg="less@3.0.4"
        pkg=${pkg/==/@}
        pkg=$(echo $pkg | tr -d "'")
        run_traced "npm install $pkg"
        run_traced "npm install less-plugin-clean-css"
        x=$(find $(npm bin) -name lessc 2>/dev/null)
        [[ -n "$x" ]] && run_traced "ln -s $x $VENV/bin" || ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      fi
    elif [[ $pkg =~ wkhtmltopdf ]]; then
      mkdir wkhtmltox.rpm_files
      pushd wkhtmltox.rpm_files >/dev/null
      wkhtmltopdf_wget=$(get_wkhtmltopdf_dwname $pkg $FH $DISTO $MACHARCH)
      pkgext=$(echo wkhtmltopdf_wget | grep --color=never -Eo ".xz$")
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
  local pkg d x srcdir pfn popts pypath v tmpdir DISTO  FH
  [[ -n $opt_FH ]] && FH=$opt_FH || FH=$(xuname -f)
  [[ -n $opt_distro ]] && DISTO=${opt_distro,,} || DISTO=$(xuname -d)
  pypath=$(find $VIRTUAL_ENV/lib -type d -name "python$opt_pyver")
  [[ -n "$pypath" && -d $pypath/site-packages ]] && pypath=$pypath/site-packages || pypath=$(find $(readlink -f $(dirname $(which $PYTHON))/../lib) -type d -name site-packages)
  tmpdir=$VIRTUAL_ENV/tmp
  pkg="$(get_actual_pkg $1)"
  [[ $pkg =~ "-e " ]] && pkg=${pkg//-e /--editable=}
  [[ $opt_alone -ne 0 && ! $pkg =~ $UNISOLATED_PKGS ]] && popts="--isolated --disable-pip-version-check --no-python-version-warning --no-cache-dir" || popts="--disable-pip-version-check --no-python-version-warning"
  [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
  [[ $PIPVER -eq 19 && ! 2020-resolver =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
  [[ $PIPVER -eq 21  && ! in-tree-build =~ $popts  ]] && popts="$popts --use-feature=in-tree-build $popts"
  [[ $opt_verbose -lt 2 ]] && popts="$popts -q"
  [[ $opt_verbose -ne 0 && PRINTED_PIPVER -eq 0 ]] && echo "# $PIP.$PIPVER $popts ..." && PRINTED_PIPVER=1
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    if [[ ! $pkg =~ $BIN_PKGS ]]; then
      srcdir=""
      [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pfn=${pkg//-/_} || pfn=$pkg
      [[ $opt_debug -eq 2 && -d $SAVED_HOME_DEVEL/../tools/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME_DEVEL/../tools/$pfn)
      if [[ $opt_debug -ge 3 ]]; then
        [[ -d $SAVED_HOME_DEVEL/pypi/$pfn/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME_DEVEL/pypi/$pfn)
      fi
      if [[ $pkg =~ ^(odoo|openerp)$ ]]; then
        [[ -z $opt_oepath ]] && echo "Missed Odoo version to install (please use -O and -o switches)!" && exit 1
        [[ -d $opt_oepath/openerp && -f $opt_oepath/openerp/__init__.py ]] && srcdir=$opt_oepath/openerp
        [[ -d $opt_oepath/odoo && -f $opt_oepath/odoo/__init__.py ]] && srcdir=$opt_oepath/odoo
      fi
      [[ -z $srcdir && $opt_debug -ge 2 && $pkg =~ $LOCAL_PKGS ]] && echo "Invalid or not found source path!" && exit 1
      [[ -z $srcdir && $pkg =~ ^(odoo|openerp)$ ]] && echo "Odoo source not found!" && exit 1
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
        x=$(grep -A3 -E "^ *package_data" $tmpdir/$pfn/setup.py|grep --color=never -Eo "\./README.rst")
        # [[ $x == "\./README.rst" ]] && run_traced "mv $tmpdir/$pfn/$pfn/README.rst $tmpdir/$pfn/README.rst"
        run_traced "$PIP install $tmpdir/$pfn $popts"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        run_traced "rm -fR $tmpdir/$pfn"
      elif [[ $opt_debug -eq 3 ]]; then
        run_traced "$PIP install $srcdir $popts"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        pushd $srcdir/.. >/dev/null
        [[ $pkg =~ ^(odoo|openerp)$ ]] && x="$opt_oever" || x=$(get_local_version $pfn)
        v=$([[ $(echo $x|grep "mismatch") ]] && echo $x|awk -F/ '{print $2}' || echo $x)
        popd >/dev/null
        x=$(ls -d $pypath/${pfn}-*DISTO-info 2>/dev/null|grep -E "${pfn}-[0-9.]*DISTO-info")
        [[ -n $x && $x != $pypath/${pfn}-${v}.DISTO-info ]] && run_traced "mv $x $pypath/${pfn}-${v}.DISTO-info"
        if [[ ! -d $pypath/${pfn}-${v}.DISTO-info ]]; then
          run_traced "mkdir $pypath/${pfn}-${v}.DISTO-info"
          for d in INSTALLER METADATA RECORD REQUESTED top_level.txt WHEEL; do
            run_traced "touch $pypath/${pfn}-${v}.DISTO-info/$d"
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
      [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
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
      [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
    elif [[ $pkg =~ $GIT_PKGS ]]; then
      d=""
      [[ $pkg =~ "openupgradelib" ]] && d="git+https://github.com/OCA/openupgradelib.git"
      [[ $pkg =~ "prestapyt" ]] && d="git+https://github.com/prestapyt/prestapyt.git@master"
      [[ -z "$d" ]] && echo "Unknown URL for $pkg" && return
      run_traced "$PIP install $d"
      [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
    elif [[ $pkg =~ $BZR_PKGS ]]; then
      x=$(which bzr 2>/dev/null)
      if [[ -z "$x" ]]; then
        echo "Package $pkg require bazar software but this software is not installed on your system"
        echo "You should install bazar ..."
        [[ $DISTO =~ ^fedora ]] && echo "dnf install bzr"
        [[ ! $DISTO =~ ^fedora && $FH == "RHEL" ]] && echo "yum install bzr"
        [[ $DISTO =~ ^debian ]] && echo "apt install bzr"
        [[ $DISTO =~ ^Ubuntu ]] && echo "add-apt-repository ppa:bzr/ppa"
        [[ $FH == "Debian" ]] && echo "apt update"
        ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        run_traced "mkdir -p $HOME/bazar"
        run_traced "cd $HOME/bazar"
        run_traced "bzr branch lp:$pkg"
        d=$(find $pkg -name setup.py | head -n1)
        [[ -n "$d" ]] && d=$(dirname $d) || d=""
        if [[ -n "$d" && -d "$d" ]]; then
          run_traced "cd $d"
          run_traced "python ./setup.py install"
          [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
        else
          echo "Invalid bazar package: file setup.py not found!"
          ERROR_PKGS="$ERROR_PKGS   '$pkg'"
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
    [[ -z "$pfn" ]] && echo "File $f not found!" && continue
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing file $pfn\e[0m"
    flist=$(get_req_list "$pfn")
    [[ $opt_verbose -gt 2 ]] && echo "<<<$flist>>>$(get_req_list '$pfn' '' 'debug')"
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
    [[ $opt_debug -eq 2 && -d $SAVED_HOME_DEVEL/../tools/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME_DEVEL/../tools/$pfn)
    [[ $opt_debug -eq 3 && -d $SAVED_HOME_DEVEL/pypi/$pfn/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME_DEVEL/pypi/$pfn/$pfn)
    [[ $opt_debug -eq 3 && -d $SAVED_HOME/pypi/$pfn/$pfn ]] && srcdir=$(readlink -f $SAVED_HOME/pypi/$pfn/$pfn)
    if [[ -n "$srcdir" ]]; then
      [[ -d $pypath/$pfn && ! -L $pypath/$pfn ]] && run_traced "rm -fR $pypath/$pfn"
      pushd $srcdir/.. >/dev/null
      [[ $pkg =~ ^(odoo|openerp)$ ]] && x="$opt_oever" || x=$(get_local_version $pfn)
      v=$([[ $(echo $x|grep "mismatch") ]] && echo $x|awk -F/ '{print $2}' || echo $x)
      popd >/dev/null
      x=$(ls -d $pypath/${pfn}-*DISTO-info 2>/dev/null|grep -E "${pfn}-[0-9.]*DISTO-info")
      [[ -n $x && $x != $pypath/${pfn}-${v}.DISTO-info ]] && run_traced "rm $x"
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

  op=$(echo "$vpkg" | grep --color=never -Eo '[!<=>]*' | head -n1)
  pkg=$(echo "$vpkg" | grep --color=never -Eo '[^!<=>\\[]*' | tr -d "'" | head -n1)
  reqver=$(echo "$vpkg" | grep --color=never -Eo '[^!<=>]*' | tr -d "'" | sed -n '2 p')
  [[ -n "$reqver" ]] && xreqver=$(echo $reqver | grep --color=never -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xreqver=0
  sts=0
  curver=$($pkg --version 2>/dev/null | grep  =never-Eo "[0-9]+\.[0-9]+\.?[0-9]*" | head -n1)
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
      [[ -n "$curver" ]] && xcurver=$(echo $curver | grep --color=never -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xcurver=0
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

  op=$(echo "$vpkg" | grep --color=never -Eo '[!<=>]*' | head -n1)
  pkg=$(echo "$vpkg" | grep --color=never -Eo '[^!<=>\\[]*' | tr -d "'" | head -n1)
  reqver=$(echo "$vpkg" | grep --color=never -Eo '[^!<=>]*' | tr -d "'" | sed -n '2 p')
  [[ -n "$reqver" ]] && xreqver=$(echo $reqver | grep --color=never -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xreqver=0
  sts=0
  if [[ $pkg =~ $BIN_PKGS ]]; then
      check_bin_package "$pkg"
  elif [[ -n "$reqver" ]]; then
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
      [[ -n "$curver" ]] && xcurver=$(echo $curver | grep --color=never -Eo '[0-9]+\.[0-9]+(\.[0-9]+|)' | awk -F. '{print $1*10000 + $2*100 + $3}') || xcurver=0
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
  if [[ ! $pkg =~ $BIN_PKGS ]]; then
    x=$($PIP show $pkg | grep "^[Ll]ocation" | awk -F: '{print $2}' | tr -d ', \r\n\(\)')
    [[ -n "$x" && ! $x =~ ^$VENV ]] && echo "Warning: file $x is outside of virtual env"
  fi
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
    [[ -z "$pfn" ]] && echo "File $f not found!" && continue
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing file $pfn\e[0m"
    flist=$(get_req_list "$pfn")
    [[ $opt_verbose -gt 1 ]] && echo "<<<$flist>>>$(get_req_list '$pfn' '' 'debug')"
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
  local VIRTUAL_ENV=$1 pyver=$(echo $2|grep --color=never -Eo "[0-9]"|head -n1)
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
  if [[ -n $opt_lang ]]; then
    if $(grep -q "^export LANG=" $VIRTUAL_ENV/bin/activate); then
      sed -e 's|^export LANG=.*|export LANG="$opt_lang"|g' -i $VIRTUAL_ENV/bin/activate
    elif $(grep -q "^# export LANG=" $VIRTUAL_ENV/bin/activate); then
      sed -e 's|^# export LANG=.*|export LANG="$opt_lang"|g' -i $VIRTUAL_ENV/bin/activate
    else
      sed -r "/deactivate *\(\) *\{/i\export LANG="$opt_lang"\n" -i $VIRTUAL_ENV/bin/activate
    fi
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
      opt_pyver=$($PYTHON --version 2>&1 | grep --color=never -Eo "[0-9]\.[0-9]" | head -n1)
      PIP=$(which pip$opt_pyver 2>/dev/null)
      [[ -z $PIP ]] && PIP="$PYTHON -m pip"
    else
      PYTHON=$(which python 2>/dev/null)
      opt_pyver=$($PYTHON --version 2>&1 | grep --color=never -Eo "[0-9]\.[0-9]" | head -n1)
      PIP=$(which pip 2>/dev/null)
      [[ -z $PIP ]] && PIP="$PYTHON -m pip"
    fi
}

find_odoo_path() {
# find_odoo_path(path opts)
    local p v x y
    [[ -n "$1" && -d $1 ]] && p="$1"
    if [[ -n $p ]]; then
      x=$(basename $p)
      [[ $x =~ ^VENV && -d $p/odoo ]] && p="$p/odoo"
      [[ $x =~ ^venv_odoo && -d $p ]] && p=$(dirname $p)
    fi
    [[ -z $p && -n $opt_oepath ]] && p="$opt_oepath"
    [[ -z $p && -n $opt_oever && -d $HOME/$opt_oever ]] && p="$HOME/$opt_oever"
    [[ $opt_verbose -gt 2 ]] && echo ">>> find $2 $p -maxdepth 3 -type f -not -path \"*tmp*\" -a -not -path \"*old*\" -not -path \"*/__to_remove/*\" -not -path \"*/lib/*\" -not -path \"*/lib64/*\" -not -path \"*/tests/res/*\" -not -path \"*/include/*\" -not -path \"*/.*/*\" -not -path \"*/node_modules/*\"  ( -name odoo-bin -o -name openerp-server )"
    for f in $(find $2 $p -maxdepth 3 -type f -not -path "*tmp*" -a -not -path "*old*" -not -path "*/__to_remove/*" -not -path "*/lib/*" -not -path "*/lib64/*" -not -path "*/tests/res/*" -not -path "*/include/*" -not -path "*/.*/*" -not -path "*/node_modules/*" \( -name odoo-bin -o -name openerp-server \) 2>/dev/null|sort); do
        opt_oepath=$(dirname $f)
        break
    done
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
    eval $x=$($PIP show "$p" 2>/dev/null | grep "Version" | grep --color=never -Eo "[0-9.]+")
  done
}

check_installed_pkgs() {
  [[ $opt_verbose -gt 2 ]] && echo ">>> check_installed_pkgs()"
  local mime p p2 popts x
  check_4_needing_pkgs
  [[ $opt_alone -ne 0 && ! $pkg =~ $UNISOLATED_PKGS ]] && popts="--isolated --disable-pip-version-check --no-python-version-warning --no-cache-dir" || popts="--disable-pip-version-check --no-python-version-warning"
  [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
  [[ $PIPVER -eq 19 && ! 2020-resolver =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
  [[ $PIPVER -eq 21  && ! in-tree-build =~ $popts  ]] && popts="$popts --use-feature=in-tree-build $popts"
  [[ $opt_verbose -lt 2 ]] && popts="$popts -q"
  for p in $NEEDING_PKGS; do
    x=${p^^}
    [[ $opt_debug -ne 0 && $p =~ $LOCAL_PKGS ]] && p2=" --extra-index-url https://testpypi.python.org/pypi" || p2=""
    p2=""
    [[ $opt_verbose -gt 2 && -z "${!x}" ]] && echo ">>> $PIP install $popts$p2 $p"
    [[ $opt_verbose -lt 2 ]] && echo -en "."
    [[ -z "${!x}" ]] && $PIP install $popts$p2 $p
  done
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
  local f p x
  if [[ -z "$opt_oever" && -n "$opt_oepath" ]]; then
    [[ -d $opt_oepath/openerp ]] && f="$opt_oepath/openerp/release.py" || f="$opt_oepath/odoo/release.py"
    opt_oever=$(grep "^version_info" $f|cut -d= -f2|tr -d "("|tr -d ")"|tr -d " "|awk -F, '{print $1 "." $2}')
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
  [[ $opt_alone -eq 2 && "$HOME" == "$SAVED_HOME" ]] && echo -e "${RED}Virtual Environment $HOME not isolated!${CLR}"
  [[ $opt_verbose -gt 0 && "$HOME" != "$SAVED_HOME" ]] && echo "Isolated environment $HOME (-I switch, parent $SAVED_HOME)."
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
  local d f mime VENV V sitecustom x
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
  BINPKGS=$(get_req_list "" "bin")
  [[ $opt_verbose -gt 2 ]] && echo "BINPKGS=$BINPKGS #$(get_req_list '' 'bin' 'debug')"
  OEPKGS=$(get_req_list "" "python")
  [[ $opt_verbose -gt 2 ]] && echo "OEPKGS=$OEPKGS #$(get_req_list '' 'python' 'debug')"
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
    x=$($PIP --version|grep --color=never -Eo "python *[23]"|grep --color=never -Eo "[23]")
    [[ $x == "2" ]] && run_traced "$PIP install \"pip<21.0\" -U" || run_traced "$PIP install pip -U"
    PIPVER=$($PIP --version | grep --color=never -Eo "[0-9]+" | head -n1)
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
  local f p pkg v VENV xpkgs SAVED_PATH x
  local venvexe pyexe pypath
  VENV="$1"
  [[ $VENV =~ /$ ]] && VENV="${VENV:0: -1}"
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
    opt_pyver=$($PYTHON --version 2>&1 | grep --color=never -Eo "[0-9]\.[0-9]" | head -n1)
    PIP=$(which pip$opt_pyver 2>/dev/null)
    [[ -z $PIP ]] && PIP="$PYTHON -m pip"
  elif [[ -n $opt_pyver ]]; then
    PYTHON=$(which python$opt_pyver 2>/dev/null)
    [[ -z "$PYTHON" && $opt_pyver =~ ^3 ]] && PYTHON=python3
    [[ -z "$PYTHON" && $opt_pyver =~ ^2 ]] && PYTHON=python2
    PYTHON=$(which $PYTHON 2>/dev/null)
    [[ -z "$PYTHON" ]] && PYTHON=$(which python 2>/dev/null)
    opt_pyver=$($PYTHON --version 2>&1 | grep --color=never -Eo "[0-9]\.[0-9]" | head -n1)
    PIP=$(which pip$opt_pyver 2>/dev/null)
    [[ -z $PIP ]] && PIP="$PYTHON -m pip"
  else
    PYTHON=$(which python 2>/dev/null)
    opt_pyver=$($PYTHON --version 2>&1 | grep -o "[0-9]\.[0-9]" | head -n1)
    PIP=$(which pip 2>/dev/null)
    [[ -z $PIP ]] && PIP="$PYTHON -m pip"
  fi
  [[ -n "$PIP" ]] && PIPVER=$($PIP --version | grep --color=never -Eo "[0-9]+" | head -n1)
  validate_py_oe_vers
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  venvexe=$(which virtualenv 2>/dev/null)
  if [[ -n "$venvexe" ]]; then
    v=$(virtualenv --version 2>&1 | grep --color=never -Eo "[0-9]+" | head -n1)
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
  venv_mgr_check_src_path "$VENV"
  x=$($PIP --version|grep --color=never -Eo "python *[23]"|grep --color=never -Eo "[23]")
  [[ $x == "2" ]] && run_traced "$PIP install \"pip<21.0\" -Uq" || run_traced "$PIP install pip -Uq"
  PIPVER=$($PIP --version | grep --color=never -Eo "[0-9]+" | head -n1)
  run_traced "$PIP install \"setuptools<58.0\" -Uq"
  [[ $opt_verbose -ne 0 && PRINTED_PIPVER -eq 0 ]] && echo "# $PIP.$PIPVER ..." && PRINTED_PIPVER=1
  check_installed_pkgs
  pypath=$(find $VENV/lib -type d -name "python$opt_pyver")
  [[ -n "$pypath" && -d $pypath/site-packages ]] && pypath=$pypath/site-packages || pypath=$(find $(readlink -f $(dirname $(which $PYTHON))/../lib) -type d -name site-packages)
  if [[ -n "$opt_oepath" && -n "$opt_oever" ]]; then
    BINPKGS=$(get_req_list "" "bin")
    [[ $opt_verbose -gt 2 ]] && echo "BINPKGS=$BINPKGS #$(get_req_list '' 'bin' 'debug')"
    OEPKGS=$(get_req_list "" "python")
    [[ $opt_verbose -gt 2 ]] && echo "OEPKGS=$OEPKGS #$(get_req_list '' 'python' 'debug')"
    bin_install_1 $VENV
  fi
  [[ $opt_dry_run -eq 0 ]] && custom_env $VENV $opt_pyver
  pip_install_1
  [[ -n "$opt_oever" ]] && pip_install_2
  [[ -n "$opt_rfile" ]] && pip_install_req
  [[ -n "$opt_oepath" && -d $opt_oepath ]] && x=$(basename $opt_oepath) || x=""
  [[ -n "$x" ]] && run_traced "ln -s $opt_oepath $(readlink -f pypath/$x)"
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
  pkg="$(get_actual_pkg $3)"
  [[ $pkg =~ "-e " ]] && pkg=${pkg//-e /--editable=}
  if [[ $opt_alone -ne 0 && ! $pkg =~ $UNISOLATED_PKGS ]]; then
    V=""
    for d in ${PATH//:/ }; do
      [[ $d =~ ^$HOME/ || $d =~ ^/(usr/bin) ]] && V="$V:$d"
    done
    PATH=${V:1}
    [[ $opt_verbose -ne 0 ]] && echo "$ PATH=$PATH"
  fi
  if [[ $cmd == "uninstall" ]]; then
    pip_uninstall "$pkg"
  else
    [[ $opt_alone -ne 0 && ! $pkg =~ $UNISOLATED_PKGS ]] && popts="--isolated --disable-pip-version-check --no-python-version-warning --no-cache-dir" || popts="--disable-pip-version-check --no-python-version-warning"
    [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
    [[ $PIPVER -eq 19 && ! 2020-resolver =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
    [[ $PIPVER -eq 21  && ! in-tree-build =~ $popts  ]] && popts="$popts --use-feature=in-tree-build $popts"
    [[ $opt_verbose -lt 2 ]] && popts="$popts -q"
    if [[ $cmd =~ (info|show) ]]; then
      pkg=$(get_pkg_wo_version $pkg)
      if [[ $pkg =~ $BIN_PKGS ]]; then
        check_bin_package "$pkg"
      else
        run_traced "$PIP show $pkg"
        x=$($PIP show $pkg | grep -E ^Location | awk -F: '{print $2}' | sed -e "s| ||")
        [[ -n $x ]] && x=$x/$pkg
        [[ -L $x ]] && echo "Actual location is $(readlink -e $x)"
      fi
    fi
    [[ $cmd == "install" ]] && pip_install "$pkg"
    [[ "$cmd" == "uninstall" ]] && run_traced "$PIP $cmd $pkg"
    [[ $cmd == "update" ]] && pip_install "$pkg" "--upgrade"
  fi
  do_deactivate
  export PATH=$SAVED_PATH
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


OPTOPTS=(h        a        B         C      D       E          f         F      k        I           i         l        n           O         o          p         q           r           s                    t          V           v)
OPTLONG=(help     ""       ""        ""     devel   distro     force     ""     keep     indipendent isolated  lang     dry_run     odoo-ver  odoo-path  python    quiet       requirement system-site-packages travis     version     verbose)
OPTDEST=(opt_help opt_bins opt_debug opt_cc opt_dev opt_distro opt_force opt_FH opt_keep opt_alone   opt_alone opt_lang opt_dry_run opt_oever opt_oepath opt_pyver opt_verbose opt_rfile   opt_spkg             opt_travis opt_version opt_verbose)
OPTACTI=('+'      "="      "+"       1      1       "="        1         "="    1        2           1         "="      1           "="       "="        "="       0           "="         1                    1          "*>"        "+")
OPTDEFL=(1        ""       0         0      0       ""         0         ""     0        0           0         ""       0           ""        ""         ""        0           ""          0                    0          ""          -1)
OPTMETA=("help"   "list"   ""        ""     ""      "distro"   ""        "name" ""       ""          ""        "iso"    ""          "version" "dir"      "pyver"   ""          "file"      ""                   ""         "version"   "verbose")
OPTHELP=("this help"
  "bin packages to install (* means wkhtmltopdf,lessc)"
  "use unstable packages: -B testpypi / -BB from ~/tools / -BBB from ~/pypi / -BBBB link to local ~/pypi"
  "clear cache before executing pip command"
  "create v.environment with development packages"
  "Simulate Linux distro: like Ubuntu20 Centos7 etc (requires -n switch)"
  "force v.environment create, even if exists or inside another virtual env"
  "Simulate Linux family: may be RHEL or Debian (requires -n switch)"
  "keep python2 executable as python (deprecated)"
  "run pip in an isolated mode and set home virtual directory"
  "run pip in an isolated mode, ignoring environment variables and user configuration"
  "set default language"
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
[[ $opt_dry_run -eq 0 ]] && opt_FH="" && opt_distro=""
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
SAVED_HOME_DEVEL=$HOME_DEVEL
SAVED_PYTHONPATH=$PYTHONPATH
PRINTED_PIPVER=0
[[ $opt_alone -ne 0 ]] && PYTHONPATH=""
FLAG=">"
[[ $opt_dry_run -eq 0 ]] && FLAG="\$"
LIST_REQ="$(which list_requirements.py)"

if [[ $action == "rm" ]]; then
  [[ $PWD == $(readlink -f $p2) ]] && cd
  rm -fR $p2
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  unset PYTHON PIP
  exit 0
elif [[ ! $action =~ (help|create) ]]; then
  do_activate "$p2" "-q"
  venv_mgr_check_src_path "$p2"
  [[ -z $opt_oepath ]] && find_odoo_path "$p2" "-L" || find_odoo_path "$opt_oepath" "-L"
  venv_mgr_check_oever
  check_installed_pkgs
  validate_py_oe_vers
fi
[[ "$opt_bins" == "*" ]] && opt_bins="${BIN_PKGS//|/,}" && opt_bins="${opt_bins:1:-1}"
if [[ $action =~ (help|create|exec|python|shell) || $opt_dev -eq 0 || -z "$FUTURE" || -z "$CONFIGPARSER" || -z "$Z0LIB" || -z "$OS0" || -z $(which list_requirements.py 2>/dev/null) ]]; then
  [[ $opt_dev -eq 0 ]] && DEV_PKGS=""
else
  DEV_PKGS=$(get_req_list "")
  [[ $opt_verbose -gt 2 ]] && echo "DEV_PKGS=$DEV_PKGS #$(get_req_list '' '' 'debug')"
fi
if [[ "$action" == "help" ]]; then
  man $(dirname $0)/man/man8/$(basename $0).8.gz
elif [[ "$action" == "exec" ]]; then
  do_venv_exec "$p2" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [[ "$action" == "python" ]]; then
  do_venv_exec "$p2" "python" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [[ "$action" == "shell" ]]; then
  do_venv_exec "$p2" "$SHELL -i" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [[ $action =~ (info|install|show|uninstall|update) ]]; then
  [[ $opt_cc -ne 0 && -d $HOME/.cache/pip ]] && run_traced "rm -fR $HOME/.cache/pip"
  do_venv_pip "$p2" "$action" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
  do_deactivate "-q"
elif [[ "$action" == "create" ]]; then
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
  [[ ! $opt_pyver =~ ^3 && $FH == "RHEL" ]] && PKGLIST="python-devel"
  [[ $opt_pyver =~ ^3 && $FH == "RHEL" ]] && PKGLIST="python3-devel python3-pip python3-venv"
  [[ ! $opt_pyver =~ ^3 && $FH != "RHEL" ]] && PKGLIST="python-dev"
  [[ $opt_pyver =~ ^3 && $FH != "RHEL" ]] && PKGLIST="python3-dev python3-pip python3-venv"
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libsass-devel"
  [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST zlib-devel" || PKGLIST="$PKGLIST zlib1g-dev"
  echo "$XTAL install $PKGLIST"
  if [[ $ERROR_PKGS =~ lxml ]]; then
    PKGLIST=""
    [[ $DISTO == "Fedora" ]] && PKGLIST="redhat-rpm-config"
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libxml2-devel" || PKGLIST="$PKGLIST libxml2-dev"
    [[ $FH == "RHEL" ]] && PKGLIST="$PKGLIST libxslt-devel" || PKGLIST="$PKGLIST libxslt-dev"
    [[ $opt_pyver =~ ^3 ]] && PKGLIST="$PKGLIST python3-lxml" || PKGLIST="$PKGLIST python-lxml"
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
