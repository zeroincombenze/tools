#!/usr/bin/env bash
[[ ! $1 =~ ^(3.6|3.7|3.8|3.9) ]] && echo "$0 3.6|3.7|3.8|3.9" && exit 1
[[ $EUID -ne 0 ]] && echo "This code may be executed just by root user" && exit 1
[[ -z $(which wget 2>/dev/null) ]] && echo "Please install wget" && exit 1
pyver="$1"
[[ $1 == "3.9" ]] && pyver="$1.15"
[[ $1 == "3.8" ]] && pyver="$1.15"
[[ $1 == "3.7" ]] && pyver="$1.15"
[[ $1 == "3.6" ]] && pyver="$1.15"
echo "If you want to use sqlite you should install some packages before this command"
echo "apt install libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev"
read -p "Press RET to continue ..."
echo "\$ cd /tmp"
cd /tmp
echo "\$ wget https://www.python.org/ftp/python/$pyver/Python-$pyver.tgz"
[[ ! -f Python-$pyver.tgz ]] && echo "File Python-$pyver.tgz already downloaded"
[[ ! -f Python-$pyver.tgz ]] && wget https://www.python.org/ftp/python/$pyver/Python-$pyver.tgz
[[ ! -f Python-$pyver.tgz ]] && echo "No file Python-$pyver.tgz downloaded!" && exit 2
echo "\$ tar -xf Python-$pyver.tgz"
tar -xf Python-$pyver.tgz
[[ ! -d Python-$pyver ]] && echo "No directory Python-$pyver created!" && exit 2
echo "\$ cd python-$pyver"
cd Python-$pyver
echo "\$ ./configure --enable-optimizations"
./configure --enable-optimizations
echo "\$ make altinstall"
make altinstall
echo ""
echo ""
py=$(echo $pyver | grep -Eo "[0-9]+\.[0-9]+" | head -n1)
python$py --version
