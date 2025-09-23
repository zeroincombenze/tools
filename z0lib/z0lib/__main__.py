#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
# from .scripts.main import internal_main
from z0lib import internal_main, z0lib

__version__ = "2.1.1"


def version():
    return __version__


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    if cli_args:
        args = []
        kwargs = {}
        for arg in cli_args[1:]:
            if re.match("[a-z0-9_]+=", arg):
                k, v = arg.split("=", 1)
                kwargs[k] = int(v) if v.isdigit() else v
            else:
                args.append(int(arg) if arg.isdigit() else arg)
        args = " ".join(args)
        if any(
                [arg in ("-V", "--version", "--copy-pkg-data") for arg in cli_args]):
            return internal_main(cli_args)
        elif cli_args[0] == "os_system":
            return getattr(z0lib, cli_args[0])(args, **kwargs)[0]
        elif cli_args[0] in (
                "os_system_traced",
                "run_traced"):
            return getattr(z0lib, cli_args[0])(args, **kwargs)[0]
        elif cli_args[0] == "get_uniqid":
            udi, umli = getattr(z0lib.Package(cli_args[1]), cli_args[0])()
            print("export UDI=\"%s\"; export UMLI=\"%s\"" % (udi, umli))
            return 0
    return 126


if __name__ == "__main__":
    sys.exit(main())
