import sys
import os


TAG = "# -*- coding: utf-8 -*-"
UNTAG = "# -*- encoding: utf-8 -*-"


def do_set_utf8(ffn):
    found_tag = False
    with open(ffn, 'r') as fd:
        lines = fd.read().split('\n')
        for nro, line in enumerate(lines):
            if line == TAG:
                found_tag = True
                break
            elif line == UNTAG:
                lines[nro] = TAG
                found_tag = True
                break
            if not line or (not line.startswith("#!")
                            and not line.startswith("# flake8")):
                break
        if not found_tag:
            lines.insert(nro, TAG)
    if not found_tag:
        bakfile = '%s~' % ffn
        if os.path.isfile(bakfile):
            os.remove(bakfile)
        if os.path.isfile(ffn):
            os.rename(ffn, bakfile)
        with open(ffn, 'w') as fd:
            fd.write("\n".join(lines))
            print(ffn)


def main(argv):
    argv = argv or sys.argv[1:]
    path = None
    for param in argv:
        if param.startswith('-'):
            pass
        else:
            path = os.path.expanduser(param)
    if not path:
        print('No path supplied! Use %s PATH' % sys.argv[0])
        return 1
    if not os.path.isdir(path):
        print('Path %s does not exist!' % sys.argv[0])
        return 2
    for root, dirs, files in os.walk(path):
        if 'setup' in dirs:
            del dirs[dirs.index('setup')]
        for fn in files:
            if not fn.endswith('.py'):
                continue
            ffn = os.path.join(root, fn)
            do_set_utf8(ffn)
    return 0


if __name__ == "__main__":
    exit(main(None))
