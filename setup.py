#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="btor2ex",
    version="0.1.0",
    description="Symbolic execution (and model checking) for BTOR2.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Adwait Godbole",
    author_email="adwait@berkeley.edu",
    url="https://github.com/adwait/btor2ex",
    packages=find_packages(exclude=["tests", "build", "dist"]),
    python_requires=">=3.11",
    install_requires=[
        "btor2-opt==0.2.1",
        "tqdm==4.67.1",
        "pyboolector==3.2.3.20240305.1",
        "bitwuzla @ git+https://github.com/bitwuzla/bitwuzla.git@0.8.1#egg=bitwuzla",
    ],
    entry_points={
        "console_scripts": [
            "btor2ex = btor2ex.btor2ex_main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
