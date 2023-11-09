Python supplemental features
----------------------------

python-plus adds various features to python 2 and python 3 programs.
It is designed to be used as integration of pypi future to help to port your code from
Python 2 to Python 3 and still have it run on Python 2.


list_requirements.py: list environment requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is an internal command of python-plus but may be used as own command.
list_requirements.py displays the pypi and binaries packages needed to create a virtual
environment.
It is specially designed to show Odoo requirements.
Passing Odoo path it reads requirements.txt files in path and setup directories of OCA
repositories.

vem: virtual environment manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command is an interactive tool with some nice features to manage standard virtual
environment.
Mainly it works ad standard pip but inside a specific virtual environment.
