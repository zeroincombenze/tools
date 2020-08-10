Emulate travis to test application before pushing to git
--------------------------------------------------------

Travis emulator can emulate TravisCi parsing .travis.yml file in local Linux machine.
You can test your application before pushing code to github.com web site.

This emulator does following steps:

* Initialize from local .travis.conf (not in travis-ci.org)
* Install packages from <apt addons>
* Install packages from cache
* Execute global from <env global>
* Execute code from <before_install>
* Execute matrix initialization, included python version
* Execute code from <install>
* Execute matrix code from <before_script>
* Execute matrix code from <script>
* Execute code from <before_cache> (not emulated)
* Execute code from <after_success> (emulated) o <after_failure> (not emulated)
* Execute code from <before_deploy> (not emulated)
* Execute code from <deploy> (not emulated)
* Execute code from <after_deploy> (not emulated)
* Execute code from <after_script> (not emulated)
* Wep from local .travis.conf (not in travis-ci.org)
