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

__version__=0.3.5.7


rmdir_if_exists() {
#rmdir_if_exists (RPTNAME odoo_vid new_vid)
#export DSTPATH
      local RPTNAME=$1
      local odoo_vid=$2
      local odoo_fver=$(build_odoo_param FULLVER "$odoo_vid")
      local new_vid=$3
      local DSTPATH=$(build_odoo_param HOME $odoo_vid "$RPTNAME")
      local sts
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
        git status -s &>/dev/null
        sts=$?
        if [ $sts -eq 0 -a "$new_vid" == "$odoo_vid" ]; then
          if [ "$DSTPATH" != "$PWD" ]; then
            run_traced "cd $DSTPATH"
          fi
          run_traced "git push origin --delete $odoo_fver"
          if [ "$CWD" != "$PWD" ]; then
            run_traced "cd $CWD"
          fi
        fi
        run_traced "rm -fR $DSTPATH"
      fi
}

set_remote_info() {
#set_remote_info (RPTNAME odoo_vid pkg_URL odoo_org)
    local RPTNAME=$1
    local odoo_vid=$2
    local odoo_fver=$(build_odoo_param FULLVER "$odoo_vid")
    local pkg_URL=$3
    local odoo_org=$4
    local UPSTREAM=$(build_odoo_param UPSTREAM $odoo_vid $RPTNAME $odoo_org)
    local rval
    if [ "$(build_odoo_param VCS $odoo_vid)" == "git" ]; then
      rval=$(build_odoo_param RUPSTREAM $odoo_vid)
      if [[ ! "$rval" == "$UPSTREAM" ]]; then
        [[ -n "$rval" ]] && run_traced "git remote remove upstream"
        [[ -n "$UPSTREAM" ]] && run_traced "git remote add upstream $UPSTREAM"
      fi
      rval=$(build_odoo_param RORIGIN $odoo_vid)
      if [[ ! "$rval" == "$pkg_URL" ]]; then
        [[ -n "$rval" ]] && run_traced "git remote remove origin"
        [[ -n "$pkg_URL" ]] && run_traced "git remote add origin $pkg_URL"
      fi 
    else
      echo "No git repositoy $RPTNAME!"
    fi
}

wep_other_branches() {
#wep_other_branches(odoo_fver)
    local sts v x lne PARSE
    git status -s &>/dev/null
    sts=$?
    if [ $sts -eq 0 ]; then
      x=$(build_odoo_param RORIGIN $1)
      if [ "${x:0:15}" == "git@github.com:" ]; then
        git remote show origin 2>/dev/null> $TMPFILE
        PARSE=0
        while read -r lne r || [ -n "$lne" ]; do
          if [[ "$lne" =~ Remote[[:space:]]branches ]]; then
            PARSE=1
          elif [[ "$lne" =~  Local ]]; then
            PARSE=0
          elif [ $PARSE -gt 0 ]; then
            lne="$(echo $lne)"
            IFS=" " read v x <<< "$lne"
            if [[ ! $v =~ (6.1|7.0|8.0|9.0|10.0|11.0) ]] ; then
              run_traced "git push origin --delete $v"
            fi
          fi
        done < $TMPFILE
      fi
      for v in $(git branch|grep -Eo [0-9.]+); do
        if [[ -n "$v" && -n "$1" &&  ! "$v" == "$1" ]] ; then
          run_traced "git branch -D $v"
        fi
      done
    fi
}

auto_add_files() {
#auto_add_files(odoo_fver)
     git status 2>/dev/null> $TMPFILE
     PARSE=0
     while IFS= read -r lne || [ -n "$lne" ]; do
     if [[ "$lne" =~ "# Untracked files:" ]]; then
       PARSE=1
     elif [ $PARSE -ne 0 ]; then
       if [[ $lne =~ (LICENSE|README\.md|README.rst) ]]; then
         lne=$(echo ${lne:1})
         run_traced "git add $lne"
       fi
     fi
     done < $TMPFILE
}

commit_files() {
#commmit_files(odoo_fver) {
    local odoo_fver=$1
    local x=$(build_odoo_param RORIGIN $1)
    if [ "${x:0:15}" == "git@github.com:" ]; then
      # run_traced "git remote update"
      run_traced "git checkout -b $odoo_fver origin/$odoo_fver"
      run_traced "git format-patch --stdout origin/$odoo_fver -- $PWD | git am -3"
      # run_traced "git branch $odoo_fver -D"
      run_traced "git push origin $odoo_fver"
    fi
}


