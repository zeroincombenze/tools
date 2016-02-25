#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#
"""
    Create a Wiki formatted software page, merging source page with a template
    Software wiki pages have sections written as '==section text=='
    Software extract section text from source and rearranges using Template.
    Template use python string template syntax -> ${macro}
    where macro is section name extracted by wiki source

    Media file from source, formatted as '[[File:H' are lost,
    because are parts of template

    Some sections have predefined formatting
    - Notes -> Expands references with '<references/>'
    - Versioni -> Write a version table of software
      Data is embedded between '<!-- <version> -->' and '<!-- </version> -->'
      Data version are rows (1 per version/release); any row has 5 coloumns:
      Status, Main, Release, Daterel, Notes
      where:
      - Status stands for support status:
        o (old), co (old supported), c (current), cp (beta), p (planned)
      - Main is main version or version name; may be empty
      - Release is public version/release identification text
      - Daterel is 1.st release date
      - Notes may be any text (mainly last date upgrade)

"""

import os.path
import ConfigParser
from string import Template
import datetime
import calendar
import argparse
from sys import platform as _platform
# import pdb


class Builder:

    def init_dict(self):
        cfg_obj = ConfigParser.SafeConfigParser(
            {"template_fn": "mknews_template.html",
             "ref_fn": ""})

        self.sections = ("hdr",
                         "footer",
                         "Versioni",
                         "Storia",
                         "Caratteristiche",
                         "Vantaggi e svantaggi",
                         "Implementazioni e Distribuzioni",
                         "Distribuzioni",
                         "Concorrenti",
                         "Guida all'uso",
                         "Guida di riferimento tecnico",
                         "Guida rapida",
                         "Installazione",
                         "Aggiornamento",
                         "FAQ",
                         "Troubleshooting",
                         "Regole di sviluppo del codice",
                         "Sviluppo del codice",
                         "Documentazione per gli sviluppatori",
                         "Librerie e ambiente di sviluppo",
                         "Programmi complementari",
                         "Guida alla sicurezza",
                         "Note",
                         "Altre notizie",
                         "Collegamenti esterni")

        self.tags = {"_None": "<>",
                     "_end_None": "</>",
                     "version": "<!-- <version>",
                     "end_version": "</version> -->",
                     "platform": "<!-- <platform",
                     "end_platform": "> -->"}

        month_des = ("", "gennaio", "febbraio", "marzo", "aprile",
                     "maggio", "giugno", "luglio", "agosto",
                     "settembre", "ottobre", "novembre", "dicembre")

        wday_des = ("lunedì",
                    "martedì",
                    "mercoledì",
                    "giovedì",
                    "venerdì",
                    "sabato",
                    "domenica")

        s = "Fiscal"
        cfg_obj.add_section(s)

        if datetime.date.today().day < 15:
            m = datetime.date.today().month
        else:
            m = datetime.date.today().month + 1
        y = datetime.date.today().year
        if m > 12:
            m = 1
            y = y + 1
        cfg_obj.set(s, 'cur_month', month_des[m])
        cfg_obj.set(s, 'cur_year', str(y))
        e = calendar.monthrange(y, m)[1]
        w = datetime.date(y, m, e).weekday()
        cfg_obj.set(s, 'last_c_day', str(e))
        cfg_obj.set(s, 'last_c_dayw', wday_des[w])

        i = 15
        # Saturday or Sunday
        while datetime.date(y, m, i).weekday() >= 5:
            i = i + 1
        cfg_obj.set(s, 'day_ivam', str(i))
        w = datetime.date(y, m, i).weekday()
        cfg_obj.set(s, 'dayw_ivam', wday_des[w])

        i = 16
        while datetime.date(y, m, i).weekday() >= 5:
            i = i + 1
        cfg_obj.set(s, 'day_ivap', str(i))
        w = datetime.date(y, m, i).weekday()
        cfg_obj.set(s, 'dayw_ivap', wday_des[w])

        m = m - 1
        if m < 1:
            m = 12
            y = y - 1
        cfg_obj.set(s, 'pre_month', month_des[m])
        cfg_obj.set(s, 'pre_year', str(y))
        cfg_obj.set(s, 'F24_IVA', '60%02d' % m)
        return cfg_obj

    def get_template(self, prm):
        s = "DEFAULT"
        if 'tmpl_fn' not in prm:
            prm['tmpl_fn'] = self.cfg_obj.get(s, "template_fn")
        if not os.path.isfile(prm['tmpl_fn']) and\
                os.path.dirname(prm['tmpl_fn']) == "":
            prm['tmpl_fn'] = "./templates/" + prm['tmpl_fn']
        if not prm['qmode']:
            print "Template {0}".format(prm['tmpl_fn'])
        if os.path.isfile(prm['tmpl_fn']):
            tmpl_fd = open(prm['tmpl_fn'], 'r')
            tmpl_str = tmpl_fd.read()
            tmpl_str = self.extract_platform_text(tmpl_str, prm)
            tmpl_fd.close()
        else:
            tmpl_str = ""
            print "Template file not found!"
        return tmpl_str

    def get_ref_text(self, dict, prm):
        s = "DEFAULT"
        if 'ref_fn' not in prm:
            prm['ref_fn'] = self.cfg_obj.get(s, "ref_fn")
        if not prm['qmode']:
            print "Source/reference file {0}".format(prm['ref_fn'])
        if prm['ref_fn'] == "":
            print "Missed reference file!"
        elif not os.path.isfile(prm['ref_fn']):
            print "Reference file not found!"
        else:
            prm['curplatform'] = _platform
            txt = ""
            ref_fd = open(prm['ref_fn'], 'r')
            ref_str = ref_fd.read()
            ref_fd.close()
            ref_str = self.extract_platform_text(ref_str, prm)
            ref_str = self.manage_category(ref_str)
            pos = {}
            for id, nm in enumerate(self.sections):
                h = "==" + self.get_sect_text(id) + "=="
                i = ref_str.find(h)
                nm = self.get_sect_name(id)
                pos[nm] = i
            # Header section
            nxt_nm = self.get_sect_name(0)
            pos[nxt_nm] = 0
            cur_i = 0
            ended = False
            while not ended:
                cur_nm = nxt_nm
                nxt_nm = ""
                min = len(ref_str) - 1
                for nm in pos:
                    i = pos[nm]
                    if i > cur_i and i < min:
                        min = i
                        nxt_nm = nm
                i = min
                while (i > cur_i and ref_str[i] != '\n'):
                    i = i - 1
                dict[cur_nm] = self.rm_double_titles(ref_str[cur_i:i])
                cur_i = min
                if nxt_nm == "":
                    ended = True

        # -- Special actions
        txt = dict['sect_Note']
        if txt.find("<references/>") < 0:
            txt = txt + "\n<references/>"
            dict['sect_Note'] = txt

        txt = dict['sect_Sviluppo__del__codice']
        if txt.find("[[{{#var:softwname}}/dev") < 0:
            txt = txt + \
                "\n[[{{#var:softwname}}/' +\
                'dev|Documentazione riservata agli sviluppatori]]"
            dict['sect_Sviluppo__del__codice'] = txt

        txt = dict['sect_footer']
        if txt.find("[[Category:{{#var:softwname}}]]") < 0:
            txt = txt + "\n[[Category:{{#var:softwname}}]]"
            dict['sect_footer'] = txt

        txt = dict['sect_footer']
        if txt.find("[[Category:Software]]") < 0:
            txt = txt + "\n[[Category:Software]]"
            dict['sect_footer'] = txt
        return

    def extract_platform_text(self, ref_str, prm):
        tag = self.tags['platform']
        etag = self.tags['end_platform']
        i = ref_str.find(tag)
        while i >= 0:
            j = ref_str.find(etag, i + 1)
            if j < 0:
                j = len(ref_str)
            l = len(tag) + i + 1
            m = len(etag) + j
            x = ref_str[l:j]
            if x != prm['tgtplatform'] and x != '*':
                j = ref_str.find(tag, j + 1)
                if j < 0:
                    j = len(ref_str)
                m = j
            ref_str = ref_str[:i] + ref_str[m:]
            i = ref_str.find(tag)
        return ref_str

    def manage_category(self, ref_str):
        tag = "[[Category:"
        etag = "]]"
        i = ref_str.find(tag)
        if i >= 0:
            j = ref_str.find(etag, i + 1)
            if j < 0:
                j = len(ref_str)
            m = len(etag) + j
            ref_str = ref_str[:i] + "==footer==" + ref_str[m:]
        return ref_str

    def rm_double_titles(self, ref_str):
        tag = "=="
        etag = "=="
        i = ref_str.find(tag)
        if i >= 0:
            j = ref_str.find(etag, i + 4)
            if j < 0:
                j = len(ref_str)
            while (i > 0 and ref_str[i] != '\n'):
                i = i - 1
            while (j < len(ref_str) and ref_str[j] != '\n'):
                j = j + 1
            ref_str = ref_str[:i] + ref_str[j:]
        ref_str = self.rm_all_tags(ref_str, "[[File:h", "]]")
        ref_str = self.rm_all_tags(ref_str, "[[File:H", "]]")
        i = len(ref_str) - 1
        j = 0
        while (i > 0 and ref_str[i] != '\n'):
            i = i - 1
            j = j + 1
        if (j > 2):
            l = len(ref_str) - j + 2
            ref_str = ref_str[:l]
        return ref_str

    def rm_all_tags(self, ref_str, tag, etag):
        i = ref_str.find(tag)
        while i >= 0:
            j = ref_str.find(etag, i + 1)
            if j < 0:
                j = len(ref_str)
            m = len(etag) + j
            ref_str = ref_str[:i] + ref_str[m:]
            i = ref_str.find(tag)
        return ref_str

    def format_sect(self, txt):
        txt = txt.replace("\r\n", "\n")
        for n, nm in enumerate(self.tags):
            if nm[0:4] != 'end_':
                tag = self.tags[nm]
                i = txt.find(tag)
                if i >= 0:
                    end_nm = "end_" + nm
                    end_tag = self.tags[end_nm]
                    j = txt.find(end_tag)
                    if j < 0:
                        j = len(txt)
                    if nm == "version":
                        i = i + len(tag)
                        f = txt[i:j].strip().replace("\n", "~").split('~')
                        p = 5
                        prm = []
                        for i in (range(p)):
                            prm.append("")
                        txt = self.version_fmt_hdr(f)
                        b = 0
                        i = 0
                        while b < len(f):
                            if i < p:
                                prm[i] = f[b].strip()
                            else:
                                txt = txt + self.version_fmt_add_line(prm)
                                for i in (range(p)):
                                    prm[i] = ""
                                i = 0
                                prm[i] = f[b].strip()
                            i = i + 1
                            b = b + 1
                        txt = txt + self.version_fmt_add_line(prm)
                        txt = txt + self.version_fmt_foo()
        l = len(txt)
        while txt[l - 1:l] == '\n':
            txt = txt[0:l - 1]
            l = len(txt)
        return txt

    def version_fmt_hdr(self, f):
        txt = self.tags['version']
        for i in range(len(f)):
            if i % 5:
                txt = txt + '~{0}'.format(f[i])
            else:
                txt = txt + '\n{0}'.format(f[i])
        txt = txt + '\n' + self.tags['end_version'] + '\n'
        txt = txt + \
            '{| class="mw-collapsible mw-collapsed" style="width:100%"\n'
        txt = txt + '|-\n'
        txt = txt + '| [[File:H versioni.png|left]]\n'
        txt = txt + '! scope=col|Nome\n'
        txt = txt + '! scope=col|Versione\n'
        txt = txt + '! scope=col|Data di Lancio\n'
        txt = txt + '! scope=col|Note\n'
        return txt

    def color_status(self, prm):
        if prm == 'o':                         # Old -> Prior version
            clr = '#FDB3AB;'
        elif prm == 'co':                      # Old still supported
            clr = '#FEF8C6;'
        elif prm == 'c':                       # Current
            clr = '#D4F4B4;'
        elif prm == 'cp':                      # Current Preview -> Beta
            clr = '#FED1A0;'
        elif prm == 'p':                       # Planned
            clr = '#C1E6F5;'
        else:
            clr = "#F5F5F5;"
        return clr

    def version_fmt_add_line(self, prm):
        clr = self.color_status(prm[0])
        txt = '|-\n'
        txt = txt + '|\n'
        if prm[1] != "":
            txt = txt + \
                '! scope="row" style="vertical-align:top;"|{0}\n'.format(
                    prm[1])
        else:
            txt = txt + '|\n'

        txt = txt +\
            '| style="white-space:nowrap; text-align:center;' +\
            ' background-color:{0}"|{1}\n'\
            .format(clr, prm[2])

        txt = txt +\
            '| style="white-space:nowrap;"|{0}\n'.format(prm[3])

        txt = txt + '| {0}\n'.format(prm[4])

        return txt

    def version_fmt_foo(self):
        txt = '|-\n'
        txt = txt + '|\n'
        txt = txt + '| colpan="4"|&nbsp;\n'
        txt = txt + '|-\n'
        txt = txt + '|\n'
        txt = txt + '| scope="row" rowspan="5"|Legenda\n'
        txt = txt +\
            '| style="white-space:nowrap; text-align:center;' +\
            ' background-color:{0}"|\n'\
            .format(self.color_status('o'))
        txt = txt + '|\n'
        txt = txt + '| Versione precedente\n'
        txt = txt + '|-\n'
        txt = txt + '|\n'
        txt = txt +\
            '| style="white-space:nowrap; text-align:center;' +\
            ' background-color:{0}"|\n'\
            .format(self.color_status('co'))
        txt = txt + '|\n'
        txt = txt + '| Versione precedente, supportata\n'
        txt = txt + '|-\n'
        txt = txt + '|\n'
        txt = txt +\
            '| style="white-space:nowrap; text-align:center;' +\
            ' background-color:{0}"|\n'\
            .format(self.color_status('c'))
        txt = txt + '|\n'
        txt = txt + '| Versione stabile corrente\n'
        txt = txt + '|-\n'
        txt = txt + '|\n'
        txt = txt +\
            '| style="white-space:nowrap; text-align:center;' +\
            ' background-color:{0}"|\n'\
            .format(self.color_status('cp'))
        txt = txt + '|\n'
        txt = txt + '| Ultima versione in beta\n'
        txt = txt + '|-\n'
        txt = txt + '|\n'
        txt = txt +\
            '| style="white-space:nowrap; text-align:center;' +\
            ' background-color:{0}"|\n'\
            .format(self.color_status('p'))
        txt = txt + '|\n'
        txt = txt + '| Futura versione\n'
        txt = txt + '|}\n'
        return txt

    def get_sect_name(self, sect_id):
        if sect_id == 7:
            sect_id = 6
        elif sect_id == 16:
            sect_id = 17
        nm = "sect_" + self.sections[sect_id]
        nm = nm.replace(" ", "__")
        nm = nm.replace("'", "_A")
        return nm

    def get_sect_text(self, sect_id):
        nm = self.sections[sect_id]
        nm = nm.replace("__", " ")
        nm = nm.replace("_A", "'")
        return nm

    def get_vers_txt(self, line):
        i = line.find(self.tags['version'])
        if i >= 0:
            txt = line[0:4]
        return txt

    def get_dict(self, prm):
        dict = {}
        self.cfg_obj = self.init_dict()
        if 'conf_fn' in prm:
            self.cfg_obj.read(prm['conf_fn'])

        for nm in ('PackageName',):
            dict[nm] = prm[nm]

        for i, nm in enumerate(self.sections):
            h = self.get_sect_name(i)
            if i != 1:
                dict[h] = "{{Template:Warning}}"
            else:
                dict[h] = ""

        s = "Fiscal"
        for nm in ('cur_month', 'pre_month',
                   'cur_year', 'pre_year',
                   'day_ivam', 'dayw_ivam',
                   'day_ivap', 'dayw_ivap',
                   'last_c_day', 'last_c_dayw',
                   'F24_IVA'):
            dict[nm] = self.cfg_obj.get(s, nm)
        return dict

    def __init__(self):
        self.version = "V1.1.3"


