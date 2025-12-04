import os
from setuptools import find_namespace_packages, setup


DESCRIPTION = "CLI toolkit for converting text to audio."
EXCLUDE_FROM_PACKAGES = ["build", "dist", "test", "src", "*~", "*.db", "ui"]


setup(
    name="ap_manager",
    author="wambua",
    author_email="swskye17@gmail.com",
    version=open(os.path.abspath("version.txt")).read(),
    packages=find_namespace_packages(exclude=EXCLUDE_FROM_PACKAGES),
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/APManager/",

    entry_points={
        "console_scripts": [
            "ap_manager=manager:argsdev",
            "ap=manager:argsdev"
        ],
    },

    python_requires=">=3.12",

    install_requires=[
        "setuptools",
        "wheel",
        "argparse",
    ],

    include_package_data=True,

    include_dirs=['config'],

    zip_safe=False,

    license="GNU v3",

    keywords=[
            "ap_manager", "access point", "hotspot", "network sharing"
    ],

    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
