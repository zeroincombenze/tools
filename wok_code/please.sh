#! /bin/bash
# -*- coding: utf-8 -*-
#
# please
# Developer shell
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2015-2021 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
# READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
# export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
<<<<<<< HEAD:wok_code/please.sh
PYPATH=""
for p in $TDIR $TDIR/.. $TDIR/../.. $HOME/venv_tools/bin $HOME/venv_tools/lib $HOME/tools; do
  [[ -d $p ]] && PYPATH=$(find $(readlink -f $p) -maxdepth 3 -name z0librc)
  [[ -n $PYPATH ]] && PYPATH=$(dirname $PYPATH) && break
done
PYPATH=$(echo -e "import os,sys;p=[os.path.dirname(x) for x in '$PYPATH'.split()];p.extend([x for x in os.environ['PATH'].split(':') if x not in p and x.startswith('$HOME')]);p.extend([x for x in sys.path if x not in p]);print(' '.join(p))"|python)
=======
[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\nHOME=os.environ.get('HOME');y=os.path.join(HOME_DEV,'pypi');t=os.path.join(HOME,'tools')\ndef apl(l,p,x):\n  d2=os.path.join(p,x,x)\n  d1=os.path.join(p,x)\n  if os.path.isdir(d2):\n   l.append(d2)\n  elif os.path.isdir(d1):\n   l.append(d1)\nl=[TDIR]\nfor x in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(y):\n  apl(l,y,x)\n elif TDIR.startswith(t):\n  apl(l,t,x)\nl=l+os.environ['PATH'].split(':')\np=set()\npa=p.add\np=[x for x in l if x and x.startswith(HOME) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|python)
>>>>>>> stash:wok_code/please
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0lib/z0librc ]]; then
    . $d/z0lib/z0librc
    Z0LIBDIR=$d/z0lib
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [[ -e $d/z0librc ]]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [[ -z "$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
ODOOLIBDIR=$(findpkg odoorc "$PYPATH" "clodoo")
if [[ -z "$ODOOLIBDIR" ]]; then
  echo "Library file odoorc not found!"
  exit 72
fi
. $ODOOLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "ODOOLIBDIR=$ODOOLIBDIR"
TRAVISLIBDIR=$(findpkg travisrc "$PYPATH" "travis_emulator")
if [[ -z "$TRAVISLIBDIR" ]]; then
  echo "Library file travisrc not found!"
  exit 72
fi
. $TRAVISLIBDIR
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TRAVISLIBDIR=$TRAVISLIBDIR"
TESTDIR=$(findpkg "" "$TDIR . .." "tests")
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "TESTDIR=$TESTDIR"
RUNDIR=$(readlink -e $TESTDIR/..)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "RUNDIR=$RUNDIR"
RED="\e[1;31m"
GREEN="\e[1;32m"
CLR="\e[0m"

<<<<<<< HEAD:wok_code/please.sh
__version__=1.0.2.2
=======
__version__=1.0.2.5
>>>>>>> stash:wok_code/please

#
# General Purpose options:
# -A dont exec odoo test
# -B exec bash test
# -b branch: must be 6.1 7.0, 8.0, 9.0 10.0 11.0 12.0 13.0 or 14.0
# -C commit & push | dont exc clodoo test
# -c configuration file
# -D duplicate odoo to another version
# -d diff
# -F fetch
# -f force
# -H use virtualenv
# -k keep files
# -K exec bash, flake8 and pylint tests | run cron environ
# -j exec tests in project dir rather in test dir
# -m show missing line in report
# -n do nothing (dry-run)
# -o limit push to ids
# -O run odoo burst
# -O replace odoo distribution
# -o OCA directives
# -P push
# -p local path
# -q silent mode
# -R replace | replica
# -r rescricted mode (w/o parsing travis.yml file)
# -S status
# -T exec regression test
# -t do nothing (test-mode)
# -u dont update newer files
# -V show version
# -v verbose mode
# -W whatis
# -w wep

move() {
  # move(src dst)
  if [ -f "$2" ]; then rm -f $2; fi
  run_traced "cp -p $1 $2"
  run_traced "rm -f $1"
}

move_n_bak() {
  # move_n_bak(src dst)
  if [ -f "$2.bak" ]; then rm -f $2.bak; fi
  run_traced "cp -p $2 $2.bak"
  run_traced "mv -f $1 $2"
}

search_pofile() {
  srcs=$(find -L $odoo_root -not -path '*/__to_remove/*' -type d -name "$opt_modules")
  f=0
  for src in $srcs; do
    if [ -n "$src" ]; then
      if [ -f $src/i18n/it.po ]; then
        src=$src/i18n/it.po
        if [ $opt_exp -ne 0 ]; then
          run_traced "cp $src $src.bak"
        fi
        f=1
        break
      else
        alt=$(find -L $src/i18n -name '*.po' | head -n1)
        src=
        if [ -n "$alt" ]; then fi=1 break; fi
      fi
    fi
  done
}

add_copyright() {
  #add_copyright(file rst zero|oca|powerp)
  if [[ "$PRJNAME" == "Odoo" ]]; then
    if [[ $2 -eq 1 ]]; then
      echo ".. [//]: # (copyright)" >>$1
    else
      echo "[//]: # (copyright)" >>$1
    fi
    echo "" >>$1
    echo "----" >>$1
    echo "" >>$1
    if [[ $2 -eq 1 ]]; then
      echo "**Odoo** is a trademark of  \`Odoo S.A." >>$1
      echo "<https://www.odoo.com/>\`_." >>$1
      echo "(formerly OpenERP, formerly TinyERP)" >>$1
    else
      echo "**Odoo** is a trademark of [Odoo S.A.](https://www.odoo.com/) (formerly OpenERP, formerly TinyERP)" >>$1
    fi
    echo "" >>$1
    if [[ $2 -eq 1 ]]; then
      echo "**OCA**, or the  \`Odoo Community Association" >>$1
      echo "<http://odoo-community.org/>\`_." >>$1
      echo "is a nonprofit organization whose" >>$1
    else
      echo "**OCA**, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose" >>$1
    fi
    echo "mission is to support the collaborative development of Odoo features and" >>$1
    echo "promote its widespread use." >>$1
    echo "" >>$1
    if [[ "$3" == "powerp" ]]; then
      echo "**powERP**, or the [powERP enterprise network](https://www.powerp.it/)" >>$1
      echo "is an Italian enterprise network whose mission is to develop high-level" >>$1
      echo "addons designed for Italian enterprise companies." >>$1
      echo "The powER software, released under Odoo Proprietary License," >>$1
      echo "adds new enhanced features to Italian localization." >>$1
      echo "La rete di imprese [powERP](https://www.powerp.it/)" >>$1
      echo "fornisce, sotto licenza OPL, estensioni evolute della localizzazine italiana." >>$1
      echo "Il software è progettato per medie e grandi imprese italiane" >>$1
      echo "che richiedono caratteristiche non disponibili nella versione Odoo CE" >>$1
      echo "" >>$1
    else
      if [ $2 -eq 1 ]; then
        echo "**zeroincombenze®** is a trademark of \`SHS-AV s.r.l." >>$1
        echo "<http://www.shs-av.com/>\`_." >>$1
      else
        echo "**zeroincombenze®** is a trademark of [SHS-AV s.r.l.](http://www.shs-av.com/)" >>$1
      fi
      echo "which distributes and promotes **Odoo** ready-to-use on own cloud infrastructure." >>$1
      echo "[Zeroincombenze® distribution of Odoo](http://wiki.zeroincombenze.org/en/Odoo)" >>$1
      echo "is mainly designed for Italian law and markeplace." >>$1
      echo "Users can download from [Zeroincombenze® distribution](https://github.com/zeroincombenze/OCB) and deploy on local server." >>$1
      echo "" >>$1
    fi
    if [ $2 -eq 1 ]; then
      echo "" >>$1
      echo ".. [//]: # (end copyright)" >>$1
    else
      echo "[//]: # (end copyright)" >>$1
    fi
  else
    if [ $2 -eq 1 ]; then
      echo ".. [//]: # (copyright)" >>$1
    else
      echo "[//]: # (copyright)" >>$1
    fi
    echo "" >>$1
    echo "----" >>$1
    echo "" >>$1
    if [ $2 -eq 1 ]; then
      echo "**zeroincombenze®** is a trademark of \`SHS-AV s.r.l." >>$1
      echo "<http://www.shs-av.com/>\`_." >>$1
    else
      echo "**zeroincombenze®** is a trademark of [SHS-AV s.r.l.](http://www.shs-av.com/)" >>$1
    fi
    echo "which distributes and promotes **Odoo** ready-to-use on its own cloud infrastructure." >>$1
    echo "" >>$1
    echo "Odoo is a trademark of Odoo S.A." >>$1
    if [ $2 -eq 1 ]; then
      echo "" >>$1
      echo ".. [//]: # (end copyright)" >>$1
    else
      echo "[//]: # (end copyright)" >>$1
    fi
  fi
}

add_addons() {
  #add_addons(file rst zero|oca|oia ORIG)
  if [ "$PRJNAME" == "Odoo" ]; then
    if [ $2 -eq 1 ]; then
      echo ".. [//]: # (addons)" >>$1
    else
      echo "[//]: # (addons)" >>$1
    fi
    $TDIR/gen_addons_table.py addons $4 >>$1
    if [ $2 -eq 1 ]; then
      echo "" >>$1
      echo ".. [//]: # (end addons)" >>$1
    else
      echo "[//]: # (end addons)" >>$1
    fi
  fi
}

add_install() {
  #add_install(file rst zero|oca|oia ORIG)
  if [ "$PRJNAME" == "Odoo" ]; then
    local pkgs
    local gitorg=$3
    [ "$3" == "zero" -o "$3" == "oia" ] && gitorg=${3}-http
    if [ -z "$REPOSNAME" ]; then
      local REPOS=$PKGNAME
      local url=$(build_odoo_param GIT_URL '.' "" "$gitorg")
      local root=$(build_odoo_param HOME '.')
    else
      pushd .. >/dev/null
      local REPOS=$REPOSNAME
      local url=$(build_odoo_param GIT_URL '.' "" "$gitorg")
      local root=$(build_odoo_param HOME '.')
      popd >/dev/null
    fi
    if [ $2 -eq 1 ]; then
      echo ".. [//]: # (install)" >>$1
    else
      echo "[//]: # (install)" >>$1
    fi
    echo "    ODOO_DIR=$root  # here your Odoo dir" >>$1
    echo "    BACKUP_DIR=$HOME/backup  # here your backup dir" >>$1
    pkgs=$(list_requirements -p $PWD -s' ' -P -t python)
    pkgs="${pkgs:7}"
    if [ -n "$pkgs" ]; then
      echo "    for pkg in $pkgs; do" >>$1
      echo "        pip install \$pkg" >>$1
      echo "    done" >>$1
    fi
    pkgs=$(list_requirements -p $PWD -s' ' -P -t modules)
    pkgs="${pkgs:8}"
    if [ -n "$pkgs" ]; then
      echo "    # Check for <$pkgs> modules" >>$1
    fi
    echo "    cd /tmp" >>$1
    echo "    git clone $url $REPOS" >>$1
    echo "    mv \$ODOO_DIR/$REPOS/$PKGNAME/ \$BACKUP_DIR/" >>$1
    echo "    mv /tmp/$REPOS/$PKGNAME/ \$ODOO_DIR/" >>$1
    if [ $2 -eq 1 ]; then
      echo "" >>$1
      echo ".. [//]: # (end install)" >>$1
    else
      echo "[//]: # (end install)" >>$1
    fi
  fi
}

restore_owner() {
  if [ "$USER" != "odoo" ]; then
    local fown="odoo:odoo"
    # [ "$USER" == "travis" ] && fown="travis:odoo"
    if sudo -v &>/dev/null; then
      run_traced "sudo chown -R $fown .git"
    elif [ "$USER" != "travis" ]; then
      run_traced "chown -R $fown .git"
    fi
  fi
}

expand_macro() {
  local t p v lne lne1
  lne="$1"
  for t in {1..9} LNK_DOCS BTN_DOCS LNK_HELP BTN_HELP; do
    p=\${$t}
    v=${M[$t]}
    lne1="${lne//$p/$v}"
    lne="$lne1"
  done
  echo -n "$lne"
}

# set_executable() {
#   run_traced "find $PKGPATH -type f -executable -exec chmod -x '{}' \;"
#   run_traced "find $PKGPATH -type f -name \"*.sh\" -exec chmod +x '{}' \;"
#   run_traced "find $PKGPATH -type f -exec grep -El \"#. *(/bin/bash|/usr/bin/env )\" '{}' \;|xargs -I{} chmod +x {}"
# }

get_ver() {
  local ver=
  if [ -n "$BRANCH" ]; then
    if [ "$BRANCH" == "master" ]; then
      ver=$BRANCH
    else
      ver=$(echo $BRANCH | grep -Eo '[0-9]+' | head -n1)
    fi
  else
    ver=master
  fi
  [ -n "$1" -a "$ver" == "master" ] && ver=0
  echo $ver
}

build_line() {
  # build_line(flag replmnt act)
  local v w x line
  v=${1^^}
  w="LNK_${v:1}"
  v="BTN_${v:1}"
  line="$2"
  if [[ "$3" =~ md_BTN ]]; then
    if [ -n "${M[$v]}" ]; then
      x="${M[$v]}"
      line="$line($x)]"
    fi
    if [ -n "${M[$w]}" ]; then
      x="${M[$w]}"
      line="$line($x)"
    fi
  elif [[ "$3" =~ rstBTN_.*/1 ]]; then
    if [ -z "$2" ]; then
      line=".. image::"
    else
      line=".. ${line:0:-1} image::"
    fi
    if [ -n "${M[$v]}" ]; then
      x="${M[$v]}"
      line="$line $x"
    fi
  elif [[ "$3" =~ rstBTN_.*/2 ]]; then
    if [ -z "$2" ]; then
      line="   :target:"
    else
      line=".. _${line:1:-2}:"
    fi
    if [ -n "${M[$w]}" ]; then
      x="${M[$w]}"
      line="$line $x"
    fi
  elif [ "$3" == "CHPT_lang_en" ]; then
    line="[![en](https://github.com/zeroincombenze/grymb/blob/master/flags/en_US.png)](https://www.facebook.com/groups/openerp.italia/)"
  elif [ "$3" == "CHPT_lang_it" ]; then
    line="[![it](https://github.com/zeroincombenze/grymb/blob/master/flags/it_IT.png)](https://www.facebook.com/groups/openerp.italia/)"
  elif [[ $3 =~ CHPT_ ]]; then
    :
  fi
  echo "$line"
}

cvt_doxygenconf() {
  local fn=$1
  if [ -f $fn ]; then
    local fntmp=$fn.tmp
    rm -f $fntmp
    local line lne submod url p v
    while IFS= read -r line r || [ -n "$line" ]; do
      if [[ $line =~ ^PROJECT_NAME ]]; then
        line="PROJECT_NAME           = \"$PRJNAME\""
      elif [[ $line =~ ^PROJECT_BRIEF ]]; then
        line="PROJECT_BRIEF          = \"$prjdesc\""
      elif [[ $line =~ ^HTML_COLORSTYLE_HUE ]]; then
        line="HTML_COLORSTYLE_HUE    = 93"
      elif [[ $line =~ ^HTML_COLORSTYLE_SAT ]]; then
        line="HTML_COLORSTYLE_SAT    = 87"
      elif [[ $line =~ ^HTML_COLORSTYLE_GAMMA ]]; then
        line="HTML_COLORSTYLE_GAMMA  = 120"
      elif [[ $line =~ ^HTML_COLORSTYLE_GAMMA ]]; then
        line="HTML_COLORSTYLE_GAMMA  = 120"
      elif [[ $line =~ ^JAVADOC_AUTOBRIEF ]]; then
        line="JAVADOC_AUTOBRIEF      = YES"
      elif [[ $line =~ ^OPTIMIZE_OUTPUT_JAVA ]]; then
        line="OPTIMIZE_OUTPUT_JAVA   = YES"
      elif [[ $line =~ ^EXTRACT_STATIC ]]; then
        line="EXTRACT_STATIC         = YES"
      elif [[ $line =~ ^FILTER_SOURCE_FILES ]]; then
        line="FILTER_SOURCE_FILES    = YES"
      elif [[ $line =~ ^INPUT_FILTER ]]; then
        line="INPUT_FILTER           = /usr/bin/doxypy.py"
      elif [[ $line =~ ^HTML_TIMESTAMP ]]; then
        line="HTML_TIMESTAMP         = YES"
      elif [[ $line =~ ^GENERATE_LATEX ]]; then
        line="GENERATE_LATEX         = NO"
      elif [[ $line =~ ^EXCLUDE_PATTERNS ]]; then
        line="EXCLUDE_PATTERNS       = */tests/* "
      fi
      echo "$line" >>$fntmp
    done <"$fn"
    if [ -n "$(diff -q $fn $fntmp)" ]; then
      # run_traced "cp -p $fn $fn.bak"
      # run_traced "mv $fntmp $fn"
      move_n_bak $fntmp $fn
    else
      rm -f $fntmp
    fi
  fi
}

cvt_gitmodule() {
  #cvt_gitmodule(oca|zero)
  if [ -f .gitmodules ]; then
    local fn=.gitmodules
    local fntmp=$fn.tmp
    local urlty=zero-http
    rm -f $fntmp
    local line lne submod url p v
    while IFS= read -r line r || [ -n "$line" ]; do
      if [ "${line:0:1}" == "[" -a "${line: -1}" == "]" ]; then
        lne="${line:1:-1}"
        read p v <<<"$lne"
        submod=${v//\"/}
      else
        lne=$(echo $line)
        IFS== read p v <<<$lne
        lne=$(echo $p)
        if [ "$lne" == "url" ]; then
          url=$(build_odoo_param URL '' $submod $urlty)
          lne=$(echo $v)
          if [ "$lne" != "$url" ]; then
            v="${line//$lne/$url}"
            line="$v"
          fi
        fi
      fi
      echo "$line" >>$fntmp
    done <"$fn"
    if [ -n "$(diff -q $fn $fntmp)" ]; then
      move_n_bak $fntmp $fn
    else
      rm -f $fntmp
    fi
  fi
}

cvt_travis() {
  # cvt_travis(file_travis oca|zero|oia currpt ORIG)
  local fn=$1
  local fntmp=$fn.tmp
  ORGNM=$(build_odoo_param GIT_ORGNM '' '' $2)
  run_traced "tope8 -B -b $odoo_fver $fn"
  run_traced "sed -e \"s|ODOO_REPO=.[^/]*|ODOO_REPO=\\\"$ORGNM|\" -i $fn"
}

cvt_readme() {
  # cvt_readme(file_readme oca|zero|oia currpt ORIG)
  # params: 1=REMOTEREPO, 2=pkgname, 3=odoo_ver, 4=ver(major), 5=helpname
  #         7=repos/pkgname, 8=(txt1)repos 9=(txt2)repos
  [ $opt_verbose -gt 0 ] && echo "Analyzing $1 ..."
  local fn=$1
  local fntmp=$fn.tmp
  local wf=0 nxtwf=0 prewf=0 preline=0
  local Irunbot=0 Ibuild=0 Icoverage=0 Icodecov=0 Iclimate=0 Ilicense=0 Itryit=0 Idocs=0 Ihelp=0 IOCA=0
  local Icright=0 Iaddons=0 Irst=0 Ichat=0 Ilang_en=0 Ilang_it=0 Idiff=0 Iinstall=0
  local line lne1 lne2 REMOTEREPO txtrepos ver ver0 i v w x y
  local ignnextlines=0
  local helpname=
  local OCA_REMOTEREPO OCA_txt1repos OCA_txt2repos
  unset M[*] TKNS[*] REPL[*] ACT[*]
  declare -gA M
  declare -a TKNS REPL ACT RHLP WK
  RHLP[0]="FI=l10n-italy-supplemental:l10n-italy"
  RHLP[1]="FI=account-:bank-:analytic:l10n_it"
  RHLP[2]="MM=product-"
  RHLP[3]="LO=stock-:purchase"
  RHLP[4]="SD=stock-:sale"
  i=0
  while [ $i -lt ${#RHLP[@]} ]; do
    x=${RHLP[$i]}
    IFS== read p v <<<$x
    w=${v//:/ }
    for v in $w; do
      if [[ "$PKGNAME" =~ "$v" ]] || [[ "$REPOSNAME" =~ "$v" ]]; then
        helpname=$p
        break
      fi
    done
    if [ -n "$helpname" ]; then
      break
    fi
    ((i++))
  done
  [ -z "$BRANCH" ] && BRANCH=master
  ver=$(get_ver)
  ver0=$(get_ver "$PRJNAME")
  OCA_REMOTEREPO=OCA
  OCA_txt1repos=repos
  OCA_txt2repos=r
  if [ "$2" == "oca" ]; then
    REMOTEREPO=$OCA_REMOTEREPO
    txt1repos=$OCA_txt1repos
    txt2repos=OCA_txt2repos
  elif [ "$2" == "zeroincombenze" -o "$2" == "zero" ]; then
    REMOTEREPO=zeroincombenze
    txt1repos=repos/github
    txt2repos=github
  elif [ "$2" == "oia" ]; then
    REMOTEREPO=Odoo-Italia-Associazione
    txt1repos=repos/github
    txt2repos=github
  fi
  M[1]=$REMOTEREPO
  if [ "$PRJNAME" == "tools" -o "$PKGNAME" == "tools" ]; then
    M[2]=tools
  elif [ "$LGITPATH" == "$HOME/tools/$PKGNAME" ]; then # Just for debug
    M[2]=tools
  else
    M[2]=$PKGNAME
  fi
  M[3]=$BRANCH
  M[4]=$ver
  M[5]=$helpname
  if [ -z "$REPOSNAME" ]; then
    M[7]=${M[2]}
  elif [ "$LGITPATH" == "$HOME/tools/$PKGNAME" ]; then # Just for debug
    M[7]=${M[2]}
  else
    M[7]=$REPOSNAME
  fi
  M[8]=$txt1repos
  M[9]=$txt2repos
  v=${M[7]}
  M[LNK_BUILD]="https://travis-ci.org/$REMOTEREPO/$v"
  M[BTN_BUILD]="https://travis-ci.org/$REMOTEREPO/$v.svg?branch=$BRANCH"
  if [ $ver0 -ge 10 -a "$PRJNAME" == "Odoo" ]; then
    M[LNK_LICENSE]="https://www.gnu.org/licenses/lgpl.html"
    M[BTN_LICENSE]="https://img.shields.io/badge/licence-LGPL--3-7379c3.svg"
  else
    M[LNK_LICENSE]="http://www.gnu.org/licenses/agpl-3.0.html"
    M[BTN_LICENSE]="https://img.shields.io/badge/licence-AGPL--3-blue.svg"
  fi
  M[LNK_COVERAGE]="https://coveralls.io/$txt2repos/$REMOTEREPO/$v?branch=$BRANCH"
  M[BTN_COVERAGE]="https://coveralls.io/$txt1repos/$REMOTEREPO/$v/badge.svg?branch=$BRANCH"
  M[LNK_OCA_COVERAGE]="https://coveralls.io/$OCA_txt2repos/$OCA_REMOTEREPO/$v?branch=$BRANCH"
  M[BTN_OCA_COVERAGE]="https://coveralls.io/$OCA_txt1repos/$OCA_REMOTEREPO/$v/badge.svg?branch=$BRANCH"
  if [ -z "$REPOSNAME" ]; then
    M[LNK_CODECOV]="https://codecov.io/gh/$REMOTEREPO/$v/branch/$BRANCH"
  else
    M[LNK_CODECOV]="https://codecov.io/gh/$REMOTEREPO/$v/branch/$BRANCH"
  fi
  M[LNK_OCA_CODECOV]="https://codecov.io/gh/$OCA_REMOTEREPO/$v/branch/$BRANCH"
  M[BTN_CODECOV]="https://codecov.io/gh/$REMOTEREPO/$v/branch/$BRANCH/graph/badge.svg"
  M[BTN_OCA_CODECOV]="https://codecov.io/gh/$OCA_REMOTEREPO/$v/branch/$BRANCH/graph/badge.svg"
  if [ "$PRJNAME" == "Odoo" ]; then
    M[LNK_DOCS]="http://wiki.zeroincombenze.org/en/Odoo/$BRANCH/dev"
    M[BTN_DOCS]="http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-$ver.svg"
  elif [ "$PKGNAME" == "tools" ]; then
    M[LNK_DOCS]="http://wiki.zeroincombenze.org/en/Python/opt"
    M[BTN_DOCS]="http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-$PKGNAME.svg"
  elif [ "$PKGNAME" != "tools" ]; then
    M[LNK_DOCS]="http://wiki.zeroincombenze.org/en/Python/opt/$PKGNAME"
    M[BTN_DOCS]="http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-$PKGNAME.svg"
  fi
  if [ "$PRJNAME" == "Odoo" ]; then
    M[LNK_HELP]="http://wiki.zeroincombenze.org/en/Odoo/$BRANCH/man/$helpname"
    M[BTN_HELP]="http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-$ver.svg"
  elif [ "$PKGNAME" == "tools" ]; then
    M[LNK_HELP]="http://wiki.zeroincombenze.org/en/Python/opt"
    M[BTN_HELP]="http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-$PKGNAME.svg"
  else
    M[LNK_HELP]="http://wiki.zeroincombenze.org/en/Python/opt/$PKGNAME/help"
    M[BTN_HELP]="http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-$PKGNAME.svg"
  fi
  local CHAT_HOME=$(get_cfg_value 0 "CHAT_HOME")
  M[LNK_CHAT]="$CHAT_HOME"
  M[BTN_CHAT]="https://www.shs-av.com/wp-content/chat_with_us.gif"

  TKNS[0]="^\.\.[[:space:]][|_][a-zA-Z_]+"
  REPL[0]="⌂"
  ACT[0]="REPL"
  TKNS[1]="^\.\.[[:space:]]image::.*chat_with_us"
  REPL[1]="⌂"
  ACT[1]="REPL1"
  TKNS[2]="^[[:space:]]+:[a-zA-Z_]+:"
  REPL[2]="⌂"
  ACT[2]="REPLC"
  TKNS[3]="^[^a-zA-Z_]*Build.Status.*https://travis-ci.org/"
  REPL[3]="[![Build Status]"
  ACT[3]="md_BTN_build"
  TKNS[4]="^\|build.status\|"
  REPL[4]="|build status|_"
  ACT[4]="rstBTN_build"
  TKNS[5]="^[^a-zA-Z_]*license.*https://img.shields.io/badge/licence-[AL]GPL"
  if [ $ver0 -ge 10 -a "$PRJNAME" == "Odoo" ]; then
    REPL[5]="[![license lgpl]"
    ACT[5]="md_BTN_license"
    TKNS[6]="^\|license.lgpl\|"
    REPL[6]="|license lgpl|_"
    ACT[6]="rstBTN_license"
  else
    REPL[5]="[![license agpl]"
    ACT[5]="md_BTN_license"
    TKNS[6]="^\|license.agpl\|"
    REPL[6]="|license agpl|_"
    ACT[6]="rstBTN_license"
  fi
  TKNS[7]="^[^a-zA-Z_]*Coverage.Status.*https://coveralls.io/"
  REPL[7]="[![Coverage Status]"
  ACT[7]="md_BTN_coverage"
  TKNS[8]="^\|coverage.status\|"
  REPL[8]="|coverage status|_"
  ACT[8]="rstBTN_coverage"
  TKNS[9]="^[^a-zA-Z_]*codecov.*https://codecov.io/gh/"
  REPL[9]="[![codecov]"
  ACT[9]="md_BTN_codecov"
  TKNS[10]="^\|codecov.status\|"
  REPL[10]="|codecov status|_"
  ACT[10]="rstBTN_codecov"
  TKNS[11]="^[^a-zA-Z_]*OCA_project.*https://github.com/OCA/"
  REPL[11]="[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-$ver.svg)](https://github.com/OCA/$v/tree/$BRANCH)"
  ACT[11]="md_BTN_OCA"
  TKNS[12]="^\|oca.project\|"
  REPL[12]="|oca project|_"
  ACT[12]="rstBTN_OCA"
  TKNS[13]="^[^a-zA-Z_]*Code.Climate.*https://codeclimate.com/github/"
  REPL[13]="Code.Climate  https://codeclimate.com/github/"
  ACT[13]="md_BTN_climate"
  TKNS[14]="^\|code.climate\|"
  REPL[14]="|code climate|_"
  ACT[14]="rstBTN_climate"
  TKNS[15]="^[^a-zA-Z_]*Tech.Doc.*(https*://www.odoo.com/documentation/|https*://wiki.zeroincombenze.org/en/)"
  REPL[15]="[![Tech Doc]"
  ACT[15]="md_BTN_docs"
  TKNS[16]="^\|technical.doc\|"
  REPL[16]="|technical doc|_"
  ACT[16]="rstBTN_docs"
  TKNS[17]="^[^a-zA-Z_]*Help.*(https*://www.odoo.com/forum/|https*://wiki.zeroincombenze.org/)"
  REPL[17]="[![Help]"
  ACT[17]="md_BTN_help"
  TKNS[18]="^\|help.zeroincombenze\|"
  REPL[18]="|help zeroincombenze|_"
  ACT[18]="rstBTN_help"
  TKNS[19]="^[^a-zA-Z_]*(Runbot|Build).Status.*https://runbot.odoo-community.org/"
  REPL[19]="Runbot Status  https://runbot.odoo-community.org/"
  ACT[19]="md_BTN_runbot"
  TKNS[20]="^\|runbot.status\|"
  REPL[20]="|runbot status|_"
  ACT[20]="rstBTN_runbot"
  TKNS[21]="^[^a-zA-Z_]*try.it.*http(s)?://www.zeroincombenze.it"
  REPL[21]="[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-$ver.svg)](https://erp$ver.zeroincombenze.it)"
  ACT[21]="md_BTN_tryit"
  TKNS[22]="^\|try.it\|"
  REPL[22]="|try it|_"
  ACT[22]="rstBTN_tryit"
  TKNS[23]="^[^a-zA-Z_]*try.it.*http(s)?://.*\.odoo-italia.org"
  REPL[23]="[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-$ver.svg)](https://odoo$ver.odoo-italia.org)"
  ACT[23]="md_BTN_tryit"
  TKNS[51]="\[//\]:.*#.*end.copyright"
  REPL[51]=""
  ACT[51]="md_END_cright"
  TKNS[52]="\[//\]:.*#.*copyright"
  REPL[52]=""
  ACT[52]="md_BEG_cright"
  TKNS[53]="\.\.\[//\]:.*#.*end.copyright"
  REPL[53]=""
  ACT[53]="rstEND_cright"
  TKNS[54]="\.\.\[//\]:.*#.*copyright"
  REPL[54]=""
  ACT[54]="rstBEG_cright"
  TKNS[55]="chat.with.us"
  REPL[55]="[![chat with us]"
  ACT[55]="md_BTN_chat"
  TKNS[56]="^\|chat.with.us\|"
  REPL[56]=""
  ACT[56]="rstBTN_chat"
  TKNS[57]="\[//\]:.*#.*end addons"
  REPL[57]=""
  ACT[57]="md_END_addons"
  TKNS[58]="\[//\]:.*#.*addons"
  REPL[58]=""
  ACT[58]="md_BEG_addons"
  TKNS[59]="\.\.\[//\]:.*#.*end addons"
  REPL[59]=""
  ACT[59]="rstEND_addons"
  TKNS[60]="\.\.\[//\]:.*#.*addons"
  REPL[60]=""
  ACT[60]="rstBEG_addons"
  TKNS[61]="^Differenze rispetto localizzazione ufficiale Odoo/OCA"
  REPL[61]=""
  ACT[61]="md_BEG_diff"
  TKNS[62]="^Coverage \|"
  REPL[62]=""
  ACT[62]="md_diff_1"
  TKNS[63]="^(Test compatibilità OCA e Odoo|Test con repository OCA e Odoo) \|"
  REPL[63]=""
  ACT[63]="md_diff_2"
  TKNS[64]="\[//\]:.*#.*end install"
  REPL[64]=""
  ACT[64]="md_END_install"
  TKNS[65]="\[//\]:.*#.*install"
  REPL[65]=""
  ACT[65]="md_BEG_install"
  TKNS[66]="\.\.\[//\]:.*#.*end install"
  REPL[66]=""
  ACT[66]="rstEND_install"
  TKNS[67]="\.\.\[//\]:.*#.*install"
  REPL[67]=""
  ACT[67]="rstBEG_install"
  TKNS[100]="^[^a-zA-Z_]*en[^a-zA-Z_]*(https*://www.shs-av.com/wp-content/en_US.png|https*://github.com/zeroincombenze/grymb/blob/master/flags/en_US.png)"
  REPL[100]=""
  ACT[100]="CHPT_lang_en"
  TKNS[101]="^[^a-zA-Z_]*it[^a-zA-Z_]*(https*://www.shs-av.com/wp-content/it_IT.png|https*://github.com/zeroincombenze/grymb/blob/master/flags/it_IT.png)"
  REPL[101]=""
  ACT[101]="CHPT_lang_it"
  TKNS[102]="^======"
  REPL[102]=""
  ACT[102]="CHPT_102"
  TKNS[103]="^-----"
  REPL[103]=""
  ACT[103]="CHPT_103"
  TKNS[104]="^Installation"
  REPL[104]=""
  ACT[104]="CHPT_104"
  TKNS[105]="^Configuration"
  REPL[105]=""
  ACT[105]="CHPT_105"
  TKNS[106]="^Usage"
  REPL[106]=""
  ACT[106]="CHPT_106"
  TKNS[107]="^Known issues / Roadmap"
  REPL[107]=""
  ACT[107]="CHPT_107"
  TKNS[108]="^Bug Tracker"
  REPL[108]=""
  ACT[108]="CHPT_108"
  TKNS[109]="^Credits"
  REPL[109]=""
  ACT[109]="CHPT_109"
  TKNS[110]="^(\[!\[Odoo Community Association\]\]|\[!\[Odoo Italia Associazione\]\])"
  REPL[110]=""
  ACT[110]="CHPT_110"
  TKNS[111]="^(### |)Contributors"
  REPL[111]=""
  ACT[111]="CHPT_111"
  TKNS[112]="^(### |)Funders"
  REPL[112]=""
  ACT[112]="CHPT_112"
  TKNS[113]="^(### |)Maintainer"
  REPL[113]=""
  ACT[113]="CHPT_113"

  local ONLY_OCA="Irunbot Iclimate"
  local ONLY_ZERO="Icright IOCA Idocs Ihelp Ichat Ilang_en Ilang_it Idiff"
  local ONLY_OIA="Icright IOCA Idocs Ihelp Ilang_en Ilang_it Idiff"
  local ONLY_ODOO="IOCA Itryit Iaddons Iinstall"
  local IGNORE_BTNOCA_4_PKG="l10n-italy-supplemental user_contributes"
  rm -f $fntmp
  while IFS= read -r line r || [ -n "$line" ]; do
    # echo "$prewf/$wf/$nxtwf/$Iinstall> line=$line" #debug
    lne1="⌂"
    lne2="⌂"
    Ibutton=0
    prewf=$nxtwf
    nxtwf=0
    for i in {1..23} {51..67} {100..113}; do
      p=${TKNS[$i]}
      if [[ $line =~ $p ]]; then
        if [ "${ACT[$i]}" == "REPL" -o "${ACT[$i]}" == "REPL1" ]; then
          if [ "${ACT[$i]}" == "REPL1" ]; then
            ignnextlines=1
          fi
          line="${REPL[$i]}"
        elif [ "${ACT[$i]}" == "REPLC" ]; then
          if [ $ignnextlines -ne 0 ]; then
            line="${REPL[$i]}"
          fi
        elif [[ "${ACT[$i]}" =~ md_BTN ]] || [[ "${ACT[$i]}" =~ rstBTN ]]; then
          if [[ "${ACT[$i]}" =~ rstBTN ]]; then
            Irst=1
          fi
          ignnextlines=0
          v="${ACT[$i]}"
          v="I${v:7}"
          Ibutton=1
          if [ ${!v} -ne 0 ]; then
            line="⌂"
          elif [[ " $ONLY_OCA " =~ [[:space:]]$v[[:space:]] ]]; then
            if [ "$2" != "oca" ]; then
              line="⌂"
            fi
          elif [[ " $ONLY_ZERO " =~ [[:space:]]$v[[:space:]] ]]; then
            if [ "$2" != "zero" ]; then
              line="⌂"
              eval $v=1
            elif [[ " $IGNORE_BTNOCA_4_PKG " =~ [[:space:]]$PKGNAME[[:space:]] ]]; then
              line="⌂"
              eval $v=1
            fi
          elif [[ " $ONLY_OIA " =~ [[:space:]]$v[[:space:]] ]]; then
            if [ "$2" != "oia" ]; then
              line="⌂"
              eval $v=1
            elif [[ " $IGNORE_BTNOCA_4_PKG " =~ [[:space:]]$PKGNAME[[:space:]] ]]; then
              line="⌂"
              eval $v=1
            fi
          elif [[ " $ONLY_ODOO " =~ [[:space:]]$v[[:space:]] ]]; then
            if [ "$PRJNAME" != "Odoo" ]; then
              line="⌂"
            fi
          fi
          if [ "$line" != "⌂" ]; then
            if [ "$2" == "zeroincombenze" -o "$2" == "zero" -o "$2" == "oia" ]; then
              line="⌂"
            else
              eval $v=1
              line=$(build_line $v "${REPL[$i]}" "${ACT[$i]}")
            fi
          fi
        elif [[ "${ACT[$i]}" =~ CHPT_ ]]; then
          v="${ACT[$i]}"
          v="${v:5}"
          if (($v)); then
            nxtwf=$v
          else
            v=I$v
            if [ ${!v} -ne 0 ]; then
              line="⌂"
            elif [[ " $ONLY_OCA " =~ [[:space:]]$v[[:space:]] ]]; then
              if [ "$2" == "zeroincombenze" -o "$2" == "zero" -o "$2" == "oia" ]; then
                line="⌂"
              fi
            elif [[ " $ONLY_ZERO " =~ [[:space:]]$v[[:space:]] ]]; then
              if [ "$2" == "oca" ]; then
                line="⌂"
              fi
            elif [[ " $ONLY_ODOO " =~ [[:space:]]$v[[:space:]] ]]; then
              if [ "$PRJNAME" != "Odoo" ]; then
                line="⌂"
              fi
            fi
            if [ "$line" != "⌂" ]; then
              eval $v=1
              Ibutton=1
              wf=2
              line=$(build_line $v "$line" "${ACT[$i]}")
            fi
          fi
        elif [ "${ACT[$i]}" == "md_BEG_cright" -o "${ACT[$i]}" == "rstBEG_cright" ]; then
          if [ $Icright -eq 0 ]; then
            Icright=2
          fi
          line="⌂"
        elif [ "${ACT[$i]}" == "md_END_cright" -o "${ACT[$i]}" == "rstEND_cright" ]; then
          if [ $Icright -eq 2 ]; then
            Icright=3
            add_copyright $fntmp $Irst $2
          fi
          line="⌂"
        elif [ "${ACT[$i]}" == "md_BEG_addons" -o "${ACT[$i]}" == "rstBEG_addons" ]; then
          if [ $Iaddons -eq 0 ]; then
            Iaddons=2
          fi
          line="⌂"
        elif [ "${ACT[$i]}" == "md_END_addons" -o "${ACT[$i]}" == "rstEND_addons" ]; then
          if [ $Iaddons -eq 2 ]; then
            Iaddons=3
            add_addons $fntmp $Irst "$2" "$4"
          fi
          line="⌂"
        elif [ "${ACT[$i]}" == "md_BEG_install" -o "${ACT[$i]}" == "rstBEG_install" ]; then
          # echo "> begin install <$line>" #debug
          if [ $Iinstall -eq 0 ]; then
            Iinstall=2
          fi
          line="⌂"
        elif [ "${ACT[$i]}" == "md_END_install" -o "${ACT[$i]}" == "rstEND_install" ]; then
          # echo "> end install <$line>" #debug
          if [ $Iinstall -eq 2 ]; then
            Iinstall=3
            add_install $fntmp $Irst "$2" "$4"
          fi
          line="⌂"
        elif [ "${ACT[$i]}" == "md_BEG_diff" ]; then
          if [ $Idiff -eq 0 ]; then
            Idiff=2
          fi
        elif [ "${ACT[$i]}" == "md_diff_1" ]; then
          if [ $Idiff -eq 2 ]; then
            if [ "$BRANCH" == "7.0" ]; then
              line="Coverage |  [![codecov](${M[BTN_CODECOV]})](${M[LNK_CODECOV]}) | [![Coverage Status](${M[BTN_OCA_COVERAGE]})](${M[LNK_OCA_COVERAGE]})"
            else
              line="Coverage |  [![codecov](${M[BTN_CODECOV]})](${M[LNK_CODECOV]}) | [![codecov](${M[BTN_OCA_CODECOV]})](${M[LNK_OCA_CODECOV]})"
            fi
          fi
        elif [ "${ACT[$i]}" == "md_diff_2" ]; then
          if [ $Idiff -eq 2 ]; then
            if [ "$BRANCH" == "7.0" ]; then
              line="Test compatibilità OCA e Odoo | :x: | [Errore import decimal precision](https://github.com/OCA/OCB/issues/629)"
            else
              line="Test compatibilità OCA e Odoo | :white_check_mark: | :white_check_mark:"
            fi
          fi
        fi
        break
      elif [ -n "$line" ] && [[ "${ACT[$i]}" =~ rstBTN ]]; then
        p=${TKNS[$i]}
        p="..[[:space:]]${p:1}"
        if [[ $line =~ $p ]]; then
          ignnextlines=0
          line="${REPL[0]}"
          break
        else
          p=${TKNS[$i]}
          p="..[[:space:]]_${p:3}"
          p=${p/\\\|/:}
          if [[ $line =~ $p ]]; then
            ignnextlines=0
            line="${REPL[0]}"
            break
          fi
        fi
      fi
    done
    if [ $Ibutton -eq 0 -a $wf -eq 0 ] && [ "$2" == "zeroincombenze" -o "$2" == "zero" -o "$2" == "oia" ]; then
      lne1="⌂"
      wf=1
      for i in {1..23}; do
        p=${TKNS[$i]}
        if [[ "${ACT[$i]}" =~ md_BTN ]] || [[ "${ACT[$i]}" =~ rstBTN ]]; then
          v="${ACT[$i]}"
          v="I${v:7}"
          if [ $Irst -gt 0 ] && [[ "${ACT[$i]}" =~ md_BTN ]]; then
            :
          elif [ $Irst -eq 0 ] && [[ "${ACT[$i]}" =~ rstBTN ]]; then
            :
          elif [ "$2" == "zeroincombenze" -o "$2" == "zero" -o "$2" == "oia" ] && [[ " $ONLY_OCA " =~ [[:space:]]$v[[:space:]] ]]; then
            :
          elif [ "$2" == "oca" ] && [[ " $ONLY_ZERO " =~ [[:space:]]$v[[:space:]] ]]; then
            :
          elif [ "$PRJNAME" != "Odoo" ] && [[ " $ONLY_ODOO " =~ [[:space:]]$v[[:space:]] ]]; then
            :
          elif [ ${!v} -eq 0 ]; then
            eval $v=1
            lne1=$(build_line $v "${REPL[$i]}" "${ACT[$i]}")
            echo "$lne1" >>$fntmp
            if [ -z "$lne1" ]; then preline=0; else preline=1; fi
          fi
        fi
      done
      [ $preline -ne 0 ] && [ -n "$line" ] && preline=0 && echo "" >>$fntmp
    fi
    # echo "> if [ \$Icright=$Icright -ne 2 -a  \$Iinstall=$Iinstall -ne 2 -a $line != '⌂' ]; then" #debug
    if [ $Icright -ne 2 -a $Iaddons -ne 2 -a $Iinstall -ne 2 -a "$line" != "⌂" ]; then
      line=$(expand_macro "$line")
      line="$(echo "$line" | sed -e 's:OpenERP:Odoo:' -e 's:openerp\.com:odoo.com:')"
      line="$(echo "$line" | sed -e 's:formerly *Odoo:formerly OpenERP:' -e 's:formerly *odoo:formerly OpenERP:')"
      if [ -n "$line" ]; then
        # [ $wf -ge 104 ] && echo "> if [ -n \"$line\" ]; then" #debug
        if [ $wf -eq 1 ]; then
          if [ $Ilang_en -eq 0 ]; then
            echo "" >>$fntmp
            echo "[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)" >>$fntmp
            echo "" >>$fntmp
          fi
          Ilang_en=1
          if [ $nxtwf -ne 100 ]; then
            wf=2
          fi
        fi
        # [ $wf -ge 104 ] && echo ">   if [ \$wf=$wf -eq 2 ]; then" #debug
        if [ $wf -eq 2 ]; then
          echo "$line" >>$fntmp
          if [ $Ibutton -eq 0 ] && [[ $line =~ ^[A-Za-z] ]]; then
            x=${#line}
            w="================================================================================================"
            v=${w:0:$x}
            echo "$v" >>$fntmp
            wf=104
          fi
        elif [ $wf -gt 100 ] && [ $nxtwf -eq 102 -o $nxtwf -eq 103 ]; then
          # [ $wf -ge 104 ] && echo ">   elif [ \$wf=$wf -gt 100 ] && [ \$nxtwf=$nxtwf -eq 102 -o \$nxtwf -eq 103 ]; then" #debug
          :
        elif [ $wf -lt 100 -o $nxtwf -ge 104 ]; then
          # [ $wf -ge 104 ] && echo ">   elif [ \$wf=$wf -lt 100 -o \$nxtwf=$nxtwf -ge 104 ]; then" #debug
          if [ $wf -lt 104 ]; then
            wf=104
          fi
          while [ $wf -le $nxtwf ]; do
            if [ $wf -ne 110 ]; then
              w=${TKNS[$wf]}
              v=${w:1}
              if [[ "$w" =~ "###" ]]; then
                w="$v"
                IFS=")" read x v <<<$w
                if [ -z "$v" ]; then v=$x; fi
                v="### $v"
              else
                echo "$v" >>$fntmp
                x=${#v}
                w="-----------------------------------------------------------------------------------------------"
                v=${w:0:$x}
              fi
              echo "$v" >>$fntmp
              ((wf++))
              if [ $wf -le $nxtwf ]; then echo "" >>$fntmp; fi
            else
              ((wf++))
            fi
          done
        else
          if [ $prewf -ge 104 ]; then
            # echo ">  echo ''" #debug
            echo "" >>$fntmp
          fi
          # [ $wf -ge 104 ] && echo ">   else" #debug
          echo "$line" >>$fntmp
        fi
      else
        # [ $wf -ge 104 ] && echo "> else" #debug
        echo "$line" >>$fntmp
      fi
      if [ -z "$line" ]; then preline=0; else preline=1; fi
    fi
    if [ "$lne2" != "⌂" ]; then
      echo "$lne2" >>$fntmp
      if [ -z "$lne2" ]; then preline=0; else preline=1; fi
    fi
  done <"$fn"
  for i in {51..67}; do
    p=${TKNS[$i]}
    if [ "${ACT[$i]}" == "md_END_cright" -o "${ACT[$i]}" == "rstEND_cright" ]; then
      if [ $Icright -eq 0 ]; then
        [ $preline -ne 0 ] && echo "" >>$fntmp
        Icright=3
        add_copyright $fntmp $Irst $2
        preline=1
      fi
    elif [ "${ACT[$i]}" == "md_END_addons" -o "${ACT[$i]}" == "rstEND_addons" ]; then
      if [ $Iaddons -eq 0 ]; then
        [ $preline -ne 0 ] && echo "" >>$fntmp
        Iaddons=3
        # add_addons $fntmp $Irst "$2" "$4"
        preline=1
      fi
    elif [ "${ACT[$i]}" == "md_END_install" -o "${ACT[$i]}" == "rstEND_install" ]; then
      if [ $Iinstall -eq 0 ]; then
        [ $preline -ne 0 ] && echo "" >>$fntmp
        Iinstall=3
        # add_install $fntmp $Irst "$2" "$4"
        preline=1
      fi
    elif [ $Irst -ne 0 ] && [[ ${ACT[$i]} =~ rstBTN ]]; then
      v="${ACT[$i]}"
      v="I${v:7}"
      eval $v=1
    fi
  done
  [ $preline -ne 0 ] && preline=0 && echo "" >>$fntmp
  for i in {1..23} {51..67}; do
    p=${TKNS[$i]}
    if [ $Irst -eq 0 -a $i -ge 50 ] && [[ "${ACT[$i]}" =~ md_BTN ]]; then
      v="${ACT[$i]}"
      v="I${v:7}"
      if [ ${!v} -eq 0 ]; then
        eval $v=1
        line=$(build_line $v "${REPL[$i]}" "${ACT[$i]}")
        echo "$line" >>$fntmp
      fi
    elif [ $Irst -ne 0 ] && [[ "${ACT[$i]}" =~ rstBTN ]]; then
      v="${ACT[$i]}"
      v="I${v:7}"
      if [ ${!v} -eq 1 ]; then
        eval $v=2
        line=$(build_line $v "${REPL[$i]}" "${ACT[$i]}/1")
        echo "$line" >>$fntmp
        line=$(build_line $v "${REPL[$i]}" "${ACT[$i]}/2")
        echo "$line" >>$fntmp
      fi
    fi
  done
  if [ ${test_mode:-0} -eq 0 -a $do_proc -gt 0 ]; then
    if [ -n "$(diff -q $fn $fntmp)" ]; then
      move_n_bak $fntmp $fn
    else
      rm -f $fntmp
    fi
  fi
}

cvt_file() {
  # cvt_file(file oca|zero|powerp travis|readme|manifest currpt ORIG)
  local f1=$1
  local sts=$STS_SUCCESS
  if [ -n "$f1" ]; then
    if [ -f "$1" ]; then
      local b=$(basename $f1)
      local d=$(dirname $f1)
      if [[ $f1 =~ $PWD ]]; then
        local l=${#PWD}
        ((l++))
        local ft=${f1:l}
      elif [ "${f1:0:2}" == "./" ]; then
        local ft=${f1:2}
      else
        local ft=$f1
      fi
      local f1_oca=$(dirname $f1)/${b}.oca
      local f1_z0i=$(dirname $f1)/${b}.z0i
      local f1_oia=$(dirname $f1)/${b}.oia
      if [ "$2" == "zero" -o -z "$2" ]; then
        local f1_new=$f1_z0i
      else
        local f1_new=$(dirname $f1)/${b}.$2
      fi
      if [ "$4" == "zero" -o -z "$4" ]; then
        local f1_cur=$f1_z0i
      else
        local f1_cur=$(dirname $f1)/${b}.$4
      fi
      if [ "$2" == "$4" -a $opt_force -eq 0 ]; then
        local do_proc=0
      else
        local do_proc=1
      fi
      local fntmp=$f1.tmp
      if [ -f $f1_new ]; then
        if [ -f "$f1_oca" -a -f "$f1_oia" -a -f "$f1_zoi" ]; then
          :
        else
          move $f1 $f1_cur
        fi
        move $f1_new $f1
        do_proc=1
      elif [ $opt_force -ne 0 -a ! -f $f1_cur -a "$3" != "graph" -a "$3" != "xml" -a "$3" != "css" -a "$3" != "sass" ]; then
        if [ -f "$f1_cur" ]; then rm -f $f1_cur; fi
        run_traced "cp -p $f1 $f1_cur"
        do_proc=1
      fi
      if [ $opt_orig -gt 0 -a -f ./tmp/$ft ]; then
        run_traced "mv -f $f1 ${f1}.bak"
        run_traced "cp -p ./tmp/$ft $f1"
      fi
      if [ "$3" == "travis" ]; then
        cvt_travis $f1 "$2" "$4" "$5"
      elif [ "$3" == "readme" ] && [ ${test_mode:-0} -ne 0 -o $do_proc -gt 0 ]; then
        cvt_readme $f1 "$2" "$4" "$5"
      fi
      if [ -f $f1_cur ] && [ $opt_force -eq 0 -o "$3" == "manifest" ]; then
        diff -q $f1 $f1_cur &>/dev/null
        if [ $? -eq 0 ]; then
          run_traced "rm -f $f1_cur"
        fi
      fi
    else
      echo "File $f1 not found!"
    fi
  else
    local f1=
    echo "Missed parameter! use:"
    echo "\$ please distribution oca|zero|oia"
    sts=$STS_FAILED
  fi
  return $sts
}

set_remote_info() {
  #set_remote_info (REPOSNAME odoo_vid odoo_org)
  local REPOSNAME=$1
  if [ "$(build_odoo_param VCS $2)" == "git" ]; then
    local odoo_fver=$(build_odoo_param FULLVER "$2")
    local DUPSTREAM=$(build_odoo_param RUPSTREAM "$2" "default" $3)
    local RUPSTREAM=$(build_odoo_param RUPSTREAM "$2" "" $3)
    local DORIGIN=$(build_odoo_param RORIGIN "$2" "default" $3)
    local RORIGIN=$(build_odoo_param RORIGIN "$2" "" $3)
    if [[ ! "$DUPSTREAM" == "$RUPSTREAM" ]]; then
      [[ -n "$RUPSTREAM" ]] && run_traced "git remote remove upstream"
      [[ -n "$DUPSTREAM" ]] && run_traced "git remote add upstream $DUPSTREAM"
    fi
    if [[ ! "$DORIGIN" == "$RORIGIN" ]]; then
      [[ -n "$RORIGIN" ]] && run_traced "git remote remove origin"
      [[ -n "$DORIGIN" ]] && run_traced "git remote add origin $DORIGIN"
    fi
  elif [ ${test_mode:-0} -eq 0 ]; then
    echo "No git repositoy $REPOSNAME!"
  fi
}

mvfiles() {
  # mvfiles(srcpath, tgtpath, files, owner)
  if [ -z "$3" ]; then
    local l="*"
  else
    local l="$3"
  fi
  local CWD=$PWD
  local sts=$STS_SUCCESS
  local f
  if [ -d $1 -a -n "$2" ]; then
    if [ -d $2 ]; then
      cd $1
      for f in $l; do
        if [ -e $1/$f ]; then
          run_traced "mv -f $1/$f $2/$f"
          if [ $4 ]; then
            run_traced "chown $4 $2/$f"
          fi
        else
          elog "! File $1/$f not found!!"
          sts=$STS_FAILED
        fi
      done
    else
      elog "! Directory $2 not found!!"
      sts=$STS_FAILED
    fi
  else
    elog "! Directory $1 not found!!"
    sts=$STS_FAILED
  fi
  cd $CWD
  return $sts
}

create_pubblished_index() {
  # create_pubblished_index(index_dir) {
  local f
  run_traced "cd $1"
  cat <<EOF >index.html
<!DOCTYPE HTML>
<html>
    <head>
        <title>Speed Test</title>
    </head>
    <body>
    <table>
EOF
  for f in *; do
    if [ "$f" != "index.html" ]; then
      echo "        <tr><td>$f</td></tr>" >>index.html
    fi
  done
  echo "    </body>" >>index.html
  echo "</html>" >>index.html
}

merge_cfg() {
  #merge_cfg(cfgfn)
  local cfgfn=$1 fbak ftmp f line ln
  local tmpl
  tmpl=$HOME/pypi/tools/install_tools.sh
  ftmp=$cfgfn.tmp
  [[ -f $ftmp ]] && rm -f $ftmp
  f=0
  while IFS= read -r line || [ -n "$line" ]; do
    if [[ $line =~ ^RFLIST__ ]]; then
      if [ $f -eq 0 ] && [[ -f $tmpl ]]; then
        while IFS= read -r ln || [ -n "$ln" ]; do
          [[ $ln =~ ^RFLIST__ ]] && echo "$ln" >>$ftmp
        done <$tmpl
      fi
      f=1
    else
      echo "$line" >>$ftmp
    fi
  done <$1
  fbak=$cfgfn.bak
  [[ -f $fbak ]] && rm -f $fbak
  [[ -f $cfgfn ]] && mv $cfgfn $fbak
  [[ -f $ftmp ]] && mv $ftmp $cfgfn
}

do_publish() {
  #do_publish PKGNAME (docs|download|pypi|svg|testpypi)
  wlog "do_publish $1 $2"
  local cmd="do_publish_$1"
  sts=$STS_SUCCESS
  if [ "$(type -t $cmd)" == "function" ]; then
    eval $cmd "$@"
  else
    echo "Missing object! Use:"
    echo "> please publish (docs|download|pypi|svg|testpypi)"
    echo "publish docs     -> publish generate docs to website (require system privileges)"
    echo "   type 'please docs' to generate docs files"
    echo "publish download -> publish tarball to download (require system privileges)"
    echo "   type 'please build' to generate tarball file"
    echo "publish pypi     -> publish package to pypi website (from odoo user)"
    echo "publish svg      -> publish test result svg file (require system privileges)"
    echo "publish tar      -> write a tarball with package files"
    echo "publish testpypi -> publish package to testpypi website (from odoo user)"
    sts=$STS_FAILED
  fi
  return $sts
}

do_publish_svg() {
  #do_publish_svg pgkname svg (prd|dev)
  local sts=$STS_FAILED
  local HTML_SVG_DIR=$(get_cfg_value 0 "HTML_SVG_DIR")
  local DEV_SVG=$(get_cfg_value 0 "DEV_SVG")
  if [ $EUID -ne 0 ]; then
    echo "!!Error: no privilege to publish svg!!"
    return $sts
  fi
  if [ "$HOSTNAME" == "$PRD_HOST" ]; then
    local tgt="prd"
  elif [ "$HOSTNAME" == "$DEV_HOST" ]; then
    local tgt="dev"
  else
    local tgt=""
  fi
  if [ ! -d $HTML_SVG_DIR ]; then
    run_traced "mkdir -p $HTML_SVG_DIR"
    run_traced "chown apache:apache $HTML_SVG_DIR"
    if [ ! -d $HTML_SVG_DIR/$tgt ]; then
      run_traced "mkdir -p $HTML_SVG_DIR/$tgt"
      run_traced "chown apache:apache $HTML_SVG_DIR/$tgt"
    fi
  fi
  mvfiles "$DEV_SVG" "$HTML_SVG_DIR/$tgt" "*.svg" "apache:apache"
  local sts=$?
  if [ "$HOSTNAME" == "$DEV_HOST" ]; then
    scpfiles "$HTML_SVG_DIR/$tgt" "$PRD_HOST:$HTML_SVG_DIR/$tgt" "*.svg"
    local s=$?
    [ $sts -eq $STS_SUCCESS ] && sts=$s
  fi
  return $sts
}

do_publish_docs() {
  #do_publish_svg pgkname docs
  local sts=$STS_FAILED
  if [ $EUID -ne 0 ]; then
    echo "!!Error: no privilege to publish documentation!!"
    return $sts
  fi
  local HTML_DOCS_DIR=$(get_cfg_value "" "HTML_DOCS_DIR")
  if [ -d $HTML_DOCS_DIR/$1 ]; then
    run_traced "rm -fR $HTML_DOCS_DIR/$1"
  fi
  if [ ! -d $HTML_DOCS_DIR/$1 ]; then
    run_traced "mkdir -p $HTML_DOCS_DIR/$1"
    run_traced "chown apache:apache $HTML_DOCS_DIR/$1"
  fi
  mvfiles "$PRJPATH/html" "$HTML_DOCS_DIR/$1" "" "apache:apache"
  local sts=$?
  rmdir $PRJPATH/html
  if [ -d $PRJPATH/latex ]; then
    rm -fR $PRJPATH/latex
  fi
  if [ $opt_verbose -gt 0 ]; then
    echo ""
    echo -e "see \e[1mdocs.zeroincombenze.org/$1\e[0m webpage"
  fi
  return $sts
}

do_publish_download() {
  #do_publish_download pgkname
  local f n s v
  local sts=$STS_FAILED
  if [ $EUID -ne 0 ]; then
    echo "!!Error: no privilege to publish download!!"
    return $sts
  fi
  local HTML_DOWNLOAD_DIR=$(get_cfg_value "" "HTML_DOWNLOAD_DIR")
  if [ "$PRJNAME" != "Odoo" ]; then
    if [ ! -d $HTML_DOWNLOAD_DIR ]; then
      run_traced "mkdir -p $HTML_DOWNLOAD_DIR"
      run_traced "chown apache:apache $HTML_DOWNLOAD_DIR"
    fi
    run_traced "cd $PKGPATH"
    s=$?; [ ${s-0} -ne 0 ] && sts=$s
    n=$(cat setup.py | grep "name *=" | awk -F= '{print $2}' | grep -Eo [a-zA-Z0-9_-]+ | head -n1)
    v=$(cat setup.py | grep version | grep -Eo [0-9]+\.[0-9]+\.[0-9]+ | head -n1)
    f=$(ls -1 $n*$v*tar.gz)
    # f=$n*$v*tar.gz
    if [ -n "$f" -a -f "$f" ]; then
      mvfiles "$PKGPATH" "$HTML_DOWNLOAD_DIR" "$f" "apache:apache"
      sts=$?
      if [ $sts -eq $STS_SUCCESS ]; then
        run_traced "cp $HTML_DOWNLOAD_DIR/$f $HTML_DOWNLOAD_DIR/$n.tar.gz"
        run_traced "chown apache:apache $HTML_DOWNLOAD_DIR/$n.tar.gz"
        create_pubblished_index "$HTML_DOWNLOAD_DIR"
        if [ $opt_verbose -gt 0 ]; then
          echo ""
          echo -e "You can download this package typing"
          echo -e "\$ wget http://download.zeroincombenze.org/$n.tar.gz"
        fi
      fi
    else
      echo "Source $n*$v*tar.gz file non found!"
    fi
  fi
  return $sts
}

do_publish_testpypi() {
  do_publish_pypi testpypi
}

do_publish_pypi() {
  #do_publish_pypi repos
  local sts=$STS_SUCCESS
  local rpt=$1
  local n p s v
  [[ -z $rpt || ! $rpt =~ (pypi|testpypi) ]] && rpt=pypi
  if [[ "$PRJNAME" != "Odoo" ]]; then
    if twine --version &>/dev/null; then
      run_traced "cd $PKGPATH"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
      [[ -f $PRJPATH/README.rst ]] && run_traced "cp $PRJPATH/README.rst ./"
      v=$(python setup.py --version)
      n=$(python setup.py --name)
      p=$(find dist -name "${n}-${v}.tar.gz")
      if [[ -z "$p" || $opt_force -gt 0 ]]; then
        run_traced "python setup.py build sdist"
        s=$?; [ ${s-0} -ne 0 ] && sts=$s
      fi
      p=$(find dist -name "${n}-${v}.tar.gz")
      [[ -z $p ]] && echo "Internal error: file tar not found!" && return 127
      run_traced "twine upload $p -r $rpt"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    else
      echo "Command twine not found!"
      echo "Do pip install twine"
      sts=1
    fi
  fi
  return $sts
}

do_register_pypi() {
  #do_register_pypi pgkname
  local sts=$STS_SUCCESS
  local rpt=testpypi
  local n p s v
  if [ "$PRJNAME" != "Odoo" ]; then
    run_traced "cd $PKGPATH"
    s=$?; [ ${s-0} -ne 0 ] && sts=$s
    n=$(cat setup.py | grep "name *=" | awk -F= '{print $2}' | grep -Eo [a-zA-Z0-9_-]+ | head -n1)
    v=$(cat setup.py | grep version | grep -Eo [0-9]+[0-9\.]* | head -n1)
    p=$(find dist -name "$n*$v*.whl")
    if [ -z "$p" -o $opt_force -gt 0 ]; then
      run_traced "python setup.py bdist_wheel --universal"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    fi
    p=$(find dist -name "$n*$v*.whl")
    run_traced "twine register $p -r $rpt"
    s=$?; [ ${s-0} -ne 0 ] && sts=$s
  fi
  return $sts
}

do_register_testpypi() {
  #do_register_testpypi pgkname
  local sts=$STS_SUCCESS
  local rpt=testpypi
  local n p s v
  if [ "$PRJNAME" != "Odoo" ]; then
    run_traced "cd $PKGPATH"
    s=$?; [ ${s-0} -ne 0 ] && sts=$s
    n=$(cat setup.py | grep "name *=" | awk -F= '{print $2}' | grep -Eo [a-zA-Z0-9_-]+ | head -n1)
    v=$(cat setup.py | grep version | grep -Eo [0-9]+[0-9\.]* | head -n1)
    p=$(find dist -name "$n*$v*.whl")
    if [ -z "$p" -o $opt_force -gt 0 ]; then
      run_traced "python setup.py bdist_wheel --universal"
      s=$?; [ ${s-0} -ne 0 ] && sts=$s
    fi
    p=$(find dist -name "$n*$v*.whl")
    run_traced "twine register $p -r $rpt"
    s=$?; [ ${s-0} -ne 0 ] && sts=$s
  fi
  return $sts
}

do_annotate() {
  wlog "Outdated function: annotate"
  return $STS_FAILED
}

do_edit() {
  #do_edit PKGNAME (pofile|translation|untranslated)
  local cmd
  wlog "do_edit $1 $2"
  cmd="do_edit_$1"
  sts=$STS_SUCCESS
  if [ "$(type -t $cmd)" == "function" ]; then
    eval $cmd "$@"
  else
    echo "Missing object! Use:"
    echo "> please edit (pofile|translation|translation_from_pofile|untranslated)"
    sts=$STS_FAILED
  fi
  return $sts
}

do_edit_pofile() {
  [[ -f "./i18n/it.po" ]] && run_traced "poedit ./i18n/it.po" || echo "No file it.po found!"
  return $STS_STS_SUCCESS
}

do_edit_translation() {
  local xfile
  [[ -f "$HOME/dev/pypi/tools/odoo_default_tnl.xlsx" ]] && xfile="$HOME/dev/pypi/tools/odoo_default_tnl.xlsx"
  [[ -f "$HOME/pypi/tools/odoo_default_tnl.xlsx" ]] && xfile="$HOME/pypi/tools/odoo_default_tnl.xlsx"
  [[ -n "$xfile" ]] && run_traced "libreoffice $xfile" || echo "No file odoo_default_tnl.xlsx found!"
  return $STS_STS_SUCCESS
}

do_edit_translation_from_pofile() {
  local xfile
  local confn db module odoo_fver sts=$STS_FAILED opts pyv pofile
  if [[ ! "$PRJNAME" == "Odoo" ]]; then
    echo "No Odoo module"
    return $STS_FAILED
  fi
  module="."
  odoo_fver=$(build_odoo_param FULLVER '.')
  pofile="$(build_odoo_param PKGPATH '.')/i18n/it.po"
  module=$(build_odoo_param PKGNAME '.')
  if [[ -z "$odoo_fver" || -z "$module" ]]; then
    echo "Invalid Odoo environment!"
    return $STS_FAILED
  fi
  odoo_ver=$(echo $odoo_fver | grep -Eo [0-9]+ | head -n1)
  if [[ ! -f "$pofile" ]]; then
    echo "File $pofile not found!"
    return $STS_FAILED
  fi
  pyv=$(python3 --version 2>&1 | grep -Eo "[0-9]+\.[0-9]+")
  [[ -n "$pyv" ]] && pyver="-p $pyv"
  pyver="-p 2.7" #debug
  [[ ! -d $HOME/clodoo/venv ]] && \
    run_traced "vem $pyver create $HOME/clodoo/venv" && \
    run_traced "vem $HOME/clodoo/venv install xlrd" && \
    run_traced "vem $HOME/clodoo/venv install Babel" && \
    run_traced "vem $HOME/clodoo/venv install clodoo"
  run_traced "pushd $HOME/clodoo >/dev/null"
  [ $opt_verbose -ne 0 ] && opts="-v" || opts="-q"
  [ $opt_dbg -ne 0 ] && opts="${opts}B"
  run_traced "vem $HOME/clodoo/venv exec \"odoo_translation.py $opts -b$odoo_fver -m $module -R $pofile\""
  sts=$?
  run_traced "popd >/dev/null"
  return $sts

  [[ -f "$HOME/dev/pypi/tools/odoo_default_tnl.xlsx" ]] && xfile="$HOME/dev/pypi/tools/odoo_default_tnl.xlsx"
  [[ -f "$HOME/pypi/tools/odoo_default_tnl.xlsx" ]] && xfile="$HOME/pypi/tools/odoo_default_tnl.xlsx"
  [[ -n "$xfile" ]] && run_traced "libreoffice $xfile" || echo "No file odoo_default_tnl.xlsx found!"
  return $STS_STS_SUCCESS
}

do_edit_untranslated() {
  local xfile
  [[ -f "$HOME/odoo_default_tnl.csv" ]] && run_traced "libreoffice $HOME/odoo_default_tnl.csv" || echo "No file odoo_default_tnl.csv found!"
  return $STS_STS_SUCCESS
}

create_pkglist() {
  # create_pkglist(pkgname type)
  local PKGLIST Z0LIB OELIB x
  local xx="$(get_cfg_value 0 filedel)"
  local yy="$(get_cfg_value 0 fileignore)"
  if [ $opt_keep -ne 0 ]; then
    xx="$xx $yy"
  else
    xx="$xx $yy tests/"
  fi
  if [ "$2" == "PkgList" -o "$2" == "binPkgList" -o "$2" == "etcPkgList" ]; then
    PKGLIST=$(cat setup.py | grep "# PKGLIST=" | awk -F= '{print $2}')
    if [ -n "$PKGLIST" ]; then
      PKGLIST="${PKGLIST//,/ }"
    fi
    if [ "$2" == "etcPkgList" ]; then
      x=$(cat setup.py | grep "# BUILD_WITH_Z0LIBR=" | awk -F= '{print $2}')
      if [ "$x" == "1" ]; then
        Z0LIB=$(findpkg z0librc "/etc . ..")
        [ -z "$Z0LIB" ] && Z0LIB=z0librc
      fi
      x=$(cat setup.py | grep "# BUILD_WITH_ODOORC=" | awk -F= '{print $2}')
      if [ "$x" == "1" ]; then
        OELIB=$(findpkg odoorc "/etc $HOME/venv_tools . ..")
        [ -z "$OELIB" ] && OELIB=odoorc
      fi
    fi
    if [ -z "$PKGLIST" -a "$2" == "PkgList" ]; then
      x="find . -type f"
      for f in $xx "setup.*"; do
        if [ "${f: -1}" == "/" ]; then
          x="$x -not -path '*/$f*'"
        else
          x="$x -not -name '*$f'"
        fi
      done
      eval $x >./tmp.log
      PKGLIST="$(cat ./tmp.log | tr '\n' ' ')"
      rm -f ./tmp.log
    fi
  fi
  echo "$PKGLIST $Z0LIB $OELIB"
}

add_file_2_pkg() {
  #add_file_2_pkg(pkgname type)
  local f s
  local PKGLIST=$(create_pkglist "$1" "$2")
  s=0
  for f in $PKGLIST; do
    if [ -f $f ]; then
      :
    elif [ "$2" == "etcPkgList" -a -f /etc/$f ]; then
      :
    elif [ ! -f $PKGPATH/$f ]; then
      s=1
      echo "File $f not found"
      break
    fi
  done
  return $s
}

do_build() {
  #do_build pgkname tar
  local sts=$STS_SUCCESS
  local rpt=pypi
  local f i l n p s v x y PKGLIST invalid PASSED
  local SETUP=./setup.sh
  local xx="$(get_cfg_value 0 filedel)"
  local yy="$(get_cfg_value 0 fileignore)"
  if [ $opt_keep -ne 0 ]; then
    xx="$xx $yy"
  else
    xx="$xx $yy tests/"
  fi
  if [ "$PRJNAME" != "Odoo" ]; then
    run_traced "cd $PKGPATH"
    # run_traced "mkdir -p tmp"
    s=$?; [ ${s-0} -ne 0 ] && sts=$s
    n=$(cat setup.py | grep "name *=" | awk -F= '{print $2}' | grep -Eo [a-zA-Z0-9_-]+ | head -n1)
    v=$(cat setup.py | grep version | grep -Eo [0-9]+\.[0-9]+\.[0-9]+ | head -n1)
    if [ ! -f "$n*$v*tar.gz" -o $opt_force -gt 0 ]; then
      PKGLIST=$(cat setup.py | grep "# PKGLIST=" | awk -F= '{print $2}')
      if [ -n "$PKGLIST" ]; then
        PKGLIST=${PKGLIST//,/ }
      else
        if [ "$PRJNAME" == "lisa" ]; then
          cp ../../clodoo/clodoo/odoorc ./
          cp ../../z0lib/z0lib/z0librc ./
        fi
        x="find . -type f"
        for f in $xx "setup.*"; do
          if [ "${f: -1}" == "/" ]; then
            x="$x -not -path '*/$f*'"
          else
            x="$x -not -name '*$f'"
          fi
        done
        eval $x >./tmp.log
        PKGLIST="$(cat ./tmp.log)"
        rm -f ./tmp.log
      fi
      invalid=
      for f in $PKGLIST; do
        if [ -f $f ]; then
          :
          #cp $f $PKGPATH/tmp
        else
          invalid=$f
        fi
      done
      if [ -n "$invalid" ]; then
        echo "File $f not found"
        return 1
      fi
      p="$n-$v.tar.gz"
      if [ -f $p ]; then
        run_traced "rm -f $p"
      fi
      echo "# $p" >$SETUP
      f=
      for i in {2..9}; do
        x=$(echo $PRJPATH | awk -F/ '{print $'$i'}')
        if [ -n "$x" ]; then
          f=$f/$x
          if [ $i -gt 3 ]; then
            echo "mkdir -p $f" >>$SETUP
          fi
        fi
      done
      l=${#PKGPATH}
      f=".${PRJPATH:l}" # subroot
      l=${#f}
      ((l++))
      PASSED=
      x="-cf"
      for f in $PKGLIST; do
        y=$(dirname ./${f:l})
        if [ "$y" != "." ]; then
          y=$(dirname ${f:l})
          if [[ " $PASSED " =~ [[:space:]]$y[[:space:]] ]]; then
            :
          else
            echo "mkdir -p $PRJPATH/$y" >>$SETUP
            PASSED="$PASSED $y"
          fi
          y=$y/
        else
          y=
        fi
        run_traced "tar $x $p $f"
        x=${x/c/r}
        # if [ -f "$f" ]; then rm -f $f; fi
        echo "cp -p $f $PKGPATH/$y" >>$SETUP
      done
      chmod +x $SETUP
      if [ -x $PRJPATH/setup.sh ]; then
        run_traced "cp $PRJPATH/setup.sh $SETUP"
      fi
      run_traced "tar $x $p $SETUP"
      run_traced "rm -f $SETUP"
    fi
  fi
  return $sts
}

do_check() {
  wlog "Outdated function: check"
  return $STS_FAILED
}

do_coverage() {
  wlog "Outdated function: coverage"
  return $STS_FAILED
}

do_commit() {
  echo "Deprecated action!"
  opts=$(inherits_travis_opts "C" "D")
  opt_dry_run=0
  run_traced "$TDIR/dist_pkg $opts $1"
  sts=$?
  return $sts
}

do_diff() {
  wlog "Outdated function: diff"
  return $STS_FAILED
}

do_distribution_pypi() {
  echo "Deprecated action!"
  local sts=$STS_SUCCESS
  diff -q ~/agpl.txt ./LICENSE &>/dev/null || run_traced "cp ~/agpl.txt  ./LICENSE"
  if [ -d docs ]; then
    OPTS=-lmodule
    [ -f README.md.bak ] && run_traced "rm -fR README.md.bak"
    [ -f README.md ] && run_traced "mv README.md README.md.bak"
    run_traced "gen_readme.py -qGzero $OPTS"
    do_docs
  fi
  return $sts
}

do_distribution_odoo() {
  local sts=$STS_SUCCESS
  local currpt=zero
  local ORIG= GIT_ORG=$2 UPSTREAM= OPTS
  local b f f1 f2 tmod x
  local odoo_ver=$(get_ver)
  [ -z "$GIT_ORG" ] && GIT_ORG=zero
  [ ${test_mode:-0} -eq 0 ] && tmod="" || tmod="default"
  if [ -n "$3" ]; then
    local travis_passed=1
    if [ -d $3/tmp ]; then
      ORIG=$3/tmp
    elif [ -d ~/original/$1 ]; then
      ORIG=~/original/$1
    fi
  else
    local travis_passed=0
    set_remote_info "$REPOSNAME" "." "$GIT_ORG"
  fi
  if [ -f .gitrepname ]; then
    currpt=$(grep "^repository" .gitrepname | awk -F= '{print $2}' | tr -d " ")
  fi
  local GITPRJ=$(build_odoo_param RUPSTREAM '.' "$tmod" $GIT_ORG)
  if [ -z "$GITPRJ" ]; then
    local GITPRJ=$(build_odoo_param RORIGIN '.' "$tmod" $GIT_ORG)
  fi
  if [ $travis_passed -eq 0 ]; then
    if [ $opt_orig -gt 0 ]; then
      if [ -z "$GITPRJ" ]; then
        echo "git project not found!"
        sts=$STS_FAILED
      else
        run_traced "git clone $GITPRJ tmp -b $BRANCH --depth 1 --single-branch"
        ORIG=$(readlink -e tmp)
      fi
    else
      if [ -d ~/original ]; then rm -fR -d ~/original; fi
      if [ -n "$GITPRJ" ]; then
        run_traced "git clone $GITPRJ ~/original/$1 -b $BRANCH --depth 1 --single-branch"
        ORIG=$(readlink -e ~/original/$1)
      fi
    fi
  fi
  if [ $travis_passed -eq 0 ]; then
    cvt_gitmodule "$GIT_ORG" "$currpt"
    if [ $sts -eq $STS_SUCCESS ]; then
      f1=oca_dependencies.txt
      if [ -f "$f1" ]; then
        cvt_file $f1 $GIT_ORG "" "$currpt" "$ORIG"
        sts=$?
      fi
    fi
  fi
  local PKGS= FL= PIGN=
  for f in $(find . -type f \( -name __openerp__.py -o -name __manifest__.py -o -name ".travis.yml" -o -name "README*" -a -not -name "*.bak" -a -not -name "*~" -a -not -name "*.z0i" -a -not -name "*.oca" -a -not -name "*.tmp" \)); do
    x=$(readlink -e $f)
    f1=$(dirname $x)
    f2=$(build_odoo_param REPOS $f1)
    b=$(basename $f)
    if [ -f .gitmodules ] && grep -q "submodule[[:space:]].$f2" .gitmodules 2>/dev/null; then
      if [[ ! " $PKGS " =~ [[:space:]]$f2[[:space:]] ]]; then
        [ $opt_verbose -gt 0 ] && echo "Found submodule $f2 ..."
        PKGS="$PKGS $f2"
      fi
    elif [ "$f2" != "OCB" -a -f .gitignore ] && grep -q "^$f2/$" .gitignore 2>/dev/null; then
      if [[ ! " $PIGN " =~ [[:space:]]$f2[[:space:]] ]]; then
        [ $opt_verbose -gt 0 ] && echo "Submodule $f2 ignored ..."
        PIGN="$PIGN $f2"
      fi
    fi
  done
  for f in $PKGS; do
    if [ $sts -ne $STS_SUCCESS ]; then
      break
    fi
    f2=$(basename $f)
    if [ ${test_mode:-0} -eq 0 -a ! -f $f2/LICENSE ]; then
      if [ $odoo_ver -ge 10 -a "$PRJNAME" == "Odoo" ]; then
        diff -q ~/lgpl.txt $f2/LICENSE &>/dev/null || run_traced "cp ~/lgpl.txt  $f2/LICENSE"
      else
        diff -q ~/agpl.txt $f2/LICENSE &>/dev/null || run_traced "cp ~/agpl.txt  $f2/LICENSE"
      fi
    fi
  done
  f2=$(readlink -e .)
  for f in $(find . -type d -name 'egg-info'); do
    d=$(dirname $f)
    run_traced "pushd $d >/dev/null"
    if [[ "$PWD" == "$f2" ]]; then
      OPTS=-lrepository
    else
      OPTS=-lmodule
    fi
    [[ -f README.md ]] && run_traced "rm -fR README.md"
    run_traced "gen_readme.py -qG$GIT_ORG $OPTS"
    if [ $odoo_ver -ge 8 ]; then
      if [ -f __openerp__.py -o -f __manifest__.py ]; then
        [ ! -d ./static ] && mkdir -p ./static
        [ ! -d ./static/description ] && mkdir -p ./static/description
        [ -d ./static/src/img/icon.png -a ! -d ./static/description/icong.png ] && run_traced "mv ./static/src/img/* ./static/description/"
        run_traced "gen_readme.py -qH -G$GIT_ORG $OPTS"
      fi
    else
      if [ -f __openerp__.py ]; then
        [ ! -d ./static ] && mkdir -p ./static
        [ ! -d ./static/src ] && mkdir -p ./static/src
        [ ! -d ./static/src/img ] && mkdir -p ./static/src/img
        [ -d ./static/description/icong.png -a ! -d ./static/src/img/icon.png ] && run_traced "mv ./static/description/* ./static/src/img/"
        run_traced "gen_readme.py -qR -G$GIT_ORG $OPTS"
      fi
    fi
    run_traced "popd >/dev/null"
  done
  if [ $opt_r -gt 0 ]; then
    for f in $PKGS; do
      if [ $sts -ne $STS_SUCCESS ]; then
        break
      fi
      local PKG=$(basename $f)
      cd $f
      pushd $f >/dev/null
      revaluate_travis
      do_distribution $PKG $2 "$CCWD"
      sts=$?
      popd >/dev/null
    done
  fi
  revaluate_travis
  if [ $sts -eq $STS_SUCCESS -a -z "$3" ]; then
    if [ -f .gitignore ]; then
      if ! grep -q "\.gitrepname" .gitignore 2>/dev/null; then
        echo ".gitrepname" >>.gitignore
      fi
    fi
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    if [ -d tmp -a $opt_keep -eq 0 ]; then
      rm -fR tmp
    fi
    if [ -f .gitrepname ]; then
      if [ "$2" != "$currpt" ]; then
        run_traced "sed -i -e 's:^repository *=.*:repository=$2:' .gitrepname"
      fi
    else
      echo "repository=$2" >>.gitrepname
    fi
    restore_owner "$2"
  fi
  return $sts
}

do_distribution() {
  # do_distribution(repos oca|zero parent)
  local sts
  wlog "do_distribution $1 $2 $3"
  if [ "$PRJNAME" == "Odoo" ]; then
    do_distribution_odoo "$1" "$2" "$3"
    sts=$?
  else
    do_distribution_pypi "$1" "$2" "$3"
    sts=$?
  fi
  return $sts
}

do_docs() {
  wlog "do_docs"
  local docs_dir=./docs
  local author version theme SETUP b f l t x
  local opts src_png odoo_fver
  local HOME_DEV
  HOME_DEV=$HOME/venv_tools
  [[ $opt_dbg -ne 0 || $PWD =~ /dev(el)?/pypi/ ]] && opts=-B || opts=
  if [ "$PRJNAME" == "Odoo" ]; then
    [[ -z "$opt_branch" ]] && odoo_fver=$(build_odoo_param FULLVER ".") || odoo_fver=$(build_odoo_param FULLVER "$opt_branch")
    [[ -z "$opt_branch" ]] && orgid=$(build_odoo_param GIT_ORGID ".") || orgid=$(build_odoo_param GIT_ORGID "$opt_branch")
    # TODO: GIT_ORGid of build_odoo_param does not work
    PARENTDIR=$(build_odoo_param PARENTDIR ".")
    if [[ -z "$opt_branch" && -d ./.git && $(git status -s &>/dev/null) ]]; then
      GIT_URL=$(git remote get-url --push origin 2>/dev/null)
      [[ -n "$GIT_URL" ]] && GIT_ORGNM=$(basename $(dirname $(git remote -v | echo $GIT_URL | awk -F: '{print $2}')))
      [[ $GIT_ORGNM == "OCA" ]] && orgid="oca"
      [[ $GIT_ORGNM == "zeroincombenze" ]] && orgid="zero"
      [[ $GIT_ORGNM =~ (PowERP-cloud|powerp1) ]] && orgid="powerp"
    elif [[ -z "$opt_branch" && -d $PARENTDIR/.git ]]; then
      pushd $PARENTDIR >/dev/null
      GIT_URL=$(git remote get-url --push origin 2>/dev/null)
      [[ -n "$GIT_URL" ]] && GIT_ORGNM=$(basename $(dirname $(git remote -v | echo $GIT_URL | awk -F: '{print $2}')))
      [[ $GIT_ORGNM == "OCA" ]] && orgid="oca"
      [[ $GIT_ORGNM == "zeroincombenze" ]] && orgid="zero"
      [[ $GIT_ORGNM =~ (PowERP-cloud|powerp1) ]] && orgid="powerp"
      popd >/dev/null
    fi
    if [[ -f ./__manifest__,py || -f ./__openerp__.py ]]; then
      l=$(build_odoo_param LICENSE "." "" "" "search")
      [[ $licence == "AGPL" && -f $HOME_DEV/license_text/agpl-3.0.txt ]] && run_traced "cp -p $HOME_DEV/license_text/agpl-3.0.txt ./LICENSE"
      [[ $licence == "LGPL" && -f $HOME_DEV/license_text/lgpl-3.0.txt ]] && run_traced "cp -p $HOME_DEV/license_text/lgpl-3.0.txt ./LICENSE"
      [[ $licence == "OPL" && -f $HOME_DEV/license_text/opl-1.0.txt ]] && run_traced "cp -p $HOME_DEV/license_text/opl-1.0.txt ./LICENSE"
    fi
    run_traced "gen_readme.py -b$odoo_fver $opts -G$orgid"
    version=$(build_odoo_param MAJVER $odoo_fver)
    if [[ ! -d ./static ]]; then
      run_traced "mkdir ./static"
      [[ $version -le 7 ]] && run_traced "mkdir ./static/src" && run_traced "mkdir ./static/src/img"
      [[ $version -gt 7 ]] && run_traced "mkdir ./static/description"
    fi
    if [[ ! -d ./egg-info && ! -d ./readme ]]; then
      mkdir ./egg-info
      opt_force=0
      run_traced "gen_readme.py -b$odoo_fver $opts -RW -G$orgid"
    fi
    [[ $version -gt 7 ]] && run_traced "gen_readme.py -b$odoo_fver $opts -H -G$orgid"
    [[ $version -le 7 && $opt_force -eq 0 ]] && run_traced "gen_readme.py -b$odoo_fver $opts -R -G$orgid"
    [[ $opt_force -ne 0 ]] && run_traced "gen_readme.py -b$odoo_fver $opts -RW -G$orgid"
    return 0
  fi
  if [[ ! -d $docs_dir ]]; then
    if [[ $opt_force -eq 0 ]]; then
      echo "Missing docs directory!"
      return 1
    fi
    run_traced "mkdir $docs_dir"
  fi
  if [[ ! -f $docs_dir/logozero_180x46.png ]]; then
    src_png=
    [[ -z "$src_png" && -f ../tools/docs/logozero_180x46.png ]] && src_png=$(readlink -e ../tools/docs/logozero_180x46.png)
    [[ -z "$src_png" && -f ../../tools/docs/logozero_180x46.png ]] && src_png=$(readlink -e ../../tools/docs/logozero_180x46.png)
    [[ -n "$src_png" ]] && run_traced "cp $src_png $docs_dir/logozero_180x46.png"
  fi
  for f in $(grep -E "^ *(rtd_|pypi_)" docs/index.rst | tr "\n" " "); do
    echo ".. toctree::" >./rtd_template.rst
    echo "   :maxdepth: 2" >>./rtd_template.rst
    echo "" >>./rtd_template.rst
    if [[ "$f" == "rtd_automodule" ]]; then
      echo "Code documentation" >>./rtd_template.rst
      echo "------------------" >>./rtd_template.rst
      echo "" >>./rtd_template.rst
      for b in $(cat __init__.py | grep "^from . import" | awk '{print $4}' | tr "\n" " "); do
        echo -e ".. automodule:: $PKGNAME.$b\n" >>./rtd_template.rst
      done
      run_traced "mv ./rtd_template.rst $docs_dir/rtd_automodule.rst"
    elif [[ $f =~ ^rtd_ ]]; then
      t=${f:4}
      [[ $t == "features" ]] && echo -e "Features\n--------" >>./rtd_template.rst
      [[ $t == "usage" ]] && echo -e "Usage\n-----" >>./rtd_template.rst
      echo "{{$t}}" >>./rtd_template.rst
      echo ".. \$include readme_footer.rst" >>./rtd_template.rst
      run_traced "gen_readme.py $opts -t ./rtd_template.rst -o $docs_dir/$f.rst"
      run_traced "rm ./rtd_template.rst"
    elif [[ $f =~ ^pypi_ ]]; then
      x=$(echo $f | grep -Eo "^pypi.*/index")
      b=${x:0:-6}
      x=${x:5:-6}
      [[ -d $docs_dir/$b ]] || run_traced "mkdir -p $docs_dir/$b"
      run_traced "rsync -avz --delete $HOME_DEV/pypi/$x/$x/docs/ $docs_dir/$b/"
    fi
  done
  # [[ $(basename $PWD) == "tools" && -f egg-info/history.rst ]] && run_traced "rm -f egg-info/history.rst"
  [[ $(basename $PWD) == "tools" ]] && run_traced "gen_readme.py $opts -W" || run_traced "gen_readme.py $opts"
  [[ $(grep "\.\. include:: MAINPAGE.rst" docs/index.rst) ]] && run_traced "gen_readme.py $opts -t mainpage -o $docs_dir/MAINPAGE.rst"
  run_traced "pushd $docs_dir >/dev/null"
  if [[ ! -f index.rst || ! -f conf.py ]]; then
    SETUP=$(build_pypi_param SETUP)
    version=$(get_value_from_file "$SETUP" "version")
    author=$(get_value_from_file "$SETUP" "author")
    run_traced "sphinx-quickstart -p '$PRJNAME' -a '$author' -v '$version' -r '$version' -l en --no-batchfile --makefile --master index --suffix .rst ./"
    cat <<EOF >conf.py
# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation on $(date "+%Y-%m-%d %H:%M:%S")
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

project = '$PRJNAME'
copyright = '2021, $author'
author = '$author'

# The short X.Y version
version = '$version'
# The full version, including alpha/beta/rc tags
release = '$version'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store',
                    'description*', 'descrizione*', 'features*',
                    'oca_diff*', 'certifications*', 'prerequisites*',
                    'installation*', 'configuration*', 'upgrade*',
                    'support*', 'usage*', 'maintenance*',
                    'troubleshooting*', 'known_issues*',
                    'proposals_for_enhancement*', 'history*', 'faq*',
                    'sponsor*', 'copyright_notes*', 'available_addons*',
                    'contact_us*',
                    '__init__*', 'name*', 'summary*', 'sommario*',
                    'maturity*', 'module_name*', 'repos_name*',
                    'today*',
                    'authors*', 'contributors*', 'translators*',
                    'acknowledges*']

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = None
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# on_rtd is whether we are on readthedocs.org,
# this line of code grabbed from docs.readthedocs.org
#     html_theme = 'master'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    # 'canonical_url': '',
    # 'analytics_id': 'UA-XXXXXXX-1',
    # 'logo_only': False,
    # 'display_version': True,
    # 'prev_next_buttons_location': 'bottom',
    # 'style_external_links': False,
    # 'vcs_pageview_mode': '',
    # 'style_nav_header_background': 'white',
    # Toc options
    # 'collapse_navigation': True,
    # 'sticky_navigation': True,
    # 'navigation_depth': 4,
    # 'includehidden': True,
    # 'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}
html_logo = 'logozero_180x46.png'
EOF
    cat <<EOF >index.rst
.. $PRJNAME documentation master file, created by
   sphinx-quickstart on $(date "+%Y-%m-%d %H:%M:%S")
   You can adapt this file completely to your liking, but it should at least
   contain the root \`toctree\` directive.

===========================================
Welcome to $PRJNAME $version documentation!
===========================================

|Maturity| |Build Status| |Coverage Status| |license gpl|

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. include:: MAINPAGE.rst


Indices and tables
==================

* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`
EOF
  fi
  if [ ! -f requirements.txt ]; then
    cat <<EOF >requirements.txt
sphinx_rtd_theme
EOF
  fi
  if [ ! -f readthedocs.yml ]; then
    cat <<EOF >readthedocs.yml
# readthedocs.yml
# Read the Docs configuration file
# See https://docs.readthedocs.io/en/stable/config-file/v2.html for details

# Required
version: 2

# Build documentation in the docs/ directory with Sphinx
sphinx:
  configuration: docs/conf.py

# Build documentation with MkDocs
#mkdocs:
#  configuration: mkdocs.yml

# Optionally build your docs in additional formats such as PDF and ePub
formats: all

# Optionally set the version of Python and requirements required to build your docs
python:
  version: 3.7
  install:
    - requirements: docs/requirements.txt

sphinx:
  builder: html
  configuration: conf.py
  fail_on_warning: true
EOF
  fi
  run_traced "make html"
  sts=$?
  run_traced "popd >/dev/null"
  return $sts
}

do_download_rep() {
  #do_download_rep(pkg [URL])
  echo "Deprecated action!"
  wlog "do_download_rep $1 $2"
  local dom full_rep local_rep
  local ORIG="~/original"
  if [ -z "$opt_branch" ]; then
    echo "Missed Odoo Version"
    exit 1
  fi
  if [[ -n "$2" ]]; then
    full_rep=$(parse_URI "$2" "https://github.com/zeroincombenze/.git" "+ALL+LOCAL")
  else
    full_rep=$(parse_URI "$1" "https://github.com/zeroincombenze/.git" "+ALL+LOCAL")
  fi
  local_rep=$(parse_URI "$full_rep" "" "+NAMEID+LOCAL")
  [ -d $ORIG ] || mkdir -p $ORIG
  pushd $ORIG >/dev/null
  [ -d "$local_rep" ] && rm -fR $local_rep/
  run_traced "git clone $full_rep $local_rep/ -b $opt_branch --single-branch"
  popd >/dev/null
}

do_duplicate() {
  set_executable
  if [ "$PRJNAME" == "Odoo" ]; then
    if [[ ! $LGITPATH =~ (14\.0|13\.0|12\.0|11\.0|10\.0|9\.0|8\.0|7\.0|6\.1) ]]; then
      echo "Missing or invalid target Odoo version"
      exit 1
    fi
    cur_ver=""
    for ver in 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1; do
      if [[ $PWD =~ $HOME/$ver ]]; then
        cur_ver="$ver"
        break
      fi
    done
    if [ -z "$cur_ver" ]; then
      echo "Unrecognized Odoo version"
      exit 1
    fi
    LGITPATH="${PWD/$cur_ver/$LGITPATH}"
    opts=$(inherits_travis_opts "D" "D")
    opt_dry_run=0
    run_traced "$TDIR/dist_pkg $opts $1 -p$LGITPATH"
    sts=$?
  fi
  return $sts
}

do_export() {
  wlog "do_export '$1' '$2' '$3'"
  local db module odoo_fver sts=$STS_FAILED
  if [[ "$PRJNAME" == "Odoo" ]]; then
    module=$2
    db=$3
  else
    module=$1
    db=$2
  fi
  if [[ -z "$module" || "$module" == '.' ]]; then
    odoo_fver=$(build_odoo_param FULLVER '.')
    pofile="$(build_odoo_param PKGPATH '.')/i18n/it.po"
    module=$(build_odoo_param PKGNAME '.')
  else
    [[ -n "$opt_branch" ]] && odoo_fver=$opt_branch
    pofile="$(find $HOME/$opt_branch -type d -name $module)/i18n/it.po"
  fi
  if [[ -z "$odoo_fver" ]]; then
    echo "Missing Odoo branch! use:"
    echo "$0 export -bBRANCH 'MODULE' 'DB'"
    return $STS_FAILED
  fi
  odoo_ver=$(echo $odoo_fver | grep -Eo [0-9]+ | head -n1)
  if [[ ! -f "$pofile" ]]; then
    echo "File $pofile not found!"
    return $STS_FAILED
  fi
  if [[ -z "$db" ]]; then
    DBs=$(psql -Atl | awk -F'|' '{print $1}' | tr \"\\n\" '|')
    DBs="^(${DBs:0: -1})\$"
    for x in tnl test demo; do
      [[ $x$odoo_ver =~ $DBs ]] && db="$x$odoo_ver" && break
    done
  fi
  if [[ -z "$module" || -z "$db" ]]; then
    echo "Parameters mismatch! use:"
    echo "$0 export -bBRANCH 'MODULE' 'DB'"
    return $STS_FAILED
  fi
  opt_user=$(get_dbuser $odoo_ver)
  stat=$(psql -U$opt_user -Atc "select state from ir_module_module where name = '$module'" $db)
  [[ -z "$stat" || $stat == "uninstalled" ]] && run_traced "run_odoo_debug -b$odoo_fver -Ism $module -d $db"
  dbdt=$(psql -U$opt_user -Atc "select write_date from ir_module_module where name='$module' and state='installed'" $db)
  [[ -n "$dbdt" ]] && dbdt=$(date -d "$dbdt" +"%s") || dbdt="999999999999999999"
  podt=$(stat -c "%Y" $pofile)
  ((dbdt < podt)) && run_traced "run_odoo_debug -b$odoo_fver -usm $module -d $db"
  run_traced "run_odoo_debug -b$odoo_fver -em $module -d $db"
  sts=$?
  return $sts
}

do_import() {
  wlog "do_import '$1' '$2' '$3'"
  local db module odoo_fver sts=$STS_FAILED
  if [ "$PRJNAME" == "Odoo" ]; then
    module=$2
    db=$3
  else
    module=$1
    db=$2
  fi
  [[ "$module" == '.' ]] && module=$PKGNAME
  [ -n "$opt_branch" ] && odoo_fver=$opt_branch || odoo_fver=10.0
  if [ -z "$module" -o -z "$db" ]; then
    echo "Missing parameters! use:"
    echo "> do_import -bBRANCH 'MODULE' 'DB'"
    return $STS_FAILED
  fi
  [ $? -eq 0 ] && run_traced "run_odoo_debug -Wb$odoo_fver -im $module -d $db"
  sts=$?
  return $sts
}

do_list() {
  local ii x y tgtpath tgtparm
  for ii in {1..9}; do
    x=tgt${ii}path
    y=tgt${ii}params
    tgtpath="$(get_cfg_value 0 $x)"
    if [ -n "$tgtpath" ]; then
      printf "%2d %s\n" $ii "$tgtpath"
    fi
  done
}

do_translate() {
  wlog "do_translate '$1' '$2' '$3'"
  local confn db module odoo_fver sts=$STS_FAILED opts pyv pofile
  if [[ "$PRJNAME" == "Odoo" ]]; then
    module=$2
    db=$3
  else
    module=$1
    db=$2
  fi
  if [[ -z "$module" || "$module" == '.' ]]; then
    odoo_fver=$(build_odoo_param FULLVER '.')
    pofile="$(build_odoo_param PKGPATH '.')/i18n/it.po"
    module=$(build_odoo_param PKGNAME '.')
  else
    [[ -n "$opt_branch" ]] && odoo_fver=$opt_branch
    pofile="$(find $HOME/$opt_branch -type d -name $module)/i18n/it.po"
  fi
  if [[ -z "$odoo_fver" ]]; then
    echo "Missing Odoo branch! use:"
    echo "$0 export -bBRANCH 'MODULE' 'DB'"
    return $STS_FAILED
  fi
  odoo_ver=$(echo $odoo_fver | grep -Eo [0-9]+ | head -n1)
  if [[ ! -f "$pofile" ]]; then
    echo "File $pofile not found!"
    return $STS_FAILED
  fi
  [[ -n "$opt_conf" ]] && conf=$opt_conf
  [[ -z "$opt_conf" ]] && confn=$HOME/clodoo/confs/${odoo_fver/./-}.conf
  if [[ ! -f $confn ]]; then
    echo "Configuration file $confn not founcd!"
    return $STS_FAILED
  fi
  if [[ -z "$db" ]]; then
    DBs=$(psql -Atl | awk -F'|' '{print $1}' | tr \"\\n\" '|')
    DBs="^(${DBs:0: -1})\$"
    for x in tnl test demo; do
      [[ $x$odoo_ver =~ $DBs ]] && db="$x$odoo_ver" && break
    done
  fi
  if [[ -z "$module" || -z "$db" ]]; then
    echo "Parameters mismatch! use:"
    echo "$0 export -bBRANCH 'MODULE' 'DB'"
    return $STS_FAILED
  fi
  if [[ ! -d $HOME/clodoo ]]; then
    echo "Missed environment!"
    echo "Directory clodoo not found!"
    return $STS_FAILED
  fi
  pyv=$(python3 --version 2>&1 | grep -Eo "[0-9]+\.[0-9]+")
  [[ -n "$pyv" ]] && pyver="-p $pyv"
  pyver="-p 2.7" #debug
  [[ ! -d $HOME/clodoo/venv ]] && \
    run_traced "vem $pyver create $HOME/clodoo/venv" && \
    run_traced "vem $HOME/clodoo/venv install openpyxl" && \
    run_traced "vem $HOME/clodoo/venv install Babel" && \
    run_traced "vem $HOME/clodoo/venv install clodoo"
  # run_traced "pushd $HOME/clodoo >/dev/null"
  [ $opt_verbose -ne 0 ] && opts="-v" || opts="-q"
  [ $opt_dbg -ne 0 ] && opts="${opts}B"
  run_traced "odoo_translation.py $opts -b$odoo_fver -m $module -d $db -c $confn -p $pofile"
  sts=$?
  # run_traced "popd >/dev/null"
  return $sts
}

do_test() {
  wlog "do_test '$1' '$2' '$3'"
  local db module odoo_fver sts=$STS_FAILED
  if [ "$PRJNAME" == "Odoo" ]; then
    module=$1
    db=$2
  else
    module=$1
    db=$2
    [ -n "$opt_branch" ] && odoo_fver=$opt_branch || odoo_fver=10.0
  fi
  if [ -z "$module" ]; then
    echo "Missing parameters! use:"
    if [ "$PRJNAME" == "Odoo" ]; then
      echo "> do_test ['DB']"
    else
      echo "> do_text -bBRANCH 'MODULE' ['DB']"
    fi
    return $STS_FAILED
  fi
  # [ -n "$db" ] && db="-d $db"
  [ $? -eq 0 ] && run_traced "run_odoo_debug -Wb$odoo_fver -Tm $module"
  sts=$?
  return $sts
}

do_fetch() {
  wlog "Outdated function: fetch"
  return $STS_FAILED
}

do_lsearch() {
  # search n log ([date] db token)
  wlog "do_lsearch '$1' '$2' '$3'"
  local CM cmd db f LOGDIRS odoo_fver odoo_ver PM sts=$STS_FAILED tok_dt token
  [ -n "$opt_branch" ] && odoo_fver=$opt_branch || odoo_fver=10.0
  odoo_ver=$(echo $odoo_fver | grep -Eo [0-9]+ | head -n1)
  tok_dt=$opt_date
  CM=$(date +%Y-%m)
  PM=$(date -d "1 month ago" +%Y-%m)
  db=$1
  token=$2
  if [ "$CM" == "$PM" ]; then
    LOGDIRS="/var/log/odoo/odoo$odoo_ver.log.$CM-* /var/log/odoo/odoo$odoo_ver.log"
  else
    LOGDIRS="/var/log/odoo/odoo$odoo_ver.log.$PM-* /var/log/odoo/odoo$odoo_ver.log.$CM-* /var/log/odoo/odoo$odoo_ver.log"
  fi
  for f in $LOGDIRS; do
    if [ -n "$tok_dt" ]; then
      if [ -n "$token" ]; then
        cmd="grep -a -A 10 --color=never \"^$tok_dt.* $db .*$token\" $f|grep -av --color=never \"/longpolling/poll HTTP/1.1\"|grep -av --color=never \"POST /jsonrpc HTTP/1.1. 200\"|grep -a --color \"$token\""
      else
        cmd="grep -av --color=never \"/longpolling/poll HTTP/1.1\" $f|grep -av --color=never \"POST /jsonrpc HTTP/1.1. 200\"|grep -a \"^$tok_dt.* $db .*\""
      fi
    else
      if [ -n "$token" ]; then
        cmd="grep -a -A 10 --color=never \" $db .*$token\" $f|grep -av --color=never \"/longpolling/poll HTTP/1.1\"|grep -av --color=never \"POST /jsonrpc HTTP/1.1. 200\"|grep -a --color \"$token\""
      else
        cmd="grep -av --color=never \"/longpolling/poll HTTP/1.1\" $f|grep -av --color=never \"POST /jsonrpc HTTP/1.1. 200\"|grep -a \" $db .*\""
      fi
    fi
    if [ $opt_dry_run -eq 0 ]; then
      eval $cmd
    else
      echo $cmd
    fi
  done
}
do_push() {
  opts=$(inherits_travis_opts "oP" "D")
  opt_dry_run=0
  run_traced "$TDIR/dist_pkg $opts $1"
  sts=$?
  return $sts
}

do_pythonhosted() {
  wlog "do_pythonhosted $1 $2 $3"
  sts=$STS_SUCCESS
  if [ -z "$2" ]; then
    echo "Missing URL! use:"
    echo "> please pythonhosted URL"
    return $STS_FAILED
  fi
  local URL=$2
  if [ "${URL: -1}" != "/" ]; then
    local URL=$URL/
  fi
  local TITLE="$3"
  local CWD=$PWD
  run_traced "cd $PKGPATH"
  cat <<EOF >index.html
<!DOCTYPE HTML>
   <head>
       <meta http-equiv="refresh" content="0; $URL">
       <script type="text/javascript">
           top.location.href = "$URL"
       </script>
       <title>Redirect</title>
   </head>
   <body>
       Please wait for a moment .. <a href='$URL' $2</a>
   </body>
</html>
EOF
  run_traced "zip -j pythonhosted-$PKGNAME.zip index.html"
  if [ -f index.html ]; then
    rm -f index.html
  fi
  cd $CWD
  if [ -f $PKGPATH/pythonhosted-$PKGNAME.zip ]; then
    echo "Now you can download $PKGPATH/pythonhosted-$PKGNAME.zip in pypi webpage of project"
  fi
  return $sts
}

do_register() {
  #do_register PKGNAME (pypi|testpypi)
  wlog "do_register $1 $2"
  local cmd="do_register_$1"
  sts=$STS_SUCCESS
  if [ "$(type -t $cmd)" == "function" ]; then
    eval $cmd "$@"
  else
    echo "Missing object! Use:"
    echo "> please register (pypi|testpypi)"
    sts=$STS_FAILED
  fi
  return $sts
}

do_replace() {
  if [[ "$PRJNAME" == "Odoo" ]]; then
    clean_dirs "$1"
    [[ $opt_force -ne 0 ]] && set_executable
    if [[ $LGITPATH =~ (oca|zero) ]]; then
      local odoo_fver=$(build_odoo_param FULLVER ".")
      local p=$(build_odoo_param HOME "." "$PKGNAME" "$LGITPATH")
      LGITPATH=$p
    fi
    if [[ ! -d "$LGITPATH" && $opt_force -ne 0 ]]; then
      [[ $opt_verbose -gt 0 ]] && echo "Creating destination directory ..."
      run_traced "mkdir -p $LGITPATH"
    fi
    if [[ ! -d "$LGITPATH" ]]; then
      echo "Destination directory $LGITPATH not found!"
      sts=$STS_FAILED
    else
      opts=$(inherits_travis_opts "O" "D")
      opt_dry_run=0
      run_traced "$TDIR/dist_pkg $opts $1 -p$LGITPATH"
      sts=$?
    fi
  else
    # do_distribution_pypi "$@"
    for f in ./*; do
      t=$(file -b --mime-type $f)
      [[ $t != "application/x-sharedlib" && ( -x $f || $f =~ .py$ ) && ! -d $f ]] && grep -q "^#\!.*/venv/bin/python3$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/venv/bin/python3$|^#\!/usr/bin/env python3|\" $f"
      [[ $t != "application/x-sharedlib" && ( -x $f || $f =~ .py$ ) && ! -d $f ]] && grep -q "^#\!.*/venv/bin/python3$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/venv/bin/python2$|^#\!/usr/bin/env python2|\" $f"
      [[ $t != "application/x-sharedlib" && ( -x $f || $f =~ .py$ ) && ! -d $f ]] && grep -q "^#\!.*/venv/bin/python$" $f &>/dev/null && run_traced "sed -i -e \"s|^#\!.*/venv/bin/python2$|^#\!/usr/bin/env python|\" $f"
    done
    do_docs
    [[ $(basename $PWD) == "tools" ]] && clean_dirs "./" || clean_dirs "../"
<<<<<<< HEAD:wok_code/please.sh
    opts=$(inherits_travis_opts "R" "D")
    [[ -x $PRJPATH/replace.sh ]] && run_traced "$PRJPATH/replace.sh" || run_traced "$TDIR/dist_pkg $opts $1"
    sts=$?
=======
    # [[ -f $PKGPATH/setup.py && -d $PRJPATH/scripts ]] && run_traced "cp $PKGPATH/setup.py $PRJPATH/scripts/setup.info"
    # [[ -f $PRJPATH/setup.py ]] && run_traced "rm -f $PRJPATH/setup.py"
    opts=$(inherits_travis_opts "R" "D")
    [[ -x $PRJPATH/replace.sh ]] && run_traced "$PRJPATH/replace.sh" || run_traced "$TDIR/dist_pkg $opts $1"
    sts=$?
    # [[ $(basename $PWD) != "tools" ]] && run_traced "cp $PKGPATH/setup.py $HOME/tools/$PKGNAME/"
>>>>>>> stash:wok_code/please
    [[ $(basename $PWD) != "tools" ]] && clean_dirs "$HOME/tools"
    [[ $opt_force -ne 0 ]] && set_executable
  fi
  return $sts
}

do_replica() {
  # do_replica(pkgname file)
  local cur_ver fn srcfn tp ver
  if [[ $PRJNAME == "Odoo" ]]; then
    cur_ver=""
    for ver in 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1; do
      if [[ $PWD =~ $HOME/$ver ]]; then
        cur_ver="$ver"
        break
      fi
    done
    if [[ -z "$cur_ver" ]]; then
      echo "Unrecognized Odoo version"
      exit 1
    fi
    tp="f"
    fn="$2"
    if [[ -d "$fn" ]]; then
      tp="d"
    elif [[ ! -f "$fn" ]]; then
      echo "File $fn not found"
      exit 1
    fi
    srcfn=$(readlink -f $fn)
    for ver in 14.0 13.0 12.0 11.0 10.0 9.0 8.0 7.0 6.1; do
      if [ "$ver" != "$cur_ver" ]; then
        tgtfn="${srcfn/$cur_ver/$ver}"
        if [ "$tp" == "f" ]; then
          tgtdir=$(dirname "$tgtfn")
          if [[ -d "$tgtdir" ]]; then
            echo "cp $srcfn $tgtfn"
            cp $srcfn $tgtfn
            if [ "${tgtfn: -4}" == ".xml" ]; then
              run_traced "$TDIR/topep8 -b$ver $tgtfn"
            fi
          else
            echo "Directory $tgtdir not found"
          fi
        else
          tgtdir=$(dirname "$tgtfn")
          if [[ ! -d "$tgtdir" ]]; then
            if [[ ! -d "$tgtdir/.." ]]; then
              echo "Directory $tgtdir not found!"
            else
              echo "Warning: directory $tgtdir not found!"
              run_traced "cp -R $srcfn $tgtdir/"
            fi
          else
            run_traced "rsync -avzb $srcfn/ $tgtfn/"
          fi
        fi
      fi
    done
    sts=0
  fi
  return $sts
}

do_show() {
  #do_show (docs|license|status)
  wlog "do_show $1"
  local cmd="do_show_$1"
  sts=$STS_SUCCESS
  if [ "$(type -t $cmd)" == "function" ]; then
    eval $cmd "$@"
  else
    echo "Missing object! Use:"
    echo "> please show (docs|licence)"
    echo "show docs        -> show docs using local firefox"
    echo "show license     -> show licenses of modules of current Odoo repository"
    echo "show status      -> show component status"
    sts=$STS_FAILED
  fi
  return $sts
}

do_showdoc() {
  echo "Deprecated action! Use please show docs"
  read -p "Press RET to continue ..."
  do_show_docs "$@"
  return 0
}

do_status() {
  echo "Deprecated action! Use please show status"
  read -p "Press RET to continue ..."
  do_show_status "$@"
  return 0
}

do_show_docs() {
  if [[ ! "$PRJNAME" == "Odoo" ]]; then
    if [[ -f ./docs/_build/html/index.html ]]; then
      firefox $(readlink -e ./docs/_build/html/index.html) &
    else
      echo "No documentation found in ./docs!"
    fi
  fi
  return 0
}

do_show_license() {
  if [[ "$PRJNAME" == "Odoo" ]]; then
    local module license FILES
    FILES=$(find ./ -maxdepth 2 -type f -not -path "*/.git/*" -not -path "*/docs/*" -not -path "*/__build*" -not -path "*/__pycache__*" -not -path "*/.idea*" -not -path "*/i18n/*" -not -path "*/static/*" \( -name "__manifest__.py" -o -name "__openerp__.py" \)|sort)
    for fn in $FILES; do
      path=$(readlink -f $(dirname $fn))
      module=$(basename $path)
      licence=$(grep "[\"']license[\"'] *:" $fn|grep -Eo "(.GPL-3|OPL-1)")
      printf "Module %-60.60s: $licence\n" $module
    done
  fi
  return 0
}

do_show_status() {
  local HOME_DEV s v1 v2 v x y
  local PKGS_LIST=$(get_cfg_value 0 "PKGS_LIST")
  HOME_DEV=$HOME/venv_tools
  pushd $HOME/tools >/dev/null
  local PKGS=$(git status -s | grep -E "^ M" | awk '{print $2}' | awk -F/ '{print $1}' | grep -v "^[0-9]" | sort -u | tr "\n" "|")
  local PKGS_V=$(git diff -G__version__ --compact-summary | awk '{print $1}' | awk -F/ '{print $1}' | grep -v "^[0-9]" | sort -u | tr "\n" "|")
  [[ -n "$PKGS" ]] && PKGS="(${PKGS:0:-1})" || PKGS="()"
  [[ -n "$PKGS_V" ]] && PKGS_V="(${PKGS_V:0:-1})" || PKGS_V="()"
  popd >/dev/null
  for pkg in $PKGS_LIST tools; do
    x=""
    [[ $opt_force -ne 0 ]] && echo -e "\e[1m[ $pkg ]\e[0m"
    [[ $opt_force -eq 0 ]] && echo -e "[ $pkg ]"
    [[ $pkg =~ (python-plus|z0bug-odoo) ]] && pkg="${pkg//-/_}"
    if [[ $pkg == "tools" ]]; then
      for fn in egg-info licence_text templates .travis.yml install_tools.sh odoo_default_tnl.xlsx setup.py; do
        vfdiff -X diff $HOME/$pkg/$fn $HOME_DEV/pypi/$pkg/$fn -q >/dev/null
        if [[ $? -ne 0 ]]; then
          x="R"
          [[ $opt_force -ne 0 ]] && vfdiff -X diff $HOME/$pkg/$fn $HOME_DEV/pypi/$pkg/$fn
          break
        fi
      done
    else
      vfdiff -m -X diff $HOME/tools/$pkg $HOME_DEV/pypi/$pkg/$pkg -q >/dev/null
      if [[ $? -ne 0 ]]; then
        x="R"
        [[ $opt_force -ne 0 ]] && vfdiff -m -X diff $HOME/tools/$pkg $HOME_DEV/pypi/$pkg/$pkg
      fi
    fi
    [[ $PKGS != "()" && $pkg =~ $PKGS ]] && x="$x G"
    [[ $PKGS_V != "()" && $pkg =~ $PKGS_V ]] && x="$x V"
    if [[ $pkg == "tools" ]]; then
      v1=$(grep -E "version" $HOME/tools/setup.py|head -n1|awk -F= '{print $2}'|grep -Eo "[0-9.]+")
      v2=$(grep -E "version" $HOME_DEV/pypi/$pkg/setup.py|head -n1|awk -F= '{print $2}'|grep -Eo "[0-9.]+")
    else
      v1=$(grep -E "version" $HOME/tools/$pkg/setup.py|head -n1|awk -F= '{print $2}'|grep -Eo "[0-9.]+")
      v2=$(grep -E "version" $HOME_DEV/pypi/$pkg/setup.py|head -n1|awk -F= '{print $2}'|grep -Eo "[0-9.]+")
    fi
    if [[ $x =~ "R" ]]; then
      [[ $pkg == "tools" ]] && s="$HOME_DEV/pypi/$pkg" || s="$HOME_DEV/pypi/$pkg/$pkg"
      if [[ $v1 == $v2 && ! $x =~ "V" ]]; then
        v=$(echo $v2 | awk -F. '{if ($NF == 3) {OFS="."; print $1,$2,int($3)+1} else {OFS="."; print $1,$2,$3,int($4)+1}}')
        echo -e "\e[1m    Execute: cd $s; please version $v2 $v; travis && please replace\e[0m"
      else
        echo -e "\e[1m    Execute: cd $s; travis && please replace\e[0m"
      fi
    fi
    [[ $x =~ "G" && $x =~ "V" ]] && echo -e "\e[1m    Package $pkg (new version $v1) have to be pushed on github.com\e[0m"
    [[ $x =~ "G" && ! $x =~ "V" ]] && echo -e "\e[1m    Package $pkg differs from github.com but it has the same version $v1!!\e[0m"
  done
  [[ -f $HOME/tools/egg-info/history.rst ]] && head $HOME/tools/egg-info/history.rst
}

do_synchro() {
  wlog "do_synchro $1 $2 \"$3\""
  local f opts
  if [ -z "$3" ]; then
    echo "Missed parameter! use:"
    echo "\$ please synchro oca|zeroincombenze|zero|zero-merged TEXT"
    return $STS_FAILED
  fi
  set_executable
  if [ "$2" == "oca" -o "$2" == "zero-merged" ]; then
    if [ "$PRJNAME" == "Odoo" ]; then
      clean_dirs "$PKGPATH"
      run_traced "git checkout $BRANCH"
      do_distribution "$PKGNAME" "oca"
      git status
      git remote -v
      run_traced "git pull --no-edit upstream $BRANCH"
      if [ "$2" == "zero-merged" ]; then
        do_distribution "$PKGNAME" "zero"
      fi
      for f in $(find $PKGPATH -type f -not -name "*.png" -exec grep -l ">>>>" '{}' \;); do
        echo "Warning: see file $f"
      done
    fi
  elif [ "$2" == "zeroincombenze" -o "$2" == "zero" ]; then
    if [ "$PRJNAME" == "Odoo" ]; then
      run_traced "git checkout $BRANCH"
      # [ "$PKGNAME" == "OCB" ] && run_traced "git submodule foreach 'git checkout $BRANCH'"
      do_distribution "$PKGNAME" "$2"
      clean_dirs "$PKGPATH"
      local x=($git status -s)
      if [ -n "$x" ]; then
        if [ -n "$3" ]; then
          run_traced "git commit -am \"$3\""
          # [ "$PKGNAME" == "OCB" ] && run_traced "git submodule foreach 'git commit -am \"$3\"'"
        # elif [ $opt_diff -ne 0 ]; then
        else
          run_traced "git commit -am \"[SYNCHRO] Update documentation\""
          # [ "$PKGNAME" == "OCB" ] && run_traced "git submodule foreach 'git commit -am \"[SYNCHRO] Update documentation\"'"
        # else
        #   run_traced "git commit -am \"[SYNCHRO] Synchronizing against OCA repository\""
        #   # [ "$PKGNAME" == "OCB" ] && run_traced "git submodule foreach 'git commit -am \"[SYNCHRO] Synchronizing against OCA repository\"'"
        fi
      fi
      opts=
      [ $opt_force -ne 0 ] && opts=-f
      # local ro=$(build_pkgurl $1 $2 RORIGIN)
      # local ro=$(build_odoo_param RORIGIN '' $1 $2)
      # run_traced "git push $opts $ro"
      run_traced "git push $opts"
      # restore_owner
      git remote -v
      git status
    fi
  else
    echo "Missed parameter! use:"
    echo "\$ please synchro oca|zeroincombenze|zero|oia|zero-merged"
    sts=$STS_FAILED
  fi
  return $sts
}

do_travis() {
  wlog "Outdated function: travis"
  return $STS_FAILED
}

do_version() {
  # do_version(pkg [cur_ver [new_ver]])
<<<<<<< HEAD:wok_code/please.sh
  if [[ "$PRJNAME" != "Odoo" ]]; then
    if [[ -z "$2" ]]; then
      find . -type f -not -name "*.pyc" -not -name "*.log" -exec grep -EH "__version__ *=" '{}' \;
=======
  if [ "$PRJNAME" != "Odoo" ]; then
    if [ -z "$2" ]; then
      find . -type f -not -path "*/.idea/*" -not -path "*/.docs/*" -not -path "*/.git/*" -not -name "*.pyc" -not -name "*.log" -exec grep -EH "__version__ *=" '{}' \;
>>>>>>> stash:wok_code/please
    else
      local ver_re2=${2//./\\.}
      local ver_re="[^0-9.]$ver_re2($|[^0-9.])"
      local new_ver=$3
<<<<<<< HEAD:wok_code/please.sh
      if [[ $opt_dry_run -ne 0 ]]; then
        echo "find . -type f -not -name "*.pyc" -not -name "*.log" -exec grep -EH "$ver_re" '{}' \;"
=======
      if [ $opt_dry_run -ne 0 ]; then
        echo "find . -type f -not -path "*/.idea/*" -not -path "*/.docs/*" -not -path "*/.git/*" -not -name "*.pyc" -not -name "*.log" -exec grep -EH "$ver_re" '{}' \;"
>>>>>>> stash:wok_code/please
      else
        find . -type f -not -path "*/.idea/*" -not -path "*/.docs/*" -not -path "*/.git/*" -not -name "*.pyc" -not -name "*.log" -exec grep -EH "$ver_re" '{}' \;
      fi
      if [ -n "$new_ver" ]; then
        for fn in $(find . -type f -not -path "*/.idea/*" -not -path "*/.docs/*" -not -path "*/.git/*" -not -name "*.pyc" -not -name "*.log" -exec grep -El "$ver_re" '{}' \;); do
          if [ $opt_dry_run -ne 0 ]; then
            echo "sed -e \"s/$ver_re2/$new_ver/\" -i $fn"
          else
            sed -e "s/$ver_re2/$new_ver/" -i $fn
          fi
        done
        if [ -f $PKGPATH/setup.py ]; then
          if [ $opt_dry_run -ne 0 ]; then
            echo "sed -e \"s/version=.$ver_re2./version='$new_ver'/\" -i $PKGPATH/setup.py"
          else
            sed -e "s/version=[\"']$ver_re2[\"']/version='$new_ver'/" -i $PKGPATH/setup.py
          fi
        fi
      fi
    fi
    if [ -f $PKGPATH/setup.py ]; then
      echo -n "Project $PRJNAME $prjversion [$PKGNAME]: "
      python $PKGPATH/setup.py --version
    fi
  else
    echo "Project $PRJNAME $BRANCH [$PKGNAME $prjversion]"
  fi
  return 0
}

do_config() {
  sts=$STS_SUCCESS
  if [ "$sub1" == "global" ]; then
    cfgfn=$TCONF
  elif [ "$sub1" == "repository" ]; then
    cfgfn=$(readlink -m $PKGPATH/../conf/.local_dist_pkg.conf)
  elif [ "$sub1" == "local" ]; then
    cfgfn=$(readlink -m $PKGPATH/conf/.local_dist_pkg.conf)
  elif [ "$sub1" == "current" ]; then
    cfgfn=$DIST_CONF
  elif [ "$sub1" == "zero" -o "$sub1" == "powerp" ]; then
    cfgfn=
  else
    echo "Missed parameter! use:"
    echo "\$ please config global|repository|local|current|zero|powerp [def|del]"
    sts=$STS_FAILED
  fi
  if [ $sts -eq $STS_SUCCESS ]; then
    if [ -n "$cfgfn" ]; then
      cfgdir=$(dirname $cfgfn)
      if [ "$sub2" == "del" ]; then
        [[ -f $cfgfn ]] && run_traced "rm -f $cfgfn"
        [[ ! -d $cfgfn ]] && run_traced "rmdir $cfgdir"
      elif [ $opt_dry_run -ne 0 ]; then
        echo "vim $cfgfn"
      else
        [[ ! -d $cfgfn ]] && run_traced "mkdir -p $cfgdir"
        [[ "$sub2" == "def" ]] && merge_cfg $cfgfn
        run_traced "vim $cfgfn"
      fi
    else
      r="origin_$sub1"
      x=$(git remote | grep $r)
      if [ -z "$x" ]; then
        local ro=$(build_odoo_param RORIGIN '' $PKGNAME $sub1)
        run_traced "git remote add $r $ro"
        run_traced "git remote set-url --add --push $r $ro"
      fi
    fi
  fi
  return $sts
}

do_wep() {
  wlog "do_wep '$1' '$2' '$3'"
  # [[ "$PRJNAME" == "Odoo" ]] && PKGPATH=$2 || PKGPATH=$1
  # [[ -z "$PKGPATH" ]] && PKGPATH="."
  # clean_dirs "$PKGPATH"
  [[ $(basename $PWD) == "tools" ]] && clean_dirs "./" || clean_dirs "../"
  [[ $opt_force -ne 0 ]] && set_executable
  return 0
}

OPTOPTS=(h        B       b          c        d        f         j        k        L         m       n           o        O        p         q           r     s        t         u       V           v)
OPTDEST=(opt_help opt_dbg opt_branch opt_conf opt_date opt_force opt_dprj opt_keep opt_log   opt_mis opt_dry_run opt_ids  opt_orig opt_dpath opt_verbose opt_r opt_srcs test_mode opt_uop opt_version opt_verbose)
OPTACTI=(1        1       "="        "="      "="      1         1        1        "="       1       1           "=>"     1        "="       0           1     "="      1         1       "*"         "+")
OPTDEFL=(1        0       ""         ""       ""       0         0        0        ""        0       0           ""       0        ""        -1          0     ""       0         0       ""          -1)
OPTMETA=("help"   ""      "branch"   "file"   "diff"   ""       "dprj"   "keep"   "logfile" ""      "noop"       "prj_id" ""       "path"    "quiet"     "rxt" "files"  "test"    "uop"   "version"   "verbose")
OPTHELP=("this help, type '$THIS help' for furthermore info"
  "debug mode"
  "branch: must be 6.1 7.0 8.0 9.0 10.0 11.0 12.0 13.0 or 14.0"
  "configuration file (def .travis.conf)"
  "date to search in log"
  "force copy (push) | build (publish) | set_exec (wep) | full (status)"
  "execute tests in project dir rather in test dir/old style synchro"
  "keep coverage statistics in annotate test/keep original repository | tests/ in publish"
  "log file name"
  "show missing line in report coverage"
  "do nothing (dry-run)"
  "push only external project ids (of push)"
  "pull original README (and docs) in distribution (deprecated)"
  "declare local destination path"
  "silent mode"
  "run restricted mode (w/o parsing travis.yml file) | recurse distribution OCB"
  "files to include in annotate test"
  "test mode (implies dry-run)"
  "check for unary operator W503 or no OCA/zero module translation"
  "show version end exit"
  "verbose mode")
OPTARGS=(actions sub1 sub2 sub3 sub4 sub5 sub6 sub7 sub8 sub9)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
HLPCMDLIST="help|build|chkconfig|commit|config|distribution|docs|download_rep|duplicate|edit|export|import|list|lsearch|publish|push|pythonhosted|synchro|replace|replica|show|status|test|translate|version|wep"
if [[ $opt_help -gt 0 ]]; then
  print_help "Developer shell\nAction may be on of:\n$HLPCMDLIST" \
    "© 2015-2021 by zeroincombenze®\nhttps://zeroincombenze-tools.readthedocs.io/\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi


opts_travis
CFG_init
conf_default
link_cfg $DIST_CONF $TCONF
# [[ $opt_verbose -gt 2 ]] && set -x
init_travis
prepare_env_travis "$actions" "-r"
sts=$STS_SUCCESS
sts_bash=127
sts_flake8=127
sts_pylint=127
test_sts=127

if [[ -z $sub1 ]]; then
  sub1="$sub2"
  sub2="$sub3"
  sub3="$sub4"
  sub4=""
fi
if [[ "$actions" == "help" ]]; then
  man $TDIR/$THIS.man
else
  [[ "$PRJNAME" == "Odoo" ]] && odoo_fver=$(build_odoo_param FULLVER ".")
  actions=${actions//+/ }
  actions=${actions//,/ }
  for action in $actions; do
    if [[ "${action:0:3}" == "if-" ]]; then
      opt_dry_run=1
      cmd="do_${action:3}"
    else
      cmd="do_${action/-/_}"
    fi
    if [[ "$(type -t $cmd)" == "function" ]]; then
      eval $cmd "'$sub1'" "'$sub2'" "'$sub3'"
      sts=$?
    else
      echo "Invalid action!"
      echo "Use $THIS $HLPCMDLIST"
      sts=$STS_FAILED
    fi
    [[ $sts -ne $STS_SUCCESS ]] && break
  done
fi
exit $sts