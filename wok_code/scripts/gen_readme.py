#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Documentation generator

This software generates the README.rst of OCB, repository and modules.
It also generates the index.html of the module.

Document may contains macro which format is {{macro_name}}.
Currently, the follow macros are recognized:

acknowledges     People acknowledge list
authors          Authors list
available_addons
branch           Odoo version for this repository/module
certifications   Certificates list
changelog        Changelog history (formerly history)
contact_us
contributors     Contributors list
configuration    How to configure
configuration_i18n
copyright_notes
description      English description of the repository/module (mandatory)
description_i18n Descrizione modulo/progetto in italiano (obbligatoria)
doc-URL          URL for button documentation
faq              FAQ
features         Features of the repository/module
GPL              same of gpl
git_orgid        Git organization
gpl              License name: may be A-GPL or L-GPL
grymb_image_*    Symbol imagae (suffix is a supported symbol name)
help-URL         URL for button help
known_issues     Known issues
installation     How to install
name             Module name (must be a python name)
now              Current timestamp
maintenance      Maintenance information
maturity
module_name
OCA-URL          URL to the same repository/module of OCA in github.com
oca_diff         OCA comparation
odoo_fver        Odoo full version (deprecated)
odoo_majver      Odoo major version; internal use to set some values
odoo_layer       Document layer, may be: ocb, module or repository
prerequisites    Installation prerequisites
prior_branch     Previous Odoo version of this repository/module
prior2_branch    Previous Odoo version of previous repository/module
proposals_for_enhancement
pypi_modules     pypi module list (may be set in __manifest__.rst)
pypi_sects       pypi section names to import (may be set in __manifest__.rst)
repos_name       Repository/project name
sponsor          Sponsors list
summary_i18n     Traduzione italiana di summary
submodules       Sub module list (only in pypi projects)
summary          Repository/module summary (CR are translated into spaces)
support          Support informations
today
translators      Translators list
troubleshooting  Troubleshooting information
try_me-URL       URL for button try-me
upgrade          How to upgrade
usage            How to usage

Documentation may contains some graphical symbols in format |symbol|.
Currently, follows symbols are recognized:

check
DesktopTelematico
en
exclamation
FatturaPA
halt
info
it
late
menu
no_check
right_do
same
warning
xml_schema
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# import ast
import os
import os.path as pth
import re
import sys
from datetime import datetime
from shutil import copyfile
from subprocess import call

from future import standard_library
from lxml import etree
from past.builtins import basestring

try:
    import license_mgnt
except ImportError:
    from wok_code.scripts import license_mgnt

from os0 import os0
from python_plus import unicodes, qsplit

try:
    from z0lib import z0lib
except ImportError:
    import z0lib
try:
    from clodoo.clodoo import build_odoo_param, transodoo
except ImportError:
    from clodoo import build_odoo_param, transodoo
try:
    from python_plus.python_plus import _b, _c, _u
except ImportError:
    from python_plus import _b, _c, _u
# import pdb
standard_library.install_aliases()


__version__ = "2.0.12"

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CLEAR = "\033[0;m"
RMODE = "rU" if sys.version_info[0] == 2 else "r"
GIT_USER = {
    "zero": "zeroincombenze",
    "oca": "OCA",
    "librerp": "LibrERP-network",
    "powerp": "PowERP-cloud",
    "didotech": "didotech",
}
DEFINED_SECTIONS = [
    "changelog",
    "description",
    "features",
    "oca_diff",
    "certifications",
    "prerequisites",
    "installation",
    "configuration",
    "upgrade",
    "support",
    "usage",
    "maintenance",
    "troubleshooting",
    "known_issues",
    "proposals_for_enhancement",
    "faq",
    "authors",
    "contributors",
    "translators",
    "acknowledges",
    "maintainer",
    "sponsor",
    "copyright_notes",
    "available_addons",
    "contact_us",
]
GROUPS = {
    "prerequisites": "getting_started",
    "installation": "getting_started",
    "configuration": "getting_started",
    "upgrade": "getting_started",
    "authors": "credits",
    "contributors": "credits",
    "translators": "credits",
    "acknowledges": "credits",
    "maintainer": "credits",
    "sponsor": "credits",
}
DEFINED_TAG = [
    "__manifest__",
    "name",
    # "nome"
    "summary",
    # "summary_i18n",
    "maturity",
    "module_name",
    "repos_name",
    "today",
]
DRAW_SECTIONS = [
    "description",
    "configuration",
    "usage",
]
MAGIC_SECTIONS = [
    "histories",
    "history-summary",
    "rdme_description",
    "rdme_authors",
    "rdme_contributors",
]
PYPI_SECTIONS_HDR = [
    "description",
    "features",
    "prerequisites",
    "installation",
    "configuration",
    "upgrade",
    "usage",
]
PYPI_SECTIONS_FOO = [
    "faq",
    "changelog",
    "support",
    "authors",
    "contributors",
]
DEF_HEADER = {
    "description": "Overview",
    "features": "Features",
    "getting_started": "Getting started",
    "prerequisites": "Prerequisites",
    "installation": "Installation",
    "configuration": "Configuration",
    "upgrade": "Upgrade",
    "faq": "FAQ",
    "changelog": "ChangeLog History",
    "support": "Support",
    "credits": "Credits",
    "authors": "Authors",
    "contributors": "Contributors",
}
# Search for old deprecated name for section
ALTERNATE_NAMES = {
    "changelog": "history",
    "__manifest__": "__init__",
    "description_i18n": "descrizione",
    "configuration": "configure",
    "summary_i18n": "sommario"
}
ZERO_PYPI_PKGS = "wok_code"
ZERO_PYPI_SECTS = "description usage"
LIST_TAG = ("authors", "contributors", "translators", "acknowledges", "maintainer")
DEFINED_GRYMB_SYMBOLS = {
    "it": [
        "flags/it_IT.png",
        "https://www.facebook.com/Zeroincombenze-"
        "Software-gestionale-online-249494305219415/",
    ],
    "en": [
        "flags/en_US.png",
        "https://www.facebook.com/Zeroincombenze-"
        "Software-gestionale-online-249494305219415/",
    ],
    "check": ["awesome/check.png", False],
    "no_check": ["awesome/no_check.png", False],
    "menu": ["awesome/menu.png", False],
    "right_do": ["awesome/right_do.png", False],
    "exclamation": ["awesome/exclamation.png", False],
    "late": ["awesome/late.png", False],
    "same": ["awesome/same.png", False],
    "warning": ["awesome/warning.png", False],
    "info": ["awesome/info.png", False],
    "halt": ["awesome/halt.png", False],
    "xml_schema": [
        "certificates/iso/icons/xml-schema.png",
        "https://github.com/zeroincombenze/grymb/"
        "blob/master/certificates/iso/scope/xml-schema.md",
    ],
    "DesktopTelematico": [
        "certificates/ade/icons/DesktopTelematico.png",
        "https://github.com/zeroincombenze/grymb/"
        "blob/master/certificates/ade/scope/Desktoptelematico.md",
    ],
    "FatturaPA": [
        "certificates/ade/icons/fatturapa.png",
        "https://github.com/zeroincombenze/grymb/"
        "blob/master/certificates/ade/scope/fatturapa.md",
    ],
}
EXCLUDED_MODULES = ["lxml"]
MANIFEST_ITEMS = (
    "name",
    "version",
    "category",
    "summary",
    "author",
    "website",
    "development_status",
    "license",
    "depends",
    "external_dependencies",
    "data",
    "qweb",
    "demo",
    "test",
    "maintainer",
    "installable",
    "active",
)
MANIFEST_ITEMS_REQUIRED = (
    "name",
    "version",
    "author",
    "website",
    "development_status",
    "license",
)
MANIFEST_ITEMS_OPTIONAL = (
    "qweb",
    "demo",
    "test",
    "external_dependencies",
    "active",
)
RST2HTML = {
    # &': '&amp;',
    "©": "&copy",
    "®": "&reg",
    "à": "&agrave;",
    "á": "&aacute;",
    "è": "&egrave;",
    "é": "&eacute;",
    "ì": "&igrave;",
    "í": "&iacute;",
    "ò": "&ograve;",
    "ó": "&oacute;",
    "ù": "&ugrave;",
    "ú": "&uacute;",
}
RST2HTML_GRYMB = {
    "|check|": '<span class="fa fa-check-square-o" style="color:green"/>',
    "|no_check|": '<span class="fa fa-close" style="color:red"/>',
    "|menu|": '<span class="fa fa-navicon"/>',
    '|right_do|': "<span class='fa fa-caret-right'/>",
    "|exclamation|": '<span class="fa fa-exclamation" style="color:orange"/>',
    "|late|": '<span class="fa fa-calendar-times-o" style="color:red"/>',
    "|same|": '<span class="fa fa-retweet"  style="color:blue"/>',
    "|warning|": '<span class="fa fa-exclamation-triangle" style="color:orange"/>',
    "|info|": '<span class="fa fa-info-circle" style="color:blue"/>',
    "|halt|": '<span class="fa fa-minus-circle" style="color:red"/>',
    "|circle|": '<span class="fa fa-circle"/>',
    "|xml_schema|": '<span class="fa fa-file-code-o"/>',
    "|DesktopTelematico|": '<span class="fa fa-wpforms"/>',
    "|FatturaPA|": '<span class="fa fa-euro"/>',
}
RE_PAT_DATE = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"


def __init__(ctx):
    transodoo.read_stored_dict(ctx)
    ctx["home_devel"] = ctx["home_devel"] or os.environ.get(
        "home_devel", pth.expanduser("~/devel")
    )
    ctx["odoo_root"] = pth.abspath(pth.join(ctx["home_devel"], ".."))
    ctx["path_name"] = pth.abspath(ctx["path_name"])
    if not ctx["product_doc"]:
        if "/pypi/" in ctx["path_name"] or ctx["path_name"].endswith("/tools"):
            ctx["product_doc"] = "pypi"
        else:
            ctx["product_doc"] = "odoo"
    if ctx["product_doc"] == "pypi":
        ctx["git_orgid"] = "zero"
        ctx["branch"] = ctx["odoo_vid"] if ctx["odoo_vid"] != "." else ""
        ctx["odoo_majver"] = 0
    else:
        ctx["branch"] = build_odoo_param(
            "FULLVER", odoo_vid=".", multi=True
        )
        if ctx["branch"] not in (
            "17.0",
            "16.0",
            "15.0",
            "14.0",
            "13.0",
            "12.0",
            "11.0",
            "10.0",
            "9.0",
            "8.0",
            "7.0",
            "6.1",
        ):
            ctx["branch"] = "12.0"
            if not ctx["suppress_warning"]:
                print_red_message(
                    "*** Invalid odoo version: please use -b switch (%s)"
                    % ctx["branch"]
                )
        ctx["odoo_majver"] = int(ctx["branch"].split(".")[0])
        if not ctx["git_orgid"]:
            ctx["git_orgid"] = build_odoo_param(
                "GIT_ORGID", odoo_vid=".", multi=True
            )

    if ctx["git_orgid"] not in ("zero", "oca", "powerp", "librerp", "didotech"):
        ctx["git_orgid"] = "zero"
        if not ctx["suppress_warning"] and ctx["product_doc"] != "pypi":
            print_red_message(
                "*** Invalid git-org: use -G %s or of zero|oca|librerp|didotech"
                % ctx["git_orgid"]
            )

    if ctx["odoo_layer"] not in ("ocb", "module", "repository"):
        if ctx["product_doc"] == "odoo":
            if (
                ctx["odoo_majver"] >= 10
                and pth.isfile(pth.join(ctx["path_name"], "__manifest__.py"))
                and pth.isfile(pth.join(ctx["path_name"], "__init__.py"))
            ):
                ctx["odoo_layer"] = "module"
            elif (
                ctx["odoo_majver"] < 10
                and pth.isfile(pth.join(ctx["path_name"], "__openerp__.py"))
                and pth.isfile(pth.join(ctx["path_name"], "__init__.py"))
            ):
                ctx["odoo_layer"] = "module"
            elif (
                ctx["odoo_majver"] >= 10
                and pth.isdir(pth.join(ctx["path_name"], "odoo"))
                and pth.isfile(pth.join(ctx["path_name"], "odoo-bin"))
            ):
                ctx["odoo_layer"] = "ocb"
            elif (
                ctx["odoo_majver"] < 10
                and pth.isdir(pth.join(ctx["path_name"], "openerp"))
                and (pth.isfile(pth.join(ctx["path_name"], "openerp-server")))
                or pth.isfile(
                    pth.join(ctx["path_name"], "server", "openerp-server")
                )
            ):
                ctx["odoo_layer"] = "ocb"
            else:
                ctx["odoo_layer"] = "repository"
        else:
            if pth.isfile(pth.join(ctx["path_name"], "../setup.py")):
                ctx["odoo_layer"] = "module"
            else:
                ctx["odoo_layer"] = "repository"

    # Read predefined section / tags
    for section in MAGIC_SECTIONS + DEFINED_SECTIONS + DEFINED_TAG:
        ctx[section] = ""
        ctx[section + "_i18n"] = ""
    ctx["pre_pat"] = r"\.\. +"

    if ctx["product_doc"] == "odoo":
        assure_docdir(ctx, "./readme")
        assure_docdir(ctx, "./static")
        if ctx["odoo_majver"] <= 7:
            assure_docdir(ctx, "./static/src")
            assure_docdir(ctx, "./static/src/img")
            ctx["img_dir"] = "./static/src/img"
        else:
            assure_docdir(ctx, "./static/description")
            ctx["img_dir"] = "./static/description"
    elif ctx["product_doc"] == "pypi":
        assure_docdir(ctx, "./egg-info")
        assure_docdir(ctx, "./docs")
    ctx["prior_lines"] = []
    ctx["in_fmt"] = ctx["out_fmt"] = "rst"
    ctx["pre_action"] = "write"
    ctx["pre_stack"] = []
    ctx["pre_do_else"] = []
    ctx["html_state"] = {"tag": ""}
    ctx["rst_state"] = ""


