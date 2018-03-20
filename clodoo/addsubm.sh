#! /bin/bash
# -*- coding: utf-8 -*-
#! /bin/bash
#
# Add odoo sub module into local repository
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2018 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYTHONPATH=$(echo -e "import sys\nprint str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1]"|python)
for d in $TDIR $TDIR/.. ${PYTHONPATH//:/ } /etc; do
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
ODOOLIBDIR=$(findpkg odoorc "$TDIR $TDIR/.. ${PYTHONPATH//:/ } . .. $HOME/tools/clodoo $HOME/dev" "clodoo")
if [ -z "$ODOOLIBDIR" ]; then
  echo "Library file odoorc not found!"
  exit 2
fi
. $ODOOLIBDIR
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
RUNDIR=$(readlink -e $TESTDIR/..)

__version__=0.3.4.12


build_pkgurl() {
# build_pkgurl(pkgname zero|oca URL|UPSTREAM|RPT|OPTS|ASM odoo_ver)
    local MODNAME=$1
    local RPT=$2
    local ITEM=$3
    local odoo_ver=$4
    if [ "$MODNAME" == "openerp_gantt_chart_modification" ]; then
      local ODOO_RPT="https://github.com/acespritech"
      local ODOO_UPSTREAM=
      local GIT_OPTS="--depth 1 --single-branch"
      local OPTS_ASM="-1"
    elif [ "$MODNAME" == "l10n-italy-supplemental" ]; then
      if [ "$RPT" == "zero-http" ]; then
        local ODOO_RPT="https://github.com/zeroincombenze"
        local GIT_OPTS="--depth 1 --single-branch"
        local OPTS_ASM="-1"
      else
        local ODOO_RPT="git@github.com:zeroincombenze"
        local GIT_OPTS=""
        local OPTS_ASM=
      fi
      local ODOO_UPSTREAM=
    elif [ "$RPT" == "oca" ]; then
      local ODOO_RPT="https://github.com/OCA"
      local ODOO_UPSTREAM=
      local GIT_OPTS="--depth 1 --single-branch"
      local OPTS_ASM="-1"
    elif [ "$RPT" == "zero" -o "$RPT" == "zeroincombenze" -o "$RPT" == "zero-git" ]; then
      local ODOO_RPT="git@github.com:zeroincombenze"
      local ODOO_UPSTREAM="https://github.com/OCA"
      local GIT_OPTS=""
      local OPTS_ASM=""
    elif [ "$RPT" == "zero-http" ]; then
      local ODOO_RPT="https://github.com/zeroincombenze"
      local ODOO_UPSTREAM="https://github.com/OCA"
      local GIT_OPTS="--depth 1 --single-branch"
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
      echo "$GIT_OPTS"
    elif [ "$ITEM" == "ASM" ]; then
      echo "$OPTS_ASM"
    else
      echo ""
    fi
}

rmdir_if_exists() {
#rmdir_if_exists (MODNAME odoo_vid new_vid)
#export DSTPATH
      local MODNAME=$1
      local odoo_vid=$2
      local odoo_fver=$(build_odoo_param FULLVER "$odoo_vid")
      local new_vid=$3
      local DSTPATH=$(build_odoo_param HOME $odoo_vid "$MODNAME")
      if [ -d $DSTPATH ]; then
        echo "Repository $DSTPATH of $odoo_fver Odoo already exists"
        if [ $opt_yes -gt 0 -o $opt_dry_run -gt 0 ]; then
          a=y
        else
          read -p "confirm action (y/n)?" a
        fi
        if [ "$a" != "y" ]; then
          exit 1
        fi
        local CWD=$PWD
        if [ "$new_vid" == "$odoo_vid" ]; then
          run_traced "cd $DSTPATH"
          run_traced "git push origin --delete $odoo_fver"
          run_traced "cd $CWD"
        fi
        run_traced "rm -fR $DSTPATH"
      fi
}

set_remote_info() {
#set_remote_info (MODNAME odoo_vid pkg_URL)
    local MODNAME=$1
    local odoo_vid=$2
    local odoo_fver=$(build_odoo_param FULLVER "$odoo_vid")
    local pkg_URL=$3
    local UPSTREAM=$(build_odoo_param UPSTREAM $odoo_vid)
    local rval
    rval=$(git remote -v 2>/dev/null|grep upstream|head -n1|awk '{ print $2}')
    if [ -n "$rval" ]; then
      run_traced "git remote remove upstream"
    fi
    if [ -n "$UPSTREAM" ]; then
      run_traced "git remote add upstream $UPSTREAM"
    fi
    rval=$(git remote -v 2>/dev/null|grep origin|head -n1|awk '{ print $2}')
    if [ -n "$rval" ]; then
      run_traced "git remote remove origin"
    fi
    run_traced "git remote add origin $pkg_URL"
}

wep_remote_branch() {
    git remote show origin 2>/dev/null> $TMPFILE
    PARSE=0
    while read -r line r || [ -n "$line" ]; do
      if [[ "$line" =~ Remote[[:space:]]branches ]]; then
        PARSE=1
      elif [[ "$line" =~  Local ]]; then
        PARSE=0
      elif [ $PARSE -gt 0 ]; then
        line="$(echo $line)"
        IFS=" " read v x <<< "$line"
        if [[ ! $v =~ (6.1|7.0|8.0|9.0|10.0|11.0) ]] ; then
          run_traced "git push origin --delete $v"
        fi
      fi
    done < $TMPFILE
}

OPTOPTS=(h        b          c        L        m          n            q           r          R            V           v           y       1)
OPTDEST=(opt_help opt_branch opt_conf opt_link opt_multi  opt_dry_run  opt_verbose opt_updrmt opt_rpt      opt_version opt_verbose opt_yes opt_one)
OPTACTI=(1        "="        "="      1        1          1            0           1          "="          "*>"        "+"         1       1)
OPTDEFL=(0        ""         ""       0        0          0            -1          0          "zero"       ""          -1          0       0)
OPTMETA=("help"   "branch"   "file"   ""       ""         "do nothing" "verbose"   ""         "repository" "version"   "verbose"   ""      "")
OPTHELP=("this help"\
 "new branch (new_odoo_ver) to create"\
 "configuration file (def .travis.conf)"\
 "create symbolic link rather copy files (if new_odoo_ver supplied)"\
 "multi-version odoo environment"\
 "do nothing (dry-run)"\
 "silent mode"\
 "do just update remote info (if no new_odoo_ver supplied)"\
 "repository name, one of oca zero-git zero-http (def zero-git)"\
 "show version"\
 "verbose mode"\
 "assume yes"\
 "if clone depth=1")
OPTARGS=(moduleid odoo_vid new_odoo_vid)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
if [ -z "$moduleid" ]; then
  opt_help=1
elif [ -z "$odoo_vid" ]; then
  opt_help=1
fi
if [ $opt_help -gt 0 ]; then
  print_help "Add oddo sub module into local repository"\
  "(C) 2015-2018 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit $STS_SUCCESS
fi
if [ $opt_verbose -eq -1 ]; then
  opt_verbose=1
fi
if [ -n "$opt_branch" ]; then
  if [ -z "$new_odoo_vid" ]; then
    new_odoo_vid=$opt_branch
  elif [ -n "$new_odoo_vid" ]; then
    echo "Invalid parameters"
    echo "You cannot declare new branch with -b option switch and with 3.th parameter"
    exit 1
  fi
fi

discover_multi
TMPFILE=$HOME/tmp_$$.out
odoo_fver=$(build_odoo_param FULLVER "$odoo_vid")
pkg_URL=$moduleid
MODNAME=$(basename $moduleid)
if [ "${MODNAME: -4}" == ".git" ]; then
  MODNAME=${MODNAME:0: -4}
fi
if [ "$pkg_URL" == "$MODNAME/" ]; then
  MODNAME=${MODNAME:0: -1}
fi
odoo_root=$(build_odoo_param ROOT $odoo_vid "OCB")
run_traced "cd $odoo_root"
if [ -z "$new_odoo_vid" ]; then
  new_odoo_fver=$odoo_fver
  if [ "$pkg_URL" == "$MODNAME" ]; then
    pkg_URL=$(build_odoo_param GIT_URL $odoo_fver $MODNAME $opt_rpt)
    git_prot=$(build_odoo_param GIT_PROT $odoo_fver $MODNAME $opt_rpt)
  else
    if [ "${pkg_URL:0:15}" == "git@github.com:" ]; then
      git_prot="git"
    else
      git_prot="https"
    fi
  fi
  if [ $opt_updrmt -eq 0 ]; then
    rmdir_if_exists $MODNAME $odoo_vid ""
    git_opts="-b $odoo_fver"
    if [ $opt_one -gt 0 ]; then
      x="--depth 1 --single-branch"
    else
      x=$(build_odoo_param GIT_OPTS $odoo_vid $MODNAME $opt_rpt)
    fi
    if [ -n "$x" ]; then
      git_opts="$git_opts $x"
    fi
    run_traced "git clone $pkg_URL $MODNAME/ $git_opts"
  fi
  DSTPATH=$(build_odoo_param HOME $odoo_vid "$MODNAME")
  run_traced "cd $DSTPATH"
  set_remote_info $MODNAME $odoo_vid $pkg_URL
  if [ "$git_prot" == "git" ]; then
    wep_remote_branch
  fi
else
  if [ "$odoo_vid" == "$new_odoo_vid" ]; then
    echo "Same source and target version"
    exit 1
  fi
  SRCPATH=$(build_odoo_param HOME $odoo_vid "$moduleid")
  DSTPATH=$(build_odoo_param HOME $new_odoo_vid "$moduleid")
  if [ "$SRCPATH" == "$DSTPATH" ]; then
    echo "Same source and target version"
    exit 1
  fi
  new_odoo_fver=$(build_odoo_param FULLVER "$new_odoo_vid")
  if [ "$pkg_URL" == "$MODNAME" ]; then
    pkg_URL=$(build_odoo_param GIT_URL $new_odoo_fver $MODNAME $opt_rpt)
    git_prot=$(build_odoo_param GIT_PROT $new_odoo_fver $MODNAME $opt_rpt)
  else
    if [ "${pkg_URL:0:15}" == "git@github.com:" ]; then
      git_prot="git"
    else
      git_prot="https"
    fi
  fi
  DSTROOT=$(readlink -e $DSTPATH/..)
  if [ -z "$DSTROOT" ]; then
    echo "Cannot evaluate target root!"
    exit 1
  fi
  if [ -d "$DSTPATH" ]; then
    run_traced "rm -fR $DSTPATH"
  fi
  if [ $opt_link -eq 0 ]; then
    run_traced "cp -r $SRCPATH/ $DSTROOT"
  else
    run_traced "ln -s $SRCPATH/ $DSTROOT"
  fi
  run_traced "cd $DSTPATH"
  set_remote_info $MODNAME $new_odoo_vid $pkg_URL
  if [ "$git_prot" == "git" ]; then
    wep_remote_branch
  fi
  odoo_root=$(build_odoo_param ROOT $new_odoo_vid "OCB")
  # if [ "$new_odoo_fver" == "$new_odoo_vid" -a "${pkg_URL:0:15}" == "git@github.com:" ]; then
  #   run_traced "git remote update"
  # fi
  # if [ "$new_odoo_fver" == "$new_odoo_vid" -a "$odoo_vid" != "$new_odoo_vid" ]; then
  #   run_traced "git checkout -b $new_odoo_vid origin/$odoo_vid"
  #   run_traced "git format-patch --stdout origin/$odoo_vid -- $DSTPATH | git am -3"
  #   run_traced "git branch $odoo_vid -D"
  # fi
  # pkg_URL=$(git remote -v 2>/dev/null|grep origin|head -n1|awk '{ print $2}')
  # if [ "$new_odoo_fver" == "$new_odoo_vid" ]; then
  #   run_traced "git push origin $new_odoo_vid"
  #   wep_remote_branch
  # fi
  # run_traced "cd $HOME/$new_odoo_vid"
fi
run_traced "cd $odoo_root"
if [ "$MODNAME" != "OCB" ]; then
  x=$(git submodule status 2>/dev/null|grep $MODNAME)
  if [ -z "$x" ]; then
    run_traced "git submodule add -f $pkg_URL $MODNAME/"
  fi
  if [ -z "$(grep "$MODNAME/" .gitignore 2>/dev/null)" ]; then
    run_traced "echo "$MODNAME/">>.gitignore"
  fi
fi
if [ -z "$new_odoo_vid" ]; then
  new_odoo_vid=$odoo_vid
fi
cfgfn=$(build_odoo_param CONFN "$new_odoo_vid")
if [ -z "$(grep "^addons_path *=.*$MODNAME" $cfgfn 2>/dev/null)" ]; then
  run_traced "sed -i \"s|^addons_path *=.*|&,$DSTPATH|\" $cfgfn"
fi
rm -f $TMPFILE
exit 0
