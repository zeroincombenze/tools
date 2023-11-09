#! /bin/bash
# -*- coding: utf-8 -*-
# Copy package files
# Tool for internal use
#
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2023 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# git report to origin
# git fetch origin , poi, git reset --hard origin/8.0-ddt-based-on-packaging-preparation_fa
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

__version__=2.0.12

# main
OPTOPTS=(h        C         c        D        F         f         n            O         o        P         p         q           R         S        u       V           v           W          w         -)
OPTDEST=(opt_help opt_cpush opt_conf opt_push opt_fetch opt_force opt_dry_run  opt_cpush opt_ids  opt_cpush opt_dpath opt_verbose opt_cpush opt_sts  opt_upd opt_version opt_verbose opt_whatis opt_cpush opt_sync)
OPTACTI=("+"      "*>"      "="      "*>"     "1>"      1         1            "*>"      "=>"     "*>"      "="       0           "*>"      "=>"     1       "*"         "+"         "=>"       "*>"      "1>")
OPTDEFL=(1        ""        ""       ""       0         0         0            ""        ""       ""        ""        0           ""        ""       0       ""          -1          ""         ""        0)
OPTMETA=("help"   "commit"  "file"   ""       "fetch"   ""        "do nothing" ""        "prj_id" "push"    "path"    "quiet"     "replace" "status" "upd"   "version"   "verbose"   "param"    "wep"     "sync")
OPTHELP=("this help"\
 "commit and push to production paths"\
 "configuration file"\
 "duplicate odoo to another version"
 "fetch from local git path"\
 "force copy (with -C -P)"\
 "do nothing (dry-run)"\
 "replace odoo to other dist path"\
 "push only external project ids (require -P)"\
 "push to external projects"\
 "declare local destination path"\
 "silent mode"\
 "replace to local git path"\
 "set development Status"\
 "do not update newer file (require -C -F -P or -R)"\
 "show version"\
 "verbose mode"\
 "whatis param value?"\
 "wep directory"\
 "refresh info for distribution")
OPTARGS=(InvalidParam InvalidParam2)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Copy package files"\
  "© 2015-2023 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi

opts_travis
conf_default
[[ $opt_verbose -gt 2 ]] && set -x
init_travis
# prepare_env_travis
sts=$STS_SUCCESS

[[ -n $LGITPATH && $PKGNAME == "tools" && $LGITPATH =~ "tools" ]] && LGITPATH=$(dirname $LGITPATH)
if [[ -n $opt_whatis ]]; then
  if [[ $opt_whatis =~ ^(LGITPATH|PKGNAME|PKGPATH|PRJNAME|PRJPATH|REPOSNAME|SETUP)$ ]]; then
    echo "${opt_whatis}=${!opt_whatis}"
  else
    echo "Unknown parame $opt_whatis!!"
  fi
  exit $STS_SUCCESS
fi

if [ $opt_dry_run -gt 0 ]; then
  if [ $opt_sync -gt 0 ]; then
    echo "$(basename $0) -n -- $PKGNAME $PRJNAME"
  elif [ "$opt_cpush" ]; then
    echo "$(basename $0) -n $opt_cpush -p \"$LGITPATH\" $PKGNAME $PRJNAME"
  elif [ $opt_fetch -gt 0 ]; then
    echo "$(basename $0) -n -f -p \"$LGITPATH\" $PKGNAME $PRJNAME"
  elif [ "$opt_sts" ]; then
    echo "$opt_sts"
  else
    echo "$(basename $0) -n -p \"$LGITPATH\" $PKGNAME $PRJNAME"
  fi
fi

if [[ $PRJNAME == "Odoo" ]]; then
    valid=0
    [[ -f "$PKGPATH/__manifest__.py" || -f "$PKGPATH/__openerp__.py" ]] && ((valid++))
    [[ -f "$PKGPATH/__init__.py" ]] && ((valid++))
    [[ -f "$PKGPATH/README.rst" || -f "$PKGPATH/README.md" ]] && ((valid++))
    if [[ $valid -lt 3 ]]; then
        echo "Invalid environment!!"
        exit 1
    fi
