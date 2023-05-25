from setuptools import find_packages, setup

author = "Antonio Maria Vigliotti"
author_email = "<info@shs-av.com>"
source_url = "https://github.com/zeroincombenze/tools"
doc_url = "https://github.com/zeroincombenze/tools"
changelog_url = "%s/blob/master/z0lib/egg-info/CHANGELOG.rst" % source_url


setup(
    name="z0lib",
    version="2.0.5",
    description="Bash zeroincombenze lib",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: System Shells",
    ],
    keywords="bash, optargs",
    url="https://zeroincombenze-tools.readthedocs.io",
    project_urls={
        "Documentation": doc_url,
        "Source": source_url,
        "Changelog": changelog_url,
    },
    author=author,
    author_email=author_email,
    license="Affero GPL",
    install_requires=["configparser", "future"],
    packages=find_packages(exclude=["docs", "examples", "tests", "junk"]),
    package_data={"": ["scripts/setup.info", "./optargs", "./xuname", "./z0librc"]},
    entry_points={"console_scripts": ["z0lib-info = z0lib.scripts.main:main"]},
    zip_safe=False,
)










