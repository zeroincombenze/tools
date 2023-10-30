# -*- coding: utf-8 -*-
import os
from datetime import datetime
import re

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    from python_plus.python_plus import _u
except ImportError:
    from python_plus import _u

COPY = {
    "zero": {
        "author": "SHS-AV s.r.l.",
        "website": "https://www.zeroincombenze.it",
        "devman": "Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>",
        "github-user": "zeroincombenze",
    },
    "shs-av": {
        "author": "SHS-AV s.r.l.",
        "website": "https://www.shs-av.com",
        "devman": "Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>",
        "github-user": "zeroincombenze",
    },
    "oca": {
        "author": "Odoo Community Association (OCA)",
        "website": "https://odoo-community.org",
        "github-user": "OCA",
    },
    "odoo-italia": {
        "author": "Associazione Odoo Italia",
        "website": "https://www.odoo-italia.org",
        "github-user": "OCA",
    },
    # "powerp": {
    #     "author": "powERP enterprise network",
    #     "website": "https://www.powerp.it",
    #     "devman": "powERP enterprise network",
    #     "github-user": "PowERP-cloud",
    # },
    "librerp": {
        "author": "LibrERP enterprise network",
        "website": "https://www.librerp.it",
        # "devman": "LibrERP enterprise network",
        "github-user": "LibrERP-network",
    },
    "didotech": {
        "author": "Didotech s.r.l.",
        "website": "https://www.didotech.com",
        "github-user": "iw3hxn",
    },
    "agilebg.com": {
        "author": "Agile Business Group sagl",
        "website": "https://www.agilebg.com",
    },
    "apuliasoftware.it": {
        "author": "Apulia Software s.r.l.",
        "website": "https://www.apuliasoftware.it",
    },
}
ALIAS = {
    "zeroincombenze": "zero",
    "odooitaliancommunity": "odoo-italia",
    "odooitaliaassociazione": "odoo-italia",
    "powerp": "librerp",
    "powerp.it": "librerp",
    "Agile Business Group": "agilebg.com",
}
ALIAS_NAME = {
    "Antonio Maria Vigliotti":
        "Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>",
}


