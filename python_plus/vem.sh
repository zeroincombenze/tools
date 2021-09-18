#! /bin/bash
#
# Manage virtual environment
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2018-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$($READLINK -f $(dirname $0))
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys\np=[x for x in (os.environ['PATH']+':$TDIR:..:$HOME_DEV').split(':') if x not in sys.path];p.extend(sys.path);print(' '.join(p))"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$($READLINK -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"

__version__=1.0.3
declare -A PY3_PKGS
NEEDING_PKGS="future clodoo configparser os0 z0lib"
DEV_PKGS="coveralls codecov flake8 pycodestyle pylint"
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

cd_venv() {
  # cd_venv(VENV -q)
  [[ $opt_verbose -gt 2 ]] && echo ">>> cd_venv($@)"
  if [[ ! "$1" == "$PWD" || $2 =~ f ]]; then
    [[ ! -d $1 && $opt_dry_run -ne 0 ]] && mkdir $1 && FINAL_CMD="rm -fR $1"
    [[ $2 =~ q || $opt_verbose -eq 0 ]] || echo "$FLAG pushd $1 >/dev/null"
    if [[ -d $1 ]]; then
      pushd $1 >/dev/null
      ((DO_POP++))
    fi
    [[ $opt_verbose -gt 2 ]] && echo "$PWD>"
  fi
}

pop_cd() {
  [[ $opt_verbose -gt 2 ]] && echo ">>> pop_cd($@)"
  if [[ $DO_POP -ne 0 ]]; then
    [[ $1 =~ q || $opt_verbose -eq 0 ]] || echo "$FLAG popd >/dev/null"
    if [[ $DO_POP -gt 0 ]]; then
      popd >/dev/null
      ((DO_POP--))
      [[ -n "$FINAL_CMD" ]] && eval $FINAL_CMD && unset FINAL_CMD
    fi
    [[ $opt_verbose -gt 2 ]] && echo "$PWD>DO_POP=$DO_POP"
  fi
}