def chain_python_cmd(pyfile, args):
    cmd = [sys.executable]
    cmd.append(pth.join(pth.dirname(__file__), pyfile))
    for arg in args:
        cmd.append(arg)
    cmd = " ".join(cmd)
    return call(cmd, shell=True)


def assure_docdir(ctx, path):
    if not pth.isdir(path):
        print_red_message("*** Documentation directory %s not found!" % path)
        if ctx["force"] or ctx["write_authinfo"]:
            os.mkdir(path)


def print_red_message(text):
    print("%s%s%s" % (RED, text, CLEAR))


def print_green_message(text):
    print("%s%s%s" % (GREEN, text, CLEAR))


def create_def___manifest__(ctx):
    fn = "./readme/__manifest__.rst"
    with open(fn, "w") as fd:
        fd.write(".. $set lang %s\n" % ctx["lang"])
        fd.write(".. $set name.%s %s\n" % (ctx["lang"], ctx["module_name"]))
        fd.write(".. $set summary.%s Documentazione non disponibile\n" % ctx["lang"])
        fd.write(".. $set no_section_oca_diff 0\n")


def create_def_changelog(ctx):
    fn = "./readme/CHANGELOG.rst"
    with open(fn, "w") as fd:
        # Conventional date on Odoo Days (October, 1st Thursday)
        fd.write(
            "%s.0.1.0 (%s)\n" % (
                ctx["branch"],
                {
                    6: "2012-10-04",
                    7: "2013-10-03",
                    8: "2014-10-02",
                    9: "2015-10-01",
                    10: "2016-10-06",
                    11: "2017-10-05",
                    12: "2018-10-04",
                    13: "2019-10-03",
                    14: "2020-10-01",
                    15: "2021-10-07",
                    16: "2022-10-06",
                    17: "2023-10-05",
                }[ctx["odoo_majver"]]
            )
        )
        fd.write("~~~~~~~~~~~~~~~~~~~~~~~\n")
        fd.write("\n")
        fd.write("* Initial implementation / Implementazione iniziale\n")


def create_def_description(ctx):
    fn = "./readme/DESCRIPTION.rst"
    with open(fn, "w") as fd:
        fd.write("Missed description\n")


def create_def_description_i18n(ctx):
    fn = "./readme/DESCRIPTION.%s.rst" % ctx["lang"]
    with open(fn, "w") as fd:
        fd.write("Descrizione non disponibile\n")


def create_def_configuration(ctx):
    fn = "./readme/CONFIGURATION.rst"
    with open(fn, "w") as fd:
        fd.write("")


def create_def_configuration_i18n(ctx):
    fn = "./readme/CONFIGURATION.%s.rst" % ctx["lang"]
    with open(fn, "w") as fd:
        fd.write("")


def create_def_usage(ctx):
    fn = "./readme/USAGE.rst"
    with open(fn, "w") as fd:
        fd.write("")


def create_def_usage_i18n(ctx):
    fn = "./readme/USAGE.%s.rst" % ctx["lang"]
    with open(fn, "w") as fd:
        fd.write("")


def get_actual_fqn(ctx, path, filename):
    if "." in filename:
        fqn = pth.join(path, filename)
        if pth.isfile(fqn):
            return fqn
    if pth.basename(pth.abspath(path)) in ("readme", "egg-info", "docs"):
        docdirs = [pth.basename(pth.abspath(path))]
        path = pth.dirname(pth.abspath(path))
    else:
        docdirs = ("readme", "egg-info")
    for docdir in docdirs:
        if "." in filename:
            fqn = pth.join(path, docdir, filename)
            if pth.isfile(fqn):
                return fqn
        section, ext = pth.splitext(filename)
        SECTION = section.upper()
        if section.endswith("_i18n"):
            fqn = pth.join(path, docdir, SECTION[: -5] + "." + ctx["lang"] + ext)
            if pth.isfile(fqn):
                return fqn
            fqn = pth.join(path, docdir, section[: -5] + "." + ctx["lang"] + ext)
            if pth.isfile(fqn):
                return fqn
        fqn = pth.join(path, docdir, SECTION + ".csv")
        if pth.isfile(fqn):
            return fqn
        fqn = pth.join(path, docdir, SECTION + ".rst")
        if pth.isfile(fqn):
            return fqn
        section = section.lower()
        fqn = pth.join(path, docdir, section + ".csv")
        if pth.isfile(fqn):
            return fqn
        fqn = pth.join(path, docdir, section + ".rst")
        if pth.isfile(fqn):
            return fqn
        fqn = pth.join(path, docdir, section + ".txt")
        if pth.isfile(fqn):
            return fqn
    if section in ALTERNATE_NAMES:
        return get_actual_fqn(ctx, path, ALTERNATE_NAMES[section])
    docdir = "readme" if pth.isdir(pth.join(path, "readme")) else "egg-info"
    return pth.join(path, docdir, section.upper() + ".rst")


def get_fqn(ctx, src_path, filename):
    if src_path.startswith("./"):
        dirname = pth.join(
            ctx["path_name"], src_path[2:].replace("${p}", ctx["product_doc"]))
    else:
        dirname = pth.join(src_path.replace("${p}", ctx["product_doc"]))
    fqn = get_actual_fqn(ctx, dirname, filename)
    if (
            pth.basename(pth.dirname(fqn)) == "docs" and
            not pth.isdir(pth.dirname(fqn))
    ):
        fqn = get_actual_fqn(ctx, pth.dirname(pth.dirname(fqn)), filename)
    return fqn


def iter_template_path(ctx, debug_mode=None, body=None):
    for src_path in (
        ".",
        "./egg-info",
        "./readme",
        "./docs",
        "%s/pypi/tools/templates/${p}" % ctx["home_devel"],
        "%s/templates/${p}" % ctx["home_devel"],
        "%s/pypi/tools/templates" % ctx["home_devel"],
        "%s/templates" % ctx["home_devel"],
        "%s/venv/bin/templates/${p}" % ctx["home_devel"],
        "%s/venv/bin/templates" % ctx["home_devel"],
    ):
        if "/devel/pypi/tools/" in src_path and not debug_mode:
            continue
        elif "/devel/venv/bin/templates" in src_path and debug_mode:
            continue
        elif "/devel/templates" in src_path and debug_mode:
            continue
        if not body and (
            src_path.find("./docs") >= 0
            or src_path.find("./egg-info") >= 0
            or src_path.find("./readme") >= 0
        ):
            continue
        yield src_path


def get_template_fn(ctx, template, ignore_ntf=None):

    def search_tmpl(ctx, template, body):
        found = False
        if body:
            layered_template = "%s_%s" % (ctx["odoo_layer"], template)
            product_template = "%s_%s" % (ctx["product_doc"], template)
        else:
            layered_template = product_template = False
        for src_path in iter_template_path(
            ctx, debug_mode=ctx["debug_template"], body=body
        ):
            if body:
                fqn = get_fqn(ctx, src_path, product_template)
                if pth.isfile(fqn):
                    found = True
                    break

                fqn = get_fqn(ctx, src_path, layered_template)
                if pth.isfile(fqn):
                    found = True
                    break

            fqn = get_fqn(ctx, src_path, template)
            if pth.isfile(fqn):
                found = True
                break

            if template == "ACKNOWLEDGES.rst":
                fqn = get_fqn(ctx, src_path, "CONTRIBUTORS.rst")
                if pth.isfile(fqn):
                    found = True
                    break
        if not body and not found:
            fqn = ""
        return found, fqn

    body = False if (template.startswith("header_")
                     or template.startswith("footer_")) else True
    found, fqn = search_tmpl(ctx, template, body)
    if ctx["product_doc"] == "odoo" and not found and body and (
            ctx["force"] or ctx["write_authinfo"]):
        fct = "create_def_" + pth.splitext(template)[0].lower()
        if fct in globals():
            globals()[fct](ctx)
            found, fqn = search_tmpl(ctx, template, body)
    if not found:
        if not body:
            return fqn
        def_template = "default_" + template
        found, fqn = search_tmpl(ctx, def_template, False)
    if not found:
        if ignore_ntf:
            fqn = ""
        else:
            raise IOError("Template %s not found" % template)
    return fqn


def clean_summary(summary):
    return " ".join(x.strip() for x in summary.split("\n"))


def get_default_available_addons(ctx):
    if "addons_info" not in ctx:
        return ""
    text = ""
    text += "Avaiable Addons / Moduli disponibili\n"
    text += "------------------------------------\n"
    text += "\n"
    lol = 0
    for pkg in list(ctx["addons_info"].keys()):
        if len(pkg) > lol:
            lol = len(pkg)
    if lol > 36:
        lol = 36
    no_oca_diff = os0.str2bool(ctx.get("no_section_oca_diff", False), False)
    if no_oca_diff:
        fmt = "| %%-%d.%ds | %%-10.10s | %%-80.80s |\n" % (lol, lol)
        lne = fmt % ("", "", "")
    else:
        fmt = "| %%-%d.%ds | %%-10.10s | %%-10.10s | %%-80.80s |\n" % (lol, lol)
        lne = fmt % ("", "", "", "")
    lne = lne.replace(" ", "-").replace("|", "+")
    text += lne
    if no_oca_diff:
        text += fmt % ("Name / Nome", "Version", "Description / Descrizione")
    else:
        text += fmt % (
            "Name / Nome",
            "Version",
            "OCA Ver.",
            "Description / Descrizione",
        )
    text += lne
    for pkg in sorted(ctx["addons_info"].keys()):
        if not ctx["addons_info"][pkg].get("oca_installable", True):
            oca_version = "|halt|"
        elif (
            ctx["addons_info"][pkg]["version"] == ctx["addons_info"][pkg]["oca_version"]
        ):
            oca_version = "|same|"
        elif ctx["addons_info"][pkg]["oca_version"] == "N/A":
            oca_version = "|no_check|"
        else:
            oca_version = ctx["addons_info"][pkg]["oca_version"]
        if not ctx["addons_info"][pkg].get("installable", True):
            version = "|halt|"
        elif ctx["addons_info"][pkg]["version"] == "N/A":
            version = "|no_check|"
        else:
            version = ctx["addons_info"][pkg]["version"]
        if no_oca_diff:
            text += fmt % (pkg, version, ctx["addons_info"][pkg]["summary"])
        else:
            text += fmt % (
                pkg,
                version,
                oca_version,
                ctx["addons_info"][pkg]["summary"],
            )
        text += lne
    return text


def url_by_doc(ctx, url):
    if not url.startswith("http") and not url.startswith("/"):
        if ctx["rewrite_manifest"]:
            fmt = "/%s/static/src/img/%s"
            url = fmt % (ctx["module_name"], url)
        else:
            fmt = "https://raw.githubusercontent.com/%s/%s/%s/%s/static/"
            if ctx["odoo_majver"] < 8:
                fmt += "src/img/%s"
            else:
                fmt += "description/%s"
            url = fmt % (
                GIT_USER[ctx["git_orgid"]],
                ctx["repos_name"],
                ctx["branch"],
                ctx["module_name"],
                url,
            )
    return url


def torst(text):
    if text:
        text = text.replace("\a", "<").replace("\b", ">")
    return text


def totroff(text):
    return text


