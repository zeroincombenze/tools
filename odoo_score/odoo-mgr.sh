#! /bin/bash
[[ -z $1 ]] && echo "$0 odoo_vid action" && exit 1
if [[ $1 == "-h" ]]; then
  echo "odoo_vid example: 10.0 12.0 oca16"
  echo "action is:"
  echo "  start"
  echo "  stop"
  echo "  status"
  echo "  enable"
  echo "  disable"
  exit 0
fi
. /home/odoo/devel/pypi/clodoo/clodoo/odoorc
vid="$1"
fn=$(build_odoo_param CONFN $vid "" "" "MULTI")
svc=$(build_odoo_param SVCNAME $vid "" "" "MULTI")
if [[ $2 =~ (start|stop|status|enable|disable) ]]; then
  echo "systemctl $2 $svc"
  sudo systemctl $2 $svc
else
  echo "Invalid action"
  echo "$0 $vid start|stop|status|enable|disablw"
fi