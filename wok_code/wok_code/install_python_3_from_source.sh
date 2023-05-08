#!/usr/bin/env bash
[[ ! $1 =~ ^(3.5|3.6|3.7|3.8|3.9) ]] && echo "$0 3.5|3.6|3.7|3.8|3.9" && exit 1
[[ $EUID -ne 0 ]] && echo "This code may be executed just by root user" && exit 1
[[ -z $(which wget 2>/dev/null) ]] && echo "Please install wget" && exit 1
pyver="$1"
[[ $1 == "3.9" ]] && pyver="$1.15"
[[ $1 == "3.8" ]] && pyver="$1.15"
[[ $1 == "3.7" ]] && pyver="$1.15"
[[ $1 == "3.6" ]] && pyver="$1.15"
[[ $1 == "3.5" ]] && pyver="$1.10"
echo ""
echo "Use $0 $1 APT WGET_OPTS CONFIG-OPTS"
echo "where:"
echo "  APT -> command to execute before build; examples:"
echo "      $0 $1 'apt install libssl-dev libffi-dev libncurses5-dev libsqlite3-dev ' \\"
echo "          'libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev libbz2-dev'"
echo "      $0 $1 'wget --no-check-certificate https://www.openssl.org/source/openssl-1.1.0e.tar.gz'"
echo "  WGET_OPTS -> options for wget; example $0 $1 '' --no-check-certificate"
echo "  CONFIG_OPTS -> options for ./configure; example $0 $1 '' ''  --with-openssl=DIR"
echo "      cd /tmp/Python-$pyver/.configure --help     # for details"
read -p "Press RET to continue ..."
APT="$2"
WGET_OPTS="$3"
CONFIG_OPTS="$4"
[[ -n "$APT" ]] && echo "\$ $APT" && $APT
echo "\$ cd /tmp"
cd /tmp
[[ -f Python-$pyver.tgz ]] && echo "File Python-$pyver.tgz already downloaded"
[[ ! -f Python-$pyver.tgz ]] && echo "\$ wget $WGET_OPTS https://www.python.org/ftp/python/$pyver/Python-$pyver.tgz"
[[ ! -f Python-$pyver.tgz ]] && wget $WGET_OPTS https://www.python.org/ftp/python/$pyver/Python-$pyver.tgz
[[ ! -f Python-$pyver.tgz ]] && echo "No file Python-$pyver.tgz downloaded!" && exit 2
[[ -d Python-$pyver ]] && rm -fR Python-$pyver
echo "\$ tar -xf Python-$pyver.tgz"
tar -xf Python-$pyver.tgz
[[ ! -d Python-$pyver ]] && echo "No directory Python-$pyver created!" && exit 2
echo "\$ cd Python-$pyver"
cd Python-$pyver
echo "\$ make clean   # It does not work for python 3.5"
make clean
echo "\$ ./configure --enable-optimizations $CONFIG_OPTS"
read -p "Press RET to configure and install ..."
./configure --enable-optimizations $CONFIG_OPTS
echo "\$ make altinstall"
make altinstall
echo ""
echo ""
py=$(echo $pyver | grep -Eo "[0-9]+\.[0-9]+" | head -n1)
python$py --version
python$py -m pip list
