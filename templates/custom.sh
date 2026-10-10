#!/bin/sh
# /etc/init.d/custom.sh

export HOSTNAME_DEV="(pc|nb)[0-9]+(shs|z0|lx)"
export HOSTNAME_PRO="shs[0-9]*pr[do][0-9]*"
# HOSTNAME_PRO=shsdef16

# Prompt: fg -> host production,devel,other / bg -> user / c2 -> privileged user
if [ -n "$PS1" ]; then
  bg="40"
  [[ $HOSTNAME =~ (shs|z0) ]] && c2="32" || c2="33"
  if [[ $HOSTNAME =~ $HOSTNAME_PRO && $HOSTNAME_DEV == $HOSTNAME_PRO ]]; then
    # Host PRO+DEV (MAGENTA)
    fg="35"
  elif [[ $HOSTNAME =~ $HOSTNAME_PRO ]]; then
    # Host PRO w/o DEV (RED)
    fg="31"
  elif [[ $HOSTNAME =~ $HOSTNAME_DEV ]]; then
    # Host DEV (GREEN)
    fg="32"
  else
    # Undefined (YELLOW)
    fg="36"
  fi
  if [[ $EUID -eq 0 ]]; then
    bg="47" && c2="31"
  elif [[ $USER =~ ^(antoniov|zeroadm|vigliotti)$ ]]; then
    c2="31"
  elif [[ $USER == "postgres" ]]; then
    bg="43"
  elif [[ $USER != "odoo" ]]; then
    bg="45"
    [[ $fg -eq 45 ]] && bg="43"
  fi
  PS1="\[\033[?25h\033[${fg};${bg}m\][\u@\h:\[\033[${c2}m\]\w]\\$\[\033[0m\] "
fi

# Postgres / odoo mapping: 2026 -> port 5432 reserved for local host default
# Odoo 6.1 - 7.0 -> psql-9.5: 5435 (deprecated)
# Odoo 7.0 - 10.0 -> psql-10: 5433 (default for Odoo 7.0 - 10.0)
# Odoo 7.0 - 15.0 -> psql-12: 5434 (default for Odoo 11.0 -15.0)
# Odoo 16.0 - 19.0 -> psql-16: 5436 (default for Odoo 16.0 - 17.0)
# Odoo 18-0 - 19.0 -> psql-18: 5438 (default for Odoo 18.0 - 19.0)
# alias psql-9.5='psql -p5435'
alias psql-10='psql -p5433'
alias psql-12='psql -p5434'
alias psql-16='psql -p5436'
alias psql-18='psql -p5432'

# User specific environment
for path in $HOME/.local/bin $HOME/bin; do
    [[ ":$PATH:" =~ ":$path:" ]] && continue
    [[ -d $path && -n "$PATH" ]] && export PATH=$path:$PATH
    [[ -d $path && -z "$PATH" ]] && export PATH=$path
done
for path in $HOME/node_modules/less/bin; do
    [[ ":$PATH:" =~ ":$path:" ]] && continue
    [[ -d $path && -n "$PATH" ]] && export PATH=$PATH:$path
    [[ -d $path && -z "$PATH" ]] && export PATH=$path
done

[[ -z $HOME_DEVEL && -d $HOME/odoo/devel ]] && export HOME_DEVEL="$HOME/odoo/devel"
[[ -z $HOME_DEVEL && -d $HOME/devel ]] && export HOME_DEVEL="$HOME/devel"
[[ -n $HOME_DEVEL && -f $HOME_DEVEL/activate_tools ]] && . $HOME_DEVEL/activate_tools

if [[ -n $PS1 ]]; then
    # export VERBOSE_MODE=1
    alias diffe="diff --suppress-common-line -y"
    alias dir='dir -lh --color=auto'
fi

export ODOO_GIT_ORGID="(zero)"
export ODOO_GIT_SHORT="(oca)"
# export npm_config_prefix="$HOME/.local"
umask 002
