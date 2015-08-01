$!
$! Regression tests for os0 module
$! Version running OpenVMS
$!
$ echo="write sys$output"
$ tf="os0_vms.rst"
$ td="[.tests]"
$ p1=f$edit(P1,"lowercase")
$ if f$extr(0,5,P1).eqs."/verb" .or. f$extr(0,6,P1).eqs."--verb"
$ then
$   p1="-v"
$ endif
$ if f$extr(0,2,P1).eqs."-h" .or. P1.eqs."-?" .or. f$extr(0,2,P1).eqs."/h" .or. f$extr(0,3,P1).eqs."--h"
$ then
$   echo "os0 tests based on doctest python module"
$   echo "Tests end without output; it means worked."
$   echo "Pass ""-v"" (lowercase v between quotes) for a detailed log"
$   echo "To execute tests, from os0 directory, type:"
$   echo "@[.tests]all_tests [-v] [/VERSION] [/HELP]"
$   echo " where"
$   echo " /HELP         this help"
$   echo " -v            verbose mode"
$   echo " /VERSION      show version"
$   echo "(C) SHS-AV s.r.l. - http://www.shs-av.com"
$   exit
$ endif
$ if f$extr(0,3,P1).eqs."-ve" .or. f$extr(0,2,P1).eqs."/v" .or. f$extr(0,3,P1).eqs."--v"
$ then
$   echo "Module os0 tests V1.2.1"
$   search/nohigh os0.py "version ="
$   exit
$ endif
$ if f$search(tf).nes.""
$ then
$   set def [-]
$ endif
$ if f$search(td+tf).nes.""
$ then
$   python -m doctest 'P1' 'td''tf'
$   python 'td'test_os0.py
$ else
$   echo "error"
$ endif