do_activate() {
  local i f
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_activate($@)"
  [[ -z $VENV_STACK ]] && declare -A VENV_STACK && export VENV_STACK
  if [[ -z "$VIRTUAL_ENV" ]]; then
    [[ $1 =~ q || $opt_verbose -eq 0 ]] || echo "$FLAG source bin/activate"
    [[ ! -f bin/activate && -n "$FINAL_CMD" ]] && DO_DEACT=1 && return
    [[ ! -f bin/activate ]] && echo "Fatal error! bin/activate not found in $PWD" && exit 1
    [[ $opt_verbose -gt 3 ]] && set +x
    [[ $opt_verbose -ge 3 ]] && echo "$FLAG source bin/activate"
    . bin/activate
    [[ $opt_verbose -ge 3 && -n $NVM_DIR && -f $NVM_DIR/nvm.sh ]] && echo "$FLAG source $NVM_DIR/nvm.sh"
    [[ -n $NVM_DIR && -f $NVM_DIR/nvm.sh ]] && . $NVM_DIR/nvm.sh
    [[ $opt_verbose -gt 3 ]] && set -x
    ((i = ${#VENV_STACK[@]}))
    VENV_STACK[$i]=$VIRTUAL_ENV
    DO_DEACT=1
  else
    f=0
    for i in "${!VENV_STACK[@]}"; do
      if [[ ${VENV_STACK[i]} == $VIRTUAL_ENV ]]; then
        f=1
        break
      fi
    done
    ((i = ${#VENV_STACK[@]}))
    [[ $f -eq 0 ]] && VENV_STACK[$i]=$VIRTUAL_ENV
  fi
}

do_deactivate() {
  local i VENV OLD_VENV
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_deactivate($@)"
  if [ $DO_DEACT -ne 0 ]; then
    [[ $1 =~ q || $opt_verbose -eq 0 ]] || echo "$FLAG deactivate"
    [[ ! -f bin/activate && -n "$FINAL_CMD" ]] && DO_DEACT=0 && return
    VENV="$VIRTUAL_ENV"
    if [[ -n $VENV_STACK ]]; then
      for i in "${!VENV_STACK[@]}"; do
        if [[ ${VENV_STACK[i]} == $VENV ]]; then
          OLD_VENV=${VENV_STACK[$i]}
          unset VENV_STACK[$i]
        fi
      done
    fi
    deactivate
    DO_DEACT=0
    [[ -n "$OLD_VENV" ]] && VIRTUAL_ENV=$OLD_VENV
  fi
}

run_traced() {
  local xcmd="$1"
  local sts=0
  local PMPT=
  [[ $opt_dry_run -ne 0 ]] && PMPT="> " || PMPT="\$ "
  [[ $opt_verbose -eq 0 ]] || echo "$PMPT$xcmd"
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
  grep "version" ./setup.py|awk -F= '{print $2}'|tr -d "'"|tr -d ","
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

set_python_exe() {
    #set_python_exe(cmd venv)
    local cmd d f mime V VENV_TGT
    cmd="$1"
    V="$2"
    d=$(find $V \( -type f -executable -o -name "*.py" \)|tr "\n" " ")
    for f in $d; do
      grep -q "^#\!.*/bin.*python[23]?$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/bin.*python[23]?|#\!$PYTHON|\" $f" && chmod +x $f
    done
}

bin_install() {
  #bin_install(pkg VENV)
  [[ $opt_verbose -gt 2 ]] && echo ">>> bin_install($@)"
  local x
  local reqver size
  local FH=$(xuname -f)
  local MACHARCH=$(xuname -m)
  local dist=$(xuname -d)
  dist=${dist,,}$(xuname -v | grep -Eo [0-9]* | head -n1)
  local pkg=$1 VENV=$2
  [[ -z "$VENV" ]] && VENV="$HOME"
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    if [[ $pkg =~ lessc ]]; then
      [[ $pkg == "lessc" ]] && pkg="less@3.0.4"
      pkg=${pkg/==/@}
      pkg=$(echo $pkg | tr -d "'")
      run_traced "npm install $pkg"
      run_traced "npm install less-plugin-clean-css"
      x=$(find $(npm bin) -name lessc 2>/dev/null)
      [ -n "$x" ] && run_traced "ln -s $x $VENV/bin"
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
  # bin_install_1(VENV)
  [[ $opt_verbose -gt 2 ]] && echo ">>> bin_install_1($@)"
  local pkg VENV=$1
  local binreq bin_re
  [[ -n "$opt_bins" ]] && binreq="${opt_bins//,/ }"
  if [[ -n "$opt_bins" ]]; then
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m.Analyzing $opt_bins\e[0m"
    for pkg in $binreq; do
      bin_install $pkg $VENV
    done
  fi
}

pip_install() {
  #pip_install(pkg opts)
  local pkg d x srcdir fn popts v
  local pypath=$(find $(readlink -f $(dirname $(which $PYTHON))/../lib) -type d -name "python$opt_pyver")
  [[ -n "$pypath" && -d $pypath/site-packages ]] && pypath=$pypath/site-packages || pypath=$VIRTUAL_ENV/lib/python$opt_pyver/site-packages
  pkg="$(get_actual_pkg $1)"
  [[ $pkg =~ "-e " ]] && pkg=${pkg//-e /--editable=}
  [[ $opt_alone -ne 0 && ! $pkg =~ ^.?- ]] && popts="--isolated --disable-pip-version-check --no-cache-dir" || popts="--disable-pip-version-check"
  [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
  [[ $PIPVER -eq 19 && ! use-feature =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
  [[ $opt_verbose -eq 0 ]] && popts="$popts -q"
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    if [[ ! $pkg =~ $BIN_PKGS ]]; then
      srcdir=""
      [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
      [[ $opt_debug -eq 2 && -d $SAVED_HOME/tools/$fn ]] && srcdir=$($READLINK -f $SAVED_HOME/tools/$fn)
      if [[ $opt_debug -ge 3 ]]; then
        [[ -d $SAVED_HOME/dev/pypi/$fn/$fn ]] && srcdir=$($READLINK -f $SAVED_HOME/dev/pypi/$fn/$fn)
        [[ -d $SAVED_HOME/devel/pypi/$fn/$fn ]] && srcdir=$($READLINK -f $SAVED_HOME/devel/pypi/$fn/$fn)
      fi
      if [[ $pkg =~ ^(odoo|openerp)$ && -z $opt_oepath ]]; then
        echo "Missed Odoo version to install (please use -O and/or -o switch)!"
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
      [[ -d $pypath/$fn && ! -L $pypath/$fn ]] && run_traced "rm -fR $pypath/$fn"
      [[ -L $pypath/$fn ]] && run_traced "rm -f $pypath/$fn"
      if [[ $opt_debug -eq 3 ]]; then
        [[ $PIPVER -gt 20 ]] && popts="$popts --use-feature=in-tree-build"
        run_traced "$PIP install $popts $srcdir/$fn"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      else
        pushd $srcdir/.. >/dev/null
        [[ $pkg =~ ^(odoo|openerp)$ ]] && x="$opt_oever" || x=$(get_local_version $fn)
        v=$([[ $(echo $x|grep "mismatch") ]] && echo $x|awk -F/ '{print $2}' || echo $x)
        popd >/dev/null
        x=$(ls -d $pypath/${fn}-*dist-info 2>/dev/null|grep -E "${fn}-[0-9.]*dist-info")
        [[ -n $x && $x != $pypath/${fn}-${v}.dist-info ]] && run_traced "mv $x $pypath/${fn}-${v}.dist-info"
        if [[ ! -d $pypath/${fn}-${v}.dist-info ]]; then
          run_traced "mkdir $pypath/${fn}-${v}.dist-info"
          for d in INSTALLER METADATA RECORD REQUESTED top_level.txt WHEEL; do
            run_traced "touch $pypath/${fn}-${v}.dist-info/$d"
          done
        fi
        run_traced "ln -s $srcdir $pypath/$fn"
        [[ $? -ne 0 && ! $ERROR_PKGS =~ $pkg ]] && ERROR_PKGS="$ERROR_PKGS   '$pkg'"
      fi
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
        [[ $DISTO != "Fedora" && $FH = "RHEL" ]] && echo "yum install bzr"
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
  local pkg
  [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m2 - Analyzing $SUP_PKGS $SECURE_PKGS $DEV_PKGS\e[0m (1)"
  for pkg in $SUP_PKGS $SECURE_PKGS $DEV_PKGS; do
    pip_install "$pkg" "$1"
  done
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
  local f fn pkg flist cmd
  for f in ${opt_rfile//,/ }; do
    fn=$($READLINK -f $f)
    [ -z "$fn" ] && echo "File $f not found!"
    [ -z "$fn" ] && continue
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing file $fn\e[0m"
    cmd="$LIST_REQ -qt python -BP"
    [[ $opt_dev -ne 0 ]] && cmd="${cmd}TR"
    [[ -n "$opt_pyver" ]] && cmd="$cmd -y$opt_pyver"
    [[ -n "$opt_oever" ]] && cmd="$cmd -b$opt_oever"
    [[ -d $HOME/OCA ]] && cmd="$cmd -d${HOME}/OCA"
    [[ $opt_verbose -gt 1 ]] && echo "$cmd -m $fn -qs\" \""
    flist=$($cmd -m $fn -qs" ")
    [[ $opt_verbose -gt 2 ]] && echo "flist=$flist"
    for pkg in $flist; do
      pip_install "$pkg" "$1"
    done
  done
}

pip_uninstall() {
  #pip_uninstall(pkg opts)
  local pkg d x srcdir fn popts v
  local pypath=$VIRTUAL_ENV/lib/python$opt_pyver/site-packages
  pkg=$(get_pkg_wo_version $(get_actual_pkg $1))
  [[ $opt_verbose -eq 0 ]] && popts="$popts -q"
  if [[ -z "$XPKGS_RE" || ! $pkg =~ ($XPKGS_RE) ]]; then
    srcdir=""
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && fn=${pkg//-/_} || fn=$pkg
    [[ $opt_debug -eq 2 && -d $SAVED_HOME/tools/$fn ]] && srcdir=$($READLINK -f $SAVED_HOME/tools/$fn)
    [[ $opt_debug -eq 3 && -d $SAVED_HOME/dev/pypi/$fn/$fn ]] && srcdir=$($READLINK -f $SAVED_HOME/dev/pypi/$fn/$fn)
    [[ $opt_debug -eq 3 && -d $SAVED_HOME/devel/pypi/$fn/$fn ]] && srcdir=$($READLINK -f $SAVED_HOME/devel/pypi/$fn/$fn)
    if [[ -n "$srcdir" ]]; then
      [[ -d $pypath/$fn && ! -L $pypath/$fn ]] && run_traced "rm -fR $pypath/$fn"
      pushd $srcdir/.. >/dev/null
      [[ $pkg =~ ^(odoo|openerp)$ ]] && x="$opt_oever" || x=$(get_local_version $fn)
      v=$([[ $(echo $x|grep "mismatch") ]] && echo $x|awk -F/ '{print $2}' || echo $x)
      popd >/dev/null
      x=$(ls -d $pypath/${fn}-*dist-info 2>/dev/null|grep -E "${fn}-[0-9.]*dist-info")
      [[ -n $x && $x != $pypath/${fn}-${v}.dist-info ]] && run_traced "rm $x"
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
  curver=$($pkg --version 2>/dev/null | grep -Eo [0-9]+\.[0-9]+\.?[0-9]* | head -n1)
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
    x=$($READLINK -e $(which $pkg 2>/dev/null) 2>/dev/null)
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
    curver=$($PIP show $pkg | grep ^[Vv]ersion | awk -F: '{print $2}' | tr -d ', \r\n\(\)') || curver=
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
  x=$($PIP show $pkg | grep ^[Ll]ocation | awk -F: '{print $2}' | tr -d ', \r\n\(\)')
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
  local f fn pkg cmd=$1 flist cmd
  for f in ${opt_rfile//,/ }; do
    fn=$($READLINK -f $f)
    [ -z "$fn" ] && echo "File $f not found!"
    [ -z "$fn" ] && continue
    [[ $opt_verbose -gt 0 ]] && echo -e "\e[1m-- Analyzing file $fn\e[0m"
    cmd="$LIST_REQ -qt python -BP"
    [[ $opt_dev -ne 0 ]] && cmd="${cmd}TR"
    [[ -n "$opt_pyver" ]] && cmd="$cmd -y$opt_pyver"
    [[ -n "$opt_oever" ]] && cmd="$cmd -b$opt_oever"
    [[ -d $HOME/OCA ]] && cmd="$cmd -d${HOME}/OCA"
    [[ $opt_verbose -gt 1 ]] && echo "$cmd -m $fn -qs\" \""
    flist=$($cmd -m $fn -qs" ")
    [[ $opt_verbose -gt 1 ]] && echo "--> $flist"
    for pkg in $flist; do
      check_package $pkg $cmd
    done
  done
}

package_debug() {
  # package_debug(VENV)
  local VENV=$1
  local pkg pkgdir
  local pkgs="${LOCAL_PKGS//|/ }"
  pkgs="${pkgs:1:-1}"
  # [[ -d $HOME/dev/pypi ]] && pkgdir=$HOME/dev/pypi
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
  [[ $opt_verbose -gt 2 ]] && echo ">>> custom_env($@)"
  local VIRTUAL_ENV=$1 pyver=$(echo $2|grep -Eo [0-9]|head -n1)
  sed -i -e 's:VIRTUAL_ENV=.*:VIRTUAL_ENV="\$($READLINK -f \$(dirname \$($READLINK -f \$BASH_SOURCE))/..)":g' $PWD/bin/activate
  if $(grep -q "^export HOME=" $PWD/bin/activate); then
    sed -i -e 's|^export HOME=.*|export HOME="\$VIRTUAL_ENV"|g' $PWD/bin/activate
  elif $(grep -q "^# export HOME=" $PWD/bin/activate); then
    sed -i -e 's|^# export HOME=.*|# export HOME="\$VIRTUAL_ENV"|g' $PWD/bin/activate
  else
    sed -ri "/deactivate *\(\) *\{/i\READLINK=\$(which greadlink 2>/dev/null) || READLINK=\$(which readlink 2>/dev/null)" $PWD/bin/activate
    sed -ri "/deactivate *\(\) *\{/i\export READLINK\n" $PWD/bin/activate
    [[ $opt_alone -gt 1 ]] && sed -ri "/deactivate *\(\) *\{/a\    export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" $PWD/bin/activate
    [[ $opt_alone -gt 1 ]] && sed -ri "/deactivate *\(\) *\{/a\    # export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" $PWD/bin/activate
    [ $pyver -gt 2 -a $opt_keep -eq 0 ] && sed -ri "/deactivate *\(\) *\{/a\    unalias pip &>/dev/null" $PWD/bin/activate
    [ $pyver -gt 2 -a $opt_keep -eq 0 ] && sed -ri "/deactivate *\(\) *\{/a\    unalias python &>/dev/null" $PWD/bin/activate
    [ $opt_spkg -ne 0 -a -n "$2" ] && echo "[ -f /usr/bin/pip$2 -a ! -f \$VIRTUAL_ENV/bin/pip ] && ln -s /usr/bin/pip$2 \$VIRTUAL_ENV/bin/pip" >>$PWD/bin/activate
    echo "for f in \$VIRTUAL_ENV/bin/*;do" >>$PWD/bin/activate
    echo "    [[ -x \$f && ! -d \$f ]] && grep -q \"^#\!.*[ /]python\" \$f &>/dev/null && sed -i -e \"s|^#\!.*[ /]python|#\!\$VIRTUAL_ENV/bin/python|\" \$f" >>$PWD/bin/activate
    echo "done" >>$PWD/bin/activate
    [ $opt_alone -gt 1 ] && echo "export HOME=\"\$VIRTUAL_ENV\"" >>$PWD/bin/activate
    [ $opt_alone -le 1 ] && echo "# export HOME=\"\$VIRTUAL_ENV\"" >>$PWD/bin/activate
    [ $pyver -gt 2 -a $opt_keep -eq 0 ] && echo "alias pip=\"$PIP\"" >>$PWD/bin/activate
    [ $pyver -gt 2 -a $opt_keep -eq 0 ] && echo "alias python=\"$PYTHON\"" >>$PWD/bin/activate
  fi
  sed -i -e 's|PATH="\$VIRTUAL_ENV/bin:\$PATH"|PATH="\$VIRTUAL_ENV/.local/bin:\$VIRTUAL_ENV/bin:\$PATH"|g' $PWD/bin/activate
  if [ $opt_spkg -ne 0 ]; then
    if [[ -d $PWD/.local/lib/python$2/site-packages ]]; then
      echo -e "import site\nsite.addsitedir('$PWD/.local/lib/python$2/site-packages')\nsite.addsitedir('/usr/lib/python$2/site-packages')\nsite.addsitedir('/usr/lib64/python$2/site-packages')\n" >$PWD/lib/python$2/site-packages/sitecustomize.py
    else
      echo -e "import site\nsite.addsitedir('/usr/lib/python$2/site-packages')\nsite.addsitedir('/usr/lib64/python$2/site-packages')\n" >$PWD/lib/python$2/site-packages/sitecustomize.py
    fi
  elif [[ -d $PWD/.local/lib/python$2/site-packages ]]; then
    echo -e "import site\nsite.addsitedir('$PWD/.local/lib/python$2/site-packages')\n" >$PWD/lib/python$2/site-packages/sitecustomize.py
  fi
}

venv_mgr_check_src_path() {
  # venv_mgr_check_src_path(VENV create)
  [[ $opt_verbose -gt 2 ]] && echo ">>> venv_mgr_check_src_path($@)"
  local f VENV
  VENV="$1"
  if [[ -z "$VENV" && $2 != "create" ]]; then
    for f in $(find . -max-depth 2 -type f -name activate); do
      [[ -d $f/../lib && -d $f/../bin ]] && VENV=$($READLINK -e $f/../..) && break
    done
  fi
  if [[ -z "$VENV" ]]; then
    echo "Missed virtual environment path!!"
    exit 1
  fi
  if [[ $2 != "create" && ( ! -d $VENV || ! -d $VENV/lib || ! -d $VENV/bin || ! -f $VENV/bin/activate ) ]]; then
    echo "Invalid virtual env $VENV!!"
    exit 1
  fi
  if [[ -z "$PYTHON" || ! -x $PYTHON ]]; then
    PYTHON=""
    PIP=""
    if [[ -n "$opt_pyver" ]]; then
      [[ -z "$PYTHON" && -x $opt_pyver ]] && PYTHON=$opt_pyver && opt_pyver=$($PYTHON --version 2>&1 | grep -o [0-9]\.[0-9] | head -n1) && PIP="$PYTHON -m pip"
      [[ -z "$PYTHON" && -n $opt_pyver ]] && PYTHON=$(which python$opt_pyver 2>/dev/null) && PIP="$PYTHON -m pip"
      [[ -z "$PYTHON" && -n $opt_pyver && $opt_pyver =~ ^3 ]] && PYTHON=python3
      [[ -z "$PYTHON" && -n $opt_pyver && $opt_pyver =~ ^2 ]] && PYTHON=python
    fi
    if [[ -z "$PYTHON" && $2 != "create" ]]; then
      for f in $VENV/bin/python3.* $VENV/bin/python3* $VENV/bin/python2.* $VENV/bin/python2*; do
        [[ -x $f ]] && PYTHON=$($READLINK -e $f)
        break
      done
      for f in $VENV/bin/pip3.* $VENV/bin/pip3* $VENV/bin/pip2.* $VENV/bin/pip2*; do
        [[ -x $f ]] && PIP=$($READLINK -e $f)
        break
      done
    fi
    if [[ $2 != "create" ]];then
      [[ -z "$PYTHON" && -x $VENV/bin/python3 ]] && PYTHON=$($READLINK -e $VENV/bin/python3)
      [[ -z "$PIP" && -x $VENV/bin/pip3 ]] && PIP=$($READLINK -e $VENV/bin/pip3)
      [[ -z "$PYTHON" && -x $VENV/bin/python ]] && PYTHON=$($READLINK -e $VENV/bin/python)
      [[ -z "$PIP" && -x $VENV/bin/pip ]] && PIP=$($READLINK -e $VENV/bin/pip)
    else
      [[ -z "$PYTHON" ]] && PYTHON=$(which python3 2>/dev/null) && PIP="$PYTHON -m pip"
      [[ -z "$PYTHON" ]] && PYTHON=$(which python 2>/dev/null) && PIP="$PYTHON -m pip"
    fi
    if [[ -z "$PYTHON" ]]; then
      [[ $2 != "create" ]] && echo "Virtual env $VENV without python!!"
      [[ $2 == "create" ]] && echo "Python executable not found!!"
      exit 1
    fi
  fi
  [[ -z "$PIP" ]] && PIP="$PYTHON -m pip"
  opt_pyver=$($PYTHON --version 2>&1 | grep -Eo "[0-9]\.[0-9]")
  [[ $opt_verbose -gt 1 ]] && echo "### Python version $opt_pyver ... ###"
}

check_4_needing_pkgs() {
  local p x
  [[ ! $NEEDING_PKGS =~ clodoo && ( -n "$opt_oepath" || -n "$opt_oever" ) ]] && NEEDING_PKGS="$NEEDING_PKGS clodoo"
  for p in $NEEDING_PKGS; do
    x=${p^^}
    eval $x=$($PIP show $p 2>/dev/null | grep "Version" | grep -Eo "[0-9.]+")
  done
}

check_installed_pkgs() {
  local p x popts
  check_4_needing_pkgs
  [[ ! $NEEDING_PKGS =~ clodoo && ( -n "$opt_oepath" || -n "$opt_oever" ) ]] && NEEDING_PKGS="$NEEDING_PKGS clodoo"
  [[ $PIPVER -eq 19 ]] && popts="--use-feature=2020-resolver" || popts=""
  [[ $opt_verbose -eq 0 ]] && popts="$potps -q"
  for p in $NEEDING_PKGS; do
    x=${p^^}
    [[ $opt_verbose -gt 2 && -z "${!x}" ]] && echo ">>> $PIP install $popts $p"
    [[ -z "${!x}" ]] && $PIP install $popts $p
  done
  LIST_REQ="list_requirements.py"
  if [[ -n "$opt_oepath" || -n "$opt_oever" ]]; then
    if [[ -z $(which list_requirements.py 2>/dev/null) ]]; then
      x=$($PIP show clodoo|grep Location|awk -F: '{print $2}')
      x=$(echo $x/clodoo/list_requirements.py)
      run_traced "chmod +x $x"
      LIST_REQ="$($READLINK -f $x)"
      run_traced "sed -i -e \"s|^#\!.*[ /]python|#\!$PYTHON|\" $x"
    fi
  fi
  check_4_needing_pkgs
}

odoo_orm_path() {
    p=$1
    for x in odoo openerp; do
      [[ -d $1/$x ]] && p="$1/$x" && break
      [[ -d $1/odoo/$x ]] && p="$1/odoo/$x" && break
      [[ -d $1/server/$x ]] && p="$1/server/$x" && break
    done
    eval $READLINK -f $p
}

venv_mgr_check_oever() {
  #venv_mgr_check_oever action venv
  local p x
  if [[ -z "$opt_oever" && ! $1 =~ (help|create) ]]; then
    p=""
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
  #do_venv_mgr_test(VENV)
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_venv_mgr_test($@)"
  local f ssp x VENV
  VENV="$1"
  [[ $opt_verbose -gt 0 ]] && echo "Validation test ..."
  [ $opt_dry_run -ne 0 ] && return
  cd_venv $VENV "-fq"
  if [[ -z "$VIRTUAL_ENV" ]]; then
    do_activate "-q"
    if [[ $opt_verbose -gt 0 ]]; then
      [[ -n "$HOME" && ! "$HOME" == "$SAVED_HOME" ]] && echo "Isolated environment (created with -I switch)."
      [[ "$HOME" == "$SAVED_HOME" ]] && echo "Environment not isolated (created w/o -I switch)."
    fi
  fi
  [[ -z "$HOME" ]] && echo "Wrong environment (No HOME directory declared)."
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
    x=$($READLINK -e $(which $f 2>/dev/null) 2>/dev/null)
    [[ -z "$x" ]] && echo "Corrupted VME: file $f not found!!"
    [[ -z "$x" ]] && continue
    [[ -n "$x" && ! $x =~ ^$VENV ]] && echo "Warning: file $x is outside of virtual env"
  done
  do_deactivate "-q"
  pop_cd "-q"
}

do_venv_mgr() {
  # do_venv_mgr {amend|check|cp|mv|merge|test} VENV NEW_VENV
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_venv_mgr($@)"
  local d f mime VENV V sitecustom x lropts
  local cmd=$1
  VENV="$2"
  [[ -n "$3" ]] && VENV_TGT=$($READLINK -m $3)
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
    grep -q "^ *\[ -x \$f -a ! -d \$f ] " $VENV/bin/activate &>/dev/null
    if [[ $? -eq 0 ]]; then
      echo "Wrong activation script $VENV/bin/activate"
      sed -Ee "s|^ *\[ -x \\\$f -a ! -d \\\$f ] |    [[ -x \$f \&\& ! -d \$f ]] \&\& grep -q \"^#\!.*[ /]python\" \$f \&>/dev/null |" -i $VENV/bin/activate
    fi
  fi
  cd_venv "$VENV" "-fq"
  do_activate "-q"
  [[ -n "$opt_oepath" ]] && lropts="-y $opt_pyver -BPRT -p $opt_oepath" || lropts="-y $opt_pyver -BPRT"
  [[ -n "$opt_oever" ]] && lropts="$lropts -b $opt_oever"
  [[ -d $HOME/OCA ]] && lropts="$lropts -d${HOME}/OCA"
  [[ $opt_verbose -gt 1 ]] && echo "$LIST_REQ -qs' ' $lropts -t bin"
  BINPKGS=$($LIST_REQ -qs' ' $lropts -t bin)
  [[ $opt_verbose -gt 2 ]] && echo "BINPKGS=$BINPKGS"
  [[ $opt_verbose -gt 1 ]] && echo "$LIST_REQ -qs' ' $lropts -t python"
  OEPKGS=$($LIST_REQ -qs' ' $lropts -t python)
  [[ $opt_verbose -gt 2 ]] && echo "OEPKGS=$OEPKGS"
  do_deactivate "-q"
  pop_cd "-q"
  if [[ $cmd =~ (amend|check|test|inspect) ]]; then
    V=$VENV
  elif [[ "$cmd" == "cp" ]]; then
    if [[ -d $VENV_TGT ]]; then
      if [ $opt_force -eq 0 ]; then
        echo "Destination v.environment $VENV_TGT already exists!!"
        echo "use: venv_mgr cp -f VENV NEW_VENV"
        exit 1
      fi
      run_traced "rm -fR $VENV_TGT"
    fi
    [[ -d $(dirname $VENV_TGT) ]] || run_traced "mkdir -p $(dirname $VENV_TGT)"
    run_traced "cp -r $VENV $VENV_TGT"
    V=$VENV_TGT
  elif [[ "$cmd" == "merge" ]]; then
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
  else
    if [[ -d $VENV_TGT ]]; then
      echo "Destination virtual env $VENV_TGT already exists!"
      exit 1
    fi
    V=$VENV
  fi
  if [[ ! $cmd =~ (amend|check|test|inspect) ]]; then
    set_python_exe "$cmd" "$V"
#    [[ $opt_travis -ne 0 ]] && d="$V/bin/* $V/tools/zerobug/_travis $V/tools/z0bug_odoo/travis" || d="$V/bin/*"
#    for f in $V/bin/*; do
#      mime=$(file --mime-type -b $f)
#      if [ "$mime" == "text/x-python" -o "${f: -3}" == ".py" ]; then
#        [[ $opt_verbose -gt 1 ]] && echo "$FLAG sed -i -e \"s|^#\!.*[ /]python|#\!$VENV_TGT/bin/python|\" $f"
#        [[ $opt_dry_run -eq 0 ]] && sed -i -e "s|^#\!.*[ /]python|#\!$VENV_TGT/bin/python|" $f
#        [[ $opt_dry_run -eq 0 && $cmd == "amend" ]] && chmod +x $f
#      fi
#    done
  fi
  if [[ ! $cmd =~ (test|inspect) ]]; then
    cd_venv $V -f
    do_activate
    if [ $opt_dry_run -eq 0 -a -L ./lib64 ]; then
      rm -f ./lib64
      ln -s ./lib ./lib64
    fi
    [[ ! $cmd =~ (amend|check|cp) ]] && bin_install_1 $VENV
    [[ $cmd =~ (amend|check) ]] && bin_check_1 $VENV
    x=$($PIP --version|grep -Eo "python [23]"|grep -Eo [23])
    [[ $x == "2" ]] && run_traced "$PIP install \"pip<21.0\" -U" || run_traced "$PIP install pip -U"
    PIPVER=$($PIP --version | grep -Eo [0-9]+ | head -n1)
    [[ ! $cmd =~ (amend|check|cp) ]] && pip_install_1 "--upgrade"
    [[ $cmd =~ (amend|check) ]] && pip_check_1 $cmd
    [[ -n "$opt_oever" && "$cmd" == "amend" ]] && pip_install_2 "--upgrade"
    [[ -n "$opt_oever" && $cmd =~ (amend|check) ]] && pip_check_2 $cmd
    [[ $cmd == "amend" && -n "$opt_rfile" ]] && pip_install_req "--upgrade"
    [[ $cmd =~ (amend|check) && -n "$opt_rfile" ]] && pip_check_req $cmd
    if [[ ! $cmd == "check" && -z "$VENV_STS" ]]; then
      run_traced "sed -i -e 's:VIRTUAL_ENV=.*:VIRTUAL_ENV=\"'$VENV_TGT'\":g' $PWD/bin/activate"
      if $(grep -q "^# export HOME=" $PWD/bin/activate); then
        [ $opt_alone -le 1 ] && run_traced "sed -i -e 's|^# export HOME=.*|# export HOME=\"\$VIRTUAL_ENV\"|g' $PWD/bin/activate"
        [ $opt_alone -gt 1 ] && run_traced "sed -i -e 's|^# export HOME=.*|export HOME=\"\$VIRTUAL_ENV\"|g' $PWD/bin/activate"
      elif $(grep -q "^export HOME=" $PWD/bin/activate); then
        [ $opt_alone -gt 1 ] && run_traced "sed -i -e 's|^export HOME=.*|export HOME=\"\$VIRTUAL_ENV\"|g' $PWD/bin/activate"
        [ $opt_alone -le 1 ] && run_traced "sed -i -e 's|^export HOME=.*|# export HOME=\"\$VIRTUAL_ENV\"|g' $PWD/bin/activate"
      fi
      if $(grep -q "^ *# export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" $PWD/bin/activate); then
        [ $opt_alone -le 1 ] && run_traced "sed -i -e 's|# export HOME=\$(grep|export HOME=\$(grep|' $PWD/bin/activate"
      elif $(grep -q "^ *export HOME=\$(getent passwd \$USER|awk -F: '{print \$6}')" $PWD/bin/activate); then
        [ $opt_alone -le 1 ] && run_traced "sed -i -e 's|export HOME=\$(grep|# export HOME=\$(grep|' $PWD/bin/activate"
      fi
      if [ $opt_dry_run -eq 0 ]; then
        if [ $opt_spkg -ne 0 ]; then
          if [[ -d $PWD/.local/lib/python$opt_pyver/site-packages ]]; then
            sitecustom=$PWD/.local/lib/python$opt_pyver/site-packages/sitecustomize.py
            echo "import sys" >$sitecustom
            echo -e "import site\nif '$VENV_TGT/.local/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('$VENV_TGT/.local/lib/python$opt_pyver/site-packages')\nif '/usr/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('/usr/lib/python$opt_pyver/site-packages')\nif '/usr/lib64/python$opt_pyver/site-packages' not in sys.path:     site.addsitedir('/usr/lib64/python$opt_pyver/site-packages')\n" >>$sitecustom
          else
            sitecustom=$PWD/lib/python$opt_pyver/site-packages/sitecustomize.py
            echo "import sys" >$sitecustom
            echo -e "import site\nif '/usr/lib/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('/usr/lib/python$opt_pyver/site-packages')\nif '/usr/lib64/python$opt_pyver/site-packages' not in sys.path:    site.addsitedir('/usr/lib64/python$opt_pyver/site-packages')\n" >>$sitecustom
          fi
        elif [[ -d $PWD/.local/lib/python$opt_pyver/site-packages ]]; then
          sitecustom=$PWD/.local/lib/python$opt_pyver/site-packages/sitecustomize.py
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
    do_deactivate
    pop_cd
    if [[ "$cmd" == "mv" ]]; then
      run_traced "mv $VENV $VENV_TGT"
    fi
  elif [[ $cmd == "inspect" ]]; then
    cd_venv $V -f
    do_activate
    x="vem $V"
    echo "Virtual Environment name: $V"
    echo "Python version: $opt_pyver ($PYTHON)"
    [[ -n $opt_pyver ]] && x="$x -p $opt_pyver"
    [[ -z $opt_pyver && -n $PYTHON ]] && x="$x -p $PYTHON"
    echo "PIP command: $PIP"
    # [[ $opt_dev -ne 0 ]] && echo "Devel packages" && x="$x -D"
    [[ $opt_dev -ne 0 ]] && x="$x -D"
    # [[ -n "$HOME" && $HOME != $SAVED_HOME ]] && echo "Isolated environment" && x="$x -I"
    [[ -n "$HOME" && $HOME != $SAVED_HOME ]] && x="$x -I"
    if [[ -f $V/pyvenv.cfg ]]; then
      ssp=$(grep -E "^include-system-site-packages" $V/pyvenv.cfg|awk -F= '{print $2}'|tr -d " ")
    else
      ssp="false"
    fi
    # [[ $ssp != true ]] && echo "No system site packages" || echo "System site packages"; x="$x -s"
    [[ $ssp != true ]] || x="$x -s"
    echo "Odoo version: $opt_oever"
    [[ -n $opt_oever ]] && x="$x -O $opt_oever"
    echo "Odoo path: $opt_oepath"
    [[ -n $opt_oepath ]] && x="$x -o $opt_oepath"
    echo "Internal sys.path: $PATH"
    echo -e "Environment created with \e[1m$x\e[0m"
    do_deactivate
    pop_cd
  fi
  do_venv_mgr_test $V
}

do_venv_create() {
  # do_venv_create VENV
  [[ $opt_verbose -gt 2 ]] && echo ">>> do_venv_create($@)"
  local f lropts p pkg v VENV xpkgs SAVED_PATH x
  local venvexe pyexe
  VENV="$1"
  venv_mgr_check_src_path "$VENV" "create"
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
      [[ -d ${VENV}~ ]] && run_traced "rm -fR ${VENV}~"
      run_traced "mv $VENV ${VENV}~"
    fi
  fi
  validate_py_oe_vers
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  venvexe=$(which virtualenv 2>/dev/null)
  if [[ -n "$venvexe" ]]; then
    v=$(virtualenv --version 2>&1 | grep -Eo [0-9]+ | head -n1)
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
    for f in ${VENV}~/*; do
      [[ $f =~ (bin|include|lib|node_modules|odoo|package-lock.json|pyvenv.cfg) ]] && continue
      [[ -d $f ]] && run_traced "mv $f/ $VENV/" || "mv $f $VENV/"
    done
  fi
  SAVED_PATH=$PATH
  [[ -d $VENV/bin ]] && export PATH=$VENV/bin:$PATH
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  [[ -x $opt_pyver ]] && opt_pyver=$($opt_pyver--version 2>&1 | grep -Eo "[0-9]\.[0-9]")
  PYTHON=""
  PIP=""
  venv_mgr_check_src_path "$VENV"
  PATH=$SAVED_PATH
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  cd_venv $VENV -f
  do_activate
  x=$($PIP --version|grep -Eo "python [23]"|grep -Eo [23])
  [[ $x == "2" ]] && run_traced "$PIP install \"pip<21.0\" -U" || run_traced "$PIP install pip -U"
  PIPVER=$($PIP --version | grep -Eo [0-9]+ | head -n1)
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
    [[ $opt_dry_run -eq 0 ]] && custom_env $VENV $opt_pyver
  fi
  pip_install_1
  [[ -n "$opt_oever" ]] && pip_install_2
  [[ -n "$opt_rfile" ]] && pip_install_req
  do_deactivate
  [[ -n "$opt_oever" && -d $HOME/$opt_oever ]] && run_traced "ln -s $opt_oepath $($READLINK -f ./odoo)"
  set_python_exe "create" "$VENV"
  pop_cd
  do_venv_mgr_test $VENV
}

do_venv_exec() {
  # do_venv_exec VENV cmd
  local d f mime VENV V sitecustom
  VENV="$1"
  cd_venv $VENV -f
  do_activate
  pop_cd
  run_traced "$2 $3 $4 $5 $6 $7 $8 $9"
  do_deactivate
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
  cd_venv "$VENV" "-f"
  do_activate
  pkg="$(get_actual_pkg $3)"
  [[ $pkg =~ "-e " ]] && pkg=${pkg//-e /--editable=}
  if [[ $cmd == "uninstall" ]]; then
    pip_uninstall "$pkg"
  else
    [[ $opt_alone -ne 0 && ! $pkg =~ ^- ]] && popts="--isolated --disable-pip-version-check --no-cache-dir" || popts="--disable-pip-version-check"
    [[ $PIPVER -gt 18 && ! no-warn-conflicts =~ $popts ]] && popts="$popts --no-warn-conflicts"
    [[ $PIPVER -eq 19 && ! use-feature =~ $popts ]] && popts="$popts --use-feature=2020-resolver"
    [[ $opt_verbose -eq 0 ]] && popts="$popts -q"
    if [[ $cmd =~ (info|show) ]]; then
      pkg=$(get_pkg_wo_version $pkg)
      run_traced "$PIP show $pkg"
      x=$($PIP show $pkg | grep -E ^Location | awk -F: '{print $2}' | sed -e "s| ||")
      [[ -n $x ]] && x=$x/$pkg
      [[ -L $x ]] && echo "Actual location is $($READLINK -e $x)"
    fi
    [[ $cmd == "install" ]] && pip_install "$pkg"
    [[ "$cmd" == "uninstall" ]] && run_traced "$PIP $cmd $pkg"
    [[ $cmd == "update" ]] && pip_install "$pkg" "--upgrade"
  fi
  do_deactivate
  pop_cd
  export PATH=$SAVED_PATH
}

find_odoo_path() {
# find_odoo_path(path opts)
    local p v x
    [[ $opt_verbose -gt 2 ]] && echo ">>> find $2 $1 -maxdepth 3 -type f -not -path "*tmp*" -a -not -path "*old*" -not -path "*/__to_remove/*" -not -path "*/lib/*" -not -path "*/lib64/*" -not -path "*/tests/res/*" -not -path "*/include/*" -not -path "*/.npm/*" -not -path "*/node_modules/*" -not -path "*/.cache/*" -name release.py"
    for f in $(find $2 $1 -maxdepth 3 -type f -not -path "*tmp*" -a -not -path "*old*" -not -path "*/__to_remove/*" -not -path "*/lib/*" -not -path "*/lib64/*" -not -path "*/tests/res/*" -not -path "*/include/*" -not -path "*/.npm/*" -not -path "*/node_modules/*" -not -path "*/.cache/*" -name release.py 2>/dev/null|sort); do
        v=$(grep "^version_info" $f|cut -d= -f2|tr -d "("|tr -d ")"|tr -d " "|awk -F, '{print $1 "." $2}')
        [[ -n "$opt_oever" && $v == $opt_oever ]] && opt_oepath="$($READLINK -e $(dirname $f)/..)" && break
        [[ -z "$opt_oever" ]] && opt_oever="$v" && break
    done
}

validate_py_oe_vers() {
  local odoo_majver
  if [[ -n $opt_oever && -z $opt_pyver ]]; then
    odoo_majver=$(echo $opt_oever|cut -d. -f1)
    [[ $odoo_mahver -le 10 ]] && opt_pyver=2 || opt_pyver=3
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
OPTACTI=(1        "="      "+"       1      1       1         1        2           1         1           "="       "="        "="       0           "="         1                    1          "*>"        "+")
OPTDEFL=(0        ""       0         0      0       0         0        0           0         0           ""        ""         ""        -1          ""          0                    0          ""          -1)
OPTMETA=("help"   "list"   ""        ""     ""      ""        ""       ""          ""        ""          "version" "dir"      "pyver"   ""          "file"      ""                   ""         "version"   "verbose")
OPTHELP=("this help"
  "bin packages to install (* means wkhtmltopdf,lessc)"
  "use unstable packages: testpypi / ~/tools (link) / local devel (copy) / (link)"
  "clear cache before execute pip command"
  "create v.environment with development packages"
  "force v.environment create, even if exists or inside another virtual env"
  "keep python2 executable as python"
  "run pip in an isolated mode, set home virtual directory"
  "run pip in an isolated mode, ignoring environment variables and user configuration"
  "do nothing (dry-run)"
  "install pypi required by odoo ver (amend or create)"
  "odoo path used to search odoo requirements"
  "python version"
  "silent mode"
  "after created v.environment install from the given requirements file"
  "create v.environment with access to the global site-packages"
  "activate environnment for travis test"
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
action=""
p2=""
for x in 3 4 5 6; do
  p="p$x"
  if [[ ${!p} =~ $REXACT ]]; then
    action="${!p}"
    eval $p=""
    [[ $action == "help" ]] && break
  elif [[ -d "${!p}" && -f ${!p}/bin/activate ]]; then
    p2="$($READLINK -e ${!p})"
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
  p2="$($READLINK -e ./)"
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
# If it is running inside travis test environment
[[ -z "$opt_pyver" && -n "$TRAVIS_PYTHON_VERSION" ]] && opt_pyver=$TRAVIS_PYTHON_VERSION
[[ $opt_verbose -eq -1 ]] && opt_verbose=1
[[ $opt_verbose -gt 3 ]] && set -x
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
[[ $opt_alone -ne 0 ]] && PYTHONPATH=""
[[ $opt_debug -eq 2 && -d $HOME/tools && :$PATH: =~ :$HOME/tools: && -n "$PYTHONPATH" ]] && PYTHONPATH=$HOME/tools:$PYTHONPATH
[[ $opt_debug -eq 2 && -d $HOME/tools && :$PATH: =~ :$HOME/tools: && -z "$PYTHONPATH" ]] && PYTHONPATH=$HOME/tools
# [[ $opt_debug -eq 2 && -d $HOME/odoo/tools && :$PATH: =~ :$HOME/odoo/tools: && -n "$PYTHONPATH" ]] && PYTHONPATH=$HOME/odoo/tools:$PYTHONPATH
# [[ $opt_debug -eq 2 && -d $HOME/odoo/tools && :$PATH: =~ :$HOME/odoo/tools: && -z "$PYTHONPATH" ]] && PYTHONPATH=$HOME/odoo/tools
[[ $opt_debug -ge 3 ]] && package_debug
FLAG=">"
[[ $opt_dry_run -eq 0 ]] && FLAG="\$"
if [[ $action == "rm" ]]; then
  [[ $PWD == $($READLINK -f $p2) ]] && cd
  rm -fR $p2
  [[ -n "${BASH-}" || -n "${ZSH_VERSION-}" ]] && hash -r 2>/dev/null
  unset PYTHON PIP
  exit 0
elif [[ ! $action =~ (help|create) ]]; then
  cd_venv $p2 "-q"
  do_activate "-q"
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
if [[ $action =~ (help|create) || $opt_dev -eq 0 || -z "$FUTURE" || -z "$CONFIGPARSER" || -z "$Z0LIB" || -z "$OS0" || -z $(which list_requirements.py 2>/dev/null) ]]; then
  DEV_PKGS=""
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
do_deactivate "-q"
pop_cd "-q"
if [ "$action" == "help" ]; then
  man $TDIR/$THIS.man
elif [ "$action" == "exec" ]; then
  do_venv_exec "$p2" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
elif [ "$action" == "python" ]; then
  do_venv_exec "$p2" "python" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
elif [ "$action" == "shell" ]; then
  do_venv_exec "$p2" "$SHELL" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
elif [[ $action =~ (info|install|show|uninstall|update) ]]; then
  [[ $opt_cc -ne 0 && -d $HOME/.cache/pip ]] && run_traced "rm -fR $HOME/.cache/pip"
  do_venv_pip "$p2" "$action" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9"
elif [ "$action" == "create" ]; then
  [[ $opt_cc -ne 0 && -d $HOME/.cache/pip ]] && run_traced "rm -fR $HOME/.cache/pip"
  do_venv_create "$p2" "$p3" "$p4" "$p5" "$p6"
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
  [[ $FH = "RHEL" ]] && XTAL="yum" || XTAL="apt"
  [[ $DISTO == "Fedora" ]] && XTAL="dnf"
  echo "Perhaps you should install ..."
  [[ $FH = "RHEL" ]] && PKGLIST="python-devel" || PKGLIST="python-dev"
  [[ $DISTO == "Fedora" ]] && PKGLIST=""
  [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST python3-devel" || PKGLIST="$PKGLIST python3-dev"
  [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST python3-pip" || PKGLIST="$PKGLIST python3-pip"
  [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST python3-venv" || PKGLIST="$PKGLIST python3-venv"
  [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST libsass-devel"
  [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST zlib-devel" || PKGLIST="$PKGLIST zlib1g-dev"
  echo "$XTAL install $PKGLIST"
  if [[ $ERROR_PKGS =~ lxml ]]; then
    PKGLIST=""
    [[ $DISTO == "Fedora" ]] && PKGLIST="redhat-rpm-config"
    [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST libxml2-devel" || PKGLIST="$PKGLIST libxml2-dev"
    [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST libxslt-devel" || PKGLIST="$PKGLIST libxslt-dev"
    echo "$XTAL install $PKGLIST    # lxml"
  fi
  if [[ $ERROR_PKGS =~ ldap ]]; then
    PKGLIST=""
    [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST openldap-devel" || PKGLIST="$PKGLIST libsasl2-dev libldap2-dev libssl-dev"
    echo "$XTAL install $PKGLIST    # ldap"
  fi
  if [[ $ERROR_PKGS =~ gevent ]]; then
    PKGLIST=""
    [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST libevent-devel" || PKGLIST="$PKGLIST libevent-dev"
    echo "$XTAL install $PKGLIST    # gevent"
  fi
  if [[ $ERROR_PKGS =~ pycups ]]; then
    PKGLIST=""
    [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST libcups2-devel" || PKGLIST="$PKGLIST libcups2-dev"
    echo "$XTAL install $PKGLIST    # pycups"
  fi
  if [[ $ERROR_PKGS =~ shapely ]]; then
    PKGLIST=""
    [[ $FH = "RHEL" ]] && PKGLIST="$PKGLIST geos-devel" || PKGLIST="$PKGLIST libgeos-dev"
    echo "$XTAL install $PKGLIST    # shapely"
  fi
fi
unset PYTHON PIP
exit 0
