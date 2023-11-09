#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


__version__ = "2.0.12"

APACHE_TEMPLATE = """##################################################################
# Odoo service %(branch)s
# Domain: <%(protocol)s://%(domain)s>
#
<VirtualHost *:%(apache_port)s>
    ServerAdmin %(email)s
    DocumentRoot %(website_document_root)s
    ServerName %(domain)s

    RemoteIPHeader X-Forwarded-For
    RemoteIPInternalProxy 127.0.0.0/8

    ProxyRequests Off
    ProxyPreserveHost On
    <Proxy *>
        AllowOverride None
        Require all granted
    </Proxy>
    ProxyVia On
    ProxyPass /longpolling http://localhost:%(longpolling_port)s/
    ProxyPassReverse /longpolling http://localhost:%(longpolling_port)s/
    ProxyPass / http://localhost:%(http_port)s/ timeout=600 keepalive=On retry=0
    ProxyPassReverse / http://localhost:%(http_port)s/

    ErrorLog %(logs)s/%(domain)s-error.log
    CustomLog %(logs)s/%(domain)s-access.log combined
%(http_proxy_block)s
%(https_block)s
</VirtualHost>
"""

APACHE_HTTP_PROXY_BLOCK = """
    RewriteEngine on
    RewriteCond %%{SERVER_NAME} =%(domain)s
    RewriteRule ^ https://%%{SERVER_NAME}%%{REQUEST_URI} [END,NE,R=permanent]
"""

APACHE_HTTPS_BLOCK = """
    SSLCertificateFile %(SSLCertificateFile)s
    SSLCertificateKeyFile %(SSLCertificateKeyFile)s
    Include /etc/letsencrypt/options-ssl-apache.conf
    # SSLCertificateChainFile
"""


class PleaseApache(object):
    """NAME
        create apache configuration file

    SYNOPSIS
        please create apache URL

    DESCRIPTION
        This command creates the apache configuration file for URL Odoo website.
        The configuration file may be deployed on /etc/apache2/site-available path
        or in equivalent path, i.e. /etc/httpd/conf

    OPTIONS
      %(options)s

    EXAMPLES
        please create apache odoo.example.com

    BUGS
        No known bugs.

    SEE ALSO
        Full documentation at: <https://zeroincombenze-tools.readthedocs.io/>
    """

    def __init__(self, please):
        self.please = please

    def action_opts(self, parser, for_help=False):
        self.please.add_argument(parser, "-b")
        self.please.add_argument(parser, "-c")
        self.please.add_argument(parser, "-l")
        if not for_help:
            self.please.add_argument(parser, "-n")
        parser.add_argument("-o", "--out-file")
        parser.add_argument(
            "-P",
            "--protocol",
            help="http or https",
            default="http",
        )
        parser.add_argument(
            "-p",
            "--http-port",
            help="http port (default from config file or 8069)",
        )
        parser.add_argument(
            "-L",
            "--long-port",
            help="long polling port(default from config file or 8070)",
        )
        if not for_help:
            self.please.add_argument(parser, "-q")
        parser.add_argument(
            "-S",
            "--https-proxy",
            action="store_true",
            help="add https proxy statements",
        )
        if not for_help:
            self.please.add_argument(parser, "-v")
        parser.add_argument(
            "-x",
            "--xmlrpc-port",
            help="xmlrpc port (default from config file or 8069)",
        )
        parser.add_argument("args", nargs="*")
        return parser

    def do_create(self):
        please = self.please
        odoo_confn = please.opt_args.odoo_config
        if odoo_confn:
            params = self._get_params_from_csv(
                odoo_confn, branch=please.opt_args.branch
            )
        else:
            params = self.default_config(please.opt_args.branch)
        params["branch"] = please.opt_args.branch
        if please.opt_args.args[0]:
            params["domain"] = please.opt_args.args[0]
        else:
            params["domain"] = "zeroincombenze.it"
        params["domain_2L"] = ".".join(params["domain"].split(".")[-2:])
        params["email"] = "postmaster@%s" % params["domain_2L"]
        if please.opt_args.log:
            params["logs"] = please.opt_args.log
        else:
            params["logs"] = "${APACHE_LOG_DIR}"
        params["protocol"] = please.opt_args.protocol
        params["apache_port"] = "443" if params["protocol"] == "https" else "80"
        params["SSLCertificateFile"] = ""
        params["SSLCertificateKeyFile"] = ""
        certificatefile = "/etc/letsencrypt/live/%s/fullchain.pem" % params["domain"]
        if os.path.isfile(certificatefile):
            params["SSLCertificateFile"] = certificatefile
        certificatekeyfile = "/etc/letsencrypt/live/%s/privkey.pem" % params["domain"]
        if os.path.isfile(certificatekeyfile):
            params["SSLCertificateKeyFile"] = certificatekeyfile

        if please.opt_args.https_proxy:
            params["http_proxy_block"] = APACHE_HTTP_PROXY_BLOCK % params
        else:
            params["http_proxy_block"] = ""
        if params["protocol"] == "https":
            params["https_block"] = APACHE_HTTPS_BLOCK % params
        else:
            params["https_block"] = ""
        content = APACHE_TEMPLATE % params
        out_file = (
            please.opt_args.out_file or ("~/%s-le-ssl.conf" % params["domain"])
            if params["protocol"] == "https"
            else "~/%s.conf" % params["domain"]
        )
        if please.opt_args.dry_run:
            if please.opt_args.verbose:
                print(content)
            print("File %s will be created" % out_file)
            return 0
        if os.path.isfile(out_file) and not please.opt_args.force:
            print("File %s already exist!")
            return 1
        with open(os.path.expanduser(out_file), "w") as fd:
            fd.write(content)
        print("File %s created" % out_file)
        return 0

    def default_config(self, branch=None):
        if branch:
            odoo_major_version = int(branch.split(".")[0])
            if odoo_major_version < 6:
                branch = None
        if branch:
            return {
                "http_port": 8160 + odoo_major_version,
                "longpolling_port": 8130 + odoo_major_version,
                "website_document_root": "/var/www/html/odoo",
            }
        return {
            "http_port": 8069,
            "longpolling_port": 8070,
            "website_document_root": "/var/www/html/odoo",
        }

    def _get_params_from_csv(self, odoo_fn, branch=None):
        config = ConfigParser.ConfigParser(self.default_config(branch=branch))
        config.read(odoo_fn)
        return {
            "http_port": self.please.opt_args.xmlrpc_port
            or self.please.opt_args.http_port
            or config.get("options", "xmlrpc_port")
            or config.get("options", "http_port"),
            "longpolling_port": self.please.opt_args.long_port
            or config.get("options", "longpolling_port"),
            "website_document_root": config.get("options", "website_document_root"),
        }