def rst2html(ctx, text, draw_button=False):
    def get_tag_image(ctx):
        html_tag = '<img src="%s"' % ctx["html_state"]["url"]
        for tag in ("alt", "target"):
            if tag in ctx["html_state"]:
                # style="width:18px;height:16px;"
                html_tag += (" %s=\"%s\"" % (tag, ctx["html_state"][tag]))
                ctx["html_state"] = {"tag": ""}
        styled = False
        for tag in ("width", "height"):
            if tag in ctx["html_state"]:
                if not styled:
                    # style="width:18px;height:16px;"
                    html_tag += " style=\""
                    styled = True
                html_tag += ("%s:%s;" % (tag, ctx["html_state"][tag]))
                ctx["html_state"] = {"tag": ""}
        if styled:
            html_tag += "max-width:1140px"
            html_tag += "\""
        ctx["html_state"] = {"tag": ""}
        html_tag += "/>"
        return html_tag

    def get_anchor(ctx, text):
        # Parse multi-line rst tags: <`>CODE<`> | <`>LINK<`__>
        start = text.find("`")
        stop = text.find("`__")
        stop2 = text.find("`", start + 1)
        while start >= 0 and (stop > start or stop2 > start):
            if stop2 > 0 and (stop2 < stop or stop < 0):
                text = "%s<code>%s</code>%s" % (text[0:start],
                                                text[start + 1: stop2],
                                                text[stop2 + 1:])
            else:
                txt = text[start + 1: stop]
                ii = txt.find("<")
                jj = txt.find(">")
                if ii < 0 and jj < 0:
                    txt = txt.replace("&lt;", "<").replace("&gt;", ">")
                    ii = txt.find("<")
                    jj = txt.find(">")
                if ii >= 0 and jj > ii:
                    url = txt[ii + 1: jj]
                    if url.startswith("http") and not url.startswith("https"):
                        url.replace("http", "https")
                    if url.startswith("http") and not url.endswith("/"):
                        url += "/"
                    if (stop + 3) < len(text):
                        text = '%s<a href="%s">%s</a>%s' % (
                            text[0:start],
                            url,
                            txt[0: ii - 1].strip(),
                            text[stop + 3:],
                        )
                    else:
                        text = '%s<a href="%s">%s</a>' % (
                            text[0:start],
                            url,
                            txt[0: ii - 1].strip(),
                        )
                elif stop >= 0 and txt.find("&lt;") < 0 and txt.find("&gt;"):
                    text = text[0:start] + text[start + 1: stop] + text[stop + 3:]
                else:
                    break
            start = text.find("`")
            stop = text.find("`__")
            stop2 = text.find("`", start + 1)
        return text

    def get_bold_italic(ctx, text):
        # Parse single-line rst tags: <*>BOLD<*> | <**>ITALIC<**>
        x = re.search(r"\*\*\w+\*\*", text)
        while x:
            text = "%s<b>%s</b>%s" % (text[0:x.start()],
                                      text[x.start() + 2: x.end() - 2],
                                      text[x.end() + 2:])
            x = re.search(r"\*\*\w+\*\*", text)

        x = re.search(r"\*\w+\*", text)
        while x:
            text = "%s<i>%s</i>%s" % (text[0:x.start()],
                                      text[x.start() + 1: x.end() - 1],
                                      text[x.end() + 1:])
            x = re.search(r"\*\w+\*", text)

        # Parse multi-line rst tags: <**>BOLD<**> ?
        start = text.find("**")
        stop = text.find("**", start + 2)
        while start > 0 and stop > start:
            text = "%s<b>%s</b>%s" % (text[0:start],
                                      text[start + 2: stop],
                                      text[stop + 2:])
            start = text.find("**")
            stop = text.find("**", start + 2)
        return text

    def get_navicon(ctx, text):
        stop = 0
        start = text.find("☰", stop)
        while start >= 0:
            text = text[0:start] + '<span class="fa fa-navicon"/>' + text[start + 1:]
            stop = start + 29
            start = text.find("☰", stop)
        return text

    if not text:
        return text
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\a", "<").replace("\b", ">")
    text = text.replace(" & ", " &amp; ")
    for t in list(RST2HTML_GRYMB.keys()):
        text = text.replace(t, RST2HTML_GRYMB[t])
    for token in DEFINED_GRYMB_SYMBOLS:
        tok = "|" + token + "|"
        start = text.find(tok)
        while start >= 0:
            value = '<img src="%s"/>' % expand_macro(ctx, "grymb_image_%s" % token)
            text = text[0:start] + value + text[start + len(tok):]
            start = text.find(tok)

    if draw_button:
        x = re.search(r"\[\w[\w ]+\w\]", text)
        while x:
            button_text = text[x.start() + 1:x.end() - 1]
            if len(button_text) <= 12:
                button_text = " " + button_text + " "
            button_text = button_text.replace(" ", "&#160;")
            text = ("%s<span style=\"color:white;background-color:#7C7BAD\">%s</span>%s"
                    % (text[0:x.start()],
                       button_text,
                       text[x.end():]))
            x = re.search(r"\[\w[\w ]+\w\]", text)
        x = re.search(r"\[`[\w ]+`\]", text)
        while x:
            tabbed_text = " " + text[x.start() + 2:x.end() - 2] + " "
            tabbed_text = tabbed_text.replace(" ", "&#160;")
            text = ("%s<span style=\"border-style:solid;border-width:1px 1px 0px 1px\">"
                    "%s</span>%s"
                    % (text[0:x.start()],
                       tabbed_text,
                       text[x.end():]))
            x = re.search(r"\[`[\w ]+`\]", text)

    def close_opened_tag(ctx, lines, lineno):
        force = lineno >= len(lines)
        if (
                not force
                and lines[lineno].startswith(" ")
                and ctx["html_state"]["tag"] in ("ul", "ol")
        ):
            endtag = "</li>"
            if lines[lineno - 1].endswith(endtag):
                lines[lineno - 1] = lines[lineno - 1][:-5]
            lines[lineno] += endtag
        elif force and ctx["html_state"]["tag"] == "ul":
            lines.append("</ul>")
            ctx["html_state"]["tag"] = ""
        elif not force and ctx["html_state"]["tag"] == "ul":
            lines.insert(lineno, "</ul>")
            lineno += 1
            ctx["html_state"]["tag"] = ""
        elif force and ctx["html_state"]["tag"] == "ol":
            lines.append("</ol>")
            ctx["html_state"]["tag"] = ""
        elif not force and ctx["html_state"]["tag"] == "ol":
            lines.insert(lineno, "</ol>")
            lineno += 1
            ctx["html_state"]["tag"] = ""
        elif force and ctx["html_state"]["tag"] == "code":
            lines.append("</code>")
            ctx["html_state"]["tag"] = ""
        elif (
                not force
                and not lines[lineno].startswith(" ")
                and ctx["html_state"]["tag"] == "code"
        ):
            lines.insert(lineno, "</code>")
            lineno += 1
            ctx["html_state"]["tag"] = ""
        return lineno

    def open_tag(ctx, lines, lineno, tag):
        if ctx["html_state"]["tag"] != tag:
            if tag == "ul":
                lines.insert(lineno, "<ul>")
                lineno += 1
            elif tag == "ol":
                lines.insert(lineno, "<ol>")
                lineno += 1
        ctx["html_state"]["tag"] = tag
        return lineno

    # Parse multi-line rst tags: <`>CODE<`> | <`>LINK<`__>
    text = get_anchor(ctx, text)

    # Parse single-line rst tags: <*>BOLD<*> | <**>ITALIC<**>
    text = get_bold_italic(ctx, text)

    # Parse menu line
    text = get_navicon(ctx, text)

    # Parse single line rst tags; remove trailing and tailing empty lines
    lines = text.split("\n")
    while len(lines) > 1 and not lines[-1]:
        del lines[-1]
    while len(lines) and not lines[0]:
        del lines[0]

    ctx["html_state"] = {"tag": ""}
    ctx["html_state"]["open_para"] = 0
    lineno = 0
    while lineno < len(lines):
        lineno = close_opened_tag(ctx, lines, lineno)
        if not lines[lineno].startswith(".. "):
            if ctx["html_state"]["tag"] in ("image", "figure"):
                x = re.match(r" +:(alt|target|width|height):", lines[lineno])
                if x:
                    ctx["html_state"][lines[lineno][x.start():x.end()].strip(
                        )[1: -1]] = lines[lineno][x.end():].strip()
                    del lines[lineno]
                    continue
                lines.insert(lineno, get_tag_image(ctx))
            elif re.match(r"^ *\+(-+\+)+ *$", lines[lineno]):
                if ctx["html_state"]["tag"] != "table":
                    lines[lineno] = (
                        '<table style="width:100%; padding:2px; '
                        'border-spacing:2px; text-align:left;"><tr>'
                    )
                    ctx["html_state"]["tag"] = "table"
                else:
                    lines[lineno] = "</tr><tr>"
            elif (
                    ctx["html_state"]["tag"] == "table"
                    and re.match(r" *\|.*\| *$", lines[lineno])
            ):
                cols = lines[lineno].split("|")
                del cols[0]
                row = ""
                for col in cols:
                    row += "</td><td>" + col.strip()
                row = row[5:-4]
                lines[lineno] = row
            elif ctx["html_state"]["tag"] == "table":
                lines[lineno - 1] = "%s</tr></table>" % lines[lineno - 1][:-4]
                ctx["html_state"]["tag"] = ""
                continue
            elif lines[lineno].startswith("* "):
                lineno = open_tag(ctx, lines, lineno, "ul")
                if re.match(".*&lt;http[^&]+&gt;$",  lines[lineno]):
                    lines[lineno] = "<li>%s</li>" % get_anchor(
                        ctx, "`%s`__" % lines[lineno][2:])
                else:
                    lines[lineno] = "<li>%s</li>" % lines[lineno][2:]
            elif lines[lineno].startswith("#. "):
                lineno = open_tag(ctx, lines, lineno, "ol")
                if re.match(".*&lt;http[^&]+&gt;$",  lines[lineno]):
                    lines[lineno] = "<li>%s</li>" % get_anchor(
                        ctx, "`%s`__" % lines[lineno][2:])
                else:
                    lines[lineno] = "<li>%s</li>" % lines[lineno][2:]
            elif not lines[lineno]:
                if ctx["html_state"]["tag"] == "Code":
                    lines[lineno] = "<code>"
                    ctx["html_state"]["tag"] = "code"
                elif ctx["html_state"]["open_para"]:
                    lines[lineno] = "</p><p align='justify'>"
                else:
                    lines[lineno] = "<p align='justify'>"
                    ctx["html_state"]["open_para"] += 1
            elif (
                re.match(r"^=+$", lines[lineno])
                and lineno > 0
                and len(lines[lineno]) == len(lines[lineno - 1])
            ):
                lines[lineno - 1] = "<h1>%s</h1>" % lines[lineno - 1]
                del lines[lineno]
                continue
            elif (
                re.match(r"^-+$", lines[lineno])
                and lineno > 0
                and len(lines[lineno]) == len(lines[lineno - 1])
            ):
                lines[lineno - 1] = "<h2>%s</h2>" % lines[lineno - 1]
                del lines[lineno]
                continue
            elif (
                re.match(r"^~+$", lines[lineno])
                and lineno > 0
                and len(lines[lineno]) == len(lines[lineno - 1])
            ):
                lines[lineno - 1] = "<h3>%s</h3>" % lines[lineno - 1]
                del lines[lineno]
                continue
            elif re.match(r"^:: *$", lines[lineno]):
                lines[lineno] = ""
                ctx["html_state"]["tag"] = "Code"
            elif lines[lineno] == "|":
                lines[lineno] = "<br/>"
        else:
            if ctx["html_state"]["tag"] == "table":
                lines[lineno - 1] = "%s</tr></table>" % lines[lineno - 1][:-4]
                ctx["html_state"]["tag"] = ""
            elif ctx["html_state"]["open_para"]:
                lines.insert(lineno, "</p>")
                ctx["html_state"]["open_para"] -= 1
            if is_rst_tag(ctx, lines[lineno], "image"):
                ctx["html_state"]["tag"] = "image"
                ctx["html_state"]["url"] = get_rst_tokens(
                    ctx, lines[lineno], "image")[0]
                del lines[lineno]
                continue
            elif is_rst_tag(ctx, lines[lineno], "figure"):
                ctx["html_state"]["tag"] = "figure"
                ctx["html_state"]["url"] = get_rst_tokens(
                    ctx, lines[lineno], "figure")[0]
                del lines[lineno]
                continue
        lineno += 1
    close_opened_tag(ctx, lines, lineno)
    if ctx["html_state"]["tag"] == "image":
        lines.append(get_tag_image(ctx))
        ctx["html_state"] = {}
    elif ctx["html_state"]["tag"] == "figure":
        lines.append(get_tag_image(ctx))
        ctx["html_state"] = {}
    elif ctx["html_state"]["tag"] == "table":
        lines[-1] = "</tr></table>"
    if ctx["html_state"]["open_para"]:
        lines.append("</p>")
        ctx["html_state"]["open_para"] -= 1
    return "\n".join(lines)