OPTOPTS=(h        b          c        L        m          n            O         q           r            V           v           y       1)
OPTDEST=(opt_help opt_branch opt_conf opt_link opt_multi  opt_dry_run  opt_org   opt_verbose opt_updrmt opt_version opt_verbose opt_yes opt_one)
OPTACTI=(1        "="        "="      1        1          1            "="       0           1          "*>"        "+"         1       1)
OPTDEFL=(0        ""         ""       0        0          0            "zero"    -1          0          ""          -1          0       0)
OPTMETA=("help"   "branch"   "file"   ""       ""         "do nothing" "git-org" "verbose"   ""         "version"   "verbose"   ""      "")
OPTHELP=("this help"\
 "new branch (new_odoo_ver) to create"\
 "configuration file (def .travis.conf)"\
 "create symbolic link rather copy files (if new_odoo_ver supplied)"\
 "multi-version odoo environment"\
 "do nothing (dry-run)"\
 "git organization, one of oca oia[-git|-http] zero[-git|-http] (def zero)"\
 "silent mode"\
 "do just update remote info (if no new_odoo_ver supplied)"\
 "show version"\
 "verbose mode"\
 "assume yes"\
 "if clone depth=1")
OPTARGS=(git_repo odoo_vid new_odoo_vid)

parseoptargs "$@"
if [ "$opt_version" ]; then
  echo "$__version__"
  exit $STS_SUCCESS
fi
if [ -z "$git_repo" ]; then
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
odoo_ver=$(build_odoo_param MAJVER $odoo_fver)
pkg_URL=$git_repo
RPTNAME=$(basename $git_repo)
if [ "${RPTNAME: -4}" == ".git" ]; then
  RPTNAME=${RPTNAME:0: -4}
fi
if [ "$pkg_URL" == "$RPTNAME/" ]; then
  RPTNAME=${RPTNAME:0: -1}
fi
if [ $opt_verbose -gt 0 ]; then
  if [ $opt_multi -ne 0 ]; then
    echo "Manage Odoo multi-version environment"
  else
    echo "Manage single Odoo version environment"
  fi
fi
odoo_root=$(build_odoo_param ROOT $odoo_vid "OCB")
if [ -z "$new_odoo_vid" ]; then
  new_odoo_fver=$odoo_fver
  if [ "$pkg_URL" == "$RPTNAME" ]; then
    pkg_URL=$(build_odoo_param GIT_URL $odoo_fver $RPTNAME $opt_org)
  fi
  DSTPATH=$(build_odoo_param HOME $odoo_vid "$RPTNAME")
  if [ $opt_updrmt -eq 0 ]; then
    rmdir_if_exists $RPTNAME $odoo_vid ""
    git_opts="-b $odoo_fver"
    if [ $opt_one -gt 0 ]; then
      x="--depth 1 --single-branch"
    else
      x=$(build_odoo_param GIT_OPTS $odoo_vid $RPTNAME $opt_org)
    fi
    if [ -n "$x" ]; then
      git_opts="$git_opts $x"
    fi
    pardir=$(build_odoo_param PARENTDIR $odoo_vid "$RPTNAME")
    if [ "$PWD" != "$pardir" ]; then
      run_traced "cd $pardir"
    fi
    pkgdir=$(basename $DSTPATH)
    run_traced "git clone $pkg_URL $pkgdir/ $git_opts"
    # run_traced "chown -R odoo:odoo $DSTPATH"
  fi
  if [ "$DSTPATH" != "$PWD" ]; then
    run_traced "cd $DSTPATH"
  fi
  if [ "$RPTNAME" == "OCB" ]; then
    discover_multi
    cfgfn=$(build_odoo_param CONFN "$odoo_vid")
    if [ ! -f "$cfgfn" ]; then
      odoo_bin=$(build_odoo_param BIN "$odoo_vid" "search")
      [ -f ~/.odoorc ] && run_traced "rm -f  ~/.odoorc"
      [ -f ~/.openerp_serverrc ] && run_traced "rm -f  ~/.openerp_serverrc"
      user=$(build_odoo_param USER "$odoo_vid")
      flog=$(build_odoo_param FLOG "$odoo_vid")
      fpid=$(build_odoo_param FPID "$odoo_vid")
      rport=$(build_odoo_param RPCPORT "$odoo_vid")
      if [ $odoo_ver -ge 7 ]; then
        pdir=$(build_odoo_param DDIR "$odoo_vid")
        if [ ! -d $pdir ]; then
          run_traced "mkdir -p $pdir"
          # run_traced "chown odoo:odoo $pdir"
        fi
        pdir="-D $pdir"
      fi
      run_traced "$odoo_bin -r $user --logfile=$flog --pidfile=$fpid --xmlrpc-port=$rport $pdir -s --stop-after-init"
      if [ -f ~/.openerp_serverrc ]; then
        run_traced "mv ~/.openerp_serverrc $cfgfn"
      elif [ -f ~/.odoorc ]; then
        run_traced "mv ~/.odoorc $cfgfn"
      fi
      run_traced "chown odoo:odoo $cfgfn"
    fi
  fi
