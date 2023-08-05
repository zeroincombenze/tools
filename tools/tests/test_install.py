# import os
import os
import os.path as pth
import sys
import argparse

from z0lib import z0lib

PKG_LIST = ("clodoo", "lisa", "odoo_score", "oerplib3", "os0", "python_plus",
            "travis_emulator", "wok_code", "z0bug_odoo", "z0lib", "zar", "zerobug")


def run_traced(cmd, dry_run=False, rtime=False):
    sts, stdout, stderr = z0lib.run_traced(
        cmd, verbose=2, dry_run=dry_run, rtime=rtime
    )
    if sts:
        print("Error %d in %s" % (sts, cmd))
    return sts, stdout, stderr


def write_test_line(fd, ln):
    if not ln.startswith("echo") and not ln.startswith("#!"):
        fd.write("echo %s\n" % ln)
    fd.write("%s\n" % ln)


def parse_opts(cli_args=[]):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Tools install test.",
        epilog=(
            "© 2022-2023 by SHS-AV s.r.l.\n"
            "Author: antoniomaria.vigliotti@gmail.com\n"
            "Full documentation at: https://zeroincombenze-tools.readthedocs.io/\n"
        ),
    )
    parser.add_argument(
        "-b",  "--odoo-branch",
        dest="branch",
        metavar="BRANCH",
        help="Run test with Odoo version",
    )
    parser.add_argument(
        "-j",
        "--python",
        metavar="PYVER",
        help="Run test with specific python version",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Do nothing (dry-run)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count", default=0,
        help="verbose mode",
    )
    parser.add_argument(
        "-w", "--from-vme",
        action="store_true",
        help="Run test with specific python version",
    )
    return parser.parse_args(cli_args)


def create_venv(opt_args, testdir, pypidir, toolsdir):
    if opt_args.from_vme:
        if opt_args.branch:
            srcdir = "~/VME/VME" + opt_args.branch
        else:
            srcdir = "~/VME/VME" + opt_args.python
        cmd = ("%s %s/python_plus/python_plus/scripts/vem.py cp %s %s"
               % (sys.executable, pypidir, srcdir, testdir))
    else:
        cmd = ("%s %s/python_plus/python_plus/scripts/vem.py create %s -D -p %s"
               % (sys.executable, pypidir, testdir, opt_args.python))
        if opt_args.branch:
            cmd += (" -o ~/%s" % opt_args.branch)
    cmd += " -v" if opt_args.verbose else ""
    run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    cmd = "mkdir %s" % toolsdir
    run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    for pkg in PKG_LIST:
        srcdir = pth.join(pypidir, pkg, pkg)
        cmd = "cp -r %s %s" % (srcdir, toolsdir)
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
        srcdir = pth.join(pypidir, pkg)
        cmd = "cp %s/setup.py %s/%s" % (srcdir, toolsdir, pkg)
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
        if pkg != "oerplib3":
            cmd = "cp %s/setup.py %s/%s/scripts/setup.info" % (srcdir, toolsdir, pkg)
            run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
        cmd = "cp %s/README.rst %s/%s" % (srcdir, toolsdir, pkg)
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    for fn in ("install_tools.sh", "odoo_default_tnl.xlsx", "odoo_template_tnl.xlsx"):
        srcpath = pth.join(pypidir, "tools", fn)
        cmd = "cp %s %s/" % (srcpath, toolsdir)
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    for fn in ("license_text", "templates", "tests"):
        srcdir = pth.join(pypidir, "tools", fn)
        cmd = "cp -r %s/ %s/" % (srcdir, toolsdir)
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    opt_args = parse_opts(cli_args)
    if not opt_args.python:
        print("No python version declared: use --python=PYVER")
        print("Python 3.9 will be used!")
        opt_args.python = "3.9"
    print("")
    print("")
    print("### Test setup ...")
    print("")
    venvdir = pth.expanduser("~/VENV_0" + opt_args.python.replace(".", ""))
    venvdir += opt_args.branch.replace(".", "") if opt_args.branch else "0"
    pypidir = pth.dirname(pth.dirname(pth.dirname(__file__)))
    toolsdir = pth.join(venvdir, "tools")
    if pth.isdir(venvdir):
        cmd = "rm -fR %s" % venvdir
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    create_venv(opt_args, venvdir, pypidir, toolsdir)

    if not opt_args.dry_run:
        with open("%s/test_install.sh" % venvdir, "w") as fd:
            write_test_line(fd, "#!/usr/bin/env bash")
            write_test_line(fd, "echo ''")
            write_test_line(fd, "echo '# Starting ./install_tools.sh'")
            write_test_line(fd, "flake8 --version || echo '*** flake8 not found ***'")
            write_test_line(fd, "pylint --version || echo '*** pylint not found ***'")
            write_test_line(fd, "echo PATH=$PATH")
            write_test_line(fd, "cd %s" % venvdir)
            write_test_line(fd, "source bin/activate")
            write_test_line(fd, "echo $PATH")
            write_test_line(fd, "which python")
            write_test_line(fd, "python --version")
            write_test_line(fd, "cd %s" % toolsdir)
            write_test_line(fd,
                            "./install_tools.sh -vptT" if opt_args.verbose
                            else "./install_tools.sh -qptT")
            write_test_line(fd, "echo PATH=$PATH")
            write_test_line(fd, "deactivate")
            write_test_line(fd, "echo PATH=$PATH")
            write_test_line(fd, "echo ''")
        run_traced("chmod +x %s/test_install.sh" % venvdir,
                   dry_run=opt_args.dry_run, rtime=True)

    print("")
    print("")
    print("### Starting test phase ...")
    print("")
    run_traced("%s/test_install.sh" % venvdir, dry_run=opt_args.dry_run, rtime=True)

    if not opt_args.dry_run:
        with open("%s/test_install2.sh" % venvdir, "w") as fd:
            write_test_line(fd, "#!/usr/bin/env bash")
            write_test_line(fd, "echo ''")
            write_test_line(fd, "echo '# Starting ./install_tools2.sh'")
            write_test_line(fd, "SAVED_PATH=\"$PATH\"")
            write_test_line(fd, "echo PATH=$PATH")
            write_test_line(fd, "cd %s" % venvdir)
            write_test_line(fd, "source bin/activate")
            write_test_line(fd, "source %s/devel/activate_tools" % venvdir)
            write_test_line(fd, "echo PATH=$PATH")
            write_test_line(fd, "which python")
            write_test_line(fd, "python --version")
            write_test_line(fd, "which vem")
            for pkg in PKG_LIST:
                if pkg == "oerplib3" and opt_args.python.startswith("2"):
                    pkg = "oerplib"
                if pkg in ("lisa", "odoo_score", "travis_emulator", "wok_code", "zar"):
                    continue
                write_test_line(
                    fd, "vem %s show %s | grep -E '^(Name|Location)'" % (venvdir, pkg))
            write_test_line(fd, "echo '# Restoring default virtualenv'")
            write_test_line(fd, "source %s" % pth.join(
                pth.dirname(venvdir), "devel", "activate_tools"))
            write_test_line(fd, "export PATH=\"$SAVED_PATH\"")
            write_test_line(fd, "echo PATH=$PATH")
        run_traced("chmod +x %s/test_install2.sh" % venvdir,
                   dry_run=opt_args.dry_run, rtime=True)
        os.system("%s/test_install2.sh" % venvdir)
    return 0


if __name__ == "__main__":
    exit(main())
