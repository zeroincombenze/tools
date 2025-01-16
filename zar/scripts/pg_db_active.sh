#! /bin/bash
# -*- coding: utf-8 -*-
#
# pg_db_active
# manage postgres sessions
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2016-2025 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
# Based on template 2.0.17
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

__version__=2.0.7


db_act_list() {
# db_act_list(-C|-c|-k|-l|-u|-w|-z [pos])  # count_all, count, return older pid to kill, list sessions, return active sess to wait
    local act=$1
    local fw ord
    local sql sqlc sess_ctr LOG wait4 valid_sess db pid w st older usr user
    local pos=0
    [[ -n "$2" ]] && pos=$2
    [[ $PSQL_VER -ge 96 ]] && fw="wait_event" || fw="waiting"
    [[ "$act" == "-z" ]] && ord="desc" || ord=""
    if [[ -z "$DB" ]]; then
      sql="select datname,pid,state_change,$fw,state,usename from pg_stat_activity where pid<>pg_backend_pid() order by state_change $ord;"
    else
      sql="select datname,pid,state_change,$fw,state,usename from pg_stat_activity where datname='$DB' and pid<>pg_backend_pid() order by state_change $ord;"
    fi
    if [[ $act == "-c" || $act == "-C" ]]; then
      if [[ -z "$DB" || $act == "-C" ]]; then
        sqlc="select count(pid) from pg_stat_activity where pid<>pg_backend_pid();"
      else
        sqlc="select count(pid) from pg_stat_activity where datname='$DB' and pid<>pg_backend_pid();"
      fi
      sess_ctr=$($PSQL -Atc "$sqlc"|head -n1)
      sess_ctr=$(echo $sess_ctr)
    else
      LOG=~/${THIS}_$$.log
      $PSQL -Atc "$sql" -o $LOG
      wait4=0
      sess_ctr=0
      valid_sess=0
      older=0
      user=
      while IFS=\| read db pid dt w st usr; do
        [[ $PSQL_VER -ge 95 && -z "$st" ]] && st="idle"
        if [[ -n "$st" ]]; then
          ((sess_ctr++))
          if [[ $PSQL_VER -ge 95 ]]; then
            [[ -n "$w" && ( $w =~ Lock || ! $w =~ Read ) ]] && w="t" || w="f"
          fi
          if [[ $act == "-l" ]]; then
            printf "(%6.6s) %-32.32s %2.2s %-8.8s %19.19s %9.9s\n" "$pid" "$db" "$w" "$st" "$dt" "$usr"
          fi
          if [[ $older -eq 0 && $w == "f" && $st == "idle" && $db != "postgres" ]]; then
            ((valid_sess++))
            if [[ $pos -gt 0 ]]; then
              if [[ $valid_sess -eq $pos ]]; then
                older=$pid;
                user=$usr
              fi
            else
              older=$pid
              user=$usr
            fi
          fi
          if [[ "$db" == "$DB" ]]; then
            if [[ "$w" != "f" ]]; then
              wait4=1
            fi
            if [[ "${st:0:4}" != "idle" ]]; then
              wait4=1
            fi
          fi
        fi
        [[ $pos -gt 0 && $valid_sess -eq $pos ]] && break
      done < $LOG
      rm -f $LOG
    fi
    if [[ $act == "-w" ]]; then
      return $wait4
    elif [[ $act == "-c" || $act == "-C" || $act == "-l" ]]; then
      echo $sess_ctr
    elif [[ $act == "-k" || $act == "-z" ]]; then
      echo $older
    elif [[ $act == "-u" ]]; then
      echo $user
    fi
    return 0
}

