# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="odoo_score",
    version="2.0.11",
    description="Odoo super core",
    long_description="""
Odoo supercore

odoo_score is a library that extends the odoo orm functionality
and makes available a simple odoo shell.
""",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        # "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: System Shells",
    ],
    keywords="odoo",
    url="https://zeroincombenze-tools.readthedocs.io",
    project_urls={
        "Documentation": "https://zeroincombenze-tools.readthedocs.io",
        "Source": "https://github.com/zeroincombenze/tools",
    },
    author="Antonio Maria Vigliotti",
    author_email="antoniomaria.vigliotti@gmail.com",
    license="GPL-3.0-or-later",
    install_requires=["z0lib>=2.0.11", "future"],
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={"": [
        "scripts/setup.info",
        "./set_workers",
        "./odooctl",
    ]},
    entry_points={
        "console_scripts": [
            "odoo_score-info = odoo_score.scripts.main:main",
            "odoo_shell.py = odoo_score.odoo_shell:main",
            "rename_odoo_module = odoo_score.scripts.rename_odoo_module:main",
        ]
    },
    zip_safe=False,
)
