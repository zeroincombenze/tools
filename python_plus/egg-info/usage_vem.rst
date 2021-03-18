vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    Usage: vem [-h][-a list][-BDfkIn][-O ver][-o dir][-p pyver][-q][-r file][-sVv] p1 p2 p3 p4 p5 p6 p7 p8 p9
    Manage virtual environment
    action may be: help amend cp check create exec info install merge mv show update test reset
     -h              this help
     -a list         bin packages to install (* means wkhtmltopdf,lessc)
     -B              debug mode: use local packages
     -D              create v.environment with development packages
     -f              force v.environment create, even if exists
     -k              keep python2 executable
     -I              run pip in an isolated mode, ignoring environment variables and user configuration
     -n              do nothing (dry-run)
     -O ver          install pypi required by odoo ver (amend, create or reset)
     -o dir          odoo path:used to search odoo requirements and linked in venv
     -p pyver        python version
     -q              silent mode
     -r file         after created v.environment install from the given requirements file
     -s              create v.environment with access to the global site-packages
     -V              show version
     -v              verbose mode


vem is an interactive tool with some nice features to manage standard virtual environment.

Action is one of:

* help
* amend [OPTIONS] [SRC_VENV]
* check [OPTIONS] [SRC_VENV]
* cp [OPTIONS] SRC_VENV TGT_ENV
* create -p PYVER [OPTIONS] [VENV]
* exec [OPTIONS] [VENV] CMD
* info [OPTIONS] [VENV] PKG
* install [OPTIONS] [VENV] PKG
* merge [OPTIONS] SRC_VENV TGT_ENV
* mv [OPTIONS] SRC_VENV TGT_ENV
* upgrade [OPTIONS] [VENV] PKG
* uninstall [OPTIONS] [VENV] PKG
* test [OPTIONS] [VENV]
* reset [OPTIONS] [VENV]
* show [OPTIONS] [VENV] PKG

amend [OPTIONS] [SRC_VENV]
      Amend package versions against requirements.  May used after 'create' or 'reset' when requirements are changed.

check [OPTIONS] [SRC_VENV]
      Compare package versions against requirements.  May be used after 'create' or 'reset' to check virtual environment
      consistency.

cp [OPTIONS] SRC_VENV TGT_ENV
      Copy SOURCE environment directory to TGT_ENV, like the bash command 'cp' and  set  relative  path  inside  virtual
      environment to aim the new directory name.

create -p PYVER [OPTIONS] VENV
      Create  a  new  virtual environment directory VENV like virtualenv command but with some nice features.  Switch -p
      declare which python version will be used to create new environment.
      This action can install various python packages to create a ready to use environment directory.
      See -I -D -O -o -r switches to furthermore information.

exec [OPTIONS] [SRC_VENV] CMD ...
      Execute a command in virtual environment. Enclose command by quotes.

info [OPTIONS] [SRC_VENV] PKG
      Show information about pypi package if installed in virtual environment (alias of show)

install [OPTIONS] [SRC_VENV] PKG
      Install pypi package or bin package into virtual environment.
      Warning! currently just 2 bin packages can be installed: wkhtmltopdf and lessc

show [OPTIONS] [SRC_VENV] PKG
      Show information about pypi package if installed in virtual environment (alias of info)

uninstall [OPTIONS] [SRC_VENV] PKG
      Uninstall pypi package from virtual environment.

upgrade [OPTIONS] [SRC_VENV] PKG
      Upgrade pypi package in virtual environment.
