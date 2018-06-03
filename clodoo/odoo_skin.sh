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
for d in $TDIR $TDIR/.. $TDIR/../.. $HOME/dev $HOME/tools ${PYPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ] && [ -e $d/z0lib/z0librc ]; then
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

__version__=0.3.6.47


get_odoo_service_name() {
# get_odoo_service_name(odoo_fver)
    local svcname=$(build_odoo_param SVCNAME $1)
    echo $svcname
}

list_themes_n_skin() {
# list_themes_n_skin (theme_dirs odoo_vid webdir sel_theme)
    local theme_dirs="$1"
    local odoo_vid=$2
    local webdir=$3
    local sel_theme=$4
    local themelist skinlist themeskin_dir
    local d d0 f fn
    for d0 in $theme_dirs; do
      if [ -d "$d0" ]; then
        [ -z "$sel_theme" -a $opt_verbose -gt 0 ] && echo "Searching in $d0 ..."
        for d in $theme_dirs/*; do
          if [ -d  $d ]; then
            if [ -f $d/$COLORFILE ]; then
              fn=$(basename $d)
              if [ -n "$sel_theme" ]; then
                if [ "$fn" == "$sel_theme" ]; then
                  themeskin_dir=$d
                  break
                fi
              elif [[ ! " $skinlist " =~ [[:space:]]$fn[[:space:]] ]]; then
                skinlist="$skinlist $fn"
              fi
            elif [ -f $d/__openerp__.py -o -f $d/__manifest__.py ]; then
              fn=$(basename $d)
              if [ -n "$sel_theme" ]; then
                if [ "$fn" == "$sel_theme" ]; then
                  themeskin_dir=$d
                  break
                fi
              elif [[ ! " $themelist " =~ [[:space:]]$fn[[:space:]] ]]; then
                themelist="$themelist $fn"
              fi
            fi
          fi
        done
      fi
    done
    [ -z "$sel_theme" -a $opt_verbose -gt 0 ] && echo "Searching in $webdir ..."
    if [ -f $webdir/base.z0i ]; then
      [ ! -f $webdir/zeroincombenze.sass ] && mv $webdir/base.z0i $webdir/zeroincombenze.sass
    fi
    if [ -f $webdir/base.oia ]; then
      [ ! -f $webdir/oia.sass ] && mv $webdir/base.oia $webdir/oia.sass
    fi
    if [ -f $webdir/base.vg7 ]; then
      [ ! -f $webdir/vg7.sass ] && mv $webdir/base.vg7 $webdir/vg7.sass
    fi
    for f in $webdir/*.sass; do
      fn=$(basename $f)
      fn=${fn:0: -5}
      if [ -n "$sel_theme" ]; then
        if [ "$fn" == "$sel_theme" ]; then
          themeskin_dir=$webdir
          break
        fi
      elif [[ ! " $skinlist " =~ [[:space:]]$fn[[:space:]] ]]; then
        skinlist="$skinlist $fn"
      fi
    done
    if [ -n "$sel_theme" ]; then
      echo "$themeskin_dir"
    else
      echo -e "Themes:$themelist\nSkins :$skinlist"
    fi
}

cp_grf_file() {
# cp_grf_file (path file)
    if [ -f "$webdir/static/src/img/$2" ]; then
      if ! diff -q $1/$2 $webdir/static/src/img/$2 &>/dev/null; then 
        [ $opt_verbose -gt 0 ] && echo "Copying $1 ..."
        mv $webdir/static/src/img/$2 $webdir/static/src/img/$2.bak
        cp $1/$2 $webdir/static/src/img/$2
        restart_req=1
      fi
    fi
}

update_base_sass() {
# update_base_sass (theme_dirs odoo_vid webdir sel_theme)
    restart_req=0
    local webdir=$3
    local res=$(list_themes_n_skin "$@")
    [ -f $res/favicon.ico ] && cp_grf_file "$res" "favicon.ico"
    [ -f $res/logo.png ] && cp_grf_file "$res" "logo.png"
    [ -f $res/logo2.png ] && cp_grf_file "$res" "logo2.png"
    if [ $restart_req -ne 0 -a $test_mode -eq 0 ]; then
      svname=$(get_odoo_service_name $odoo_vid)
      run_traced "sudo systemctl restart $svname"
    fi
    return

    local theme_dirs="$1"
    local theme_dirs="$2"
    local odoo_vid=$3

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
    while IFS=~ read -r line; do
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
          if [[ $line =~ ^//.[a-zA-Z0-9_-]+:[[:space:]]*$devcol ]]; then
            echo $line|sed -e s://::>>$ftmp
          elif [[ $line =~ ^.[a-zA-Z0-9_-]+:[[:space:]]*$devcol ]]; then
            echo "$line">>$ftmp
          elif [[ $line =~ ^[^/] ]]; then
            echo "//$line">>$ftmp
          else
             eval $cmd>>$ftmp
          fi
        elif [ "$tgt" == "prd" ]; then
          if [[ $line =~ ^//.[a-zA-Z0-9_-]+:[[:space:]]*$prdcol ]]; then
            echo $line|sed -e s://::>>$ftmp
          elif [[ $line =~ ^.[a-zA-Z0-9_-]+:[[:space:]]*$prdcol ]]; then
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
        if [[ $line =~ ^.[a-zA-Z0-9_-]+[[:space:]]*: ]]; then
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


OPTOPTS=(h        c        D        d          f         l        m         n            q           s           T         V           v           x)
OPTDEST=(opt_help opt_conf opt_diff opt_webdir opt_force opt_list opt_multi opt_dry_run  opt_verbose opt_sass    test_mode opt_version opt_verbose opt_xml)
OPTACTI=(1        "="      1        "="        1         1        1         1            0           "="         1         "*>"        "+"         "=")
OPTDEFL=(1        ""       0        ""         0         0        -1        0            -1          "base.sass" 0         ""          -1          "base.xml")
OPTMETA=("help"   "file"   ""       "dir"      ""        "list"   ""        "do nothing" "quit"      "file"      "test"    "version"   "verbose"   "file")
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
 "verbose mode"\
 "target xml file (def=base.xml)")
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
if [ $test_mode -ne 0 ]; then
  theme_dirs=$TESTDIR/website-themes
else
  theme_dirs=$(build_odoo_param ROOT $odoo_vid)/website-themes
fi
COLORFILE="skin_colors.def"
if [ -z "$opt_conf" -a $test_mode -ne 0 ]; then
  opt_conf=~/dev/pypi/travis_emulator/travis_emulator/.travis.conf
fi
CFG_init
link_cfg $TCONF
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
    opt_webdir=$TESTDIR/odoo/addons/web/static/src/css
  else
    xml=$(findpkg $opt_xml "/opt/odoo/$odoo_vid/addons/web/static/src/xml /opt/odoo/$odoo_vid/website /opt/odoo/$odoo_vid")
    if [ -n "$xml" ]; then
      opt_webdir=$(dirname $xml)
    fi
  fi
fi
if [ -z "$opt_webdir" ]; then
  echo "No valid skin (File $opt_xml not found)!"
  exit 1
fi
opt_css=${opt_sass:0: -5}.css
opt_webdir=$(readlink -f $opt_webdir/../../..)
if [ $opt_list -ne 0 ]; then
  list_themes_n_skin "$theme_dirs" "$odoo_vid" "$opt_webdir"
else
  update_base_sass "$theme_dirs" "$odoo_vid" "$opt_webdir" "$sel_skin"
fi
