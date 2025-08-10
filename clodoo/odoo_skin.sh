#! /bin/bash
# -*- coding: utf-8 -*-
#
# set_color
# Set color for Odoo web interface
#
# Files layout:
# {web_module_root}/static/src/xml/base.xml
#     xml web interface to build web pages, i.e. login and/or db management
# {web_module_root}/static/src/css/base.css
#     css used to build web pages base on base.xml. This file is created by
#     base.sass using sass command.
#     This css are also used to print qweb pages
# {web_module_root}/static/src/css/img/*
#     Directory with base image like favicon, odoo logo, etc. Main are:
#     - favicon.ico -> favicon (16x16px image)
#     - logo.png -> odoo logo (1); about 180x46px
#     - logo2.png -> odoo logo (1); about 190x46px
#     - no_logo.png -> trasparent logo (1); bout 180x46px
#     (1) name is defined by above base.xml
# {base_module_root}/static/src/img/*
#     Directory with some images used in internal views:
#     - avatar.png -> avatar for users
#     - company_image.png -> palceholder for company in partner view
#     - icon.png -> placeholer for app w/o icon
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2019 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
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
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"

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

__version__=2.0.14


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
                if [ "$fn" == "$sel_theme" -o "$fn" == "theme_$sel_theme" ]; then
                  themeskin_dir=$d
                  break
                fi
              elif [[ ! " $skinlist " =~ [[:space:]]$fn[[:space:]] ]]; then
                skinlist="$skinlist $fn"
              fi
            elif [ -f $d/__openerp__.py -o -f $d/__manifest__.py ]; then
              fn=$(basename $d)
              if [ -n "$sel_theme" ]; then
                if [ "$fn" == "$sel_theme" -o "$fn" == "theme_$sel_theme" ]; then
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
        if [ "$fn" == "$sel_theme" -o "$fn" == "theme_$sel_theme" ]; then
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
      if [ -f $webdir/static/current_skin.txt ]; then
        echo -n "Current skin: "
        cat $webdir/static/current_skin.txt
      fi
    fi
}

cp_grf_file() {
# cp_grf_file (path file)
    [ $opt_verbose -gt 0 ] && echo "Check for $2 ..."
    if [ -f "$webdir/static/src/img/$2" ]; then
      if ! diff -q $1/$2 $webdir/static/src/img/$2 &>/dev/null; then
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          [ $opt_verbose -gt 0 ] && echo "Copying $1/$2 to $webdir/static/src/img/..."
          mv $webdir/static/src/img/$2 $webdir/static/src/img/$2.bak
          cp $1/$2 $webdir/static/src/img/$2
          restart_req=1
        else
          [ $opt_verbose -gt 0 ] && echo "File $1/$2 should be copied to $webdir/static/src/img/"
        fi
      fi
    fi
}

cp_icon_file() {
# cp_grf_file (path file)
    [ $opt_verbose -gt 0 ] && echo "Check for $2 ..."
    if [ -f "$opt_icond/$2" ]; then
      if ! diff -q $1/$2 $opt_icond/$2 &>/dev/null; then
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          [ $opt_verbose -gt 0 ] && echo "Copying $1/$2 to $opt_icond/"
          mv $opt_icond/$2 $opt_icond/$2.bak
          cp $1/$2 $opt_icond/$2
          restart_req=1
        else
          [ $opt_verbose -gt 0 ] && echo "File $1/$2 should be copied to $opt_icond/"
        fi
      fi
    fi
}

cp_demo_grf_file() {
# cp_demo_grf_file (path file)
    [ $opt_verbose -gt 0 ] && echo "Check for $2 ..."
    if [ -f "$webdir/static/src/img/$2" ]; then
      if ! diff -q $1/$2 $webdir/static/src/img/$2 &>/dev/null; then
        if [ ${opt_dry_run:-0} -eq 0 ]; then
          [ $opt_verbose -gt 0 ] && echo "Copying $1/$2 to $webdir/static/src/img/..."
          mv $webdir/static/src/img/$2 $webdir/static/src/img/$2.bak
          cp $1/$2 $webdir/static/src/img/$2
          restart_req=1
        else
          [ $opt_verbose -gt 0 ] && echo "File $1/$2 should be copied to $webdir/static/src/img/"
        fi
      fi
    fi
}

write_def_conf() {
    f=$1/default.def
    cat << EOF > $f
CSS_facets_border=#afafb6
CSS_section_title_color=#7C7BAD
CSS_tag_bg_light=#f0f0fa
CSS_tag_bg_dark=#7C7BAD
CSS_tag_border=#afafb6
CSS_tag_border_selected=#a6a6fe
CSS_hover_background=#f0f0fa
CSS_link_color=#7C7BAD
CSS_sheet_max_width=auto
CSS_sheet_min_width=650px
CSS_sheet_padding=16px
EOF
}

