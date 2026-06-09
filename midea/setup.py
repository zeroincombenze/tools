# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="midea",
    version="1.0.0",
    description="Simple app to test",
    long_description="""
This app is experimantla to test
""",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
    ],
    keywords="test",
    url="http://zeroincombenze.it",
    author="Antonio Maria Vigliotti",
    author_email="antoniomaria.vigliotti@gmail.com",
    license="GPL-3.0-or-later",
    packages=find_packages(exclude=["docs", "examples", "tests", "egg-info", "junk"]),
    package_data={"": []},
    zip_safe=False,
)


