f() {
  local p=$1
  l=${p[0]}
  o=${p[1]}
  r=${p[2]}
  echo "l=$l; o=$o; r=$r"
}

declare -a p
p[0]="left"
p[1]="op"
p[2]="right"
echo "l=${p[0]}; o==${p[1]}; r=${p[2]}"
f "$p"
