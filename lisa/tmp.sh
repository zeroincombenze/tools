f() {
    local c=$(echo "$1"|grep -Eo '[!<=>]*'|wc -l)
    local i pkgname Lop Rop Lreqver Rreqver xtlcmd op x
    pkgname=$(echo "$1"|grep -Eo '[^!<=>]*'|head -n1)
    i=1
    while ((i<=c)); do
      op=$(echo "$1"|grep -Eo '[!<=>]*'|head -n$i|tail -n1)
      ((i++))
      x=$(echo "$1"|grep -Eo '[^!<=>]*'|head -n$i|tail -n1)
      # echo "$i)$x$op"
      if [ "$op" == "!!" ]; then
        xtlcmd=$x
      elif [ -z "$Lreqver" ]; then
        Lreqver=$x
        Lop=$op
      elif [ -z "$Rreqver" ]; then
        Rreqver=$x
        Rop=$op
      fi
    done
    echo "$pkgname~$Lop~$Lreqver~$Rop~$Rreqver~$xtlcmd"
}

f "$1"

