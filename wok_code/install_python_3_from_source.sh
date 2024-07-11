#!/usr/bin/env bash

xuname() {
  OS=$(uname -s)
  REV=$(uname -r)
  MACH=$(uname -m)
  KERNEL="$REV"
  VER=""
  DIST=""
  ARCH=$(uname -p)
  FAMILY=""
  XDES=""

  if [ "${OS}" = "SunOS" ]; then
    OS=Solaris
    ARCH=$(uname -p)
    VER=$(uname -v)
    OSSTR="${OS} ${REV}(${ARCH} $(uname -v))"
  elif [ "${OS}" = "AIX" ]; then
    OSSTR="${OS} $(oslevel) ($(oslevel -r))"
  elif [ "${OS}" = "Darwin" ]; then
    DIST=$OS
    FAMILY="osx"
    OSSTR="${OS} ${VER}(${CODENAME} ${KERNEL} ${MACH})"
  elif [ "${OS}" = "Linux" ]; then
    KERNEL=$(uname -r)
    CODENAME=""
    if [ -f /etc/vmware-release ]; then
      DIST='VMWare'
      CODENAME=$(cat /etc/vmware-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/vmware-release | sed s/.*release\ // | sed s/\ .*//)
    elif [ -f /etc/centos-release ]; then
      DIST='CentOS'
      XDES=$(cat /etc/centos-release|tr -d " \n")
      CODENAME=$(cat /etc/centos-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/centos-release | sed s/.*release\ // | sed s/\ .*//)
      FAMILY="RHEL"
    elif [ -f /etc/gentoo-release ]; then
      DIST='Gentoo'
      CODENAME=$(cat /etc/gentoo-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/gentoo-release | sed s/.*release\ // | sed s/\ .*//)
    elif [ -f /etc/SUSE-release ]; then
      DIST="SuSE"
      CODENAME=$(cat /etc/SUSE-release | tr "\n" ' '| sed s/VERSION.*//)
      VER=$(cat /etc/SUSE-release | tr "\n" ' ' | sed s/.*=\ //)
      FAMILY="RHEL"
    elif [ -f /etc/SuSE-release ]; then
      DIST="SuSE"
      CODENAME=$(cat /etc/SuSE-release | tr "\n" ' '| sed s/VERSION.*//)
      VER=$(cat /etc/SuSE-release | tr "\n" ' ' | sed s/.*=\ //)
      FAMILY="RHEL"
    elif [ -f /etc/mandriva-release ]; then
      DIST='Mandriva'
      CODENAME=$(cat /etc/mandriva-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/mandriva-release | sed s/.*release\ // | sed s/\ .*//)
      FAMILY="RHEL"
    elif [ -f /etc/mandrake-release ]; then
      DIST='Mandrake'
      CODENAME=$(cat /etc/mandrake-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/mandrake-release | sed s/.*release\ // | sed s/\ .*//)
    elif [ -f /etc/fedora-release ]; then
      DIST="Fedora"
      CODENAME=$(cat /etc/fedora-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/fedora-release | sed s/.*release\ // | sed s/\ .*//)
      FAMILY="RHEL"
    elif [ -f /etc/slackware-version ]; then
      DIST="Slackware"
      VER=""
    elif [ -f /etc/lsb-release -o -d /etc/lsb-release.d ]; then
      DIST=$(grep "DISTRIB_ID" /etc/lsb-release|awk -F"=" '{print $2}'|tr -d "\"', \n")
      if [ -z "$DIST" ]; then
        DIST="Ubuntu"
      fi
      VER=$(grep "DISTRIB_RELEASE" /etc/lsb-release|awk -F"=" '{print $2}'|tr -d "\"', \n")
      CODENAME=$(grep "DISTRIB_CODENAME" /etc/lsb-release|awk -F"=" '{print $2}'|tr -d "\"', \n")
      XDES=$(grep "DISTRIB_DESCRIPTION" /etc/lsb-release|awk -F"=" '{print $2}'|tr -d "\"', \n")
      FAMILY="Debian"
    elif [ -f /etc/debian_version ]; then
      DIST="Debian"
      ls_relase &>/dev/null
      [ $? -ne 127 ] && VER=$(lsb_release --release --short) || VER=$(cat /etc/debian_version)
      FAMILY="Debian"
    elif [ -f /etc/redhat-release ]; then
      DIST='RedHat'
      CODENAME=$(cat /etc/redhat-release | sed s/.*\(// | sed s/\)//)
      VER=$(cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//)
      FAMILY="RHEL"
    elif [ -f /etc/os-release ]; then
      DIST="Debian"
      ls_relase &>/dev/null
      [ $? -ne 127 ] && VER=$(lsb_release --release --short) || VER=$(cat /etc/os-release)
      FAMILY="Debian"
    fi
    if [ -f /etc/UnitedLinux-release ]; then
      DIST="${DIST}[$(cat /etc/UnitedLinux-release | tr "\n" ' ' | sed s/VERSION.*//)]"
    fi
    OSSTR="${OS} ${DIST} ${VER}(${CODENAME} ${KERNEL} ${MACH})"
  fi
  if [ "$1" == "-c" ]; then
    echo ${CODENAME}
  elif [ "$1" == "-d" ]; then
    echo ${DIST}
  elif [ "$1" == "-f" ]; then
    echo ${FAMILY}
  elif [ "$1" == "-k" ]; then
    echo ${KERNEL}
  elif [ "$1" == "-m" -o  "$1" == "-i" ]; then
    echo ${MACH}
  elif [ "$1" == "-p" ]; then
    echo ${ARCH}
  elif [ "$1" == "-s" ]; then
    echo ${OS}
  elif [ "$1" == "-r" ]; then
    echo ${REV}
  elif [ "$1" == "-v" ]; then
    echo ${VER}
  elif [ "$1" == "-x" ]; then
    echo ${XDES}
  else
    echo ${OSSTR}
  fi
}

install_via_apt() {
# install_via_apt(PYVER)
#    if [[ $DIST == "Debian" ]]; then
#        echo "\$ " apt install -y python3-launchpadlib
#        apt install -y python3-launchpadlib
#    fi
    echo "\$ " apt update -y && apt upgrade -y && apt autoremove -y
    apt update -y && apt upgrade -y && apt autoremove -y
    echo "\$ " apt install -y software-properties-common
    apt install -y software-properties-common
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y gnupg2
    apt install -y gnupg2
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y ca-certificates
    apt install -y ca-certificates
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " add-apt-repository -y ppa:deadsnakes/ppa
    add-apt-repository -y ppa:deadsnakes/ppa
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt update -y && apt upgrade -y && apt autoremove -y
    apt update -y && apt upgrade -y && apt autoremove -y
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-dev
    apt install -y python$1-dev
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-distutils
    apt install -y python$1-distutils
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-setuptools
    apt install -y python$1-setuptools
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-venv
    apt install -y python$1-venv
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-lib2to3
    apt install -y python$1-lib2to3
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-gdbm
    apt install -y python$1-gdbm
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1-tk
    apt install -y python$1-tk
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
    echo "\$ " apt install -y python$1
    apt install -y python$1
    [[ $? -ne 0 ]] && read -p  "Error installing above package. Press RET to continue ..."
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

clear
[[ ! $1 =~ ^(2.7|3.5|3.6|3.7|3.8|3.9|3.10|3.11) ]] && echo "$0 2.7|3.5|3.6|3.7|3.8|3.9|3.10|3.11" && exit 1
echo ""
DISTID=$(xuname -d)$(xuname -v|grep -Eo "[0-9]+"|head -n1)
echo "Install python $1 on $(xuname -a) (brief $DISTID)"
[[ $EUID -ne 0 ]] && echo "This code should be executed just by root user" && exit 1
[[ -z $(which wget 2>/dev/null) ]] && echo "Please install wget" && exit 1
DEFPYVER=$(python3 --version 2>&1 | grep "Python" | grep --color=never -Eo "3\.[0-9]+" | head -n1)
[[ $1 == $DEFPYVER ]] && echo "You are trying to install default python version" && exit 1
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

OSPKGS="(libssl-dev|libffi-dev|libncurses5-dev|libsqlite3-dev|libreadline-dev|libtk8.6|libgdm-dev|libdb4o-cil-dev|libpcap-dev|libbz2-dev)"
ADD_REPO=$(which add-apt-repository)
installed=$(apt list --installed 2>/dev/null|grep -E "$OSPKGS")
pkgs_list=${OSPKGS:1: -1}
pkgs_list=${pkgs_list//|/ }
APT_XTL=""
for p in $pkgs_list; do
    echo $installed | grep "$p" >/dev/null
    [[ $? -ne 0 ]] && APT_XTL="$APT_XTL $p"
done
if [[ -n $ADD_REPO ]]; then
  echo ""
  echo "Use $0 $1 'APT_XTL'    # Via add-apt-repository"
  echo ""
  echo "where:"
  echo "    APT_XTL -> command to execute before build"
  echo "example:"
  echo "    $0 $1 'apt install $APT_XTL'"
else
  echo ""
  echo "Use $0 $1 'APT_XTL' 'WGET_OPTS' 'CONFIG-OPTS'"
  echo ""
  echo "where:"
  echo "    APT_XTL -> command to execute before build"
  echo "    WGET_OPTS -> options for wget"
  echo "    CONFIG_OPTS -> options for ./configure"
  echo "example:"
  echo "    $0 $1 'apt install $APT_XTL' 'wget --no-check-certificate https://www.openssl.org/source/openssl-1.1.0e.tar.gz' '--with-openssl=DIR'    # Via source"
fi
echo ""
echo "OS Packages needed are:"
for p in $pkgs_list; do
    echo $installed | grep "$p" >/dev/null
    [[ $? -eq 0 ]] && echo "    Package $p installed [OK]" || echo "    Please install package $p!!! -> apt install $p"
done
echo "For wget options type:"
echo "    wget --help"
echo "For configure details:"
echo "    cd /tmp/Python-$pyver/.configure --help"
echo ""
read -p "Press RET to continue ..."
APT_XTL="$2"
WGET_OPTS="$3"
CONFIG_OPTS="$4"
[[ -n "$APT_XTL" ]] && echo "\$ $APT_XTL" && $APT_XTL
if [[ $DIST == "Ubuntu" && -n $ADD_REPO ]]; then
    install_via_apt $1
else
    install_from_source $1
fi
PIP=$(which pip3)
if [[ -z $PIP ]]; then
    echo "\$ " apt install -y python3-pip
    apt install -y python3-pip
    echo "\$ " pip3 install pip -U
    pip3 install pip -U
fi
py=$(echo $pyver | grep -Eo "[0-9]+\.[0-9]+" | head -n1)
if [[ $py != $DEFPYVER ]]; then
    echo "\$ " apt install .y python$py-distutils
    apt install -y python$py-distutils
    echo "\$ " apt install -y python$py-setuptools
    apt install -y python$py-setuptools
    echo "\$ " apt install -y python$py-dev
    apt install -y python$py-dev
    echo "\$ " apt install -y python$1-venv
    apt install -y python$1-venv
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
PIP=$(which pip$py)
[[ -n $PIP ]] && echo "\$ " pip$py install virtualenv && pip$py install virtualenv
echo ""
echo ""
python$py --version
echo ""
echo ""
pip$py --version
echo ""
