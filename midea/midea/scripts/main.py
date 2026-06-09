#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from .midea_do_something import MideaDoSomething


def internal_main(cli_args=None):  # pragma: no cover
    if not cli_args:
        cli_args = sys.argv[1:]
    if len(cli_args):
        Something = MideaDoSomething(cli_args[0])
        Something.do_repeat_last_action()
    return 0
