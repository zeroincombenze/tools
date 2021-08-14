from setuptools import setup

setup(name='devel_tools',
      version='1.0.1.14',
      description='Python developers tools',
      long_description="""
Tool to parse, edit and migrate python source code
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
      packages=['devel_tools'],
      zip_safe=False)
