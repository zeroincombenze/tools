# import os
import os.path as pth
import sys
import argparse

from z0lib import z0lib


def run_traced(cmd, dry_run=False, rtime=False):
    sts, stdout, stderr = z0lib.run_traced(
        cmd, verbose=2, dry_run=dry_run, rtime=rtime
    )
    if sts:
        print("Error %d in %s" % (sts, cmd))
    return sts, stdout, stderr


def write_test_line(fd, ln):
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
        help="Do nothing (dry-run)",
        action="store_true",
    )
    return parser.parse_args(cli_args)


def main(cli_args=[]):
    if not cli_args:
        cli_args = sys.argv[1:]
    opt_args = parse_opts(cli_args)
    if not opt_args.python:
        print("No python version decalred: use --python=PYVER")
        print("Python 3.9 will be used!")
        opt_args.python = "3.9"
    print("")
    print("# Test setup ...")
    testdir = pth.expanduser("~/VENV_0000")
    pypidir = pth.dirname(pth.dirname(pth.dirname(__file__)))
    toolsdir = pth.join(testdir, "tools")
    if pth.isdir(testdir):
        cmd = "rm -fR %s" % testdir
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    cmd = ("%s %s/python_plus/python_plus/scripts/vem.py create %s -D -p %s"
           % (sys.executable, pypidir, testdir, opt_args.python))
    if opt_args.branch:
        cmd += (" -o ~/%s" % opt_args.branch)
    run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    cmd = "mkdir %s" % toolsdir
    run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    for pkg in ("clodoo", "lisa", "odoo_score", "oerplib3", "os0", "python_plus",
                "travis_emulator", "wok_code", "z0bug_odoo", "z0lib", "zar", "zerobug"):
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
    for fn in ("templates", "tests"):
        srcdir = pth.join(pypidir, "tools", fn)
        cmd = "cp -r %s/ %s/" % (srcdir, toolsdir)
        run_traced(cmd, dry_run=opt_args.dry_run, rtime=True)
    if not opt_args.dry_run:
        with open("%s/test_install.sh" % testdir, "w") as fd:
            write_test_line(fd, "flake8 --version\n")
            write_test_line(fd, "pylint --version\n")
            write_test_line(fd, "cd %s\n" % testdir)
            write_test_line(fd, ". bin/activate\n")
            write_test_line(fd, "cd %s\n" % toolsdir)
            write_test_line(fd, "./install_tools.sh -vptT\n")
            write_test_line(fd, "echo ''\n")
        run_traced("chmod +x %s/test_install.sh" % testdir, dry_run=opt_args.dry_run, rtime=True)

    print("")
    print("# Start test ...")
    run_traced("%s/test_install.sh" % testdir, dry_run=opt_args.dry_run, rtime=True)
    return 0


if __name__ == "__main__":
    exit(main())