def expand_macro(ctx, token, default=None):
    if token[0:12] == "grymb_image_" and token[12:] in DEFINED_GRYMB_SYMBOLS:
        value = (
            "https://raw.githubusercontent.com/zeroincombenze/grymb"
            "/master/%s" % DEFINED_GRYMB_SYMBOLS[token[12:]][0]
        )
    elif token[0:10] == "grymb_url_" and token[10:] in DEFINED_GRYMB_SYMBOLS:
        value = DEFINED_GRYMB_SYMBOLS[token[10:]][1]
    elif token == "module_version":
        value = ctx["manifest"].get("version", "%s.0.1.0" % ctx["branch"])
        if ctx["branch"] and not value.startswith(ctx["branch"]):
            value = ctx["branch"] + "." + value.split(".", 2)[-1]
    elif token == "icon":
        value = url_by_doc(ctx, "icon.png")
    elif token == "GIT_URL_ROOT":
        value = "https://github.com/%s/%s" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
        )
    elif token == "GIT_URL":
        value = "https://github.com/%s/%s.git" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
        )
    elif token == "GIT_ORGID":
        value = ctx["git_orgid"]
    elif token == "badge-maturity":
        if ctx["development_status"].lower() == "alfa":
            value = "https://img.shields.io/badge/maturity-Alfa-red.png"
        elif ctx["development_status"].lower() == "beta":
            value = "https://img.shields.io/badge/maturity-Beta-yellow.png"
        elif ctx["development_status"].lower() in ("mature", "production/stable"):
            value = "https://img.shields.io/badge/maturity-Mature-green.png"
        else:
            value = "https://img.shields.io/badge/maturity-Alfa-black.png"
    elif token == "badge-gpl":
        if ctx["product_doc"] == "pypi":
            value = "AGPL"
        else:
            value = build_odoo_param("LICENSE", odoo_vid=ctx["branch"], multi=True)
        if value == "AGPL":
            value = "licence-%s--3-blue.svg" % value
        else:
            value = "licence-%s--3-7379c3.svg" % value
    elif token == "badge-status":
        value = "https://travis-ci.org/%s/%s.svg" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
        )
    elif token == "badge-coverage":
        value = "https://coveralls.io/repos/github/%s/%s/badge.svg" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
        )
    elif token == "badge-codecov":
        value = "https://codecov.io/gh/%s/%s/branch/%s/graph/badge.svg" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
            ctx["branch"],
        )
    elif token == "badge-oca-codecov":
        value = "https://codecov.io/gh/%s/%s/branch/%s/graph/badge.svg" % (
            "OCA",
            ctx["repos_name"],
            ctx["branch"],
        )
    elif token == "badge-doc":
        value = (
            "https://www.zeroincombenze.it/wp-content/"
            "uploads/ci-ct/prd/button-docs-%d.svg" % (ctx["odoo_majver"])
        )
    elif token == "badge-help":
        value = (
            "https://www.zeroincombenze.it/wp-content/"
            "uploads/ci-ct/prd/button-help-%s.svg" % (ctx["odoo_majver"])
        )
    elif token == "badge-try_me":
        value = (
            "https://www.zeroincombenze.it/wp-content/"
            "uploads/ci-ct/prd/button-try-it-%s.svg" % (ctx["odoo_majver"])
        )
    elif token == "maturity-URL":
        value = "https://odoo-community.org/page/development-status"
    elif token == "ci-travis-URL":
        value = "https://travis-ci.com/%s/%s" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
        )
    elif token == "coverage-URL":
        value = "https://coveralls.io/github/%s/%s" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
        )
    elif token == "codecov-URL":
        value = "https://codecov.io/gh/%s/%s/branch/%s" % (
            GIT_USER[ctx["git_orgid"]],
            ctx["repos_name"],
            ctx["branch"],
        )
    elif token == "codecov-oca-URL":
        value = "https://codecov.io/gh/%s/%s/branch/%s" % (
            "OCA",
            ctx["repos_name"],
            ctx["branch"],
        )
    elif token == "OCA-URL":
        value = "https://github.com/OCA/%s/tree/%s" % (ctx["repos_name"], ctx["branch"])
    elif token == "doc-URL":
        value = "https://wiki.zeroincombenze.org/en/Odoo/%s/dev" % (ctx["branch"])
    elif token == "help-URL":
        value = "https://wiki.zeroincombenze.org/it/Odoo/%s/man" % (ctx["branch"])
    elif token == "try_me-URL":
        if ctx["git_orgid"] == "oca":
            value = "http://runbot.odoo.com/runbot"
        else:
            value = "https://erp%s.zeroincombenze.it" % (ctx["odoo_majver"])
    elif token in ("gpl", "GPL"):
        if ctx["product_doc"] == "pypi":
            value = "AGPL"
        else:
            value = build_odoo_param("LICENSE", odoo_vid=ctx["branch"], multi=True)
        if token == "gpl":
            value = value.lower()
    elif token in ctx:
        value = ctx[token]
    elif default is not None:
        value = default
    else:
        value = (
            parse_local_file(ctx, "%s.csv" % token, ignore_ntf=True)
            or parse_local_file(ctx, "%s.rst" % token, ignore_ntf=True)
            or "Unknown %s" % token
        )
    return value


def expand_macro_in_line(ctx, line, out_fmt=None):
    """Expand content of macro like {{macro}}
    Function can return more than one line
    """
    out_fmt = out_fmt or ctx["out_fmt"]
    # All internal macros are in rst format
    in_fmt = "rst"
    # srctype = ctx.get("srctype", "")
    section = ""
    x = re.search(r"\{\{[^}]+\}\}", line)
    if x:
        tokens = line[x.start() + 2: x.end() - 2].split(":")
        if "{{" in tokens[0]:
            token = expand_macro_in_line(ctx, tokens[0], out_fmt=out_fmt)
            return expand_macro_in_line(
                ctx, line[: x.start()] + token + line[x.end():], out_fmt=out_fmt)
        for sect in DEFINED_SECTIONS + DEFINED_TAG:
            if tokens[0].startswith(sect):
                section = sect
                break
        value = expand_macro(ctx, tokens[0])
        if value is False or value is None:
            print_red_message("*** Invalid macro %s!" % tokens[0])
            value = ""
        if value and out_fmt in ("html", "troff"):
            value = parse_source(
                ctx, value, in_fmt=in_fmt, out_fmt=out_fmt, section=section
            )
            if "srctype" in ctx:
                del ctx["srctype"]
            return expand_macro_in_line(
                ctx, line[: x.start()] + value + line[x.end():], out_fmt=out_fmt)

        line = line[: x.start()] + value + line[x.end():]
        if len(value.split("\n")) > 1:
            value = parse_source(
                ctx, line, in_fmt=in_fmt, out_fmt=out_fmt, section=section
            )
            if "srctype" in ctx:
                del ctx["srctype"]
            return value
        return expand_macro_in_line(ctx, line, out_fmt=out_fmt)

    return line


def validate_condition(ctx, *args):
    val = ""
    in_cond = False
    i = 0
    while i < len(args):
        pad = "," if in_cond else " "
        if args[i][0].isalpha() or args[i][0] == "_":
            if args[i] == "defined":
                i += 1
                if args[i] in ctx and ctx[args[1]]:
                    val += "%s%s" % ("True", pad)
                else:
                    val += "%s%s" % ("False", pad)
            elif args[i] == "isfile":
                i += 1
                val += "%s%s" % (
                    pth.isfile(expand_macro(ctx, args[i], default=args[i])),
                    pad,
                )
            elif args[i] in ctx or args[i] in ("not", "in"):
                val += "%s%s" % (args[i], pad)
                if args[i] == "in":
                    in_cond = True
                    val += "("
            else:
                val += "'%s'%s" % (expand_macro(ctx, args[i], default=""), pad)
        else:
            val += "%s%s" % (args[i], pad)
        i += 1
    if in_cond:
        val += ")"
    try:
        res = eval(val, ctx)
    except BaseException:
        res = False
    return res


def is_rst_tag(ctx, line, tag):
    return re.match(ctx["pre_pat"] + tag + "::", line) if line else None


def get_rst_tokens(ctx, line, tag, maxsplit=None):
    return [
        x
        for x in qsplit(re.match(ctx["pre_pat"] + tag + "::(.*)?$",
                                 line).groups()[0],
                        "", maxsplit, enquote=True, strip=True)
        if x
    ]


def is_preproc_tag(ctx, line, tag):
    return re.match(ctx["pre_pat"] + r"\$" + tag + r"(\W.*)?$", line) if line else None


def get_preproc_tokens(ctx, line, tag, maxsplit=None):
    rex = ctx["pre_pat"] + r"\$" + tag + r"(\W.*)?$"
    return [
        x
        for x in qsplit(re.match(rex, line).groups()[0],
                        "", maxsplit, enquote=True, strip=True)
        if x
    ]


def is_preproc_line(ctx, line):
    is_preproc = False
    if is_preproc_tag(ctx, line, "if"):
        is_preproc = True
        if ctx["pre_action"] != "pass1":
            conditions = get_preproc_tokens(ctx, line, "if")
            res = validate_condition(ctx, *conditions)
            ctx["pre_stack"].append(res)
            ctx["pre_do_else"].append(res)
            if False in ctx["pre_stack"]:
                ctx["pre_action"] = "susp"
            else:
                ctx["pre_action"] = "write"
    elif is_preproc_tag(ctx, line, "elif"):
        is_preproc = True
        if ctx["pre_action"] != "pass1":
            conditions = get_preproc_tokens(ctx, line, "elif")
            if len(ctx["pre_stack"]):
                res = validate_condition(ctx, *conditions)
                ctx["pre_stack"][-1] = res
                if res:
                    ctx["pre_do_else"][-1] = res
                if False in ctx["pre_stack"]:
                    ctx["pre_action"] = "susp"
                else:
                    ctx["pre_action"] = "write"
            else:
                ctx["pre_action"] = "susp"
    elif is_preproc_tag(ctx, line, "else"):
        is_preproc = True
        if ctx["pre_action"] != "pass1":
            if len(ctx["pre_stack"]):
                ctx["pre_stack"][-1] = not ctx["pre_do_else"][-1]
                if False in ctx["pre_stack"]:
                    ctx["pre_action"] = "susp"
                else:
                    ctx["pre_action"] = "write"
            else:
                ctx["pre_action"] = "susp"
    elif is_preproc_tag(ctx, line, "fi"):
        is_preproc = True
        if ctx["pre_action"] != "pass1":
            if len(ctx["pre_stack"]):
                del ctx["pre_stack"][-1]
                del ctx["pre_do_else"][-1]
            if len(ctx["pre_stack"]):
                if False in ctx["pre_stack"]:
                    ctx["pre_action"] = "susp"
                else:
                    ctx["pre_action"] = "write"
            else:
                ctx["pre_action"] = "write"
    elif ctx["pre_action"] != "susp":
        if is_preproc_tag(ctx, line, "include"):
            is_preproc = True
        elif is_preproc_tag(ctx, line, "block"):
            is_preproc = True
        elif is_preproc_tag(ctx, line, "set"):
            is_preproc = True
        elif is_preproc_tag(ctx, line, "pypi_pages"):
            is_preproc = True
        elif is_preproc_tag(ctx, line, "merge_docs"):
            is_preproc = True
    return is_preproc


def parse_acknowledge_list(ctx, source):
    lines = source.split("\n")
    lno = 0
    while lno < len(lines):
        if not lines[lno]:
            del lines[lno]
            continue
        elif lines[lno][0] == "#":
            del lines[lno]
            continue
        names = lines[lno].split(" ")
        if names[0] and names[0][0] == "*":
            ctr = 0
            for i in range(3):
                if names[i] in ctx["contributors"]:
                    ctr += 1
            if ctr >= 2:
                del lines[lno]
                continue
        lno += 1
    return "\n".join(lines)


def compose_line_rst(ctx, line):
    ctx["prior_lines"] += line.split("\n")
    if re.match(ctx["pre_pat"] + "[^$]", line):
        # Start directive ".. DIRECTIVE"
        if ctx["rst_state"] == "cache":
            print_red_message("Wrong rst command: %s" % line)
        ctx["rst_state"] = "directive"
        if is_rst_tag(ctx, line, "image"):
            url = get_rst_tokens(ctx, line, "image")[0]
            line = line.replace(url, url_by_doc(ctx, url))
    elif ctx["rst_state"] == "directive":
        # End directive
        if not line.startswith(" "):
            ctx["rst_state"] = ""
    elif (
            ctx["prior_lines"][-1]
            and re.match(r"^(=+|-+|~+)$", ctx["prior_lines"][-1])
    ):
        # Title level
        # ***********
        if (
                ctx["rst_state"] == "cache"
                and len(ctx["prior_lines"]) > 2
                and re.match(r"^=+$", ctx["prior_lines"][-1])
                and re.match(r"^=+$", ctx["prior_lines"][-3])
        ):
            # ===========
            # Title level
            # ===========
            dash_line = ctx["prior_lines"][-1][0] * len(ctx["prior_lines"][-2])
            line = dash_line + "\n" + ctx["prior_lines"][-2] + "\n" + dash_line
            ctx["rst_state"] = ""
        elif len(ctx["prior_lines"]) > 1 and ctx["prior_lines"][-2]:
            dash_line = ctx["prior_lines"][-1][0] * len(ctx["prior_lines"][-2])
            line = dash_line
            ctx["rst_state"] = ""
            ctx["prior_lines"] = []
        elif re.match(r"^=+$", ctx["prior_lines"][-1]):
            ctx["rst_state"] = "cache"
            ctx["prior_lines"] = ctx["prior_lines"][-1:]
        else:
            ctx["rst_state"] = ""
    elif ctx["rst_state"] == "cache" and (not ctx["prior_lines"][-1]
                                          or len(ctx["prior_lines"]) > 2):
        line = "\n".join(ctx["prior_lines"])
        ctx["rst_state"] = ""
        ctx["prior_lines"] = []
    if len(ctx["prior_lines"]) > 3:
        ctx["prior_lines"] = ctx["prior_lines"][-3:]
    return (line + "\n") if ctx["rst_state"] != "cache" else ""


def tail(ctx, source, max_ctr=None, max_days=None, module=None):
    target = ""
    min_ctr = 2
    max_ctr = max(max_ctr or 24 if ctx["product_doc"] == "pypi" else 12, min_ctr)
    max_days = max_days or (1090 if ctx["product_doc"] == "pypi" else 720)
    left = ""
    ctr = 0
    for _lno, line in enumerate(source.split("\n")):
        if left:
            line = "%s%s" % (left, line)
            left = ""
        x = re.match(r"^[0-9]+\.[0-9]+\.[0-9]+", line)
        if x:
            ctr += 1
            if ctr > max_ctr:
                break
            x = re.search(RE_PAT_DATE, line)
            if (
                ctr > min_ctr
                and x
                and (
                    datetime.now()
                    - datetime.strptime(line[x.start() : x.end()], "%Y-%m-%d")
                ).days
                > max_days
            ):
                break
            if module:
                line = "%s: %s" % (module, line)
                left = "~" * (len(module) + 2)
        target += line
        target += "\n"
    return target


def sort_history(source):
    histories = {}
    hash = ""
    histories[hash] = ""
    for _lno, line in enumerate(source.split("\n")):
        x = re.match(r"^.*: [0-9]+\.[0-9]+\.[0-9]+", line)
        if x:
            x = re.search(RE_PAT_DATE, line)
            dt = line[x.start() : x.end()]
            module = line.split(": ")[0]
            hash = "%s %s" % (dt, module)
            histories[hash] = ""
        histories[hash] += line
        histories[hash] += "\n"
    target = ""
    for item in sorted(histories.keys(), reverse=True):
        target += histories[item]
        target += "\n"
    return target


