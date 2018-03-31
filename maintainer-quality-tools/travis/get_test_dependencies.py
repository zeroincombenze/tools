# [antoniov: 2018-02-18]
import sys
from getaddons import get_addons, get_modules, is_installable_module
from test_server import get_test_dependencies
__version__ = '0.2.1.2'
ltype = ''
path = ''
addons_list=None
if len(sys.argv) > 1: ltype=sys.argv[1]
if len(sys.argv) > 2: path=sys.argv[2]
if len(sys.argv) > 3: addons_list=sys.argv[3].split(',')
if ltype == 'mod':
    paths=path.split(',')
    res=[]
    for path in paths:
        r=get_modules(path)
        for m in r:
            if m not in res:
                res.append(m)
    print ','.join(res)
elif ltype == 'dep':
    res=get_test_dependencies(path, addons_list)
    print ','.join(res)
else:
    print 'get_test_dependencies.py mod|dep path [addons_list]'
