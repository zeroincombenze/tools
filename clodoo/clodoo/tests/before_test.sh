#!/bin/bash

for port in 8172 8170 8168; do
  for ctr in {11..0}; do
      ss -lt|grep 0.0.0.0:$port
      [[ $? -eq 0 ]] && break
      [[ $port -ge 8200 ]] && vid="oca$((port-8260))" || vid="odoo$((port-8160))"
      echo "No Odoo instance running found at port $port ($vid)"
      sleep 5
  done
  [[ $ctr -eq 0 ]] && exit 1
done
[[ $ctr -eq 0 ]] && exit 1
exit 0
