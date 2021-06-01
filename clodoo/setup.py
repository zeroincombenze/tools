from setuptools import setup

setup(name='clodoo',
      version='0.3.31.2',
      description='Do massive operations on Odoo Cloud',
      long_description="""
Crete consistent DB for test and/or
do massive operation on multiple Odoo databases.
""",
      classifiers=[
          'Development Status :: 4 - Beta',
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
      package_data={'odoorc': ['./odoorc']},
      install_requires=['future', 'psycopg2-binary', 'odoorpc', 'oerplib', 'unidecode', 'z0lib'],
      zip_safe=False)
