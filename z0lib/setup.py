from setuptools import setup

setup(name='z0lib',
      version='1.0.2',
      description='Bash zeroincombenze lib',
      long_description="""
General purpose bash and python library for zeroincombenze(R) tools

Features:

- unix/linux platform recognizer (tested on varioous environments)

- parseopt interface (mainly for basg scripts)

- log management

- local memory simple DB (only for bash scripts)

- configuration file management (only for bash scripts, like python configparser)
""",
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Operating System :: POSIX',
          'Programming Language :: Unix Shell',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: System :: System Shells',
      ],
      keywords='bash, optargs',
      url='http://wiki.zeroincombenze.org/en/Zerobug',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=['z0lib'],
      package_data={'z0lib': ['./z0librc', './z0lib']},
      zip_safe=False)
