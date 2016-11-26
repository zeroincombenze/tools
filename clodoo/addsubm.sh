#! /bin/bash
# -*- coding: utf-8 -*-
__version__=0.1.20
if [ -z "$1" -o -z "$2" ]; then
  echo "$0 git_URL odoo_ver"
  echo "$0 modulename|directory|gitrepository old_odoo_ver new_odoo_ver"
  exit 1
fi
# set -v
if [ -z "$3" ]; then
  echo "\$ cd ~/$2"
  cd ~/$2
  pkg_URL=$1
  MODNAME=$(basename $1)
  if [ "${MODNAME: -4}" == ".git" ]; then
    MODNAME=${MODNAME:0: -4}
  fi
  # git_opts="--single-branch --depth=1"
  git_opts="-b $2"
  echo "\$ git clone $pkg_URL $MODNAME/ $git_opts"
  git clone $pkg_URL $MODNAME/ $git_opts
else
  if [[ $3 =~ (7.0|8.0|9.0|10.0) ]] ; then
    :
  else
    echo "Invalid target version: must be 7.0 8.0 9.0 or 10.0"
    exit 1
  fi
  if [ -d "$1" ]; then
    SRCPATH=$1
  elif [ -d ~/$2/$1 ]; then
    SRCPATH=~/$2/$1
  elif [ "${1:0:23}" == "https://github.com/OCA/" ]; then
    if [ -d ~/$3 ]; then
      echo "\$ cd ~/$3"
      cd ~/$3
      pkg_URL=$1
      MODNAME=$(basename $1)
      if [ "${MODNAME: -4}" == ".git" ]; then
         MODNAME=${MODNAME:0: -4}
      fi
      DSTPATH=~/$3/$MODNAME
      if [ -d $DSTPATH ]; then
        echo "Version $3 already exists"
        if [ "$4" == "-y" ]; then
          a=y
        else
          read -p "confirm action (y/n)?" a
        fi
        if [ "$a" != "y" ]; then
          exit 1
        fi
        CWD=$PWD
        echo "\$ cd $DSTPATH"
        cd $DSTPATH
        echo "\$ git push origin --delete $3"
        git push origin --delete $3
        echo "\$ cd $CWD"
        cd $CWD
        echo "\$ rm -fR $DSTPATH"
        rm -fR $DSTPATH
      fi
      git_opts="-b $2"
      echo "\$ git clone $pkg_URL $MODNAME/ $git_opts"
      git clone $pkg_URL $MODNAME/ $git_opts
      echo "\$ cd $MODNAME"
      cd $MODNAME
      echo "\$ git remote add upstream $pkg_URL"
      git remote add upstream $pkg_URL
      pkg_URL="git@github.com:zeroincombenze/$MODNAME.git"
      echo "\$ git remote remove origin"
      git remote remove origin
      echo "\$ git remote add origin $pkg_URL"
      git remote add origin $pkg_URL
      SRCPATH=
    else
      echo "Directory ~/$3 not found"
      exit 1
    fi
  else
    echo "Directory $1 not found"
    echo "Directory ~/$1/$2 not found"
    exit 1
  fi
  if [ -n "$SRCPATH" ]; then
    if [ "$2" == "$3" ]; then
      echo "Same source and target version"
      exit 1
    fi
    MODNAME=$(basename $SRCPATH)
    DSTPATH=~/$3/$MODNAME
    if [ -d $DSTPATH ]; then
      echo "Version $3 already exists"
      if [ "$4" == "-y" ]; then
        a=y
      else
        read -p "confirm action (y/n)?" a
      fi
      if [ "$a" != "y" ]; then
        exit 1
      fi
      echo "\$ rm -fR $DSTPATH"
      rm -fR $DSTPATH
    fi
    echo "\$ cd ~/$3"
    cd ~/$3
    echo "\$ cp -r $SRCPATH/ ./"
    cp -r $SRCPATH/ ./
  fi
  echo "\$ cd $DSTPATH"
  cd $DSTPATH
  if [ " ${MODNAME:0:10}" != "l10n-italy" ]; then
    echo "\$ git remote update"
    git remote update
  fi
  if [ "$2" != "$3" ]; then
    echo "\$ git checkout -b ${3} origin/${2}"
    git checkout -b ${3} origin/${2}
    echo "\$ git format-patch --stdout origin/${2} -- $DSTPATH | git am -3"
    git format-patch --stdout origin/${2} -- $DSTPATH | git am -3
    echo "\$ git branch ${2} -D"
    git branch ${2} -D
  fi
  pkg_URL=$(git remote -v|grep origin|head -n1|awk '{ print $2}')
  echo "\$ git push origin $3"
  git push origin $3
  echo "\$ git push origin --delete 5.0"
  git push origin --delete 5.0
  echo "\$ git push origin --delete 6.0"
  git push origin --delete 6.0
  echo "\$ git push origin --delete 6.1"
  git push origin --delete 6.1
  echo "\$ cd ~/$3"
  cd ~/$3
fi
x=$(git submodule status|grep $MODNAME)
if [ -z "$x" ]; then
  echo "\$ git submodule add -f $pkg_URL $MODNAME/"
  git submodule add -f $pkg_URL $MODNAME/
fi
if [ -z "$(grep "$MODNAME/" .gitignore 2>/dev/null)" ]; then
  echo "\$ echo $MODNAME/>>.gitignore"
  echo "$MODNAME/">>.gitignore
fi
