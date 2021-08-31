from setuptools import setup

setup(name='zerobug',
      version='1.0.2',
      description='Zeroincombenze continuous testing framework'
                  ' and tools for python and bash programs',
      long_description="""
This library can run unit test of target package software.
Supported languages are *python* (through z0testlib.py)
and *bash* (through z0testrc)

*zerobug* supports test automation, aggregation of tests into collections
and independence of the tests from the reporting framework.
The *zerobug* module provides all code that make it easy to support testing
both for python programs both for bash scripts.
*zerobug* differs from pytest standard library because show execution test with
a message like "n/tot message" where *n* is current unit test and *tot* is the
total unit test to execute, that is a sort of advancing test progress.

*zerobug* is built on follow concepts:

* test main - it is a main program to executes all test runners
* test runner - it is a program to executes one or more test suites
* test suite - it is a collection of test cases
* test case -it is a smallest unit test
""",
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          # 'Topic :: Software Development:: Quality Assurance'
      ],
      keywords='unit test',
      url='http://wiki.zeroincombenze.org/en/Zerobug',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=['zerobug'],
      package_data={'zerobug': ['./z0testrc']},
      zip_safe=False)