class main:
    #
    # Run main if executed as a script
    if __name__ == "__main__":
        # pdb.set_trace()
        B = Builder()

        parser = argparse.ArgumentParser(
            description="Zeroincombenze® make news.",
            epilog="© 2015 by SHS-AV s.r.l. - http://www.shs-av.com",
            argument_default=argparse.SUPPRESS)
        parser.add_argument("-c", "--conf",
                            help="configuration file",
                            dest="conf_fn",
                            metavar="file",
                            default="mknews.conf")
        parser.add_argument("-n", "--name",
                            help="software name",
                            dest="PackageName",
                            metavar="name",
                            default="wok_news")
        parser.add_argument("-o", "--out",
                            help="output filename",
                            dest="out_fn",
                            metavar="file",
                            default="news.txt")
        parser.add_argument("-p", "--platform",
                            help="Platform specific texts;"
                                 " may be linux2, win32 or OpenVMS",
                            dest="tgtplatform",
                            default=_platform)
        parser.add_argument("-q", "--brief",
                            help="No output message",
                            action="store_true",
                            dest="qmode", default=False)
        parser.add_argument("-r", "--ref",
                            help="reference news (source) filename",
                            dest="ref_fn",
                            metavar="file")
        parser.add_argument("-t", "--template",
                            help="news template (default from conf.file)",
                            dest="tmpl_fn", metavar="file")
        parser.add_argument("-T", "--test",
                            help="test execution mode",
                            action="store_true",
                            dest="simulate",
                            default=False)
        parser.add_argument("-V", "--version", action="version",
                            version="%(prog)s " + B.version)
