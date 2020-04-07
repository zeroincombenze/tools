from setuptools import setup

setup(name='clodoo',
      version='0.3.8.73',
      description='Do massive operations on Odoo Cloud',
      long_description="""
Crete consistent DB for test and/or
do massive operation on multiple Odoo databases.
""",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
      ],
      keywords='odoo',
      url='http://wiki.zeroincombenze.org/en/Python/opt/clodoo',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=['clodoo'],
      package_data={'odoorc': ['./odoorc', './odoorc']},
      zip_safe=False)
