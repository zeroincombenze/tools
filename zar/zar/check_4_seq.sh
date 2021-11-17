#!/usr/bin/env bash
# __version__=1.3.36.1
READLINK=$(which greadlink 2>/dev/null) || READLINK=$(which readlink 2>/dev/null)
export READLINK
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
[ $BASH_VERSINFO -lt 4 ] && echo "This script cvt_script requires bash 4.0+!" && exit 4
[[ -d "$HOME/dev" ]] && HOME_DEV="$HOME/dev" || HOME_DEV="$HOME/devel"
PYPATH=$(echo -e "import os,sys;\nTDIR='"$TDIR"';HOME_DEV='"$HOME_DEV"'\nHOME=os.environ.get('HOME');y=os.path.join(HOME_DEV,'pypi');t=os.path.join(HOME,'tools')\ndef apl(l,p,x):\n  d2=os.path.join(p,x,x)\n  d1=os.path.join(p,x)\n  if os.path.isdir(d2):\n   l.append(d2)\n  elif os.path.isdir(d1):\n   l.append(d1)\nl=[TDIR]\nfor x in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(y):\n  apl(l,y,x)\n elif TDIR.startswith(t):\n  apl(l,t,x)\nl=l+os.environ['PATH'].split(':')\np=set()\npa=p.add\np=[x for x in l if x and x.startswith(HOME) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|python)
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=$PYPATH"
for d in $PYPATH /etc; do
  if [[ -e $d/z0librc ]]; then
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
[[ $TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=$Z0LIBDIR"

user=${2:-odoo}
while IFS=\| read a tbl typ own; do
  if [[ "$a" == "public" && ( "$typ" == "table" || "$typ" == "tabella" ) && "$own" == $user ]]; then
    # echo "Table=$tbl type=$typ own=$own"
    sql="select last_value from ${tbl}_id_seq;"
    psql -tc "$sql" "$1" &>/dev/null
    if [ $? -eq 0 ]; then
      last=$(psql -tc "$sql" "$1")
      last=$(printf "%d" $last)
      sql="select max(id) from ${tbl};"
      psql -tc "$sql" "$1" &>/dev/null
      if [ $? -eq 0 ]; then
        max=$(psql -tc "$sql" "$1")
        max=$(printf "%d" $max)
        if [ $last -lt $max ] || [ "$3" == "-z" -a $max -eq 0 ] || [ "$3" == "-f" -a $last -ne $max ]; then
          [ $last -lt $max ] && echo "*** Error in table $tbl: last value $last < max $max! ***"
          [ $last -ge $max ] && echo "Reset table $tbl: last value $last != max $max!!"
          ((max++))
          psql -c "alter sequence ${tbl}_id_seq restart $max" "$1"
        else
          printf "Table %-50.50s (%d/%d)\n" "$tbl" $last $max
        fi
      fi
    fi
  fi
done < <(psql -Atc "\\d" "$1")