OPTOPTS=(h        a           C        c        G         k        L        n           p        P         s        U        V           v           w       z)
OPTLONG=(help     kill-all-db count    count-db grant     kill-out lock     dry-run     pool     port      show     user     version     verbose     wait    last)
OPTDEST=(opt_help act_kill4db act_ctra act_ctr  opt_grant act_kill opt_lock opt_dry_run pool     opt_port  opt_show opt_user opt_version opt_verbose wait_db opt_last)
OPTACTI=("+"      "1>"        "1>"     "1>"     1         "1>"     1        1           "="      "="       1        "="      "*"         1           1       1)
OPTDEFL=(0        0           0        0        0         0        0        0           -1       ""        ""       ""       ""          0           0       0)
OPTMETA=("help"   "kill_all" "count"   "count"  ""        "kill"   ""       ""          "number" "dbport"  ""       "dbuser" "version"   "verbose"   "wait"  "")
OPTHELP=("this help"
 "kill all sessions of DB!"
 "count all active connections"
 "count active connections on DB"
 "grant connection to DB"
 "kill all sessions out of pool"
 "lock DB to avoid new connections (may be used with -a)"
 "do nothing (dry-run)"
 "declare # of session pool"
 "db port"
 "show pool size"
 "db user"
 "show version end exit"
 "verbose mode"
 "wait for DB idle after kill"
 "search just for last session")
OPTARGS=(DB)

parseoptargs "$@"
if [[ "$opt_version" ]]; then
  echo "$__version__"
  exit 0
fi
if [[ $opt_help -gt 0 ]]; then
  print_help "Check/kill for postgres DB sessions"\
  "(C) 2016-2025 by zeroincombenze®\nhttp://wiki.zeroincombenze.org/en/Postgresql\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi
PSQL=""
for port in $opt_port 5432 5433 5434 5435 5436 5437; do
  for u in $opt_user $USER odoo openerp postgresql; do
    if [[ -n "$u" ]]; then
      [[ -n $port ]] && opt="-p$port" || opt=""
      psql -U$u $opts -l &>/dev/null
      if [[ $? -eq 0 ]]; then
        dbuser=$u
        if [[ -n $port ]]; then
          dbport=$port
          PSQL="psql -U$u -p$port -dtemplate1"
        else
          dbport=""
          PSQL="psql -U$u -dtemplate1"
        fi
        break
      fi
    fi
  done
  [[ -n $PSQL ]] && break
done
if [[ -z $PSQL ]]; then
    echo "Denied inquire with psql. Please configure user $USER to access via psql"
    exit 2
fi
PSQL_VER=$(psql --version|grep --color=never -Eo "[0-9]+\.[0-9]"|tr -d "."|head -n1)
if [[ $pool -lt 1 ]]; then
  pool=$($PSQL -Atc "select setting from pg_settings where name='max_connections';"|head -n1)
  pool=$(echo $pool)
fi
if [[ $opt_show -ne 0 ]]; then
  echo $pool
  exit 0
fi
if [[ $pool -lt 5 ]]; then
  pool=5
fi
sleep_tm=5
loop_ctr=1
if [[ $act_ctr -ne 0 ]]; then
  if [[ -n "$DB" ]]; then
    act=-c
  else
    echo "Missing DB name!"
    exit 1
  fi
elif [[ $act_ctra -ne 0 ]]; then
  act=-C
elif [[ $act_kill -ne 0 ]]; then
  act=-C
  loop_ctr=8
  sleep_tm=1
elif [[ $act_kill4db -ne 0 ]]; then
  if [[ -n "$DB" ]]; then
    act=-c
    loop_ctr=1
    sleep_tm=0
    if [[ $opt_lock -gt 0 ]]; then
      [[ $opt_verbose -gt 0 ]] && echo "Revoke access to $dbuser from $DB"
      if [[ $opt_dry_run -eq 0 ]]; then
        sqlc="REVOKE CONNECT ON DATABASE $DB FROM PUBLIC, $dbuser;"
        $PSQL -tc "$sqlc" &>/dev/null
      fi
    fi
  else
    echo "Missing DB name!"
    exit 1
  fi
elif [[ $wait_db -ne 0 ]]; then
  if [[ -n "$DB" ]]; then
    act=-c
  else
    act=-C
  fi
else
  act=-l
