from setuptools import find_packages, setup

setup(
    name='python_plus',
    version='2.0.6',
    description='python useful function',
    long_description="""
Python supplemental features
----------------------------

python-plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code from Python 2 to Python 3 and still have it run on Python 2.


list_requirements.py: list environment requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is an internal command of python-plus but may be used as own command.
list_requirements.py displays the pypi and binaries packages needed to create a virtual environment.
It is specially designed to show Odoo requirements.
Passing Odoo path it reads requirements.txt files in path and setup directories of OCA repositories.

vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is an interactive tool with some nice features to manage standard virtual environment.
Mainly it works ad standard pip but inside a specific virtual environment.

vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    Usage: vem.sh [-h][-a list][-BCD][-d paths][-E distro][-f][-F name][-gkIi][-l iso][-n][-O version][-o dir][-p pyver][-q][-r file][-stVvy] p3 p4 p5 p6 p7 p8 p9
    Manage virtual environment
    action may be: help amend cp check create exec info inspect install merge mv python shell rm show uninstall update test
     -h --help            this help
     -a list              bin packages to install (* means wkhtmltopdf,lessc)
     -B                   use unstable packages: -B testpypi / -BB from ~/tools / -BBB from ~/pypi / -BBBB link to local ~/pypi
     -C                   clear cache before executing pip command
     -D --devel           create v.environment with development packages
     -d --dep-path paths
                          odoo dependencies paths (comma separated)
     -E --distro distro
                          simulate Linux distro: like Ubuntu20 Centos7 etc (requires -n switch)
     -f --force           force v.environment create, even if exists or inside another virtual env
     -F name              simulate Linux family: may be RHEL or Debian (requires -n switch)
     -g --global          install npm packages globally
     -k --keep            keep python2 executable as python (deprecated)
     -I --indipendent     run pip in an isolated mode and set home virtual directory
     -i --isolated        run pip in an isolated mode, ignoring environment variables and user configuration
     -l --lang iso
                          set default language
     -n --dry_run         do nothing (dry-run)
     -O --odoo-ver version
                          install pypi required by odoo version (amend or create)
     -o --odoo-path dir
                          odoo path used to search odoo requirements
     -p --python pyver
                          python version
     -q --quiet           silent mode
     -r --requirement file
                          after created v.environment install from the given requirements file
     -s --system-site-pack
                          create v.environment with access to the global site-packages
     -t --travis          activate environment for travis test
     -V --version         show version
     -v --verbose         verbose mode
     -y --yes             assume yes

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
* update [OPTIONS] [VENV] PKG
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
      Copying virtual environments is not well supported.
      Each virtualenv has path information hard-coded into it, and there may be cases where the copy code does not know it needs to update a particular file.
      Use with caution.

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

update [OPTIONS] [SRC_VENV] PKG
      Upgrade pypi package in virtual environment.

History
-------

2.0.4 (2022-12-15)
~~~~~~~~~~~~~~~~~~

* [IMP] Package version adjustment
* [IMP] vem: amend show current package version
* [IMP] vem: no python2 warning in linux kernel 3
* [FIX] vem: best recognition of python version
""",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: System Shells',
    ],
    keywords='unit test virtual environment venv',
    project_urls={
        'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
        'Source': 'https://github.com/zeroincombenze/tools',
    },
    url='https://zeroincombenze-tools.readthedocs.io',
    author='Antonio Maria Vigliotti',
    author_email='antoniomaria.vigliotti@gmail.com',
    license='Affero GPL',
    install_requires=['future', 'z0lib'],
    packages=find_packages(exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
    package_data={'': ['scripts/setup.info', 'scripts/vem.sh', './vem.man']},
    entry_points={
        'console_scripts': [
            'python-plus-info = python_plus.scripts.main:main',
            'vem = python_plus.scripts.vem:main',
            "list_requirements.py = python_plus.scripts.list_requirements:main",
        ]
    },
    zip_safe=False,
)
