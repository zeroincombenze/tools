#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path as pth
import sys

if sys.version_info[0] < 3 or sys.version_info[1] <= 7:
    import platform
else:
    try:
        import distro
    except ImportError:
        # During local test execution, distro is loaded on local test environment
        import os

        os.system("python -m pip install distro")


__version__ = "2.0.22"


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
        if sys.version_info[0] < 3 or sys.version_info[1] <= 7:
            dist, ver, suppl = platform.dist()
        else:
            dist, ver, suppl = distro.linux_distribution()
        if dist == "centos":
            before = (
                "yum install libffi-devel gcc openssl-devel bzip2-devel"
                " ncurses-devel readline-devel"
            )
        else:
            before = (
                "apt install libssl-dev libffi-dev libncurses5-dev"
                " libsqlite3-dev libreadline-dev"
            )
        parser.add_argument(
            "--cmd-before",
            help=("Command to execute before install python; example:" + before),
        )
        parser.add_argument(
            "--config-opts",
            help="Options for ./configure; example:  --with-openssl=DIR",
        )
        if not for_help:
            self.please.add_argument(parser, "-j")
            self.please.add_argument(parser, "-n")
            self.please.add_argument(parser, "-q")
            self.please.add_argument(parser, "-v")
        parser.add_argument(
            "--wget-opts", help="Options for wget; example: --no-check-certificate"
        )
        parser.add_argument("args", nargs="*")
        return parser

    def do_install(self):
        please = self.please
        cmd = pth.join(
            pth.dirname(pth.dirname(pth.abspath(__file__))),
            "install_python_3_from_source.sh",
        )
        if not pth.isfile(cmd):
            print("Internal package error: file %s not found!" % cmd)
            return 127
        valid_odoo_vers = ("2.7", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11")
        if please.opt_args.python not in valid_odoo_vers:
            print("You must specify the python version: %s" % ",".join(valid_odoo_vers))
            return 1
        cmd += " " + please.opt_args.python
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
            please.os_system(
                cmd,
                verbose=self.please.opt_args.verbose,
                dry_run=please.opt_args.dry_run,
            )
            return 0
        return please.os_system(cmd)

