#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from cryptography.fernet import Fernet

__version__ = "2.0.19"


def spit_host_param(host, param):
    if param and not host:
        if ":" in param:
            host, param = param.split(":", 1)
        elif "@" in param:
            host = param
            param = ""
    return host, param


def split_user_host(ruser, host):
    if host and "@" in host:
        ruser, host = host.split("@", 1)
    return ruser, host


def get_remote_path(path):
    if not path:
        path = os.getcwd()
        if path.startswith(os.environ["HOME"]):
            path = path.replace(os.environ["HOME"], "~", 1)
    if path == "~":
        path = "~/"
    return path


def get_remote_user(CONF, host=None, cuser=None):
    cuser = cuser or os.environ["USER"]
    ruser = None
    default_user = None
    if host:
        for key, item in CONF["RUSER"][host].items():
            if "users" in item and cuser not in item["users"]:
                continue
            if not default_user or key == cuser:
                default_user = key
            if (
                    (not root_user and key == cuser)
                    or (root_user and key != cuser)
            ):
                ruser = key
                break
        if not ruser:
            ruser = default_user
    else:
        ruser = cuser
    return ruser


def get_pwd(CONF, host, ruser):
    passwd = CONF["RUSER"][host][ruser].get("passwd")
    if not passwd and CONF["KEY"] and CONF["RUSER"][host][ruser].get("crypt_password"):
        passwd = Fernet(CONF["KEY"]).decrypt(
            CONF["RUSER"][host][ruser]["crypt_password"]).decode()
    return passwd


def get_cmd(CONF, host, ruser, via=None):
    via = via or CONF["RUSER"][host][ruser]["via"]
    param = CONF["RUSER"][host][ruser].get("param", "")
    passwd = get_pwd(CONF, host, ruser)
    if via == "pwd" and passwd:
        os.environ["SSHPASS"] = passwd
        return (
            "sshpass -e ssh %s %s@%s" % (param, ruser, host)
            if param
            else "sshpass -e ssh %s@%s" % (ruser, host)
        )
    return "ssh %s %s@%s" % (param, ruser, host) if param else "ssh %s@%s" % (ruser,
                                                                              host)


def get_cmd_rsync(CONF, host, host_side, ruser, source, dest, recurse, via=None):
    via = via or CONF["RUSER"][host][ruser]["via"]
    param = CONF["RUSER"][host][ruser].get("param", "")
    port = ""
    if param.startswith("-p"):
        port = param.split(" ")[1]
        param = ""
    passwd = get_pwd(CONF, host, ruser)
    if recurse and not source.endswith("/"):
        source = "%s/" % source
    if recurse and not dest.endswith("/"):
        dest = "%s/" % dest
    if host_side == "s":
        source = "%s@%s:%s" % (ruser, host, source)
    elif host_side == "d":
        dest = "%s@%s:%s" % (ruser, host, dest)
    if via == "pwd" and passwd:
        os.environ["SSHPASS"] = passwd
        cmd = "sshpass -e rsync -avz"
    else:
        cmd = "rsync -avz"
    if port:
        cmd += " -e 'ssh -p %s'" % port
    cmd += " %s %s %s" % (param, source, dest)
    return cmd


def get_cmd_scp(CONF, host, host_side, ruser, source, dest, recurse, via=None):
    via = via or CONF["RUSER"][host][ruser]["via"]
    param = CONF["RUSER"][host][ruser].get("param", "")
    passwd = get_pwd(CONF, host, ruser)
    if host_side == "s":
        source = "%s@%s:%s" % (ruser, host, source)
    elif host_side == "d":
        dest = "%s@%s:%s" % (ruser, host, dest)
    if via == "pwd" and passwd:
        os.environ["SSHPASS"] = passwd
        cmd = "sshpass -e scp"
    else:
        cmd = "scp"
    if recurse:
        cmd += " -r"
    cmd += " %s %s %s" % (param, source, dest)
    return cmd


