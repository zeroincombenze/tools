Emulate travis to test application before pushing to git
--------------------------------------------------------

Travis emulator can emulate TravisCi parsing the .travis.yml file in local Linux machine.
You can test your application before pushing code to github.com web site.

Travis emulator can creates all the build declare by .travis.yml; all the builds are executed in sequential way.
The directory ~/travis_log (see -l switch) keeps the logs of all build executed.
Please note that log file is a binary file with screen escape code.
If you want to see the log use follow command:

    `less -R ~/travis_log/<build_name>.log`

A travis build does following steps:

* Initialize from local .travis.conf (not in travis-ci.org)
* Optional install packages `apt addons`
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