def extract_imported_names(ctx):
    py_file = pth.join("./__init__.py")
    imported_names = []
    if not pth.isfile(py_file):
        print_red_message("Python file %s not found!" % py_file)
        print()
    else:
        with open(py_file, "r") as fd:
            for ln in fd.read().split("\n"):
                if re.match(r"^ *from \. import", ln):
                    tokens = ln.strip().split()
                    name = tokens[3]
                    if len(tokens) == 4 and name not in ("scripts",
                                                         "travis",
                                                         "_travis"):
                        imported_names.append(name)
    return imported_names


def write_automodule(ctx):
    def write_1_automodule(ctx, name):
        fqn = "%s.%s" % (ctx["module_name"], name)
        ctx["contents"] += ("\n" + fqn + "\n")
        ctx["contents"] += ("~" * len(fqn))
        ctx["contents"] += "\n\n"
        ctx["contents"] += ".. automodule:: %s\n" % fqn
    names = extract_imported_names(ctx)
    if names:
        rtd_fn = "./docs/rtd_automodule.rst"
        ctx["header"] = ctx["contents"] = ""
        for name in names:
            write_1_automodule(ctx, name)
        if pth.isfile("./testenv/testenv.py"):
            write_1_automodule(ctx, "testenv")
        contents = parse_local_file(
            ctx, "rtd_template_automodule.rst", section="usage")
        with open(rtd_fn, "w") as fd:
            fd.write(contents)
        if "contents" in ctx:
            del ctx["contents"]
        return "   rtd_automodule\n"
    return ""


def load_subsection(ctx, fn, section, sub):
    fqn = pth.join("./egg-info", fn)
    with open(fqn, "r") as fd:
        ctx["contents"] = fd.read()
    return write_rtd_file(ctx,
                          section,
                          header="Digest of " + sub,
                          fn=pth.join("docs", "rtd_" + fn),
                          sub=sub)


def write_rtd_file(ctx, section, header=None, fn=None, sub=None):
    name = GROUPS.get(section, section)
    rtd_fn = fn or "./docs/rtd_" + name + ".rst"
    if not ctx.get("contents") and not ctx.get(section):
        if pth.isfile(rtd_fn):
            os.unlink(rtd_fn)
        return ""
    ctx["header1"] = header or DEF_HEADER.get(name, name.title())
    if name == section:
        ctx["header2"] = ""
        with open(rtd_fn, "w") as fd:
            fd.write(parse_local_file(
                ctx, "rtd_template.rst", section=section))
    else:
        if not ctx[name]:
            ctx[name] = (ctx["header1"] + "\n")
            ctx[name] += ("=" * len(ctx["header1"]))
            ctx[name] += "\n"
        ctx["header2"] = DEF_HEADER.get(section, section.title())
        ctx[name] += ("\n" + ctx["header2"] + "\n")
        ctx[name] += ("-" * len(ctx["header2"]))
        ctx[name] += "\n\n"
        ctx[name] += ctx[section]
    if "contents" in ctx:
        del ctx["contents"]
    ctx["header1"] = ""
    return ("   rtd_%s_%s\n" % (section, sub)
            if sub
            else "   rtd_%s\n" % section if name == section else "")


def write_rtd_group(ctx, name):
    if not ctx[name]:
        return ""
    rtd_fn = "./docs/rtd_" + name + ".rst"
    ctx["contents"] = ctx[name]
    ctx["header1"] = ctx["header2"] = ""
    with open(rtd_fn, "w") as fd:
        fd.write(parse_local_file(ctx, "rtd_template.rst"))
    ctx[name] = ""
    return "   rtd_%s\n" % name


def parse_include(ctx, section, line, in_fmt=None, out_fmt=None):
    filename = get_preproc_tokens(ctx, line, "include")[0]
    text = parse_local_file(
        ctx, filename, in_fmt=in_fmt, out_fmt=out_fmt, section=section)
    if in_fmt == "rst":
        text = compose_line_rst(ctx, text)
    return text + "\n" if text else ""


def parse_block(ctx, section, line, in_fmt=None):
    blockname = get_preproc_tokens(ctx, line, "block")[0]
    if ctx.get(blockname):
        if in_fmt == "rst":
            text = compose_line_rst(ctx, ctx[blockname])
        else:
            text = ctx[blockname]
    elif ctx.get(section):
        if in_fmt == "rst":
            text = compose_line_rst(ctx, ctx[section])
        else:
            text = ctx[section]
    else:
        print_red_message("NO BLOCK '%s' FOUND" % blockname)
    return text


def parse_set(ctx, section, line):
    tokens = get_preproc_tokens(ctx, line, "set", maxsplit=2)
    if "." in tokens[0]:
        if tokens[0].endswith(".%s" % ctx["lang"]):
            name = tokens[0].split(".")[0] + "_i18n"
            value = tokens[1] if len(tokens) > 1 else ""
            ctx[name] = value
    else:
        name = tokens[0]
        value = tokens[1] if len(tokens) > 1 else ""
        ctx[name] = value
    return ""


def parse_pypi_packges(ctx):
    # Input format is RST
    target = "\n"
    files = os.listdir("./egg-info")
    submodules = {}
    for fn in sorted(files):
        sub, ext = pth.splitext(fn)
        if ext != ".rst":
            continue
        sub = sub.lower()
        for section in PYPI_SECTIONS_HDR:
            if not sub.startswith(section + "_") or sub == section:
                continue
            sub = sub[len(section) + 1:]
            if sub not in submodules:
                submodules[sub] = [fn]
            else:
                submodules[sub].append(fn)
    groups = {}
    for section in DEFINED_SECTIONS:
        if section in GROUPS:
            name = GROUPS[section]
            if name not in groups:
                groups[name] = []
                ctx[name] = ""
            groups[name].append(section)
    for section in PYPI_SECTIONS_HDR:
        target += write_rtd_file(ctx, section)
    for name in groups.keys():
        target += write_rtd_group(ctx, name)
    if submodules:
        for sub in sorted(list(submodules.keys())):
            for section in PYPI_SECTIONS_HDR:
                for fn in submodules[sub]:
                    if section not in fn.lower():
                        continue
                    target += load_subsection(ctx, fn, section, sub)
    target += write_automodule(ctx)
    for section in PYPI_SECTIONS_FOO:
        target += write_rtd_file(ctx, section)
    for name in groups.keys():
        target += write_rtd_group(ctx, name)
    target += "\n"
    return target


def parse_merge_docs(ctx):
    for module in ctx["pypi_modules"].split(" "):
        target = ""
        # Up to global pypi root
        module_dir = pth.abspath(
            pth.join(os.getcwd(), "..", "..")
        )
        while pth.isdir(pth.join(module_dir, module)):
            # down to module root
            module_dir = pth.join(module_dir, module)
        if pth.isdir(pth.join(module_dir, "docs")):
            for name in ctx["pypi_sects"].split(" "):
                name = "rtd_%s" % name
                src = pth.join(module_dir, "docs", "%s.rst" % name)
                if pth.isfile(src):
                    tgt = pth.join(
                        ".", "pypi_%s_%s.rst" % (module, name)
                    )
                    copyfile(src, tgt)
                    target += "\n   pypi_%s_%s" % (module, name)
            target += "\n"
    return target


def parse_line(ctx, line, in_fmt=None, out_fmt=None, section=None):
    is_preproc = is_preproc_line(ctx, line)
    if ctx["pre_action"] == "susp":
        return ""
    if is_preproc:
        if is_preproc_tag(ctx, line, "include"):
            line = parse_include(
                ctx, section, line, in_fmt=in_fmt, out_fmt=out_fmt)
        elif is_preproc_tag(ctx, line, "block"):
            line = parse_block(ctx, section, line, in_fmt=in_fmt)
        elif is_preproc_tag(ctx, line, "set"):
            parse_set(ctx, section, line)
        elif is_preproc_tag(ctx, line, "pypi_pages"):
            line = parse_pypi_packges(ctx)
        elif is_preproc_tag(ctx, line, "merge_docs"):
            line = parse_merge_docs(ctx)
        else:
            line = ""
    else:
        lines = expand_macro_in_line(ctx, line, out_fmt=out_fmt).split("\n")
        if len(lines) > 1:
            target = ""
            for text in lines:
                target += parse_line(
                    ctx, text, in_fmt=in_fmt, out_fmt=out_fmt, section=section)
            return target
        line = lines[0]
        if (
                section == "changelog"
                and ctx["product_doc"] == "odoo"
                and ctx["branch"]
                and re.search(RE_PAT_DATE, line)
                and not line.startswith(ctx["branch"])
        ):
            line = ctx["branch"] + "." + ctx["branch"].split(".", 1)[1]
        if in_fmt == "rst":
            line = compose_line_rst(ctx, line)
        else:
            line += "\n"
    return line


def parse_source(ctx, source, in_fmt=None, out_fmt=None, section=None):
    out_fmt = out_fmt or ctx["out_fmt"]
    in_fmt = in_fmt or ctx["in_fmt"]
    while source.startswith("\n"):
        source = source[1:]
    while source.endswith("\n\n"):
        source = source[:-1]
    target = ""
    for line in source.split("\n"):
        target += parse_line(ctx, line, in_fmt=in_fmt, out_fmt=out_fmt, section=section)
    if in_fmt == "rst" and out_fmt == "html":
        target = rst2html(
            ctx, target,
            draw_button=any([x
                             for x in DRAW_SECTIONS
                             if (section and section.startswith(x))]))
    elif in_fmt == "rst" and out_fmt == "troff":
        target = totroff(target)
    else:
        target = torst(target)
    while target.endswith("\n\n"):
        target = target[:-1]
    if target and not target.endswith("\n"):
        target += "\n"
    if ctx["pre_action"] != "write":
        print_red_message("Documentation writing suspended by block!")
        ctx["pre_action"] = "write"
        ctx["pre_stack"] = []
        ctx["pre_do_else"] = []
    if ctx["rst_state"]:
        if ctx["rst_state"] == "cache":
            print_red_message("Wrong block formatting: some date will be lost!")
        ctx["rst_state"] = ""
    if ctx["html_state"]["tag"]:
        print_red_message("HTML formatting error!")
        print_red_message("Wrong block formatting: some date will be lost!")
        ctx["html_state"] = {"tag": ""}

    return target


def load_hdr_foo(ctx, filename):
    fqn = get_template_fn(ctx, "header_" + filename)
    hdr_foo = ""
    if fqn:
        fd = open(fqn, RMODE)
        hdr_foo = _u(fd.read())
        fd.close()
        if len(hdr_foo) and ctx["trace_file"]:
            mark = '.. !! from "%s"\n\n' % fqn
            hdr_foo = mark + hdr_foo
    return hdr_foo


def parse_local_file(
    ctx, filename, ignore_ntf=None, in_fmt=None, out_fmt=None, section=None
):
    if not in_fmt:
        if filename.endswith(".rst"):
            in_fmt = "rst"
        elif filename.endswith(".html"):
            in_fmt = "html"
        elif filename.endswith(".troff"):
            in_fmt = "troff"
        else:
            in_fmt = ctx["in_fmt"]
    out_fmt = out_fmt or ctx["out_fmt"]
    fqn = get_template_fn(ctx, filename, ignore_ntf=ignore_ntf)
    if not fqn:
        base, ext = pth.splitext(filename)
        action = "get_default_%s" % base
        if action in list(globals()):
            return parse_source(
                ctx, globals()[action](ctx), out_fmt=out_fmt, section=section)
        return ""

    if fqn.endswith(".csv"):
        fqn_csv = fqn
        fqn = fqn_csv.replace(".csv", ".rst")
        remove_fqn = not pth.isfile(fqn)
    elif fqn.endswith(".rst"):
        fqn_csv = fqn.replace(".rst", ".csv")
        remove_fqn = False
    else:
        fqn_csv = ""
        remove_fqn = False
    if fqn_csv and pth.isfile(fqn_csv):
        args = [
            "-b", ctx["branch"],
            "-S" if ctx["product_doc"] == "pypi" else "",
            "-q",
            fqn_csv,
            fqn
        ]
        chain_python_cmd("cvt_csv_2_rst.py", args)
    if ctx["opt_verbose"]:
        print("Reading %s" % fqn)
    if section:
        ctx["%s_filename"] = fqn
    with open(fqn, RMODE) as fd:
        source = _u(fd.read())
    if remove_fqn:
        os.unlink(fqn)
    if not source and section == "acknowledges":
        source1 = parse_source(
            ctx, source.replace("branch", "prior_branch"),
            in_fmt=in_fmt, out_fmt=out_fmt, section=section
        )
        source2 = parse_source(
            ctx, source.replace("branch", "prior2_branch"),
            in_fmt=in_fmt, out_fmt=out_fmt, section=section
        )
        source = parse_acknowledge_list(
            ctx, "\n".join(set(source1.split("\n")) | set(source2.split("\n")))
        )
    if source and section == "changelog":
        source = tail(ctx, source)
        if ctx["odoo_layer"] == "module":
            ctx["history-summary"] = source
    if source:
        if ctx["trace_file"]:
            mark = '.. !! from "%s"\n\n' % filename
            source = mark + source
        source = load_hdr_foo(ctx, filename) + source + load_hdr_foo(ctx, filename)
    return parse_source(ctx, source, in_fmt=in_fmt, out_fmt=out_fmt, section=section)


def read_manifest_file(ctx, manifest_path, force_version=None):
    try:
        with open(manifest_path, RMODE) as fd:
            manifest = eval(fd.read())
    except (ImportError, IOError, SyntaxError):
        raise Exception("Wrong manifest file %s" % manifest_path)
    if force_version:
        manifest["version"] = adj_version(ctx, manifest.get("version", ""))
    return unicodes(manifest)


def fake_setup(**kwargs):
    globals()["setup_args"] = kwargs