def show_host(CONF, sel_host=None, glob=False, cuser=None):
    valid_hosts = []
    cuser = cuser or os.environ["USER"]
    prior_host = ""
    for host in CONF["RUSER"].keys():
        if sel_host and host != sel_host:
            continue
        alias = CONF["REV_ALIAS"].get(host, "")
        for ruser in CONF["RUSER"][host]:
            gl = "g" if (cuser not in CONF["RUSER"][host][ruser]["users"]) else "l"
            if not glob and gl == "g":
                continue
            if host != prior_host:
                if alias:
                    print("%s (%s)" % (host, alias))
                else:
                    print(host)
                prior_host = host
            prompt = "$" if gl == "l" else " "
            print(
                "    %s %-64.64s # %s"
                % (prompt, get_cmd(CONF, host, ruser),
                   CONF["RUSER"][host][ruser]["users"])
            )
            if gl == "l" and host not in valid_hosts:
                valid_hosts.append(host)
    if not valid_hosts:
        print("")
        print("No host found for this user!")


def show_alias(CONF):
    for key, alias in CONF["ALIAS"].items():
        print("%s=%s" % (key, alias))
    return


def show_pwd(CONF, host, ruser=None):
    if not host:
        print("Missing host")
        exit(1)
    ruser = ruser or get_remote_user(CONF, host=host)
    if host in CONF["RUSER"].keys():
        if ruser in CONF["RUSER"][host]:
            passwd = get_pwd(CONF, host, ruser)
            if passwd:
                print("%s (%s)" % (passwd, ruser))
            else:
                print("<certificate> (%s)" % ruser)


def do_force_crypt(CONF):
    do_rewrite = False
    for host in CONF["RUSER"].keys():
        for ruser in CONF["RUSER"][host].keys():
            if (
                "passwd" in CONF["RUSER"][host][ruser]
                and "crypt_password" not in CONF["RUSER"][host][ruser]
            ):
                passwd = Fernet(CONF["KEY"]).encrypt(
                    CONF["RUSER"][host][ruser]["passwd"].encode())
                del CONF["RUSER"][host][ruser]["passwd"]
                CONF["RUSER"][host][ruser]["crypt_password"] = passwd
                do_rewrite = True
    if do_rewrite:
        confn = os.path.join(os.environ["HOME"], ".ssh", "my_network.dat")
        with open(confn, "w") as fd:
            fd.write(str(CONF["RUSER"]))


def show_help():
    print("ssh.py [-adlnvwz] [user@]host  # ssh")
    print("ssh.py -[n][r]s[vz] [user@]host:source destination  # scp")
    print("ssh.py -[n][r]s[vz] source [user@]host:destination  # scp")
    print("ssh.py -[n][r]m[vz] [user@]host:source destination  # rsync")
    print("ssh.py -[n][r]m[vz] source [user@]host:destination  # rsync")
    print("")
    print("  -a show aliases")
    print("  -d show remote dir")
    print("  -g list global hosts")
    print("  -l list user hosts")
    print("  -m do mirror (rsync)")
    print("  -p prefer password")
    print("  -n dry-run")
    print("  -r recurse")
    print("  -s do scp")
    print("  -v verbose")
    print("  -w show password")
    print("  -Y force password encryption")
    print("  -z use privilegiated user")


def load_config():
    # CONF
    #   RUSER
    #       host
    #           ruser
    #               - 'users' -> Local users login authorized
    #               - 'crypt_password' -> Encrypted remote password
    #               - 'param' -> ssh params, i.e. '-p 4322'
    #               - 'via' -> 'cert' (default w/o pwd), 'pwd'
    #   CUSER
    #       host
    #           cuser
    #               remote users
    #   ALIAS
    #       aliasname
    #           hostname
    #   REV_ALIAS
    #       hostname
    #           alias
    CONF = {
        "KEY": "",
        "RUSER": {},
        "CUSER": {},
        "ALIAS": {},
        "REV_ALIAS": {},
    }
    keyfn = os.path.join(os.environ["HOME"], ".ssh", "id_rsa.key")
    if not os.path.isfile(keyfn):
        print("No key file found!")
    else:
        with open(keyfn, "r") as fd:
            CONF["KEY"] = fd.read().encode()
    confn = os.path.join(os.environ["HOME"], ".ssh", "my_network.dat")
    if not os.path.isfile(confn):
        print("No configuration file found!")
    else:
        with open(confn, "r") as fd:
            CONF["RUSER"] = eval(fd.read())
            for host in CONF["RUSER"].keys():
                for ruser in CONF["RUSER"][host].keys():
                    if "via" not in CONF["RUSER"][host][ruser]:
                        CONF["RUSER"][host][ruser]["via"] = "pwd" if get_pwd(
                            CONF, host, ruser) else "cert"
                    if host not in CONF["CUSER"]:
                        CONF["CUSER"][host] = {}
                    for user in CONF["RUSER"][host][ruser]["users"]:
                        if user not in CONF["CUSER"][host]:
                            CONF["CUSER"][host][user] = []
                        if ruser not in CONF["CUSER"][host][user]:
                            CONF["CUSER"][host][user].append(ruser)
    alias = os.path.join(os.environ["HOME"], ".ssh", "my_network_alias.dat")
    if os.path.isfile(alias):
        with open(alias, "r") as fd:
            CONF["ALIAS"] = eval(fd.read())
        for alias, host in CONF["ALIAS"].items():
            CONF["REV_ALIAS"][host] = alias
    return CONF


