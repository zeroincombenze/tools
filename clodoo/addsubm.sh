#! /bin/bash
# -*- coding: utf-8 -*-
#! /bin/bash
#
# Add odoo sub module into local repository
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2017 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
THIS=$(basename $0)
TDIR=$(readlink -f $(dirname $0))
for x in $TDIR $TDIR/.. $TDIR/../z0lib $TDIR/../../z0lib . .. /etc; do
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
TRAVISLIBDIR=$(findpkg travisrc "$TDIR $TDIR/.. $TDIR/../travis_emulator $TDIR/../../travis_emulator . .. $HOME/dev")
if [ -z "$TRAVISLIBDIR" ]; then
  echo "Library file travisrc not found!"
  exit 2
fi
. $TRAVISLIBDIR
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)

__version__=0.1.31


set_dstpath() {
#set_dstpath(modname ver)
    if [ "$1" == "OCB" ]; then
      local DSTPATH=$HOME/$2
    else
      local DSTPATH=$HOME/$2/$1
    fi
    echo "$DSTPATH"
}

build_pkgurl() {
# build_pkgurl(pkgname zero|oca URL|UPSTREAM|RPT|OPTS|ASM odoo_ver)
    local MODNAME=$1
    local RPT=$2
    local ITEM=$3
    local odoo_ver=$4
    if [ "$MODNAME" == "openerp_gantt_chart_modification" ]; then
      local ODOO_RPT="https://github.com/acespritech"
      local ODOO_UPSTREAM=
      local OPTS_GIT="--depth 1 --single-branch"
      local OPTS_ASM="-1"
    elif [ "$MODNAME" == "l10n-italy-supplemental" ]; then
      if [ "$RPT" == "zero-http" ]; then
        local ODOO_RPT="https://github.com/zeroincombenze"
        local OPTS_GIT="--depth 1 --single-branch"
        local OPTS_ASM="-1"
      else
        local ODOO_RPT="git@github.com:zeroincombenze"
        local OPTS_GIT=""
        local OPTS_ASM=
      fi
      local ODOO_UPSTREAM=
    elif [ "$RPT" == "oca" ]; then
      local ODOO_RPT="https://github.com/OCA"
      local ODOO_UPSTREAM=
      local OPTS_GIT="--depth 1 --single-branch"
      local OPTS_ASM="-1"
    elif [ "$RPT" == "zero" -o "$RPT" == "zeroincombenze" -o "$RPT" == "zero-git" ]; then
      local ODOO_RPT="git@github.com:zeroincombenze"
      local ODOO_UPSTREAM="https://github.com/OCA"
      local OPTS_GIT=""
      local OPTS_ASM=""
    elif [ "$RPT" == "zero-http" ]; then
      local ODOO_RPT="https://github.com/zeroincombenze"
      local ODOO_UPSTREAM="https://github.com/OCA"
      local OPTS_GIT="--depth 1 --single-branch"
      local OPTS_ASM="-1"
    else
      echo "Odoo repository is one of oca|zero|zero-http|zero-git"
      sts=1
      exit $sts
    fi
    if [ "$ITEM" == "RPT" ]; then
      echo "$ODOO_RPT"
    elif [ "$ITEM" == "URL" ]; then
      local pkg_URL="$ODOO_RPT/$MODNAME.git"
      echo "$pkg_URL"
    elif [ "$ITEM" == "UPSTREAM" ]; then
      if [ "$odoo_ver" == "6.1" ]; then
        ODOO_UPSTREAM=
      fi
      if [ -n "$ODOO_UPSTREAM" ]; then
        local pkg_URL="$ODOO_UPSTREAM/$MODNAME.git"
      else
        local pkg_URL=
      fi
      echo "$pkg_URL"
    elif [ "$ITEM" == "OPTS" ]; then
      echo "$OPTS_GIT"
    elif [ "$ITEM" == "ASM" ]; then
      echo "$OPTS_ASM"
    else
      echo ""
    fi
}

rmdir_if_exists() {
#rmdir_if_exists (MODNAME new_odoo_ver rq_oev)
#export DSTPATH
      local MODNAME=$1
      local new_odoo_ver=$2
      local rq_oev=$3
      DSTPATH=$(set_dstpath $MODNAME $new_odoo_ver)
      if [ -d $DSTPATH ]; then
        echo "Version $new_odoo_ver already exists"
        if [ $opt_yes -gt 0 -o $opt_dry_run -gt 0 ]; then
          a=y
        else
          read -p "confirm action (y/n)?" a
        fi
        if [ "$a" != "y" ]; then
          exit 1
        fi
        local CWD=$PWD
        if [ "$rq_oev" == "$new_odoo_ver" ]; then
          run_traced "cd $DSTPATH"
          run_traced "git push origin --delete $new_odoo_ver"
          run_traced "cd $CWD"
        fi
        run_traced "rm -fR $DSTPATH"
      fi
}

