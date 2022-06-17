from setuptools import find_packages, setup

setup(
    name='z0bug_odoo',
    version='1.0.16',
    description='Odoo testing framework',
    long_description="""
Zeroincombenze(R) continuous testing framework for Odoo modules.

Make avaiable test functions indipendent by Odoo version.
""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: System Shells',
    ],
    keywords='unit test debug',
    url='https://zeroincombenze-tools.readthedocs.io',
    project_urls={
        'Documentation': 'https://zeroincombenze-tools.readthedocs.io',
        'Source': 'https://github.com/zeroincombenze/tools',
    },
    author='Antonio Maria Vigliotti',
    author_email='antoniomaria.vigliotti@gmail.com',
    license='Affero GPL',
    install_requires=['future', 'python-magic', 'zerobug'],
    packages=find_packages(exclude=['docs', 'examples', 'tests', 'egg-info', 'junk']),
    package_data={
        '': [
            'scripts/setup.info',
            'data/*',
            'travis/cfg/*',
            'travis/pylint_deprecated_modules/*',
            'travis/pylint_deprecated_modules/openerp/*',
            'travis/pylint_deprecated_modules/openerp/osv/*',
            'travis/clone_oca_dependencies',
            'travis/test_flake8',
            'travis/test_pylint',
            'travis/travis_makepot',
            'travis/travis_run_flake8',
            'travis/travis_run_tests',
            'travis/travis_test_dependencies',
        ]
    },
    entry_points={
        'console_scripts': [
            'z0bug-odoo-info = z0bug_odoo.scripts.main:main',
            # 'travis_run_tests = z0bug_odoo.travis.travis_run_tests:main',
        ]
    },
    zip_safe=False,
)
