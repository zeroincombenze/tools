#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

__version__ = "2.0.12"


def get_remote_user():
    local_user = os.environ["USER"]
    user = None
    default_user = None
    for key, item in DATA[host].items():
        if "users" in item and local_user not in item["users"]:
            continue
        if not default_user or key == local_user:
            default_user = key
        if (not root_user and key == local_user) or (root_user and key != local_user):
            user = key
            break
    if not user:
        user = default_user
    return user


def get_cmd(host, user):
    param = DATA[host][user].get("param")
    passwd = DATA[host][user].get("passwd")
    if passwd:
        os.environ["SSHPASS"] = passwd
        return (
            "sshpass -e ssh %s %s@%s" % (param, user, host)
            if param
            else "sshpass -e ssh %s@%s" % (user, host)
        )
    return "ssh %s %s@%s" % (param, user, host) if param else "ssh %s@%s" % (user, host)


def get_cmd_rsync(host, user, source, dest, recurse):
    param = DATA[host][user].get("param", "")
    port = ""
    if param.startswith("-p"):
        port = param.split(" ")[1]
        param = ""
    passwd = DATA[host][user].get("passwd")
    if recurse and not source.endswith("/"):
        source = "%s/" % source
    if recurse and not dest.endswith("/"):
        dest = "%s/" % dest
    if source.startswith("@"):
        source = "%s@%s:%s" % (user, host, source[1:])
    elif dest.startswith("@"):
        dest = "%s@%s:%s" % (user, host, dest[1:])
    if passwd:
        os.environ["SSHPASS"] = passwd
        return "sshpass -e rsync -avz %s %s %s" % (param, source, dest)
    if port:
        return "rsync -avz -e 'ssh -p %s' %s %s %s" % (port, param, source, dest)
    return "rsync -avz %s %s %s" % (param, source, dest)


def get_cmd_scp(host, user, source, dest, recurse):
    param = DATA[host][user].get("param", "").replace("-p", "-P")
    if recurse:
        if param.startswith("-"):
            param += " -r"
        else:
            param = "-r"
    passwd = DATA[host][user].get("passwd")
    if source.startswith("@"):
        source = "%s@%s:%s" % (user, host, source[1:])
    elif dest.startswith("@"):
        dest = "%s@%s:%s" % (user, host, dest[1:])
    if passwd:
        os.environ["SSHPASS"] = passwd
        return "sshpass -e scp %s %s %s" % (param, source, dest)
    return "scp %s %s %s" % (param, source, dest)


def show_host(sel_host=None):
    valid_hosts = []
    prior_host = ""
    for host in DATA.keys():
        if sel_host and host != sel_host:
            continue
        if host != prior_host:
            print("")
            prior_host = host
        for user in DATA[host].keys():
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
    user = get_remote_user()
    if host in DATA.keys():
        if user in DATA[host]:
            passwd = DATA[host][user].get("passwd")
            if passwd:
                print("%s (%s)" % (passwd, user))
            else:
                print("<certificate> (%s)" % user)


# import pdb; pdb.set_trace()
DATA = {}
ALIAS = {}
REV_ALIAS = {}
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
ctr = 0
for param in sys.argv[1:]:
    if param.startswith("-"):
        if "h" in param:
            print("ssh.py [-adlnvwz] host [user]  # ssh")
            print("ssh.py -[n][r]s[vz] host [user] source destination  # scp")
            print("ssh.py -[n][r]m[vz] host [user] source destination  # rsync")
            # show_host()
            exit(0)
        if "a" in param:
            sh_alias = True
        if "d" in param:
            do_dir = True
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
        if "z" in param:
            root_user = True
    elif ctr == 0:
        host = param
        ctr += 1
    elif ctr == 1:
        user = param
        ctr += 1
    elif ctr == 2:
        source = param
        ctr += 1
    elif ctr == 3:
        dest = param
        ctr += 1

if (scp or rsync) and user and not source and not dest:
    # ssh.py -m|s user@host:source dest
    # ssh.py -m|s source user@host:dest
    source = host
    host = ""
    dest = user
    user = ""
    if ":" in source and ":" not in dest:
        host, source = source.split(":", 1)
        source = "@" + source
    elif ":" not in source and ":" in dest:
        host, dest = dest.split(":", 1)
        dest = "@" + dest
    else:
        print("Invalid params! Use:")
        print("ssh.py -m|s user@host:source dest")
        print("ssh.py -m|s source user@host:dest")
        exit(1)
    if "@" in host:
        user, host = host.split("@", 1)
elif (scp or rsync) and user and source and not dest:
    dest = source
    source = user
    user = ""
elif do_dir and user and not source:
    source = user
    user = ""

if host not in DATA and host in ALIAS:
    host = ALIAS[host]
if list_host:
    show_host(sel_host=host)
    exit(0)
if sh_alias:
    show_alias()
    exit(0)
if list_pwd:
    show_pwd()
    exit(0)
if host not in DATA:
    if host:
        print("Host %s not found!" % host)
    show_host()
    exit(1)

if not user:
    user = get_remote_user()
if not user:
    print("No user supplied!")
    show_host(sel_host=host)
    exit(1)
if user not in DATA[host]:
    print("User %s not found for host %s!" % (user, host))
    show_host(sel_host=host)
    exit(1)
if os.environ["USER"] not in DATA[host][user].get("users"):
    print("No valid connection parameter for current user!")
    show_host(sel_host=host)
    exit(1)

if do_dir:
    if not source:
        print("No source path supplied!")
        exit(1)
    cmd = get_cmd(host, user)
    cmd = "%s dir '%s'" % (cmd, source)
elif scp or rsync:
    if not source:
        print("No source path supplied!")
        exit(1)
    if not dest:
        print("No destination path supplied!")
        exit(1)
    if rsync:
        cmd = get_cmd_rsync(host, user, source, dest, recurse)
    else:
        cmd = get_cmd_scp(host, user, source, dest, recurse)
else:
    cmd = get_cmd(host, user)
if verbose:
    print(cmd)
if dry_run:
    exit(0)
exit(os.system(cmd))

