#! /bin/bash
# -*- coding: utf-8 -*-
# Build start/stop odoo daemon script
# Tool for internal use
#
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2023 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
# This free software is released under GNU Affero GPL3
#
## split log
## conditions: logrotate = False && workers != 0
## options: logrotate-size = 2G (default)
## command: ($sz > size, $log > Logfile, $last > last_chunk
## split -a1 -d -b $sz $log ${log}.
## rm -f ${log}.0
## rm -f $log
## mv ${log}.${last} $log
##
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

__version__=2.0.4


get_arch () {
    if [ "$1" == "CentOS7" -o "$1" == "CentOS" -o "$1" == "RHEL" ]; then
      DISTO="CentOS7"
      FH="RHEL"
      LXCORE=
      MACHARCH="x86_64"
    elif [ "$1" == "CentOS6" ]; then
      DISTO="CentOS6"
      FH="RHEL"
      LXCORE=
      MACHARCH="i686"
    elif [ "$1" == "Ubuntu14" -o "$1" == "Ubuntu"  -o "$1" == "Debian" ]; then
      DISTO="Ubuntu14"
      FH="Debian"
      LXCORE="trusty"
      MACHARCH="x86_64"
    elif [ "$1" == "Ubuntu12" ]; then
      DISTO="Ubuntu12"
      FH="Debian"
      LXCORE="precise"
      MACHARCH="i686"
    fi
}