#        parser.add_argument("saveset", help="saveset",
#                            nargs='?')

        opt_obj = parser.parse_args()
        prm = {}
        prm['qmode'] = opt_obj.qmode
        if hasattr(opt_obj, 'tmpl_fn'):
            prm['tmpl_fn'] = opt_obj.tmpl_fn
        if hasattr(opt_obj, 'ref_fn'):
            prm['ref_fn'] = opt_obj.ref_fn
        if hasattr(opt_obj, 'conf_fn'):
            prm['conf_fn'] = opt_obj.conf_fn
        prm['tgtplatform'] = opt_obj.tgtplatform
        prm['out_fn'] = opt_obj.out_fn
        prm['simulate'] = opt_obj.simulate
        if hasattr(opt_obj, 'PackageName'):
            prm['PackageName'] = opt_obj.PackageName

        if not prm['qmode']:
            print "Make news -c {0}".format(prm['conf_fn'])
        dict = B.get_dict(prm)
        news_str = B.get_template(prm)
        B.get_ref_text(dict, prm)
        news_obj = Template(news_str)
        news_str = news_obj.safe_substitute(dict).replace("\r\n", "\n")
        if not prm['simulate']:
            if not prm['qmode']:
                print "Writing {0}".format(prm['out_fn'])
            fd = open(prm['out_fn'], 'w')
            fd.write(news_str)
            fd.close()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
