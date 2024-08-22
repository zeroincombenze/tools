#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from cryptography.fernet import Fernet

__version__ = "2.0.19"


def get_remote_user():
    local_user = os.environ["USER"]
    user = None
    default_user = None
    if host:
        for key, item in DATA[host].items():
            if "users" in item and local_user not in item["users"]:
                continue
            if not default_user or key == local_user:
                default_user = key
            if (
                    (not root_user and key == local_user)
                    or (root_user and key != local_user)
            ):
                user = key
                break
        if not user:
            user = default_user
    else:
        user = local_user
    return user


def get_remote_pwd(path):
    if not path:
        path = os.getcwd()
        if path.startswith(os.environ["HOME"]):
            path = path.replace(os.environ["HOME"], "~", 1)
    if path == "~":
        path = "~/"
    return path


def get_pwd(host, user):
    passwd = DATA[host][user].get("passwd")
    if not passwd and KEY and DATA[host][user].get("crypt_password"):
        passwd = Fernet(KEY).decrypt(DATA[host][user]["crypt_password"]).decode()
    return passwd


def get_cmd(host, user):
    param = DATA[host][user].get("param")
    passwd = get_pwd(host, user)
    if passwd:
        os.environ["SSHPASS"] = passwd
        return (
            "sshpass -e ssh %s %s@%s" % (param, user, host)
            if param
            else "sshpass -e ssh %s@%s" % (user, host)
        )
    return "ssh %s %s@%s" % (param, user, host) if param else "ssh %s@%s" % (user, host)


def get_cmd_rsync(host, host_side, user, source, dest, recurse):
    param = DATA[host][user].get("param", "")
    port = ""
    if param.startswith("-p"):
        port = param.split(" ")[1]
        param = ""
    passwd = get_pwd(host, user)
    if recurse and not source.endswith("/"):
        source = "%s/" % source
    if recurse and not dest.endswith("/"):
        dest = "%s/" % dest
    if host_side == "s":
        source = "%s@%s:%s" % (user, host, source)
    elif host_side == "d":
        dest = "%s@%s:%s" % (user, host, dest)
    if passwd:
        os.environ["SSHPASS"] = passwd
        return "sshpass -e rsync -avz %s %s %s" % (param, source, dest)
    if port:
        return "rsync -avz -e 'ssh -p %s' %s %s %s" % (port, param, source, dest)
    return "rsync -avz %s %s %s" % (param, source, dest)


def get_cmd_scp(host, host_side, user, source, dest, recurse):
    param = DATA[host][user].get("param", "").replace("-p", "-P")
    if recurse:
        if param.startswith("-"):
            param += " -r"
        else:
            param = "-r"
    passwd = get_pwd(host, user)
    if host_side == "s":
        source = "%s@%s:%s" % (user, host, source)
    elif host_side == "d":
        dest = "%s@%s:%s" % (user, host, dest)
    if passwd:
        os.environ["SSHPASS"] = passwd
        return "sshpass -e scp %s %s %s" % (param, source, dest)
    return "scp %s %s %s" % (param, source, dest)


def show_host(sel_host=None, glob=False):
    valid_hosts = []
    prior_host = ""
    cur_user = get_remote_user()
    for host in DATA.keys():
        if sel_host and host != sel_host:
            continue
        if host != prior_host:
            print("")
            prior_host = host
        for user in DATA[host].keys():
            if not glob and user != cur_user:
                continue
            if os.environ["USER"] not in DATA[host][user].get("users"):
                print(
                    "      %-48.48s# %s"
                    % (get_cmd(host, user), DATA[host][user]["users"])
                )
            else:
                print(
                    "    $ %-48.48s# %s"
                    % (get_cmd(host, user), DATA[host][user]["users"])
                )
                if host not in valid_hosts:
                    valid_hosts.append(host)
    if not valid_hosts:
        print("")
        print("No host for this user!")
    else:
        print("You should type:")
        for host in valid_hosts:
            if host in REV_ALIAS:
                print("$ ssh %-30.30s # %s" % (host, REV_ALIAS[host]))
            else:
                print("$ ssh %s" % host)


def show_alias():
    for key, alias in ALIAS.items():
        print("%s=%s" % (key, alias))
    return


