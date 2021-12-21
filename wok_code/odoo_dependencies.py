#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Return module list or dependencies list or depends list of odoo modules.

usage: odoo_dependencies.py [-h] [-A {dep,help,jrq,mod,rev,tree}] [-a]
                            [-b version] [-B DEPENDS_BY] [-c file] [-D file]
                            [-E] [-e] [-H] [-M MODULES_TO_MATCH]
                            [-N] [-n] [-o] [-P] [-q] [-R] [-S SEP_LIST]
                            [-V] [-v] [-x] [-1]
                            [path_list [path_list ...]]

Odoo dependencies

positional arguments:
  path_list

optional arguments:
  -h, --help            show this help message and exit
  -A {dep,help,jrq,mod,rev,tree}, --action {dep,help,jrq,mod,rev,tree}
  -a, --and-list
  -b version, --branch version
                        Odoo branch
  -B DEPENDS_BY, --depends-by DEPENDS_BY
  -c file, --config file
                        configuration command file
  -D file, --dbname file
                        DB name
  -E, --only-missed
  -e, --external-dependencies
  -H, --action-help
  -M MODULES_TO_MATCH, --modules-to-match MODULES_TO_MATCH
  -N, --only-count
  -n, --dry-run         do nothing (dry-run)
  -o, --or-list
  -P, --pure-list
  -q, --quiet           silent mode
  -R, --recurse
  -S SEP_LIST, --sep-list SEP_LIST
  -V, --version         show program's version number and exit
  -v, --verbose         verbose mode
  -x, --external-bin-dependencies
  -1, --no-depth

© 2020-21 by SHS-AV s.r.l.


This app can execute following actions:
  mod: print module list of paths
  dep: print dependencies list of modules 
  rev: print dependents list of module in paths
  jrq: print just strict dependents list of module in paths
  tree: print modules tree

Action 'mod' returns module list from path_list (comma separated). 
With -R switch, the search traverses directories.
With -M switch, list matches only modules in MODULES_TO_MATCH.
With -E switch, list matches only modules in MODULES_TO_MATCH
                not found in path_list.
See below for -D and -c switches.
With -B switch returns modules list which have one or more dependencies
in DEPENDS_BY. In conjunction with -a switch return module which have all
dependencies in DEPENDS_BY.

Action 'dep' returns children dependencies list from MODULES_TO_MATCH;
MODULES_TO_MATCH is get from -M switch or else they are get from path_list.
With -R switch, the search traverses directories.
Returned modules in list depend from one or more MODULES_TO_MATCH.
This is the default behavior or using -o switch.
Modules in list may depend from all MODULES_TO_MATCH with -a switch (and).
MODULES_TO_MATCH are includes in dependencies list.
If you want to avoid this inclusion, use -P switch (pure).
You can also limit list to modules supplied by -B switch.

Action 'rev' return ancestor modules by list of modules to match
supplied by -B switch or module base.
With -1 switch, it does not traverses parent tree.

Action 'jrq' is like 'rev' but returns strictly list of common ancestors.

Action 'tree' print modules tree. With -E switch print only missed modules.

SPECIAL FEATURES

Switch -N returns, for all actions, the reckoning of modules.

Switch -D replaces value of MODULES_TO_MATCH with installed module in DB;
so, with -A mod, -D and -E switches and without -M switch, return installed modules
list in DB without python code. List contains module with state 'to*' too.

