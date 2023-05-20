#!/bin/bash
[[ -n $1 && $1 == "-h" ]] && echo $0 [start][reload][restart][start-stopped][status][stop] && exit 0
[[ -n $1 && $1 =~ (start|reload|restart|start-stopped|status|stop) ]] && action=$1 || action="start"
if [[ $action == "start" ]]
then
    hwclock|tr " " "T"|xargs -I '{}' date "+%Y-%m-%dT%H:%M:%S.%N" -s "{}"
    apt update -y && apt upgrade -y && apt autoremove -y
    for f in /tmp/*; do [[ -d $f ]] && rm -fR $f || rm -f $f; done
    [[ -x /usr/local/bin/systemd_cmd ]] && systemd_cmd $action
    systemctl $action set_hosts
    chown odoo:odoo /var/run/odoo/*
    chown odoo:odoo /var/log/odoo/*
fi
for svc in postgresql apache2 httpd odoo link_windows_cmd
do
    for fn in /etc/init.d/${svc}*
    do
        [[ ! -x $fn ]] && continue
        [[ $action != "start-stopped" ]] && systemctl $action $(basename $fn) && continue
        systemctl status $(basename $fn) | grep "stopped" && systemctl start $(basename $fn)
    done
done
[[ $action == "stop" && -x /usr/local/bin/systemd_cmd ]] && systemd_cmd $action
