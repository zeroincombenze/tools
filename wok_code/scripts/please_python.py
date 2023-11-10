#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from z0lib import z0lib

__version__ = "2.0.12"


class PleasePython(object):
    """NAME
    please install python - install a specific python version

SYNOPSIS
    please install python PYTHON3_VERSION [options]

DESCRIPTION
    This command installs a specific python version on system from source.
    To install python you must be the root user or you must have the admin
    privileges.

OPTIONS
  %(options)s

  --cmd-before
      Command to execute before install python3; usually install some system packages.
      On Ubuntu the command should be:
      --cmd-before='apt install libssl-dev libffi-dev libncurses5-dev libsqlite3-dev ' \
          'libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev libbz2-dev'

  --config-opts
    Options to apply for ./configure; read python documentation for furthermore info.
    After install you can obtain help withh follow command:
    cd /tmp/Python-PYTHON-VERSION/.configure --help
    example: --config-opts='--with-openssl=DIR'

  --wget-opts
    Options to apply to wget when python source wil be downloaded from python.org;
    read wget documentation for furthermore info.
    example: --wget-info='--no-check-certificate'

EXAMPLES
    please python 3.9

BUGS
    No known bugs."""

    def __init__(self, please):
        self.please = please

    def action_opts(self, parser, for_help=False):
        parser.add_argument(
            "--cmd-before",
            help=(
                "Command to execute before install python; example:"
                "apt install libssl-dev libffi-dev libncurses5-dev libsqlite3-dev"
            ),
        )
        parser.add_argument(
            "--config-opts",
            help="Options for ./configure; example:  --with-openssl=DIR",
        )
        if not for_help:
            self.please.add_argument(parser, "-n")
            self.please.add_argument(parser, "-q")
            self.please.add_argument(parser, "-v")
        parser.add_argument(
            "--wget-opts", help="Options fro wget; example: --no-check-certificate"
        )
        parser.add_argument("args", nargs="*")
        return parser

    def do_install(self):
        please = self.please
        cmd = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "install_python_3_from_source.sh",
        )
        if not os.path.isfile(cmd):
            print("Internal package error: file %s not found!" % cmd)
            return 127
        if not please.sub1 or please.sub1 not in ("3.6", "3.7", "3.8", "3.9"):
            print("You must specify the python version: 3.6 or 3.7 or 3.8 or 3.9")
            return 1
        cmd += " " + please.sub1
        cmd += (
            " '"
            + (please.opt_args.cmd_before if please.opt_args.cmd_before else "")
            + "'"
        )
        cmd += (
            " '"
            + (please.opt_args.wget_opts if please.opt_args.wget_opts else "")
            + "'"
        )
        cmd += (
            " '"
            + (please.opt_args.config_opts if please.opt_args.config_opts else "")
            + "'"
        )
        if please.opt_args.dry_run:
            z0lib.run_traced(
                cmd, verbose=self.opt_args.verbose, dry_run=please.opt_args.dry_run
            )
            return 0
        return please.run_traced(cmd)