With -D switch you have to supply configuration files; one of them is ordinary
odoo configuration file; you must add another configuration file with:
login_user, login_password parameters to connect to DB.
"""
from __future__ import print_function, unicode_literals

import sys
import os
import ast
from six import string_types
# try:
#     from os0 import os0
# except ImportError:
#     import os0
try:
    from z0lib.z0lib import z0lib
except ImportError:
    from z0lib import z0lib
try:
    from clodoo import clodoo
except ImportError:
    import clodoo

__version__ = '1.0.4'


MANIFEST_FILES = [
    '__manifest__.py',
    '__odoo__.py',
    '__openerp__.py',
    '__terp__.py',
]
MAX_DEEP = 20
UNDEF_DEEP = MAX_DEEP + 5
MISSED = 99

def get_test_dependencies(addons_path, addons_list, depends_by=None,
                          ao_list=None, external_dependencies=None,
                          external_bin_dependencies=None):
    """
    Get the list of core and external modules dependencies
    for the modules to test.
    :param addons_path: string with a comma separated list of addons paths
    :param addons_list: list of the modules to test
    """
    depends_by = depends_by or []
    ao_list = ao_list or '|'
    if not addons_list:
        return ['base']
    modules = {}
    for path in addons_path.split(','):
        modules.update(get_modules_info(path))
    dependencies = set()
    if ao_list == '|':
        for module in addons_list:
            deps = get_dependencies(
                modules, module,
                external_dependencies=external_dependencies,
                external_bin_dependencies=external_bin_dependencies)
            if depends_by:
                deps &= set(depends_by)
            dependencies |= deps
    elif ao_list == '&':
        dependencies = get_dependencies(
            modules, addons_list[0],
            external_dependencies=external_dependencies,
            external_bin_dependencies=external_bin_dependencies)
        for module in addons_list[1:]:
            deps = get_dependents(modules, module)
            if depends_by:
                deps &= set(depends_by)
            dependencies &= set(deps)
            if not dependencies:
                break
    return list(dependencies - set(addons_list))


def get_dependencies(modules, module_name, depth=None,
                     external_dependencies=None,
                     external_bin_dependencies=None):
    """Return a set of all the dependencies in deep of the module_name.
    The module_name is included in the result."""
    depth = depth or 999
    result = set()
    if external_bin_dependencies:
        for dependency in modules.get(module_name, {}).get(
                'external_dependencies', {}).get('bin', []):
            result |= set([dependency])
        return result
    elif external_dependencies:
        for dependency in modules.get(module_name, {}).get(
                'external_dependencies', {}).get('python', []):
            result |= set([dependency])
        return result
    else:
        for dependency in modules.get(module_name, {}).get('depends', []):
            if depth > 1:
                result |= get_dependencies(
                    modules, dependency, depth=depth-1,
                    external_dependencies=external_dependencies,
                    external_bin_dependencies=external_bin_dependencies)
            else:
                result |= set([dependency])
        return result | set([module_name])


def get_dependents(modules, module_name, depth=None):
    """Return a set of all the modules that are dependent of the module_name.
    The module_name is included in the result."""
    depth = depth or 999
    result = set()
    for dependent in modules.keys():
        if module_name in modules.get(dependent, {}).get('depends', []):
            if depth <= 1:
                result |= set([dependent])
            else:
                result |= get_dependents(modules, dependent, depth=depth-1)
    return result | set([module_name])


def get_dep_of_module(addons_path, addons_list,
                      external_dependencies=None,
                      external_bin_dependencies=None):
    if not addons_list:
        return ['base']
    else:
        modules = {}
        for path in addons_path.split(','):
            modules.update(get_modules_info(path))
        dependencies = set()
        for module in addons_list:
            dependencies |= get_dependencies(
                modules, module,
                external_dependencies=external_dependencies,
                external_bin_dependencies=external_bin_dependencies)
        return list(dependencies - set(addons_list))


def is_module(path):
    """return False if the path doesn't contain an odoo module, and the full
    path to the module manifest otherwise"""

    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        return False
    files = os.listdir(path)
    filtered = [x for x in files if x in (MANIFEST_FILES + ['__init__.py'])]
    if len(filtered) == 2 and '__init__.py' in filtered:
        return os.path.join(
            path, next(x for x in filtered if x != '__init__.py'))
    else:
        return False


def read_manifest(manifest_path):
    try:
        manifest = ast.literal_eval(open(manifest_path).read())
    except (IOError, ImportError):
        raise Exception('Wrong manifest file %s' % manifest_path)
    return manifest


def read_valid_manifest(manifest_path, depends_by=None, ao_list=None):
    ao_list = ao_list or '|'
    manifest = read_manifest(manifest_path)
    if not manifest.get('installable', True):
        return False
    if depends_by:
        deps = manifest.get('depends', [])
        if ((ao_list == '|' and not list(set(depends_by) & set(deps))) or
            (ao_list == '&' and list(set(depends_by) - set(deps))) or
            (ao_list == '=' and list(set(depends_by) - set(deps)) and
             list(set(depends_by) - set(deps)))
        ):
            return False
    return manifest


def get_modules_info(path, depth=1, depends_by=None, ao_list=None):
    """ Return a digest of each installable module's manifest in path repo"""
    path = os.path.expanduser(path)
    # Avoid empty basename when path ends with slash
    path = os.path.dirname(path) if not os.path.basename(path) else path
    modules = {}
    if os.path.isdir(path) and depth > 0:
        for module in sorted(os.listdir(path)):
            module_path = os.path.join(path, module)
            manifest_path = is_module(module_path)
            if manifest_path:
                manifest = read_valid_manifest(manifest_path,
                                               depends_by=depends_by,
                                               ao_list=ao_list)
                if manifest:
                    modules[module] = {
                        'application': manifest.get('application', False),
                        'depends': manifest.get('depends', []),
                        'external_dependencies': manifest.get(
                            'external_dependencies', {}),
                        'auto_install': manifest.get('auto_install', False),
                    }
            # ignore module whom name starts by '_'
            elif (not module.startswith('_') and
                    os.path.isdir(module_path)):
                deeper_modules = get_modules_info(
                    os.path.join(path, module),
                    depth=depth-1,
                    depends_by=depends_by,
                    ao_list=ao_list)
                modules.update(deeper_modules)
    return modules


