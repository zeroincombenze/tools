lisa
----

*lisa* stands for Linux Install Simplifier App

*lisa* is an interactive tool to install, update, remove, query and manage software for building a complete LAMP server.
LAMP means Linux Apache Mysql PHP; in recent times, Python and Postgresql were added.

*lisa* is just a front-end for yum and apt-get commands, it is not a real package installer.
It require yum on CentOS and Red Hat family distros, and apt-get on Ubuntu and debian family distros.
It is very useful to manage all the packages needed to build a complete LAMP server and to check the real server status.
For every main package, may be managed some dependent package; i.e. openssh-server manages openssh-client too.

You can easily write portable script to install packages on every Linux distribution.
