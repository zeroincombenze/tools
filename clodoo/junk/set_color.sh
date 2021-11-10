#! /bin/bash
# -*- coding: utf-8 -*-
# Set web interface colors to customize odoo
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\nHOME=os.environ.get('HOME');y=os.path.join(HOME_DEV,'pypi');t=os.path.join(HOME,'tools')\ndef apl(l,p,x):\n  d2=os.path.join(p,x,x)\n  d1=os.path.join(p,x)\n  if os.path.isdir(d2):\n   l.append(d2)\n  elif os.path.isdir(d1):\n   l.append(d1)\nl=[TDIR]\nfor x in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(y):\n  apl(l,y,x)\n elif TDIR.startswith(t):\n  apl(l,t,x)\nl=l+os.environ['PATH'].split(':')\np=set()\npa=p.add\np=[x for x in l if x and x.startswith(HOME) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"

__version__=0.3.36.1


OPTOPTS=(h        n            V           v)
OPTDEST=(opt_help opt_dry_run  opt_version opt_verbose )
OPTACTI=(1        "1"          "*>"        1)
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
  "(C) 2015-2016 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
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
