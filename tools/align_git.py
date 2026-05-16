#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from z0lib import z0lib


def check_cwd():
    tgt_path = os.getcwd()
    if not os.path.isdir(os.path.join(tgt_path, ".git")):
        print("Current directory %s is not a git path!" % tgt_path)
        return 1
    return 0


def run_git_summary():
    cmd = ["git", "diff", "--summary"]
    sts, stdout, stderr = z0lib.os_system_traced(cmd, with_shell=True, rtime=True)
    if sts:
        return sts
    for ln in stdout.split("\n"):
        if not ln.strip().startswith("mode change"):
            continue
        tokens = ln.strip().split(" ")
        # print("File %s with stat %s will be change to %s" % (tokens[5], tokens[4], tokens[2]))
        cmd = "chmod %s %s  # %s" % (tokens[2][-3:], tokens[5], tokens[4][-3:])
        sts = z0lib.os_system(cmd, with_shell=True, rtime=True)
    return 0


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    sts = check_cwd()
    if sts == 0:
        sts= run_git_summary()
    return sts


if __name__ == "__main__":
    exit(main())