set_remote_info() {
#set_remote_info (MODNAME new_odoo_ver pkg_URL)
    local MODNAME=$1
    local new_odoo_ver=$2
    local pkg_URL=$3
    local DSTPATH=$(set_dstpath $MODNAME $new_odoo_ver)
    local UPSTREAM=$(build_pkgurl $MODNAME $opt_rpt UPSTREAM $new_odoo_ver)
    run_traced "cd $DSTPATH"
    local rval=$(git remote -v 2>/dev/null|grep upstream|head -n1|awk '{ print $2}')
    if [ -n "$rval" ]; then
      run_traced "git remote remove upstream"
    fi
    if [ -n "$UPSTREAM" ]; then
      run_traced "git remote add upstream $UPSTREAM"
    fi
    # pkg_URL="git@github.com:zeroincombenze/$MODNAME.git"
    local rval=$(git remote -v 2>/dev/null|grep origin|head -n1|awk '{ print $2}')
    if [ -n "$rval" ]; then
      run_traced "git remote remove origin"
    fi
    run_traced "git remote add origin $pkg_URL"
}

wep_remote_branch() {
    git remote show origin 2>/dev/null> $TMPFILE
    PARSE=0
    while IFS=⌂ read -r line r || [ -n "$line" ]; do
      if [[ "$line" =~ Remote[[:space:]]branches ]]; then
        PARSE=1
      elif [[ "$line" =~  Local ]]; then
        PARSE=0
      elif [ $PARSE -gt 0 ]; then
        line="$(echo $line)"
        IFS=" " read v x <<< "$line"
        if [[ $v =~ (6.1|7.0|8.0|9.0|10.0) ]] ; then
          :
        else
          run_traced "git push origin --delete $v"
        fi
      fi
    done < $TMPFILE
}

OPTOPTS=(h        b          c        L        n            q           r          R            V           v           y       1)
OPTDEST=(opt_help opt_branch opt_conf opt_link opt_dry_run  opt_verbose opt_updrmt opt_rpt      opt_version opt_verbose opt_yes opt_one)
OPTACTI=(1        "="        "="      1        1            0           1          "="          "*>"        "+"         1       1)
OPTDEFL=(0        ""         ""       0        0            -1          0          "zero-git"   ""          -1          0       0)
OPTMETA=("help"   "branch"   "file"   ""       "do nothing" "verbose"   ""         "repository" "version"   "verbose"   ""      "")
OPTHELP=("this help"\
 "new branch (new_odoo_ver) to create"\
 "configuration file (def .travis.conf)"\
 "create symbolic link rather copy files (if new_odoo_ver supplied)"\
 "do nothing (dry-run)"\
 "silent mode"\
 "do just update remote info (if no new_odoo_ver supplied)"\
 "repository name, one of oca zero-git zero-http (def zero-git)"\
 "show version"\
 "verbose mode"\
 "assume yes"\
 "if clone depth=1")
OPTARGS=(moduleid odoo_ver new_odoo_ver)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
if [ -z "$moduleid" ]; then
  opt_help=1
elif [ -z "$odoo_ver" ]; then
  opt_help=1
fi
if [ $opt_help -gt 0 ]; then
  print_help "Add oddo sub module into local repository"\
  "(C) 2015-2017 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi
if [ $opt_verbose -eq -1 ]; then
  opt_verbose=1
fi
if [ -n "$opt_branch" ]; then
  if [ -z "$new_odoo_ver" ]; then
    new_odoo_ver=$opt_branch
  elif [ -n "$new_odoo_ver" ]; then
    echo "Invalid parameters"
    echo "You cannot declare new branch with -b option switch and with 3.th parameter"
    exit 1
  fi
fi

TMPFILE=$HOME/tmp_$$.out
if [ -z "$new_odoo_ver" ]; then
  run_traced "cd $HOME/$odoo_ver"
  pkg_URL=$moduleid
  MODNAME=$(basename $moduleid)
  if [ "${MODNAME: -4}" == ".git" ]; then
    MODNAME=${MODNAME:0: -4}
  fi
  if [ "$pkg_URL" == "$MODNAME/" ]; then
    MODNAME=${MODNAME:0: -1}
  fi
  if [ "$pkg_URL" == "$MODNAME" ]; then
    pkg_URL=$(build_pkgurl $MODNAME $opt_rpt URL $odoo_ver)
  fi
  if [ $opt_updrmt -eq 0 ]; then
    rmdir_if_exists $MODNAME $odoo_ver ""
    git_opts="-b $odoo_ver"
    if [ $opt_one -gt 0 ]; then
      git_opts="$git_opts --single-branch --depth=1"
    else
      x=$(build_pkgurl $MODNAME $opt_rpt OPTS $odoo_ver)
      if [ -n "$x" ]; then
        git_opts="$git_opts $x"
      fi
    fi
    run_traced "git clone $pkg_URL $MODNAME/ $git_opts"
  else
    DSTPATH=$(set_dstpath $MODNAME $new_odoo_ver)
  fi
  set_remote_info $MODNAME $odoo_ver $pkg_URL
  if [ "${pkg_URL:0:15}" == "git@github.com:" ]; then
    wep_remote_branch
  fi
