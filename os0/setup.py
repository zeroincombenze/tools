from setuptools import setup

setup(name='os0',
      version='0.2.14.3',
      description='OS indipendent interface',
      long_description="""
OS interface for Linux, OpenVMS and Windows

This module expands standard os.py module.
os0 is platform independent and can run on Linux, OpenVMS and Linux.
os0 is the only package that intefaces OpenVMS and can execute OpenVMS command.

Features:
- Conversion any string type to unicode or utf-8 (avoid python2/3 conflict)
- Manage both URI both local filenames

URI filename conversion rules by os0.setlfilename
|Case              |Linux             |Windows          |OpenVMS              |
|------------------|------------------|-----------------|---------------------|
|Simple file       |myfile.ext        |myfile.ext       |myfile.ext           |
|Abs pathname      |/root/myfile.ext  |\\root\\myfile.ext |[root]myfile.ext   |
|Rel pathname      |lib/myfile.ext    |lib\\myfile.ext   |[.lib]myfile.ext    |
|CWD pathname      |./myfile.ext      |.\\myfile.ext     |[]myfile.ext        |
|Updir pathname    |../myfile.ext     |..\\myfile.ext    |[-]myfile.ext       |
|Root file         |/myfile.ext       |\\myfile.ext      |[000000]myfile.ext  |
|dotted pathname   |/u/os.1.0/a.b.c  |\\u\\os.1.0/a.b.c |[u.os^.1^.0]a^.^.b.c |
|hidden/leading dot |.myfile          |.myfile          |.myfile ??           |
|                  |                  |                 |                     |
|executable        |myfile            |myfile.exe       |myfile.exe           |
|command file      |myfile            |myfile.bat       |myfile.com           |
|directory         |mydir/            |mydir            |mydir.DIR            |
|                  |                  |                 |                     |
|dev null          |/dev/null         |nul              |NL0:                 |
|dev/disk/myfile   |/dev/disk/myfile  |c:\\myfile       |disk:[000000]myfile  |
|system disk       |/c/temp/myfile    |c:\\temp\\myfile |c:[temp]myfile       |

Notes:
-# URL with username (user@) is not supported by this version
-# URL with port number or service (http:) is not supported by this version
-# URL with server domain (//server) is not supported by this version
-# URL with character encoding (%20) is not supported by this version
-# Linux has not disk device in pathname; in order to manager Windows and
  OpenVMS devices here is used /dev/disk where disk may be a letter in Windows
  or a name in OpenVMS.
  Both Windows and OpenVMS use colon (:) at the end of disk device in local
  pathname (see last but one example above)
-# Here is also implemented a brief form for disk device, if exist on hosting
  machine
  Brief form is /dev/pathname like /c/windows/ or /sys$sysdevice/sys0/
  This brief form may be not universal translatable (see last example above)
-# Updir (..) may be recursive -> ../../myfile -> ..\\..\\myfile -> [-.-]myfile
-# Home dir (~/myfile) is no supported by this version
-# OpenVMS logical names use dollar sign, such as sys$sysdevice;
  in Linux dollar start a macro.
  Need to verify about some trouble
-# OpenVMS files have version; syntax is 'myfile.exe;ver' where ';ver'
   can be omitted
   No any other OS has this feature, so in version of module there is no
   support for filename version
""",
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.6',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Operating System :: OS Independent',
      ],
      keywords='os path linux windows openvms',
      url='http://wiki.zeroincombenze.org/en/Python/opt/os0',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero: GPL',
      packages=['os0'],
      zip_safe=False)