def is_addons(path):
    res = get_modules(path) != []
    return res


def get_addons(path, depth=1):
    """Return repositories in path. Can search in inner folders as depth."""
    path = os.path.expanduser(path)
    if not os.path.exists(path) or depth < 0:
        return []
    res = []
    if is_addons(path):
        res.append(path)
    else:
        new_paths = [os.path.join(path, x)
                     for x in sorted(os.listdir(path))
                     if os.path.isdir(os.path.join(path, x))]
        for new_path in new_paths:
            res.extend(get_addons(new_path, depth-1))
    return res


def add_auto_install(modules, to_install):
    """ Append automatically installed glue modules to to_install if their
    dependencies are already present. to_install is a set. """
    found = True
    while found:
        found = False
        for module, module_data in modules.items():
            if (module_data.get('auto_install') and
                    module not in to_install and
                    all(dependency in to_install
                        for dependency in module_data.get('depends', []))):
                found = True
                to_install.add(module)
    return to_install


def get_applications_with_dependencies(modules,
                                       external_dependencies=None,
                                       external_bin_dependencies=None):
    """ Return all modules marked as application with their dependencies.
    For our purposes, l10n modules cannot be an application. """
    result = set()
    for module, module_data in modules.items():
        if module_data.get('application') and not module.startswith('l10n_'):
            result |= get_dependencies(
                modules, module,
                external_dependencies=external_dependencies,
                external_bin_dependencies=external_bin_dependencies)
    return add_auto_install(modules, result)


def get_localizations_with_dependents(modules):
    """ Return all localization modules with the modules that depend on them
    """
    result = set()
    for module in modules.keys():
        if module.startswith('l10n_'):
            result |= get_dependents(modules, module)
    return result


def get_modules(path, depth=1, depends_by=None, ao_list=None):
    """ Return modules of path repo (used in test_server.py)"""
    return sorted(list(get_modules_info(path,
                                        depth=depth,
                                        depends_by=depends_by,
                                        ao_list=ao_list).keys()))


