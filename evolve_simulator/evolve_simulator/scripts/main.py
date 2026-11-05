# -*- coding: utf-8 -*-
# Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
# License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
"""evolve-simulator: run the Evolve web service simulator"""

import argparse
import atexit
import os
import signal
import sys

from .. import __version__
from ..config import Config


def write_pid_file(pid_file, debug=False):
    """Write the pid of the server process; the file is removed at exit"""
    # Flask debug reloader runs the server in a child process (WERKZEUG_RUN_MAIN):
    # the parent pid is the one to kill to stop the simulator
    if debug and os.environ.get("WERKZEUG_RUN_MAIN"):
        return
    pid_file = os.path.abspath(os.path.expanduser(pid_file))
    pid = os.getpid()
    with open(pid_file, "w") as fd:
        fd.write("%d\n" % pid)

    def remove_pid_file():
        try:
            with open(pid_file) as fd:
                if fd.read().strip() != str(pid):
                    return
            os.unlink(pid_file)
        except OSError:
            pass

    atexit.register(remove_pid_file)
    # Stopped by "kill $(cat pid_file)": exit cleanly, so the pid file is removed
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))


def main(cli_args=None):
    parser = argparse.ArgumentParser(
        prog="evolve-simulator",
        description="Evolve (certdoc.it) e-invoice web service simulator",
    )
    parser.add_argument("-H", "--host", default="127.0.0.1", help="bind address")
    parser.add_argument("-p", "--port", type=int, default=5000, help="TCP port")
    parser.add_argument("-d", "--database-url", help="SQLAlchemy URL of the database")
    parser.add_argument("-c", "--client-id", help="Odoo Client ID")
    parser.add_argument("-k", "--client-key", help="Odoo Client Key (16/24/32 chars)")
    parser.add_argument(
        "-C", "--company-id", type=int, help="Odoo Company ID of client"
    )
    parser.add_argument("--sdi-delay", type=int, help="seconds before delivery to SdI")
    parser.add_argument("--outcome-delay", type=int, help="seconds before outcome")
    parser.add_argument("--outcome", help="default SdI outcome")
    parser.add_argument("--pid-file", help="file where the simulator writes its pid")
    parser.add_argument(
        "--filestore",
        help="directory of xml files to receive as inbound invoices",
    )
    parser.add_argument("-n", "--no-auth", action="store_true", help="skip auth check")
    parser.add_argument("--debug", action="store_true", help="Flask debug mode")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    args = parser.parse_args(cli_args)

    from ..app import create_app

    settings = {}
    for key, value in (
        ("DATABASE_URL", args.database_url),
        ("CLIENT_ID", args.client_id),
        ("CLIENT_KEY", args.client_key),
        ("COMPANY_ID", args.company_id),
        ("SDI_DELAY", args.sdi_delay),
        ("OUTCOME_DELAY", args.outcome_delay),
        ("DEFAULT_OUTCOME", args.outcome),
        ("FILESTORE", args.filestore),
    ):
        if value is not None:
            settings[key] = value
    if args.no_auth:
        settings["AUTH_CHECK"] = False
    if len(settings.get("CLIENT_KEY", Config.CLIENT_KEY)) not in (16, 24, 32):
        print("Client Key must be 16, 24 or 32 chars long")
        return 1
    if settings.get("FILESTORE"):
        settings["FILESTORE"] = os.path.abspath(
            os.path.expanduser(settings["FILESTORE"])
        )
        if not os.path.isdir(settings["FILESTORE"]):
            print("Filestore %s is not a directory" % settings["FILESTORE"])
            return 1
    app = create_app(settings)
    if args.pid_file:
        write_pid_file(args.pid_file, args.debug)
    print(
        "Odoo SdI channel: Sender URL = http://%s:%d%s/  Client ID = %s"
        "  Company ID = %s"
        % (
            args.host,
            args.port,
            app.config["API_PREFIX"],
            app.config["CLIENT_ID"],
            app.config["COMPANY_ID"],
        )
    )
    print("Simulator page: http://%s:%d/" % (args.host, args.port))
    if app.config.get("FILESTORE"):
        print("Inbound xml files from %s" % app.config["FILESTORE"])
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
