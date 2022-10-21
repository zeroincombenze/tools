Operating System indipendent interface
--------------------------------------

This module is deprecated. It was born to extend python os module.

It recognizes file name structure and manages both URI standard name
both local name, as UNC and ODS5.

- URI (Uniform Resource Identifier) is standard posix filename.
- UNC (Uniform Naming Convention) is windows standard
- ODS5 is used for define OpenVMS standard filenames

An example of URI filename is '/home/myfile'.

UNC example for the same of previous URI name is '\\home\\myfile'
(with single backslash).

ODS5 (OpenVMS) for the same of previous URI name is '[home]myfile'

See https://en.wikipedia.org/wiki/Path_(computing)

Migration path
~~~~~~~~~~~~~~

* isunicode -> python_plus.isunicode
* isbytestr -> python_plus.isbytestr
* b -> python_plus._b
* u -> python_plus._u
* nakedname -> z0lib.nakedname
* muteshell -> z0lib.run_traced

No yet migration path
~~~~~~~~~~~~~~~~~~~~~

* str2bool
