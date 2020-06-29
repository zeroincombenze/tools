from setuptools import setup

setup(name='maintainer-quality-tools',
      version='0.2.3.3',
      description='QA Tools for Odoo maintainers (MQT)',
      long_description="""
The goal of Maintainer Quality Tools (MQT) is to provide helpers to ensure the quality of Odoo addons.
In order to setup TravisCI continuous integration for your project, just copy the
content of the [./sample_files] into your project’s root directory.
Then you can edit the files to ensure value for your project.
""",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Operating System :: OS Independent',
      ],
      keywords='linux travis development',
      url='https://github.com/OCA/maintainer-quality-tools',
      author='OCA',
      author_email='pedro.baeza@gmail.com',
      license='Affero GPL',
      packages=['maintainer-quality-tools'],
      zip_safe=False)
