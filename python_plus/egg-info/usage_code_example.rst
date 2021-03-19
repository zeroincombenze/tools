Code example
------------

class / type test
~~~~~~~~~~~~~~~~~

Test if a string is unicode.

On Py2, this gives us:

    >>> s = 'Hello World'
    >>> isinstance(object, str)
    True

On Py3, this gives us:

    >>> s = b'Hello World'
    >>> isinstance(object, bytes)
    True


Then, for example, the following code has the same effect on Py2 as on Py3:

    >>> from python_plus import isbytestr
    >>> s = b'Hello World'
    >>> isbytestr(s)
    True


quoted string
~~~~~~~~~~~~~

Using class __:

    >>> from python_plus import __

    >>> my_str_list = __('abc,"d,e",fgh')
    >>> my_list = my_str_list.qsplit(my_str_list)
    >>> print my_list
    ['abc', 'd,e', 'fgh']

|

General function:

    >>> from python_plus import qsplit

    >>> my_str_list = 'abc,"d,e",fgh'
    >>> my_list = qsplit(my_str_list)
    >>> print my_list
    ['abc', 'd,e', 'fgh']