update_base_sass() {
# update_base_sass (sassdir confdir fsass fconf)
    [ $opt_verbose -gt 0 ] && echo "Update $1/$3 by $2/$4 ..."
    write_def_conf $2
    run_traced "cd $2"
    run_traced "link_cfg $4 default.def"
    run_traced "cd $1"
    local fsrc=$3
    if [ ! -f "$fsrc" ]; then
      echo "No file $3 found for skin!"
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
    ctr=10  #debug
    while IFS= read -r line; do
      [ $ctr -eq 0 ] && break
      ((ctr--)) #debug
      if [[ $line =~ ^\$[a-zA-Z0-9_-]+[[:space:]]*: ]]; then
        param=$(echo $line|grep --color=never -Eo "[a-zA-Z0-9_-]+"|head -n1)
        param=CSS_${param//-/_}
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
    done < "$fsrc"
    if [ ! -f Makefile ]; then
      echo "$opt_fcss: $opt_fsass" > Makefile
      echo -e "\tsass --trace -t expanded $opt_fsass $opt_fcss" >> Makefile
    fi
    if [ $opt_force -ne 0 ] || $(diff -q $ftmp $fsrc &>/dev/null); then
      if [ $opt_diff -ne 0 ]; then
        echo "diff -y --suppress-common-line $opt_fsass $ftmp"
        diff -y --suppress-common-line $opt_fsass $ftmp
      fi
      run_traced "cp -f $fsrc $fsrc.bak"
      run_traced "mv -f $ftmp $opt_fsrc"
      run_traced "sass --trace -t expanded $opt_fsass $opt_fcss"
      run_traced "chown odoo:odoo $opt_fsass $opt_fcss $fsrc.bak"
      svname=$(get_odoo_service_name $odoo_vid)
      run_traced "sudo systemctl restart $svname"
    else
      [ $opt_verbose -gt 0 ] && echo "No skin changed"
      [ ${opt_dry_run:-0} -eq 0 ] && rm -f $fntmp
    fi
}

update_skin() {
# update_skin (theme_dirs odoo_vid webdir sel_theme)
    restart_req=0
    local f
    local webdir=$3
    local res=$(list_themes_n_skin "$@")
    for f in favicon.ico logo.png logo2.png nologo.png; do
      [ -f $res/$f ] && cp_grf_file "$res" "$f"
    done
    for f in icon.png avatar.png; do
      [ -f $res/$f ] && cp_icon_file "$res" "$f"
    done
    for f in main_partner-image.png; do
      [ -f $res/$f ] && cp_demo_grf_file "$res" "$f"
    done
    update_base_sass $opt_sassd $res $opt_fsass skin_colors.def
    res=$(findpkg res_company.py "$odoo_root/odoo/addons/base/res $odoo_root/openerp/addons/base/res  /opt/odoo/$odoo_vid/server/openerp/addons/base/res")
    if [ -n "$res" ]; then
      run_traced "sed -e \"s|>generated by [^\ ]\+<|>generated by Zeroincombenze®<|1\" -i $res"
    fi
    [ ${opt_dry_run:-0} -eq 0 ] && echo "$4">$webdir/static/current_skin.txt
    if [ $restart_req -ne 0 -a $test_mode -eq 0 ]; then
      svname=$(get_odoo_service_name $odoo_vid)
      run_traced "sudo systemctl restart $svname"
    fi
    return
}


OPTOPTS=(h        c        D        d          f         i         I         l        m         n            q           s           S         T         V           v           x)
OPTDEST=(opt_help opt_conf opt_diff opt_webdir opt_force opt_icond opt_demod opt_list opt_multi opt_dry_run  opt_verbose opt_fsass   opt_sassd test_mode opt_version opt_verbose opt_xml)
OPTACTI=("+"      "="      1        "="        1         "="       ""        1        1         1            0           "="         "="       1         "*"         "+"         "=")
OPTDEFL=(1        ""       0        ""         0         ""        ""        0        -1        0            -1          "base.sass" ""        0         ""          -1          "base.xml")
OPTMETA=("help"   "file"   ""       "dir"      ""        "dir"     "dir"     "list"   ""        "do nothing" "quit"      "file"      "dir"     "test"    "version"   "verbose"   "file")
OPTHELP=("this help"\
 "configuration file (def .travis.conf)"\
 "show diff (implies dry-run)"\
 "odoo web dir (def. /opt/odoo/{odoo_fver}/addons/web/static/src/css)"\
 "force generation of css file"\
 "odoo icon dir (def. /opt/odoo/{odoo_fver}/(openerp|odoo)/addons/base/static/description)"\
 "odoo demo grf dir (def. /opt/odoo/{odoo_fver}/(openerp|odoo)/addons/base/static/src/img)"\
 "list themes"\
 "multi-version odoo environment"\
 "do nothing (dry-run)"\
 "silent mode"\
 "target sass file (def=base.sass)"\
 "odoo css dir (def. /opt/odoo/{odoo_fver}/(openerp|odoo)/addons/base/static/src/css)"\
 "test mode (implies dry-run)"\
 "show version"\
 "verbose mode"\
 "target xml file (def=base.xml)")
OPTARGS=(odoo_vid sel_skin)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Manage odoo themes (8.0+) & skin (all versions)"\
  "(C) 2015-2019 by zeroincombenze®\nhttp://wiki.zeroincombenze.org/en/Odoo\nAuthor: antoniomaria.vigliotti@gmail.com"
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
odoo_root=$(build_odoo_param ROOT $odoo_vid)
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
if [ "${opt_fsass: -5}" != ".sass" ]; then
  opt_fsass=$opt_fsass.sass
fi
if [ -z "$opt_webdir" ]; then
  if [ $test_mode -ne 0 ]; then
    opt_webdir=$TESTDIR/odoo/addons/web/static/src/css
  else
    xml=$(findpkg $opt_xml "$odoo_root/addons/web/static/src/xml $odoo_root/website $odoo_root")
    if [ -n "$xml" ]; then
      opt_webdir=$(dirname $xml)
    fi
  fi
fi
if [ -z "$opt_webdir" ]; then
  echo "No valid skin (File $opt_xml not found)!"
  exit 1
fi
if [ -z "$opt_icond" ]; then
  if [ $test_mode -ne 0 ]; then
    opt_icond=$TESTDIR/odoo/addons/odoo/base/static/src/img
  else
    ico=$(findpkg icon.png "$odoo_root/odoo/addons/base/static/src/img $odoo_root/odoo/addons/base/static/description $odoo_root/openerp/addons/base/static/src/img $odoo_root/openerp/addons/base/static/description /opt/odoo/$odoo_vid/server/openerp/addons/base/static/src/img")
    if [ -n "$ico" ]; then
      opt_icond=$(dirname $ico)
    fi
  fi
fi
if [ -z "$opt_icond" ]; then
  echo "No valid skin (Icon directory not found)!"
  exit 1
fi
if [ -z "$opt_demod" -a $odoo_ver -gt 7 ]; then
  if [ $test_mode -ne 0 ]; then
    opt_demod=$TESTDIR/odoo/addons/odoo/base/static/src/img
  else
    grf=$(findpkg main_partner-image.png "$odoo_root/odoo/addons/base/static/img $odoo_root/odoo/addons/base/static/src/img $odoo_root/openerp/addons/base/static/src/img $odoo_root/openerp/addons/base/static/img $odoo_root/server/openerp/addons/base/static/src/img")
    if [ -n "$grf" ]; then
      opt_demod=$(dirname $grf)
    fi
  fi
fi
if [ -z "$opt_demod" -a $odoo_ver -gt 7 ]; then
  echo "No valid skin (Demo graphical directory not found)!"
  exit 1
fi
if [ -z "$opt_sassd" ]; then
  if [ $test_mode -ne 0 ]; then
    opt_sassd=$TESTDIR/odoo/addons/odoo/base/static/src/img
  elif [ $odoo_ver -ge 10 ]; then
    [ "$opt_fsass" == "base.sass" ] && opt_fsass=description.sass
    css=$(findpkg $opt_fsass "$odoo_root/odoo/addons/base/static/src/css")
    if [ -n "$css" ]; then
      opt_sassd=$(dirname $css)
    fi
  else
    css=$(findpkg $opt_fsass "$opt_webdir/../css $odoo_root/website")
    if [ -n "$css" ]; then
      opt_sassd=$(dirname $css)
    fi
  fi
fi
if [ -z "$opt_sassd" -a $odoo_ver -gt 6 ]; then
  echo "No valid skin (Sass/css directory not found)!"
  exit 1
fi

opt_fcss=${opt_fsass:0: -5}.css
opt_webdir=$(readlink -f $opt_webdir/../../..)
if [ $opt_list -ne 0 ]; then
  list_themes_n_skin "$theme_dirs" "$odoo_vid" "$opt_webdir"
else
  update_skin "$theme_dirs" "$odoo_vid" "$opt_webdir" "$sel_skin"
fi
