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
