#__version__=0.1.3
# Change os PATH in order to run lessc 2.0+ instead of lessc 1.7
# Odoo won't work if lessc version is 2.0-
# Standard ruby set lessc 1.7
#
# This script have to deployed in /etc/profile.d
# Warning: if you create startup script with lisa_bld_ods this script is incorporated
# but service start wil be slower
#
# set -x

set_lessc() {
    local f=$1
    local minv=$2
    [ -z "$minv" ] && minv=30000
    local lv=$($f --version 2>/dev/null|grep -Eo "[0-9.]+"|head -n1|awk -F. '{print $1*10000 + $2*100 + $3}')
    [ -z "$lv" ] && lv=0
    if [ $lv -ge $minv ]; then
      if [ $EUID -eq 0 ]; then
        [ -x /usr/bin/lessc ] && rm -f /usr/bin/lessc
        echo "\$ ln -s $f /usr/bin"
        ln -s $f /usr/bin
      else
        local p=$(dirname $f)
        echo "\$ export PATH=$P:$PATH"
        export PATH=$P:$PATH
      fi
    fi
}

NEW_PATH=
ALT_PATH=
# Set ruby 2.4.0 less priority in PATH
for p in ${PATH//:/ }; do
  if [[ "$p" =~ "ruby-2.4.0" ]]; then
    [ -n "$ALT_PATH" ] && ALT_PATH=$ALT_PATH:$p || ALT_PATH=$p
  else
    [ -n "$NEW_PATH" ] && NEW_PATH=$NEW_PATH:$p || NEW_PATH=$p
  fi
done
[ -n "$ALT_PATH" ] && NEW_PATH=$NEW_PATH:$ALT_PATH
export PATH=$NEW_PATH

lv=$(lessc --version 2>/dev/null|grep -Eo "[0-9.]+"|head -n1|awk -F. '{print $1*10000 + $2*100 + $3}')
[ -z "$lv" ] && lv=0
if [ $lv -lt 30000 ]; then
  echo "# Searching for lessc ..."
  alt_less=
  for f in $(find / -nowarn -type f -name lessc 2>/dev/null); do
    lv=$($f --version 2>/dev/null|grep -Eo "[0-9.]+"|head -n1|awk -F. '{print $1*10000 + $2*100 + $3}')
    [ -z "$lv" ] && lv=0
    if [ $lv -gt 30000 ]; then
      set_lessc $f 30000
      break
    elif [ $lv -gt 20000 ]; then
      alt_less=$f
    fi
  done
fi
lv=$(lessc --version 2>/dev/null|grep -Eo "[0-9.]+"|head -n1|awk -F. '{print $1*10000 + $2*100 + $3}')
[ -z "$lv" ] && lv=0
if [ $lv -lt 20000 -a -n "$alt_less" ]; then
  set_lessc $alt_less 20000
fi
# lessc --version