fi
let threshold="$pool/5"
let pool_max="$pool-$threshold"
let pool_min="$pool_max-$threshold"
bias=0
sts=1
while [[ $sts -ne 0 && $loop_ctr -gt 0 ]]; do
  if [[ $act_kill -ne 0 || $act_kill4db -ne 0 ]]; then
    sess_ctr=$(db_act_list "$act")
    [[ $opt_verbose -gt 0 ]] && echo "Found $sess_ctr currently active sessions"
    if [[ $sess_ctr -gt 0 ]]; then
      if [[ $act_kill4db -ne 0 ]]; then
        killing=1
        if [[ $bias -eq 0 ]]; then
          bias=1
          if [[ $opt_last -eq 0 ]]; then
            loop_ctr=$sess_ctr
            ((loop_ctr++))
          fi
        elif [[ $opt_dry_run -ne 0 ]]; then
          ((bias++))
        fi
      elif [[ $sess_ctr -gt $pool_max ]]; then
        killing=1
        ((bias++))
        loop_ctr=$threshold
      elif [[ $sess_ctr -gt $pool_min && $bias -ne 0 ]]; then
        killing=1
      else
        killing=0
        bias=0
      fi
      if [[ $killing -gt 0 ]]; then
        if [[ $opt_last -ne 0 ]]; then
          if [[ $opt_dry_run -ne 0 ]]; then
            pid=$(db_act_list "-z" "$bias")
            user=$(db_act_list "-u" "$bias")
          else
            pid=$(db_act_list "-z")
            user=$(db_act_list "-u")
          fi
        else
          if [[ $opt_dry_run -ne 0 ]]; then
            pid=$(db_act_list "-k" "$bias")
            user=$(db_act_list "-u" "$bias")
          else
            pid=$(db_act_list "-k")
            user=$(db_act_list "-u")
          fi
        fi
        if [[ ${pid:-0} -ne 0 ]]; then
          if [[ $opt_dry_run -eq 0 ]]; then
            [[ $opt_verbose -gt 0 ]] && echo "Killing process pid=$pid of $user"
            sqlc="select pg_terminate_backend(pid) from pg_stat_activity where pid<>pg_backend_pid() and pid=$pid;"
            [[ $opt_verbose -gt 0 ]] && run_traced "$PSQL -tc \"$sqlc\" -U$user"
            $PSQL -tc "$sqlc" -U $user &>/dev/null
          else
            echo "Process pid=$pid of $user should be killed"
            sts=0
          fi
        elif [[ $opt_dry_run -eq 0 ]]; then
          ((loop_ctr++))
        fi
        sts=1
      else
        sts=0
      fi
    else
      sts=0
    fi
  else
    db_act_list "$act"
    sts=$?
  fi
  ((loop_ctr--))
  if [[ $sts -ne 0 ]]; then
    sleep $sleep_tm
  fi
done
if [[ $wait_db -ne 0 && -n "$DB" ]]; then
  act=-w
  loop_ctr=3
  sleep_tm=1
  while [ $sts -ne 0 -a $loop_ctr -gt 0 ]; do
    db_act_list "$act"
    sts=$?
    ((loop_ctr--))
    if [ $sts -ne 0 ]; then
      if [ $opt_verbose -gt 0 ]; then
        echo "Waiting for DB going idle"
      fi
      sleep $sleep_tm
    fi
  done
  sleep 1
fi
if [ $opt_grant -gt 0 -a -n "$DB" ]; then
  if [ $opt_verbose -gt 0 ]; then
    echo "Grant access to $DB"
  fi
  if [ $opt_dry_run -eq 0 ]; then
    sqlc="GRANT CONNECT ON DATABASE $DB TO PUBLIC, odoo;"
    $PSQL -tc "$sqlc" &>/dev/null
  fi
elif [ $opt_lock -gt 0 -a -n "$DB" ]; then
  if [ $opt_verbose -gt 0 ]; then
    echo "Revoce access from $DB"
  fi
  if [ $opt_dry_run -eq 0 ]; then
    sqlc="REVOKE CONNECT ON DATABASE $DB FROM PUBLIC, odoo;"
    $PSQL -tc "$sqlc" &>/dev/null
  fi
fi
exit $sts