class License:
    def __init__(self, path=None):
        self.org_ids = {}
        self.authors = {}
        self.contributors = {}
        self.cur_year = datetime.today().year
        path = path or "."
        for item in ("authors", "contributors", "acknowledges.txt"):
            for docdir in ("readme", "egg-info"):
                fn = os.path.join(path, docdir, item.upper() + ".rst")
                if os.path.isfile(fn):
                    self.parse_file(fn)
                    break
                fn = os.path.join(path, docdir, item + ".rst")
                if os.path.isfile(fn):
                    self.parse_file(fn)
                    break
                fn = os.path.join(path, docdir, item + ".txt")
                if os.path.isfile(fn):
                    self.parse_file(fn)
                    break
        self.gpl2license = {
            "agpl": "AGPL-3",
            "lgpl": "LGPL-3",
            "opl": "OPL-1",
            "oee": "OEE-1",
        }
        self.license2gpl = {
            "AGPL-3": "agpl",
            "LGPL-3": "lgpl",
            "OPL-1": "opl",
            "OEE-1": "oee",
        }

    def add_copyright(self, org_id, name, website, email, years):
        if org_id and org_id not in self.org_ids:
            if org_id in COPY:
                if not name:
                    name = COPY[org_id]["author"]
                if not website:
                    website = COPY[org_id]["website"]
            self.org_ids[org_id] = [name, website, email, years]
        elif email and email not in self.contributors:
            self.contributors[email] = [name, email, years]
        elif name and name not in self.authors:
            self.authors[name] = [name, website, years]
        self.purge_duplicate()

    def parse_file(self, author_file):
        with open(author_file, "r") as fd:
            for line in _u(fd.read().split("\n")):
                self.add_copyright(
                    *self.extract_info_from_line(line, add_copy=False))

    def purge_duplicate(self):
        for name in self.authors.copy().keys():
            website = self.authors[name][1]
            for org_id in self.org_ids.keys():
                if (
                    name == self.org_ids[org_id][0]
                    or website == self.org_ids[org_id][1]
                ):
                    del self.authors[name]
                    break
        for name in self.contributors.copy().keys():
            email = self.contributors[name][1]
            for org_id in self.org_ids.keys():
                if name == self.org_ids[org_id][0] or email == self.org_ids[org_id][2]:
                    del self.contributors[name]
                    break

    def extract_info_from_line(self, line, force=False, add_copy=True):
        """ "Return org_id, name, website, email, years from line"""

        def split_name_url(line):
            x = re.match("[^<]*", line)
            y = re.search("[<][^>]*", line)
            if x and y:
                name = line[x.start(): x.end()].strip()
                url = line[y.start() + 1: y.end()].strip()
            else:
                x = re.match("[^(]*", line)
                y = re.search("[(][^)]*", line)
                if x and y:
                    name = line[x.start(): x.end()].strip()
                    url = line[y.start() + 1: y.end()].strip()
                    if "http" not in url and "@" not in url:
                        if line.startswith(".") or "::" in line:
                            return False, False, False, False, False
                        name = line.strip()
                        url = ""
                else:
                    name = line.strip()
                    url = ""
            if url == "False":
                url = ""
            url = url.replace("http:", "https:").replace("http//", "https://")
            if url.endswith("/"):
                url = url[0:-1]
            new_name = ALIAS_NAME.get(name, name)
            if name and new_name != name and not url:
                return split_name_url(new_name)
            return name, url

        def from_rst_line(line):
            org_id = False
            website = False
            email = False
            name, url = split_name_url(line)
            if "@" in url or url.startswith("https://github.com/"):
                email = url
                if not name:
                    name = " ".join(
                        [
                            x.capitalize()
                            for x in email.split("@")[0].split(".")        # noqa: F812
                        ]
                    )
            else:
                found = False
                if url:
                    parts = urlparse(url)
                    if parts.netloc == "github.com":
                        org_id = parts.path.split("/", 2)[1].lower()
                        website = "%s//%s/%s" % (parts.scheme, parts.netloc, org_id)
                    else:
                        org_id = parts.netloc.lower()
                        website = parts.scheme + "://" + parts.netloc
                else:
                    org_id = re.sub("[^a-z0-9A-Z]*", "", name).lower()
                org_id = ALIAS.get(org_id, org_id)
                for kk, item in COPY.items():
                    if (
                        org_id == kk
                        or (
                            item["website"]
                            and (
                                org_id == urlparse(item["website"]).netloc
                                or org_id
                                == urlparse(item["website"]).netloc.split(".", 1)[-1]
                            )
                        )
                        or (
                            re.sub("[^a-z0-9A-Z&+-]*", "", name)
                            == re.sub("[^a-z0-9A-Z&+-]*", "", item["author"])
                        )
                    ):
                        org_id = kk
                        if item["website"]:
                            website = item["website"]
                        elif website:
                            item["website"] = website
                        name = item["author"]
                        found = True
                        break
                if not found and website:
                    org_id = ALIAS.get(org_id, org_id)
                    COPY[org_id] = {
                        "website": website,
                        "author": name,
                    }
            return org_id, name, website, email, ""

        def from_comment_line(line):
            head = r"^ *([Cc]opyright|\([Cc]\)|©)"
            rex = "%s%s" % (head[0:-1], r"|http:|https:|\w+\@[a-zA-z0-9-.]+)")
            org_id = False
            name = False
            website = False
            email = False
            years = ""
            if re.match(rex, line):
                ipos = 1
                loom = re.match(r"^ *([Cc]opyright|\([Cc]\)|©)", line)
                if loom:
                    ipos += loom.end() + 1
                    loom = re.match("^ *[0-9]+", line[ipos:])
                    if loom:
                        ii = ipos + loom.end()
                        years = line[ipos:ii]
                        if line[ii] == "-":
                            ipos = ii + 1
                            loom = re.match("[0-9]+", line[ipos:])
                            if loom:
                                ii = loom.end()
                                if ii == 4:
                                    ipos += 2
                                    ii = ipos + ii - 2
                                else:
                                    ii += ipos
                                if line[ipos:ii] == str(self.cur_year)[2:]:
                                    years = "%s-%s" % (years, line[ipos:ii])
                                else:
                                    years = "%s-%s" % (years, str(self.cur_year)[-2:])
                            elif years != str(self.cur_year):
                                years = "%s-%s" % (years, str(self.cur_year)[-2:])
                        elif years != str(self.cur_year):
                            years = "%s-%s" % (years, str(self.cur_year)[-2:])
                org_id, name, website, email, dummy = from_rst_line(line[ipos:].strip())
            return org_id, name, website, email, years

        line = line.replace("`__", "").replace("`", "")
        if line.startswith("*"):
            res = from_rst_line(line[1:].strip())
        elif line.startswith("#"):
            res = from_comment_line(line[1:].strip())
        elif force:
            res = from_rst_line(line.strip())
        else:
            res = [False, False, False, False, False]
        if add_copy and res[1]:
            self.add_copyright(*res)
            if res[0] and res[0] not in self.org_ids:
                # Entry purged
                res = [False, False, False, False, False]
        return res

    def summary_authors(self, summarize=False):
        author = ""
        if self.org_ids:
            for org_id in ("oca", "librerp", "zero", "shs-av", "didotech", "powerp"):
                if org_id in self.org_ids:
                    author = self.org_ids[org_id][0]
                    break
            if author and (not summarize or len(self.org_ids) < 3):
                for org_id in self.org_ids.keys():
                    if self.org_ids[org_id][0] not in author:
                        author = "%s,%s" % (author, self.org_ids[org_id][0])
            elif author and len(self.org_ids) >= 3:
                author += " and other partners"
            else:
                for org_id in self.org_ids.keys():
                    author = "%s,%s" % (author, self.org_ids[org_id][0])
                author = author[1:]
        elif self.authors:
            for item in self.authors.keys():
                author = "%s,%s" % (author, self.authors[item][0])
            author = author[1:]
        return author

    def get_website(self, org_id=None, repo=None, module=None):
        website = ""
        if org_id in self.org_ids:
            website = self.org_ids[org_id][1]
        elif self.org_ids:
            for org_id in ("oca", "librerp", "powerp", "zero", "shs-av", "didotech"):
                if org_id in self.org_ids:
                    website = self.org_ids[org_id][1]
                    break
        if not website and self.org_ids:
            for item in self.org_ids.keys():
                website = self.org_ids[item][1]
                if website:
                    break
        if not website and self.authors:
            for item in self.authors.keys():
                website = self.authors[item][1]
                if website:
                    break
        if repo and org_id == "oca":
            website += "/" + repo
        elif repo and org_id == "zero":
            if repo.startswith("l10n-italy"):
                website += "/fatturazione-elettronica"
            else:
                website += "/crm"
        return website

    def get_maintainer(self):
        maintainer = ""
        if self.org_ids:
            for org_id in ("oca", "librerp", "powerp", "zero", "shs-av", "didotech"):
                if org_id in self.org_ids:
                    maintainer = COPY[org_id].get("devman", "")
                    if maintainer:
                        break
        return maintainer

    def get_license(self, odoo_majver=None):
        odoo_majver = odoo_majver or 12.0
        if odoo_majver <= 8:
            license = "agpl"
        else:
            if "oca" in self.org_ids:
                license = "lgpl"
            elif "powerp" in self.org_ids:
                license = "opl"
            else:
                license = "lgpl"
        return license

    def license_text(self, gpl):
        return self.gpl2license.get(gpl, "AGPL-3")

    def license_code(self, license):
        return self.license2gpl.get(license, "agpl")

    def get_info_from_id(self, git_orgid):
        if git_orgid in COPY:
            return (
                git_orgid,
                COPY[git_orgid]["author"],
                COPY[git_orgid]["website"],
                "",
                "",
            )