expand_line () {
  local ln="$1"
  for p in $2; do
      ln="${ln//\$\{$p\}/${!p}}"
  done
  if [ "${1:0:14}" == "# \${xtl_name} " ]; then
    local x="${ln%%This*}"
    i=${#x}
    local y="${1%%This*}"
    j=${#y}
    local x="${ln:0:i}                           "
    local y="${ln:i}"
    ln="${x:0:j}$y"
  elif  [ "${1:0:11}" == "# version: " ]; then
    local v=$(echo "$1"|awk -F: '{ print $2 }')
    local ln="# version: ${__version__} ($(echo $v)) $(date +%Y-%m-%d)"
  fi
  echo "$ln"
}


update_odoo_conf() {
# update_odoo_conf(odoo_vid confn)
    local odoo_vid=$1
    if [ -z "$2" ]; then
      local confn=$(build_odoo_param CONFN $odoo_vid '' $opt_org)
    else
      local confn=$1
    fi
    if [ ! -f $confn ]; then
      echo "File $confn not found!"
      exit 1
    fi
    local tgt=$confn.tmp
    [ -f $tgt ] && rm -f $tgt
    touch $tgt
    local DDIR=$(build_odoo_param DDIR $odoo_vid '' $opt_org)
    local FLOG=$(build_odoo_param FLOG $odoo_vid '' $opt_org)
    local FPID=$(build_odoo_param FPID $odoo_vid '' $opt_org)
    local RPCPORT=$(build_odoo_param RPCPORT $odoo_vid '' $opt_org)
    local odoo_ver=$(build_odoo_param MAJVER $odoo_vid)
    while IFS=\| read -r line || [ -n "$line" ]; do
      if [[ $line =~ ^data_dir[[:space:]]*=[[:space:]]*.*Odoo ]]; then
        line=$(echo "data_dir = $DDIR")
      elif [[ $line =~ ^logfile[[:space:]]*=[[:space:]]*.*  ]]; then
        line=$(echo "logfile = $FLOG")
      elif [[ $line =~ ^pidfile[[:space:]]*=[[:space:]]*.* ]]; then
        line=$(echo "pidfile = $FPID")
      elif [[ $line =~ ^[#[:space:]]*xmlrpc_port[[:space:]]*=[[:space:]]*[0-9]+ ]]; then
        if [ $odoo_ver -gt 10 ]; then
          line=$(echo "# xmlrpc_port = $RPCPORT")
        else
          line=$(echo "xmlrpc_port = $RPCPORT")
        fi
      elif [[ $line =~ ^[#[:space:]]*http_port[[:space:]]*=[[:space:]]*[0-9]+ ]]; then
        if [ $odoo_ver -gt 10 ]; then
          line=$(echo "http_port = $RPCPORT")
        else
          line=$(echo "# http_port = $RPCPORT")
        fi
      fi
      echo "$line">>$tgt
    done < "$confn"
    if $(diff -q $confn $tgt &>/dev/null); then
      rm -f $tgt
    else
      [ -f $confn.bak ] && rm -f $confn.bak
      mv $confn $confn.bak
      mv $tgt $confn
    fi
}


OPTOPTS=(h        b         c         D        E       G       L        M        n            P       S       T        t        U        V           v           X)
OPTDEST=(opt_help odoo_vid  opt_confn opt_ucfg opt_osf opt_org opt_flog opt_main opt_dry_run  opt_pid opt_svc opt_test opt_tmpl opt_user opt_version opt_verbose opt_sudo)
OPTACTI=("+"      "=>"      "=>"      1        "=>"    "="     "=>"     1        1            "=>"    "=>"    "*>"     "=>"     "=>"     "*>"        1           1)
OPTDEFL=(1        ""        ""        0        ""      ""      ""       0        0            ""      ""      ""       ""       "odoo"   ""          0           0)
OPTMETA=("help"   "vid"     "file"    ""       "linux" "id"    "file"   ""       "do nothing" "file"  "file"  "test"   "file"   "user"   "version"   "verbose"   "")
OPTHELP=("this help"\
 "select odoo version id: may be 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 or 16"
 "set odoo configuration file (default search in /etc/{id_name}/{id_name}-server).conf"
 "update default values in /etc configuration file before creating script"
 "select linux distribution: RHEL or Debian (default is current platform)"
 "set id name (odoo or openerp, default is odoo)"
 "set odoo log filename (default /var/log/{id_name}/{id_name}-server).log"
 "mono-version Odoo instance"
 "do nothing (dry-run)"
 "set odoo PID filename (default /var/run/{id_name}/{id_name}-server).pid"
 "service name (def from configuration file)"
 "created test script does nothing (used for debug)"
 "use template (def /etc/lisa/odoo-server_{linux_dist})"
 "odoo service username"
 "show version"
"verbose mode"
 "use sudo to execute command instead of start-stop-daemon (only Debian)")
OPTARGS=()

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Build Odoo daemon script"\
  "(C) 2015-2023 by zeroincombenze®\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi
# discover_multi
[[ $opt_main -ne 0 ]] && opt_multi=0 || opt_multi=1
[[ -z $opt_confn ]] && echo "Missed configuration file!" && exit 1
script_name=$(basename $opt_confn)
[[ $script_name =~ \.conf$ ]] && script_name=${script_name:0: -5}
if [[ -z $odoo_vid ]]; then
  odoo_ver=$(echo $script_name|grep -Eo "(odoo|oca)[0-9]+"|grep -Eo "[0-9]+")
  [[ ! $odoo_ver =~ (6|7|8|9|10|11|12|13|14|15|16) ]] && echo "No odoo version detected! Please use -b" && exit 1
  odoo_fver=$(build_odoo_param FULLVER $odoo_ver)
else
  odoo_fver=$(build_odoo_param FULLVER $odoo_vid)
  odoo_ver=$(build_odoo_param MAJVER $odoo_fver)
fi
if [[ -z $opt_org ]]; then
  xtl_org=$(echo $script_name|grep -Eo "[a-zA-Z0-9_]+-[a-zA-Z0-9_]*"|cut -d- -f2)
  [[ ! $xtl_org =~ (oca|odoo|librerp|zero) ]] && sfx="$xtl_org" && xtl_org=""
else
  xtl_org=$opt_org
  sfx=""
fi
if [[ -z $odoo_vid ]]; then
  [[ -z $xtl_org ]] && odoo_vid="odoo${odoo_ver}" || odoo_vid="${xtl_org}${odoo_ver}"
  [[ -n $sfx ]] && odoo_vid="${odoo_vid}-${sfx}"
fi
GIT_ORGNM=$(build_odoo_param GIT_ORGNM $odoo_vid)
if [[ -z $opt_svc ]]; then
  SVCNAME=$(build_odoo_param SVCNAME $odoo_vid)
  [[ -n $sfx && ! $SVCNAME =~ $sfx$ ]] && SVCNAME="${SVCNAME}-$sfx"
else
  SVCNAME=$opt_svc
fi
CONFN=$(build_odoo_param CONFN $odoo_vid)
[[ -n $sfx && ! $CONF =~ $sfx$ ]] && CONFN="${CONFN/.conf/-$sfx.conf}"
if [[ $script_name != $SVCNAME || $CONFN != $opt_confn ]]; then
  echo "Configuration data mismatch!"
  echo "Odoo version=$odoo_fver"
  echo "Odoo branch=$odoo_vid"
  echo "Config=$CONFN (by Odoo branch) / Config=$opt_confn (supplied value)"
  echo "Service name=$SVCNAME (by Odoo branch) / Service name=$script_name (from config file)"
  read -p "Confirm build (y/n)? " dummy
  [[ ! $dummy =~ y ]] && exit 1
  CONFN=$opt_confn
  SVCNAME=$script_name
fi

def_pidfile=$(build_odoo_param FPID $odoo_vid)
[[ -n $sfx && ! $def_pidfile =~ $sfx$ ]] && def_pidfile="${def_pidfile/.pid/-$sfx.pid}"
def_flogfile=$(build_odoo_param FLOG $odoo_vid)
[[ -n $sfx && ! $def_flogfile =~ $sfx$ ]] && def_flogfile="${def_flogfile/.log/-$sfx.log}"

if [[ -n "$CONFN" ]]; then
  PIDFILE=$(grep "^pidfile *=" $CONFN|awk -F= '{print $2}')
  PIDFILE=$(echo $PIDFILE)
  [[ -n "$opt_pid" && $opt_pid != $PIDFILE ]] && echo -e "\e[31mMismatch pid file <$opt_pid>: config name is <$PIDFILE>\e[0m" && exit 1
  LOGFILE=$(grep "^logfile *=" $CONFN|awk -F= '{print $2}')
  LOGFILE=$(echo $LOGFILE)
  [[ -n "$opt_flog" && $opt_flog != $LOGFILE ]] && echo -e "\e[31mMismatch log file <$opt_flog>: config name is <$LOGFILE>\e[0m" && exit 1
else
  PIDFILE="$def_pidfile"
  [[ -n "$opt_pid" && $opt_pid != $PIDFILE ]] && echo -e "\e[33mWarning! Supplied pid file <$opt_pid> but expected <$PIDFILE>" && PIDFILE="$opt_pid\e[0m"
  LOGFILE="$def_flogfile"
  [[ -n "$opt_flog" && $opt_flog != $LOGFILE ]] && echo -e "\e[33mWarning! Supplied log file <$opt_flog> but expected <$LOGFILE>" && LOGFILE="$opt_flog\e[0m"
fi
[[ $def_pidfile != $PIDFILE ]] && echo -e "\e[33mWarning! PID file is <$PIDFILE> but expected <$def_pidfile>\e[0m"
[[ $def_flogfile != $LOGFILE ]] && echo -e "\e[33mWarning! LOG file is <$LOGFILE> but expected <$def_flogfile>\e[0m"

if [[ $SVCNAME =~ ^openerp ]]; then
  opt_id="openerp"
else
  opt_id="odoo"
fi
opt_confn2="$(dirname $opt_confn)"
opt_confn2="$(readlink -m $opt_confn2/..)/$(basename $opt_confn)"
if [[ -n $opt_osf ]]; then
  get_arch "$opt_osf"
  if [[ ! $FH =~ (RHEL|Debian) ]]; then
    echo "Invalid Linux distribution: use -d RHEL o -d Debian"
    exit 1
  fi
else
  FH=$(xuname "-f")
fi

echo "Building $script_name for $SVCNAME service under $FH Linux distribution"
echo -e "- logfile is \e[32m$LOGFILE\e[0m"
echo -e "- pidfile is \e[32m$PIDFILE\e[0m"
echo -e "- def.conf.file is \e[32m$CONFN\e[0m"
echo -e "- alt.conf.file is \e[32m$opt_confn2\e[0m"
src_template=""
[[ -n "$opt_tmpl" && -f $opt_tmpl ]] && src_template="$opt_tmpl"
if [[ -z $src_template ]]; then
  for d in $TDIR . /etc/lisa; do
    if [[ -f $d/$opt_tmpl ]]; then
        src_template=$d/$opt_tmpl
        break
    else
        for p in $FH .;do
          if [[ "$p" == "." ]]; then
            n=$d/odoo-server
          else
            n=$d/odoo-server_$FH
          fi
          if [[ -f $n ]]; then
            src_template=$n
            break
          fi
        done
        if [[ -n "$src_template" ]]; then
          break
        fi
    fi
  done
fi
if [[ -z $src_template ]]; then
  echo "Template odoo-server_* not found"
  exit 1
fi

[[ -f $script_name.tmp ]] && rm -f $script_name.tmp
begin_scrpt=0
prm_list="xtl_org"
dbg=0
while IFS=\| read -r line; do
  if [ "${line:0:1}" == "#" ]; then
    begin_scrpt=1
  elif [ $begin_scrpt -eq 0 ]; then
    prm=$(echo "$line"|awk -F\= '{ print $1 }')
    val=$(echo "$line"|awk -F\= '{ print $2 }')
    if [ "$prm" == "xtl_id" ]; then
      declare $prm="$opt_id"
    elif [ "$prm" == "xtl_Id" ]; then
      if [ "$opt_id" == "odoo" ]; then
        declare $prm="Odoo"
      elif [ "$opt_id" == "openerp" ]; then
        declare $prm="OpenERP"
      else
        declare $prm="$opt_id"
      fi
    elif [ "$prm" == "xtl_name" ]; then
      declare $prm="$SVCNAME"
    elif [ "$prm" == "xtl_logfile" ]; then
      declare $prm="$LOGFILE"
    elif [ "$prm" == "xtl_pidfile" ]; then
      declare $prm="$PIDFILE"
    elif [ "$prm" == "xtl_cfgfile" ]; then
      declare $prm="$CONFN"
    elif [ "$prm" == "xtl_altcfgfile" ]; then
      declare $prm="$opt_confn2"
    elif [ "$prm" == "xtl_version" ]; then
      declare $prm="$odoo_ver"
    elif [ "$prm" == "xtl_fversion" ]; then
      declare $prm="$odoo_fver"
    elif [ "$prm" == "xtl_user" ]; then
      declare $prm="$opt_user"
    elif [ "$prm" == "xtl_test" ]; then
      if [ "$opt_test" == "-T" ]; then
        declare $prm="1"
      else
        declare $prm="0"
      fi
    elif [ "$prm" == "xtl_sudo" ]; then
      if [ "$opt_sudo" -ne 0 ]; then
        declare $prm="1"
      else
        declare $prm="0"
      fi
    else
      val=$(expand_line "$val" "$prm_list")
      declare $prm="$val"
    fi
    prm_list="$prm_list $prm"
  fi
  if [ $begin_scrpt -gt 0 ]; then
    line=$(expand_line "$line" "$prm_list")
    if [ $opt_verbose -gt 0 ]; then
      echo "$line"
    fi
    echo "$line">>$script_name.tmp
  fi
done < "$src_template"

if [ $opt_dry_run -eq 0 ]; then
  if [ -f $script_name ]; then
    mv -f $script_name $script_name.bak
  fi
  mv -f $script_name.tmp $script_name
  chmod +x $script_name
  d=$(dirname $script_name)
  if [ "$d" != "/etc/init.d" ]; then
    echo "To make active created script, you must type \"mv $script_name /etc/init.d\""
  fi
else
  echo "See $script_name.tmp to discover how to script works"
fi