def read_history(ctx, fqn, module=None):
    if module:
        with open(fqn, RMODE) as fd:
            ctx["histories"] += tail(ctx, _u(fd.read()), max_days=60, module=module)
    with open(fqn, RMODE) as fd:
        ctx["history-summary"] += tail(
            ctx, _u(fd.read()), max_ctr=1, max_days=30, module=module
        )


def read_setup(ctx):
    if ctx["product_doc"] == "pypi":
        MANIFEST_LIST = ("../setup.py", "./setup.py")
    else:
        MANIFEST_LIST = ("./setup.py",)
    for manifest in MANIFEST_LIST:
        manifest_filename = pth.abspath(pth.join(ctx["path_name"], manifest))
        if pth.isfile(manifest_filename):
            break
        manifest_filename = ""
    if manifest_filename:
        if ctx["odoo_layer"] == "module" and ctx["rewrite_manifest"]:
            complete_setup(ctx, manifest_filename)
        with open(manifest_filename, RMODE) as fd:
            content = fd.read()
            content = re.sub(r"setup *\(", "fake_setup(", content)
            if (
                "README.rst" in content
                and not pth.isfile("../README.rst")
                and not pth.isfile("README.rst")
            ):
                with open("../README.rst", "w"):
                    pass
            if pth.isfile("../README.rst"):
                content = content.replace("README.rst", "../README.rst")
            exec(_b(content))
            ctx["manifest"] = globals()["setup_args"]
        ctx["manifest_filename"] = manifest_filename
    else:
        if not ctx["suppress_warning"]:
            print_red_message("*** Warning: manifest file not found!")
        ctx["manifest"] = {}
    ctx["history-summary"] = ""
    if ctx["odoo_layer"] == "repository":
        ctx["histories"] = ""
        for root, dirs, _files in os.walk("../"):
            for dir in dirs:
                if dir == "tools":
                    continue
                fqnn = get_fqn(
                    ctx, pth.join(root, dir, "egg-info"), "CHANGELOG.rst")
                if pth.isfile(fqnn):
                    read_history(ctx, fqnn, module=pth.basename(dir))

        ctx["histories"] = sort_history(ctx["histories"])
        ctx["history-summary"] = sort_history(ctx["history-summary"])
    else:
        fqnn = get_fqn(
            ctx, pth.join(".", "egg-info"), "CHANGELOG.rst")
        if pth.isfile(fqnn):
            with open(fqnn, RMODE) as fd:
                read_history(ctx, fqnn)


def read_manifest(ctx):
    if ctx["odoo_layer"] != "module":
        ctx["manifest"] = {}
        return
    if ctx["odoo_majver"] >= 10:
        MANIFEST_LIST = ("__manifest__.py", "__openerp__.py")
    else:
        MANIFEST_LIST = ("__openerp__.py",)
    for manifest in MANIFEST_LIST:
        manifest_filename = pth.join(ctx["path_name"], manifest)
        if pth.isfile(manifest_filename):
            break
        manifest_filename = ""
    if manifest_filename:
        ctx["manifest"] = read_manifest_file(ctx, manifest_filename, force_version=True)
        ctx["manifest_filename"] = manifest_filename
    else:
        if not ctx["suppress_warning"]:
            print_red_message("*** Warning: manifest file not found!")
        ctx["manifest"] = {}


def adj_version(ctx, odoo_version):
    if not odoo_version:
        odoo_version = "0.1.0"
    if odoo_version[0].isdigit():
        if not odoo_version.startswith(ctx["branch"]):
            odoo_version = "%s.%s" % (ctx["branch"], odoo_version)
    return odoo_version


def read_all_manifests(ctx, path=None, module2search=None):
    def valid_dir(dirname):
        if dirname.startswith(".") or dirname.startswith("__") or dirname == "setup":
            return False
        return True

    path = path or "."
    ctx["manifest"] = {}
    ctx["histories"] = ""
    ctx["history-summary"] = ""
    addons_info = {}
    local_modules = "l10n_%s" % ctx["lang"][0:2]
    if ctx["odoo_majver"] >= 10:
        manifest_file = "__manifest__.py"
    else:
        manifest_file = "__openerp__.py"
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if valid_dir(d)]
        # For OCB read just addons
        if module2search or ctx["odoo_layer"] != "ocb" or root.find("addons") >= 0:
            module_name = pth.basename(root)
            if module2search and module2search != module_name:
                continue
            # Ignore local modules
            if (
                not module2search
                and (
                    module_name.startswith("l10n_")
                    and not module_name.startswith(local_modules)
                )
                or module_name.startswith("test_")
            ):
                continue
            if manifest_file in files:
                fqn = pth.join(root, manifest_file)
                try:
                    addons_info[module_name] = read_manifest_file(
                        ctx, fqn, force_version=True
                    )
                    if "summary" not in addons_info[module_name]:
                        addons_info[module_name]["summary"] = addons_info[module_name][
                            "name"
                        ].strip()
                    else:
                        addons_info[module_name]["summary"] = clean_summary(
                            addons_info[module_name]["summary"]
                        )
                    addons_info[module_name]["oca_version"] = "N/A"
                    if root.find("__unported__") >= 0:
                        addons_info[module_name]["installable"] = False
                    if module2search:
                        break
                except KeyError:
                    pass
                fqn = get_fqn(
                    ctx, pth.join(".", "egg-info"), "CHANGELOG.rst")
                if pth.isfile(fqn):
                    with open(fqn, RMODE) as fd:
                        ctx["histories"] += tail(
                            ctx, _u(fd.read()), max_days=180, module=module_name
                        )
                        with open(fqn, RMODE) as fd:
                            ctx["history-summary"] += tail(
                                ctx,
                                _u(fd.read()),
                                max_ctr=1,
                                max_days=15,
                                module=module_name,
                            )
    if not module2search:
        if ctx["odoo_layer"] == "ocb":
            oca_root = "%s/oca%d" % (ctx["odoo_root"], ctx["odoo_majver"])
        else:
            oca_root = "%s/oca%d/%s" % (
                ctx["odoo_root"],
                ctx["odoo_majver"],
                ctx["repos_name"],
            )
        for root, dirs, files in os.walk(oca_root):
            dirs[:] = [d for d in dirs if valid_dir(d)]
            if ctx["odoo_layer"] != "ocb" or root.find("addons") >= 0:
                module_name = pth.basename(root)
                if (
                    ctx["odoo_layer"] == "ocb" and module_name[0:5] == "l10n_"
                ) or module_name[0:5] == "test_":
                    continue
                if manifest_file in files:
                    fqn = pth.join(root, manifest_file)
                    oca_manifest = read_manifest_file(ctx, fqn, force_version=True)
                    oca_version = oca_manifest["version"]
                    if module_name not in addons_info:
                        addons_info[module_name] = {}
                        if "summary" in oca_manifest:
                            addons_info[module_name]["summary"] = clean_summary(
                                oca_manifest["summary"]
                            )
                        else:
                            addons_info[module_name]["summary"] = oca_manifest[
                                "name"
                            ].strip()
                        addons_info[module_name]["version"] = "N/A"
                    addons_info[module_name]["oca_version"] = oca_version
                    if root.find("__unported__") >= 0:
                        addons_info[module_name]["oca_installable"] = False
                    else:
                        addons_info[module_name]["oca_installable"] = oca_manifest.get(
                            "installable", True
                        )
        ctx["histories"] = sort_history(ctx["histories"])
        ctx["history-summary"] = sort_history(ctx["history-summary"])
    ctx["addons_info"] = addons_info


def manifest_item(ctx, item):
    q = ctx["quote_with"]
    if (
            isinstance(ctx["manifest"][item], basestring)
            and ctx["manifest"][item] in ("True", "False")
    ):
        ctx["manifest"][item] = eval(ctx["manifest"][item])
    if (
            item in MANIFEST_ITEMS_OPTIONAL
            and item in ctx and (ctx[item] is False or ctx[item] == [])
    ):
        target = ""
    elif item in ("website", "maintainer"):
        target = '    %s%s%s: %s%s%s,\n' % (q, item, q, q, ctx[item], q)
    elif item == "author":
        text = ctx["manifest"][item]
        if len(text) < 70:
            target = '    %s%s%s: %s%s%s,\n' % (q, item, q, q, text, q)
        else:
            target = '    %s%s%s: (' % (q, item, q)
            authors = text.split(",")
            slice = []
            slice_len = 0
            comma = ""
            for auth in authors:
                slice_len += len(auth)
                if slice_len < 68:
                    slice.append(auth)
                    continue
                text = ",".join(slice)
                target += (q + comma + text + q + "\n")
                comma = ","
                slice = [auth]
                slice_len = len(auth)
            if slice:
                text = ",".join(slice)
                target += ("               " + q + comma + text + q + "\n")
            target = target[: -1] + "),\n"
    elif isinstance(ctx["manifest"][item], basestring):
        while ctx["manifest"][item].startswith("\n"):
            ctx["manifest"][item] = ctx["manifest"][item][1:]
        while ctx["manifest"][item].endswith("\n"):
            ctx["manifest"][item] = ctx["manifest"][item][:-1]
        ctx["manifest"][item] = ctx["manifest"][item].strip()
        if "\n" in ctx["manifest"][item]:
            text = ctx["manifest"][item].replace('"', "'")
            pfx = '    %s%s%s: """%s\n'
            lastline = len(text.split("\n")) - 1
            for ii, ln in enumerate(text.split("\n")):
                if pfx:
                    target = pfx % (q, item, q, ln)
                    pfx = ""
                elif ii < lastline:
                    target += "%s\n" % ln
                else:
                    target += '%s"""\n' % ln
        else:
            text = ctx["manifest"][item].replace('"', "'")
            target = '    %s%s%s: %s%s%s,\n' % (q, item, q, q, text, q)
    elif isinstance(ctx["manifest"][item], list):
        if len(ctx["manifest"][item]) == 0:
            target = ""
        elif len(ctx["manifest"][item]) == 1:
            target = '    %s%s%s: [%s%s%s],\n' % (
                q, item, q, q, ctx["manifest"][item][0], q)
        else:
            target = '    %s%s%s: [\n' % (q, item, q)
            for kk in ctx["manifest"][item]:
                if isinstance(kk, basestring):
                    text = kk.replace("'", '"')
                    target += '        %s%s%s,\n' % (q, text, q)
                else:
                    text = str(kk)
                    target += "        %s,\n" % text
            target += "    ],\n"
    else:
        text = str(ctx["manifest"][item])
        target = '    %s%s%s: %s,\n' % (q, item, q, text)
    return target


def read_dependecies_license(ctx):
    def_license = "LGPL-3" if ctx["odoo_majver"] > 8 else "AGPL-3"
    license = ctx["manifest"]["license"]
    if license == "AGPL-3":
        return
    saved_manifest = ctx["manifest"].copy()
    root = build_odoo_param("ROOT", odoo_vid=".", multi=True)
    for module in ctx["manifest"].get("depends", []):
        read_all_manifests(ctx, path=root, module2search=module)
        if module not in ctx["addons_info"]:
            if not ctx["suppress_warning"]:
                print_red_message(
                    "*** Unknow license of module %s: license may be invalid!" % module
                )
        elif (
            ctx["addons_info"][module].get("license", def_license) == "AGPL-3"
            and not ctx["suppress_warning"]
        ):
            print_red_message(
                "*** INVALID LICENSE %s: depending module <%s> is AGPL-3 ***"
                % (license, module)
            )
    ctx["manifest"] = saved_manifest


def manifest_contents(ctx):
    fqn = ctx["manifest_filename"]
    source = ""
    if fqn:
        with open(fqn, RMODE) as fd:
            source = _u(fd.read())
    target = ""
    for line in source.split("\n"):
        if not line or line[0] != "#":
            break
        target += line + "\n"
    target += "{\n"
    for item in MANIFEST_ITEMS:
        if item not in ctx["manifest"] and item in MANIFEST_ITEMS_REQUIRED:
            ctx["manifest"][item] = ctx[item]
        elif item == "depends":
            modules = []
            for module in ctx["manifest"].get(item, []):
                if ctx["from_version"] and ctx["branch"]:
                    new_module = transodoo.translate_from_to(
                        ctx,
                        "ir.module.module",
                        module,
                        ctx["from_version"],
                        ctx["branch"],
                        ttype="module",
                    )
                    if isinstance(new_module, (list, tuple)):
                        if module in new_module:
                            modules.append(module)
                        else:
                            module.update(new_module)
                    else:
                        modules.append(new_module)
                else:
                    modules.append(module)
            ctx["manifest"][item] = modules
        elif ctx.get(item):
            ctx["manifest"][item] = ctx[item]
        if item in ctx["manifest"]:
            target += manifest_item(ctx, item)
    for item in list(ctx["manifest"].keys()):
        if item != "description" and item not in MANIFEST_ITEMS:
            target += manifest_item(ctx, item)
    if ctx["odoo_majver"] < 8:
        text = parse_local_file(ctx, "readme_manifest.rst")
        target += "    'description': r'''%s''',\n" % text
    target += "}\n"
    return target


def xml_replace_text(ctx, root, item, text, pos=None):
    pos = pos or [1, 999]
    ctr = 0
    for element in root.iter():
        if element.tag == item:
            ctr += 1
            if ctr >= pos[0] and ctr <= pos[1]:
                element.text = text