else
  if [[ $new_odoo_ver =~ (v7|6.1|7.0|8.0|9.0|10.0) ]] ; then
    :
  else
    echo "Invalid target version: must be v7 6.1 7.0 8.0 9.0 or 10.0"
    exit 1
  fi
  rq_oev=$(echo $new_odoo_ver|grep -Eo [0-9.]+)
  if [ "$rq_oev" == "7" ]; then rq_oev=7.0; fi
  if [ -d "$moduleid" ]; then
    SRCPATH=$moduleid
  elif [ -d ~/$odoo_ver/$moduleid ]; then
    SRCPATH=~/$odoo_ver/$moduleid
  # elif [ "${moduleid:0:23}" == "https://github.com/OCA/" ]; then
  else
    pkg_URL=$(build_pkgurl $MODNAME $opt_rpt UPSTREAM $odoo_ver)
    if [ -z "pkg_URL" ]; then
      pkg_URL=$(build_pkgurl $MODNAME $opt_rpt URL $odoo_ver)
    fi
    if [ -d ~/$new_odoo_ver ]; then
      run_traced "cd $HOME/$new_odoo_ver"
      MODNAME=$(basename $moduleid)
      if [ "${MODNAME: -4}" == ".git" ]; then
         MODNAME=${MODNAME:0: -4}
      fi
      rmdir_if_exists $MODNAME $new_odoo_ver $rq_oev
      if [ -n "$new_odoo_ver" -a "$rq_oev" == "$new_odoo_ver" ]; then
        git_opts="-b $odoo_ver"
        if [ $opt_one -gt 0 ]; then
          git_opts="$git_opts --single-branch --depth=1"
        else
          x=$(build_pkgurl $MODNAME $opt_rpt OPTS $new_odoo_ver)
          if [ -n "$x" ]; then
            git_opts="$git_opts $x"
          fi
        fi
        run_traced "git clone $pkg_URL $MODNAME/ $git_opts"
        set_remote_info $MODNAME $new_odoo_ver $pkg_URL
      fi
      SRCPATH=
    else
      echo "Directory ~/$new_odoo_ver not found"
      exit 1
    fi
  fi
  if [ -n "$SRCPATH" ]; then
    if [ "$odoo_ver" == "$new_odoo_ver" ]; then
      echo "Same source and target version"
      exit 1
    fi
    MODNAME=$(basename $SRCPATH)
    rmdir_if_exists $MODNAME $new_odoo_ver $rq_oev
    run_traced "cd $HOME/$new_odoo_ver"
    if [ $opt_link -eq 0 ]; then
      run_traced "cp -r $SRCPATH/ ./"
    else
      run_traced "ln -s $SRCPATH/ ./"
    fi
  fi
  run_traced "cd $DSTPATH"
  # if [ "$rq_oev" == "$new_odoo_ver" -a " ${MODNAME:0:10}" != "l10n-italy" ]; then
  if [ "$rq_oev" == "$new_odoo_ver" -a "${pkg_URL:0:15}" == "git@github.com:" ]; then
    run_traced "git remote update"
  fi
  if [ "$rq_oev" == "$new_odoo_ver" -a "$odoo_ver" != "$new_odoo_ver" ]; then
    run_traced "git checkout -b $new_odoo_ver origin/$odoo_ver"
    run_traced "git format-patch --stdout origin/$odoo_ver -- $DSTPATH | git am -3"
    run_traced "git branch $odoo_ver -D"
  fi
  pkg_URL=$(git remote -v 2>/dev/null|grep origin|head -n1|awk '{ print $2}')
  if [ "$rq_oev" == "$new_odoo_ver" ]; then
    run_traced "git push origin $new_odoo_ver"
    wep_remote_branch
  fi
  run_traced "cd $HOME/$new_odoo_ver"
fi
run_traced "cd $HOME/$odoo_ver"
if [ "$MODNAME" != "OCB" -a "$rq_oev" == "$new_odoo_ver" ]; then
  x=$(git submodule status 2>/dev/null|grep $MODNAME)
  if [ -z "$x" ]; then
    run_traced "git submodule add -f $pkg_URL $MODNAME/"
  fi
  if [ -z "$(grep "$MODNAME/" .gitignore 2>/dev/null)" ]; then
    run_traced "echo "$MODNAME/">>.gitignore"
  fi
fi
if [ -z "$new_odoo_ver" ]; then
  new_odoo_ver=$odoo_ver
fi
if [ "$new_odoo_ver" == "10.0" ]; then
  cfgfn=/etc/odoo/odoo10.conf
elif [ "$new_odoo_ver" == "v7" ]; then
  cfgfn=/etc/odoo/openerp-server.conf
else
  v=$(echo $new_odoo_ver|grep -Eo [0-9]+|head -n1)
  cfgfn=/etc/odoo/odoo${v}-server.conf
fi
if [ -z "$(grep "^addons_path *=.*$MODNAME" $cfgfn 2>/dev/null)" ]; then
  run_traced "sed -i \"s|^addons_path *=.*|&,$DSTPATH|\" $cfgfn"
fi
rm -f $TMPFILE
exit 0
