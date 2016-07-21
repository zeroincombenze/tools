|build status|_
|coverage status|_
|license agpl|_

product
=======

Simple LAMP installer and manager

product is an interactive tool to install, update, remove, query and manage software for building a complete LAMP server.
LAMP means Linux Apache Mysql PHP; in recent times, Python and Postgresql were added.

product is just a front-end for yum and apt-get commands, it is not a real package installer.
It require yum on CentOS and Red Hat family distros, and apt-get on Ubuntu and debian family distros.
It is very useful to manage all the packages needed to build a complete LAMP server and to check the real server status.
For every main package, may be managed some dependent package; i.e. openssh-server manages openssh-client too.

All operations are logged in /var/log/product.log in order to trace operational flow.

You can easily write portable script to install packages on every Linux distribution.

You can find more info here:
http://wiki.zeroincombenze.org/en/Linux/dev


.. |build status| image:: https://travis-ci.org/antoniov/tools.svg
.. _build status: https://travis-ci.org/antoniov/tools
.. |coverage status| image:: https://coveralls.io/repos/antoniov/tools/badge.svg?branch=master&service=github
.. _coverage status: https://coveralls.io/github/antoniov/tools?branch=master
.. |license agpl| image:: https://img.shields.io/badge/licence-AGPL--3-green.svg
.. _license agpl: http://www.gnu.org/licenses/agpl-3.0.html

.. image::  http://www.shs-av.com/wp-content/chat_with_us.png
   :alt: Join the chat at http://www.zeroincombenze.it/supporto-software-gestionale/live-chat-assistenza-online/
   :target: http://www.zeroincombenze.it/supporto-software-gestionale/live-chat-assistenza-online/

.. image::  http://www.shs-av.com/wp-content/Assosoftware.gif
   :alt: Join the chat at http://www.assosoftware.it/
   :target: http://www.assosoftware.it/
