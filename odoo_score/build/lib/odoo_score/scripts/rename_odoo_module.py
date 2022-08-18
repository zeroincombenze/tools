# template 18
"""
Renames Odoo module
"""
import sys
import os
import argparse

try:
    from clodoo import clodoo
except ImportError:
    import clodoo

__version__ = '2.0.0'


def update_module_names(ctx, namespec, merge_modules=False):
    """Deal with changed module names, making all the needed changes on the
    related tables, like XML-IDs, translations, and so on.

    :param namespec: list of tuples of (old name, new name)
    :param merge_modules: Specify if the operation should be a merge instead
        of just a renaming.
    """
    odoo_majver = 10.0
    for (old_name, new_name) in namespec:
        query = "SELECT id FROM ir_module_module WHERE name = %s"
        ctx['_cr'].execute(query, [new_name])
        row = ctx['_cr'].fetchone()
        if row and merge_modules:
            # Delete meta entries, that will avoid the entry removal
            # They will be recreated by the new module anyhow.
            query = "SELECT id FROM ir_module_module WHERE name = %s"
            ctx['_cr'].execute(query, [old_name])
            row = ctx['_cr'].fetchone()
            if row:
                old_id = row[0]
                query = "DELETE FROM ir_model_constraint WHERE module = %s"
                ctx['_cr'].execute(query, [old_id])
                query = "DELETE FROM ir_model_relation WHERE module = %s"
                ctx['_cr'].execute(query, [old_id])
        else:
            query = "UPDATE ir_module_module SET name = %s WHERE name = %s"
            ctx['_cr'].execute(query, (new_name, old_name))
            query = ("UPDATE ir_model_data SET name = %s "
                     "WHERE name = %s AND module = 'base' AND "
                     "model='ir.module.module' ")
            ctx['_cr'].execute(query,
                               ("module_%s" % new_name, "module_%s" % old_name))
        # The subselect allows to avoid duplicated XML-IDs
        query = ("UPDATE ir_model_data SET module = %s "
                 "WHERE module = %s AND name NOT IN "
                 "(SELECT name FROM ir_model_data WHERE module = %s)")
        ctx['_cr'].execute(query, (new_name, old_name, new_name))
        # Rename the remaining occurrences for let Odoo's update process
        # to auto-remove related resources
        query = ("UPDATE ir_model_data "
                 "SET name = name || '_openupgrade_' || id, "
                 "module = %s, noupdate = FALSE "
                 "WHERE module = %s")
        ctx['_cr'].execute(query, (new_name, old_name))
        query = ("UPDATE ir_module_module_dependency SET name = %s "
                 "WHERE name = %s")
        ctx['_cr'].execute(query, (new_name, old_name))
        if odoo_majver > 7:
            query = ("UPDATE ir_translation SET module = %s "
                     "WHERE module = %s")
            ctx['_cr'].execute(query, (new_name, old_name))
        if merge_modules:
            # Conserve old_name's state if new_name is uninstalled
            ctx['_cr'].executey(
                "UPDATE ir_module_module m1 "
                "SET state=m2.state, latest_version=m2.latest_version "
                "FROM ir_module_module m2 WHERE m1.name=%s AND "
                "m2.name=%s AND m1.state='uninstalled'",
                (new_name, old_name),
            )
            query = "DELETE FROM ir_module_module WHERE name = %s"
            ctx['_cr'].execute(query, [old_name])
            ctx['_cr'].execute(
                "DELETE FROM ir_model_data WHERE module = 'base' "
                "AND model='ir.module.module' AND name = %s",
                ('module_%s' % old_name,),
            )


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Rename Odoo module",
        epilog="© 2021-2022 by SHS-AV s.r.l."
    )
    parser.add_argument('-c', '--config')
    parser.add_argument('-d', '--database')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action="version", version=__version__)
    parser.add_argument('old')
    parser.add_argument('new')
    opt_args = parser.parse_args(cli_args)
    sts = 0
    if not opt_args.config:
        print('Missed configuration file: use -c CONFIG')
        sts = 1
    elif not os.path.isfile(opt_args.config):
        print('File %s not found!' % opt_args.config)
        sts = 1
    if not opt_args.database:
        print('Missed database name: use -d DATABASE')
        sts = 1
    if sts == 0:
        uid, ctx = clodoo.oerp_set_env(
            confn=opt_args.config,
            db=opt_args.database)
        update_module_names(ctx, [(opt_args.old, opt_args.new)])
    return sts


if __name__ == "__main__":
    exit(main())
