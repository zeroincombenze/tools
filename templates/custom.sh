#!/bin/sh
# /etc/init.d/custom.sh

export HOSTNAME_DEV="(pc|nb)[0-9]+(shs|z0|lx)"
export HOSTNAME_PRD="shs[0-9]*pr[do][0-9]*"
# HOSTNAME_PRD=shsdef16

if [ -n "$PS1" ]; then
  [[ $EUID -eq 0 ]] && fg=";47"
  if [[ $HOSTNAME =~ $HOSTNAME_PRD && $HOSTNAME_DEV == $HOSTNAME_PRD ]]; then
    PS1="\[\033[1;31${fg}m\][\u@\h:\W]\\$\[\033[0m\] "
  elif [[ $HOSTNAME =~ $HOSTNAME_PRD && -z "$HOSTNAME_DEV" ]]; then
    PS1="\[\033[1;31${fg}m\][\u@\h:\W]\\$\[\033[0m\] "
  elif [[ $HOSTNAME =~ $HOSTNAME_DEV ]]; then
    PS1="\[\033[1;34${fg}m\][\u@\h:\W]\\$\[\033[0m\] "
  elif [[ $HOSTNAME =~ $HOSTNAME_PRD ]]; then
    PS1="\[\033[1;35${fg}m\][\u@\h:\W]\\$\[\033[0m\] "
  else
    PS1="\[\033[1;30${fg}m\][\u@\h:\W]\\$\[\033[0m\] "
  fi
fi

alias psql-9.5="psql -p5434"
alias psql-10="psql -p5433"
alias psql-14="psql -p5435"
alias psql-15="psql -p5436"

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

export ODOO_GIT_ORGID="(librerp|zero)"
export ODOO_GIT_SHORT="(oca|librerp)"
export npm_config_prefix="$HOME/.local"
umask 002

