# -*- coding: utf-8 -*-
import sys
import os.path as pth

def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    if len(cli_args) < 2:
        print("usage: %s srcpath tgtpath" % sys.argv[0])
    srcpath = cli_args[0]
    tgtpath = cli_args[1]
    if pth.isdir(srcpath):
        if pth.basename(srcpath) != "scripts":
            srcpath = pth.join(srcpath, "scripts", "main.py")
        else:
            srcpath = pth.join(srcpath, "main.py")
    if not pth.isfile(srcpath):
        print("File %s not found!" % srcpath)
        return 3
    if pth.isdir(tgtpath):
        if pth.basename(tgtpath) != "scripts":
            tgtpath = pth.join(tgtpath, "scripts", "main.py")
        else:
            tgtpath = pth.join(tgtpath, "main.py")
    if not pth.isfile(tgtpath):
        print("File %s not found!" % tgtpath)
        return 3
    with open(srcpath, "r") as fd:
        source = fd.read().split("\n")
    srclineno = 0
    while not source[srclineno].startswith("__version__ ="):
        srclineno += 1
    srclineno += 1
    with open(tgtpath, "r") as fd:
        target = fd.read().split("\n")
    tgtlineno = 0
    while not target[tgtlineno].startswith("__version__ ="):
        tgtlineno += 1
    tgtlineno += 1
    del target[tgtlineno:]
    while srclineno < len(source):
        target.append(source[srclineno])
        srclineno += 1
    with open(tgtpath, "w") as fd:
        fd.write("\n".join(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
