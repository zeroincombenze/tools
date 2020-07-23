#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

# import ast
import re
import os
import shutil
import subprocess
import sys
from six import string_types
from getaddons import (
    get_addons, get_modules, get_modules_info, get_dependencies,
    get_applications_with_dependencies, get_localizations_with_dependents)
from travis_helpers import success_msg, fail_msg
from configparser import ConfigParser

__version__ = '0.2.3.10'


def has_test_errors(fname, dbname, odoo_version, check_loaded=True):
    """
    Check a list of log lines for test errors.
    Extension point to detect false positives.
    """
    # Rules defining checks to perform
    # this can be
    # - a string which will be checked in a simple substring match
    # - a regex object that will be matched against the whole message
    # - a callable that receives a dictionary of the form
    #     {
    #         'loglevel': ...,
    #         'message': ....,
    #     }
    errors_ignore = [
        'Mail delivery failed',
        'failed sending mail',
        ]
    errors_report = [
        lambda x: x['loglevel'] == 'CRITICAL',
        'At least one test failed',
        'no access rules, consider adding one',
        'invalid module names, ignored',
        ]
    # Only check ERROR lines before 7.0
    if odoo_version < '7.0':
        errors_report.append(
            lambda x: x['loglevel'] == 'ERROR')

    def make_pattern_list_callable(pattern_list):
        for i in range(len(pattern_list)):
            if isinstance(pattern_list[i], string_types):
                regex = re.compile(pattern_list[i])
                pattern_list[i] = lambda x, regex=regex:\
                    regex.search(x['message'])
            elif hasattr(pattern_list[i], 'match'):
                regex = pattern_list[i]
                pattern_list[i] = lambda x, regex=regex:\
                    regex.search(x['message'])

    make_pattern_list_callable(errors_ignore)
    make_pattern_list_callable(errors_report)

    print("-"*10)
    # Read log file removing ASCII color escapes:
    # http://serverfault.com/questions/71285
    color_regex = re.compile(r'\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
    log_start_regex = re.compile(
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ (?P<loglevel>\w+) '
        r'(?P<db>(%s)|([?])) (?P<logger>\S+): (?P<message>.*\S)\s*$' % dbname)
    log_records = []
    last_log_record = dict.fromkeys(log_start_regex.groupindex.keys())
    with open(fname) as log:
        for line in log:
            line = color_regex.sub('', line)
            match = log_start_regex.match(line)
            if match:
                last_log_record = match.groupdict()
                log_records.append(last_log_record)
            else:
                last_log_record['message'] = '%s\n%s' % (
                    last_log_record['message'], line.rstrip('\n')
                )
    errors = []
    for log_record in log_records:
        ignore = False
        for ignore_pattern in errors_ignore:
            if ignore_pattern(log_record):
                ignore = True
                break
        if ignore:
            continue
        for report_pattern in errors_report:
            if report_pattern(log_record):
                errors.append(log_record)
                break

    if check_loaded:
        if not [r for r in log_records if 'Modules loaded.' in r['message']]:
            errors.append({'message': "Message not found: 'Modules loaded.'"})

    if errors:
        for e in errors:
            print(e['message'])
        print("-"*10)
    return len(errors)


def parse_list(comma_sep_list):
    return [x.strip() for x in comma_sep_list.split(',')]


def str2bool(string):
    return str(string or '').lower() in ['1', 'true', 'yes']


def get_server_path(odoo_full, odoo_version, travis_home):
    """
    Computes server path
    :param odoo_full: Odoo repository path
    :param odoo_version: Odoo version
    :param travis_home: Travis home directory
    :return: Server path
    """
    odoo_version = odoo_version.replace('/', '-')
    odoo_org, odoo_repo = odoo_full.split('/')
    server_dirname = "%s-%s" % (odoo_repo, odoo_version)
    server_path = os.path.join(travis_home, server_dirname)
    return server_path


def get_addons_path(travis_dependencies_dir, travis_base_dir, server_path,
                    odoo_test_select):
    """
    Computes addons path
    :param travis_dependencies_dir: Travis dependencies directory
    :param travis_base_dir: Travis odoo core directory
    :param server_path: Server path
    :param odoo module set to include/exclude
    :return: Addons path
    """
    addons_path_list = []
    for ldir in ('server/openerp', 'openerp', 'odoo'):
        if os.path.isdir(os.path.join(server_path, ldir, 'addons')):
            addons_path_list = [os.path.join(server_path, ldir, 'addons')]
            break
    addons_path_list.append(os.path.join(server_path, "addons"))
    if odoo_test_select != 'NO-CORE':
        addons_path_list.extend(get_addons(travis_base_dir))
    addons_path_list.extend(get_addons(travis_dependencies_dir))
    addons_path = ','.join(addons_path_list)
    return addons_path


# Discover automatically Odoo dir and version
# Recognizes old 6.1 tree, 7.0/8.0/9.0 tree and new 10.0/11.0/12.0 tree
def get_build_dir():
    odoo_version = os.environ.get("VERSION")
    travis_base_dir = os.environ.get("TRAVIS_BUILD_DIR", "../..")
    tested_version = ''
    for ldir in ('./server/openerp', './openerp', './odoo'):
        if os.path.isdir(ldir) and os.path.isfile('%s/release.py' % ldir):
            sys.path.append(ldir)
            import release
            tested_version = release.version
            if odoo_version == "auto":
                odoo_version = tested_version
            travis_base_dir = os.path.abspath('%s/addons' % ldir)
            break
    if not odoo_version and sys.argv[1]:
        # For backward compatibility, take version from parameter
        # if it's not globally set
        odoo_version = sys.argv[1]
        print("WARNING: no env variable set for VERSION. "
              "Using '%s'" % odoo_version)
    return travis_base_dir, odoo_version


# Return server script for all Odoo versions
def get_server_script(server_path):
    if os.path.isfile(get_script_path(server_path, 'odoo-bin')):
        return get_script_path(server_path, 'odoo-bin')
    elif os.path.isfile(get_script_path(server_path, 'openerp-server')):
        return get_script_path(server_path, 'openerp-server')
    return 'Script not found!'


def get_addons_to_check(travis_base_dir, odoo_include, odoo_exclude,
                        odoo_test_select):
    """
    Get the list of modules that need to be installed
    :param travis_base_dir: Travis odoo core directory
    :param odoo_include: addons to include (travis parameter)
    :param odoo_exclude: addons to exclude (travis parameter)
    :param odoo module set to include/exclude
    :return: List of addons to test
    """
    if odoo_include:
        addons_list = parse_list(odoo_include)
    elif odoo_test_select != 'NO-CORE':
        addons_list = get_modules(travis_base_dir)
    else:
        addons_list = []

    if odoo_exclude:
        exclude_list = parse_list(odoo_exclude)
        addons_list = [
            x for x in addons_list
            if x not in exclude_list]

    if odoo_test_select in ('APPLICATION', 'NO-APPLICATION',
                            'LOCALIZATION', 'NO-LOCALIZATION'):
        applications, localizations = set(), set()
        if odoo_test_select in ('APPLICATION', 'NO-APPLICATION'):
            applications = get_applications_with_dependencies(addons_list)
            if odoo_test_select == 'NO-APPLICATION':
                addons_list -= applications
                applications = set()
        if odoo_test_select in ('LOCALIZATION', 'NO-LOCALIZATION'):
            localizations = get_localizations_with_dependents(addons_list)
            if odoo_test_select == 'NO-LOCALIZATION':
                addons_list -= localizations
                localizations = set()
        if applications or localizations:
            addons_list = applications | localizations

    return addons_list


def get_test_dependencies(addons_path, addons_list):
    """
    Get the list of core and external modules dependencies
    for the modules to test.
    :param addons_path: string with a comma separated list of addons paths
    :param addons_list: list of the modules to test
    """
    if not addons_list:
        return ['base']
    else:
        modules = {}
        for path in addons_path.split(','):
            modules.update(get_modules_info(path))
        dependencies = set()
        for module in addons_list:
            dependencies |= get_dependencies(modules, module)
        return list(dependencies - set(addons_list))


def cmd_strip_secret(cmd):
    cmd_secret = []
    skip_next = False
    for param in cmd:
        if skip_next:
            skip_next = False
            continue
        if param.startswith('--db_'):
            cmd_secret.append(param.split('=')[0] + '=***')
            continue
        if param.startswith('--log-db'):
            cmd_secret.append('--log-db=***')
            continue
        if param in ['-w', '-r']:
            cmd_secret.extend([param, '***'])
            skip_next = True
            continue
        cmd_secret.append(param)
    return cmd_secret


# [antoniov: 2018-02-28]
def get_script_path(server_path, script_name):
    script_path = os.path.join(server_path, 'server')
    if os.path.isdir(script_path):
        script_path = os.path.join(server_path, 'server', script_name)
    else:
        script_path = os.path.join(server_path, script_name)
    return script_path


# [antoniov: 2018-03-31]
def build_run_cmd_odoo(server_path, script_name, db, preinstall_modules,
                       cmd_odoo, init=None, install_options=None,
                       server_options=None):
    script_path = get_script_path(server_path, script_name)
    if init:
        preinstall_modules = ','.join(preinstall_modules)
    cmd_odoo += [script_path,
                 "-d", db,
                 "--log-level=info",
                 "--stop-after-init",
                 "--init", preinstall_modules]
    if install_options:
        cmd_odoo.append(install_options)
    if server_options:
        cmd_odoo.append(server_options)
    return cmd_odoo


def new_server_instance(db, odoo_unittest, server_path, script_name,
                        addons_path, install_options, preinstall_modules=None,
                        unbuffer=True, server_options=None,
                        travis_debug_mode=None):
    """
    Setup the base module before running the tests
    if the database template exists then will be used.
    :param db: Template database name
    :param odoo_unittest: Boolean for unit test (travis parameter)
    :param server_path: Server path
    :param script_name: Odoo start-up script (openerp-server or odoo-bin)
    :param addons_path: Addons path
    :param install_options: Install options (travis parameter)
    :param server_options: (list) Add these flags to the Odoo server init
    """
    travis_debug_mode = travis_debug_mode or 0
    if preinstall_modules is None:
        preinstall_modules = ['base']
    if server_options is None:
        server_options = []
    print("\nCreating instance:")
    try:
        subprocess.check_call(["createdb", db])
    except subprocess.CalledProcessError:
        print("Using previous openerp_template database.")
    else:
        # unbuffer keeps output colors
        if os.environ.get('TRAVIS_PDB') == 'True':
            cmd_odoo = []
        else:
            cmd_odoo = ["unbuffer"] if unbuffer else []
        # [antoniov: 2018-02-28]
        script_path = get_script_path(server_path, script_name)
        cmd_odoo += [script_path,
                     "-d", db,
                     "--log-level=info",
                     "--stop-after-init",
                     "--init", ','.join(preinstall_modules),
                     ] + install_options + server_options   # 1
        print(" ".join(cmd_strip_secret(cmd_odoo)))
        if travis_debug_mode < 9:
            try:
                subprocess.check_call(cmd_odoo)
            except subprocess.CalledProcessError as e:
                return e.returncode
    return 0


def run_from_env_var(env_name_startswith, environ):
    """Method to run a script defined from an environment variable
    :param env_name_startswith: String with name of first letter of
                                environment variable to find.
    :param environ: Dictionary with full environ to search
    """
    commands = [
        command
        for environ_variable, command in sorted(environ.items())
        if environ_variable.startswith(env_name_startswith)
    ]
    for command in commands:
        print("command: ", command)
        subprocess.call(command, shell=True)


def set_conf_data(addons_path, data_dir):
    conf_data = {
        'addons_path': addons_path,
        'data_dir': data_dir,
    }
    # [ antoniov: 2018-02-28 ]
    if os.uname()[1][0:3] == 'shs':
        pid = os.getpid()
        if pid > 18000:
            rpcport = str(pid)
        else:
            rpcport = str(18000 + pid)
        conf_data['xmlrpc_port'] = rpcport
        conf_data['db_user'] = 'odoo'
    return conf_data


def write_server_conf(data, version):
    """Create (or edit) default configuration file of odoo
    :params data: Dict with all info to save in file"""
    fname_conf = os.path.expanduser('~/.openerp_serverrc')
    if not os.path.exists(fname_conf):
        # If not exists the file then is created
        fconf = open(fname_conf, "w")
        fconf.close()
    config = ConfigParser()
    config.read(fname_conf)
    if not config.has_section('options'):
        config['options'] = {}
    config['options'].update(data)
    with open(fname_conf, 'w') as configfile:
        config.write(configfile)


def copy_attachments(dbtemplate, dbdest, data_dir):
    attach_dir = os.path.join(os.path.expanduser(data_dir), 'filestore')
    attach_tmpl_dir = os.path.join(attach_dir, dbtemplate)
    attach_dest_dir = os.path.join(attach_dir, dbdest)
    if os.path.isdir(attach_tmpl_dir) and not os.path.isdir(attach_dest_dir):
        print("copy", attach_tmpl_dir, attach_dest_dir)
        shutil.copytree(attach_tmpl_dir, attach_dest_dir)


def get_environment():
    odoo_full = os.environ.get("ODOO_REPO", "odoo/odoo")
    travis_base_dir, odoo_version = get_build_dir()
    odoo_exclude = os.environ.get("EXCLUDE")
    odoo_include = os.environ.get("INCLUDE")
    odoo_unittest = str2bool(os.environ.get("UNIT_TEST"))
    odoo_unittest |= str2bool(os.environ.get('ODOO_TNLBOT', '0'))
    install_options = os.environ.get("INSTALL_OPTIONS", "").split()
    travis_home = os.environ.get("HOME", os.path.expanduser("~"))
    travis_dependencies_dir = os.path.join(travis_home, 'dependencies')
    odoo_branch = os.environ.get("ODOO_BRANCH")
    data_dir = os.path.expanduser(
        os.environ.get("DATA_DIR", os.path.expanduser('~/data_dir')))
    odoo_test_select = os.environ.get('ODOO_TEST_SELECT', 'ALL')
    dbtemplate = os.environ.get('MQT_TEMPLATE_DB', 'openerp_template')
    database = os.environ.get('MQT_TEST_DB', 'openerp_test')
    travis_debug_mode = eval(os.environ.get('TRAVIS_DEBUG_MODE', '0'))
    if odoo_version == '6.1':
        unbuffer = str2bool(os.environ.get('UNBUFFER', False))
    else:
        unbuffer = str2bool(os.environ.get('UNBUFFER', True))
    if travis_debug_mode:
        print('DEBUG: test_server.sys.path=%s' % sys.path)
    set_sys_path()
    if travis_debug_mode:
        print('DEBUG: test_server.sys.path=%s' % sys.path)

    server_path = get_server_path(odoo_full,
                                  odoo_branch or odoo_version,
                                  travis_home)
    script_name = get_server_script(server_path)
    if script_name != 'Script not found!':
        script_path = get_script_path(server_path, script_name)
        addons_path = get_addons_path(travis_dependencies_dir,
                                      travis_base_dir,
                                      server_path,
                                      odoo_test_select)
    else:
        script_path = ''
        addons_path = ''
    return (
        odoo_full,
        odoo_version,
        travis_base_dir,
        odoo_exclude,
        odoo_include,
        odoo_unittest,
        install_options,
        travis_home,
        travis_dependencies_dir,
        odoo_branch,
        server_path,
        script_name,
        odoo_test_select,
        addons_path,
        dbtemplate,
        database,
        data_dir,
        script_path,
        travis_debug_mode,
        unbuffer)


def get_log_level(odoo_version, test_enable, tnlbot=False):
    test_loghandler = None
    options = []
    if tnlbot:
        if odoo_version == "6.1" and not test_enable:
            options = ["--test-disable"]
        test_loglevel = 'info'
    elif odoo_version == "6.1":
        if not test_enable:
            options = ["--test-disable"]
        test_loglevel = 'test'
    else:
        if test_enable:
            options = ["--test-enable"]
        if odoo_version == '7.0':
            test_loglevel = 'test'
        else:
            test_loglevel = 'info'
            test_loghandler = 'openerp.tools.yaml_import:DEBUG'
    return options, test_loglevel, test_loghandler


def set_sys_path():
    x = -1
    for i in range(len(sys.path)):
        x = i if sys.path[i].endswith('/tools') else x
    if x > 0:
        sys.path.insert(0, sys.path[x])
        del sys.path[x + 1]
    else:
        sys.path.insert(0, os.path.join(os.environ.get('HOME'), 'tools'))


def main(argv=None):
    if argv is None:
        argv = sys.argv
    run_from_env_var('RUN_COMMAND_MQT', os.environ)
    # travis_home = os.environ.get("HOME", "~/")
    # travis_dependencies_dir = os.path.join(travis_home, 'dependencies')
    # odoo_branch = os.environ.get("ODOO_BRANCH")
    # odoo_unittest = str2bool(os.environ.get("UNIT_TEST"))
    # odoo_exclude = os.environ.get("EXCLUDE")
    # odoo_include = os.environ.get("INCLUDE")
    options = os.environ.get("OPTIONS", "").split()
    # install_options = os.environ.get("INSTALL_OPTIONS", "").split()
    server_options = os.environ.get('SERVER_OPTIONS', "").split()
    expected_errors = int(os.environ.get("SERVER_EXPECTED_ERRORS", "0"))
    instance_alive = str2bool(os.environ.get('INSTANCE_ALIVE'))
    # unbuffer = str2bool(os.environ.get('UNBUFFER', True))
    # data_dir = os.path.expanduser(os.environ.get("DATA_DIR", '~/data_dir'))
    test_enable = str2bool(os.environ.get('TEST_ENABLE', True))
    # dbtemplate = os.environ.get('MQT_TEMPLATE_DB', 'openerp_template')
    # database = os.environ.get('MQT_TEST_DB', 'openerp_test')
    # [antoniov: 2018-02-28]
    # travis_debug_mode = eval(os.environ.get('TRAVIS_DEBUG_MODE', '0'))
    odoo_test_select = os.environ.get('ODOO_TEST_SELECT', 'ALL')
    # travis_base_dir, odoo_version = get_build_dir()
    odoo_full, odoo_version, travis_base_dir, \
        odoo_exclude, odoo_include, odoo_unittest, \
        install_options, travis_home, \
        travis_dependencies_dir, odoo_branch, \
        server_path, script_name, odoo_test_select, \
        addons_path, dbtemplate, database, \
        data_dir, script_path, travis_debug_mode, \
        unbuffer = get_environment()
    # if not odoo_version:
    #     # For backward compatibility, take version from parameter
    #     # if it's not globally set
    #     odoo_version = argv[1]
    #     print("WARNING: no env variable set for VERSION. "
    #           "Using '%s'" % odoo_version)
    # test_loghandler = None
    # if odoo_version == "6.1":
    #     if not test_enable:
    #         options += ["--test-disable"]
    #     test_loglevel = 'test'
    # else:
    #     if test_enable:
    #         options += ["--test-enable"]
    #     if odoo_version == '7.0':
    #         test_loglevel = 'test'
    #     else:
    #         test_loglevel = 'info'
    #         test_loghandler = 'openerp.tools.yaml_import:DEBUG'
    opts, test_loglevel, test_loghandler = get_log_level(odoo_version,
                                                         test_enable)
    options += opts
    # odoo_full = os.environ.get("ODOO_REPO", "odoo/odoo")
    # server_path = get_server_path(odoo_full,
    #                               odoo_branch or odoo_version,
    #                              travis_home)
    # [antoniov: 2018-02-28]
    if travis_debug_mode:
        print("DEBUG: server_path='%s'" % server_path)
    # script_name = get_server_script(server_path)
    # [antoniov: 2018-02-28]
    if travis_debug_mode:
        print("DEBUG: script_name='%s'" % script_name)
    if script_name == 'Script not found!':
        return 1
    conf_data = set_conf_data(addons_path, data_dir)
    write_server_conf(conf_data, odoo_version)
    tested_addons_list = get_addons_to_check(travis_base_dir,
                                             odoo_include,
                                             odoo_exclude,
                                             odoo_test_select)
    tested_addons = ','.join(tested_addons_list)

    print("Working in %s" % travis_base_dir)
    print("Using repo %s and addons path %s" % (odoo_full, addons_path))

    if not tested_addons:
        print("WARNING!\nNothing to test- exiting early.")
        return 0
    else:
        print("Modules to test: %s" % tested_addons_list)
    # setup the preinstall modules without running the tests
    preinstall_modules = get_test_dependencies(addons_path,
                                               tested_addons_list)

    preinstall_modules = list(set(preinstall_modules or []) - set(get_modules(
        os.environ.get('TRAVIS_BUILD_DIR')) or [])) or ['base']
    print("Modules to preinstall: %s" % preinstall_modules)
    new_server_instance(dbtemplate, odoo_unittest, server_path,
                 script_name, addons_path, install_options, preinstall_modules,
                 unbuffer, server_options, travis_debug_mode)

    # Running tests [antoniov: 2018-02-28]
    script_path = get_script_path(server_path, script_name)
    if os.environ.get('TRAVIS_PDB') == 'True':
        cmd_odoo_test = ["python",  "-m", "pdb",
                         script_path,
                         "-d", database,
                         "--db-filter=^%s$" % database,
                         "--stop-after-init",
                         "--log-level", test_loglevel,
                         ]      # 2
    else:
        cmd_odoo_test = ["python", "-m", "coverage", "run",
                         script_path,
                         "-d", database,
                         "--db-filter=^%s$" % database,
                         "--stop-after-init",
                         "--log-level", test_loglevel,
                         ]      # 2

    if test_loghandler is not None:
        cmd_odoo_test += ['--log-handler', test_loghandler]
    cmd_odoo_test += options + ["--init", None]

    if odoo_unittest:
        to_test_list = tested_addons_list
        # [antoniov: 2018-02-28]
        cmd_odoo_install = [
            script_path,
            "-d", database,
            "--stop-after-init",
            "--log-level=warn",
        ] + install_options + server_options + ["--init", None]   #3
        commands = ((cmd_odoo_install, False),
                    (cmd_odoo_test, True),
                    )
    else:
        to_test_list = [tested_addons]
        commands = ((cmd_odoo_test, True),
                    )
    all_errors = []
    counted_errors = 0
    for to_test in to_test_list:
        print("\nTesting %s:" % to_test)
        db_odoo_created = False
        try:
            db_odoo_created = subprocess.call(
                ["createdb", "-T", dbtemplate, database])
            copy_attachments(dbtemplate, database, data_dir)
        except subprocess.CalledProcessError:
            db_odoo_created = True
        for command, check_loaded in commands:
            if db_odoo_created and instance_alive:
                # If exists database of odoo test
                # then start server with regular command without tests params
                rm_items = [
                    'python', '-m', 'coverage', 'run', '--stop-after-init',
                    '--test-enable', '--init', None,
                    '--log-handler', 'openerp.tools.yaml_import:DEBUG',
                ]
                command_call = [item
                                for item in commands[0][0]
                                if item not in rm_items] + \
                    ['--pidfile=/tmp/odoo.pid']     # 4
            else:
                command[-1] = to_test
                # Run test command; unbuffer keeps output colors
                if os.environ.get('TRAVIS_PDB') != 'True':
                    command_call = (["unbuffer"] if unbuffer else []) + command
                else:
                    command_call = command
            if travis_debug_mode >= 9:
                errors = 0
            else:
                print(" ".join(cmd_strip_secret(command_call)))
                pipe = subprocess.Popen(command_call,
                                        stderr=subprocess.STDOUT,
                                        stdout=subprocess.PIPE)
                with open('stdout.log', 'wb') as stdout:
                    for line in iter(pipe.stdout.readline, b''):
                        stdout.write(line)
                        print(line.strip().decode('UTF-8'))
                returncode = pipe.wait()
                # Find errors, except from failed mails
                errors = has_test_errors(
                    "stdout.log", database, odoo_version, check_loaded)
                if returncode != 0:
                    all_errors.append(to_test)
                    print(fail_msg, "Command exited with code %s" % returncode)
                    # If not exists errors then
                    # add an error when returcode!=0
                    # because is really a error.
                    if not errors:
                        errors += 1
            if errors:
                counted_errors += errors
                all_errors.append(to_test)
                print(fail_msg, "Found %d lines with errors" % errors)
        if not instance_alive and odoo_unittest:
            # Don't drop the database if will be used later.
            subprocess.call(["dropdb", database])

    print('Module test summary')
    for to_test in to_test_list:
        if to_test in all_errors:
            print(fail_msg, to_test)
        else:
            print(success_msg, to_test)
    if expected_errors and counted_errors != expected_errors:
        print("Expected %d errors, found %d!"
              % (expected_errors, counted_errors))
        return 1
    elif counted_errors != expected_errors:
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
