Package os0
===========

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



See also
--------

http://www.zeroincombenze.org/
