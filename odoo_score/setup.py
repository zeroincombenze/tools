from setuptools import setup

setup(name='odoo_score',
      version='1.0.1',
      description='Odoo 10.0 super core',
      long_description="""
Odoo super core by Zeroincombenze(R) 
""",
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          # 'Topic :: Software Development:: Quality Assurance'
      ],
      keywords='odoo',
      url='http://wiki.zeroincombenze.org/',
      author='Antonio Maria Vigliotti',
      author_email='antoniomaria.vigliotti@gmail.com',
      license='Affero GPL',
      packages=['odoo_score'],
      zip_safe=False)