# import pdb; pdb.set_trace()
CONF = load_config()

host = None
ruser = None
source = None
dest = None
verbose = False
dry_run = False
recurse = False
list_host = False
list_pwd = False
scp = False
rsync = False
sh_alias = False
do_dir = False
root_user = False
force_crypt = False
glob = False
host_side = ""
via_pwd = False
if not sys.argv[1:]:
    show_help()
    exit(0)
for param in sys.argv[1:]:
    if param.startswith("-"):
        if "h" in param:
            show_help()
            exit(0)
        if "a" in param:
            sh_alias = True
        if "d" in param:
            do_dir = True
        if "g" in param:
            glob = True
            list_host = True
        if "l" in param:
            list_host = True
        if "m" in param:
            rsync = True
        if "n" in param:
            dry_run = True
        if "p" in param:
            via_pwd = "pwd"
        if "r" in param:
            recurse = True
        if "s" in param:
            scp = True
        if "v" in param:
            verbose = True
        if "w" in param:
            list_pwd = True
        if "Y" in param:
            force_crypt = True
        if "z" in param:
            root_user = True
    else:
        host, param = spit_host_param(host, param)
        ruser, host = split_user_host(ruser, host)
        if not param:
            param = get_remote_path(param)
        if host or ruser:
            host_side = "d" if source else "s"
        if not source:
            source = param
        elif not dest:
            dest = param
        elif not host:
            host = source
            source = dest
            dest = param
        elif not ruser:
            ruser = source
            source = dest
            dest = param
        else:
            print("Invalid params %s" % param)
            exit(1)

if not host and source and not dest:
    host = source
    host_side = "s"
    source = None
if host not in CONF["RUSER"] and host in CONF["ALIAS"]:
    host = CONF["ALIAS"][host]

if list_host:
    show_host(CONF, sel_host=host, glob=glob)
    exit(0)
if sh_alias:
    show_alias(CONF)
    exit(0)
if force_crypt:
    do_force_crypt(CONF)
    exit(0)
if host not in CONF["RUSER"]:
    if host:
        print("Host %s not found!" % host)
    else:
        print("Missing host")
    exit(1)

if list_pwd:
    show_pwd(CONF, host, ruser=ruser)
    exit(0)
if not ruser:
    ruser = get_remote_user(CONF, host=host)
if not ruser:
    print("No user supplied!")
    exit(1)
if ruser not in CONF["RUSER"][host]:
    print("User %s not found for host %s!" % (ruser, host))
    exit(1)
if os.environ["USER"] not in CONF["RUSER"][host][ruser].get("users"):
    print("No valid connection parameter between current and remote user!")
    exit(1)

if do_dir:
    source = get_remote_path(source)
    cmd = get_cmd(CONF, host, ruser, via=via_pwd)
    cmd = "%s dir '%s'" % (cmd, source)
elif scp or rsync:
    if not source and dest:
        source = get_remote_path(source)
    if not source:
        print("No source path supplied!")
        exit(1)
    if not dest and source:
        dest = get_remote_path(dest)
    if not dest:
        print("No destination path supplied!")
        exit(1)
    if rsync:
        cmd = get_cmd_rsync(CONF, host, host_side, ruser, source, dest, recurse)
    else:
        cmd = get_cmd_scp(CONF, host, host_side, ruser, source, dest, recurse)
else:
    cmd = get_cmd(CONF, host, ruser, via=via_pwd)
if verbose:
    print(cmd)
if dry_run:
    exit(0)
exit(os.system(cmd))