def build_module_tree(path_list, matches=None, depth=None, only_missed=None):

    def init_module(level=None):
        return {
            'application': None,
            'depends': [],
            'external_dependencies': {},
            'auto_install': False,
            'level': level or MISSED,
            'status': '',
            'dependents': [],
            'missed_dependents': [],
            'visited': False,
            'missed_depends': [],
            'recurse': False,
        }

    def walk_module_tree(module):
        all_modules[module]['visited'] = True
        module_level = all_modules[module]['level']
        for subm in all_modules[module]['depends']:
            if subm not in all_modules.keys():
                all_modules[subm] = init_module()
                module_level = UNDEF_DEEP
            all_modules[subm]['dependents'].append(module)
            if all_modules[subm]['level'] == MISSED:
                if module in all_modules[subm]['missed_dependents']:
                    all_modules[subm]['recurse'] = True
                else:
                    all_modules[subm]['missed_dependents'].append(module)
                if subm in all_modules[module]['missed_depends']:
                    all_modules[module]['recurse'] = True
                else:
                    all_modules[module]['missed_depends'].append(subm)
            if not all_modules[subm]['visited']:
                walk_module_tree(subm)
            if all_modules[subm]['level'] != MISSED:
                module_level = max(module_level,
                                   all_modules[subm]['level'] + 1)
        all_modules[module]['level'] = module_level

    depth = depth or 999
    all_modules = {}
    for path in path_list:
        all_modules.update(get_modules_info(path, depth=depth))
    modules_2_match = matches or get_modules_list(path_list, depth=depth)
    visit_list = sorted(
        list(set(all_modules.keys()) | set(modules_2_match)))

    for module in visit_list:
        if module not in all_modules.keys():
            # Searched module not found
            all_modules[module] = init_module()
        else:
            all_modules[module]['dependents'] = []
            all_modules[module]['missed_dependents'] = []
            all_modules[module]['missed_depends'] = []
            all_modules[module]['visited'] = False
            all_modules[module]['level'] = 0
            all_modules[module]['recurse'] = False
    if 'base' in all_modules:
        walk_module_tree('base')
    else:
        walk_module_tree(all_modules.keys()[0])
    while True:
        found = False
        for module in all_modules.keys():
            if (all_modules[module]['level'] == 0 and
                    not all_modules[module]['visited']):
                walk_module_tree(module)
                found = True
                break
        if not found:
            break
    for module in all_modules.keys():
        status = 'Ok'
        if all_modules[module]['recurse']:
            status = 'Recursive chain'
            all_modules[module]['level'] = UNDEF_DEEP + MAX_DEEP
        elif all_modules[module]['missed_depends']:
            missed = ','.join(all_modules[module]['missed_depends'])
            status = 'Not installable, missed %s' % missed
        elif all_modules[module]['missed_dependents']:
            missed = ','.join(all_modules[module]['missed_dependents'])
            status = 'Missed dependency of %s' % missed
        elif all_modules[module]['level'] == 0:
            status = 'Root module'
        elif all_modules[module]['level'] >= UNDEF_DEEP:
            status = 'Recursive chain'
        all_modules[module]['status'] = status

    return False, all_modules


