# -*- coding: utf-8 -*-
import os
import sys
import re


def os_env(item, default=None):
    default = default or item
    return os.environ.get(item, default)


def comment_line(line):
    line_out = ""
    while line.startswith(" "):
        line_out += " "
        line = line[1:]
    line_out += "# "
    line_out += line
    return line_out


def expand_macro(line, section, ctx):
    for item in ctx.keys():
        if item == "ODOO_MAIN_VERSION":
            continue
        line = line.replace("${%s}" % item, ctx[item])
    branch = ctx["TRAVIS_BRANCH"].split(".")[0]
    if re.match(r"^ *#", line) or not line.strip():
        pass
    elif ctx["PRJNAME"] == "Odoo" and section == "python":
        if (
            (re.match(r"^ *\- *[\"']?3", line)
             and ctx["TRAVIS_PYTHON_VERSION"].startswith("2"))
            or (re.match(r"^ *\- *[\"']?2", line)
                and ctx["TRAVIS_PYTHON_VERSION"].startswith("3"))
        ):
            line = comment_line(line)
    elif section == "before_install":
        if re.match(r"^ *\- \$HOME/tools/install_tools.sh", line):
            verbose = "q" if int(ctx["TRAVIS_DEBUG_MODE"]) < 3 else "vv"
            if ctx["TRAVIS_PYTHON_VERSION"].startswith("2"):
                line = "  - $HOME/tools/install_tools.sh -%spt2" % verbose
            else:
                line = "  - $HOME/tools/install_tools.sh -%spt" % verbose
    elif section == "install":
        if re.match(r"^ *\- travis_install_env", line):
            if ctx["PRJNAME"] == "Odoo":
                line = "  - travis_install_env"
            else:
                line = "  - travis_install_env tools"
    elif section == "env.global":
        if re.match(r"^ *\- WKHTMLTOPDF_VERSION", line):
            line = {
                "6": "  - WKHTMLTOPDF_VERSION=\"0.12.1\"",
                "7": "  - WKHTMLTOPDF_VERSION=\"0.12.1\"",
                "8": "  - WKHTMLTOPDF_VERSION=\"0.12.4\"",
                "9": "  - WKHTMLTOPDF_VERSION=\"0.12.4\"",
                "10": "  - WKHTMLTOPDF_VERSION=\"0.12.4\"",
                "11": "  - WKHTMLTOPDF_VERSION=\"0.12.4\"",
                "12": "  - WKHTMLTOPDF_VERSION=\"0.12.5\"",
                "13": "  - WKHTMLTOPDF_VERSION=\"0.12.5\"",
                "14": "  - WKHTMLTOPDF_VERSION=\"0.12.6\"",
                "15": "  - WKHTMLTOPDF_VERSION=\"0.12.6\"",
                "16": "  - WKHTMLTOPDF_VERSION=\"0.12.6\"",
            }.get(branch, line)
    elif section == "env.matrix":
        if (
            (ctx["PRJNAME"] == "Odoo"
             and re.match(r"^ *\- (DEV_ENVIRONMENT|MODULE_PATH)=", line))
            or (ctx["PRJNAME"] != "Odoo"
                and not re.match(r"^ *\- (DEV_ENVIRONMENT|MODULE_PATH)=", line))
        ):
            line = comment_line(line)
    elif section == "script":
        if re.match(r"^ *\- travis_run", line):
            if ctx["PRJNAME"] == "Odoo":
                line = "  - travis_run_tests"
            elif ctx["REPOSNAME"] == "tools" and ctx["PRJNAME"] == "tools":
                line = "  - cd $MODULE_PATH; travis_run_pypi_tests"
            else:
                line = "  - travis_run_pypi_tests"
    return line


def get_pyver_4_odoo(odoo_major):
    if odoo_major <= 10:
        pyver = "2.7"
    else:
        pyver = "3.%d" % (int((odoo_major - 9) / 2) + 6)
    return pyver


def make_travis_conf(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    src = cli_args[0]
    tgt = cli_args[1]
    ctx = {
        "PKGNAME": os_env("PKGNAME", os.path.basename(os.getcwd())),
        "PRJNAME": os_env("PRJNAME"),
        "REPOSNAME": os_env("REPOSNAME"),
        "TRAVIS_BRANCH": os_env("TRAVIS_BRANCH", os_env("BRANCH")),
        "TRAVIS_DEBUG_MODE": os_env("TRAVIS_DEBUG_MODE", "0"),
        "TRAVIS_BUILD_DIR": os_env("TRAVIS_BUILD_DIR", os.getcwd()),
        "TRAVIS_PYTHON_VERSION": os_env("TRAVIS_PYTHON_VERSION"),
        "TRAVIS_REPO_SLUG":
            os_env("TRAVIS_REPO_SLUG", "local/%s" % os.path.basename(os.getcwd())),
    }
    odoo_major = ctx["TRAVIS_BRANCH"].split(".")[0]
    ctx["GIT_ORG"] = "zeroincombenze"
    if odoo_major.isdigit():
        odoo_major = eval(odoo_major)
        ctx["ODOO_MAIN_VERSION"] = odoo_major
        ctx["TRAVIS_PYTHON_VERSION"] = get_pyver_4_odoo(odoo_major)
    else:
        ctx["ODOO_MAIN_VERSION"] = 0

    contents = section = ""
    with open(src, "r") as fd:
        for line in fd.read().split("\n"):
            if not line.startswith(" ") and line.endswith(":"):
                section = line.strip().split(":")[0]
                contents += ("%s\n" % line)
            elif line.startswith("  ") and line.endswith(":"):
                section = "%s.%s" % (section.split(".")[0], line.strip().split(":")[0])
                contents += ("%s\n" % line)
            else:
                contents += ("%s\n" % expand_macro(line, section, ctx))
    with open(tgt, "w") as fd:
        fd.write(contents)
    return 0


if __name__ == "__main__":
    exit(make_travis_conf())
