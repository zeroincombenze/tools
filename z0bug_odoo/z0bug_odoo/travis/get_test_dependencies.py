# -*- coding: utf-8 -*-
"""
Usage: get_test_dependencies.py -r|-m|-d|mod|dep -1 path_list [module_list]

If 1st switch is 'mod' or -m, return module list from path_list (comma separated)
If 1st switch is 'dep' or -d, return dependencies list from path_list
for specific module_list (comma separated) if supplied or
module_list is generated from path_list.
if -1 is supplied return just 1 level depth dependecies (no recurse)
If 1st swicth is -r, return module which dependes from module_list
"""
from __future__ import print_function

import os
import sys

try:
    from getaddons import (get_dependencies, get_dependents, get_modules,
                           get_modules_info)
    from test_server import get_test_dependencies
except ImportError:
    from .getaddons import (get_dependencies, get_dependents, get_modules,
                            get_modules_info)
    from .test_server import get_test_dependencies


__version__ = '2.0.17'


def get_module_list(paths):
    res = []
    for path in paths.split(','):
        r = get_modules(os.path.expanduser(path))
        for m in r:
            if m not in res:
                res.append(m)
    return res


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


def main(argv=None):
    if argv is None:
        argv = sys.argv
    argv = argv[1:]
    if not argv:
        print(__doc__)
        return 1

    list_type = False
    paths = ''
    module_list = None
    not_recurse = False

    params = []
    while argv:
        if argv[0].startswith('-'):
            param = argv.pop(0)
            if param == '-h' or param == '--help':
                print(__doc__)
                return 1
            elif param == '-V' or param == '--version':
                print(__version__)
                return 1
            elif param == '-d':
                list_type = 'dep'
            elif param == '-m':
                list_type = 'mod'
            elif param == '-r':
                list_type = 'req'
            elif param == '-1':
                not_recurse = True
            else:
                raise Exception('Unknown parameter: %s' % param)
        else:
            params.append(argv.pop(0))

    if not list_type and len(params):
        list_type = params.pop(0)
    if len(params):
        paths = params.pop(0)
    if len(params):
        module_list = params.pop(0).split(',')

    if list_type == 'mod':
        print(','.join(get_module_list(paths)))
    elif list_type == 'dep':
        if not module_list:
            module_list = get_module_list(paths)
        if not_recurse:
            modules = get_modules_info(paths, depth=1)
            res = []
            for module in module_list:
                res += modules[module].get('depends', [])
        else:
            res = get_test_dependencies(paths, module_list)
        print(','.join(res))
    elif list_type == 'req':
        if not module_list:
            module_list = get_module_list(paths)
        modules = get_modules_info(paths, depth=1)
        res = []
        for module in module_list:
            res += get_dependents(modules, module)
        print(','.join(res))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())






