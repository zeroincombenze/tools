#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Usage: odoo_dependencies.py -r|-m|-d|mod|dep -1 path_list
                    [-M modules_to_match] [-a] [-b depends_by_module_list]

With switch 'mod' or -m, return module list from path_list (comma separated).

With switch -r, return module which depends from one of modules_to_match.
Adding -a switch, return module that depends from all modules_to_match, just 1 level

With switch 'dep' or -d, return dependencies list from path_list
  for specific modules_to_match (comma separated) if supplied
  otherwise modules_to_match is generated from path_list.
Return just 1 level depth dependecies (no recurse) with switch -1.
Adding -a switch, limit dependency list to only modules which all its depends
  are in -b switch.

Limit result list just to modules which depends by one of -b switch.
"""
from __future__ import print_function, unicode_literals

import sys
import os
import ast
from six import string_types
try:
    from os0 import os0
except ImportError:
    import os0
try:
    from z0lib.z0lib import parseoptargs
except ImportError:
    from z0lib import parseoptargs

__version__ = '0.2.2.6'


MANIFEST_FILES = [
    '__manifest__.py',
    '__odoo__.py',
    '__openerp__.py',
    '__terp__.py',
]


def get_test_dependencies(addons_path, addons_list,
                          depends_by=None, ao_list=None):
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
            deps = get_dependencies(modules, module)
            if depends_by:
                deps &= set(depends_by)
            dependencies |= deps
    elif ao_list == '&':
        dependencies = get_dependencies(modules, addons_list[0])
        for module in addons_list[1:]:
            deps = get_dependents(modules, module)
            if depends_by:
                deps &= set(depends_by)
            dependencies &= set(deps)
            if not dependencies:
                break
    return list(dependencies - set(addons_list))


def get_dependencies(modules, module_name, depth=None):
    """Return a set of all the dependencies in deep of the module_name.
    The module_name is included in the result."""
    depth = depth or 999
    result = set()
    for dependency in modules.get(module_name, {}).get('depends', []):
        if depth > 1:
            result |= get_dependencies(modules, dependency, depth=depth-1)
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


def get_dep_of_module(addons_path, addons_list):
    if not addons_list:
        return ['base']
    else:
        modules = {}
        for path in addons_path.split(','):
            modules.update(get_modules_info(path))
        dependencies = set()
        for module in addons_list:
            dependencies |= get_dependencies(modules, module)
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


def get_modules(path, depth=1):
    """ Return modules of path repo (used in test_server.py)"""
    return sorted(list(get_modules_info(path, depth).keys()))


def get_modules_info(path, depth=1):
    """ Return a digest of each installable module's manifest in path repo"""
    path = os.path.expanduser(path)
    # Avoid empty basename when path ends with slash
    path = os.path.dirname(path) if not os.path.basename(path) else path
    modules = {}
    if os.path.isdir(path) and depth > 0:
        for module in os.listdir(path):
            module_path = os.path.join(path, module)
            manifest_path = is_module(module_path)
            if manifest_path:
                try:
                    manifest = ast.literal_eval(open(manifest_path).read())
                except ImportError:
                    raise Exception('Wrong file %s' % manifest_path)
                if manifest.get('installable', True):
                    modules[module] = {
                        'application': manifest.get('application', False),
                        'depends': manifest.get('depends', []),
                        'auto_install': manifest.get('auto_install', False),
                    }
            elif (not module.startswith('_') and
                    os.path.isdir(module_path)):
                deeper_modules = get_modules_info(
                    os.path.join(path, module), depth-1)
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


def get_modules_changed(path, ref='HEAD'):
    """Get modules changed from git diff-index {ref}
    :param path: String path of git repo
    :param ref: branch or remote/branch or sha to compare
    :return: List of paths of modules changed
    """
    path = os.path.expanduser(path)
    git_run_obj = GitRun(os.path.join(path, '.git'))
    if ref != 'HEAD':
        fetch_ref = ref
        if ':' not in fetch_ref:
            # to force create branch
            fetch_ref += ':' + fetch_ref
        git_run_obj.run(['fetch'] + fetch_ref.split('/', 1))
    items_changed = git_run_obj.get_items_changed(ref)
    folders_changed = set([
        item_changed.split('/')[0]
        for item_changed in items_changed
        if '/' in item_changed]
    )
    modules = set(get_modules(path))
    modules_changed = list(modules & folders_changed)
    modules_changed_path = [
        os.path.join(path, module_changed)
        for module_changed in modules_changed]
    return modules_changed_path


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


def get_applications_with_dependencies(modules):
    """ Return all modules marked as application with their dependencies.
    For our purposes, l10n modules cannot be an application. """
    result = set()
    for module, module_data in modules.items():
        if module_data.get('application') and not module.startswith('l10n_'):
            result |= get_dependencies(modules, module)
    return add_auto_install(modules, result)


def get_localizations_with_dependents(modules):
    """ Return all localization modules with the modules that depend on them
    """
    result = set()
    for module in modules.keys():
        if module.startswith('l10n_'):
            result |= get_dependents(modules, module)
    return result


