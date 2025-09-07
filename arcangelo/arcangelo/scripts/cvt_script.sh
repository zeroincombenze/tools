#! /bin/bash
# -*- coding: utf-8 -*-
#
# Upgrade bash script with z0lib odoorc travisrc libraries
#
# This free software is released under GNU Affero GPL3
# author: Antonio Maria Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2016-2025 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# Based on template 2.1.1
[ $BASH_VERSINFO -lt 4 ] && echo "This script $0 requires bash 4.0+!" && exit 4
READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
ME=$(readlink -e $0)
if [[ -d $HOME/devel || -z $HOME_DEVEL || ! -d $HOME_DEVEL ]]; then
  [[ -d $HOME/odoo/devel ]] && HOME_DEVEL="$HOME/odoo/devel" || HOME_DEVEL="$HOME/devel"
fi
PYPATH=""
[[ $(basename $PWD) == "tests" && $(basename $PWD/../..) == "build" ]] && PYPATH="$(dirname $PWD)"
[[ $(basename $PWD) == "tests" && $(basename $PWD/../..) == "build" && -d $PWD/../scripts ]] && PYPATH="$PYPATH $(readlink -f $PWD/../scripts)"
x=$ME; while [[ $x != $HOME && $x != "/" && ! -d $x/lib && ! -d $x/bin && ! -d $x/pypi ]]; do x=$(dirname $x); done
[[ -d $x/pypi ]] && PYPATH="$PYPATH $x/pypi"
[[ -d $x/pypi/z0lib ]] && PYPATH="$PYPATH $x/pypi/z0lib"
[[ -d $x/pypi/z0lib/z0lib ]] && PYPATH="$PYPATH $x/pypi/z0lib/z0lib"
[[ -d $x/tools ]] && PYPATH="$PYPATH $x/tools"
[[ -d $x/tools/z0lib ]] && PYPATH="$PYPATH $x/tools/z0lib"
[[ -d $x/bin ]] && PYPATH="$PYPATH $x/bin"
[[ -d $x/lib ]] && PYPATH="$PYPATH $x/lib"
[[ -d $HOME_DEVEL/venv/bin ]] && PYPATH="$PYPATH $HOME_DEVEL/venv/bin"
[[ -d $HOME_DEVEL/../tools ]] && PYPATH="$PYPATH $(readlink -f $HOME_DEVEL/../tools)"
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $TDIR $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$(readlink -e $d)
    break
  fi
done
[[ -z "$Z0LIBDIR" ]] && echo "Library file z0librc not found in <$PYPATH>!" && exit 72
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"

# DIST_CONF=$(findpkg ".z0tools.conf" "$PYPATH")
# TCONF="$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg $DIST_CONF $TCONF
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=$DIST_CONF" && echo "TCONF=$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
CYAN="\e[1;36m"
GREEN="\e[1;32m"
CLR="\e[0m"

__version__=2.1.1

#//Only human upgradable code/
# blk1 => z0librc
# blk2 => odoorc
# blk3 => travisrc
# blk4 => zarrc
# blk8 => TESTDIR= ...
# blk9 => z0testrc

parse_blk_2() {
  if [ $prc -lt 2 ]; then
    prc=2
    if [ $opt_oeLib -ne 0 -a $opt_UT -eq 0 ]; then
      blk_2 "$fntmp"
      empty=0
    fi
  fi
}

parse_blk_3() {
  if [ $prc -lt 3 ]; then
    prc=3
    if [ $opt_tjLib -ne 0 -a $opt_UT -eq 0 ]; then
      blk_3 "$fntmp"
      empty=0
    fi
  fi
}

parse_blk_4() {
  if [ $prc -lt 4 ]; then
    prc=5
    if [ $opt_zLib -ne 0 -a $opt_UT -eq 0 ]; then
      blk_4 "$fntmp"
      empty=0
    fi
  fi
}

parse_blk_8() {
  if [[ $prc -lt 8 ]]; then
    prc=8
    if [[ $opt_UT -ne 0 || $opt_Test -ne 0 ]]; then
      blk_8 "$fntmp"
      empty=0
    fi
  fi
}

parse_blk_9() {
  if [ $prc -lt 9 ]; then
    prc=9
    if [ $opt_UT -ne 0 ]; then
      blk_9 "$fntmp"
      empty=0
    fi
  fi
}

parse_blk_10() {
  if [[ $prc -lt 10 ]]; then
    prc=10
    blk_10 "$fntmp"
    empty=0
  fi
}

