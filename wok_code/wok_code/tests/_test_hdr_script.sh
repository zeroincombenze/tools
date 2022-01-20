TDIR=$(readlink -f $(dirname $0))
test_script=$TDIR/sub.sh
cat <<EOF >$test_script
# Sub script $(date +"%Y-%m-%d %H:%M:%S")
# set -x
READLINK=\$(which greadlink 2>/dev/null) || READLINK=\$(which readlink 2>/dev/null)
export READLINK
THIS=\$(basename "\$0")
TDIR=\$(readlink -f \$(dirname \$0))
[ \$BASH_VERSINFO -lt 4 ] && echo "This script \$0 requires bash 4.0+!" && exit 4
HOME_DEV="\$HOME/devel"
[[ -x \$TDIR/../bin/python ]] && PYTHON=\$(readlink -f \$TDIR/../bin/python) || [[ -x \$TDIR/python ]] && PYTHON="\$TDIR/python" || PYTHON="python"
PYPATH=\$(echo -e "import os,sys;\nTDIR='"\$TDIR"';HOME_DEV='"\$HOME_DEV"'\nHOME=os.environ.get('HOME');d=os.path.join(HOME_DEV,'pypi');t=os.path.join(HOME,'tools');n=os.path.join(HOME,'pypi')\ndef apl(l,p,b):\n p2=os.path.join(p,b,b)\n p1=os.path.join(p,b)\n if os.path.isdir(p2):\n  l.append(p2)\n elif os.path.isdir(p1):\n  l.append(p1)\nl=[TDIR]\nv=''\nfor x in sys.path:\n if os.path.basename(x)=='site-packages':\n  v=x\n  break\nfor b in ('z0lib','zerobug','odoo_score','clodoo','travis_emulator'):\n if TDIR.startswith(d):\n  apl(l,d,b)\n elif TDIR.startswith(n):\n  apl(l,n,b)\n elif TDIR.startswith(t):\n  apl(l,t,b)\n elif v:\n  apl(l,v,b)\nl=l+os.environ['PATH'].split(':')\np=set()\npa=p.add\np=[x for x in l if x and x.startswith(HOME) and not (x in p or pa(x))]\nprint(' '.join(p))\n"|\$PYTHON)
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "PYPATH=\$PYPATH"
for d in \$PYPATH /etc; do
  if [[ -e \$d/z0librc ]]; then
    . \$d/z0librc
    Z0LIBDIR=\$(readlink -e \$d)
    break
  fi
done
if [[ -z "\$Z0LIBDIR" ]]; then
  echo "Library file z0librc not found!"
  exit 72
fi
[[ \$TRAVIS_DEBUG_MODE -ge 8 ]] && echo "Z0LIBDIR=\$Z0LIBDIR"

__version__=1.0.7

set +x

echo "  - Z0LIB=\$Z0LIBDIR/z0librc"
echo "  - HOME=\$HOME"
echo "  - HOME_DEV=\$HOME_DEV"
echo "  - PYTHON=\$PYTHON (\$(which \$PYTHON))"
echo "  - PYPATH=\$PYPATH"
exit 0
EOF

chmod +x $test_script
./cvt_script -kyq $test_script

USER_HOME=$(getent passwd $USER|awk -F: '{print $6}')
for pkg in clodoo odoo_score python_plus os0 z0bug_odoo z0lib zerobug; do
  [[ -d $HOME/.local/lib/python2.7/site-packages/$pkg ]] && rm -fR $HOME/.local/lib/python2.7/site-packages/$pkg && rm -fR $HOME/.local/lib/python2.7/site-packages/$pkg-*.dist-info
