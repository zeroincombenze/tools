from setuptools import setup

setup(name='z0bug_odoo',
      version='0.1.0.1.2',
      description='Odoo testing framework',
      long_description="""
Zeroincombenze(R) continuous testing framework for Odoo modules.

Make avaiable test functions indipendent by Odoo version.
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