def get_module_list(path_list, depth=None, matches=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 1
    matches = matches or []
    res = []
    for path in paths:
        repo = get_modules(os.path.expanduser(path), depth=depth)
        for module in repo:
            if module not in res:
                res.append(module)
    if matches:
            res = list(set(res) & set(matches))
    return sorted(res)


def get_dependencies_list(path_list, matches=None, depth=None,
                          depends_by=None, ao_list=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 999
    depends_by = depends_by or []
    ao_list = ao_list or '|'
    module_list = matches or get_module_list(path_list, depth=depth)
    modules = {}
    for path in paths:
        modules.update(get_modules_info(path, depth=depth))
    dependencies = set()
    if ao_list == '|':
        for module in module_list:
            deps = get_dependencies(modules, module, depth=depth)
            if depends_by:
                deps &= set(depends_by)
            dependencies |= deps
    elif ao_list == '&':
        dependencies = get_dependencies(modules, module_list[0], depth=depth)
        for module in module_list[1:]:
            deps = get_dependencies(modules, module, depth=depth)
            if depends_by:
                deps &= set(depends_by)
            dependencies &= set(deps)
            if not dependencies:
                break
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
    module_list = matches or get_module_list(path_list, depth=depth)
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
                             depends_by=None, ao_list=None):
    if isinstance(path_list, string_types):
        paths = path_list.split(',')
    else:
        paths = path_list
    depth = depth or 1
    depends_by = depends_by or ['base']
    ao_list = ao_list or '|'
    module_list = matches or get_module_list(path_list, depth=depth)
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
                d2 = get_dependencies(modules, m2, depth=depth)
                if d2 - set_depends_by == set([m2]):
                    depends |= set([m2])
    elif ao_list == '&':
        depends = get_dependents(modules, depends_by[0], depth=depth)
        for module in depends_by[1:]:
            deps = get_dependents(modules, module, depth=depth)
            if matches:
                deps &= set(matches)
            for m2 in deps:
                d2 = get_dependencies(modules, m2, depth=depth)
                if d2 - set_depends_by == set([m2]):
                    depends &= set([m2])
                    if not depends:
                        break
    return sorted(list(depends))


def main(argv=None):
    if ctx['action'] == 'mod':
        res = get_module_list(ctx['path_list'],
                              depth=ctx['depth'],
                              matches=ctx['modules_to_match'])
        if ctx['only_count']:
            print(len(res))
        else:
            print(ctx['sep_list'].join(res))
    elif ctx['action'] == 'dep':
        res = get_dependencies_list(ctx['path_list'],
                                    matches=ctx['modules_to_match'],
                                    depth=ctx['depth'],
                                    depends_by=ctx['depends_by'],
                                    ao_list=ctx['ao_list'])
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
        res = get_just_dependents_list(ctx['path_list'],
                                  matches=ctx['modules_to_match'],
                                  depth=ctx['depth'],
                                  depends_by=ctx['depends_by'],
                                  ao_list=ctx['ao_list'])
        if ctx['only_count']:
            print(len(res))
        else:
            print(ctx['sep_list'].join(res))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    parser = parseoptargs("Odoo dependencies",
                          "© 2019 by SHS-AV s.r.l.",
                          version=__version__)
    parser.add_argument('-h')
    parser.add_argument('-a', '--and-list',
                        action='store_true',
                        dest='and_list')
    parser.add_argument('-B', '--depends-by',
                        action='store',
                        default='',
                        dest='depends_by')
    parser.add_argument('-d', '--action-depends',
                        action='store_true',
                        dest='act_depends')
    parser.add_argument('-H', '--action-help',
                        action='store_true',
                        dest='act_show_full_help')
    parser.add_argument('-j', '--action-just-reverse-modules',
                        action='store_true',
                        dest='act_just_reverse_modules')
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
    parser.add_argument('-q')
    parser.add_argument('-R', '--recurse',
                        action='store_true',
                        dest='recurse')
    parser.add_argument('-r', '--action-reverse-modules',
                        action='store_true',
                        dest='act_reverse_modules')
    parser.add_argument('-S', '--sep-list',
                        action='store',
                        default=',',
                        dest='sep_list')
    parser.add_argument('-V')
    parser.add_argument('-v')
    parser.add_argument('-1', '--no-depth',
                        action='store_true',
                        dest='no_depth')
    parser.add_argument('action',
                        nargs='?')
    parser.add_argument('path_list',
                        nargs='?')
    ctx = parser.parseoptargs(sys.argv[1:])
    if ctx['action'] not in ('dep', 'help', 'jrq', 'mod', 'rev'):
        if not ctx['path_list']:
            ctx['path_list'] = ctx['action']
            ctx['action'] = ''
    if not ctx['action']:
        if ctx['act_modules']:
            ctx['action'] ='mod'
        elif ctx['act_depends']:
            ctx['action'] ='dep'
        elif ctx['act_just_reverse_modules']:
            ctx['action'] ='jrq'
        elif ctx['act_reverse_modules']:
            ctx['action'] ='rev'
        elif ctx['act_show_full_help']:
            ctx['action'] ='help'
    if ctx['action'] not in ('dep', 'help', 'jrq', 'mod', 'rev'):
        print('Invalid action!')
        exit (1)
    if ctx['action'] == 'help':
        print(__doc__)
        exit(1)
    if not ctx['path_list']:
        print('No odoo path list!')
        exit (1)
    if ctx['path_list']:
        ctx['path_list'] = ctx['path_list'].split(',')
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
    exit(main(ctx))
