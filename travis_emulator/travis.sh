#! /bin/bash
# -*- coding: utf-8 -*-
#
# Travis-ci emulator
# Emulate travis-ci on local machine, to test before upgrade git project
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
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
  exit 2
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=$ODOOLIBDIR"
TRAVISLIBDIR=$(findpkg travisrc "$PYPATH" "travis_emulator")
if [ -z "$TRAVISLIBDIR" ]; then
  echo "Library file travisrc not found!"
  exit 2
fi
. $TRAVISLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TRAVISLIBDIR=$TRAVISLIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$($READLINK -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"

__version__=1.0.2.99

store_cfg_param_value() {
  #store_cfg_param_value(tid key value [opt] [section])
  local p
  if [[ $2 =~ ^pip_pkgver__ ]]; then
    if [ -z "$PIPPKGVER" ]; then
      declare -gA PIPPKGVER
    fi
    p=${2:12}
    PIPPKGVER[$p]=$3
  fi
  a_add "$1" "$2" "$3" "$4"
}

process_yaml_init() {
  local u
  YML_sect=
  YML_sect0=
  YML_env=
  YML_global=
  YML_matrix=
  YML_packages=
  YML_install=
  YML_before_script=
  YML_script=
  YML_after=
  YML_pid=$$
  if [[ "$REMOTEREPO" == "oca" ]]; then
    YML_repo=OCA/OCB
  elif [[ "$REMOTEREPO" == "odoo" ]]; then
    YML_repo=odoo/odoo
  else
    YML_repo=
  fi
  export TRAVIS_PULL_REQUEST="false"
  export MQT_TEMPLATE_DB="$(get_cfg_value "" "MQT_TEMPLATE_DB")$YML_pid"
  export MQT_TEST_DB="$(get_cfg_value "" "MQT_TEST_DB")$YML_pid"
  export PGUSER="$(get_cfg_value "" "MQT_DBUSER")"
  [[ -z $PGUSER ]] && export PGUSER=$(get_dbuser)
  python_ver_req=""
  python_ver_ena=""
  [[ -f $PRJPATH/travis.ini ]] && python_ver_ena=$(cat $PRJPATH/travis.ini|grep PYPI_RUN_PYVER|awk -F= '{print $2}'|grep -Eo "[0-9.]+"|head -n1)
  if [ $opt_dbgmnt -ne 0 ]; then
    [[ -d $HOME/devel ]] && \
      export YML_lisa=$HOME/pypi/lisa/lisa/lisa || \
      export YML_lisa=$HOME/dev/pypi/lisa/lisa/lisa
    [[ -d $HOME/devel ]] && \
      export YML_mgrodoo=$HOME/pypi/clodoo/clodoo/manage_odoo || \
      export YML_mgrodoo=$HOME/dev/pypi/clodoo/clodoo/manage_odoo
    (($opt_debug)) && export TRAVIS_PDB="true"
  else
    export YML_lisa=lisa
    export YML_mgrodoo=manage_odoo
  fi
  export TRAVIS_DEBUG_MODE="${opt_dlvl:-1}"
  [[ $TRAVIS_DEBUG_MODE -gt 1 ]] && export VERBOSE_MODE=$TRAVIS_DEBUG_MODE
  [[ $osx_d -ne 0 ]] && export TRAVIS_EMULATE_OSX="true"
  ODOO_TNLBOT="${opt_tnl:-0}"
  if [ $opt_full -ne 0 ]; then
    export SYSTEM_SITE_PACKAGES="${opt_syspkg:-false}"
  else
    export SYSTEM_SITE_PACKAGES="${opt_syspkg:-true}"
  fi
  LINT_CHECK_LEVEL="${opt_llvl^^}"
  for i in {1..9}; do
    declare YML_CMD_DIS_$i=$(get_cfg_value "" "yaml__cmd_dis__$i")
  done
  FH=$(xuname -f)
}

process_yaml_unquote() {
  lne="$(echo $1 | sed -e s/\"/%%22/g -e s/\'/%%26/g -e s/\ /%%20/g)"
  echo $lne
}

process_yaml_quote() {
  lne="$(echo $1 | sed -e s/%%22/\"/g -e s/%%26/\'/g -e s/%%20/\ /g -e s/%%24/\$/g)"
  echo $lne
}

process_yaml_quote_xtl() {
  lne="$(echo $1 | sed -e s/%%22/\"/g -e s/%%26/\'/g -e s/%%20/\ /g -e s/%%24/\$/g)"
  lne=$(expand_path "$lne")
  echo $lne
}

process_yaml_do() {
  local a b i lne
  if [[ ${1:0:1} == " " ]]; then
    local line="${1:1}"
  else
    local line="$1"
  fi
  if [[ $line =~ LINT_CHECK=... ]]; then
    if [[ $action =~ ^(force-lint|lint)$ ]]; then
      line=$(echo "$line" | sed -e s/LINT_CHECK=[\"']0[\"']/LINT_CHECK=\"1\"/g)
    elif [[ $action != "emulate" ]]; then
      line=$(echo "$line" | sed -e s/LINT_CHECK=[\"']1[\"']/LINT_CHECK=\"0\"/g)
    fi
  elif [[ $line =~ BASH_CHECK=... ]]; then
    if [[ $action =~ ^(force-lint|lint)$ ]]; then
      line=$(echo "$line" | sed -e s/BASH_CHECK=[\"']0[\"']/BASH_CHECK=\"1\"/g)
    elif [[ $action != "emulate" ]]; then
      line=$(echo "$line" | sed -e s/BASH_CHECK=[\"']1[\"']/BASH_CHECK=\"0\"/g)
    fi
  elif [[ $line =~ TESTS=... ]]; then
    if [[ $action =~ ^(force-test|test)$ ]]; then
      line=$(echo "$line" | sed -e s/TESTS=[\"']0[\"']/TESTS=\"1\"/g)
    elif [[ $action != "emulate" ]]; then
      line=$(echo "$line" | sed -e s/TESTS=[\"']1[\"']/TESTS=\"0\"/g)
    fi
  elif [[ $line =~ TEST_DEPENDENCIES=... ]]; then
    if [[ $action =~ ^(force-testdeps|testdeps)$ ]]; then
      line=$(echo "$line" | sed -e s/TEST_DEPENDENCIES=[\"']0[\"']/TEST_DEPENDENCIES=\"1\"/g)
    elif [[ $action != "emulate" ]]; then
      line=$(echo "$line" | sed -e s/TEST_DEPENDENCIES=[\"']1[\"']/TEST_DEPENDENCIES=\"0\"/g)
    fi
  elif [[ $line =~ ODOO_TNLBOT=... ]]; then
    if [[ $action =~ ^(force-translate|translate)$ ]]; then
      line=$(echo "$line" | sed -e s/ODOO_TNLBOT=[\"']0[\"']/ODOO_TNLBOT=\"1\"/g)
    elif [[ $action != "emulate" ]]; then
      line=$(echo "$line" | sed -e s/ODOO_TNLBOT=[\"']1[\"']/ODOO_TNLBOT=\"0\"/g)
    fi
  fi
  if [[ $line =~ TRAVIS_DEBUG_MODE= && -n "$opt_dlvl" ]]; then
    line=$(echo "$line" | sed -e "s/TRAVIS_DEBUG_MODE=[0-9\"']\+/TRAVIS_DEBUG_MODE=\"$opt_dlvl\"/")
  fi
  if [[ $line =~ ODOO_TNLBOT= ]] && [ -n "$opt_tnl" ]; then
    line=$(echo "$line" | sed -e "s/ODOO_TNLBOT=[A-Za-z0-9_\"']\+/ODOO_TNLBOT=\"$opt_tnl\"/")
  fi
  if [[ $line =~ LINT_CHECK_LEVEL= ]] && [ -n "$opt_llvl" ]; then
    line=$(echo "$line" | sed -e "s/LINT_CHECK_LEVEL=[A-Za-z0-9_\"']\+/LINT_CHECK_LEVEL=\"${opt_llvl^^}\"/")
  fi
  if [[ "${line:0:1}" == "(" && "${line: -1}" == ")" ]]; then
    lne=$(process_yaml_unquote "${line:1:-1}")
  elif [[ "${line:0:1}" == "\"" && "${line: -1}" == "\"" ]]; then
    line=${line//\\\"/\"}
    lne=$(process_yaml_unquote "${line:1:-1}")
  else
    lne=$(process_yaml_unquote "$line")
  fi
  if [[ $YML_sect == "python" ]]; then
    [[ -z $python_ver_ena || $lne == $python_ver_ena ]] && python_ver_req="$python_ver_req $lne"
    lne="#"
  elif [[ $YML_sect == "addons.apt.packages" ]]; then
    YML_packages="$YML_packages $lne"
  elif [[ $YML_sect == "env" ]]; then
    YML_env="$YML_env $lne"
  elif [[ $YML_sect == "env.global" ]]; then
    if [[ ${lne:0:7} == "secure:" ]]; then
      lne="# $lne"
    else
      YML_global="$YML_global $lne"
      [[ $line =~ TRAVIS_DEBUG_MODE= ]] && eval $(process_yaml_quote $lne)
    fi
  elif [[ $YML_sect == "env.matrix" ]]; then
    YML_matrix="$YML_matrix $lne"
    if [[ $line =~ ODOO_REPO=.?$REMOTEREPO/ ]]; then
      [[ $REMOTEREPO == "odoo" ]] && YML_repo=$REMOTEREPO/odoo || YML_repo=$REMOTEREPO/OCB
    elif [[ $line =~ ODOO_REPO=.?odoo/odoo && -z "$YML_repo" ]]; then
      YML_repo=odoo/odoo
    elif [[ $line =~ ODOO_REPO=.?OCA/OCB && -z "$YML_repo" ]]; then
      YML_repo=OCA/OCB
    elif [[ $line =~ ODOO_REPO=.?zeroincombenze/OCB && $REMOTEREPO == "local" ]]; then
      YML_repo=zeroincombenze/OCB
    fi
  elif [[ $YML_sect == "before_install" ]]; then
    YML_before_install="$YML_before_install $lne"
  elif [[ $YML_sect == "install" ]]; then
    YML_install="$YML_install $lne"
  elif [[ $YML_sect == "before_script" ]]; then
    YML_before_script="$YML_before_script $lne"
  elif [[ $YML_sect == "script" ]]; then
    YML_script="$YML_script $lne"
  elif [[ $YML_sect == "after_success" ]]; then
    YML_after="$YML_after $lne"
  else
    lne="$(echo $1)"
  fi
}

process_yaml_0() {
  if [ -n "$lne" ]; then
    IFS=- read a b <<<"$lne"
    if [ -n "$a" ]; then
      IFS=: read a b <<<"$lne"
      if [ -z "$b" ]; then
        YML_sect0=$a
        YML_sect="$YML_sect0"
      else
        YML_sect0=
        YML_sect=
        declare YML_$a="$(echo $b)"
      fi
    else
      process_yaml_do "$b"
    fi
  fi
}

process_yaml_1() {
  local val
  if [ -n "$lne" ]; then
    IFS=- read a b <<<"$lne"
    if [ -n "$a" ]; then
      IFS=: read a b <<<"$lne"
      if [ -z "$b" ]; then
        YML_sect1=$a
        YML_sect="$YML_sect0.$YML_sect1"
      else
        if [[ "${YML_sect0}__$a" == "virtualenv__system_site_packages" ]]; then
          [[ -z "$opt_syspkg" ]] && export SYSTEM_SITE_PACKAGES=$(echo $b)
          [[ "$SYSTEM_SITE_PACKAGES" == "true" ]] && TRAVIS_ENVOPTS="$TRAVIS_ENVOPTS --system-site-packages"
        else
          YML_sect1=
          YML_sect="$YML_sect0"
          declare ${YML_sect0}__$a="$(echo $b)"
        fi
      fi
    else
      process_yaml_do "$b"
    fi
  fi
}

process_yaml_2() {
  if [ -n "$lne" ]; then
    IFS=- read a b <<<"$lne"
    if [ -n "$a" ]; then
      IFS=: read a b <<<"$lne"
      if [ -z "$b" ]; then
        YML_sect2=$a
        YML_sect="$YML_sect0.$YML_sect1.$YML_sect2"
      else
        YML_sect2=
        YML_sect="$YML_sect0.$$YML_sect1"
        declare ${YML_sect0}__${YML_sect1}__$a="$(echo $b)"
      fi
    else
      process_yaml_do "$b"
    fi
  fi
}

process_yaml_3() {
  if [ -n "$lne" ]; then
    IFS=- read a b <<<"$lne"
    if [ -z "$a" ]; then
      process_yaml_do "$b"
    fi
  fi
}

process_yaml_file() {
  local YML_FILE=$1
  process_yaml_init
  local lev=0
  local ident=0
  local line=
  local lne=
  local line1=
  local lne1=
  local linex=
  local a b i r
  while IFS="#" read -r line r || [ -n "$line" ]; do
    if [ -n "$line" -a "${line: -1}" != " " -a -n "$r" ]; then
      line="$line#$r"
      r=
    fi
    if [[ $line =~ ^[[:space:]]+ ]]; then
      for i in {0..10}; do if [ "${line:i:1}" != " " ]; then break; fi; done
      if [ $i -gt $ident ]; then
        ((lev++))
        ident=$i
      elif [ $i -lt $ident ]; then
        ((lev--))
        ident=$i
      fi
    else
      lev=0
      ident=0
    fi
    lne=$(echo ${line//$/%%24})
    if [ $lev -eq 0 ]; then
      process_yaml_0
    elif [ $lev -eq 1 ]; then
      process_yaml_1
    elif [ $lev -eq 2 ]; then
      process_yaml_2
    elif [ $lev -eq 3 ]; then
      process_yaml_3
    fi
  done <"$YML_FILE"
}

process_yaml_initialize() {
  local sts=$STS_SUCCESS
  local i s line lne X
  wlog "\e[${PS_HDR2_COLOR}m===== [Initialize] =====\e[0m"
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[initialize] from .travis.conf] ------\e[0m"
  fi
  line=$(get_cfg_value "" "GBL_EXCLUDE")
  [[ -n "$line" ]] && run_traced "export GBL_EXCLUDE=$line"
  for i in {1..9}; do
    line=$(get_cfg_value "" "yaml_init_$i")
    if [ -n "$line" ]; then
      process_yaml_run_cmd "$line"
        s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    fi
  done
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[initialize.packages] from .travis.conf] ------\e[0m"
  fi
  X="${PKGNAME}__"
  line=$(get_cfg_value "" "${X}yaml_init_1")
  if [ -n "$line" ]; then
    for i in {1..9}; do
      line=$(get_cfg_value "" "${X}yaml_init_$i")
      if [ -n "$line" ]; then
        process_yaml_run_cmd "$line"
        s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
      fi
    done
  fi
  return $sts
}

process_yaml_exit() {
  local sts=$STS_SUCCESS
  local i line lne X
  wlog "\e[${PS_HDR2_COLOR}m===== [Ending] =====\e[0m"
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[exit.packages] from .travis.conf] ------\e[0m"
  fi
  X="${PKGNAME}__"
  line=$(get_cfg_value "" "${X}yaml_exit_1")
  if [ -n "$line" ]; then
    for i in {1..9}; do
      line=$(get_cfg_value "" "${X}yaml_exit_$i")
      if [ -n "$line" ]; then
        process_yaml_run_cmd "$line"
      fi
    done
  fi
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[exit] from .travis.conf] ------\e[0m"
  fi
  for i in {1..9}; do
    line=$(get_cfg_value "" "yaml_exit_$i")
    if [ -n "$line" ]; then
      process_yaml_run_cmd "$line"
    fi
  done
  return $sts
}

process_yaml_global() {
  [[ $PWD != $TRAVIS_BUILD_DIR ]] && run_traced "cd $TRAVIS_BUILD_DIR"
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[env.global] in .travis.yml] ------\e[0m"
  fi
  for lne in $YML_global; do
    line="export $(process_yaml_quote_xtl $lne)"
    run_traced "$line"
    s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
  done
  return $sts
}

process_yaml_before_install() {
  wlog "\e[${PS_HDR2_COLOR}m===== [Before install] =====\e[0m"
  local sts=$STS_SUCCESS
  local i s line lne X CURPYVER
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[addons.packages] in .travis.yml] ------\e[0m"
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    CURPYVER=$(echo $TRAVIS_PYTHON_VERSION | grep -Eo [0-9] | head -n1)
    for lne in $YML_packages; do
      if [[ "$lne" == "python-dev" && $CURPYVER == "3" ]]; then
        [[ "$FH" == "RHEL" ]] && lne="python3-devel" || lne="python3-dev"
      elif [ "$FH" == "RHEL" ]; then
        if [[ "$lne" == "build-essential" ]]; then
          lne="redhat-rpm-config"
        elif [[ $lne =~ (python-dev|python3-dev) ]]; then
          lne="python3-devel"
        elif [[ "$lne" == "libxml2-dev" ]]; then
          lne="libxml2-devel"
        elif [[ "$lne" == "libxslt1-dev" ]]; then
          lne="libxslt-devel"
        elif [[ "$lne" == "zlib1g" ]]; then
          lne="zlib"
        elif [[ "$lne" == "zlib1g-dev" ]]; then
          lne="zlib-devel"
        elif [[ "$lne" == "libffi-dev" ]]; then
          lne="libffi-devel"
        elif [[ "$lne" == "libssl-dev" ]]; then
          lne="openssl-devel"
        elif [[ "$lne" == "libevent-dev" ]]; then
          lne="libevent-devel"
        fi
        line="yum install $lne"
      else
        line="apt-get install $lne"
      fi
      process_yaml_run_cmd "$line"
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
      [ $s -ne 0 ] && echo "Internal error! Statement failed! <<<"
    done
  fi
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[before_install] in .travis.yml] ------\e[0m"
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    for lne in $YML_before_install; do
      [[ $TRAVIS_DEBUG_MODE -ge 3 ]] && echo "#> $(process_yaml_quote_xtl $lne)"
      process_yaml_run_cmd "$lne"
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
      [ $s -ne 0 ] && echo "Internal error! Statement failed! <<<"
    done
  fi
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[env] in .travis.yml] ------\e[0m"
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    for lne in $YML_env; do
      line="export $(process_yaml_quote_xtl $lne)"
      run_traced "$line"
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    done
  fi
  return $sts
}

process_yaml_install() {
  # process_yaml_install(init)
  local sts=$STS_SUCCESS
  local i s line line1 lne
  [ -n "$1" ] && line1="export $(process_yaml_quote_xtl $1)"
  wlog "\e[${PS_HDR2_COLOR}m===== [Install $line1] =====\e[0m"
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[install] in .travis.yml] ------\e[0m"
  fi
  run_traced "$line1"
  for lne in $YML_install; do
    process_yaml_run_cmd "$lne"
    s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
  done
  return $sts
}

process_yaml_before_script() {
  # process_yaml_before_script(init)
  local sts=$STS_SUCCESS
  local line1 lne
  line1=$(process_yaml_quote $1)
  wlog "\e[${PS_HDR2_COLOR}m===== [Before script $line1] =====\e[0m"
  if [[ -z "$line1" || "${line1:0:1}" == "#" ]]; then
    sts=127
  else
    for lne in $YML_before_script; do
      process_yaml_run_cmd "$lne" "$line1"
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    done
  fi
  return $sts
}

process_yaml_after_success() {
  local sts=$STS_SUCCESS
  local i
  local s
  local line
  local line1
  local lne
  for lne in $YML_after; do
    line=$(process_yaml_quote_xtl $lne)
    process_yaml_run_cmd "$line"
    s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
  done
  return $sts
}

process_yaml_run_cmd() {
  #process_yaml_run_cmd (cmd init)
  local xcmd=$(process_yaml_quote_xtl "$1")
  local ix ix1 ix2 c i x s opts p pp tk z sts xtlcmd
  local xlint xtest xtfex xpkg xcd
  if [[ -n "$2" ]]; then
    local line1="$(process_yaml_quote_xtl $2) "
  else
    local line1
  fi
  c=$xcmd
  if [ "$FH" == "RHEL" ]; then
    if [[ $xcmd =~ which[[:space:]]nodejs ]]; then
      xcmd=$(echo "$xcmd" | sed -e s/nodejs/node/g)
    fi
  fi
  read -r -a x <<<"$xcmd"
  ix=0
  if [ ${opt_virt:-0} -eq 0 -a "${x[$ix]}" == "sudo" ]; then
    xcmd="$(echo $xcmd | sed -e 's/sudo //g')"
    ((ix++))
  fi
  if [ ${opt_virt:-0} -eq 0 -a "${x[$ix]}" == "if" ]; then
    ((ix++))
    while [ -n "${x[$ix]}" ]; do
      if [ "${x[$ix]}" == "then" ]; then break; fi
      ((ix++))
    done
    ((ix++))
  fi
  ix1=$ix
  ((ix1++))
  ix2=$ix1
  ((ix2++))
  ix3=$ix2
  ((ix3++))
  if [ "$FH" == "Debian" -a "${x[$ix]}" == "yum" ]; then
    xcmd="$(echo $xcmd | sed -e 's/yum /apt-get /g')"
    x[$ix]="apt-get"
  elif [ "$FH" == "RHEL" -a "${x[$ix]}" == "apt-get" ]; then
    xcmd="$(echo $xcmd | sed -e 's/apt-get /yum /g')"
    x[$ix]="yum"
  fi
  if [[ ${x[$ix]} =~ ^(yum|apt-get)$ ]]; then
    pp="(python-serial|libcups2-dev|cups-devel|unixodbc|unixODBC|unixodbc-dev|unixODBC-dev|unixODBC-devel"
    pp="$pp|python-mysqldb|MYSQL-python|python-yaml|pyyaml|pyYAML|PyYAML|python-pypdf|pypdf|pyPdf"
    pp="$pp|ruby-sass|rubygem-sass|python-simplejson|python2-simplejson|expect-dev|antiword)"
    if [[ ${x[$ix2]} =~ $pp ]]; then
      xcmd=$(echo $xcmd | sed -e 's/yum/$YML_lisa/g')
      xcmd=$(echo $xcmd | sed -e 's/apt-get/$YML_lisa/g')
      x[$ix]=$YML_lisa
    fi
  fi
  if [ "${x[$ix]}" == "$YML_lisa" -a "${x[$ix1]}" == "install" ]; then
    if $($YML_lisa status ${x[$ix2]} &>/dev/null); then
      xcmd="# $xcmd"
    elif [[ ${x[$ix2]} =~ (expect|expect-dev|expect-devel|python-dev) ]]; then
      xcmd="true;   # Warning! TODO> $xcmd"
    else
      xcmd="false;  # Error! TODO> $xcmd"
    fi
  elif [ "${x[$ix]}" == "yum" -a "${x[$ix1]}" == "install" ]; then
    if $(rpm -q ${x[$ix2]} &>/dev/null); then
      xcmd="# $xcmd"
    elif $(yum info ${x[$ix2]} &>/dev/null); then
      xcmd="# $xcmd"
    elif [[ ${x[$ix2]} =~ (expect|expect-dev|expect-devel|python-dev) ]]; then
      xcmd="true;   # Warning! TODO# $xcmd"
    else
      xcmd="false;  # Error! TODO# $xcmd"
    fi
  elif [ "${x[$ix]}" == "apt-get" -a "${x[$ix1]}" == "install" ]; then
    if $(dpkg-query -s ${x[$ix2]} &>/dev/null); then
      xcmd="# $xcmd"
    elif [[ ${x[$ix2]} =~ (expect|expect-dev|expect-devel|python-dev) ]]; then
      xcmd="true;   # Warning! TODO> $xcmd"
    else
      xcmd="false;  # Error! TODO> $xcmd"
    fi
  elif [ "${x[$ix]}" == "git" -a "${x[$ix1]}" == "clone" ]; then
    ix=$ix2
    tk=${x[$ix]}
    while [ "${tk:0:1}" == "-" ]; do
      ((ix++))
      tk=${x[$ix]}
    done
    if [[ "$TRAVIS" != "true" && "${x[$ix]}" == "https://github.com/zeroincombenze/tools.git" ]]; then
      xcmd="$(echo $xcmd | sed -e 's/git clone/git_clone/g')"
    fi
  elif [ "${x[$ix]}" == "pip" -a "${x[$ix1]}" == "install" ]; then
    if [ ${opt_virt:-0} -eq 0 ]; then
      ix=$ix2
      tk=${x[$ix]}
      xcmd="# ${x[$ix]} ${x[$ix1]}"
      while [ -n "${x[$ix]}" ]; do
        if [ "${x[$ix]}" == "-r" -o "${x[$ix]}" == "--requirement" ]; then
          ((ix++))
          pp=${x[$ix]}
          xcmd="$xcmd -r $pp"
          while IFS="#" read -r tk r || [ -n "$tk" ]; do
            if [ -n "$tk" ]; then
              if [ "${tk:0:4}" == "http" ]; then
                p=$(basename $tk)
                tk=$(echo $p | grep -Eo '[a-zA-Z0-9_]*' | head -n1)
              fi
              p=$(echo "$tk" | grep -Eo '[^!<=>;\[]*' | head -n1)
              p=${p//\"/}
              p=$(echo $p)
              if [ "$p" == "transifex-client" ]; then
                xcmd="$xcmd $p"
              elif $(pip show $p &>/dev/null); then
                xcmd="$xcmd $p"
              else
                xcmd="false; $xcmd <$p>"
              fi
            fi
          done <$pp
        elif [ "${tk:0:1}" != "-" ]; then
          p=$(echo "${x[$ix]}" | grep -Eo '[^!<=>;]*' | head -n1)
          p=${p//\"/}
          if $(pip show $p &>/dev/null); then
            xcmd="$xcmd $p"
          else
            xcmd="false; $xcmd <$p>"
          fi
          if [ "${tk: -1}" == ";" ]; then break; fi
        else
          xcmd="$xcmd $p"
        fi
        ((ix++))
        tk=${x[$ix]}
      done
    elif [[ ! "$SYSTEM_SITE_PACKAGES" == "true" ]]; then
      if ! $(echo $xcmd | grep -q "\--user"); then
        xcmd=${xcmd/pip install/pip install --user --no-warn-conflicts}
      fi
    else
      if ! $(echo $xcmd | grep -q "\--no-warn-conflicts"); then
        xcmd=${xcmd/pip install/pip install --no-warn-conflicts}
      fi
    fi
  elif [ "${x[$ix]}" == "mv" -a "${x[$ix1]}" == "${HOME}/tools/maintainer-quality-tools" ]; then
    xcmd=${xcmd/cp/mv}
  elif [ "${x[$ix]}" == "rvm" -a "${x[$ix1]}" == "install" ]; then
    xcmd="# $xcmd"
  elif [ ${opt_virt:-0} -eq 0 -a "${x[$ix]}" == "ln" -a "${x[$ix1]}" == "-s" -a "${x[$ix2]:0:16}" == "/opt/odoo/build/" ]; then
    xcmd="# $xcmd"
  elif [ "${x[$ix]}" == "sh" -a "${x[$ix2]}" == "/etc/init.d/xvfb" ]; then
    xcmd="# $xcmd"
  else
    if [ -z "$REPOSNAME" ]; then
      pp=$PKGPATH
    else
      pp=$($READLINK -e $PRJPATH/../$REPOSNAME/)
    fi
    while [ -n "${x[$ix]}" ]; do
      if [[ "${x[$ix]}" =~ cd ]]; then
        xcd=1
      elif [[ "${x[$ix]}" =~ LINT_CHECK=.1. ]]; then
        xlint=1
      elif [[ "${x[$ix]}" =~ LINT_CHECK=.0. ]]; then
        xlint=0
      elif [[ "${x[$ix]}" =~ TRANSIFEX=.1. ]]; then
        xcmd="# $xcmd"
      elif [[ "${x[$ix]}" =~ TESTS=.1. ]]; then
        xtest=1
      elif [[ "${x[$ix]}" =~ MQT_TEMPLATE_DB= ]]; then
        xcmd=$(echo $xcmd | sed -e "s|${x[$ix]}|${x[$ix]}$YML_pid|g")
      elif [[ "${x[$ix]}" =~ MQT_TEST_DB= ]]; then
        xcmd=$(echo $xcmd | sed -e "s|${x[$ix]}|${x[$ix]}$YML_pid|g")
      elif [ "${x[$ix]}" == "\${OPTS}" ]; then
        xcmd="$(echo $xcmd | sed -e 's|${OPTS}|'$OPTS'|g')"
        x[$ix]=$OPTS
      else
        for xpkg in travis_install_nightly travis_after_tests_success; do
          if [[ "${x[$ix]}" == "$xpkg" ]]; then
            xtlcmd="$xpkg"
            if [ "$xlint" != "1" -o "$xtest" == "1" ] && [ "$xcd" != "1" -a $opt_force -eq 0 ]; then
              if [ ${opt_virt:-0} -eq 0 ]; then
                xtlcmd=$(get_cfg_value "" "EM_$xpkg")
              else
                xtlcmd=$(get_cfg_value "" "RUN_$xpkg")
              fi
              if [ -n "$xtlcmd" ]; then
                xtlcmd=$(process_yaml_unquote "$xtlcmd")
                xcmd="$(echo $xcmd | sed -e 's|'$xpkg'|'$xtlcmd'|g')"
                xcmd=$(process_yaml_quote "$xcmd")
              elif [ -z "${x[$ix]}" ] && [[ "$xtlcmd" =~ \$\{ ]]; then
                xcmd=$(process_yaml_quote "$xcmd")
                xcmd="# $xcmd"
              fi
            fi
          fi
        done
      fi
      ((ix++))
    done
  fi
  sts=0
  if [[ $action == "parseyaml" ]]; then
    [[ $c != $xcmd && ! $xcmd =~ ^# ]] && echo "\e[${PS_NOP_COLOR}m## $c\e[${PS_TXT_COLOR}m"
    echo "$xcmd"
    s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
  else
    [[ $c != $xcmd && ! $xcmd =~ ^# ]] && wlog "\e[${PS_NOP_COLOR}m> $c\e[${PS_TXT_COLOR}m" && ((Z0_STACK=Z0_STACK+2))
    run_traced "$line1$xcmd"
    s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    if [[ $xcmd =~ "travis_install_env" ]]; then
      ((Z0_STACK=Z0_STACK+2))
      opts=$(inherits_travis_opts "" "V")
      [[ $TRAVIS == "true" ]] || opts="$opts -f"
      [ $opt_keepE -eq 0 ] || run_traced "vem create $VENVOPTS $TRAVIS_HOME $opts -p$TRAVIS_PYTHON_VERSION"
      ((Z0_STACK=Z0_STACK-2))
    fi
    [[ $c != $xcmd && ! $xcmd =~ ^# ]] && ((Z0_STACK=Z0_STACK-2))
  fi
  return $sts
}

process_yaml() {
  # process_yaml ()
  local sts=$STS_SUCCESS
  local i s p v X
  local line lne line1 lne1
  load_colors
  if [[ $action == "chkconfig" ]]; then
    YML_FILE=$TOOLS_PATH/chkconfig.yml
    if [ ! -f $YML_FILE ]; then
      do_chkconfig
      return $STS_SUCCESS
    fi
  else
    YML_FILE=$opt_fyaml
    [[ ! -f $YML_FILE ]] && YML_FILE=$PRJPATH/$opt_fyaml
    [[ ! -f $YML_FILE ]] && YML_FILE=$TOOLS_PATH/travis.yml
  fi
  if [[ -f $YML_FILE ]]; then
    echo -e "\e[0;30;107m$(printf '%-80.80s' ' ')\e[0m"
    wlog "\e[${PS_HDR1_COLOR}m$(printf '%-80.80s' '=== Process YAML file ===')\e[0m"
    export TRAVIS_HOME_BRANCH=$PWD
    process_yaml_file "$YML_FILE"
    unset PYTHONPATH
    sts=$STS_SUCCESS
    wlog "\e[${PS_HDR2_COLOR}m===== [System informations] =====\e[0m"
    TODAY=$(date "+%Y-%m-%d %H:%M:%S")
    for lne in TODAY job-id __version__ TCONF YML_FILE YML_lisa YML_mgrodoo YML_repo BRANCH DIST LOGFILE PGUSER MQT_TEMPLATE_DB MQT_TEST_DB PRJNAME PKGNAME REPOSNAME PRJPATH PKGPATH PATH TOOLS_PATH TRAVIS TRAVIS_EMULATE_OSX TRAVIS_HOME_BRANCH TRAVIS_REPO_SLUG TRAVIS_PDB; do
      if [[ $lne == "job-id" ]]; then
        lne1=$$
      elif [[ $lne == "DIST" ]]; then
        lne1=$(xuname -a)
      elif [[ $lne == "__version__" ]]; then
        lne1=$__version__
      else
        lne1=${!lne}
      fi
      [[ -n "$lne1" || $lne =~ PATH ]] && wlog "\e[${PS_NOP_COLOR}m\$ $lne=$lne1\e[0m"
    done
    if [[ $sts -eq $STS_SUCCESS ]]; then
      process_yaml_initialize
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    fi
    if [[ $sts -eq $STS_SUCCESS ]]; then
      [[ -z "$python_ver_req" ]] && python_ver_req=$(python --version 2>&1 | grep -Eo "[0-9]+\.[0-9]+")
      [[ -z "$opt_pyv" ]] && opt_pyv=$(get_cfg_value "" "PYTHON_MATRIX")
      [[ -z "$opt_pyv" ]] && opt_pyv="(2.7|3.5|3.6|3.7|3.8)"
      opt_pyv="${opt_pyv//,/|}"
      opt_pyv="${opt_pyv// /|}"
      [[ $opt_pyv =~ ^\( ]] || opt_pyv="($opt_pyv)"
      python_matrix=""
      for v in $python_ver_req; do
        [[ $v =~ $opt_pyv ]] && python_matrix="$python_matrix $v"
      done
      [[ -z $python_matrix && $opt_pyv =~ ^\([0-9.]+\) ]] && python_matrix=${opt_pyv:1: -1}
      [[ -n "$python_matrix" ]] || python_matrix="3.8"
      for TRAVIS_PYTHON_VERSION in $python_matrix; do
        [[ $sts -eq $STS_SUCCESS ]] || break
        wlog "\e[${PS_HDR1_COLOR}m===== [Build python $TRAVIS_PYTHON_VERSION] =====\e[0m"
        CURPYVER=$(echo $TRAVIS_PYTHON_VERSION | grep -Eo [0-9] | head -n1)
        PYTHON=$(which python$TRAVIS_PYTHON_VERSION)
        [[ -z "$PYTHON" ]] && PYTHON=$(which python$CURPYVER)
        PYTHON_VERSION=$($PYTHON --version 2>&1 | grep -Eo "[0-9]+\.[0-9]+")
        if [[ $PYTHON_VERSION != $TRAVIS_PYTHON_VERSION ]]; then
          wlog "\e[${PS_HDR1_COLOR}mError: Required version $TRAVIS_PYTHON_VERSION of python is not availale. Replace by $PYTHON_VERSION\e[${PS_TXT_COLOR}m"
          continue
        fi
        alias python=$PYTHON
        export TRAVIS_PYTHON_VERSION
        PIP=$(which pip$TRAVIS_PYTHON_VERSION)
        [[ -z "$PIP" ]] && PIP=$(which pip$CURPYVER)
        alias pip=$PIP
        for lne in PIP PYTHON PYTHONPATH TRAVIS_PYTHON_VERSION; do
          lne1=${!lne}
          [[ -n "$lne1" || $lne =~ PATH ]] && wlog "\e[${PS_RUN_COLOR}m\$ $lne=$lne1\e[0m"
        done
        if [[ $TRAVIS_DEBUG_MODE -gt 2 ]]; then
          if [ $CURPYVER -eq 3 ]; then
            echo -e "import sys\nprint('sys.path=%s' % sys.path)\n" | $PYTHON
          else
            echo -e "import sys\nprint 'sys.path=%s' % sys.path\n" | $PYTHON
          fi
        fi
        [[ -n "$YML_matrix" ]] || YML_matrix=":"
        for lne in $YML_matrix; do
          if [[ $lne == ":" ]]; then
            line1=
            lne1=
          else
            line1="$lne"
            lne1=$(process_yaml_quote "$lne")
          fi
          if [[ $lne1 =~ ODOO_REPO=.[A-Za-z]+ && ! $lne1 =~ ODOO_REPO=.$YML_repo. ]]; then
            wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped due invalid repo\e[${PS_TXT_COLOR}m"
            continue
          fi
          if [[ $action =~ ^(force-lint|lint)$ && ! $lne1 =~ LINT=.1. ]]; then
            wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the lint action\e[${PS_TXT_COLOR}m"
            continue
          elif [[ $action =~ ^(force-test|test)$ && ! $lne1 =~ TESTS=.1. ]]; then
            wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the test action\e[${PS_TXT_COLOR}m"
            continue
          elif [[ $action =~ ^(force-testdeps|testdeps)$ && ! $lne1 =~ TEST_DEPENDENCIES=.1. ]]; then
            wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the testdeps action\e[${PS_TXT_COLOR}m"
            continue
          elif [[ $action =~ ^(force-translate|translate)$ && ! $lne1 =~ ODOO_TNLBOT=.1. ]]; then
            wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the translate action\e[${PS_TXT_COLOR}m"
            continue
          fi
          wlog "\e[${PS_HDR1_COLOR}m===== [Build job $lne1] =====\e[0m"
          create_virtual_env
          wlog "\e[${PS_HDR2_COLOR}m----- [System informations] -----\e[0m"
          for p in PATH HOME TRAVIS TRAVIS_BUILD_DIR TRAVIS_BRANCH TRAVIS_HOME TRAVIS_SAVED_HOME HOME_BRANCH PYPI_CACHED SYSTEM_SITE_PACKAGES; do
            X=${!p}
            [[ -n "$X" || $p =~ PATH ]] && wlog "\e[${PS_RUN_COLOR}m\$ $p=$X\e[0m"
          done
          process_yaml_global
          if [ $sts -eq $STS_SUCCESS ]; then
            process_yaml_before_install
            s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
          fi
          if [ $sts -eq $STS_SUCCESS ]; then
            process_yaml_install "$line1"
            s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
          fi
          if [ $sts -eq $STS_SUCCESS ]; then
            process_yaml_before_script "$line1"
            s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
          fi
          if [ $sts -eq $STS_SUCCESS ]; then
            wlog "\e[${PS_HDR2_COLOR}m===== [Script matrix $lne1] =====\e[0m"
            for lne in $YML_script; do
              process_yaml_run_cmd "$lne"
              s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
              if [ $sts -ne $STS_SUCCESS ]; then
                elog "!Script aborted by error!!"
                break
              fi
            done
          fi
          if [ $sts -eq $STS_SUCCESS ]; then
            wlog "\e[${PS_HDR2_COLOR}m===== [After success] =====\e[0m"
            process_yaml_after_success
          fi
          if [ $sts -eq $STS_SUCCESS ]; then
            process_yaml_exit
            drop_virtual_env
          else
            break
          fi
        done
      done
    fi
  fi
  echo -e "\e[0m"
  return $sts
}

process_yaml_echo() {
  # process_yaml_echo(lev, line)
  local lev=$1
  ((lev++))
  local lm="            "
  lm=${lm:0:$lev}
  local lne="$2"
  if [ $opt_dprj -ne 0 ]; then
    echo -n "$lm- "
    process_yaml_run_cmd "$lne"
  else
    local line="- $(process_yaml_quote_xtl $lne)"
    echo "$lm$line"
  fi
}

load_colors() {
    export PS_TXT_COLOR=$(get_cfg_value "" "PS_TXT_COLOR")
    export PS_RUN_COLOR=$(get_cfg_value "" "PS_RUN_COLOR")
    export PS_NOP_COLOR=$(get_cfg_value "" "PS_NOP_COLOR")
    export PS_HDR1_COLOR=$(get_cfg_value "" "PS_HDR1_COLOR")
    export PS_HDR2_COLOR=$(get_cfg_value "" "PS_HDR2_COLOR")
    export PS_HDR3_COLOR=$(get_cfg_value "" "PS_HDR3_COLOR")
}

travis_status() {
    local sts=0
    grep -Eq "\| .*test.*FAIL" $1
    if [[ $? -eq 0 ]]; then
      sts=1
    else
      grep -Eq "\| .*test.*Success" $1 && sts=0 || sts=1
    fi
    return $sts
}


OPTOPTS=(h        B         C         c        D           d     E         F        f         j        k        L          l        M          m       n            O         p        q           r     S            V           v           X           Y             y       Z)
OPTLONG=(help     debug     no-cache  conf     debug-level osx   no-savenv full     force     ''       keep     lint-level logdir   ''         missing dry-run      org       pytest   quiet       ''    syspkg       version     verbose     translation yaml-file     pyver   zero)
OPTDEST=(opt_help opt_debug opt_cache opt_conf opt_dlvl    osx_d opt_keepE opt_full opt_force opt_dprj opt_keep opt_llvl   opt_flog opt_dbgmnt opt_mis opt_dry_run  opt_org   opt_pyth opt_verbose opt_r  opt_syspkg  opt_version opt_verbose opt_tnl     opt_fyaml     opt_pyv opt_dbgmnt)
OPTACTI=(1        1         0         "="      "="         1     0         1        1         1        1        "="        "="      1          1       "1>"         "="       1        0           1     "="          "*>"        "+"         "="         "="           "="     1)
OPTDEFL=(0        0         1         ""       ""          0     1         0        0         0        0        ""         ""       0          0       0            "local"   0        -1          0     ""           ""          -1          ""          ".travis.yml" ""      0)
OPTMETA=("help"   "version" ""        "file"   "number"    ""    ""        ""       ""        "dprj"   ""       "number"   "dir"    ""         ""      "do nothing" "git-org" ""       "verbose"   "res" "false|true" "version"   "verbose"   "0|1"       "file"        "pyver" "")
OPTHELP=("this help"
  "debug mode: do not create log"
  "do not use stored PYPI"
  "configuration file (def .travis.conf)"
  "travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)"
  "emulate osx-darwin"
  "do not save virtual environment into ~/VME/... if does not exist"
  "run final travis with full features"
  "force yaml to run w/o cmd subst"
  "execute tests in project dir rather in test dir (or expand macro if parseyaml)"
  "keep DB and virtual environment after tests"
  "lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml"
  "log directory (def=$HOME/travis_log)"
  "use local MQT (deprecated)"
  "show missing line in report coverage"
  "do nothing (dry-run)"
  "git organization, i.e. oca or zeroincombenze"
  "prefer python test over bash test when avaiable"
  "silent mode"
  "run restricted mode (deprecated)"
  "use python system packages (def yaml dependents)"
  "show version"
  "verbose mode"
  "enable translation test (def yaml dependents)"
  "file yaml to process (def .travis.yml)"
  "test with specific python versions (comma separated)"
  "use local zero-tools")
OPTARGS=(action sub sub2)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
ACTIONS="(help|emulate|force-lint|lint|force-test|test|force-testdeps|testdeps|force-translate|translate|chkconfig|parseyaml|show-log|show-color|summary|wep-db)"
if [[ $opt_help -gt 0 ]]; then
  print_help "Travis-ci emulator for local developer environment\nAction may be: ${ACTIONS//|/,}" \
  "© 2015-2021 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi

export PYTHONWARNINGS="ignore"
[[ -z "$action" ]] && action=emulate
VIRTACTS="(force-lint|lint|force-test|test|emulate)"
opt_virt=1
if [[ $action =~ $ACTIONS ]]; then
  [[ ! $action =~ $VIRTACTS ]] && opt_virt=0
else
  echo "Invalid action!"
  echo "action should be one of ${ACTIONS//|/,}"
  exit $STS_FAILED
fi
opts_travis
CFG_init
conf_default
link_cfg $DIST_CONF $TCONF
[[ $opt_verbose -gt 1 ]] && set -x
init_travis

[[ -n $opt_flog ]] && LOGDIR="$(dirname $opt_flog)" || LOGDIR="$(get_cfg_value "" "LOGDIR")"
[[ -d $LOGDIR ]] || mkdir $LOGDIR
if [[ -n $opt_flog ]]; then
    LOGFILE="$opt_flog"
else
    [[ -n "$REPOSNAME" ]] && LOGFILE="$REPOSNAME" || LOGFILE=""
    [[ -n "$PKGNAME" && ! $PKGNAME == $REPOSNAME ]] && LOGFILE="${LOGFILE}_$PKGNAME"
    [[ "$PRJNAME" == "Odoo" ]] && LOGFILE="${LOGFILE}_$(build_odoo_param GIT_ORGNM '.')"
    [[ -n "$BRANCH" ]] && LOGFILE="${LOGFILE}_$BRANCH"
    LOGFILE="$LOGDIR/${LOGFILE}.log"
fi
OLD_LOGFILE=${LOGFILE/.log/_old.log}

if [[ $action == "help" ]]; then
  man $0.man
  exit $STS_SUCCESS
elif [[ $action == "parseyaml" ]]; then
  prepare_env_travis "$action"
  check_4_travis
  if [[ -z "$sub" ]]; then
    sub=$PRJPATH/.travis.yml
    if [[ ! -f $sub ]]; then
      sub=$TOOLS_PATH/travis.yml
    fi
  fi
  process_yaml_file "$sub"

  echo "python:"
  for v in $python_ver_req; do
    echo "  - $v"
  done
  echo ""
  echo "virtualenv:"
  echo " - system_site_packages: $SYSTEM_SITE_PACKAGES"
  echo ""
  echo "addons:"
  echo "  apt:"
  echo "    packages:"
  for lne in $YML_packages; do
    process_yaml_echo 3 "$lne"
  done
  echo ""
  echo "env:"
  for lne in $YML_env; do
    process_yaml_echo 1 "$lne"
  done
  echo "  global:"
  for lne in $YML_global; do
    process_yaml_echo 1 "$lne"
  done
  echo "  matrix:"
  for lne in $YML_matrix; do
    process_yaml_echo 1 "$lne"
  done
  echo ""
  echo "before_install:"
  for lne in $YML_before_install; do
    process_yaml_echo 1 "$lne"
  done
  echo ""
  echo "install:"
  for lne in $YML_install; do
    process_yaml_echo 1 "$lne"
  done
  echo ""
  echo "before_script:"
  for lne in $YML_before_script; do
    process_yaml_echo 1 "$lne"
  done
  echo ""
  echo "script:"
  for lne in $YML_script; do
    process_yaml_echo 1 "$lne"
  done
  echo ""
  echo "after_success:"
  for lne in $YML_after; do
    process_yaml_echo 1 "$lne"
  done
  exit $STS_SUCCESS
elif [[ $action =~ (wep_db|wep-db) ]]; then
  export PGUSER="$(get_cfg_value "" "MQT_DBUSER")"
  [[ -z $PGUSER ]] && export PGUSER=$(get_dbuser)
  if [[ -n $PGUSER ]]; then
    done=0
    all_dbs=1
    [[ $opt_force -ne 0 ]] && md=30 || md=1800
    dt=$(date "+%s")
    for d in $HOME/VENV_*; do
      if [[ "$d" != "$HOME/VENV_*" ]]; then
        dd=$(stat -c "%Y" $d)
        df=$(($dt - $dd))
        if [[ $df -gt $md ]]; then
          echo "\$ rm -fR $d ($(date -d@$df -u +"%H:%M:%S") old)"
          rm -fR $d
          sfx=$(echo "$d" | grep -Eo "[0-9]+$")
          for db in openerp_template$sfx openerp_test$sfx; do
            echo "\$ dropdb -U$PGUSER $db"
            pg_db_active -wa $db
            dropdb -U$PGUSER $db --if-exists &>/dev/null
            done=1
          done
        else
          ((dd = md - df))
          echo "$d ($(date -d@$df -u +"%H:%M:%S") old) will be removed in ${dd}s"
          all_dbs=0
        fi
      fi
    done
    if [[ $all_dbs -ne 0 ]]; then
      for db in $(psql -U$PGUSER -Atl | grep -E "(openerp_template|openerp_test)" | awk -F"|" '{print $1}'); do
        echo "\$ dropdb -U$PGUSER $db"
        pg_db_active -wa $db
        dropdb -U$PGUSER $db --if-exists &>/dev/null
        done=1
      done
    fi
    ((md = 60 * 60 * 24 * 90))
    if [[ -n "$LOGDIR" && -d $LOGDIR ]]; then
      for d in $LOGDIR/*; do
        dd=$(stat -c "%Y" $d)
        df=$(($dt - $dd))
        if [[ $df -gt $md ]]; then
          echo "\$ rm -fR $d ($(date -d@$df -u +"%H:%M:%S") old)"
          rm -fR $d
        fi
      done
    fi
    [[ $done -eq 0 ]] && echo "Nothing to wep"
    exit $STS_SUCCESS
  else
    exit 2
  fi
elif [[ $action == "summary" ]]; then
  [[ "$sub" == "old" ]] && logfile=$OLD_LOGFILE || logfile=$LOGFILE
  sts=0
  if [[ -f $logfile ]]; then
    echo "$(readlink -f $logfile):\$ VIRTUALENV=$(grep -E "vem .*VENV_" $logfile|grep -Eo "VENV_[0-9]+"|head -n1)"
    grep -EH "(\| .*test|TODAY=|PKGNAME=|LOGFILE=|Build python [23])" $logfile
    travis_status "$logfile"
    sts=$?
  else
    echo "File $logfile not found!"
    sts=1
  fi
  exit $sts
elif [[ $action == "show-log" ]]; then
  [[ "$sub" == "old" ]] && logfile=$OLD_LOGFILE || logfile=$LOGFILE
  if [[ ${opt_dry_run:-0} -gt 0 ]]; then
    echo "> travis > $logfile"
    sts=0
  elif [[ -f $logfile ]]; then
    less -R $logfile
    sts=0
  else
    echo "File $logfile not found!"
    sts=1
  fi
  exit $sts
elif [[ $action =~ show-colors? ]]; then
  load_colors
  echo "Colors dump"
  echo -e "\e[${PS_HDR1_COLOR}m=== HEADER 1 ===\e[0m"
  echo -e "\e[${PS_HDR2_COLOR}m--- HEADER 2 ---\e[0m"
  echo -e "\e[${PS_HDR3_COLOR}m... HEADER 3 ...\e[0m"
  echo -e "\e[${PS_RUN_COLOR}mCommand execution\e[0m"
  echo -e "\e[${PS_TXT_COLOR}mInfo text\e[0m"
  echo -e "\e[${PS_NOP_COLOR}mNo operational info\e[0m"
  exit 0
fi
if [[ $PWD == $HOME ]]; then
  echo "Cannot execute travis-ci from home directory!"
  exit 1
fi

sts=$STS_SUCCESS
prepare_env_travis "$action"
if [[ $sts -eq $STS_SUCCESS ]]; then
    if [[ $opt_debug -ne 0 ]]; then
        echo -e "\e[0;30;107m$(printf '%-80.80s' ' ')\e[0m"
        process_yaml
        sts=2
    else
        TMP_LOGFILE=${LOGFILE/.log/.tmp}
        if [[ ${opt_dry_run:-0} -gt 0 ]]; then
            echo "> travis > $LOGFILE"
        else
            echo -e "\e[0;30;107m$(printf '%-80.80s' ' ')\e[0m"
            process_yaml 2>&1 | stdbuf -i0 -o0 -e0 tee -a $TMP_LOGFILE
            sts=$?
            if [[ -f "$LOGFILE" && $LOGFILE != $OLD_LOGFILE ]]; then
                [[ -f $OLD_LOGFILE ]] && rm -f $OLD_LOGFILE
                mv -f $LOGFILE $OLD_LOGFILE
            fi
            mv -f $TMP_LOGFILE $LOGFILE
            $0 wep-db &>/dev/null
            travis_status "$LOGFILE"
            sts=$?
        fi
    fi
fi
exit $sts