def show_pwd():
    if not host:
        print("Missing host")
        exit(1)
    user = get_remote_user()
    if host in DATA.keys():
        if user in DATA[host]:
            passwd = get_pwd(host, user)
            if passwd:
                print("%s (%s)" % (passwd, user))
            else:
                print("<certificate> (%s)" % user)


def do_force_crypt():
    for host in DATA.keys():
        for user in DATA[host].keys():
            if (
                "passwd" in DATA[host][user]
                and "crypt_password" not in DATA[host][user]
            ):
                passwd = Fernet(KEY).encrypt(DATA[host][user]["passwd"].encode())
                del DATA[host][user]["passwd"]
                DATA[host][user]["crypt_password"] = passwd
    confn = os.path.join(os.environ["HOME"], ".ssh", "my_network.dat")
    with open(confn, "w") as fd:
        fd.write(str(DATA))


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
    print("  -l list hosts")
    print("  -m do mirror (rsync)")
    print("  -n dry-run")
    print("  -r recurse")
    print("  -s do scp")
    print("  -v verbose")
    print("  -w show passwords")
    print("  -Y force password encryption")
    print("  -z use privilegiated user")


# import pdb; pdb.set_trace()
DATA = {}
ALIAS = {}
REV_ALIAS = {}
KEY = None
keyfn = os.path.join(os.environ["HOME"], ".ssh", "id_rsa.key")
if os.path.isfile(keyfn):
    with open(keyfn, "r") as fd:
        KEY = fd.read().encode()
confn = os.path.join(os.environ["HOME"], ".ssh", "my_network.dat")
if os.path.isfile(confn):
    with open(confn, "r") as fd:
        DATA = eval(fd.read())
alias = os.path.join(os.environ["HOME"], ".ssh", "my_network_alias.dat")
if os.path.isfile(alias):
    with open(alias, "r") as fd:
        ALIAS = eval(fd.read())
    for key, item in ALIAS.items():
        REV_ALIAS[item] = key

host = None
user = None
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
host_side = "d"
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
        if "l" in param:
            list_host = True
        if "m" in param:
            rsync = True
        if "n" in param:
            dry_run = True
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
        if ":" in param and not host:
            host, param = param.split(":", 1)
            if "@" in host:
                user, host = host.split("@", 1)
            if not param:
                param = get_remote_pwd(param)
            if source:
                host_side = "d"
        if not source:
            source = param
        elif not dest:
            dest = param
        elif not host:
            host = source
            source = dest
            dest = param
        elif not user:
            user = source
            source = dest
            dest = param
        else:
            print("Invalid params %s" % param)
            exit(1)

if not host and source and not dest:
    host = source
    source = None
if host not in DATA and host in ALIAS:
    host = ALIAS[host]
if list_host:
    show_host(sel_host=host, glob=glob)
    exit(0)
if sh_alias:
    show_alias()
    exit(0)
if force_crypt:
    do_force_crypt()
    exit(0)
if host not in DATA:
    if host:
        print("Host %s not found!" % host)
    else:
        print("Missing host")
    exit(1)

if list_pwd:
    show_pwd()
    exit(0)
if not user:
    user = get_remote_user()
if not user:
    print("No user supplied!")
    # show_host(sel_host=host)
    exit(1)
if user not in DATA[host]:
    print("User %s not found for host %s!" % (user, host))
    # show_host(sel_host=host)
    exit(1)
if os.environ["USER"] not in DATA[host][user].get("users"):
    print("No valid connection parameter for current user!")
    # show_host(sel_host=host)
    exit(1)

if do_dir:
    source = get_remote_pwd(source)
    cmd = get_cmd(host, user)
    cmd = "%s dir '%s'" % (cmd, source)
elif scp or rsync:
    if not source and dest:
        source = get_remote_pwd(source)
    if not source:
        print("No source path supplied!")
        exit(1)
    if not dest and source:
        dest = get_remote_pwd(dest)
    if not dest:
        print("No destination path supplied!")
        exit(1)
    if rsync:
        cmd = get_cmd_rsync(host, host_side, user, source, dest, recurse)
    else:
        cmd = get_cmd_scp(host, host_side, user, source, dest, recurse)
else:
    cmd = get_cmd(host, user)
if verbose:
    print(cmd)
if dry_run:
    exit(0)
exit(os.system(cmd))