else
    valid=0
    [[ -f "$PKGPATH/setup.py" ]] && ((valid++))
    [[ -f "$PRJPATH/__init__.py" ]] && ((valid++))
    [[ -d "$PRJPATH/scripts" ]] && ((valid++))
    [[ $PKGNAME == "tools" && -x "$PKGPATH/install_tools.sh" ]] && ((valid++))
    [[ $PKGNAME == "tools" && -d "$PKGPATH/templates" ]] && ((valid++))
    if [[ $valid -lt 3 ]]; then
        echo "Invalid environment!!"
        exit 1
    fi
    LSETUP=$PKGPATH/setup.py
fi

if [ "$opt_cpush" == "-O" ]; then
  # Copy files from Odoo package to another Odoo distribution (same version)
  opts_common=
  [ $opt_dry_run -ne 0 ] && opts_common="${opts_common}n"
  [ ${opt_verbose:-0} -ne 0 ] && opts_common="${opts_common}v"
  [ -n "$opts_common" ] && opts_common="-${opts_common}"
  srcdir=$($READLINK -f .)
  [ "${srcdir: -1}" == "/" ] && srcdir=${srcdir:0: -1}
  tgtdir=$LGITPATH
  [ "${tgtdir: -1}" == "/" ] && tgtdir=${tgtdir:0: -1}
  if [ ! -d "$srcdir" ]; then
    echo "Invalid source dir $srcdir!"
    exit 1
  fi
  if [ -z "$tgtdir" -o ! -d "$tgtdir" ]; then
    echo "Invalid target dir $tgtdir!"
    exit 1
  fi
  if [ "$srcdir" == "$tgtdir" ]; then
    echo "Same source and target directory"
    exit
  fi
  pkg=$(build_odoo_param REPOS "$srcdir")
  cd $tgtdir
  [ -d ./setup ] && rm -fR ./setup
  if [ "$pkg" == "OCB" ]; then
    echo "Replicate OCB ..."
    valid=$(build_odoo_param OCB_SUBDIRS_RE)
    for d in $srcdir/* $srcdir/.travis.yml; do
      f=$(basename $d)
      if [ -d $srcdir/$f ]; then
        if [[ $f =~ $valid ]]; then
          [ $opt_verbose -gt 0 ] && echo "rsync $opts_common -abC --del --copy-links --exclude=*.log --exclude=*.bak --exclude=*.out --exclude=*.tmp --exclude=*.tracehis --exclude=*.tracehistory --exclude=*,cover --exclude=*.coverage --exclude=.cover/ --exclude=.coverage/ --exclude=*~ --exclude=*test*.pdf* --exclude=*tmp* --exclude=*tmp.** --exclude=*npm-debug.log.** --exclude=*.pyc --exclude=*.conf --exclude=build/ --exclude=dist/ --exclude=conf/ --exclude=filestore/ --exclude=.git/ --exclude=docs/ --exclude=html/ --exclude=latex/ --exclude=*.gz --exclude=*__old_** --exclude=*.gitrepname $srcdir/$f/ $tgtdir/$f/"
          rsync $opts_common -abC --del --copy-links --exclude=*.log --exclude=*.bak --exclude=*.out --exclude=*.tmp --exclude=*.tracehis --exclude=*.tracehistory --exclude=*,cover --exclude=*.coverage --exclude=.cover/ --exclude=.coverage/ --exclude=*~ --exclude=*test*.pdf* --exclude=*tmp* --exclude=*tmp.** --exclude=*npm-debug.log.** --exclude=*.pyc --exclude=*.conf --exclude=build/ --exclude=dist/ --exclude=conf/ --exclude=filestore/ --exclude=.git/ --exclude=docs/ --exclude=html/ --exclude=latex/ --exclude=*.gz --exclude=*__old_** --exclude=*.gitrepname $srcdir/$f/ $tgtdir/$f/
        fi
      else
        [ $opt_verbose -gt 0 ] && echo "rsync $opts_common -abC $srcdir/$f $tgtdir/"
        rsync $opts_common -abC $srcdir/$f $tgtdir/
      fi
    done
  else
    echo "Replicate $pkg ..."
    [ $opt_verbose -gt 0 ] && echo "rsync $opts_common -abC --del --copy-links --exclude=*.log --exclude=*.bak --exclude=*.out --exclude=*.tmp --exclude=*.tracehis --exclude=*.tracehistory --exclude=*,cover --exclude=*.coverage --exclude=.cover/ --exclude=.coverage/ --exclude=*~ --exclude=*test*.pdf* --exclude=*tmp* --exclude=*tmp.** --exclude=*npm-debug.log.** --exclude=*.pyc --exclude=*.conf --exclude=build/ --exclude=dist/ --exclude=conf/ --exclude=filestore/ --exclude=.git/ --exclude=docs/ --exclude=html/ --exclude=latex/ --exclude=*.gz --exclude=*__old_** --exclude=*.gitrepname $srcdir/ $tgtdir/"
    rsync $opts_common -abC --del --copy-links --exclude=*.log --exclude=*.bak --exclude=*.out --exclude=*.tmp --exclude=*.tracehis --exclude=*.tracehistory --exclude=*,cover --exclude=*.coverage --exclude=.cover/ --exclude=.coverage/ --exclude=*~ --exclude=*test*.pdf* --exclude=*tmp* --exclude=*tmp.** --exclude=*npm-debug.log.** --exclude=*.pyc --exclude=*.conf --exclude=build/ --exclude=dist/ --exclude=conf/ --exclude=filestore/ --exclude=.git/ --exclude=docs/ --exclude=html/ --exclude=latex/ --exclude=*.gz --exclude=*__old_** --exclude=*.gitrepname $srcdir/ $tgtdir/
    [ $opt_verbose -gt 0 ] && echo "cp $srcdir/.travis.yml $tgtdir/.travis.yml"
    cp $srcdir/.travis.yml $tgtdir/.travis.yml
  fi
  RORIGIN=$(build_odoo_param RORIGIN ".")
  gitorg=$(basename $(dirname $(echo $RORIGIN|awk -F: '{print $2}')))
  if [ "$gitorg" == "Odoo-Italia-Associazione" ]; then
    odoo_ver=$(build_odoo_param MAJVER ".")
    [ $opt_verbose -gt 0 ] && echo "odoo_skin.sh oia$odoo_ver oia -v"
    odoo_skin.sh oia$odoo_ver oia -v
    [ $opt_verbose -gt 0 ] && echo "$TDIR/please distribution oia $opts_dry_run -f"
    $TDIR/please distribution oia $opts_dry_run -f
    for f in $(find $tgtdir/ -type d -name 'egg-info'); do
      d=$(dirname $f)
      echo "\$ cd $d"
      cd $d
      [ -f README.md ] && rm -fR README.md
      run_traced "$TDIR/gen_readme.py -Goia"
      if [ $odoo_ver -ge 8 ]; then
        if [ -f __openerp__.py -o -f __manifest__.py ]; then
          [ ! -d ./static ] && mkdir -p ./static
          [ ! -d ./static/description ] && mkdir -p ./static/description
          run_traced "$TDIR/gen_readme.py -H -Goia"
        fi
      fi
    done
  fi
  exit 0
fi

if [ "$opt_cpush" == "-D" ]; then
  # Duplicate files from Odoo package to another Odoo version (same distribution)
  opts_common=
  [ $opt_dry_run -ne 0 ] && opts_common="${opts_common}n"
  [ ${opt_verbose:-0} -ne 0 ] && opts_common="${opts_common}v"
  [ -n "$opts_common" ] && opts_common="-${opts_common}"
  srcdir=$($READLINK -f .)
  [ "${srcdir: -1}" == "/" ] && srcdir=${srcdir:0: -1}
  tgtdir=$LGITPATH
  [ "${tgtdir: -1}" == "/" ] && tgtdir=${tgtdir:0: -1}
  if [ ! -d "$srcdir" ]; then
    echo "Invalid source dir $srcdir!"
    exit 1
  fi
  if [ -z "$tgtdir" ]; then
    echo "Invalid target dir $tgtdir!"
    exit 1
  elif [ ! -d "$tgtdir" ]; then
    if [ $opt_force -ne 0 ]; then
      run_traced "mkdir -p $tgtdir"
    else
      echo "Target dir $tgtdir does not exit!"
      exit 1
    fi
  fi
  if [ "$srcdir" == "$tgtdir" ]; then
    echo "Same source and target directory!"
    exit
  fi
  src_fver=$(build_odoo_param VERSION "$srcdir")
  src_ver=$(build_odoo_param MAJVER $src_fver)
  src_mfst=$(build_odoo_param MANIFEST $src_fver)
  tgtc_fver=$(build_odoo_param VERSION "$tgtdir")
  tgt_ver=$(build_odoo_param MAJVER $tgt_fver)
  tgt_mfst=$(build_odoo_param MANIFEST $tgt_fver)
  repository=$(build_odoo_param REPOS "$srcdir")
  module=$(build_odoo_param PKGNAME "$srcdir")
  [ ! -d /opt/odoo/$tgt_fver/__to_remove/ ] && mkdir -p /opt/odoo/$tgt_fver/__to_remove/
  [ -d /opt/odoo/$tgt_fver/__to_remove/$module/ ] && run_traced "rm -fR /opt/odoo/$tgt_fver/__to_remove/$module/"
  [ -d /opt/odoo/$tgt_fver/$repository/$module/ ] && run_traced "cp /opt/odoo/$tgt_fver/$repository/$module/ /opt/odoo/$tgt_fver/__to_remove/"
  run_traced "rsync -abuv /opt/odoo/$src_fver/$repository/$module/ /opt/odoo/$tgt_fver/$repository/$module/"
  if [ "$src_mfst" != "$tgt_mfst" ]; then
    run_traced "mv /opt/odoo/$tgt_fver/$repository/$module/$src_mfst /opt/odoo/$tgt_fver/$repository/$module/$tgt_mfst"
    run_traced "sed -e \"s/$src_ver\./$tgt_ver./\" -i /opt/odoo/$tgt_fver/$repository/$module/$tgt_mfst"
  fi
  if [ $src_ver -lt 10 -a $tgt_ver -ge 10 ]; then
    run_traced "sed -e \"s/AGPL-3/LGPL-3/\" -i /opt/odoo/$tgt_fver/$repository/$module/$tgt_mfst"
  elif [ $src_ver -ge 10 -a $tgt_ver -lt 10 ]; then
    run_traced "sed -e \"s/LGPL-3\./AGPL-3/\" -i /opt/odoo/$tgt_fver/$repository/$module/$tgt_mfst"
  fi
  for f in $(find /opt/odoo/$tgt_fver/$repository/$module/ -name '*.py'); do
    run_traced "$TDIR/topep8 -F $src_fver  -b $tgt_fver -ciaG -Coia,zero $f"
  done
  for f in $(find /opt/odoo/$tgt_fver/$repository/$module/ -name '*.xml'); do
    run_traced "$TDIR/topep8 -b $tgt_fver $f"
  done
  for f in $(find $tgtdir/ -type d -name 'egg-info'); do
    d=$(dirname $f)
    echo "\$ pushd $d"
    psuhd $d &>/dev/null
    [ -f README.md ] && rm -fR README.md
    run_traced "$TDIR/gen_readme.py -Goia"
    if [ $tgt_ver -ge 8 ]; then
      if [ -f __openerp__.py -o -f __manifest__.py ]; then
        [ ! -d ./static ] && mkdir -p ./static
        [ ! -d ./static/description ] && mkdir -p ./static/description
        run_traced "$TDIR/gen_readme.py -H -Gzero -lmodule"
      fi
    fi
  done
  exit 0
fi

if [[ $opt_cpush =~ ^(-C|-P) ]]; then
  robocopy_init "$PRJNAME" "$PKGNAME"
  f_done=0
  for ii in {1..9}; do
    [[ -z "$opt_ids" || $ii != $opt_ids ]] && continue
    declare x=tgt${ii}path
    declare y=tgt${ii}params
    declare tgtpath="$(get_cfg_value 0 $x)"
    declare tgtparm="$(get_cfg_value 0 $y)"
    if [[ -n "$tgtpath" ]]; then
      srcpath=$PKGPATH
      [[ -n $PKGPATH ]] || tgtpath="${tgtpath/pkgpath/prjpath}"
      [[ -n $PKGPATH ]] || srcpath="$PRJPATH"
      tgtpath=$(expand_path $tgtpath)
      declare z=tgt${ii}enable
      declare enabled="$(get_cfg_value 0 $z)"
      [[ ${enabled:-0} -eq 0 ]] && enabled=$opt_force
      if [[ ${enabled:-0} -eq 2 && "$opt_cpush" != "-C" ]]; then
        enabled=0;
      elif [[ ${enabled:-0} -eq 1 && "$opt_cpush" == "-C" ]]; then
        enabled=0;
      fi
      if [[ ${enabled:-0} -gt 0 ]]; then
        if [[ -n "$tgtparm" ]]; then
          declare $y="$(echo \"$tgtparm\"|sed 's:\\::g')"
          [[ $opt_verbose -gt 0 ]] && echo "$ robocopy \"$srcpath\" \"$tgtpath\" \"ssh $tgtparm\""
          robocopy "$srcpath" "$tgtpath" "ssh $tgtparm"
        else
          [[ $opt_verbose -gt 0 ]] && echo "$ robocopy \"$srcpath\" \"$tgtpath\" \"ssh\""
          robocopy "$srcpath" "$tgtpath" "ssh"
        fi
        f_done=1
        if [ "$opt_cpush" == "-C" ]; then
          break
        fi
      fi
    fi
  done
  if [[ $f_done -eq 0 ]]; then
    echo "No destination found in configuration file $DIST_CONF"
    echo "Nothing is done"
  fi
  exit $STS_SUCCESS
fi

# check for source dirs
check_4_travis
[[ "$PRJNAME" == "Odoo" ]] && echo "Invalid project Odoo!" && exit 1
[[ $PKGNAME != $PRJNAME ]] && echo "Warning: package name $PKGNAME and project name $PRJNAME are different!"
[[ $opt_sync -gt 0 ]] && exit $STS_SUCCESS

if [ "$opt_cpush" == "-w" ]; then
  clean_dirs "$PKGPATH"
  if [ "$PRJNAME" == "Odoo" ]; then
    cd $PKGPATH
  else
    cd $PKGPATH/$PKGNAME
  fi
  if [ "$PRJNAME" != "z0lib" ]; then
    if [ -f ./Makefile -a -f /opt/odoo/dev/Makefile ]; then
      rm -f ./Makefile
    fi
    if [ -f ./z0librc -a -f /etc/z0librc ]; then
      x=$(_install_z0librc -n)
      if [ -z "$x" ]; then
        rm -f ./z0librc
        ln -s /etc/z0librc ./
      fi
    fi
  elif [ "$PRJNAME" != "travis_emulator" ]; then
    if [ -d ./_travis -a -d /opt/odoo/dev/_travis ]; then
      rm -f ./_travis
    fi
  fi
  exit $STS_SUCCESS
fi

[[ ! -d $LGITPATH ]] && echo "Destination path $LGITPATH not found!" && exit $STS_FAILED
robocopy_init "$PRJNAME" "$PKGNAME"
if [[ $opt_fetch -eq 0 ]]; then
  [[ $PKGNAME != "tools" ]] && run_traced "cp $PKGPATH/setup.py $PRJPATH/scripts/setup.info"
  [[ -f $PRJPATH/setup.py && -f $PRJPATH/scripts/setup.info ]] &&  run_traced "rm -f $PRJPATH/setup.py"
  [[ -x $PRJPATH/replace.sh ]] && run_traced "$PRJPATH/replace.sh"
  [[ ! -x $PRJPATH/replace.sh ]] && robocopy "$PRJPATH" "$LGITPATH"
  if [[ $PKGNAME != "tools" ]]; then
    [[ -f $PKGPATH/setup.py ]] &&  run_traced "cp $PKGPATH/setup.py $LGITPATH/setup.py"
    [[ -f $PKGPATH/README.rst ]] &&  run_traced "cp $PKGPATH/README.rst $LGITPATH/README.rst"
    [[ -f "$PRJPATH/scripts/setup.info" ]] &&  run_traced "cp $PRJPATH/scripts/setup.info $LGITPATH/scripts/setup.info"
  fi
fi
exit $STS_SUCCESS

