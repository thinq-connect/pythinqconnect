"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""

import os

from setuptools import find_packages, setup

packages = ["thinqconnect"]

with open(os.path.join("README.md"), "r") as fh:
    long_description = fh.read()


setup(
    name="thinqconnect",
    version="1.0.4",
    packages=find_packages(exclude=["tests"]),
    description="ThinQ Connect Python SDK",
    author="ThinQConnect",
    author_email="thinq-connect@lge.com",
    url="https://github.com/thinq-connect/pythinqconnect",
    python_requires=">=3.10",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["aiohttp", "awsiotsdk", "pyOpenSSL"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
