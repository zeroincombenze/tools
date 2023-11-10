#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import argparse

# import re
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

TEMPLATE = """#############################################
# Odoo service
# Domain: <http://%(domain)s>
#
<VirtualHost *:80>
    ServerAdmin %(email)s
    DocumentRoot /var/www/html/odoo
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
    ProxyPass /longpolling http://localhost:%(longport)s/
    ProxyPassReverse /longpolling http://localhost:%(longport)s/
    ProxyPass / http://localhost:%(port)s/ timeout=600 keepalive=On retry=0
    ProxyPassReverse / http://localhost:%(port)s/

    ErrorLog ${APACHE_LOG_DIR}/%(domain)s-error.log
    CustomLog ${APACHE_LOG_DIR}/%(domain)s-access.log combined

    RewriteEngine on
    RewriteCond %%{SERVER_NAME} =%(domain)s
    RewriteRule ^ https://%%{SERVER_NAME}%%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
"""


TEMPLATE_HTTPS = """#############################################
# Odoo service
# Domain: <http://%(domain)s>
#
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin %(email)s
    DocumentRoot /var/www/html/odoo
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
    ProxyPass /longpolling http://localhost:%(longport)s/
    ProxyPassReverse /longpolling http://localhost:%(longport)s/
    ProxyPass / http://localhost:%(port)s/ timeout=600 keepalive=On retry=0
    ProxyPassReverse / http://localhost:%(port)s/

    ErrorLog logs/%(domain)s-error.log
    CustomLog logs/%(domain)s-access.log combined

    SSLCertificateFile
    SSLCertificateKeyFile
    Include /etc/letsencrypt/options-ssl-apache.conf
    SSLCertificateChainFile
</VirtualHost>
</IfModule>
"""

__version__ = "2.0.12"


class CreateConfig(object):
    def __init__(self, domain, opt_args):
        self.opt_args = opt_args
        if "." in domain:
            self.domain = domain
        else:
            self.domain = "%s.zeroincombenze.it" % domain
        self.confn = "%s.conf" % self.domain

        self.odoo_config = {}
        if self.opt_args.odoo_config:
            if not os.path.isfile(self.opt_args.odoo_config):
                print("Odoo config file %s not found!" % self.opt_args.odoo_config)
                return
            config = ConfigParser.ConfigParser()
            config.read(self.opt_args.odoo_config)
            for param in ("http_port", "xmlrpc_port", "longpolling_port"):
                if config.has_option("options", param):
                    self.odoo_config[param] = config.getint("options", param)

        self.email = "postmaster@%s" % ".".join(self.domain.split(".")[-2:])
        self.site_id = self.domain.split(".")[0]
        self.odoo_major_version = int(opt_args.odoo_version.split(".")[0])
        if opt_args.http_port:
            self.http_port = opt_args.http_port
        elif self.odoo_config.get("http_port"):
            self.http_port = self.odoo_config["http_port"]
        elif self.odoo_config.get("xmlrpc_port"):
            self.http_port = self.odoo_config["xmlrpc_port"]
        else:
            self.http_port = 8160 + self.odoo_major_version
        if opt_args.longpolling_port:
            self.http_port = opt_args.longpolling_port
        elif self.odoo_config.get("longpolling_port"):
            self.longport = self.odoo_config["longpolling_port"]
        elif int(self.http_port) >= 19000:
            self.longport = "%s" % (int(self.http_port) - 19000 + 100)
        else:
            self.longport = 8130 + self.odoo_major_version
        params = {
            "domain": self.domain,
            "port": self.http_port,
            "longport": self.longport,
            "email": "%s" % self.email,
        }
        if self.opt_args.https:
            self.http_config = TEMPLATE_HTTPS % params
        else:
            self.http_config = TEMPLATE % params

    def close(self):
        def write_file(fn, content):
            bakfile = "%s.bak" % fn
            if os.path.isfile(bakfile):
                os.remove(bakfile)
            if os.path.isfile(fn):
                os.rename(fn, bakfile)
            with open(fn, "w") as fd:
                fd.write(content)
                if self.opt_args.verbose > 0:
                    print("👽 %s" % fn)

        if not self.opt_args.dry_run:
            write_file(self.confn, self.http_config)
            # if self.odoo_config:
            #     write_file("odoo12-%s.conf" % self.site_id, self.odoo_config)


def main(cli_args=None):
    cli_args = cli_args or sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Create apache config file for Odoo instance",
        epilog="© 2021-2023 by SHS-AV s.r.l.",
    )
    parser.add_argument("-b", "--odoo-version", dest="odoo_version", default="12.0")
    parser.add_argument("-c", "--odoo-config", dest="odoo_config")
    parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true")
    parser.add_argument("-l", "--longpolling-port")
    parser.add_argument("-p", "--http-port", dest="http_port")
    parser.add_argument("-s", "--https", action="store_true", dest="https")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument("domain")
    opt_args = parser.parse_args(cli_args)
    sts = 0
    source = CreateConfig(opt_args.domain, opt_args)
    # source.do_migrate_openerp()
    source.close()
    return sts


if __name__ == "__main__":
    exit(main())

