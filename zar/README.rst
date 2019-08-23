
==========
zar 0.3.31
==========



|Maturity| |Build Status| |Coverage Status| |license gpl|


.. contents::


Overview / Panoramica
=====================

|en| zar
========

Zeroincombenze® Archive Replica
-------------------------------

ZAR stand for Zeroincombenze® Archive Replica.
It is a tool kit to backup, restore, replicate files and/or database.

ZAR manages easily backup for Odoo database, keeps last nth copies and purges oldest copies.


|

|it| 

|

Features / Caratteristiche
--------------------------

* backup and restore odoo database
* backup and restore based on rules by configuration file
* restore database with automatic actions disabled
* multiple copies of database by configuration file
* automatic purging of oldest copies
* configuration based on host name: it works on duplicate host image too
* backup on same host or on remote host


|

Usage / Utilizzo
----------------

zar should be execute by postgres user

Execute zar_upd to install and configure.
Configuration file is zar.conf
Execute zar_bck to do backup or restore, based on host role
Execute zar_rest to do restore

To execute in cron, use zar_bck -k


There are avaiable two postgresql facilities:

* pg_db_active
* pg_db_reassign owner

`pg_db_active` show and kill postgres session. It can kill oldest session out of pool.

`pg_db_reassign_owner` can reassign owner to database. It reassign the ownership of all objects.