def get_modules_list(path_list, depth=None, matches=None, depends_by=None,
                     ao_list=None, only_missed=None, modules_unstable=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 1
    matches = matches or []
    modules_unstable = modules_unstable or []
    res = []
    for path in paths:
        repo = get_modules(os.path.expanduser(path),
                           depth=depth,
                           depends_by=depends_by,
                           ao_list=ao_list)
        for module in repo:
            if module not in res:
                res.append(module)
    if matches:
        if only_missed:
            res = list((set(matches) - set(res)) | set(modules_unstable))
        else:
            res = list(set(res) & set(matches))
    return sorted(res)


def get_dependencies_list(path_list, matches=None, depth=None,
                          depends_by=None, ao_list=None, pure_list=None,
                          external_dependencies=None,
                          external_bin_dependencies=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 999
    depends_by = depends_by or []
    ao_list = ao_list or '|'
    pure_list = pure_list or False
    module_list = matches or get_modules_list(path_list, depth=depth)
    modules = {}
    for path in paths:
        modules.update(get_modules_info(path, depth=depth))
    dependencies = set()
    if ao_list == '|':
        for module in module_list:
            deps = get_dependencies(
                modules, module, depth=depth,
                external_dependencies=external_dependencies,
                external_bin_dependencies=external_bin_dependencies)
            if depends_by:
                deps &= set(depends_by)
            dependencies |= deps
    elif ao_list == '&':
        dependencies = get_dependencies(
            modules, module_list[0], depth=depth,
            external_dependencies=external_dependencies,
            external_bin_dependencies=external_bin_dependencies)
        for module in module_list[1:]:
            deps = get_dependencies(
                modules, module, depth=depth,
                external_dependencies=external_dependencies,
                external_bin_dependencies=external_bin_dependencies)
            if depends_by:
                deps &= set(depends_by)
            dependencies &= set(deps)
            if not dependencies:
                break
    if pure_list:
        dependencies -= set(module_list)
    return sorted(list(dependencies))


def get_dependents_list(path_list, matches=None, depth=None,
                        depends_by=None, ao_list=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 1
    depends_by = depends_by or ['base']
    ao_list = ao_list or '|'
    # module_list = matches or get_modules_list(path_list, depth=depth)
    modules = {}
    for path in paths:
        modules.update(get_modules_info(path, depth=depth))
    depends = set()
    if ao_list == '|':
        for module in depends_by:
            deps = get_dependents(modules, module, depth=depth)
            if matches:
                deps &= set(matches)
            depends |= deps
    elif ao_list == '&':
        depends = get_dependents(modules, depends_by[0], depth=depth)
        for module in depends_by[1:]:
            deps = get_dependents(modules, module, depth=depth)
            if matches:
                deps &= set(matches)
            depends &= deps
            if not depends:
                break
    return sorted(list(depends))


def get_just_dependents_list(path_list, matches=None, depth=None,
                             depends_by=None, ao_list=None,
                             external_dependencies=None,
                             external_bin_dependencies=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 1
    depends_by = depends_by or ['base']
    ao_list = ao_list or '|'
    # module_list = matches or get_modules_list(path_list, depth=depth)
    modules = {}
    for path in paths:
        modules.update(get_modules_info(path, depth=depth))
    depends = set()
    set_depends_by = set(depends_by)
    if ao_list == '|':
        for module in depends_by:
            deps = get_dependents(modules, module, depth=depth)
            if matches:
                deps &= set(matches)
            for m2 in deps:
                d2 = get_dependencies(
                    modules, m2, depth=depth,
                    external_dependencies=external_dependencies,
                    external_bin_dependencies=external_bin_dependencies)
                if d2 - set_depends_by == set([m2]):
                    depends |= set([m2])
    elif ao_list == '&':
        depends = get_dependents(modules, depends_by[0], depth=depth)
        for module in depends_by[1:]:
            deps = get_dependents(modules, module, depth=depth)
            if matches:
                deps &= set(matches)
            for m2 in deps:
                d2 = get_dependencies(
                    modules, m2, depth=depth,
                    external_dependencies=external_dependencies,
                    external_bin_dependencies=external_bin_dependencies)
                if d2 - set_depends_by == set([m2]):
                    depends &= set([m2])
                    if not depends:
                        break
    return sorted(list(depends))


def retrieve_db_modules(ctx, do_login=None):
    ctx['modules_unstable'] = []
    if ctx.get('db_name'):
        if do_login:
            if ctx.get('branch'):
                uid, ctx = clodoo.oerp_set_env(ctx=ctx,
                                               oe_version=ctx['branch'])
            else:
                uid, ctx = clodoo.oerp_set_env(ctx=ctx)
        model = 'ir.module.module'
        if not ctx.get('modules_to_match'):
            ctx['modules_to_match'] = sorted([x.name for x in
                clodoo.browseL8(ctx, model, clodoo.searchL8(
                    ctx, model, [('state', 'not in',
                                 ['uninstalled', 'uninstallable'])]))
            ])
        ctx['modules_unstable'] =  sorted([x.name for x in
                clodoo.browseL8(ctx, model, clodoo.searchL8(
                    ctx, model, [('state', 'in',
                                 ['to install', 'to upgrade', 'to remove'])]))
            ])
    return ctx


def main(ctx):
    ctx = retrieve_db_modules(ctx, do_login=True)
    if ctx['action'] == 'mod':
        res = get_modules_list(ctx['path_list'],
                               depth=ctx['depth'],
                               matches=ctx['modules_to_match'],
                               depends_by=ctx['depends_by'],
                               ao_list=ctx['ao_list'],
                               only_missed=ctx['only-missed'],
                               modules_unstable=ctx['modules_unstable'])
        if ctx['only_count']:
            print(len(res))
        else:
            print(ctx['sep_list'].join(res))
    elif ctx['action'] == 'dep':
        res = get_dependencies_list(
            ctx['path_list'],
            matches=ctx['modules_to_match'],
            depth=ctx['depth'],
            depends_by=ctx['depends_by'],
            ao_list=ctx['ao_list'],
            pure_list=ctx['pure_list'],
            external_dependencies=ctx['external_dependencies'],
            external_bin_dependencies=ctx['external_bin_dependencies'])
        if ctx['only_count']:
            print(len(res))
        else:
            print(ctx['sep_list'].join(res))
    elif ctx['action'] == 'rev':
        res = get_dependents_list(ctx['path_list'],
                                  matches=ctx['modules_to_match'],
                                  depth=ctx['depth'],
                                  depends_by=ctx['depends_by'],
                                  ao_list=ctx['ao_list'])
        if ctx['only_count']:
            print(len(res))
        else:
            print(ctx['sep_list'].join(res))
    elif ctx['action'] == 'jrq':
        res = get_just_dependents_list(
            ctx['path_list'],
            matches=ctx['modules_to_match'],
            depth=ctx['depth'],
            depends_by=ctx['depends_by'],
            ao_list=ctx['ao_list'],
            external_dependencies=ctx['external_dependencies'],
            external_bin_dependencies=ctx['external_bin_dependencies'])
        if ctx['only_count']:
            print(len(res))
        else:
            print(ctx['sep_list'].join(res))
    elif ctx['action'] == 'tree':
        error, modules = build_module_tree(ctx['path_list'],
                                           matches=ctx['modules_to_match'],
                                           depth=ctx['depth'])
        if error:
            print('Broken tree structure')

        rank_modules = {}
        for module in modules:
            level = modules[module].get('level', MISSED)
            if level not in rank_modules:
                rank_modules[level] = []
            rank_modules[level].append(module)

        for level in sorted(rank_modules.keys()):
            if level == MISSED or (level <= MAX_DEEP and
                                   ctx['only-missed']):
                continue
            for module in sorted(rank_modules[level]):
                if modules[module].get('level', MISSED) >= MAX_DEEP:
                    print(
                        '%s %s (%s)' % ('-' * MAX_DEEP,
                                        module,
                                        modules[module].get('status', '')))
                else:
                    print('%2d %s%s' % (level, ' ' * level, module))
        for module in sorted(rank_modules[MISSED]):
            print('%s %s (%s)' % ('*' * MAX_DEEP,
                                  module,
                                  modules[module].get('status', '')))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    ACTIONS = ('dep', 'help', 'jrq', 'mod', 'rev', 'tree')
    parser = z0lib.parseoptargs("Odoo dependencies management",
                                "© 2020-21 by SHS-AV s.r.l.",
                                version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-A', '--action',
                        action='store',
                        choices=ACTIONS,
                        dest='action')
    parser.add_argument('-a', '--and-list',
                        action='store_true',
                        dest='and_list')
    parser.add_argument("-b", "--branch",
                        help="Odoo branch",
                        dest="branch",
                        metavar="version")
    parser.add_argument('-B', '--depends-by',
                        action='store',
                        default='',
                        dest='depends_by')
    parser.add_argument("-c", "--config",
                        help="configuration command file",
                        dest="conf_fn",
                        metavar="file",
                        default=False)
    parser.add_argument("-D", "--dbname",
                        help="DB name",
                        dest="db_name",
                        metavar="file",
                        default=False)
    parser.add_argument('-E', '--only-missed',
                        action='store_true',
                        dest='only-missed')
    parser.add_argument('-e', '--external-dependencies',
                        action='store_true',
                        default='',
                        dest='external_dependencies')
    parser.add_argument('-H', '--action-help',
                        action='store_true',
                        dest='act_show_full_help')
    parser.add_argument('-M', '--modules-to-match',
                        action='store',
                        default='',
                        dest='modules_to_match')
    parser.add_argument('-m', '--action-modules',
                        action='store_true',
                        dest='act_modules')
    parser.add_argument('-N', '--only-count',
                        action='store_true',
                        dest='only_count')
    parser.add_argument('-n')
    parser.add_argument('-o', '--or-list',
                        action='store_true',
                        dest='or_list')
    parser.add_argument('-P', '--pure-list',
                        action='store_true',
                        dest='pure_list')
    parser.add_argument('-q')
    parser.add_argument('-R', '--recurse',
                        action='store_true',
                        dest='recurse')
    parser.add_argument('-S', '--sep-list',
                        action='store',
                        default=',',
                        dest='sep_list')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-x', '--external-bin-dependencies',
                        action='store_true',
                        default='',
                        dest='external_bin_dependencies')
    parser.add_argument('-1', '--no-depth',
                        action='store_true',
                        dest='no_depth')
    parser.add_argument('path_list',
                        nargs='*')
    ctx = parser.parseoptargs(sys.argv[1:])
    if (ctx['action'] not in ACTIONS and 
            ctx['path_list'] and ctx['path_list'][0] in ACTIONS):
        ctx['action'] = ctx['path_list'].pop(0)
    if not ctx['action']:
        if ctx['act_show_full_help']:
            ctx['action'] ='help'
    if ctx['action'] not in ACTIONS:
        print('Invalid action!')
        ctx['action'] = 'help'
    if ctx['action'] == 'help':
        print(__doc__)
        exit(1)
    if not ctx['path_list']:
        print('No odoo path list!')
        exit(1)
    path_list = []
    for path in ctx['path_list']:
        path_list += path.split(',')
    ctx['path_list'] = path_list
    if ctx['modules_to_match']:
        ctx['modules_to_match'] = ctx['modules_to_match'].split(',')
    if ctx['depends_by']:
        ctx['depends_by'] = ctx['depends_by'].split(',')
    if ctx['and_list']:
        ctx['ao_list'] = '&'
    elif ctx['or_list']:
        ctx['ao_list'] = '|'
    else:
        ctx['ao_list'] = False
    if ctx['no_depth']:
        ctx['depth'] = 1
    elif ctx['recurse']:
        ctx['depth'] = 999
    else:
        ctx['depth'] = False
    if ctx['db_name'] and not ctx['conf_fn']:
        print('No configuration file for DB access!')
        exit(1)
    if ctx['only-missed'] and (ctx['external_dependencies'] or
                               ctx['external_bin_dependencies']):
        print('Switches -E and -e or -b are mutually exclusive!')
        exit(1)
    if ctx['conf_fn'] and not ctx['db_name']: 
        print('Warning: configuration file without db name!')
    if ctx['db_name'] and ctx['modules_to_match']:
        print('Warning: -M switch disable -D switch!')
    exit(main(ctx))