def index_html_content(ctx, source):
    target = ""
    # title = "%s / %s" % (ctx["summary"], ctx["summary_i18n"])
    for section in source.split("\f"):
        try:
            root = etree.XML(section)
        except SyntaxError as e:
            print_red_message("***** Error %s *****" % e)
            continue
        # xml_replace_text(ctx, root, "h2", title)
        try:
            target += "\n%s" % _u(etree.tostring(root, pretty_print=True))
        except SyntaxError as e:
            print_red_message("***** Error %s *****" % e)
            target += section
    for t in list(RST2HTML.keys()):
        target = target.replace(t, RST2HTML[t])
    return target


def set_default_values(ctx):
    ctx["today"] = datetime.strftime(datetime.today(), "%Y-%m-%d")
    ctx["now"] = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
    if not ctx["branch"] or ctx["branch"] == ".":
        ctx["branch"] = ctx["manifest"].get("version", "")
    if ctx["manifest"].get("version", ""):
        if not ctx.get("odoo_fver"):
            ctx["odoo_fver"] = ctx["manifest"]["version"]
    # TODO: to remove early
    if not ctx.get("odoo_fver"):
        ctx["odoo_fver"] = ctx["branch"]
    if ctx["product_doc"] == "odoo":
        ctx["odoo_majver"] = int(ctx["odoo_fver"].split(".")[0])
        if not ctx.get("prior_branch"):
            pmv = ctx["odoo_majver"] - 1
            if pmv == 6:
                ctx["prior_branch"] = "%d.1" % pmv
            elif pmv > 6:
                ctx["prior_branch"] = "%d.0" % pmv
            if not ctx.get("prior2_branch"):
                pmv = ctx["odoo_majver"] - 2
                if pmv == 6:
                    ctx["prior2_branch"] = "%d.1" % pmv
                elif pmv > 6:
                    ctx["prior2_branch"] = "%d.0" % pmv
    else:
        releases = [int(x) for x in ctx["branch"].split(".")]
        if not ctx.get("prior_branch"):
            ctx["odoo_majver"] = releases[0]
            pmv = ctx["odoo_majver"] - 1
            ctx["prior_branch"] = "%d.%d" % (pmv, releases[1])
    if ctx["output_file"]:
        ctx["dst_file"] = ctx["output_file"]
    elif ctx["write_index"] and ctx["product_doc"] == "odoo":
        if pth.isdir("./static/description"):
            ctx["dst_file"] = "./static/description/index.html"
        else:
            ctx["dst_file"] = "./index.html"
        ctx["trace_file"] = False
    elif ctx["write_index"] and ctx["product_doc"] == "pypi":
        if pth.isdir("./docs"):
            ctx["dst_file"] = "./docs/index.rst"
        else:
            ctx["dst_file"] = "./index.rst"
    elif (
        ctx["product_doc"] == "odoo"
        and ctx["odoo_layer"] == "module"
        and ctx["rewrite_manifest"]
    ):
        ctx["dst_file"] = ctx["manifest_filename"]
    elif ctx["odoo_layer"] == "module" and ctx["write_man_page"]:
        ctx["dst_file"] = "page.man"
    elif pth.isfile("../setup.py"):
        ctx["dst_file"] = "../README.rst"
    else:
        ctx["dst_file"] = "./README.rst"
    if ctx["odoo_layer"] != "module":
        ctx["manifest"] = {"name": "repos_name", "development_status": "Alfa"}
    if ctx["product_doc"] == "odoo":
        ctx["development_status"] = (
            ctx["manifest"].get(
                "development_status", ctx.get("force_maturity", "Alpha")
            )
            or "Alpha"
        )
    else:
        ctx["development_status"] = "Alfa"
        for item in ctx["manifest"].get("classifiers", []):
            if item.startswith("Development Status"):
                ctx["development_status"] = item.split("-")[1].strip()
                break
    ctx["name"] = ctx["manifest"].get("name", ctx["module_name"].replace("_", " "))
    ctx["summary"] = (
        ctx["manifest"].get("summary", ctx["name"]).strip().replace("\n", " ")
    )
    ctx["zero_tools"] = (
        "`Zeroincombenze Tools <https://zeroincombenze-tools.readthedocs.io/>`__"
    )
    if ctx["odoo_layer"] == "ocb":
        ctx["local_path"] = "%s/%s" % (ctx["odoo_root"], ctx["branch"])
    elif ctx["odoo_layer"] == "repository":
        ctx["local_path"] = "%s/%s/%s/" % (
            ctx["odoo_root"],
            ctx["branch"],
            ctx["repos_name"],
        )
    else:
        ctx["local_path"] = "%s/%s/%s/" % (
            ctx["odoo_root"],
            ctx["branch"],
            ctx["repos_name"],
        )
    if ctx["product_doc"] == "odoo":
        ctx["src_icon"] = ctx["manifest"].get(
            "category", "").strip().split(" ")[0].lower() + ".png"


def setup_names(fn, email=None):
    if email == "name":
        with open(fn, RMODE) as fd:
            return ", ".join(
                [
                    x.split("*", 1)[1].split("<", 1)[0].strip()
                    if x.startswith("*")
                    else x.split("<", 1)[0].strip()
                    for x in fd.read().split("\n")
                    if x
                ]
            )
    elif email == "email":
        with open(fn, RMODE) as fd:
            return ", ".join(
                [
                    "<" + x.split("*", 1)[1].split("<", 1)[1].strip()
                    if x.startswith("*")
                    else "<" + x.split("<", 1)[1].strip()
                    for x in fd.read().split("\n")
                    if x
                ]
            )
    else:
        with open(fn, RMODE) as fd:
            return ", ".join(
                [
                    x.split("*", 1)[0].strip() if x.startswith("*") else x.strip()
                    for x in fd.read().split("\n")
                    if x
                ]
            )


def complete_setup(ctx, setup_fn):
    with open(setup_fn, RMODE) as fd:
        AUTH_RE = re.compile("^author *=")
        EMAIL_RE = re.compile("^author_email *=")
        SOURCE_ROOT = "https://github.com/zeroincombenze/tools"
        URL_RE = re.compile(r"^ +url=[\"']")
        SOURCE_URL_RE = re.compile("^source_url *=")
        SOURCE_URL = SOURCE_ROOT + "/tree/master/%s"
        DOC_URL_RE = re.compile("^doc_url *=")
        DOC_URL = "https://zeroincombenze-tools.readthedocs.io/en/latest/%s"
        CHANGELOG_RE = re.compile("^changelog_url *=")
        CHANGELOG_URL = SOURCE_ROOT + "/blob/master/%s/egg-info/CHANGELOG.rst"
        contents = ""
        for line in fd.read().split("\n"):
            if AUTH_RE.match(line):
                line = "author = \"%s\"" % setup_names(
                    "egg-info/CONTRIBUTORS.txt", email="name"
                )
            elif EMAIL_RE.match(line):
                line = "author_email = \"%s\"" % setup_names(
                    "egg-info/CONTRIBUTORS.txt", email="email"
                )
            elif URL_RE.match(line):
                line = line.split("=")[0] + ("=\"%s\"," % SOURCE_ROOT)
            elif SOURCE_URL_RE.match(line):
                line = "source_url = \"%s\"" % (SOURCE_URL % ctx["module_name"])
            elif DOC_URL_RE.match(line):
                line = "doc_url = \"%s\"" % (DOC_URL % ctx["module_name"])
            elif CHANGELOG_RE.match(line):
                line = "changelog_url = \"%s\"" % (CHANGELOG_URL % ctx["module_name"])
            contents += line
            contents += "\n"
    with open(setup_fn, "w") as fd:
        fd.write(contents)


def read_purge_readme(ctx, source):
    if source is None:
        return "", "", ""
    lines = source.split("\n")
    out_sections = {"description": "", "authors": "", "contributors": ""}
    cur_sect = ""
    ix = 0
    while ix < len(lines):
        line = lines[ix]
        next_line = lines[ix + 1] if ix < (len(lines) - 1) else ""
        if is_rst_tag(ctx, line, "contents"):
            out_sections = {"description": "", "authors": "", "contributors": ""}
            ix += 1
            continue
        elif (
            re.match(r"^[A-Za-z]\w\w+", line)
            and re.match("^[-=~]+$", next_line)
        ):
            cur_sect = line.split("/")[0].strip().lower()
            ix += 2
            if (
                    cur_sect == "overview"
                    or cur_sect.startswith(ctx["module_name"] + " ")
            ):
                cur_sect = "description"
                out_sections[cur_sect] = ""
            continue
        elif (
            re.match(r"^\|icon\| [A-Za-z]\w\w+", line)
            and re.match("^=+$", next_line)
        ):
            out_sections = {"description": "", "authors": "", "contributors": ""}
            ix += 1
            continue
        elif re.match("^-+$", line) and not next_line:
            cur_sect = ""
        elif (
            re.match(r"^\|$", line)
            and re.match(r"^\|$", next_line)
        ):
            cur_sect = ""
        elif re.match(r"^\* *[|.:]", line):
            cur_sect = ""

        if cur_sect in list(out_sections.keys()):
            out_sections[cur_sect] += (line + "\n")
        ix += 1
    for sect in list(out_sections.keys()):
        while (
                out_sections[sect].startswith("\n")
                or out_sections[sect].startswith(" \n")
                or out_sections[sect].startswith("|\n")
                or out_sections[sect].startswith("|it| N/D")
                or out_sections[sect].startswith("|en| N/A")
                or out_sections[sect].startswith("|en| No info available")
        ):
            out_sections[sect] = out_sections[sect].split("\n", 1)[1]
        while out_sections[sect].endswith("\n\n"):
            out_sections[sect] = out_sections[sect][:-1]
    return (
        out_sections["description"],
        out_sections["authors"],
        out_sections["contributors"],
    )


def merge_lists(ctx, left, right):
    """left (str), right(list)"""
    lefts = []
    for ln in left.split(",") if "," in left and "\n" not in left else left.split("\n"):
        if ln:
            res = ctx["license_mgnt"].extract_info_from_line(ln, force=True)
            if res[1]:
                lefts.append(res)
    if isinstance(right, (list, tuple)):
        rights = right
    else:
        rights = []
        for ln in (
                right.split(",")
                if "," in right and "\n" not in right else right.split("\n")):
            if ln:
                res = ctx["license_mgnt"].extract_info_from_line(ln, force=True)
                if res[1]:
                    rights.append(res)
    for right_item in rights:
        found = False
        for left_item in lefts:
            if (
                    (right_item[0] and right_item[0] == left_item[0])
                    or (right_item[1] and right_item[1] == left_item[1])
                    or (right_item[2] and right_item[2] == left_item[2])
                    or (right_item[3] and right_item[3] == left_item[3])
            ):
                found = True
                for ix in range(3):
                    if not left_item[ix] and right_item[ix]:
                        if isinstance(left_item, tuple):
                            left_item = list(left_item)
                        left_item[ix] = right_item[ix]
                break
        if not found:
            lefts.append(right_item)
    return lefts


def item_2_set(item, field=None):
    if isinstance(item, dict):
        return set([x[0] for x in item.values()])
    return set([x[field] for x in item])


def item_2_test(ctx, section):
    if section == "authors":
        ctx["manifest"]["author"] = ",".join([x[1] for x in ctx[section]])
        ctx[section] = "\n".join(
            ["* %s <%s>" % ((x[1], x[2])) for x in ctx[section]])
    elif section == "maintainer":
        ctx[section] = "%s <%s>" % (ctx[section][0][1],
                                    ctx[section][0][3] or ctx[section][0][2])
        ctx["manifest"]["author"] = ctx[section]
    else:
        ctx[section] = "\n".join(
            ["* %s <%s>" % ((x[1], x[3] or x[2])) for x in ctx[section]])
    if ctx[section] and not ctx[section].endswith("\n"):
        ctx[section] += "\n"


def write_rst_file(ctx, path, section):
    fqn = get_actual_fqn(ctx, path, section)
    force_write = False
    if (
        section == "changelog"
        and ctx["odoo_layer"] in ("repository", "ocb")
        and ctx["histories"]
    ):
        ctx[section] = ctx["histories"]
        force_write = True
    elif (
        section in ("authors", "contributors")
    ):
        force_write = True
    if force_write or pth.isfile(fqn):
        with open(fqn, "w") as fd:
            if section == "changelog" and not ctx[section]:
                header = "%s (%s)" % (
                    ctx["manifest"].get("version", ""),
                    ctx["today"],
                )
                dash = "~" * len(header)
                line = "* [IMP] Created documentation directory"
                ctx[section] = "%s\n%s\n\n%s\n" % (header, dash, line)
            fd.write(_c(ctx[section.lower()]))


def write_egg_info(ctx):

    for section in (
        "authors",
        "contributors",
        "description",
        "description_i18n",
        "changelog",
    ):
        write_rst_file(ctx, ".", section)


