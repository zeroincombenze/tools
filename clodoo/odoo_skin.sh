#! /bin/bash
# -*- coding: utf-8 -*-
#
# set_color
# Set color for Odoo web interface
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2017 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in $TDIR $TDIR/.. . .. $TDIR/../../z0lib $TDIR/../z0lib /etc; do
  if [ -e $x/z0librc ]; then
    . $x/z0librc
    Z0LIBDIR=$x
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi
TRAVISLIBDIR=$(findpkg travisrc "$TDIR $TDIR/.. . .. $HOME/dev $TDIR/../../travis_emulator")
if [ -z "$TRAVISLIBDIR" ]; then
  echo "Library file travisrc not found!"
  exit 2
fi
. $TRAVISLIBDIR
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)

__version__=0.1.9


get_odoo_service_name() {
# get_odoo_service_name(odoo_ver)
    local svcname=
    if [ "$1" == "v7" ]; then
      svcname="openerp-server"
    elif [ "$1" == "10.0" ]; then
      svcname="odoo10"
    else
      svcname="odoo${1:0:1}-server"
    fi
    echo $svcname
}

list_themes() {
# list_themes(themedirlist odoo_ver webdir)
    local themedirlist="$1"
    local odoo_ver=$2
    local webdir=$3
    local themelist
    local d f fn
    for d in $themedirlist; do
      if [ -d  $d ]; then
        [ $opt_verbose -gt 0 ] && echo "Searching in $d ..."
        for f in $d/odoo_theme_*.conf; do
          if [ -f "$f" ]; then
            x=$(basename $f)
            fn=${x:11: -5}
            if [[ " $themelist " =~ [[:space:]]$fn[[:space:]] ]]; then
              :
            else
              themelist="$themelist $fn"
            fi
          fi
        done
        for f in $(find /opt/odoo/$odoo_ver/themes -type d); do
          if [ -f $f/odoo_theme.conf ]; then
            fn=$(basename $f)
            if [[ " $themelist " =~ [[:space:]]$fn[[:space:]] ]]; then
              :
            else
              themelist="$themelist $fn"
            fi
          fi
        done
      fi
    done
    [ $opt_verbose -gt 0 ] && echo "Searching in $webdir ..."
    for f in $webdir/*.sass; do
      fn=$(basename $f)
      fn=${fn:0: -5}
      if [ "$fn" != "base" ]; then
        if [[ " $themelist " =~ [[:space:]]$fn[[:space:]] ]]; then
          :
        else
          themelist="$themelist $fn"
        fi
      fi
    done
    echo $themelist
}

update_base_sass() {
#update_base_sass(theme tgt webdir odoo_ver)
    local theme=$1
    local tgt=$2
    local webdir=$3
    local odoo_ver=$4
    run_traced "cd $webdir"
    local fsrc=$(get_cfg_value 0 sass_filename)
    cd $webdir
    if [ -z "$fsrc" ]; then
      fsrc="$theme.sass"
    fi
    if [ ! -f "$fsrc" ]; then
      fsrc="base.sass"
    fi
    if [ ! -f "$fsrc" ]; then
      echo "No file base.sass found!"
      return
    fi
    [ $opt_verbose -gt 0 ] && echo "Reading $fsrc ..."
    local ftmp="$fsrc.tmp"
    rm -f $ftmp;
    local lctr=0
    local tk devcol qtcol prdcol svcname
    local color param prm msts x
    local cmd=
    color=
    param=
    msts=0
    while IFS=\~ read -r line; do
      if [ $msts -eq 0 ] && [[ $line =~ ^//.*dev=.*prod=.* ]]; then
        if [[ $line =~ ^//.*dev=.*qt=.*prod=.* ]]; then
          msts=3
        else
          msts=2
        fi
        for tk in $line; do
          if [[ $tk =~ dev=.* ]]; then
            devcol=$(echo $tk|awk -F= '{print $2}')
            if [ "$tgt" == "dev" ]; then
              cmd="echo \$line|sed -e s~^.[a-zA-Z0-9_\-]+:[[:space:]]*$devcol~//\&~"
            fi
          elif [[ $tk =~ qt=.* ]]; then
            qtcol=$(echo $tk|awk -F= '{print $2}')
          elif [[ $tk =~ prod=.* ]]; then
            prdcol=$(echo $tk|awk -F= '{print $2}')
            if [ "$tgt" == "prd" ]; then
              cmd="echo \$line|sed -e s~^.[a-zA-Z0-9_\-]+:[[:space:]]*$prdcol~//\&~"
            fi
          fi
        done
        echo "$line">>$ftmp
      elif [ $msts -gt 0 ]; then
        ((msts--))
        if [ "$tgt" == "dev" ]; then
          if [[ $line =~ ^//.[a-zA-Z0-9_\-]+:[[:space:]]*$devcol ]]; then
            echo $line|sed -e s://::>>$ftmp
          elif [[ $line =~ ^.[a-zA-Z0-9_\-]+:[[:space:]]*$devcol ]]; then
            echo "$line">>$ftmp
          elif [[ $line =~ ^[^/] ]]; then
            echo "//$line">>$ftmp
          else
             eval $cmd>>$ftmp
          fi
        elif [ "$tgt" == "prd" ]; then
          if [[ $line =~ ^//.[a-zA-Z0-9_\-]+:[[:space:]]*$prdcol ]]; then
            echo $line|sed -e s://::>>$ftmp
          elif [[ $line =~ ^.[a-zA-Z0-9_\-]+:[[:space:]]*$prdcol ]]; then
            echo "$line">>$ftmp
          elif [[ $line =~ ^[^/] ]]; then
            echo "//$line">>$ftmp
          else
            eval $cmd>>$ftmp
          fi
        else
          eval $cmd>>$ftmp
        fi
      else
        if [[ $line =~ ^.[a-zA-Z0-9_\-]+[[:space:]]*: ]]; then
          param=${line:1}
          prm=$(echo $param|grep -Eo "^[a-zA-Z0-9_\-]+"|head -n1)
          param=CSS_${prm//-/_}
          x=$(get_cfg_value 0 $param)
          if [ -z "$x" ]; then
            echo "$line">>$ftmp
          else
            if [ "${x:0:1}" == "#" ]; then
              color="${x^^}"
            else
              color="$x"
            fi
            echo "\$$prm: $color">>$ftmp
          fi
        else
          echo "$line">>$ftmp
        fi
      fi
    done < "$fsrc"
    if [ ! -f Makefile ]; then
      echo "base.css: base.sass" > Makefile
      echo -e "\tsass --trace -t expanded base.sass base.css" >> Makefile
    fi
    # if [ ${opt_dry_run:-0} -eq 0 ]; then
    if [ "$fsrc" == "base.sass" -a ! -f "openerp.sass" ]; then
      run_traced "cp -p $fsrc openerp.sass"
    fi
    run_traced "mv -f $fsrc $fsrc.bak"
    run_traced "mv -f $ftmp base.sass"
    run_traced "make"
    run_traced "chown odoo:odoo base.sass base.css $fsrc.bak"
    svname=$(get_odoo_service_name $odoo_ver)
    run_traced "service $svname restart"
    # fi
}


OPTOPTS=(h        c        d          l        n            q           T         V           v)
OPTDEST=(opt_help opt_conf opt_webdir opt_list opt_dry_run  opt_verbose test_mode opt_version opt_verbose )
OPTACTI=(1        "="      "="        1        1            0           1         "*>"        "+")
OPTDEFL=(1        ""       ""         0        0            -1          0         ""          -1)
OPTMETA=("help"   "file"   "dir"      "list"   "do nothing" "quit"      "test"    "version"   "verbose")
OPTHELP=("this help"\
 "configuration file (def .travis.conf)"\
 "odoo web dir (def. /opt/odoo/{odoo_ver}/addons/web/static/src/css)"\
 "list themes"\
 "do nothing (dry-run)"\
 "silent mode"\
 "test mode (implies dry-run)"\
 "show version"\
 "verbose mode")
OPTARGS=(odoo_ver theme)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Install odoo theme"\
  "(C) 2015-2017 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi
if [ "$DEV_ENVIRONMENT" == "$THIS" ]; then
  test_mode=1
fi
if [ $test_mode -ne 0 ]; then
  opt_dry_run=1
fi
themedirlist=""
if [ $opt_list -ne 0 ]; then
  if [ $test_mode -ne 0 ]; then
    themedirlist="$TESTDIR/themes $TESTDIR/../themes ./themes ../themes"
  else
    themedirlist="/opt/odoo/$odoo_ver/themes $TDIR/themes $TDIR/../themes ./themes ../themes"
  fi
else
  if [ -n "$theme" -a $test_mode -eq 0 ]; then
    COLORFILE=$(findpkg "odoo_theme.conf" "/opt/odoo/$odoo_ver/themes/$theme")
  else
    COLORFILE=
  fi
  if [ -z "$COLORFILE" ]; then
    if [ $test_mode -ne 0 ]; then
      COLORFILE=$(findpkg "odoo_theme_$theme.conf" "$TESTDIR/themes $TESTDIR/../themes ./themes ../themes")
    else
      COLORFILE=$(findpkg "odoo_theme_$theme.conf" "$TDIR/themes $TDIR/../themes ./themes ../themes")
    fi
  fi
fi
if [ -z "$opt_conf" -a $test_mode -ne 0 ]; then
  opt_conf=~/dev/pypi/travis_emulator/travis_emulator/.travis.conf
fi
opts_travis
CFG_init
conf_default

link_cfg $COLORFILE $TCONF
if [ $opt_verbose -gt 1 ]; then set -x; fi
if [[ $HOSTNAME =~ $HOSTNAME_PRD ]]; then
  tgt="prd"
elif [[ $HOSTNAME =~ $HOSTNAME_DEV ]]; then
  tgt="dev"
else
  tgt=""
fi
if [ -z "$opt_webdir" ]; then
  if [ $test_mode -ne 0 ]; then
    opt_webdir=$TESTDIR/themes
  else
    sass=$(findpkg base.sass "/opt/odoo/$odoo_ver/addons/web/static/src/css /opt/odoo/$odoo_ver")
    opt_webdir=$(dirname $sass)
  fi
fi
if [ $opt_list -ne 0 ]; then
  list_themes "$themedirlist" "$odoo_ver" "$opt_webdir"
else
  update_base_sass "$theme" "$tgt" "$opt_webdir" "$odoo_ver"
fi
