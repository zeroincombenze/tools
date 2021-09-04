Emulate travis to test application before pushing to git
--------------------------------------------------------

Travis emulator can emulate TravisCi parsing the **.travis.yml** file in local Linux machine and it is osx/darwin compatible.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declared in **.travis.yml**; all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all builds created.
Please note that log file is a binary file with escape ANSI screen code.
If you want to see the log use one of following command:

    `travis show`

    `less -R ~/travis_log/<build_name>.log`

A travis build executes the following steps:

* Initialize from local .travis.conf (not in travis-ci.org)
* Optional install packages `apt addons` (emulatore makes just the check)
* Optional install packages `cache`
* Set global values `env global`
* Execute code `before_install`
* Execute matrix initialization, included python version
* Execute build code `install`
* Execute build code `before_script`
* Execute build code `script`
* Execute build `before_cache` (only if cache is effective, not emulated)
* Execute build code `after_success` (emulated) or `after_failure` (not emulated)
* Optional code `before_deploy` (only if deployment is effective, not emulated)
* Optional code `deploy` (not emulated)
* Optional code `after_deploy` (only if deployment is effective, not emulated)
* Execute code `after_script` (not emulated)
* Wep from local .travis.conf (not in travis-ci.org)

Read furthermore info read `travis-ci phase <https://docs.travis-ci.com/user/job-lifecycle/>`__


Difference between local travis and web site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The travis emulator works mostly like TravisCi web site. However you ha to consider some points where you run local tests:

Local software is not published

    When you test on your local PC, the software is not yet publishd. Perhaps you prefer test
    local packages or local modules.
    The travis emulator with z0bug_odoo replace the commands `git clone` with local `ln -s` creating
    logical link with local repository, if possible.
    Local module are searched in the testing module directory. See Odoo structure for furthermore info.

Your PC is not TravisCi web site

    Probability you have just one python interpreter and your user is not sudo enabled.
    The travis emulator run build just with Odoo interpreter installed even if your
    .travis.yml file contains more python version to test.
    The travis emulator does not try to install global packages because
    it does not change the PC configuration.
    Please, install manually all the global packages using apt-get, yum, dnf or your local installer software.
