from setuptools import setup

setup(name='travis_emulator',
      version='0.2.2.20',
      description='Travis CI emulator for local develop environment',
      long_description="""
Simple emulator to simulate travis-ci operations on local host
before publishing code
Warning: this code does not replace travis-ci functionality!
It serves just to test before git push command
""",
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Operating System :: OS Independent',
      ],
      keywords='linux travis development',
      url='http://wiki.zeroincombenze.org/',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=['travis_emulator'],
      zip_safe=False)
