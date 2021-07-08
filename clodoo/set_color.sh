#! /bin/bash
# -*- coding: utf-8 -*-
# Set web interface colors to customize odoo
#
THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in "$TDIR" "." ".." "~" "/etc"; do
  if [ -e $x/z0librc ]; then
    . $x/z0librc
    Z0LIBDIR=$x
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi

__version__=0.3.31.3


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
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
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
