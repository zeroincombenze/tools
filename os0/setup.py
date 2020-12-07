from setuptools import setup

setup(name='os0',
      version='0.2.15',
      description='OS indipendent interface',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Operating System :: OS Independent',
      ],
      keywords='os path linux windows openvms',
      url='http://wiki.zeroincombenze.org/en/Python/opt/os0',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero: GPL',
      packages=['os0'],
      zip_safe=False)
