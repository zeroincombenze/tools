#! /bin/bash
# -*- coding: utf-8 -*-
#
# set_color
# Set color for Odoo web interface
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2018 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYPATH=$(echo -e "import sys\nprint(str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1])"|python)
for d in $TDIR $TDIR/.. $TDIR/../z0lib $TDIR/../../z0lib ${PYPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ]; then
    . $d/z0lib/z0librc
    Z0LIBDIR=$d/z0lib
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi
ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. $HOME/tools/clodoo $HOME/dev ${PYPATH//:/ } . .." "clodoo")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)

__version__=0.3.6.44


get_odoo_service_name() {
# get_odoo_service_name(odoo_fver)
    local svcname=$(build_odoo_param SVCNAME $1)
    echo $svcname
}

list_themes_n_skin() {
# list_themes_n_skin (odoo_theme_rep skindirlist odoo_vid opt_webdir)
    local odoo_theme_rep="$1"
    local skindirlist="$2"
    local odoo_vid=$3
    local webdir=$4
    local themelist skinlist
    local d f fn
    for d in $skindirlist $odoo_theme_rep; do
      if [ -d  $d ]; then
        [ $opt_verbose -gt 0 ] && echo "Searching in $d ..."
        for f in $d/odoo_theme_*.conf; do
          if [ -f "$f" ]; then
            x=$(basename $f)
            fn=${x:11: -5}
            if [[ ! " $skinlist " =~ [[:space:]]$fn[[:space:]] ]]; then
              skinlist="$skinlist $fn"
            fi
          fi
        done
        for d in $odoo_theme_rep/*; do
          if [ -d  $d ]; then
            if [ -f $d/__openerp__.py -o -f $d/__manifest__.py ]; then
              f=$(basename $d)
              if [[ ! " $themelist " =~ [[:space:]]$f[[:space:]] ]]; then
                themelist="$themelist $f"
              fi
            fi
          fi
        done
      fi
    done
    [ $opt_verbose -gt 0 ] && echo "Searching in $webdir ..."
    for f in $webdir/*.sass; do
      fn=$(basename $f)
      fn=${fn:0: -5}
      if [[ ! " $skinlist " =~ [[:space:]]$fn[[:space:]] ]]; then
        skinlist="$skinlist $fn"
      fi
    done
    [ -f $webdir/base.z0i ] && skinlist="$skinlist zeroincombenze"
    [ -f $webdir/base.oia ] && skinlist="$skinlist oia"
    [ -f $webdir/base.vg7 ] && skinlist="$skinlist vg7"
    echo -e "Themes:$themelist\nSkins :$skinlist"
}

update_base_sass() {
# update_base_sass (odoo_theme_rep skindirlist odoo_vid opt_webdir sel_skin)
    local odoo_theme_rep="$1"
    local skindirlist="$2"
    local odoo_vid=$3
    local webdir=$4
    local sel_skin=$5
    run_traced "cd $webdir"
    local fsrc=$(get_cfg_value 0 sass_filename)
    [ -n "$fsrc" ] || fsrc="$sel_skin.sass"
    [ -f "$fsrc" ] || fsrc="$opt_sass"
    [ ! -f "$fsrc" -a "$sel_skin" == "zeroincombenze"  -a -f "base.z0i" ] || fsrc="base.z0i"
    [ ! -f "$fsrc" -a "$sel_skin" == "oia"  -a -f "base.oia" ] || fsrc="base.oia"
    [ ! -f "$fsrc" -a "$sel_skin" == "vg7"  -a -f "base.oia" ] || fsrc="base.vg7"
    if [ ! -f "$fsrc" ]; then
      echo "No file $opt_sass found for skin $sel_skin!"
      return
    fi
    local ftmp="$fsrc.tmp"
    [ $opt_verbose -gt 0 ] && echo "Reading $fsrc, writing $ftmp ..."
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
      echo "$opt_css: $opt_sass" > Makefile
      echo -e "\tsass --trace -t expanded $opt_sass $opt_css" >> Makefile
    fi
    if [ "$fsrc" == "base.sass" -a ! -f "odoo-default.sass" ]; then
      run_traced "cp -p $fsrc odoo-default.sass"
    fi
    if [ $opt_force -ne 0 ] || [ -n "$(diff -q $ftmp $fsrc)" ] || [ -n "$(diff -q $ftmp $opt_sass)" ]; then
      if [ $opt_diff -ne 0 ]; then
        echo "diff -y --suppress-common-line $opt_sass $ftmp"
        diff -y --suppress-common-line $opt_sass $ftmp
      fi
      run_traced "cp -f $fsrc $fsrc.bak"
      run_traced "mv -f $ftmp $opt_sass"
      run_traced "sass --trace -t expanded $opt_sass $opt_css"
      run_traced "chown odoo:odoo $opt_sass $opt_css $fsrc.bak"
      svname=$(get_odoo_service_name $odoo_vid)
      if [ "$theme" == "odoo" ]; then
        run_traced "sed -i -e 's:^web_skin *=:# web_skin =:' /etc/odoo/$svname.conf"
      else
        run_traced "sed -i -e 's:^[# ]*web_skin *=.*:web_skin = $theme:' /etc/odoo/$svname.conf"
      fi
      run_traced "sudo systemctl restart $svname"
    else
      [ $opt_verbose -gt 0 ] && echo "No skin changed"
      [ ${opt_dry_run:-0} -eq 0 ] && rm -f $fntmp
    fi
}


OPTOPTS=(h        c        D        d          f         l        m         n            q           s           T         V           v)
OPTDEST=(opt_help opt_conf opt_diff opt_webdir opt_force opt_list opt_multi opt_dry_run  opt_verbose opt_sass    test_mode opt_version opt_verbose )
OPTACTI=(1        "="      1        "="        1         1        1         1            0           "="         1         "*>"        "+")
OPTDEFL=(1        ""       0        ""         0         0        -1        0            -1          "base.sass" 0         ""          -1)
OPTMETA=("help"   "file"   "dir"      ""        "list"   ""        "do nothing" "quit"      "file"      "test"    "version"   "verbose")
OPTHELP=("this help"\
 "configuration file (def .travis.conf)"\
 "show diff (implies dry-run)"\
 "odoo web dir (def. /opt/odoo/{odoo_fver}/addons/web/static/src/css)"\
 "force generation of css file"\
 "list themes"\
 "multi-version odoo environment"\
 "do nothing (dry-run)"\
 "silent mode"\
 "target sass file (def=base.sass)"\
 "test mode (implies dry-run)"\
 "show version"\
 "verbose mode")
OPTARGS=(odoo_vid sel_skin)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Manage odoo themes (8.0+) & skin (all versions)"\
  "(C) 2015-2018 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi
if [ "$DEV_ENVIRONMENT" == "$THIS" ]; then
  test_mode=1
fi
if [ $test_mode -ne 0 ]; then
  opt_dry_run=1
fi
if [ $opt_diff -ne 0 ]; then
  opt_dry_run=1
fi
discover_multi
odoo_fver=$(build_odoo_param FULLVER $odoo_vid)
odoo_ver=$(build_odoo_param MAJVER $odoo_vid)
odoo_theme_rep=$(build_odoo_param ROOT $odoo_vid)/website-themes
skindirlist=""
if [ $opt_list -ne 0 ]; then
  if [ $test_mode -ne 0 ]; then
    skindirlist="$TESTDIR/themes $TESTDIR/../themes ./themes ../themes"
  else
    skindirlist="$TDIR/themes $TDIR/../themes ./themes ../themes"
  fi
else
  if [ -n "$theme" -a $test_mode -eq 0 ]; then
    COLORFILE=$(findpkg "odoo_theme.conf" "/opt/odoo/$odoo_fver/themes/$theme")
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
  if [ -n "$COLORFILE" -a $opt_verbose -gt 0 ]; then
    echo "$THIS -c $COLORFILE"
  fi
fi
if [ -z "$opt_conf" -a $test_mode -ne 0 ]; then
  opt_conf=~/dev/pypi/travis_emulator/travis_emulator/.travis.conf
fi
CFG_init
link_cfg $COLORFILE $TCONF                                      # No Std Code
if [ $opt_verbose -gt 1 ]; then set -x; fi
if [[ $HOSTNAME =~ $HOSTNAME_PRD ]]; then
  tgt="prd"
elif [[ $HOSTNAME =~ $HOSTNAME_DEV ]]; then
  tgt="dev"
else
  tgt=""
fi
if [ "${opt_sass: -5}" != ".sass" ]; then
  opt_sass=$opt_sass.sass
fi
if [ -z "$opt_webdir" ]; then
  if [ $test_mode -ne 0 ]; then
    opt_webdir=$TESTDIR/themes
  else
    sass=$(findpkg $opt_sass "/opt/odoo/$odoo_vid/addons/web/static/src/css /opt/odoo/$odoo_vid/website /opt/odoo/$odoo_vid")
    if [ -n "$sass" ]; then
      opt_webdir=$(dirname $sass)
    fi
  fi
fi
if [ -z "$opt_webdir" ]; then
  echo "No valid skin (File $opt_sass not found)!"
  exit 1
fi
opt_css=${opt_sass:0: -5}.css
if [ $opt_list -ne 0 ]; then
  list_themes_n_skin "$odoo_theme_rep" "$skindirlist" "$odoo_vid" "$opt_webdir"
else
  update_base_sass "$odoo_theme_rep" "$skindirlist" "$odoo_vid" "$opt_webdir" "$sel_skin"
fi
