set_ver() {
    local chid lnemod newln prm val sfx prp cup ver alt_ver fntmp
    ver=_$odoo_ver
    if [ "$odoo_ver" == "7.0" ]; then
      alt_ver=_8.0
    else
      alt_ver=_7.0
    fi
    fntmp=$1.tmp
    if  [ -f $fntmp ]; then
      rm -f $fntmp
    fi
    newln=
    prp=
    echo "===== File $1 ====="
    while IFS= read lne; do
      chid=${lne:0:1}
      lnemod="$lne"
      if [ -z "$lne" ]; then
        :
      elif [ "$chid" == "#" -o "$chid" == ";" ]; then
        :
      elif [ "$chid" == "[" ]; then
        prp=
      else
        prm=$(echo $lne|awk -F= '{print $1}')
        sfx=${prm: -4}
        cup=${prm:0: -4}
        val="$(echo $lne|awk -F= '{print $2}')"
        # echo "<<p=$prm; v=$val; x=$prp; s=$sx; c=$cup>>"
        if [ "$prm" == "oe_version" ]; then
          lnemod="oe_version=$odoo_ver"
          prp=
        elif [ "$prm" == "db_name" -a -n "$db_name" ]; then
          lnemod="db_name=$db_name"
          prp=
        elif [ "$prm" == "$prp" ]; then
          lnemod="  "
        elif [ "$sfx" == "$ver" ]; then
          newln="$cup=$val"
        else
          prp=
        fi
        if [ "$sfx" == "_7.0" -o "$sfx" == "_8.0" -o "$sfx" == "_9.0" -o "$sfx" == "_10.0" ]; then
          prp=$cup
          # echo "<<<$prp>>>"
        fi
      fi
      # if [ "$lne" != "$lnemod" ]; then
      #   echo "$lne->$lnemod"
      # fi
      if [ "$lnemod" != "  " ]; then
        echo "$lnemod">>$fntmp
     fi
      if [ -n "$newln" ]; then
        # echo "$newln"
        echo "$newln">>$fntmp
      fi
      newln=
    done < $1
    # diff -y $1 $fntmp|less
    mv $1 $1.bak
    mv $fntmp $1
}

if [ -z "$1" ]; then
  echo "$0 odoo_version [dbname]"
  exit 1
fi
if [ "$1" != "7.0" -a "$1" != "8.0" -a "$1" != "9.0" -a "$1" != "10.0" ]; then
  echo "$0 (7.0|8.0|9.0|10.0)"
  exit 1
fi
odoo_ver=$1
db_name=$2
for f in conf/*conf; do
  set_ver $f
done
# set_ver conf/z0_install_11.conf
