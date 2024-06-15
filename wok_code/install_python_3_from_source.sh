#!/usr/bin/env bash

install_via_apt() {
# install_via_apt(PYVER)
    echo "\$ " apt update -y && apt upgrade -y && apt autoremove-y
    apt update -y && apt upgrade -y && apt autoremove-y
    echo "\$ " apt install software-properties-common
    apt install software-properties-common
    echo "\$ " add-apt-repository ppa:deadsnakes/ppa
    add-apt-repository ppa:deadsnakes/ppa
    echo "\$ " apt update -y && apt upgrade -y && apt autoremove-y
    apt update -y && apt upgrade -y && apt autoremove-y
    echo "\$ " apt install python$1
    apt install python$1
    echo ""
}

install_from_source() {
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
}

set_hashbang() {
# set_hashbang(file fqn_python)
    local p f
    f="$1"
    p="$2"
    grep -Eq "^#\!.*/bin.*python3.*$" $f &>/dev/null && echo "\$ " sed -E "\"s|^#\!.*/bin.*python3.*|#\!$p|\"" -i $f && sed -E "s|^#\!.*/bin.*python3.*|#\!$p|" -i $f && chmod +x $f
}

[[ ! $1 =~ ^(2.7|3.5|3.6|3.7|3.8|3.9|3.10|3.11) ]] && echo "$0 2.7|3.5|3.6|3.7|3.8|3.9|3.10|3.11" && exit 1
[[ $EUID -ne 0 ]] && echo "This code should be executed just by root user" && exit 1
[[ -z $(which wget 2>/dev/null) ]] && echo "Please install wget" && exit 1
DEFPYVER=$(python3 --version 2>&1 | grep "Python" | grep --color=never -Eo "3\.[0-9]+" | head -n1)
[[ $1 == $DEFPYVER ]] && echo "You try to install default python version" && exit 1
pyver="$1"
[[ $1 == "3.11" ]] && pyver="$1.6"
[[ $1 == "3.10" ]] && pyver="$1.13"
[[ $1 == "3.9" ]] && pyver="$1.18"
[[ $1 == "3.8" ]] && pyver="$1.18"
[[ $1 == "3.7" ]] && pyver="$1.17"
[[ $1 == "3.6" ]] && pyver="$1.15"
[[ $1 == "3.5" ]] && pyver="$1.10"
[[ $1 == "3.4" ]] && pyver="$1.10"
[[ $1 == "2.7" ]] && pyver="$1.18"
echo ""
echo "Use $0 $1 APT_XTL WGET_OPTS CONFIG-OPTS"
echo "where:"
echo "  APT_XTL -> command to execute before build; examples:"
echo "      $0 $1 'apt install libssl-dev libffi-dev libncurses5-dev libsqlite3-dev ' \\"
echo "          'libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev libbz2-dev'"
echo "      $0 $1 'wget --no-check-certificate https://www.openssl.org/source/openssl-1.1.0e.tar.gz'"
echo "  WGET_OPTS -> options for wget; example $0 $1 '' --no-check-certificate -4"
echo "  CONFIG_OPTS -> options for ./configure; example $0 $1 '' ''  --with-openssl=DIR"
echo "      cd /tmp/Python-$pyver/.configure --help     # for details"
read -p "Press RET to continue ..."
APT_XTL="$2"
WGET_OPTS="$3"
CONFIG_OPTS="$4"
[[ -n "$APT_XTL" ]] && echo "\$ $APT_XTL" && $APT_XTL
APT=$(which apt)
if [[ -x $APT ]]; then
    install_via_apt $1
else
    install_from_source $1
fi
PIP=$(which pip3)
if [[ -z $PIP ]]; then
    echo "\$ " apt install python3-pip
    apt install python3-pip
    echo "\$ " pip3 install pip -U
    pip3 install pip -U
fi
py=$(echo $pyver | grep -Eo "[0-9]+\.[0-9]+" | head -n1)
if [[ $py != $DEFPYVER ]]; then
    echo "\$ " apt install python$py-distutils
    apt install python$py-distutils
    echo "\$ " apt install python$py-setuptools
    apt install python$py-setuptools
    echo "\$ " apt install python$py-dev
    apt install python$py-dev
    echo "\$ " cd /tmp
    cd /tmp
    echo "\$ " wget $WGET_OPTS https://bootstrap.pypa.io/pip/$py/get-pip.py
    wget $WGET_OPTS https://bootstrap.pypa.io/pip/$py/get-pip.py
    if [[ ! -f get-pip.py ]]; then
        echo "Specific pip version not found! Try with generic pip"
        echo "\$ " wget $WGET_OPTS https:-pip//bootstrap.pypa.io/pip/get-pip.py
        wget $WGET_OPTS https://bootstrap.pypa.io/pip/get-pip.py
    fi
    if [[ ! -f get-pip.py ]]; then
        echo "Warning! pip no installed!"
    else
        echo "\$ " python$py get-pip.py
        python$py get-pip.py
        rm -f get-pip.py
        echo "\$ " python$py -m pip install pip
        python$py -m pip install pip
    fi
else
    echo "\$ " python$py -m pip install pip -U
    python$py -m pip install pip -U
fi
python$py -m pip list
PIP=$(which pip$py)
if [[ -z $PIP ]]; then
    echo "Warning: pip$py non installed"
    echo "You should use python$py -m pip"
    if [[ -f /usr/bin/pip3 ]]; then
        echo "\$ " cp /usr/bin/pip3 /usr/local/bin/pip$py
        cp /usr/bin/pip3 /tmp/pip$py
        set_hashbang "/tmp/pip$py" $(which python$py)
        /tmp/pip3.7 --version | grep -q "$py" | echo "$ " mv /tmp/pip$py /usr/local/bin/pip$py && mv /tmp/pip$py /usr/local/bin/pip$py
    fi
fi
echo ""
echo ""
python$py --version
echo ""
echo ""
pip$py --version
echo ""