done
[[ -d $HOME/.local/bin/python2.7 ]] && rm -fR $HOME/.local/bin/python2.7
[[ -f ~/devel/venv/bin/z0librc ]] && mv ~/devel/venv/bin/z0librc ~/devel/venv/bin/z0librc~
venv_dir=~/VENV_1
# set -x
for home_dev in devel venv_tools; do
  vem create $venv_dir -p2.7 -Ifq
  rm_dir=0
  [[ $home_dev == "venv_tools" ]] && PATH=$(echo -e "import os\nprint(':'.join([d.replace('/devel/venv','/venv_tools').replace('/devel','/venv_tools') for d in os.environ['PATH'].split(':')]))\n"|python)
  [[ $home_dev == "devel" ]] && PATH=$(echo -e "import os\nprint(':'.join([d.replace('/venv_tools','/devel/venv',1).replace('/venv_tools','/devel') for d in os.environ['PATH'].split(':')]))\n"|python)
  echo ""
  echo "HOME_DEV=$home_dev"
  echo "PATH=$PATH"
  if [[ ! -d $HOME/$home_dev ]]; then
    rm_dir=1
    [[ $home_dev == "devel" ]] && mkdir ~/devel && cp -R ~/venv_tools ~/devel/venv
    [[ $home_dev == "venv_tools" ]] && cp -R ~/devel/venv ~/venv_tools
  fi
  [[ $home_dev == "venv_tools" ]] && echo -e ""
  for path in $USER_HOME $USER_HOME/devel/pypi/wok_code/wok_code $USER_HOME/pypi/wok_code/wok_code $USER_HOME/devel/venv/bin $venv_dir; do
    echo "  ===[$path]==="
    cd $path
    [[ $path == $venv_dir ]] && SAVED_HOME=$HOME && . bin/activate && HOME=$venv_dir
    cp -p $test_script ./
    cur_script="./$(basename $test_script)"
    sed -E "s|^HOME_DEV=.*|HOME_DEV=\"\$HOME/$home_dev\"|" -i $cur_script
    eval $cur_script
    [[ $? -ne 0 ]] && echo "TEST FAILED!!!!" && exit 1
    match=""

    [[ $home_dev == "devel" && $PWD == $USER_HOME ]] && match="Z0LIB=$USER_HOME/tools/z0lib/z0librc"
    [[ $home_dev == "devel" && $PWD == $USER_HOME/devel/pypi/wok_code/wok_code ]] && match="Z0LIB=$USER_HOME/devel/pypi/z0lib/z0lib/z0librc"
    [[ $home_dev == "devel" && $PWD == $USER_HOME/pypi/wok_code/wok_code ]] && match="Z0LIB=$USER_HOME/tools/z0lib/z0librc"
    [[ $home_dev == "devel" && $PWD == $USER_HOME/devel/venv/bin ]] && match="Z0LIB=$USER_HOME/devel/venv/lib/python2.7/site-packages/z0lib/z0librc"
    [[ $home_dev == "devel" && $PWD == $venv_dir ]] && match="Z0LIB=/home/odoo/VENV_1/lib/python2.7/site-packages/z0lib/z0librc"

    [[ $home_dev == "venv_tools" && $PWD == $USER_HOME ]] && match="Z0LIB=$USER_HOME/tools/z0lib/z0librc"
    [[ $home_dev == "venv_tools" && $PWD == $USER_HOME/devel/pypi/wok_code/wok_code ]] && match="Z0LIB=$USER_HOME/venv_tools/bin/z0librc"
    [[ $home_dev == "venv_tools" && $PWD == $USER_HOME/pypi/wok_code/wok_code ]] && match="Z0LIB=$USER_HOME/pypi/z0lib/z0lib/z0librc"
    [[ $home_dev == "venv_tools" && $PWD == $USER_HOME/devel/venv/bin ]] && match="Z0LIB=$USER_HOME/devel/venv/lib/python2.7/site-packages/z0lib/z0librc"
    [[ $home_dev == "venv_tools" && $PWD == $venv_dir ]] && match="Z0LIB=/home/odoo/VENV_1/lib/python2.7/site-packages/z0lib/z0librc"

    if [[ -n $match ]]; then
      echo "  - Check for $match ..."
      if ! $cur_script | grep "$match" &>/dev/null; then
        echo "TEST FAILED: no valid path >$match< found!" && exit 1
      fi
    fi

    if [[ $path == $venv_dir ]]; then
      echo "  ===[$path(2)]==="
      for p in clodoo os0 python-plus z0lib z0bug_odoo zerobug; do
        pip uninstall $p -y
      done
      cp $USER_HOME/devel/pypi/z0lib/z0lib/z0librc $venv_dir/bin
      eval $cur_script
      [[ $? -ne 0 ]] && echo "TEST FAILED!!!!" && exit 1
      match="$USER_HOME/VENV_1/bin/z0librc"
      if ! $cur_script | grep "$match" &>/dev/null; then
        echo "TEST FAILED: no valid path >$match< found!" && exit 1
      fi
    fi

    [[ $path == $venv_dir ]] && deactivate && HOME=$SAVED_HOME && rm -fR $venv_dir

    rm -f $cur_script
  done
  [[ $rm_dir -ne 0 ]] && echo rm -fR $HOME/$home_dev
done
[[ -f ~/devel/venv/bin/z0librc~ ]] && mv ~/devel/venv/bin/z0librc~ ~/devel/venv/bin/z0librc
rm -f $test_script
