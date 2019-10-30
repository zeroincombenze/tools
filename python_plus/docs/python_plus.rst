Package python_plus
===================

Python supplemental features
----------------------------

python_plus adds various features to python 2 and python 3 programs.
It is designed to be used as follows:

    `>>> from python_plus import _u, _b, isbytestr`


Code examples
-------------

Test if a string is unicode.

On Py2, this gives us:

    `>>> s = u'Hello World'`
    `>>> isinstance(s, unicode)`
    `True`


On Py3, this gives us:

    `>>> s = 'Hello World'`
    `>>> isinstance(s, str)`
    `True`

Then, for example, the following code has the same effect on Py2 as on Py3:

    `>>> from python_plus import isbytestr`
    `>>> s = 'Hello World'`
    `>>> isbytestr(s)`
    `True`
