Module os0
==========

Operating System indipendent interface
--------------------------------------


Operating System indipendent interface
--------------------------------------

This module provides a portable way of using operating system dependent functionality.
It expands standard os module naming using both URI standard name both local name, as UNC and ODS5.

* URI (Uniform Resource Identifier) is standard posix filename.
* UNC (Uniform Naming Convention) is windows standard
* ODS5 is used for define OpenVMS standard filenames

An example of URI filename is '/home/myfile'.

UNC example for the same of previous URI name is '\\home\\myfile' (with single backslash)

ODS5 (OpenVMS) for the same of previous URI name is '[home]myfile'

See https://en.wikipedia.org/wiki/Path_(computing)

To use module os0 import it
    >>> from os0 import os0

First method is set local filename of URI file.
Set local filename of URI name is the same URI name
    >>> os0.setlfilename('myFile')
    'myFile'

Set local filename has optional parameter. FLAT means generic file name
    >>> os0.setlfilename('myFile', os0.LFN_FLAT)
    'myFile'

<!-- <platform linux2> -->
Executable file in Windows or OpenVMS have .EXE extension.
Conversion of URI name must add .EXE suffix, while URI is unchanged.
    >>> os0.setlfilename('myFile', os0.LFN_EXE)
    'myFile'

<!-- <platform win32> -->
Executable file in Windows has .EXE extension.
Conversion of URI name must add .EXE suffix.
    >>> os0.setlfilename('myFile', os0.LFN_EXE)
    'myFile.exe'

<!-- <platform OpenVMS> -->
Executable file in OpenVMS has .EXE extension.
Conversion of URI name must add .EXE suffix.
    >>> os0.setlfilename('myFile', os0.LFN_EXE)
    'myFile.exe'

<!-- <platform linux2> -->
Command file in Windows has .BAT suffix while in OpenVMS haS .COM extension.
Conversion of URI name must add these suffix, while URI is unchanged.
    >>> os0.setlfilename('myFile', os0.LFN_CMD)
    'myFile'

<!-- <platform win32> -->
Command file in Windows has .BAT extension.
Conversion of URI name must add .BAT suffix.
    >>> os0.setlfilename('myFile', os0.LFN_CMD)
    'myFile.bat'

<!-- <platform OpenVMS> -->
Command file in OpenVMS has .COM extension.
Conversion of URI name must add .COM suffix.
    >>> os0.setlfilename('myFile', os0.LFN_CMD)
    'myFile.com'

<!-- <platform *> -->