cvt_file() {
  # cvt_file(file)
  # global empty prc
  local f1=$1
  local fntmp=$f1.tmp
  local bakfn=$f1.bak
  local x y line line_ver
  local state=0
  sts=$STS_SUCCESS
  prc=0
  if [[ -n "$f1" ]]; then
    if [[ -x "$f1" ]]; then
      OPTS_JOZ=
      if [ $opt_tjLib -ne 0 ]; then
        OPTS_J="-J"
        OPTS_JOZ=${OPTS_JOZ}J
      else
        OPTS_J=
      fi
      if [ $opt_oeLib -ne 0 ]; then
        OPTS_O="-O"
        OPTS_JOZ=${OPTS_JOZ}O
      else
        OPTS_O=
      fi
      if [ $opt_zLib -ne 0 ]; then
        OPTS_Z="-Z"
        OPTS_JOZ=${OPTS_JOZ}Z
      else
        OPTS_Z=
      fi
      [[ -n "$OPTS_JOZ" ]] && OPTS_JOZ="-$OPTS_JOZ"
      local incl=0
      empty=0
      susp=0
      break_susp=""
      rm -f $fntmp
      while IFS= read -r line || [[ -n "$line" ]]; do
        while [[ "${line: -1}" == " " ]]; do line="${line:0:-1}"; done
        [[ susp -lt 0 && $line =~ $break_susp ]] && ((susp=-susp)) && break_susp=""
        [[ susp -gt 0 ]] && ((susp--)) && continue
        # line="${line/2021/2023}"
        # line="${line/-21/-23}"
        if [[ $prc -lt 10 && $line =~ ^__version__=.* ]]; then
          if [[ $opt_keep -ne 0 ]]; then
            line_ver="$line"
          elif [ $opt_lev3 -eq 0 ]; then
            x=$(echo $line | grep --color=never -Eo '[0-9]+\.[0-9]+\.[0-9]+\(\.[0-9]*\)?' | awk -F. '{print $4}')
            ((x++))
            y="$(echo $line | grep --color=never -Eo ''[0-9.]+'' | awk -F. '{print $1"."$2"."$3}')"
            line_ver="__version__=$y.$x"
          else
            x=$(echo $line | grep --color=never -Eo '[0-9]+\.[0-9]+\.[0-9]+' | awk -F. '{print $3}')
            ((x++))
            y="$(echo $line | grep --color=never -Eo ''[0-9.]+'' | awk -F. '{print $1"."$2}')"
            line_ver="__version__=$y.$x"
          fi
          if [ $prc -eq 0 ]; then
            [[ $opt_keep -ne 0 ]] && echo "$line_ver" >>$fntmp
            continue
          fi
        fi
        if [[ $line =~ ^#[^A-Za-z09_]*Enable.auto.upgrade.code.* ]]; then
          echo "$line" >>$fntmp
          incl=0
        elif [[ $line =~ ^#[^A-Za-z09_]*Only.human.upgradable.code.* ]]; then
          echo "$line" >>$fntmp
          incl=1
        elif [[ $incl -eq 1 ]]; then
          echo "$line" >>$fntmp
        elif [[ $line =~ ^if.*\$opt_help.*gt.*then$ ]]; then
          echo "if [[ \$opt_help -gt 0 ]]; then" >>$fntmp
        elif [[ $line =~ ^if.*\$opt_version.*then$ ]]; then
          echo "if [[ \"\$opt_version\" ]]; then" >>$fntmp
        elif [[ $line =~ ^[[:space:]]*man[[:space:]]\$TDIR/\$THIS.man ]]; then
          echo "  man \$(dirname \$0)/man/man8/\$(basename \$0).8.gz" >>$fntmp
        elif [[ $line =~ set_cfg_def ]]; then
          echo "${line/set_cfg_def/CFG_set}" >>$fntmp
        elif [[ $line =~ ^OPTACTI=\(1... ]]; then
          x="(\"+\""
          echo "${line/(1  /$x}" >>$fntmp
        elif [ $prc -eq 0 ]; then
          if [[ $line =~ ^THIS=..basename || $line =~ ^#?.?export.READLINK= || $line =~ ^#?.?READLINK= || $line =~ ^#.Based.on.template ]]; then
            prc=1
            blk_1 "$fntmp"
            empty=0
            susp=-3
            break_susp="^if ..? -z ..Z0LIBDIR. ..?; then"
          else
            echo "$line" >>$fntmp
          fi
        elif [[ $prc -ge 1 && $prc -le 9 ]]; then
          if [[ $line =~ ^ODOOLIBDIR.*findpkg.*odoorc ]]; then
            parse_blk_2
            if [ $opt_oeLib -eq 0 -a $opt_nowarn -eq 0 ]; then
              echo "Warning: found Odoo library statements w/o -O switch"
              ToRepeat="$ToRepeat opt_oeLib=1"
            fi
          elif [[ $line =~ ^TRAVISLIBDIR.*findpkg.*travisrc.* ]]; then
            if [ $prc -lt 2 ]; then
              parse_blk_2
            fi
            parse_blk_3
            if [ $opt_tjLib -eq 0 -a $opt_nowarn -eq 0 ]; then
              echo "Warning: found Travis library statements w/o -J switch"
              ToRepeat="$ToRepeat opt_tjLib=1"
            fi
          elif [[ $line =~ ^ZARLIB.*findpkg.*zarrc.* ]]; then
            if [ $prc -lt 2 ]; then
              parse_blk_2
            fi
            if [ $prc -lt 3 ]; then
              parse_blk_3
            fi
            parse_blk_4
            if [ $opt_zLib -eq 0 ]; then
              echo "Warning: found Zar library w/o -Z switch"
              ToRepeat="$ToRepeat opt_zLib=1"
            fi
          elif [[ $line =~ ^TESTDIR.*findpkg.*TDIR.* ]]; then
            if [ $prc -lt 2 ]; then
              parse_blk_2
            fi
            if [ $prc -lt 3 ]; then
              parse_blk_3
            fi
            if [ $prc -lt 4 ]; then
              parse_blk_4
            fi
            if [ $opt_UT -ne 0 -o $opt_Test -ne 0 ]; then
              parse_blk_8
            elif [ $opt_Test -eq 0 -a $opt_nowarn -eq 0 ]; then
              echo "Warning: found statements to remove w/o -T switch"
              ToRepeat="$ToRepeat opt_Test=1"
            fi
          elif [[ $line =~ ^Z0TLIBDIR.*findpkg.*z0testrc.* ]]; then
            [[ $prc -lt 2 ]] && parse_blk_2
            [[ $prc -lt 3 ]] && parse_blk_3
            [[ $prc -lt 4 ]] && parse_blk_4
            [[ $prc -lt 8 ]] && parse_blk_8
            [[ $prc -lt 9 ]] && parse_blk_9
            if [[ $opt_UT -eq 0 ]]; then
              echo "Warning: found Zerobug library w/o -U switch"
              ToRepeat="$ToRepeat opt_UT=1"
            fi
          elif [[ $line =~ ^__version__= || $line =~ ^[a-zA_Z0-9_]+[:space:]*\( ]]; then
            [[ $prc -lt 2 ]] && parse_blk_2
            [[ $prc -lt 3 ]] && parse_blk_3
            [[ $prc -lt 4 ]] && parse_blk_4
            [[ $prc -lt 8 ]] && parse_blk_8
            [[ $prc -lt 9 ]] && parse_blk_9
            [[ $prc -lt 10 ]] && parse_blk_10
            [[ $empty -eq 0 ]] && echo "" >>$fntmp
            echo "$line_ver" >>$fntmp
            # prc=10
            if ! [[ $line =~ ^__version__.* ]]; then
              echo "$line" >>$fntmp
            fi
          else
            :
          fi
        elif [[ $line =~ ^parseoptargs ]]; then
          echo "parseoptargs \"\$@\"" >>$fntmp
          state=1
        elif [[ $state == "1" && $line =~ ^\ +print_help ]]; then
          echo "$line" >>$fntmp
          state=2
        elif [[ $state == "2" ]]; then
          if [ -n "${COPY[$opt_id]}" ]; then
            echo "  \"${COPY[$opt_id]}\"" >>$fntmp
          else
            echo "$line" >>$fntmp
          fi
          state=0
        elif [ $prc -eq 10 ]; then
          if [[ $line =~ ^Z0BUG_init ]]; then
            prc=11
            blk_11 "$fntmp"
            empty=0
          elif [[ $line =~ ^opts_travis ]]; then
            prc=21
            blk_21 "$fntmp"
            # susp=2
          elif [[ $line =~ ^(# *)?TCONF=.* ]]; then
            :
          else
            echo "$line" >>$fntmp
          fi
        elif [ $prc -eq 11 ]; then
          if [ -z "$line" ]; then
            prc=12
            echo "$line" >>$fntmp
          elif [[ $line =~ ^UT1?_LIST=.* ]]; then
            prc=12
            echo "$line" >>$fntmp
          else
            :
          fi
        elif [ $prc -eq 12 ]; then
          if [[ $line =~ ^.*type.*Z0BUG_setup.*function.* ]]; then
            prc=13
            blk_13 "$fntmp"
            empty=0
          elif [[ $line =~ ^Z0BUG_main_file.* ]]; then
            blk_13 "$fntmp"
            prc=14
            blk_14 "$fntmp"
            empty=0
          else
            echo "$line" >>$fntmp
          fi
        elif [ $prc -eq 13 ]; then
          if [[ $line =~ ^.*type.*Z0BUG_setup.*function.* ]]; then
            :
          elif [[ $line =~ ^Z0BUG_main_file.* ]]; then
            prc=14
            blk_14 "$fntmp"
            empty=0
          elif [[ $line =~ ^#[^A-Za-z09_]End.Include.Block.* ]]; then
            echo "$line" >>$fntmp
            incl=0
          elif [[ $line =~ ^#[^A-Za-z09_]Follow.code.must.be.executed.* ]]; then
            echo "$line" >>$fntmp
            incl=2
          elif [ $incl -eq 2 ]; then
            echo "$line" >>$fntmp
          fi
        elif [ $prc -eq 14 ]; then
          :
        elif [ $prc -eq 21 ]; then
          if [[ $line =~ ^init_travis ]]; then
            # echo "$line" >>$fntmp
            prc=22
          elif [[ $line =~ ^prepare_env_travis ]]; then
            prc=22
          elif [[ $line =~ ^#[^A-Za-z09_]End.Include.Block.* ]]; then
            echo "$line" >>$fntmp
            incl=0
          elif [[ $line =~ ^#[^A-Za-z09_]Follow.code.must.be.executed.* ]]; then
            echo "$line" >>$fntmp
            incl=2
          elif [ $incl -eq 2 ]; then
            echo "$line" >>$fntmp
          fi
        elif [ "${line:0:1}" == "#" ]; then
          echo "$line" >>$fntmp
          empty=0
        elif [ -z "$line" ]; then
          [[ $empty -le 2 ]] && echo "$line" >>$fntmp
          ((empty++))
        else
          echo "$line" >>$fntmp
          empty=0
        fi
      done <$f1
    else
      echo "File $f1 not found or not executable!"
      sts=2
    fi
  fi
  if [ -f $fntmp -a -z "$ToRepeat" ]; then
    if [ $opt_verbose -eq 0 -a $opt_yes -ne 0 ]; then
      diff -q $f1 $fntmp &>/dev/null
    else
      diff --suppress-common-line -y $f1 $fntmp
      # diff -y $f1 $fntmp
    fi
    if [ $? -eq 0 ]; then
      dummy='q'
    elif [ $opt_dry_run -ne 0 ]; then
      dummy='n'
    elif [ $opt_yes -ne 0 ]; then
      dummy='y'
    else
      read -p "Confirm (Y/N)? " dummy
    fi
    if [ "$dummy" == "Y" -o "$dummy" == "y" ]; then
      cp -p $f1 $bakfn
      mv $fntmp $f1
      chmod +x $f1
      if [ $opt_verbose -gt 0 ]; then
        echo "File $f1 upgraded"
      fi
    else
      rm -f $fntmp
      if [ $opt_verbose -gt 0 ]; then
        if [ "$dummy" == "q" ]; then
          echo "Script $1 already upgraded"
        else
          echo "Upgrade of $f1 discarded!"
        fi
      fi
    fi
  fi
  return $sts
}

blk_1() {
  cat <<EOF >>$1
# Based on template 2.1.1
[ \$BASH_VERSINFO -lt 4 ] && echo "This script \$0 requires bash 4.0+!" && exit 4
READLINK=\$(which readlink 2>/dev/null)
export READLINK
THIS=\$(basename "\$0")
TDIR=\$(readlink -f \$(dirname \$0))
ME=\$(readlink -e \$0)
if [[ -d \$HOME/devel || -z \$HOME_DEVEL || ! -d \$HOME_DEVEL ]]; then
  [[ -d \$HOME/odoo/devel ]] && HOME_DEVEL="\$HOME/odoo/devel" || HOME_DEVEL="\$HOME/devel"
fi
PYPATH=""
[[ \$(basename \$PWD) == "tests" && \$(basename \$PWD/../..) == "build" ]] && PYPATH="\$(dirname \$PWD)"
[[ \$(basename \$PWD) == "tests" && \$(basename \$PWD/../..) == "build" && -d \$PWD/../scripts ]] && PYPATH="\$PYPATH \$(readlink -f \$PWD/../scripts)"
x=\$ME; while [[ \$x != \$HOME && \$x != "/" && ! -d \$x/lib && ! -d \$x/bin && ! -d \$x/pypi ]]; do x=\$(dirname \$x); done
[[ -d \$x/pypi ]] && PYPATH="\$PYPATH \$x/pypi"
[[ -d \$x/pypi/z0lib ]] && PYPATH="\$PYPATH \$x/pypi/z0lib"
[[ -d \$x/pypi/z0lib/z0lib ]] && PYPATH="\$PYPATH \$x/pypi/z0lib/z0lib"
[[ -d \$x/tools ]] && PYPATH="\$PYPATH \$x/tools"
[[ -d \$x/tools/z0lib ]] && PYPATH="\$PYPATH \$x/tools/z0lib"
[[ -d \$x/bin ]] && PYPATH="\$PYPATH \$x/bin"
[[ -d \$x/lib ]] && PYPATH="\$PYPATH \$x/lib"
[[ -d \$HOME_DEVEL/venv/bin ]] && PYPATH="\$PYPATH \$HOME_DEVEL/venv/bin"
[[ -d \$HOME_DEVEL/../tools ]] && PYPATH="\$PYPATH \$(readlink -f \$HOME_DEVEL/../tools)"
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=\$PYPATH"
for d in \$TDIR \$PYPATH /etc; do
  if [[ -e \$d/z0librc ]]; then
    . \$d/z0librc
    Z0LIBDIR=\$(readlink -e \$d)
    break
  fi
done
[[ -z "\$Z0LIBDIR" ]] && echo "Library file z0librc not found in <\$PYPATH>!" && exit 72
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=\$Z0LIBDIR"
EOF
}

blk_2() {
  cat <<EOF >>$1
ODOOLIBDIR=\$(findpkg odoorc "\$PYPATH" "clodoo" "clodoo")
[[ -z "\$ODOOLIBDIR" ]] && echo "Library file odoorc not found!" && exit 72
. \$ODOOLIBDIR
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=\$ODOOLIBDIR"
EOF
}

blk_3() {
  cat <<EOF >>$1
TRAVISLIBDIR=\$(findpkg travisrc "\$PYPATH" "travis_emulator" "travis_emulator")
[[ -z "\$TRAVISLIBDIR" ]] && echo "Library file travisrc not found!" && exit 72
. \$TRAVISLIBDIR
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TRAVISLIBDIR=\$TRAVISLIBDIR"
EOF
}

blk_4() {
  cat <<EOF >>$1
ZARLIB=\$(findpkg zarrc "\$PYPATH")
[[ -z "\$ZARLIB" ]] && echo "Library file zarrc not found!" && exit 72
. \$ZARLIB
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ZARLIB=\$ZARLIB"
EOF
}

blk_8() {
  cat <<EOF >>$1
TESTDIR=\$(findpkg "" "\$TDIR . .." "tests")
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=\$TESTDIR"
RUNDIR=\$(readlink -e \$TESTDIR/..)
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=\$RUNDIR"
EOF
}

blk_9() {
  cat <<EOF >>$1
Z0TLIBDIR=\$(findpkg z0testrc "\$PYPATH" "zerobug")
[[ -z "\$Z0TLIBDIR" ]] && echo "Library file z0testrc not found!" && exit 72
. \$Z0TLIBDIR
Z0TLIBDIR=\$(dirname \$Z0TLIBDIR)
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0TLIBDIR=\$Z0TLIBDIR"
EOF
}

blk_10() {
  cat <<EOF >>$1

# DIST_CONF=\$(findpkg ".z0tools.conf" "\$PYPATH")
# TCONF="\$HOME/.z0tools.conf"
CFG_init "ALL"
link_cfg_def
link_cfg \$DIST_CONF \$TCONF
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "DIST_CONF=\$DIST_CONF" && echo "TCONF=\$TCONF"
get_pypi_param ALL
RED="\e[1;31m"
CYAN="\e[1;36m"
GREEN="\e[1;32m"
CLR="\e[0m"
EOF
}

blk_11() {
  cat <<EOF >>$1
Z0BUG_init
EOF
  if [ $opt_tjLib -ne 0 -o $opt_oeLib -ne 0 -o $opt_zLib -ne 0 ]; then
    cat <<EOF >>$1
parseoptest -l\$TESTDIR/test_${opt_id}.log "\$@" "$OPTS_JOZ"
EOF
  else
    cat <<EOF >>$1
parseoptest -l\$TESTDIR/test_${opt_id}.log "\$@"
EOF
  fi
  cat <<EOF >>$1
sts=\$?
[[ \$sts -ne 127 ]] && exit \$sts
EOF
  # blk_2z "$1"
  # blk_3z "$1"
  # blk_4z "$1"
  cat <<EOF >>$1
for p in z0librc odoorc travisrc zarrc z0testrc; do
  if [[ -f \$RUNDIR/\$p ]]; then
    [[ \$p == "z0librc" ]] && Z0LIBDIR="\$RUNDIR" && source \$RUNDIR/\$p
    [[ \$p == "odoorc" ]] && ODOOLIBDIR="\$RUNDIR" && source \$RUNDIR/\$p
    [[ \$p == "travisrc" ]] && TRAVISLIBDIR="\$RUNDIR" && source \$RUNDIR/\$p
    [[ \$p == "zarrc" ]] && ZARLIB="\$RUNDIR" && source \$RUNDIR/\$p
    [[ \$p == "z0testrc" ]] && Z0TLIBDIR="\$RUNDIR" && source \$RUNDIR/\$p
  fi
done
EOF
  echo "" >>$1
}

blk_13() {
  cat <<EOF >>$1
[[ "\$(type -t Z0BUG_setup)" == "function" ]] && Z0BUG_setup
EOF
}

blk_14() {
  cat <<EOF >>$1
Z0BUG_main_file "\$UT1_LIST" "\$UT_LIST"
sts=\$?
[[ "\$(type -t Z0BUG_teardown)" == "function" ]] && Z0BUG_teardown
exit \$sts
EOF
}

blk_21() {
  cat <<EOF >>$1
opts_travis
conf_default
[[ \$opt_verbose -gt 2 ]] && set -x
init_travis
EOF
}
#//Enable.auto.upgrade.code/

OPTOPTS=(h        J         K        k        m        n           O         q           T        U      V           v           w          y       Z)
OPTLONG=(help     ""        ""       keep     mod-name dry-run     ""        quiet       ""       ""     version     verbos      no-warn    yes     "")
OPTDEST=(opt_help opt_tjLib opt_lev3 opt_keep opt_id   opt_dry_run opt_oeLib opt_verbose opt_Test opt_UT opt_version opt_verbose opt_nowarn opt_yes opt_zLib)
OPTACTI=("+"      1         1        1        "="      1           1         0           1        1      "*"         "+"         1          1       1)
OPTDEFL=(1        0         0        0        ""       0           0         0           0        0      ""          -1          0          0       0)
OPTMETA=("help"   ""        ""       ""       "name"   "noop"      ""        "quiet"     ""       ""     "version"   "verbose"   ""         ""      "")
OPTHELP=("this help"
  "load travisrc library"
  "set script version format n.n.n"
  "Keep script version"
  "module name"
  "do nothing (dry-run)"
  "load odoorc library"
  "silent mode"
  "script with test_mode switch"
  "unit test script with z0testrc library"
  "show version end exit"
  "verbose mode"
  "suppress warning messages"
  "assume yes"
  "load zar library")
OPTARGS=(bashscript)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Update bash script" \
    "© 2016-25 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi

[[ $opt_verbose -gt 1 ]] && set -x
declare -A COPY
COPY[z0lib]="© 2015-25 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
COPY[travis_em]="© 2015-25 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
[[ -z "$opt_id" ]] && opt_id=$(basename $(dirname $(readlink -f $bashscript)))
[[ $opt_id == "tests" ]] && opt_id=$(basename $(dirname $(dirname $(readlink -f $bashscript))))
ToRepeat=
cvt_file $bashscript
if [[ -n "$ToRepeat" ]]; then
  eval $ToRepeat
  echo "Found wrong flags, repeating operation ..."
  ToRepeat=
  cvt_file $bashscript
fi
sts=$STS_SUCCESS
exit $sts