else
  if [ "$odoo_vid" == "$new_odoo_vid" ]; then
    echo "Same source and target version"
    exit 1
  fi
  SRCPATH=$(build_odoo_param HOME $odoo_vid "$git_repo")
  DSTPATH=$(build_odoo_param HOME $new_odoo_vid "$git_repo")
  if [ "$SRCPATH" == "$DSTPATH" ]; then
    echo "Same source and target version"
    exit 1
  fi
  new_odoo_fver=$(build_odoo_param FULLVER "$new_odoo_vid")
  if [ "$pkg_URL" == "$RPTNAME" ]; then
    pkg_URL=$(build_odoo_param GIT_URL $new_odoo_fver $RPTNAME $opt_org)
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
  if [ "$DSTPATH" != "$PWD" ]; then
    run_traced "cd $DSTPATH"
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
  #   wep_other_branches
  # fi
  # run_traced "cd $HOME/$new_odoo_vid"
fi
if [ -z "$new_odoo_vid" ]; then
  new_odoo_vid=$odoo_vid
fi
set_remote_info "$RPTNAME" "$new_odoo_vid" "$pkg_URL" "$opt_org"
if [ $opt_updrmt -eq 0 ]; then
  auto_add_files "$new_odoo_fver"
  commit_files "$new_odoo_fver"
  wep_other_branches "$new_odoo_fver"
fi
is_submodule=$(build_odoo_param VCS $new_odoo_vid)
[ -n "$is_submodule" ] && git_orgnm=$(build_odoo_param RORIGIN $new_odoo_vid) || git_orgnm=
[ -n "$git_orgnm" ] && git_orgnm=$(dirname $git_orgnm)
if [ "$odoo_root" != "$PWD" ]; then
  run_traced "cd $odoo_root"
fi
if [ "$RPTNAME" != "OCB" -a -n "$is_submodule" ]; then
  root_orgnm=$(build_odoo_param RORIGIN $new_odoo_vid)
  [ -n "$root_orgnm" ] && root_orgnm=$(dirname $root_orgnm)
  if [ -n "$root_orgnm" -a "$root_orgnm" == "$git_orgnm" ]; then
    x=$(git submodule status 2>/dev/null|grep $RPTNAME)
    if [ -z "$x" ]; then
      run_traced "git submodule add -f $pkg_URL $RPTNAME/"
    fi
  else
    echo "Origin '$git_orgnm' of '$RPTNAME' does not match origin '$root_orgnm'!"
  fi
fi
if [ -z "$(grep "$RPTNAME/" .gitignore 2>/dev/null)" ]; then
   run_traced "echo "$RPTNAME/">>.gitignore"
fi
cfgfn=$(build_odoo_param CONFN "$new_odoo_vid")
if [ "$RPTNAME" == "OCB" ]; then
  DSTPATH="$DSTPATH/addons"
fi
[[ ! $(grep "^addons_path *= .*$DSTPATH" $cfgfn) ]] && run_traced "sed -ie \"s|^addons_path *=.*|&,$DSTPATH|\" $cfgfn"
rm -f $TMPFILE
exit 0