def generate_readme(ctx):

    def set_values_of_manifest(ctx):
        if not ctx.get("pypi_modules"):
            ctx["pypi_modules"] = "%s" % ZERO_PYPI_PKGS
        if not ctx.get("pypi_sects"):
            ctx["pypi_sects"] = "%s" % ZERO_PYPI_SECTS

    def read_manifest_setup(ctx):
        if ctx["product_doc"] == "pypi":
            if ctx["odoo_layer"] == "repository":
                ctx["module_name"] = ""
            else:
                ctx["module_name"] = pth.basename(ctx["path_name"])
            ctx["repos_name"] = "tools"
            read_setup(ctx)
        elif ctx["odoo_layer"] == "ocb":
            ctx["module_name"] = ""
            ctx["repos_name"] = "OCB"
            read_all_manifests(ctx)
        elif ctx["odoo_layer"] == "repository":
            ctx["module_name"] = ""
            ctx["repos_name"] = pth.basename(ctx["path_name"])
            read_all_manifests(ctx)
        else:
            if not ctx["module_name"]:
                ctx["module_name"] = build_odoo_param(
                    "PKGNAME", odoo_vid=".", multi=True
                )
                if not ctx["module_name"]:
                    ctx["module_name"] = build_odoo_param(
                        "PKGNAME", odoo_vid=".", multi=True
                    )
            if not ctx["repos_name"]:
                ctx["repos_name"] = build_odoo_param("REPOS", odoo_vid=".", multi=True)
                if not ctx["repos_name"]:
                    ctx["repos_name"] = build_odoo_param(
                        "REPOS", odoo_vid=".", multi=True
                    )
            read_manifest(ctx)

    def set_description(ctx):
        section = "description"
        if not ctx[section] or ctx[section] == "N/A":
            ctx[section] = ctx["rdme_description"]
        if re.match(r"\s*$", ctx[section]):
            ctx[section] = "No info available"

    def set_description_i18n(ctx):
        section = "description_i18n"
        if not ctx[section] or re.match(r"\s*$", ctx[section]):
            ctx[section] = "Nessuna informazione disponibile"

    def set_authors(ctx):
        section = "authors"
        if ctx["manifest"].get("author"):
            ctx[section] = merge_lists(
                ctx, ctx["manifest"]["author"], ctx[section])
        else:
            ctx[section] = merge_lists(
                ctx, ctx["rdme_authors"], ctx[section])
        authors = []
        for item in ctx[section]:
            if not item[2] and item[3]:
                ctx["contributors"].append(item)
            else:
                authors.append(item)
        ctx[section] = authors
        found = False
        for git_org in ctx[section]:
            if ctx["git_orgid"] == git_org[0]:
                found = True
                break
        if not found:
            print("Warning! Organization %s not found in documents" % ctx["git_orgid"])
            ctx[section].append(ctx["license_mgnt"].get_info_from_id(ctx["git_orgid"]))
        left = item_2_set(ctx["license_mgnt"].org_ids, field="author")
        right = item_2_set(ctx[section], field=1)
        if (
                not ctx["suppress_warning"]
                and left != right
        ):
            print_red_message(
                "*** Warning: authors %s in documentation do not match expected %s!" % (
                    ",".join(left), ",".join(right))
            )

    def set_contributors(ctx):
        section = "contributors"
        ctx[section] = merge_lists(ctx, ctx["rdme_contributors"], ctx[section])
        if not ctx[section]:
            ctx[section] = ctx["license_mgnt"].get_maintainer()

    def set_website(ctx):
        section = "website"
        if ctx["product_doc"] == "pypi" and ctx["manifest"].get("author_email"):
            ctx["manifest"][section] = ctx["manifest"]["author_email"]
        if ctx["write_authinfo"]:
            ctx[section] = ctx["license_mgnt"].get_website(
                org_id=ctx["git_orgid"],
                repo=ctx["repos_name"]) or ctx["manifest"].get(section, "")
        else:
            ctx[section] = ctx["manifest"].get(
                section, ctx["license_mgnt"].get_website(
                    org_id=ctx["git_orgid"], repo=ctx["repos_name"]))
        if not ctx["suppress_warning"] and ctx["manifest"].get(section) != ctx[section]:
            print_red_message(
                "*** Warning: website %s in the manifest replaced by %s!" % (
                    ctx["manifest"].get(section, ""), ctx[section])
            )
        ctx["manifest"][section] = ctx[section]

    def set_maintainer(ctx):
        section = "maintainer"
        if ctx["write_authinfo"]:
            ctx[section] = ctx["manifest"].get(
                section, ctx["license_mgnt"].get_maintainer())
        elif not ctx[section]:
            ctx[section] = merge_lists(
                ctx, ctx["manifest"].get(section, ""),
                ctx["license_mgnt"].get_maintainer())
        else:
            if isinstance(ctx[section], (list, tuple)):
                res = ctx["license_mgnt"].extract_info_from_line(ctx[section][0][1])
            else:
                res = ctx["license_mgnt"].extract_info_from_line(ctx[section])
            if res[1]:
                ctx[section] = [res]
            else:
                ctx[section] = ctx["manifest"].get(
                    section, ctx["license_mgnt"].get_maintainer())

    def set_license(ctx):
        section = "license"
        if ctx["opt_gpl"]:
            left = ctx["license_mgnt"].license_code(ctx["manifest"].get(section))
            right = ctx["opt_gpl"]
            if (
                    not ctx["suppress_warning"]
                    and left != right
            ):
                print_red_message(
                    "*** Warning: manifest license %s does not match expected %s!" % (
                        ctx["license_mgnt"].license_text(left),
                        ctx["license_mgnt"].license_text(right)
                        )
                )
        if ctx["opt_gpl"] or not ctx["manifest"].get(section):
            if ctx["opt_gpl"] not in ("agpl", "lgpl", "opl", "oee"):
                ctx["opt_gpl"] = ctx["license_mgnt"].get_license(
                    odoo_majver=ctx["odoo_majver"])
            ctx[section] = ctx["license_mgnt"].license_text(ctx["opt_gpl"])
            ctx["manifest"][section] = ctx[section]
        else:
            ctx[section] = ctx["manifest"][section]
            ctx["opt_gpl"] = ctx["license_mgnt"].license_code(ctx[section])

    def set_name_i18n(ctx):
        section = "name_i18n"
        if not ctx.get(section):
            ctx[section] = ctx["module_name"]

    def set_summary(ctx):
        section = "summary"
        if not ctx[section]:
            ctx[section] = "No summary"

    def set_summary_i18n(ctx):
        section = "summary_i18n"
        if not ctx[section]:
            ctx[section] = "Sommario non disponibile"

    def load_section_from_file(ctx, section, is_tag=None):
        if not is_tag or re.match(r"\s*$", ctx.get(section, "")):
            ctx[section] = parse_local_file(
                ctx, "%s.rst" % section, ignore_ntf=True, section=section
            )
        if "description" in section:
            # Remove old header text
            x = ctx[section].split("\n", 2)
            if len(x) > 2 and re.match(r"^(=+|-+|~+)$", x[1]):
                ctx[section] = x[2]
                while ctx[section].startswith("\n"):
                    ctx[section] = ctx[section][1:]
        if re.match(r"\s*$", ctx[section]):
            ctx[section] = ""
        if pth.isfile(pth.join("static", "description", "%s.png" % section)):
            ctx["%s_png" % section] = """.. figure:: /%s/static/description/%s.png
  :alt: %s
  :width: 98%%""" % (ctx["module_name"], section, ctx["name"])
        else:
            ctx["%s_png" % section] = ""

    # === Starting generate ===
    __init__(ctx)
    read_manifest_setup(ctx)
    if ctx["odoo_layer"] == "module":
        for fn in ("./README.md", "./README.rst", "../README.rst"):
            if not pth.isfile(fn):
                continue
            with open(fn, RMODE) as fd:
                (
                    ctx["rdme_description"],
                    ctx["rdme_authors"],
                    ctx["rdme_contributors"],
                ) = read_purge_readme(ctx, _u(fd.read()))
            break
    set_default_values(ctx)
    ctx["license_mgnt"] = license_mgnt.License()
    ctx["license_mgnt"].add_copyright(ctx["git_orgid"], "", "", "", "")

    # Contents of sections are in rst format
    for section in DEFINED_SECTIONS:
        load_section_from_file(ctx, section)
        load_section_from_file(ctx, section + "_i18n")

    for tag in DEFINED_TAG:
        load_section_from_file(ctx, tag, is_tag=True)
        load_section_from_file(ctx, tag + "_i18n", is_tag=True)

    # List tags (i.e. authors) are python list of license data
    for section in LIST_TAG:
        tag_items = (
            ctx[section].split(",")
            if "," in ctx[section] and "\n" not in ctx[section]
            else ctx[section].split("\n")
        )
        ctx[section] = []
        for ln in tag_items:
            if ln:
                res = ctx["license_mgnt"].extract_info_from_line(ln)
                if res[1]:
                    ctx[section].append(res)

    set_description(ctx)
    set_description_i18n(ctx)
    set_name_i18n(ctx)
    set_summary(ctx)
    set_summary_i18n(ctx)
    if ctx["odoo_layer"] == "module":
        set_authors(ctx)
        set_contributors(ctx)
        set_website(ctx)
        set_maintainer(ctx)
        set_license(ctx)
    set_values_of_manifest(ctx)
    if ctx["module_name"]:
        read_dependecies_license(ctx)
    for section in LIST_TAG:
        if isinstance(ctx[section], (list, tuple)):
            item_2_test(ctx, section)

    if ctx["write_authinfo"]:
        write_egg_info(ctx)

    if ctx["write_index"] and ctx["product_doc"] == "odoo":
        icon_fn = pth.join(ctx["img_dir"], ctx["src_icon"])
        if not pth.isfile(icon_fn):
            if ctx["debug_template"]:
                src_icon = pth.join(ctx["home_devel"],
                                    "pypi",
                                    "tools",
                                    "templates",
                                    "odoo",
                                    "icons",
                                    ctx["src_icon"])
            else:
                src_icon = pth.join(ctx["odoo_root"],
                                    "tools",
                                    "templates",
                                    "odoo",
                                    "icons",
                                    ctx["src_icon"])
            if pth.isfile(src_icon):
                copyfile(src_icon, icon_fn)
        if not ctx["template_name"]:
            ctx["template_name"] = "readme_index.html"
        target = index_html_content(
            ctx, parse_local_file(ctx, ctx["template_name"], out_fmt="html")
        )
    elif ctx["write_index"] and ctx["product_doc"] == "pypi":
        if not ctx["template_name"]:
            ctx["template_name"] = "module_index.rst"
        target = parse_local_file(ctx, ctx["template_name"], out_fmt="rst")
    else:
        if not ctx["template_name"]:
            ctx["template_name"] = "readme_main_%s.rst" % ctx["odoo_layer"]
        target = parse_local_file(ctx, ctx["template_name"], out_fmt="rst")
    if ctx["rewrite_manifest"] and ctx["odoo_layer"] == "module":
        if ctx["product_doc"] != "odoo":
            return
        target = manifest_contents(ctx)
    dst_file = ctx["dst_file"]
    if ctx["opt_verbose"]:
        print("Writing %s" % dst_file)
    with open(dst_file, "w") as fd:
        fd.write(_c(target))
    if (
        ctx["rewrite_manifest"]
        and ctx["odoo_layer"] == "module"
        and not ctx["suppress_warning"]
    ):
        print(
            "\n\nYou should update license info of the files.\n"
            "Please, type\n"
            "> topep8 -h\n"
            "for furthermore information\n"
        )
    if ctx["opt_verbose"]:
        if ctx["history-summary"]:
            print("\nRecent History\n~~~~~~~~~~~~~~\n")
            print_green_message(ctx["history-summary"])
        else:
            if ctx["odoo_layer"] == "module" and ctx["module_name"]:
                item = ctx["module_name"]
            else:
                item = "code"
            print_red_message("Missed documentation for last %s updates!!!" % item)


def main(cli_args=None):
    if not cli_args:
        cli_args = sys.argv[1:]
    parser = z0lib.parseoptargs(
        "Generate README", "© 2018-2023 by SHS-AV s.r.l.", version=__version__
    )
    parser.add_argument("-h")
    parser.add_argument(
        "-b", "--odoo-branch", action="store", default=".", dest="odoo_vid"
    )
    parser.add_argument("-B", "--debug-template", action="store_true")
    parser.add_argument(
        "-D", "--home-devel", metavar="PATH", help="Home devel directory"
    )
    parser.add_argument("-F", "--from-version")
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="force creating documentation even if doc dirs do not exit",
    )
    parser.add_argument("-G", "--git-org", action="store", dest="git_orgid")
    parser.add_argument("-g", "--gpl-info", action="store", dest="opt_gpl", default="")
    parser.add_argument(
        "-H", "-I", "--write-index", action="store_true", dest="write_index"
    )
    parser.add_argument(
        "-l", "--layer", action="store", help="ocb|module|repository", dest="odoo_layer"
    )
    parser.add_argument(
        "-L", "--lang", action="store", help="iso code", default="it_IT"
    )
    parser.add_argument("-m", "--module-name", action="store", help="filename")
    parser.add_argument(
        "-M",
        "--force-maturity",
        action="store",
        help="Alfa,Beta,Mature,Production/stable",
        dest="force_maturity",
    )
    parser.add_argument("-n")
    parser.add_argument("-o", "--output-file", action="store", help="filename")
    parser.add_argument(
        "-P",
        "--product-doc",
        action="store",
        help="may be odoo or pypi",
        dest="product_doc",
        default="",
    )
    parser.add_argument(
        "-p",
        "--path-name",
        action="store",
        help="pathname",
        default=".",
    )
    parser.add_argument("-q")
    parser.add_argument("-R", "--rewrite-manifest", action="store_true")
    parser.add_argument("-r", "--repos_name", action="store", help="dirname")
    parser.add_argument("-Q", "--quote-with", help="CHAR", default="\"")
    parser.add_argument("-t", "--template_name", action="store", help="filename")
    parser.add_argument("-T", "--trace-file", action="store_true")
    parser.add_argument("-V")
    parser.add_argument("-v")
    parser.add_argument("-W", "--write-authinfo", action="store_true")
    parser.add_argument("-w", "--suppress-warning", action="store_true")
    parser.add_argument(
        "-Y", "--write-man-page", action="store_true", dest="write_man_page"
    )
    ctx = unicodes(parser.parseoptargs(cli_args))
    return generate_readme(ctx)


if __name__ == "__main__":
    exit(main())
    exit(main())


