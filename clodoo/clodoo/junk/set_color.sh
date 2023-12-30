#! /bin/bash
# -*- coding: utf-8 -*-
# Set web interface colors to customize odoo
#
# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
# Based on template 2.0.13
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
if [[ -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
[[ -x $TDIR/../bin/python3 ]] && PYTHON=$(readlink -f $TDIR/../bin/python3) || [[ -x $TDIR/python3 ]] && PYTHON="$TDIR/python3" || PYTHON=$(which python3 2>/dev/null) || PYTHON="python"
[[ -z $PYPATH ]] && PYPATH=$(echo -e "import os,sys\no=os.path\na=o.abspath\nj=o.join\nd=o.dirname\nb=o.basename\nf=o.isfile\np=o.isdir\nC=a('"$TDIR"')\nD='"$HOME_DEVEL"'\nU='setup.py'\nH=o.expanduser('~')\nR=j(D,'pypi')\nW=j(D,'venv')\nS='site-packages'\nX='scripts'\nY=[x for x in sys.path if b(x)==S]\nY=Y[0] if Y else C\ndef isk(P):\n return P.startswith((H,D,C,W)) and p(P) and p(j(P,X)) and f(j(P,'__init__.py')) and f(j(P,'__main__.py'))\ndef adk(L,P):\n if p(j(P,X)) and j(P,X) not in L:\n  L.append(j(P,X))\n if P not in L:\n  L.append(P)\nL=[C]\nfor B in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n for P in [C]+os.environ['PATH'].split(':')+[W,R]:\n  P=a(P)\n  if b(P) in (X,'tests','travis','_travis'):\n   P=d(P)\n  if b(P)==b(d(P)) and f(j(P,'..',U)):\n   P=d(d(P))\n  if B==b(P) and isk(P):\n   adk(L,P)\n   break\n  elif isk(j(P,B,B)):\n   adk(L,j(P,B,B))\n   break\n  elif isk(j(P,B)):\n   adk(L,j(P,B))\n   break\n  else:\n   adk(L, j(Y,B))\nadk(L,os.getcwd())\nprint(' '.join(L))\n"|$PYTHON)
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

CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.0.8


OPTOPTS=(h        n            V           v)
OPTDEST=(opt_help opt_dry_run  opt_version opt_verbose )
OPTACTI=("+"      "1"          "*>"        1)
OPTDEFL=(1        0            ""          0)
OPTMETA=("help"   "do nothing" "version"   "verbose")
OPTHELP=("this help"\
 "do nothing (dry-run)"\
 "touch config file, do not run odoo"\
 "show version"\
 "verbose mode")
OPTARGS=(odoo_ver)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Set odoo web interface colors"\
  "(C) 2015-2016 by zeroincombenze®\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi


update_base_sass () {
    local fsrc="base.sass"
    local ftmp="base.sass.tmp"
    local lctr=0
    local tk
    local devcol
    local prdcol
    local cmd=
    cd /opt/odoo/$odoo_ver/addons/web/static/src/css
    if [ -f $ftmp ]; then rm -f $ftmp; fi
    msts=0
    while IFS=\~ read -r line; do
      if [ $msts -eq 0 ]; then
        if [[ $line =~ ^//.*dev=.*prod=.* ]]; then
          msts=3
          for tk in $line; do
            if [[ $tk =~ dev=.* ]]; then
              devcol=$(echo $tk|awk -F= '{print $2}')
              if [ "$HOSTNAME" == "$HOSTNAME_PRD" ]; then
                cmd="echo \$line|sed -e s~^.[a-zA-Z0-9_\-]*:[[:space:]]*$devcol~//\&~"
              fi
            elif [[ $tk =~ prod=.* ]]; then
              prdcol=$(echo $tk|awk -F= '{print $2}')
              if [ "$HOSTNAME" == "$HOSTNAME_DEV" ]; then
                cmd="echo \$line|sed -e s~^.[a-zA-Z0-9_\-]*:[[:space:]]*$prdcol~//\&~"
              fi
            fi
          done
        fi
        echo "$line">>$ftmp
      elif [ $msts -gt 0 ]; then
        ((msts--))
        if [ "$HOSTNAME" == "$HOSTNAME_DEV" ]; then
          if [[ $line =~ ^//.[a-zA-Z0-9_\-]*:[[:space:]]*$devcol ]]; then
            echo $line|sed -e s://::>>$ftmp
          else
             eval $cmd>>$ftmp
          fi
        elif [ "$HOSTNAME" == "$HOSTNAME_PRD" ]; then
          if [[ $line =~ ^//.[a-zA-Z0-9_\-]*:[[:space:]]*$prdcol ]]; then
            echo $line|sed -e s://::>>$ftmp
          else
            eval $cmd>>$ftmp
          fi
        else
          eval $cmd>>$ftmp
        fi
      else
        echo "$line">>$ftmp
      fi
    done < "$fsrc"
    if [ ${opt_dry_run:-0} -eq 0 ]; then
      mv -f $ftmp $fsrc
      make
      service openerp-server restart
    fi
}


HOSTNAME_PRD="shsdef16"
HOSTNAME_DEV="shsita16"
if [ "$HOSTNAME" == "$HOSTNAME_DEV" ]; then
  echo "Impostazione colori macchina di sviluppo"
  update_base_sass
elif [ "$HOSTNAME" == "$HOSTNAME_PRD" ]; then
  echo "Impostazione colori macchina di produzione"
  update_base_sass
else
  echo "Macchina non riconosciuta"
fi

