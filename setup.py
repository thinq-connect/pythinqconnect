import os

from setuptools import find_packages, setup

packages = ["thinqconnect"]

with open(os.path.join("README.md"), "r") as fh:
    long_description = fh.read()

setup(
    name="thinqconnect",
    version="0.9.5",
    packages=find_packages(exclude=["tests"]),
    description="ThinQ Connect Python SDK",
    author="ThinQConnect",
    author_email="thinq-connect@lge.com",
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
