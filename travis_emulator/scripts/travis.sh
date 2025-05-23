#! /bin/bash
# -*- coding: utf-8 -*-
#
# Travis-ci emulator
# Emulate travis-ci on local machine, to test before upgrade git project
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2025 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 2.0.0
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
[[ -x $TDIR/../bin/python3 ]] && PYTHON=$(readlink -f $TDIR/../bin/python3) || [[ -x $TDIR/python3 ]] && PYTHON="$TDIR/python3" || PYTHON=$(which python3 2>/dev/null) || PYTHON="python"
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
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo")
[[ -z "$ODOOLIBDIR" ]] && echo "Library file odoorc not found!" && exit 72
. $ODOOLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=$ODOOLIBDIR"
TRAVISLIBDIR=$(findpkg travisrc "$PYPATH" "travis_emulator")
[[ -z "$TRAVISLIBDIR" ]] && echo "Library file travisrc not found!" && exit 72
. $TRAVISLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TRAVISLIBDIR=$TRAVISLIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"

CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.10


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
  CFG_set "$2" "$3" "$1" "$4" "$5"
}

debug_shell() {
    echo "PS1='ctrl+d to exit> '">/tmp/$$.sh
    [[ -n "$1" ]] && echo "TODO>$1"
    eval $SHELL --noprofile --rcfile /tmp/$$.sh -s
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
  [[ -z $PGUSER ]] && export PGUSER=$(get_dbuser)
  python_ver_yaml=""
  if [ $opt_dbgmnt -ne 0 ]; then
    [[ -d $HOME_DEVEL/pypi ]] && export YML_lisa=$HOME_DEVEL/pypi/lisa/lisa/lisa
    (($opt_debug)) && export TRAVIS_PDB="true"
  else
    export YML_lisa=lisa
    export YML_mgrodoo=manage_odoo
  fi
  [[ $TRAVIS_DEBUG_MODE -gt 1 ]] && export VERBOSE_MODE=$TRAVIS_DEBUG_MODE
  # [[ $osx_d -ne 0 ]] && export TRAVIS_EMULATE_OSX="true"
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
  TRAVIS_VERBOSE=$opt_verbose
  [[ -n $opt_patrn ]] && export TRAVIS_TEST_PATTERN="$opt_patrn"
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
    if [[ $action =~ ^(force-test|test|force-test-multi|test-multi)$ ]]; then
      line=$(echo "$line" | sed -e s/TESTS=[\"']0[\"']/TESTS=\"1\"/g)
    elif [[ $action != "emulate" ]]; then
      line=$(echo "$line" | sed -e s/TESTS=[\"']1[\"']/TESTS=\"0\"/g)
    fi
     if [[ $action =~ ^(force-test-multi|test-multi)$ ]]; then
      echo "$line" | grep -q "UNIT_TEST=..." && line=$(echo "$line" | sed -e s/UNIT_TEST=[\"']0[\"']/UNIT_TEST=\"1\"/g)
      echo "$line" | grep -qv "UNIT_TEST=..." && line="$line UNIT_TEST=\"1\""
    else
      line=$(echo "$line" | sed -e s/UNIT_TEST=[\"']1[\"']/UNIT_TEST=\"0\"/g)
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
    python_ver_yaml="$lne $python_ver_yaml"
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
    elif [[ $line =~ ODOO_REPO=.?librerp/OCB && $REMOTEREPO == "local" ]]; then
      YML_repo=librerp/OCB
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
  export TRAVIS_YAML_FILE=$1
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
  done <"$TRAVIS_YAML_FILE"
}

process_yaml_defaults() {
  local sts=$STS_SUCCESS
  local i s line lne X
  opt_verbose=$TRAVIS_VERBOSE
  wlog "\e[${PS_HDR2_COLOR}m===== [Initialize] =====\e[0m"
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [Initialize from .travis.conf] ------\e[0m"
  fi
  [[ -n $opt_trace && ::travis.conf =~ $opt_trace ]] && debug_shell "::travis.conf"
  line=$(get_cfg_value "" "GBL_EXCLUDE")
  [[ -n "$line" ]] && run_traced "export GBL_EXCLUDE=$line"
  for i in {1..9}; do
    line=$(get_cfg_value "" "yaml_init_$i")
    if [ -n "$line" ]; then
      process_yaml_run_cmd "$line"
        s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    fi
  done
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
  [[ -n $opt_tafter && ::travis.conf =~ $opt_tafter ]] && debug_shell
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
  [[ -n $opt_trace && ::env.global =~ $opt_trace ]] && debug_shell "::env.global"
  for lne in $YML_global; do
    line="export $(process_yaml_quote_xtl $lne)"
    run_traced "$line"
    s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
  done
  [[ -n $opt_tafter && ::env.global =~ $opt_tafter ]] && debug_shell
  return $sts
}

process_yaml_before_install() {
  wlog "\e[${PS_HDR2_COLOR}m===== [Before install] =====\e[0m"
  [[ -n $opt_trace && ::before_install =~ $opt_trace ]] && debug_shell "::before_install"
  local sts=$STS_SUCCESS
  local i s line lne X CURPYVER
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[addons.apt.packages] in .travis.yml] ------\e[0m"
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    [[ -n $opt_trace && ::addons.apt.package =~ $opt_trace ]] && debug_shell "::addons.apt.package"
    CURPYVER=$(echo $TRAVIS_PYTHON_VERSION | grep --color=never -Eo '[0-9]' | head -n1)
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
      [[ $s -ne 0 ]] && echo -e "\e[${PS_HDR3_COLOR}mInternal error! Statement failed!\e[${PS_TXT_COLOR}m"
    done
    [[ -n $opt_tafter && ::addons.apt.package =~ $opt_tafter ]] && debug_shell
  fi
  if [[ $TRAVIS_DEBUG_MODE -ne 0 ]]; then
    wlog "\e[${PS_HDR3_COLOR}m------ [[before_install] in .travis.yml] ------\e[0m"
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    for lne in $YML_before_install; do
      [[ $TRAVIS_DEBUG_MODE -ge 3 ]] && echo "#> $(process_yaml_quote_xtl $lne)"
      process_yaml_run_cmd "$lne"
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
      [[ $s -ne 0 ]] && echo -e "\e[${PS_HDR3_COLOR}mInternal error! Statement failed!\e[${PS_TXT_COLOR}m"
    done
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    for lne in $YML_env; do
      line="export $(process_yaml_quote_xtl $lne)"
      run_traced "$line"
      s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
    done
  fi
  [[ -n $opt_tafter && ::before_install =~ $opt_tafter ]] && debug_shell
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
  [[ -n $opt_trace && $xcmd =~ $opt_trace ]] && debug_shell "$xcmd"
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
                tk=$(echo $p | grep --color=never -Eo '[a-zA-Z0-9_]*' | head -n1)
              fi
              p=$(echo "$tk" | grep --color=never -Eo '[^!<=>;\[]*' | head -n1)
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
          p=$(echo "${x[$ix]}" | grep --color=never -Eo '[^!<=>;]*' | head -n1)
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
      pp=$(readlink -e $PRJPATH/../$REPOSNAME/)
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
    [[ $c != $xcmd && ! $xcmd =~ ^# ]] && ((Z0_STACK=Z0_STACK-2))
  fi
  [[ $TRAVIS_DEBUG_MODE -gt 2 ]] && echo "<<<PATH=$PATH>>>"
  [[ -n $opt_tafter && $xcmd =~ $opt_tafter ]] && debug_shell
  return $sts
}

get_pyver_4_odoo() {
#get_pyver_4_odoo(odoo_version)
    local m x
    m=$(echo $1|grep -Eo [0-9]+|head -n1)
    if [[ $m -le 10 ]]; then
      echo "2.7"
    else
      ((x=((m-9)/2)+6))
      echo "3.$x"
    fi
}

process_yaml() {
  # process_yaml ()
  local sts=$STS_SUCCESS
  local i s p v X x
  local line lne line1 lne1
  load_colors
  export TRAVIS_DEBUG_MODE="${opt_dlvl:-1}"
  if [[ -n $opt_fyaml ]]; then
      export TRAVIS_YAML_FILE=$opt_fyaml
  else
      export TRAVIS_YAML_FILE="$PWD/.travis.yml"
      [[ ! -f $TRAVIS_YAML_FILE ]] && export TRAVIS_YAML_FILE="$PRJPATH/.travis.yml"
      if [[ ! -f $TRAVIS_YAML_FILE ]]; then
          [[ ! -d $HOME/tmp ]] && mkdir $HOME/tmp
          export TRAVIS_YAML_FILE=$HOME/tmp/travis$$.yml
          mk_travis_conf=$(readlink -e $TDIR/make_travis_conf.py)
          [[ -z $mk_travis_conf ]] && mk_travis_conf=$(find $PYPATH -name make_travis_conf.py|head -n1)
          export TRAVIS_YAML_ORIG=$(find $PYPATH -name template_travis.yml|head -n1)
          python $mk_travis_conf "$TRAVIS_YAML_ORIG" "$TRAVIS_YAML_FILE"
      fi
  fi
  if [[ $action == "chkconfig" ]]; then
      if [[ ! -f $TRAVIS_YAML_FILE ]]; then
        do_chkconfig
        return $STS_SUCCESS
      fi
  fi
  if [[ ! -f $TRAVIS_YAML_FILE ]]; then
      echo -e "\e[${PS_HDR3_COLOR}mNo configuration file $TRAVIS_YAML_FILE found!\e[${PS_TXT_COLOR}m"
      return 127
  fi

  echo -e "\e[0;30;107m$(printf '%-80.80s' ' ')\e[0m"
  wlog "\e[${PS_HDR1_COLOR}m$(printf '%-80.80s' '=== Process YAML file ===')\e[0m"
  export TRAVIS_HOME_BRANCH=$PWD
  process_yaml_file "$TRAVIS_YAML_FILE"
  unset PYTHONPATH
  sts=$STS_SUCCESS

  if [[ $sts -eq $STS_SUCCESS ]]; then
    [[ -n $opt_trace && ::matrix =~ $opt_trace ]] && debug_shell "::matrix"
    [[ -z "$python_ver_yaml" ]] && python_ver_yaml="3.11 3.10 3.9 3.8 3.7 3.6 3.5 2.7"
    if [[ -n $opt_pyv ]]; then
      TRAVIS_PYTHON_MATRIX="${opt_pyv//,/ }"
      python_ver_yaml="$TRAVIS_PYTHON_MATRIX"
    elif [[ $PRJNAME == "Odoo" ]]; then
      TRAVIS_PYTHON_MATRIX=$(get_pyver_4_odoo $BRANCH)
    else
      TRAVIS_PYTHON_MATRIX=""
      for v in "3.11" "3.10" "3.9" "3.8" "3.7" "3.6" "3.5" "2.7"; do
          grep -q "^ *.Programming Language :: Python :: $v" $PKGPATH/setup.py && TRAVIS_PYTHON_MATRIX="$TRAVIS_PYTHON_MATRIX|$v"
      done
      TRAVIS_PYTHON_MATRIX="${TRAVIS_PYTHON_MATRIX:1}"
    fi
    TRAVIS_PYTHON_MATRIX="${TRAVIS_PYTHON_MATRIX//,/|}"
    TRAVIS_PYTHON_MATRIX="${TRAVIS_PYTHON_MATRIX// /|}"
    [[ $TRAVIS_PYTHON_MATRIX =~ ^\( ]] || TRAVIS_PYTHON_MATRIX="($TRAVIS_PYTHON_MATRIX)"
    python_matrix=""
    for v in $python_ver_yaml; do
      [[ $v =~ $TRAVIS_PYTHON_MATRIX ]] && python_matrix="$python_matrix $v"
    done
    [[ -n $python_matrix ]] || python_matrix=$(get_pyver_4_odoo $BRANCH)

    for TRAVIS_PYTHON_VERSION in $python_matrix; do
      [[ $sts -eq $STS_SUCCESS ]] || break
      echo -e "\e[0;30;107m$(printf '%-80.80s' ' ')\e[0m"
      wlog "\e[${PS_HDR1_COLOR}m===== [Build python $TRAVIS_PYTHON_VERSION] =====\e[0m"
      set_pybin $TRAVIS_PYTHON_VERSION "PYTHON_VERSION"
      TRAVIS_PYVER_1=$(echo $TRAVIS_PYTHON_VERSION | grep --color=never -Eo "[0-9]" | head -n1)
      TRAVIS_PYVER_2=$(echo $TRAVIS_PYTHON_VERSION | grep --color=never -Eo "[0-9]\.[0-9]" | head -n1)
      if [[ $PYTHON_VERSION != $TRAVIS_PYTHON_VERSION ]]; then
        if [[ $PYTHON_VERSION != $TRAVIS_PYVER_2 ]]; then
          wlog "\e[${PS_HDR3_COLOR}mError: Required version $TRAVIS_PYTHON_VERSION of python is not availale. You could use $PYTHON_VERSION\e[${PS_TXT_COLOR}m"
          continue
        fi
        wlog "\e[${PS_HDR1_COLOR}mWarning: Required version $TRAVIS_PYTHON_VERSION of python is replaced by $PYTHON_VERSION\e[${PS_TXT_COLOR}m"
        TRAVIS_PYTHON_VERSION=$TRAVIS_PYVER_2
      fi
      export TRAVIS_PYTHON_VERSION
      [[ -n "$YML_matrix" ]] || YML_matrix=":"
      for lne in $YML_matrix; do
        if [[ $lne == ":" ]]; then
          line1=
          lne1=
        else
          line1="$lne"
          lne1=$(process_yaml_quote "$lne")
        fi
        [[ -n $opt_tafter && ::matrix =~ $opt_tafter ]] && debug_shell
        if [[ $lne1 =~ ODOO_REPO=.[A-Za-z]+ && ! $lne1 =~ ODOO_REPO=.$YML_repo. ]]; then
          wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped due invalid repo\e[${PS_TXT_COLOR}m"
          continue
        fi
        if [[ $action =~ ^(force-lint|lint)$ && ! $lne1 =~ LINT=.1. ]]; then
          wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the lint action\e[${PS_TXT_COLOR}m"
          continue
        elif [[ $action =~ ^(force-test|test|force-test-multi|test-multi)$ && ! $lne1 =~ TESTS=.1. ]]; then
          wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the test action\e[${PS_TXT_COLOR}m"
          continue
        elif [[ $action =~ ^(force-testdeps|testdeps)$ && ! $lne1 =~ TEST_DEPENDENCIES=.1. ]]; then
          wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the testdeps action\e[${PS_TXT_COLOR}m"
          continue
        elif [[ $action =~ ^(force-translate|translate)$ && ! $lne1 =~ ODOO_TNLBOT=.1. ]]; then
          wlog "\e[${PS_HDR3_COLOR}mMatrix [$lne1] skipped because does not match the translate action\e[${PS_TXT_COLOR}m"
          continue
        fi
        echo -e "\e[0;30;107m$(printf '%-80.80s' ' ')\e[0m"
        wlog "\e[${PS_HDR1_COLOR}m===== [Build job $lne1] =====\e[0m"
        [[ -n $opt_trace && ::build =~ $opt_trace ]] && debug_shell "::build"
        create_virtual_env

        wlog "\e[${PS_HDR2_COLOR}m===== [System informations] =====\e[0m"
        TODAY=$(date "+%Y-%m-%d %H:%M:%S")
        for p in TODAY job-id __version__ TCONF YML_lisa YML_mgrodoo YML_repo\
         BRANCH DIST HOME HOME_BRANCH HOME_DEVEL LOGFILE MQT_TEMPLATE_DB MQT_TEST_DB\
          ODOO_ROOT PATH PKGNAME PKGPATH PIP PIPVER PRJNAME PRJPATH PGUSER PYPI_CACHED\
           PYTHON PYTHONPATH REPOSNAME TRAVIS TRAVIS_BRANCH TRAVIS_BUILD_DIR\
             TRAVIS_HOME TRAVIS_HOME_BRANCH TRAVIS_PDB TRAVIS_PYTHON_MATRIX\
              TRAVIS_PYTHON_VERSION TRAVIS_REPO_SLUG TRAVIS_SAVED_HOME\
               TRAVIS_SAVED_HOME_DEVEL TRAVIS_TEST_PATTERN TRAVIS_YAML_FILE\
                TRAVIS_YAML_ORIG SYSTEM_SITE_PACKAGES; do
          if [[ $p == "job-id" ]]; then
            X=$$
          elif [[ $p == "DIST" ]]; then
            X=$(xuname -a)
          elif [[ $p == "__version__" ]]; then
            X=$__version__
          else
            X=${!p}
          fi
          [[ -n "$X" || $p =~ PATH ]] && wlog "\e[${PS_NOP_COLOR}m\$ $p=$X\e[0m"
        done

        if [[ $sts -eq $STS_SUCCESS ]]; then
          process_yaml_defaults
          s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
        fi
        [[ -n $opt_tafter && ::build =~ $opt_tafter ]] && debug_shell
        process_yaml_global
        if [[ $sts -eq $STS_SUCCESS ]]; then
          process_yaml_before_install
          s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
        fi
        if [[ $sts -eq $STS_SUCCESS ]]; then
          process_yaml_install "$line1"
          s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
        fi
        if [[ $sts -eq $STS_SUCCESS ]]; then
          process_yaml_before_script "$line1"
          s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
        fi
        if [[ $sts -eq $STS_SUCCESS ]]; then
          wlog "\e[${PS_HDR2_COLOR}m===== [Script matrix $lne1] =====\e[0m"
          [[ -n $opt_trace && ::script =~ $opt_trace ]] && debug_shell "::script"
          for lne in $YML_script; do
            process_yaml_run_cmd "$lne"
            s=$?; [ ${s-1} -eq 0 -o $sts -ne 0 ] || sts=$s
            if [ $sts -ne $STS_SUCCESS ]; then
              elog "!Script aborted by error!!"
              break
            fi
          done
        fi
        if [[ $sts -eq $STS_SUCCESS ]]; then
          wlog "\e[${PS_HDR2_COLOR}m===== [After success] =====\e[0m"
          process_yaml_after_success
        fi
        if [[ $sts -eq $STS_SUCCESS ]]; then
          process_yaml_exit
          drop_virtual_env
          [[ $TRAVIS_YAML_FILE =~ ^$HOME/tmp ]] && run_traced "mv $TRAVIS_YAML_FILE ${LOGFILE/.log/.yml}"
          [[ ! $TRAVIS_YAML_FILE =~ ^$HOME/tmp && -f ./travis.yml ]] && run_traced "cp .travis.yml ${LOGFILE/.log/.yml}"
        else
          break
        fi
      done
    done
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
  local line="- $(process_yaml_quote_xtl $lne)"
  echo "$lm$line"
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
    grep -iEq "test (['\"][^'\"]+['\"] )?failed" $1
    if [[ $? -eq 0 ]]; then
      sts=1
    else
      grep -iEq "\| .*test.*successfully" $1 && sts=0 || sts=1
    fi
    return $sts
}

set_log_filename() {
    # UDI (Unique DB Identifier): format "{pkgname}_{git_org}{major_version}"
    # UMLI (Unique Module Log Identifier): format "{git_org}{major_version}.{repos}.{pkgname}"
    local m="$PKGNAME" odoo_ver=$(build_odoo_param MAJVER ${BRANCH})
    [[ -z $GIT_ORGID ]] && GIT_ORGID="$(build_odoo_param GIT_ORGID '.')"
    [[ -n $ODOO_GIT_ORGID && $GIT_ORGID =~ $ODOO_GIT_ORGID ]] && UDI="$m" || UDI="$m_${GIT_ORGID}"
    [[ $PRJNAME == "Odoo" && -n $UDI ]] && UDI="${UDI}_${odoo_ver}"
    [[ $PRJNAME == "Odoo" && -z $UDI ]] && UDI="${odoo_ver}"
    [[ $PRJNAME == "Odoo" ]] && UMLI="${GIT_ORGID}${odoo_ver}" || UMLI="${GIT_ORGID}"
    [[ -n "$REPOSNAME" && $REPOSNAME != "OCB" ]] && UMLI="${UMLI}.${REPOSNAME//,/+}"
    [[ -n $m ]] && UMLI="${UMLI}.$m"
    if [[ -n $opt_flog ]]; then
      LOGDIR="$(dirname $opt_flog)"
      LOGFILE="$opt_flog"
    else
      LOGDIR="$(get_cfg_value "" "LOGDIR")"
      [[ -z $LOGDIR ]] && LOGDIR="$ODOO_ROOT/travis_log"
      [[ -d $LOGDIR ]] || mkdir $LOGDIR
      LOGFILE="$LOGDIR/${UMLI}.log"
    fi
    OLD_LOGFILE=${LOGFILE/.log/_old.log}
}


OPTOPTS=(h        A           B         C         D           E         e       F        f         k        j       L          l        m       n            O         P           p         Q        q           r     S            T         V           v           X           Y         Z)
OPTLONG=(help     trace-after debug     no-cache  debug-level no-savenv locale  full     force     keep     python  lint-level logdir   missing dry-run      org       python-brk  pattern   config   quiet       ''    syspkg       trace     version     verbose     translation yaml-file zero)
OPTDEST=(opt_help opt_tafter  opt_debug opt_cache opt_dlvl    opt_keepE opt_loc opt_full opt_force opt_keep opt_pyv opt_llvl   opt_flog opt_mis opt_dry_run  opt_org   opt_pybrk   opt_patrn opt_tcfg opt_verbose opt_r  opt_syspkg  opt_trace opt_version opt_verbose opt_tnl     opt_fyaml opt_dbgmnt)
OPTACTI=('+'      "="         1         0         "="         0         "="     1        1         1        "="     "="        "="      1       "1>"         "="       "="         "="       "="      0           1     "="          "="       "*>"        "+"         "="         "="       1)
OPTDEFL=(0        ""          0         1         ""          1         ""      0        0         0        ""      ""         ""       0       0            "local"   ""          ""        ""       0           0     ""           ""        ""          -1          ""          ""        0)
OPTMETA=("help"   "regex"     "version" ""        "number"    ""        "iso"   ""       ""        ""       "pyver" "number"   "dir"    ""      "do nothing" "git-org" "file:line" "pattern" "file"   "verbose"   "res" "false|true" "regex"   "version"   "verbose"   "0|1"       "file"    "")
OPTHELP=("this help"
  "travis stops after executed yaml statement"
  "debug mode: do not create log"
  "do not use stored PYPI"
  "travis_debug_mode: may be 0,1,2,3,8 or 9 (def yaml dependents)"
  "do not save virtual environment into ~/VME/... if does not exist"
  "use locale"
  "run final travis with full features"
  "force to create stored VME or remove recent log (wep-db)"
  "keep DB and virtual environment before and after tests"
  "test with specific python versions (comma separated)"
  "lint_check_level: may be minimal,reduced,average,nearby,oca; def value from .travis.yml"
  "log directory (def=$ODOO_ROOT/travis_log)"
  "show missing line in report coverage"
  "do nothing (dry-run)"
  "git organization to test, i.e. oca or zeroincombenze"
  "set python breakpoint at file:linenumber"
  "pattern to apply for test files (comma separated)"
  "configuration file (def .z0tools.conf)"
  "silent mode"
  "run restricted mode (deprecated)"
  "use python system packages (def yaml dependents)"
  "trace stops before executing yaml statement"
  "show version"
  "verbose mode"
  "enable translation test (def yaml dependents)"
  "file yaml to process (def .travis.yml)"
  "use local zero-tools")
OPTARGS=(action sub sub2)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
ACTIONS="(help|emulate|force-lint|lint|force-test|test|force-test-multi|test-multi|force-testdeps|testdeps|force-translate|translate|chkconfig|parseyaml|show|show-log|show-color|summary|wep-db)"
if [[ $opt_help -gt 0 ]]; then
  print_help "Travis-ci emulator for local developer environment\nAction may be: ${ACTIONS//|/,}" \
  "© 2015-2022 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi

export PYTHONWARNINGS="ignore"
[[ -n "$opt_tafter" || -n "$opt_trace" || -n "$opt_pybrk" ]] && opt_debug=1
[[ -z "$action" && $opt_debug -ne 0 ]] && action="test"
[[ -z "$action" ]] && action="emulate"
VIRTACTS="(force-lint|lint|force-test|test|force-test-multi|test-multi|emulate)"
opt_virt=1
if [[ $action =~ $ACTIONS ]]; then
  [[ ! $action =~ $VIRTACTS ]] && opt_virt=0
else
  echo "Invalid action!"
  echo "action should be one of ${ACTIONS//|/,}"
  exit $STS_FAILED
fi
opts_travis
conf_default
[[ $opt_verbose -gt 2 ]] && set -x
init_travis
# prepare_env_travis

set_log_filename

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
  for v in $python_ver_yaml; do
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
  done_db=0
  done_ve=0
  all_dbs=1
  [[ $opt_force -ne 0 ]] && md=30 || md=1800
  dt=$(date "+%s")
  for d in $HOME/VENV_*; do
    if [[ "$d" != "$HOME/VENV_*" ]]; then
      dd=$(stat -c "%Y" $d)
      df=$(($dt - $dd))
      if [[ $df -gt $md ]]; then
        [[ $opt_verbose -gt 0 ]] && echo "\$ rm -fR $d ($(date -d@$df -u +"%H:%M:%S") old)"
        rm -fR $d
        ((done_ve++))
        sfx=$(echo "$d" | grep --color=never -Eo "[0-9]+$")
        if [[ -n $PGUSER ]]; then
          for db in template_odoo_$sfx test_odoo_$sfx; do
            [[ $opt_verbose -gt 0 ]] && echo "\$ dropdb -U$PGUSER \"$db\""
            pg_db_active -wa "$db"
            run_traced "dropdb -U$PGUSER \"$db\" --if-exists &>/dev/null"
            c=$(pg_db_active -c "$db")
            [[ $c -ne 0 ]] && echo "FATAL! There are $c other sessions using the database \"$db\"" || ((done_db++))
          done
        fi
      else
        ((dd = md - df))
        echo "$d ($(date -d@$df -u +"%H:%M:%S") old) will be removed in ${dd}s"
        all_dbs=0
      fi
    fi
  done
  if [[ -n $PGUSER && $all_dbs -ne 0 ]]; then
    for db in $(psql -U$PGUSER -Atl | grep -E "(openerp_test|openerp_template|test_openerp|template_openerp|test_odoo|template_odoo)[0-9]+" | awk -F"|" '{print $1}'); do
      [[ $opt_verbose -gt 0 ]] && echo "\$ dropdb -U$PGUSER \"$db\""
      pg_db_active -wa "$db"
      run_traced "dropdb -U$PGUSER \"$db\" --if-exists &>/dev/null"
      c=$(pg_db_active -c "$db")
      [[ $c -ne 0 ]] && echo "FATAL! There are $c other sessions using the database \"$db\"" || ((done_db++))
    done
  fi
  ((md = 60 * 60 * 24 * 90))
  if [[ -n "$LOGDIR" && -d $LOGDIR ]]; then
    for d in $LOGDIR/*; do
      dd=$(stat -c "%Y" $d)
      df=$(($dt - $dd))
      if [[ $df -gt $md ]]; then
        [[ $opt_verbose -gt 0 ]] && echo "\$ rm -fR $d ($(date -d@$df -u +"%H:%M:%S") old)"
        rm -fR $d
        ((done_ve++))
      fi
    done
  fi
  [[ $done_db -eq 0 ]] && echo "Warning: no DB to wep"
  [[ $done_db -ne 0 && $opt_verbose -gt 0 ]] && echo "$done_db DB removed"
  [[ $done_ve -ne 0 && $opt_verbose -gt 0 ]] && echo "$done_ve directories removed"
  exit $STS_SUCCESS
elif [[ $action == "summary" ]]; then
  [[ "$sub" == "old" ]] && logfile=$OLD_LOGFILE || logfile=$LOGFILE
  sts=0
  if [[ -f $logfile ]]; then
    echo "$(readlink -f $logfile):\$ VIRTUALENV=$(grep -E "vem .*VENV_" $logfile|grep --color=never -Eo "VENV_[0-9]+"|head -n1)"
    grep -EH "(\| .*test|TODAY=|PKGNAME=|LOGFILE=|Build python [23])" $logfile
    travis_status "$logfile"
    sts=$?
  else
    echo -e "\e[${PS_HDR3_COLOR}mFile $logfile not found!\e[${PS_TXT_COLOR}m"
    sts=1
  fi
  exit $sts
elif [[ $action =~ ^(show|show-log)$ ]]; then
  [[ "$sub" == "old" ]] && logfile=$OLD_LOGFILE || logfile=$LOGFILE
  if [[ ${opt_dry_run:-0} -gt 0 ]]; then
    echo "> travis > $logfile"
    sts=0
  elif [[ -f $logfile ]]; then
    less -R $logfile
    sts=0
  else
    echo -e "\e[${PS_HDR3_COLOR}mFile $logfile not found!\e[${PS_TXT_COLOR}m"
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
            clear
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

