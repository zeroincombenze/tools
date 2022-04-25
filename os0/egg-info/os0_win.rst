Module os0
==========

Operating System indipendent interface
--------------------------------------

This module provides a portable way of using operating system dependent functionality.
It expands standard os module naming using both URI and local filename.
URI (Uniform Resource Identifier) is standard posix filename.
An example of URI filename is '/home/myfile'.
URI may be used in windows and OpenVMS but these OS have an own filesystem.
Windows filename of previous URI example is '\\home\\myfile' (with single backslash)
OpenVMS filename of previous URI example is '[home]myfile'
This module provides function to manage local filename, URI filename
and conversions between both of them. 

To use module os0 import it
    >>> from os0 import os0

First method is set local filename of URI file.
Set local filename of URI name is the same URI name
    >>> os0.setlfilename('myFile')
    'myFile'

Set local filename has optional parameter. FLAT means generic file name
    >>> os0.setlfilename('myFile', os0.LFN_FLAT)
    'myFile'


Executable file in Windows has .EXE extension.
Conversion of URI name must add .EXE suffix.
    >>> os0.setlfilename('myFile', os0.LFN_EXE)
    'myFile.exe'


Command file in Windows has .BAT extension.
Conversion of URI name must add .BAT suffix.
    >>> os0.setlfilename('myFile', os0.LFN_CMD)
    'myFile.bat'


