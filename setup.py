#!/usr/bin/env python3
"""
Setup script for the JBMC workflow tool
"""

from setuptools import setup, find_packages

setup(
    name="jbmc-workflow",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jbmc-workflow=jbmc_workflow:main',
        ],
    },
    description="Tool to automate JBMC workflow and generate counter examples",
    author="Mueez Nadeem",
    author_email="mueeznadeem@example.com",
    python_requires=">=3.6",
)
