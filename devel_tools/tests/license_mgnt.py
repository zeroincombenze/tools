# -*- coding: utf-8 -*-
import os
from datetime import datetime
import re

COPY = {
    'zero': {
        'author': 'SHS-AV s.r.l.',
        'website': 'https://www.zeroincombenze.it',
        'devman': 'Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>',
    },
    'shs': {
        'author': 'SHS-AV s.r.l.',
        'website': 'https://www.shs-av.com',
        'devman': 'Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>',
    },
    'oca': {
        'author': 'Odoo Community Association (OCA)',
        'website': 'https://odoo-community.org',
    },
    'powerp': {
        'author': 'powERP enterprise network',
        'website': 'https://www.powerp.it',
        'devman': 'powERP enterprise network',
    },
    'didotech': {
        'author': 'Didotech s.r.l.',
        'website': 'https://www.didotech.com',
    },
}
ALIAS = {
    'shs-av': 'shs',
    'zeroincombenze': 'zero'
}


class License:

    def __init__(self, path=None):
        self.org_ids = {}
        self.authors = {}
        self.contributors = {}
        self.cur_year = datetime.today().year
        path = path or '.'
        author_file = os.path.join(path, 'egg-info', 'authors.txt')
        if not os.path.isfile(author_file):
            author_file = os.path.join(path, 'readme', 'AUTHORS.rst')
        if os.path.isfile(author_file):
            self.parse_file(author_file)
        author_file = os.path.join(path, 'egg-info', 'contributors.txt')
        if not os.path.isfile(author_file):
            author_file = os.path.join(path, 'readme', 'CONTRIBUTORS.rst')
        if os.path.isfile(author_file):
            self.parse_file(author_file)
        author_file = os.path.join(path, 'egg-info', 'acknowledges.txt')
        if os.path.isfile(author_file):
            self.parse_file(author_file)

    def add_copyright(self, org_id, name, website, email, years):
        if org_id and org_id not in self.org_ids:
            self.org_ids[org_id] = [name, website, email, years]
        elif email and email not in self.contributors:
            self.contributors[email] = [name, email, years]
        elif name and name not in self.authors:
            self.authors[name] = [name, website, years]
        self.purge_duplicate()

    def parse_file(self, author_file):
        with open(author_file, 'rb') as fd:
            for line in fd.read().split('\n'):
                self.add_copyright(*self.extract_info_from_line(line))

    def purge_duplicate(self):
        for name in self.authors.copy().keys():
            website = self.authors[name][1]
            for org_id in self.org_ids.keys():
                if (name == self.org_ids[org_id][0] or
                        website == self.org_ids[org_id][1]):
                    del self.authors[name]
                    break
        for name in self.contributors.copy().keys():
            email = self.contributors[name][1]
            for org_id in self.org_ids.keys():
                if (name == self.org_ids[org_id][0] or
                        email == self.org_ids[org_id][2]):
                    del self.contributors[name]
                    break

    def extract_info_from_line(self, line):

        def from_rst_line(line):
            org_id = False
            website = False
            email = False
            ii = line.find('<')
            jj = line.find('>')
            if 0 <= ii < jj and jj >= 0:
                name = line[0: ii].strip()
                url = line[ii + 1: jj]
                url = url.replace('http:', 'https:')
                if url.endswith('/'):
                    url = url[0: -1]
                if '@' in url:
                    email = url
                    if not name:
                        name = ' '.join(
                            [x.capitalize()
                             for x in email.split('@')[0].split('.')])
                else:
                    website = '.'.join(os.path.basename(url).split('.')[-2:])
                    for kk, item in COPY.items():
                        if item['website'].endswith(website):
                            org_id = kk
                            website = item['website']
                            name = item['author']
                            break
                    if not org_id:
                        org_id = os.path.basename(website).split('.')[-2]
                        org_id = ALIAS.get(org_id, org_id)
                        COPY[org_id] = {
                            'website': 'http://%s' % website,
                            'author': name,
                        }
            else:
                name = line
            return org_id, name, website, email, ''

        def from_comment_line(line):
            head = r'^ *([Cc]opyright|\([Cc]\)|©)'
            rex = '%s%s' % (head[0: -1], r'|http:|https:|\w+\@[a-zA-z0-9-.]+)')
            org_id = False
            name = False
            website = False
            email = False
            years = ''
            if re.match(rex, line):
                ipos = 1
                loom = re.match(r'^ *([Cc]opyright|\([Cc]\)|©)', line)
                if loom:
                    ipos += loom.end() + 1
                    loom = re.match('^ *[0-9]+', line[ipos:])
                    if loom:
                        ii = ipos + loom.end()
                        years = line[ipos:ii]
                        if line[ii] == '-':
                            ipos = ii + 1
                            loom = re.match('[0-9]+', line[ipos:])
                            if loom:
                                ii = loom.end()
                                if ii == 4:
                                    ipos += 2
                                    ii = ipos + ii - 2
                                else:
                                    ii += ipos
                                if line[ipos:ii] == str(self.cur_year)[2:]:
                                    years = '%s-%s' % (
                                        years, line[ipos:ii])
                                else:
                                    years = '%s-%s' % (
                                        years, str(self.cur_year)[-2:])
                            elif years != str(self.cur_year):
                                years = '%s-%s' % (
                                    years,
                                    str(self.cur_year)[-2:])
                        elif years != str(self.cur_year):
                            years = '%s-%s' % (
                                years,
                                str(self.cur_year)[-2:])
                org_id, name, website, email = from_rst_line(
                    line[ipos:].strip())
            return org_id, name, website, email, years

        if line.startswith('*'):
            return from_rst_line(line[1:].strip())
        elif line.startswith('#'):
            return from_comment_line(line[1:].strip())
        return False, False, False, False, False

    def summary_authors(self):
        author = ''
        if self.org_ids:
            for org_id in ('oca', 'powerp', 'zero', 'shs', 'didotech'):
                if org_id in self.org_ids:
                    author = self.org_ids[org_id][0]
                    break
            if author and len(self.org_ids) < 3:
                for org_id in self.org_ids.keys():
                    if self.org_ids[org_id][0] not in author:
                        author = '%s, %s' % (author, self.org_ids[org_id][0])
            elif author and len(self.org_ids) >= 3:
                author += ' and other partners'
            else:
                for org_id in self.org_ids.keys():
                    author = '%s, %s' % (author, self.org_ids[org_id][0])
                author = author[2:]
        elif self.authors:
            for item in self.authors.keys():
                author = '%s, %s' % (author, self.authors[item][0])
            author = author[2:]
        return author

    def get_website(self):
        website = ''
        if self.org_ids:
            for org_id in ('oca', 'powerp', 'zero', 'shs', 'didotech'):
                if org_id in self.org_ids:
                    website = self.org_ids[org_id][1]
                    break
        if not website and self.org_ids:
            for item in self.org_ids.keys():
                website = self.websites[item][1]
                if website:
                    break
        if not website and self.authors:
            for item in self.authors.keys():
                website = self.authors[item][1]
                if website:
                    break
        return website

    def get_maintainer(self):
        maintainer = ''
        if self.org_ids:
            for org_id in ('oca', 'powerp', 'zero', 'shs', 'didotech'):
                if org_id in self.org_ids:
                    maintainer = COPY[org_id].get('devman', '')
                    if maintainer:
                        break
        return maintainer
